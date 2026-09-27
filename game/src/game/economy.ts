import { type Rng, rngFor } from '../engine/rng';
import { CONFIG } from './config';
import { type GameData, type Offer, type RunState, type Tier, TIERS } from './types';

export function offerKey(actorId: string, goodId: string): string {
  return `${actorId}:${goodId}`;
}

/** Weighted pick of a deal tier using CONFIG.dealWeights. */
export function rollTier(r: Rng): Tier {
  const total = TIERS.reduce((sum, t) => sum + CONFIG.dealWeights[t], 0);
  let x = r.next() * total;
  for (const t of TIERS) {
    x -= CONFIG.dealWeights[t];
    if (x < 0) return t;
  }
  return TIERS[TIERS.length - 1];
}

/** Today's deal tier, price and stock/demand for every actor present in the run.
 *  A pure function of (seed, day, actor, good), so it is reproducible. */
export function rollMarket(data: GameData, state: RunState): Record<string, Offer> {
  const market: Record<string, Offer> = {};
  for (const loc of state.locations) {
    for (const actorId of loc.actorIds) {
      for (const ag of data.actors[actorId].goods) {
        const r = rngFor(state.seed, 'market', state.day, actorId, ag.good);
        const tier = rollTier(r);
        market[offerKey(actorId, ag.good)] = {
          tier,
          price: ag.prices[tier],
          left: r.int(ag.qtyMin, ag.qtyMax),
        };
      }
    }
  }
  return market;
}
