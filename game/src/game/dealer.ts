import { rngFor } from '../engine/rng';
import { areaView, goodOf } from './area';
import { CONFIG } from './config';
import { offerKey, sellerPrice, stockMultiplier, tierPrice } from './economy';
import type { ActorGood, CategoryKind, DealerDeal, DealerOffer, DealerVisit, GameData, RankedKind, Role, RunState, SingleKind } from './types';

export const BAG_TIERS = CONFIG.dealer.ranks.bag;

const RANKED: RankedKind[] = ['bag', 'stockAll', 'buyerStockAll', 'luckAll'];
const PER_CATEGORY: CategoryKind[] = ['discount', 'stock', 'buyerStock', 'luck'];

export function isRanked(deal: DealerDeal): deal is Extract<DealerDeal, { tier: number }> {
  return 'tier' in deal;
}

/** Stable id for a deal, used to remember which ones were bought. */
export function dealKey(deal: DealerDeal): string {
  if (isRanked(deal)) return `${deal.kind}:${deal.tier}`;
  if ('category' in deal) return `${deal.kind}:${deal.category}`;
  return deal.kind;
}

/** Inverse of dealKey. */
export function dealFromKey(key: string): DealerDeal {
  const [kind, arg] = key.split(':');
  if ((RANKED as string[]).includes(kind)) return { kind: kind as RankedKind, tier: Number(arg) };
  if ((PER_CATEGORY as string[]).includes(kind)) return { kind: kind as CategoryKind, category: arg };
  return { kind: kind as SingleKind };
}

export function owns(state: RunState, deal: DealerDeal): boolean {
  return state.perks.owned.includes(dealKey(deal));
}

/** The deals that affect every good (drawn as purple stamps). */
export function isUniversal(deal: DealerDeal): boolean {
  return deal.kind === 'discountAll' || deal.kind === 'stockAll' || deal.kind === 'buyerStockAll' || deal.kind === 'luckAll';
}

export function dealCost(deal: DealerDeal): number {
  return deal.kind === 'bag' ? CONFIG.dealer.bagCosts[deal.tier - 1] : CONFIG.dealer.cost[deal.kind];
}

/** Every deal (stamp) in the game: every rank of the ranked deals, a discount (if the category's
 *  goods have one), extra stock, extra demand and better buyers per category, the all-goods
 *  discount, Daily Discount, Tip Jar and Can't Get Enough. Category deals work in every area. */
export function allDeals(data: GameData): DealerDeal[] {
  const categories = Object.keys(data.categories);
  const hasDiscount = (category: string) =>
    Object.values(data.goods).some((g) => g.category === category && g.dealerDiscount > 0);
  const all: DealerDeal[] = [];
  const ranks = (kind: RankedKind) => {
    for (let tier = 1; tier <= CONFIG.dealer.ranks[kind]; tier++) all.push({ kind, tier });
  };
  ranks('bag');
  for (const kind of PER_CATEGORY)
    for (const category of categories) if (kind !== 'discount' || hasDiscount(category)) all.push({ kind, category });
  all.push({ kind: 'discountAll' });
  all.push({ kind: 'dailyDiscount' });
  all.push({ kind: 'tip' });
  all.push({ kind: 'cantGetEnough' });
  ranks('stockAll');
  ranks('buyerStockAll');
  ranks('luckAll');
  return all;
}

/** Is this kind of deal switched on (not in CONFIG.dealer.disabled)? */
export function dealEnabled(deal: DealerDeal): boolean {
  return !CONFIG.dealer.disabled.includes(deal.kind);
}

/** Deals the Dealer could offer right now: every enabled deal not yet bought, except that only
 *  the next rank of a ranked deal is offered (each needs the one before). */
export function eligibleDeals(data: GameData, state: RunState): DealerDeal[] {
  const unowned = allDeals(data).filter((d) => dealEnabled(d) && !owns(state, d));
  return unowned.filter(
    (d) => !isRanked(d) || !unowned.some((o) => o.kind === d.kind && isRanked(o) && o.tier < d.tier),
  );
}

/** A stamp deck card: the deal's key, or just the kind for a ranked deal (each of its cards stands
 *  for whichever rank is next). */
function cardOf(deal: DealerDeal): string {
  return isRanked(deal) ? deal.kind : dealKey(deal);
}

/** The deal a card offers right now (the next unowned rank for a ranked card), or null once it's
 *  all owned or switched off. */
function cardDeal(state: RunState, card: string): DealerDeal | null {
  if ((RANKED as string[]).includes(card)) {
    const kind = card as RankedKind;
    for (let tier = 1; tier <= CONFIG.dealer.ranks[kind]; tier++) {
      const deal: DealerDeal = { kind, tier };
      if (!owns(state, deal)) return dealEnabled(deal) ? deal : null;
    }
    return null;
  }
  const deal = dealFromKey(card);
  return dealEnabled(deal) && !owns(state, deal) ? deal : null;
}

