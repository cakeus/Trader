import { rngFor } from '../engine/rng';
import { CONFIG } from './config';
import { offerKey, sellerPrice } from './economy';
import type { DealerDeal, DealerVisit, GameData, GoodKind, RankedKind, Role, RunState } from './types';

export const BAG_TIERS = CONFIG.dealer.ranks.bag;

const RANKED: RankedKind[] = ['bag', 'stockAll', 'buyerStockAll', 'sellChanceAll'];
const PER_GOOD: GoodKind[] = ['discount', 'stock', 'buyerStock', 'sellChance'];

export function isRanked(deal: DealerDeal): deal is Extract<DealerDeal, { tier: number }> {
  return 'tier' in deal;
}

/** Stable id for a deal, used to remember which ones were bought. */
export function dealKey(deal: DealerDeal): string {
  if (isRanked(deal)) return `${deal.kind}:${deal.tier}`;
  if ('good' in deal) return `${deal.kind}:${deal.good}`;
  return deal.kind;
}

/** Inverse of dealKey. */
export function dealFromKey(key: string): DealerDeal {
  const [kind, arg] = key.split(':');
  if ((RANKED as string[]).includes(kind)) return { kind: kind as RankedKind, tier: Number(arg) };
  if ((PER_GOOD as string[]).includes(kind)) return { kind: kind as GoodKind, good: arg };
  return { kind: 'discountAll' };
}

export function owns(state: RunState, deal: DealerDeal): boolean {
  return state.perks.owned.includes(dealKey(deal));
}

/** The deals that affect every good (drawn as purple stamps). */
export function isUniversal(deal: DealerDeal): boolean {
  return deal.kind === 'discountAll' || deal.kind === 'stockAll' || deal.kind === 'buyerStockAll' || deal.kind === 'sellChanceAll';
}

export function dealCost(deal: DealerDeal): number {
  return deal.kind === 'bag' ? CONFIG.dealer.bagCosts[deal.tier - 1] : CONFIG.dealer.cost[deal.kind];
}

/** Every deal (stamp) in the game: every rank of the ranked deals, a discount (if the good has
 *  one), extra stock, extra demand and better buyers per good, and the all-goods discount. */
export function allDeals(data: GameData): DealerDeal[] {
  const goods = Object.keys(data.goods).sort();
  const all: DealerDeal[] = [];
  const ranks = (kind: RankedKind) => {
    for (let tier = 1; tier <= CONFIG.dealer.ranks[kind]; tier++) all.push({ kind, tier });
  };
  ranks('bag');
  for (const kind of PER_GOOD)
    for (const good of goods) if (kind !== 'discount' || data.goods[good].dealerDiscount > 0) all.push({ kind, good });
  all.push({ kind: 'discountAll' });
  ranks('stockAll');
  ranks('buyerStockAll');
  ranks('sellChanceAll');
  return all;
}

/** Deals the Dealer could offer right now: every deal not yet bought, except that only the next
 *  rank of a ranked deal is offered (each needs the one before). */
export function eligibleDeals(data: GameData, state: RunState): DealerDeal[] {
  const unowned = allDeals(data).filter((d) => !owns(state, d));
  return unowned.filter(
    (d) => !isRanked(d) || !unowned.some((o) => o.kind === d.kind && isRanked(o) && o.tier < d.tier),
  );
}

/** Today's Dealer visit, or null. He only comes once you've earned stars; his first visit is
 *  guaranteed, after that it's CONFIG.dealer.chance per day. He brings up to CONFIG.dealer.offers
 *  distinct deals: for each, a kind is picked among the kinds still available (evenly, or by
 *  CONFIG.dealer.weight), then a deal of that kind (which good, or the next rank). He doesn't
 *  come once there's nothing left to sell. Deterministic for (seed, day). */
