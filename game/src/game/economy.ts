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

/** Weighted pick of a seller's base daily stock (CONFIG.stockWeights). */
export function rollStock(r: Rng): number {
  const entries = Object.entries(CONFIG.stockWeights);
  const total = entries.reduce((sum, [, w]) => sum + w, 0);
  let x = r.next() * total;
  for (const [qty, w] of entries) {
    x -= w;
    if (x < 0) return Number(qty);
  }
  return Number(entries[entries.length - 1][0]);
}

/** Buyers' tier weights for a good after the Dealer's better-buyers perks (that good's, plus the
 *  all-goods one): great and amazing gain, bad pays for both, then good once bad is gone. */
export function buyerWeights(state: RunState, good: string): Record<Tier, number> {
  const w = CONFIG.buyerDealWeights;
  const s = (state.perks.sellChance[good] ?? 0) + state.perks.sellChanceAll;
  const bad = Math.max(0, w.bad - 2 * s);
  const fromGood = 2 * s - (w.bad - bad);
  return { bad, good: Math.max(0, w.good - fromGood), great: w.great + s, amazing: w.amazing + s };
}

/** A seller's price after the Dealer's discounts on that good and on everything (never below $1). */
export function sellerPrice(state: RunState, good: string, base: number): number {
  return Math.max(1, base - (state.perks.discounts[good] ?? 0) - state.perks.discountAll);
}

/** Extra daily stock a seller of `good` has from the Dealer's stock deals. */
export function extraStock(state: RunState, good: string): number {
  return (state.perks.stock[good] ?? 0) + state.perks.stockAll;
}

/** Extra daily demand a buyer of `good` has from the Dealer's demand deals. */
export function extraDemand(state: RunState, good: string): number {
  return (state.perks.buyerStock[good] ?? 0) + state.perks.buyerStockAll;
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
        const tier = rollTier(r, seller ? CONFIG.dealWeights : buyerWeights(state, ag.good));
        market[offerKey(actorId, ag.good)] = {
          tier,
          price: seller ? sellerPrice(state, ag.good, ag.prices[tier]) : ag.prices[tier],
          left: seller
            ? rollStock(r) + extraStock(state, ag.good)
            : r.int(ag.qtyMin, ag.qtyMax) + extraDemand(state, ag.good),
        };
      }
    }
  }
  return market;
}
