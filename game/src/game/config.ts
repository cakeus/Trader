import type { DealerDeal, Tier } from './types';

/** Tunable rule switches. Mutable so tests can flip them. */
export const CONFIG = {
  /** Suppliers have limited daily stock and buyers limited daily demand. */
  limitStock: true,
  /** Clicking an actor trades directly (shift = max) instead of opening the trade dialog. */
  quickTrade: true,
  /** Chance of each deal tier being rolled for an actor's good on a given day (sums to 1). */
  dealWeights: { good: 0.5, great: 0.3, amazing: 0.2 } as Record<Tier, number>,
  /** The star Dealer. */
  dealer: {
    /** Chance he shows up on a given day, after his guaranteed first visit. */
    chance: 0.5,
    /** Star cost per deal kind. */
    cost: { bag: 3, discount: 3, sellChance: 3 } as Record<DealerDeal['kind'], number>,
    /** Each sellChance deal adds this to buyers' great and amazing weights (taking both from good). */
    sellChanceStep: 0.05,
    /** sellChance is no longer offered once it would push buyers' good weight below this. */
    minGoodWeight: 0.1,
  },
};
