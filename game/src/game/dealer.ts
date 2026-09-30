import { rngFor } from '../engine/rng';
import { areaView, goodOf } from './area';
import { CONFIG } from './config';
import { bustlePrice, dealPrice, offerKey, offerPrice, stockMultiplier } from './economy';
import { type ActorGood, type CategoryKind, type DealerDeal, type DealerOffer, type DealerVisit, type GameData, type RankedKind, RARITIES, type Rarity, type Role, type RunState, type SingleKind } from './types';

export const BAG_TIERS = CONFIG.dealer.ranks.bag;

const RANKED: RankedKind[] = ['bag', 'stockAll', 'buyerStockAll', 'luckAll'];
const PER_CATEGORY: CategoryKind[] = ['discount', 'stock', 'buyerStock', 'luck'];
/** The one-time stamps, in the order the collection lists them. */
const SINGLES: SingleKind[] = [
  'discountAll', 'dailyDiscount', 'tip', 'cantGetEnough', 'collector',
  'birdsEye', 'haggler', 'fannyPack', 'packedHouse', 'cramazing', 'mixedBag', 'lastCall', 'bigTipper',
  'fuzzyDice', 'sleepingBag', 'campFire', 'monocle', 'detour', 'vintage', 'cleanSweep', 'flipper',
  'perfectPlanner', 'dumpTruck',
];

/** A deal's rarity (CONFIG.dealer.rarity; common unless listed). */
export function rarityOf(deal: DealerDeal | DealerDeal['kind']): Rarity {
  return CONFIG.dealer.rarity[typeof deal === 'string' ? deal : deal.kind] ?? 'common';
}

/** The chance of each rarity for a stamp drawn in `week` (quota index + 1). The odds start in week 2,
 *  his first week, and rare and epic grow every week after. */
export function rarityOdds(week: number): Record<Rarity, number> {
  const n = Math.max(0, week - 2);
  const { epic, rare } = CONFIG.dealer.rarityOdds;
  const e = Math.min(1, epic.base + epic.perWeek * n);
  const r = Math.min(1 - e, rare.base + rare.perWeek * n);
  return { common: 1 - e - r, rare: r, epic: e };
}

/** The rarity at `u` (0..1): epic first, then rare, else common. */
export function rollRarity(u: number, week: number): Rarity {
  const odds = rarityOdds(week);
  if (u < odds.epic) return 'epic';
  if (u < odds.epic + odds.rare) return 'rare';
  return 'common';
}

/** The rarities to draw from when `rarity` is rolled: it, then each lower one, then (so a slot is
 *  still filled when everything below is gone) the higher ones. */
export function rarityFallback(rarity: Rarity): Rarity[] {
  const i = RARITIES.indexOf(rarity);
  return [...RARITIES.slice(0, i + 1).reverse(), ...RARITIES.slice(i + 1)];
}

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

/** The deals that affect every good (drawn with a 2x2 grid of the goods). */
export function isUniversal(deal: DealerDeal): boolean {
  return deal.kind === 'discountAll' || deal.kind === 'stockAll' || deal.kind === 'buyerStockAll' || deal.kind === 'luckAll';
}

export function dealCost(deal: DealerDeal): number {
  return deal.kind === 'bag' ? CONFIG.dealer.bagCosts[deal.tier - 1] : CONFIG.dealer.cost[deal.kind];
}

/** Every deal (stamp) in the game: every rank of the ranked deals, a discount (if the category's
 *  goods have one), extra stock, extra demand and better buyers per category, and the one-time
 *  stamps (SINGLES). Category deals work in every area. */
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
  for (const kind of SINGLES) all.push({ kind });
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

