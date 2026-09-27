import type { DealerDeal, Tier } from './types';

/** Tunable rule switches. Mutable so tests can flip them. */
export const CONFIG = {
  /** Suppliers have limited daily stock and buyers limited daily demand. */
  limitStock: true,
  /** Clicking an actor trades directly (shift = max) instead of opening the trade dialog. */
  quickTrade: true,
  /** Chance of each deal tier being rolled for an actor's good on a given day (sums to 1). */
  dealWeights: { good: 0.5, great: 0.3, amazing: 0.2 } as Record<Tier, number>,
  /** Each quota is this many times the previous one (2 = doubling), rounded to $5. */
  quotaGrowth: 1.6,
  /** The star Dealer. */
  dealer: {
    /** Chance he shows up on a given day, after his guaranteed first visit. */
    chance: 0.5,
    /** Distinct deals offered per visit. */
    offers: 3,
    /** Star cost per deal kind (bag deals use bagCosts). Every deal can be bought once per run. */
    cost: { bag: 3, discount: 3, sellChance: 3, stock: 3, discountAll: 6, stockAll: 6, sellChanceAll: 6 } as Record<DealerDeal['kind'], number>,
    /** Star cost of bag upgrades I, II, III; each unlocks after the one before. */
    bagCosts: [3, 4, 5],
    /** Relative chance of a deal being drawn into a visit's offers (default 1): the rares. */
    weight: { discountAll: 0.25, stockAll: 0.25, sellChanceAll: 0.25 } as Partial<Record<DealerDeal['kind'], number>>,
    /** sellChance adds this to buyers' great and amazing weights for its good (taking both from good). */
    sellChanceStep: 0.05,
    /** A stock deal adds this to the daily stock of every seller of its good. */
    stockStep: 1,
    /** The rare all-goods deals: $ off every seller and extra stock for every seller. Stack with per-good deals. */
    discountAll: 1,
    stockAll: 1,
    /** The rare better-buyers deal: added to every buyer's great and amazing weights. Stacks with sellChance. */
    sellChanceAll: 0.1,
  },
};
