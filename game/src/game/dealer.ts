import { rngFor } from '../engine/rng';
import { CONFIG } from './config';
import { buyerWeights, sellerPrice } from './economy';
import type { DealerDeal, DealerVisit, GameData, RunState } from './types';

/** Deals the Dealer could offer right now: always a bag slot, a discount on any good not yet
 *  discounted (they don't stack), and better selling odds while buyers' good weight allows it. */
export function eligibleDeals(data: GameData, state: RunState): DealerDeal[] {
  const deals: DealerDeal[] = [{ kind: 'bag' }];
  for (const good of Object.keys(data.goods).sort())
    if (!state.perks.discounts[good] && data.goods[good].dealerDiscount > 0) deals.push({ kind: 'discount', good });
  if (buyerWeights(state).good - 2 * CONFIG.dealer.sellChanceStep >= CONFIG.dealer.minGoodWeight - 1e-9)
    deals.push({ kind: 'sellChance' });
  return deals;
}

/** Today's Dealer visit, or null. He only comes once you've earned stars; his first visit is
 *  guaranteed, after that it's CONFIG.dealer.chance per day. Deterministic for (seed, day). */
export function rollDealer(data: GameData, state: RunState): DealerVisit | null {
  if (state.stats.starsEarned <= 0) return null;
  const r = rngFor(state.seed, 'dealer', state.day);
  const roll = r.next();
  if (state.dealerSeen && roll >= CONFIG.dealer.chance) return null;
  state.dealerSeen = true;
  const locationId = state.locations[r.int(0, state.locations.length - 1)].id;
  const deals = eligibleDeals(data, state);
  const deal = deals[r.int(0, deals.length - 1)];
  return { locationId, deal, cost: CONFIG.dealer.cost[deal.kind], sold: false };
}

export type DealerBlock = 'sold' | 'noStars' | null;

export function dealerBlock(state: RunState): DealerBlock {
  const d = state.dealer;
  if (!d || d.sold) return 'sold';
  if (state.stars < d.cost) return 'noStars';
  return null;
}

/** Buy today's deal. Returns false if blocked. */
export function buyDealerDeal(data: GameData, state: RunState): boolean {
  const d = state.dealer;
  if (!d || dealerBlock(state) !== null) return false;
  state.stars -= d.cost;
  d.sold = true;
  const deal = d.deal;
  if (deal.kind === 'bag') {
    state.capacity++;
  } else if (deal.kind === 'discount') {
    state.perks.discounts[deal.good] = data.goods[deal.good].dealerDiscount;
    // takes effect right away: re-price today's sellers of that good
    for (const loc of state.locations)
      for (const actorId of loc.actorIds) {
        const a = data.actors[actorId];
        if (a.role !== 'supplier') continue;
        for (const ag of a.goods) {
          const o = state.market[`${actorId}:${ag.good}`];
          if (ag.good === deal.good && o) o.price = sellerPrice(state, ag.good, ag.prices[o.tier]);
        }
      }
  } else {
    state.perks.sellChance += CONFIG.dealer.sellChanceStep;
  }
  return true;
}

/** Short title and a longer description for tooltips and the dialog. */
export function describeDeal(data: GameData, deal: DealerDeal): { title: string; body: string } {
  switch (deal.kind) {
    case 'bag':
      return { title: '+1 bag slot', body: 'A roomier bag. Carry one more unit, forever.' };
    case 'discount': {
      const g = data.goods[deal.good];
      return {
        title: `$${g.dealerDiscount} off ${g.name}`,
        body: `Every seller charges you $${g.dealerDiscount} less for ${g.name} (never below $1).`,
      };
    }
    case 'sellChance': {
      const pct = Math.round(CONFIG.dealer.sellChanceStep * 100);
      return {
        title: 'Better buyers',
        body: `Buyers are +${pct}% likelier to offer Great and +${pct}% likelier to offer Amazing deals, from tomorrow.`,
      };
    }
  }
}
