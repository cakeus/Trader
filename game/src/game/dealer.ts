import { rngFor } from '../engine/rng';
import { CONFIG } from './config';
import { offerKey, sellerPrice } from './economy';
import type { DealerDeal, DealerVisit, GameData, RunState } from './types';

export const BAG_TIERS = 3;

/** Stable id for a deal, used to remember which ones were bought. */
export function dealKey(deal: DealerDeal): string {
  switch (deal.kind) {
    case 'bag':
      return `bag:${deal.tier}`;
    case 'discount':
    case 'stock':
    case 'sellChance':
      return `${deal.kind}:${deal.good}`;
    default:
      return deal.kind;
  }
}

export function owns(state: RunState, deal: DealerDeal): boolean {
  return state.perks.owned.includes(dealKey(deal));
}

/** The rare deals that affect every good. */
export function isRare(deal: DealerDeal): boolean {
  return deal.kind === 'discountAll' || deal.kind === 'stockAll' || deal.kind === 'sellChanceAll';
}

export function dealCost(deal: DealerDeal): number {
  return deal.kind === 'bag' ? CONFIG.dealer.bagCosts[deal.tier - 1] : CONFIG.dealer.cost[deal.kind];
}

/** Deals the Dealer could offer right now. Every deal can be bought once per run: the next bag
 *  upgrade (each needs the one before), a discount and extra stock per good, better buyers, and
 *  the rare all-goods discount and stock deals. */
export function eligibleDeals(data: GameData, state: RunState): DealerDeal[] {
  const goods = Object.keys(data.goods).sort();
  const all: DealerDeal[] = [];
  // only the next bag upgrade
  const nextBag = Array.from({ length: BAG_TIERS }, (_, i) => i + 1).find((tier) => !owns(state, { kind: 'bag', tier }));
  if (nextBag) all.push({ kind: 'bag', tier: nextBag });
  for (const good of goods) if (data.goods[good].dealerDiscount > 0) all.push({ kind: 'discount', good });
  for (const good of goods) all.push({ kind: 'stock', good });
  for (const good of goods) all.push({ kind: 'sellChance', good });
  all.push({ kind: 'discountAll' }, { kind: 'stockAll' }, { kind: 'sellChanceAll' });
  return all.filter((d) => !owns(state, d));
}

/** Today's Dealer visit, or null. He only comes once you've earned stars; his first visit is
 *  guaranteed, after that it's CONFIG.dealer.chance per day. He brings up to CONFIG.dealer.offers
 *  distinct deals, drawn by CONFIG.dealer.weight (rares are less likely), and doesn't come once
 *  there's nothing left to sell. Deterministic for (seed, day). */
export function rollDealer(data: GameData, state: RunState): DealerVisit | null {
  if (state.stats.starsEarned <= 0) return null;
  const r = rngFor(state.seed, 'dealer', state.day);
  const roll = r.next();
  if (state.dealerSeen && roll >= CONFIG.dealer.chance) return null;
  const pool = eligibleDeals(data, state);
  if (pool.length === 0) return null;
  state.dealerSeen = true;
  const locationId = state.locations[r.int(0, state.locations.length - 1)].id;
  const weight = (d: DealerDeal) => CONFIG.dealer.weight[d.kind] ?? 1;
  const offers = [];
  while (offers.length < CONFIG.dealer.offers && pool.length > 0) {
    let x = r.next() * pool.reduce((sum, d) => sum + weight(d), 0);
    let i = 0;
    while (i < pool.length - 1 && (x -= weight(pool[i])) >= 0) i++;
    const [deal] = pool.splice(i, 1);
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
        forTodaysSellers(data, state, good, (actorId, prices) => {
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
        forTodaysSellers(data, state, good, (actorId) => {
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

function forTodaysSellers(
  data: GameData,
  state: RunState,
  good: string,
  fn: (actorId: string, prices: Record<string, number>) => void,
): void {
  for (const loc of state.locations)
    for (const actorId of loc.actorIds) {
      const a = data.actors[actorId];
      const ag = a.goods.find((g) => g.good === good);
      if (a.role === 'supplier' && ag && state.market[offerKey(actorId, good)]) fn(actorId, ag.prices);
    }
}

/** The good a deal is about, if any (for its icon). */
export function dealGood(deal: DealerDeal): string | null {
  return deal.kind === 'discount' || deal.kind === 'stock' || deal.kind === 'sellChance' ? deal.good : null;
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
      return { title: `${g.name} Dealer`, body: `+${pct}% more deals on ${g.name}.` };
    }
    case 'sellChanceAll': {
      const pct = Math.round(d.sellChanceAll * 100);
      return { title: 'Deals, Deals, Everyone', body: `+${pct}% Deals on all goods.` };
    }
    case 'discountAll':
      return { title: `Clearnace Sale`, body: `ALL sellers charge $${d.discountAll} less (min $1).` };
    case 'stockAll':
      return { title: `Overflowing Supply`, body: `EVERY seller stocks ${d.stockAll} more item each day.` };
  }
}