/** Every card of a rarity still in play: one per enabled deal not yet bought (one per unowned rank). */
function stampCards(data: GameData, state: RunState, rarity: Rarity): string[] {
  return allDeals(data).filter((d) => dealEnabled(d) && !owns(state, d) && rarityOf(d) === rarity).map(cardOf);
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

/** How many stamps he brings a visit: CONFIG.dealer.offers, plus the Stamp Collector's extra. */
export function dealerOfferCount(state: RunState): number {
  return CONFIG.dealer.offers + (owns(state, { kind: 'collector' }) ? CONFIG.dealer.collectorOffers : 0);
}

/** Today's Dealer visit, or null. He only comes once you've earned stars; his first visit is
 *  guaranteed, after that it's CONFIG.dealer.chance per day. His stamps come from one shuffled deck
 *  per rarity (`state.stampDecks`, a card per deal still to buy): each of the
 *  `dealerOfferCount` stamps he brings rolls a rarity (`rollRarity`, rarer as the weeks go by) and
 *  takes the next card of that deck, or of the next lower rarity when it has none (see
 *  `rarityFallback`). Once a deck's cards are used up he shuffles the rest of that rarity (every
 *  unbought deal not in the deck or on his table) under whatever's left. A card that can't be
 *  offered right now (a second card of a ranked deal already on the table) is skipped but stays in
 *  the deck. On his first visit after a met quota (`dealerCheapOwed`), the first offer is the first
 *  card costing at most CONFIG.dealer.cheapAfterQuota, skipping pricier ones the same way. He
 *  doesn't come once there's nothing left to sell. Deterministic for (seed, day). */
export function rollDealer(data: GameData, state: RunState): DealerVisit | null {
  if (state.stats.starsEarned <= 0) return null;
  const r = rngFor(state.seed, 'dealer', state.day);
  const roll = r.next();
  if (state.dealerSeen && roll >= CONFIG.dealer.chance) return null;
  if (eligibleDeals(data, state).length === 0) return null;
  state.dealerSeen = true;
  // never at the bustling location (Fireworks Night)
  const spots = state.locations.filter((l) => l.id !== state.bustlingAt);
  const locationId = spots[r.int(0, spots.length - 1)].id;
  const offers: DealerOffer[] = [];
  const cheap = state.dealerCheapOwed;
  state.dealerCheapOwed = false;
  drawStamps(data, state, r, offers, dealerOfferCount(state), cheap);
  return { locationId, offers };
}

/** Draw stamp cards from `state.stampDecks` onto his table (`offers`) until it holds `count`
 *  (see rollDealer). With `cheapFirst`, the first one drawn costs at most
 *  CONFIG.dealer.cheapAfterQuota. */
function drawStamps(
  data: GameData,
  state: RunState,
  r: ReturnType<typeof rngFor>,
  offers: DealerOffer[],
  count: number,
  cheapFirst = false,
): void {
  const week = state.quota.index + 1;
  const onTable = () => offers.filter((o) => !o.sold);
  const offered = (d: DealerDeal) => onTable().some((o) => dealKey(o.deal) === dealKey(d));
  const cards = {} as Record<Rarity, string[]>;
  const decks = {} as Record<Rarity, string[]>;
  for (const rarity of RARITIES) {
    cards[rarity] = stampCards(data, state, rarity);
    const saved = state.stampDecks?.[rarity] ?? [];
    // drop cards bought (or switched off) since they were shuffled in
    decks[rarity] = without(saved, without(saved, cards[rarity]));
  }
  /** Draw the first card of a rarity's deck that `ok` accepts, reshuffling once if none is left. */
  const drawFrom = (rarity: Rarity, ok: (d: DealerDeal) => boolean) => {
    const deck = decks[rarity];
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
      if (pass === 0) deck.push(...r.shuffle(without(cards[rarity], [...deck, ...onTable().map((o) => cardOf(o.deal))])));
    }
    return false;
  };
  /** Roll a rarity and draw from it, falling back to the other rarities when it has nothing. */
  const draw = (ok: (d: DealerDeal) => boolean) =>
    rarityFallback(rollRarity(r.next(), week)).some((rarity) => drawFrom(rarity, ok));
  if (cheapFirst && offers.length < count) draw((d) => dealCost(d) <= CONFIG.dealer.cheapAfterQuota);
  while (offers.length < count && draw(() => true));
  state.stampDecks = decks;
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
  grantDeal(data, state, o.deal);
  return true;
}

