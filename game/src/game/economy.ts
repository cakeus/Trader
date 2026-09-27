import { type Rng, rngFor } from '../engine/rng';
import { CONFIG } from './config';
import { type GameData, type Offer, type RunState, type Tier, TIERS } from './types';

export function offerKey(actorId: string, goodId: string): string {
  return `${actorId}:${goodId}`;
}

/** Weighted pick of a deal tier (CONFIG.dealWeights by default). */
export function rollTier(r: Rng, weights: Record<Tier, number> = CONFIG.dealWeights): Tier {
  const total = TIERS.reduce((sum, t) => sum + weights[t], 0);
  let x = r.next() * total;
  for (const t of TIERS) {
    x -= weights[t];
    if (x < 0) return t;
  }
  return TIERS[TIERS.length - 1];
}

/** Buyers' tier weights after the Dealer's sellChance perk: great and amazing gain, good pays for both. */
export function buyerWeights(state: RunState): Record<Tier, number> {
  const w = CONFIG.dealWeights;
  const s = state.perks.sellChance;
  return { good: Math.max(0, w.good - 2 * s), great: w.great + s, amazing: w.amazing + s };
}

/** A seller's price after the Dealer's discount on that good (never below $1). */
export function sellerPrice(state: RunState, good: string, base: number): number {
  return Math.max(1, base - (state.perks.discounts[good] ?? 0));
}

/** Today's deal tier, price and stock/demand for every actor present in the run.
 *  A pure function of (seed, day, actor, good), so it is reproducible. */
export function rollMarket(data: GameData, state: RunState): Record<string, Offer> {
  const market: Record<string, Offer> = {};
  for (const loc of state.locations) {
    for (const actorId of loc.actorIds) {
      const seller = data.actors[actorId].role === 'supplier';
      for (const ag of data.actors[actorId].goods) {
        const r = rngFor(state.seed, 'market', state.day, actorId, ag.good);
        const tier = rollTier(r, seller ? CONFIG.dealWeights : buyerWeights(state));
        market[offerKey(actorId, ag.good)] = {
          tier,
          price: seller ? sellerPrice(state, ag.good, ag.prices[tier]) : ag.prices[tier],
          left: r.int(ag.qtyMin, ag.qtyMax),
        };
      }
    }
  }
  return market;
}