/** Every card still in play: one per enabled deal not yet bought (one per unowned rank). */
function stampCards(data: GameData, state: RunState): string[] {
  return allDeals(data).filter((d) => dealEnabled(d) && !owns(state, d)).map(cardOf);
}

/** `cards` with each card in `used` taken out once (a multiset difference, keeping order). */
function without(cards: string[], used: string[]): string[] {
  const left = [...used];
  return cards.filter((c) => {
    const i = left.indexOf(c);
    if (i < 0) return true;
    left.splice(i, 1);
    return false;
  });
}

/** Today's Dealer visit, or null. He only comes once you've earned stars; his first visit is
 *  guaranteed, after that it's CONFIG.dealer.chance per day. His stamps come from one shuffled deck
 *  (`state.stampDeck`, a card per deal still to buy): each visit he draws the next
 *  CONFIG.dealer.offers cards, and once they're used up he shuffles the rest (every unbought deal
 *  not in the deck or on his table) under whatever's left. A card that can't be offered right now
 *  (a second card of a ranked deal already on the table) is skipped but stays in the deck. On his
 *  first visit after a met quota (`dealerCheapOwed`), the first offer is the first card costing at
 *  most CONFIG.dealer.cheapAfterQuota, skipping pricier ones the same way. He doesn't come once
 *  there's nothing left to sell. Deterministic for (seed, day). */
export function rollDealer(data: GameData, state: RunState): DealerVisit | null {
  if (state.stats.starsEarned <= 0) return null;
  const r = rngFor(state.seed, 'dealer', state.day);
  const roll = r.next();
  if (state.dealerSeen && roll >= CONFIG.dealer.chance) return null;
  if (eligibleDeals(data, state).length === 0) return null;
  state.dealerSeen = true;
  const locationId = state.locations[r.int(0, state.locations.length - 1)].id;
  const cards = stampCards(data, state);
  // drop cards bought (or switched off) since they were shuffled in
  const deck = without(state.stampDeck ?? [], without(state.stampDeck ?? [], cards));
  const offers: DealerOffer[] = [];
  const offered = (d: DealerDeal) => offers.some((o) => dealKey(o.deal) === dealKey(d));
  /** Draw the first card that `ok` accepts, reshuffling once if none is left. */
  const draw = (ok: (d: DealerDeal) => boolean) => {
    for (let pass = 0; pass < 2; pass++) {
      const i = deck.findIndex((c) => {
        const d = cardDeal(state, c);
        return d !== null && !offered(d) && ok(d);
      });
      if (i >= 0) {
        const deal = cardDeal(state, deck.splice(i, 1)[0])!;
        offers.push({ deal, cost: dealCost(deal), sold: false });
        return true;
      }
      if (pass === 0) deck.push(...r.shuffle(without(cards, [...deck, ...offers.map((o) => cardOf(o.deal))])));
    }
    return false;
  };
  if (state.dealerCheapOwed) {
    draw((d) => dealCost(d) <= CONFIG.dealer.cheapAfterQuota);
    state.dealerCheapOwed = false;
  }
  while (offers.length < CONFIG.dealer.offers && draw(() => true));
  state.stampDeck = deck;
  return { locationId, offers };
}

export type DealerBlock = 'sold' | 'noStars' | null;

export function dealerBlock(state: RunState, index: number): DealerBlock {
  const o = state.dealer?.offers[index];
  if (!o || o.sold) return 'sold';
  if (state.stars < o.cost) return 'noStars';
  return null;
}