/** Add a deal to the run's stamps and apply what it does right away (buying one, or the debug menu). */
export function grantDeal(data: GameData, state: RunState, deal: DealerDeal): void {
  if (owns(state, deal)) return;
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
          offer.price = offerPrice(data, state, g, 'supplier', prices, offer.tier, offer.bustling);
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
    case 'collector':
      // he brings one more stamp from now on, starting with this visit
      if (state.dealer)
        drawStamps(data, state, rngFor(state.seed, 'dealer', state.day, 'collector'), state.dealer.offers,
          state.dealer.offers.length + CONFIG.dealer.collectorOffers);
      break;
    case 'cramazing':
      // today's Amazing deals get better right away (buyers keep any Can't Get Enough raises)
      for (const g of allGoods) {
        forTodays(data, state, 'supplier', g, (actorId, prices) => {
          const offer = state.market[offerKey(actorId, g)];
          if (offer.tier === 'amazing') offer.price = offerPrice(data, state, g, 'supplier', prices, 'amazing', offer.bustling);
        });
        forTodays(data, state, 'buyer', g, (actorId, prices) => {
          const offer = state.market[offerKey(actorId, g)];
          const bustle = (p: number) => (offer.bustling ? bustlePrice(data, state, 'buyer', p) : p);
          if (offer.tier === 'amazing') offer.price += bustle(dealPrice(state, prices, 'amazing')) - bustle(prices.amazing);
        });
      }
      break;
    // the other one-time stamps only need to be owned (see run.ts, deal.ts and the scenes)
  }
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
const pct = (x: number) => Math.round(x * 100);

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
    case 'collector':
      return { title: 'Stamp Collector', body: `Nox brings ${d.collectorOffers} more stamp each visit.` };
    case 'tip':
      return { title: 'Tip Jar', body: `Buyers tip $${d.tip} when you sell them ${d.tipAfter} goods in a day.` };
    case 'cantGetEnough':
      return { title: "Can't Get Enough", body: `Buyers pay $${d.cantGetEnoughStep} more after every good you sell them.` };
    case 'birdsEye':
      return { title: "Bird's Eye", body: 'See every price on the map.' };
    case 'haggler':
      return { title: 'Haggler', body: `Sellers pay +${pct(d.hagglerStart)}% more. Reduce by ${pct(d.hagglerStep)}% each sale.` };
    case 'fannyPack':
      return { title: 'Fanny Pack', body: `End of day: $${d.fannyPack} per different good in your bag.` };
    case 'packedHouse':
      return { title: 'Packed House', body: 'One place has an extra trader every day.' };
    case 'cramazing':
      return { title: 'Cramazing', body: `Amazing deals are ${d.cramazing}x as amazing.` };
    case 'mixedBag':
      return { title: 'Mixed Bag', body: `$${d.mixedBagTip} tip for each different good you sell a day.` };
    case 'lastCall':
      return { title: 'Last Call', body: 'The last-chance buyer pays Amazing prices.' };
    case 'bigTipper':
      return { title: 'Big Tipper', body: `Every tip is ${d.bigTipper}x bigger.` };
    case 'fuzzyDice':
      return { title: 'Fuzzy Dice', body: `1 in ${Math.round(1 / d.fuzzyDiceChance)} sales makes the buyer an Amazing deal.` };
    case 'sleepingBag':
      return { title: 'Sleeping Bag', body: `A day without trading pays ${pct(d.sleepingBag)}% of your bag's cost.` };
    case 'campFire':
      return { title: 'Camp Fire', body: 'The second good you buy each day is half price.' };
    case 'monocle':
      return { title: 'Monocle', body: `Every buy and sell price is ${pct(d.monocle)}% higher.` };
    case 'detour':
      return { title: 'Detour', body: "Didn't trade? Visit a second place that day." };
    case 'vintage':
      return { title: 'Vintage', body: `Goods sell for ${pct(d.vintagePerDay)}% more per day in your bag.` };
    case 'cleanSweep':
      return { title: 'Clean Sweep', body: `End the day with an empty bag: $${d.cleanSweep} per bag slot.` };
    case 'flipper':
      return { title: 'Flipper', body: `Goods bought yesterday sell for $${d.flipper} more.` };
    case 'perfectPlanner':
      return { title: 'Perfect Planner', body: 'Your priciest good always has a buyer.' };
    case 'dumpTruck':
      return { title: 'Dump Truck', body: 'Your most common good always has a buyer.' };
  }
}
