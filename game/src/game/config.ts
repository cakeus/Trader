import type { Tier } from './types';

/** Tunable rule switches. Mutable so tests can flip them. */
export const CONFIG = {
  /** Suppliers have limited daily stock and buyers limited daily demand. */
  limitStock: true,
  /** Clicking an actor trades directly (shift = max) instead of opening the trade dialog. */
  quickTrade: true,
  /** Chance of each deal tier being rolled for an actor's good on a given day (sums to 1). */
  dealWeights: { good: 0.5, great: 0.3, amazing: 0.2 } as Record<Tier, number>,
};
