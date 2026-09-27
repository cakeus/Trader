import type { DealerDeal, RankedKind, Tier } from './types';

/** Tunable rule switches. Mutable so tests can flip them. */
export const CONFIG = {
  /** Sellers have limited daily stock. */
  limitStock: true,
  /** Buyers have limited daily demand (off: they take everything you bring). */
  limitDemand: false,
  /** Clicking an actor trades directly (shift = max) instead of opening the trade dialog. */
  quickTrade: true,
  /** Chance of each deal tier being rolled for a seller's good on a given day (sums to 1). */
  dealWeights: { bad: 0, good: 0.5, great: 0.3, amazing: 0.2 } as Record<Tier, number>,
  /** The same for a buyer's good. A bad buyer pays the good's great seller price, so selling to one
   *  only breaks even on a great buy and profits on an amazing one. */
  buyerDealWeights: { bad: 0.2, good: 0.4, great: 0.25, amazing: 0.15 } as Record<Tier, number>,
  /** Chance of each base daily stock for a seller's good (stock deals add on top). */
  stockWeights: { 1: 0.5, 2: 0.3, 3: 0.2 } as Record<number, number>,
  /** Each quota is this many times the previous one (2 = doubling), rounded to $5. */
  quotaGrowth: 1.6,
  /** The star Dealer. */
  dealer: {
    /** Chance he shows up on a given day, after his guaranteed first visit. */
    chance: 0.5,
    /** Distinct deals offered per visit. */
    offers: 3,
    /** Deal kinds he doesn't offer for now (stamps already owned keep working). */
    disabled: ['discount', 'discountAll', 'buyerStock', 'buyerStockAll'] as DealerDeal['kind'][],
    /** His first visit after each met quota has at least one deal costing this many stars or fewer. */
    cheapAfterQuota: 5,
    /** Star cost per deal kind, the same for every rank (bag deals use bagCosts). Every deal can be
     *  bought once per run. */
    cost: {
      bag: 3, discount: 3, sellChance: 3, stock: 3, buyerStock: 3,
      discountAll: 6, stockAll: 6, buyerStockAll: 6, sellChanceAll: 6,
    } as Record<DealerDeal['kind'], number>,
    /** Star cost of bag upgrades I, II, III; each unlocks after the one before. */
    bagCosts: [3, 4, 5],
    /** How many ranks the ranked deals have; only the next rank is ever offered. */
    ranks: { bag: 3, stockAll: 3, buyerStockAll: 3, sellChanceAll: 3 } as Record<RankedKind, number>,
    /** Relative chance of each deal kind being picked for an offer slot (default 1). The good (or the
     *  next rank) is then picked evenly within the kind. */
    weight: {} as Partial<Record<DealerDeal['kind'], number>>,
    /** sellChance adds this to buyers' great and amazing weights for its good (taking both from bad, then good). */
    sellChanceStep: 0.1,
    /** A stock deal adds this to the daily stock of every seller of its good. */
    stockStep: 2,
    /** A buyerStock deal adds this to the daily demand of every buyer of its good. */
    buyerStockStep: 2,
    /** The all-goods deals, per rank: $ off every seller, extra stock for every seller, and extra
     *  demand for every buyer. They stack with the per-good deals. */
    discountAll: 1,
    stockAll: 1,
    buyerStockAll: 1,
    /** The all-goods better-buyers deal, per rank: added to every buyer's great and amazing weights.
     *  Stacks with sellChance. */
    sellChanceAll: 0.1,
  },
};