/** Buy one of today's offers. Returns false if blocked. */
export function buyDealerDeal(data: GameData, state: RunState, index: number): boolean {
  const o = state.dealer?.offers[index];
  if (!o || dealerBlock(state, index) !== null) return false;
  state.stars -= o.cost;
  o.sold = true;
  const deal = o.deal;
  const { perks } = state;
  perks.owned.push(dealKey(deal));
  data = areaView(data, state.area);
  const allGoods = Object.keys(data.goods);
  /** Today's good in the deal's category. */
  const good = () => ('category' in deal ? goodOf(data, deal.category, state.area) : '');
  switch (deal.kind) {
    case 'bag':
      state.capacity += CONFIG.dealer.bagSlots[deal.tier - 1];
      break;
    case 'discount':
    case 'discountAll': {
      if (deal.kind === 'discount') perks.discounts[deal.category] = 1;
      else perks.discountAll += CONFIG.dealer.discountAll;
      // takes effect right away: re-price today's sellers
      for (const g of deal.kind === 'discount' ? [good()] : allGoods)
        forTodays(data, state, 'supplier', g, (actorId, prices) => {
          const offer = state.market[offerKey(actorId, g)];
          offer.price = sellerPrice(data, state, g, tierPrice(prices, offer.tier));
        });
      break;
    }
    case 'stock': {
      const n = CONFIG.dealer.stockStep[deal.category];
      perks.stock[deal.category] = (perks.stock[deal.category] ?? 0) + n;
      // today's sellers restock right away (multiplied by Overflowing Supply, if owned)
      const g = good();
      forTodays(data, state, 'supplier', g, (actorId) => {
        state.market[offerKey(actorId, g)].left += n * stockMultiplier(state);
      });
      break;
    }
    case 'stockAll': {
      perks.stockAll += 1;
      // today's sellers multiply what they have left right away
      for (const g of allGoods)
        forTodays(data, state, 'supplier', g, (actorId) => {
          state.market[offerKey(actorId, g)].left *= CONFIG.dealer.stockAll;
        });
      break;
    }
    case 'buyerStock':
    case 'buyerStockAll': {
      const n = deal.kind === 'buyerStock' ? CONFIG.dealer.buyerStockStep : CONFIG.dealer.buyerStockAll;
      if (deal.kind === 'buyerStock') perks.buyerStock[deal.category] = (perks.buyerStock[deal.category] ?? 0) + n;
      else perks.buyerStockAll += n;
      // today's buyers want more right away
      for (const g of deal.kind === 'buyerStock' ? [good()] : allGoods)
        forTodays(data, state, 'buyer', g, (actorId) => {
          state.market[offerKey(actorId, g)].left += n;
        });
      break;
    }
    case 'luck':
      perks.luck[deal.category] = (perks.luck[deal.category] ?? 0) + CONFIG.dealer.luckStep;
      break;
    case 'luckAll':
      perks.luckAll += CONFIG.dealer.luckAll;
      break;
    // dailyDiscount, tip and cantGetEnough only need to be owned (see buyPrice and sell in run.ts)
  }
  return true;
}

/** Run `fn` for every actor of `role` dealt in today who trades `good`. */
function forTodays(
  data: GameData,
  state: RunState,
  role: Role,
  good: string,
  fn: (actorId: string, prices: ActorGood['prices']) => void,
): void {
  for (const loc of state.locations)
    for (const actorId of loc.actorIds) {
      const a = data.actors[actorId];
      const ag = a.goods.find((g) => g.good === good);
      if (a.role === role && ag && state.market[offerKey(actorId, good)]) fn(actorId, ag.prices);
    }
}

/** The good a deal is about in an area, if any (for its icon). */
export function dealGood(data: GameData, deal: DealerDeal, areaId: string): string | null {
  return 'category' in deal ? goodOf(data, deal.category, areaId) : null;
}

const ROMAN = ['I', 'II', 'III', 'IV', 'V'];

/** Short title and a one-line description for the dialog and tooltip. Category deals are named
 *  after the category, with the area's good in the description. */
export function describeDeal(data: GameData, deal: DealerDeal, areaId: string): { title: string; body: string } {
  const d = CONFIG.dealer;
  const cat = 'category' in deal ? data.categories[deal.category].name : '';
  const g = 'category' in deal ? data.goods[goodOf(data, deal.category, areaId)] : null;
  const what = g ? `${cat} (${g.name})` : '';
  switch (deal.kind) {
    case 'bag': {
      const n = d.bagSlots[deal.tier - 1];
      return { title: `Bigger Bag ${ROMAN[deal.tier - 1]}`, body: `+${n} bag slot${n === 1 ? '' : 's'}.` };
    }
    case 'discount':
      return { title: `${cat} Sale`, body: `${what} costs $${g!.dealerDiscount} less (min $1).` };
    case 'stock':
      return { title: `${cat} Surplus`, body: `+${d.stockStep[deal.category]} ${what} for sale each day.` };
    case 'luck': {
      const pct = Math.round(d.luckStep * 100 * 2);
      return { title: `${cat} Dealer`, body: `+${pct}% more deals on ${what}.` };
    }
    case 'buyerStock':
      return { title: `${cat} Demand`, body: `Buyers want ${d.buyerStockStep} more ${what} each day.` };
    case 'luckAll': {
      const pct = Math.round(d.luckAll * 100 * 2);
      return { title: `Deals, Deals, Everywhere ${ROMAN[deal.tier - 1]}`, body: `+${pct}% more deals on ALL goods.` };
    }
    case 'discountAll':
      return { title: `Clearance Sale`, body: `ALL sellers charge $${d.discountAll} less (min $1).` };
    case 'stockAll':
      return { title: 'Overflowing Supply', body: `EVERY seller stocks ${d.stockAll}x as many items each day.` };
    case 'buyerStockAll':
      return { title: `Universal Demand ${ROMAN[deal.tier - 1]}`, body: `EVERY buyer wants ${d.buyerStockAll} more item each day.` };
    case 'dailyDiscount':
      return { title: 'Daily Discount', body: 'The first good you buy each day is half price.' };
    case 'tip':
      return { title: 'Tip Jar', body: `Buyers tip $${d.tip} when you sell them ${d.tipAfter} goods in a day.` };
    case 'cantGetEnough':
      return { title: "Can't Get Enough", body: `Buyers pay $${d.cantGetEnoughStep} more after every good you sell them.` };
  }
}
