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
  dealWeights: { good: 0.5, great: 0.3, amazing: 0.2 } as Partial<Record<Tier, number>>,
  /** The same for a buyer's good. A bad buyer pays $1 under the good's great seller price
   *  (strawberry: the great seller price), so selling to one loses unless you bought at amazing. */
  buyerDealWeights: { bad: 0.2, good: 0.4, great: 0.25, amazing: 0.15 } as Record<Tier, number>,
  /** Buyer weights during the first quota (days 1–7): half the bad buyers, the rest turned good. */
  firstQuotaBuyerDealWeights: { bad: 0.1, good: 0.5, great: 0.25, amazing: 0.15 } as Record<Tier, number>,
  /** Deal tiers are dealt from a shuffled deck per role (seller / buyer) instead of rolled
   *  independently, so each cycle of `deckSize` cards follows the tier weights closely. Only the
   *  location you visit uses up cards, so every card dealt is one you see. Each quota starts a
   *  fresh deck, so luck in one quota isn't paid back in the next. */
  tierDeck: true,
  /** Cards per deck cycle: about one quota's worth for each role. At 10, a 10% weight is exactly
   *  one card per cycle; a 25% weight comes out as 2 or 3. */
  deckSize: 10,
  /** A seller's base daily stock by its good's category: [min, max], rolled evenly (stock deals
   *  add on top). */
  stockRange: { food: [3, 3], treasure: [2, 3], music: [1, 3], tools: [1, 1] } as Record<string, [number, number]>,
  /** Each quota is this many times the previous one (2 = doubling), rounded to $5. */
  quotaGrowth: 1.75,
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
      bag: 3, discount: 3, luck: 3, stock: 3, buyerStock: 3,
      discountAll: 6, stockAll: 6, buyerStockAll: 6, luckAll: 8,
      dailyDiscount: 5, tip: 5, cantGetEnough: 5,
    } as Record<DealerDeal['kind'], number>,
    /** Star cost of bag upgrades I, II, III, IV; each unlocks after the one before. */
    bagCosts: [3, 5, 7, 9],
    /** Bag slots added by bag upgrades I, II, III, IV (8 in all). */
    bagSlots: [2, 2, 2, 2],
    /** How many ranks the ranked deals have; only the next rank is ever offered. */
    ranks: { bag: 4, stockAll: 1, buyerStockAll: 3, luckAll: 3 } as Record<RankedKind, number>,
    /** A luck deal adds this to the great and amazing weights of every seller and buyer of its good
     *  (taking both from bad, then good). */
    luckStep: 0.05,
    /** A stock deal adds this (by category) to the daily stock of every seller of its good. */
    stockStep: { food: 3, treasure: 2, music: 2, tools: 1 } as Record<string, number>,
    /** A buyerStock deal adds this to the daily demand of every buyer of its good. */
    buyerStockStep: 2,
    /** The all-goods deals, per rank: $ off every seller and extra demand for every buyer. They
     *  stack with the per-good deals. */
    discountAll: 1,
    buyerStockAll: 1,
    /** Overflowing Supply multiplies every seller's daily stock by this (per rank), after the
     *  per-category stock deals are added, so it does the most for food. */
    stockAll: 2,
    /** The all-goods luck deal, per rank: added to every seller's and buyer's great and amazing
     *  weights. Stacks with luck. */
    luckAll: 0.05,
    /** Tip Jar: a buyer pays this extra once you've sold it `tipAfter` goods in a day
     *  (once per buyer per day). */
    tip: 5,
    tipAfter: 2,
    /** Can't Get Enough: a buyer's price goes up this much after every unit sold to it (for the day). */
    cantGetEnoughStep: 1,
  },
};