export function rollDealer(data: GameData, state: RunState): DealerVisit | null {
  if (state.stats.starsEarned <= 0) return null;
  const r = rngFor(state.seed, 'dealer', state.day);
  const roll = r.next();
  if (state.dealerSeen && roll >= CONFIG.dealer.chance) return null;
  const pool = eligibleDeals(data, state);
  if (pool.length === 0) return null;
  state.dealerSeen = true;
  const locationId = state.locations[r.int(0, state.locations.length - 1)].id;
  const weight = (k: DealerDeal['kind']) => CONFIG.dealer.weight[k] ?? 1;
  const offers = [];
  while (offers.length < CONFIG.dealer.offers && pool.length > 0) {
    const kinds = [...new Set(pool.map((d) => d.kind))];
    let x = r.next() * kinds.reduce((sum, k) => sum + weight(k), 0);
    let i = 0;
    while (i < kinds.length - 1 && (x -= weight(kinds[i])) >= 0) i++;
    const options = pool.filter((d) => d.kind === kinds[i]);
    const deal = options[r.int(0, options.length - 1)];
    pool.splice(pool.indexOf(deal), 1);
    offers.push({ deal, cost: dealCost(deal), sold: false });
  }
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
  const allGoods = Object.keys(data.goods);
  switch (deal.kind) {
    case 'bag':
      state.capacity++;
      break;
    case 'discount':
    case 'discountAll': {
      if (deal.kind === 'discount') perks.discounts[deal.good] = data.goods[deal.good].dealerDiscount;
      else perks.discountAll += CONFIG.dealer.discountAll;
      // takes effect right away: re-price today's sellers
      for (const good of deal.kind === 'discount' ? [deal.good] : allGoods)
        forTodays(data, state, 'supplier', good, (actorId, prices) => {
          const offer = state.market[offerKey(actorId, good)];
          offer.price = sellerPrice(state, good, prices[offer.tier]);
        });
      break;
    }
    case 'stock':
    case 'stockAll': {
      const n = deal.kind === 'stock' ? CONFIG.dealer.stockStep : CONFIG.dealer.stockAll;
      if (deal.kind === 'stock') perks.stock[deal.good] = (perks.stock[deal.good] ?? 0) + n;
      else perks.stockAll += n;
      // today's sellers restock right away
      for (const good of deal.kind === 'stock' ? [deal.good] : allGoods)
        forTodays(data, state, 'supplier', good, (actorId) => {
          state.market[offerKey(actorId, good)].left += n;
        });
      break;
    }
    case 'buyerStock':
    case 'buyerStockAll': {
      const n = deal.kind === 'buyerStock' ? CONFIG.dealer.buyerStockStep : CONFIG.dealer.buyerStockAll;
      if (deal.kind === 'buyerStock') perks.buyerStock[deal.good] = (perks.buyerStock[deal.good] ?? 0) + n;
      else perks.buyerStockAll += n;
      // today's buyers want more right away
      for (const good of deal.kind === 'buyerStock' ? [deal.good] : allGoods)
        forTodays(data, state, 'buyer', good, (actorId) => {
          state.market[offerKey(actorId, good)].left += n;
        });
      break;
    }
    case 'sellChance':
      perks.sellChance[deal.good] = (perks.sellChance[deal.good] ?? 0) + CONFIG.dealer.sellChanceStep;
      break;
    case 'sellChanceAll':
      perks.sellChanceAll += CONFIG.dealer.sellChanceAll;
      break;
  }
  return true;
}

/** Run `fn` for every actor of `role` dealt in today who trades `good`. */
function forTodays(
  data: GameData,
  state: RunState,
  role: Role,
  good: string,
  fn: (actorId: string, prices: Record<string, number>) => void,
): void {
  for (const loc of state.locations)
    for (const actorId of loc.actorIds) {
      const a = data.actors[actorId];
      const ag = a.goods.find((g) => g.good === good);
      if (a.role === role && ag && state.market[offerKey(actorId, good)]) fn(actorId, ag.prices);
    }
}

/** The good a deal is about, if any (for its icon). */
export function dealGood(deal: DealerDeal): string | null {
  return 'good' in deal ? deal.good : null;
}

const ROMAN = ['I', 'II', 'III', 'IV', 'V'];

/** Short title and a one-line description for the dialog and tooltip. */
export function describeDeal(data: GameData, deal: DealerDeal): { title: string; body: string } {
  const d = CONFIG.dealer;
  switch (deal.kind) {
    case 'bag':
      return { title: `Bigger Bag ${ROMAN[deal.tier - 1]}`, body: '+1 bag slot.' };
    case 'discount': {
      const g = data.goods[deal.good];
      return { title: `${g.name} Sale`, body: `${g.name} cost $${g.dealerDiscount} less (min $1).` };
    }
    case 'stock': {
      const g = data.goods[deal.good];
      return { title: `${g.name} Surplus`, body: `+${d.stockStep} ${g.name} for sale each day.` };
    }
    case 'sellChance': {
      const pct = Math.round(d.sellChanceStep * 100);
      const g = data.goods[deal.good];
      return { title: `${g.name} Dealer`, body: `+${pct}% better deals on ${g.name}.` };
    }
    case 'buyerStock': {
      const g = data.goods[deal.good];
      return { title: `${g.name} Demand`, body: `Buyers want ${d.buyerStockStep} more ${g.name} each day.` };
    }
    case 'sellChanceAll': {
      const pct = Math.round(d.sellChanceAll * 100);
      return { title: `Deals, Deals, Everywhere ${ROMAN[deal.tier - 1]}`, body: `+${pct}% better deals on all goods.` };
    }
    case 'discountAll':
      return { title: `Clearance Sale`, body: `ALL sellers charge $${d.discountAll} less (min $1).` };
    case 'stockAll':
      return { title: `Overflowing Supply ${ROMAN[deal.tier - 1]}`, body: `EVERY seller stocks ${d.stockAll} more item each day.` };
    case 'buyerStockAll':
      return { title: `Universal Demand ${ROMAN[deal.tier - 1]}`, body: `EVERY buyer wants ${d.buyerStockAll} more item each day.` };
  }
}
