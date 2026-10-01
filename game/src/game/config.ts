import type { DealerDeal, RankedKind, Rarity, Tier } from './types';

/** Tunable rule switches. Mutable so tests can flip them. */
export const CONFIG = {
  /** Sellers have limited daily stock. */
  limitStock: true,
  /** Buyers have limited daily demand (off: they take everything you bring). */
  limitDemand: false,
  /** Clicking an actor trades directly (shift = max) instead of opening the trade dialog. */
  quickTrade: true,
  /** Chance of each deal tier being rolled for a seller's or buyer's good on a given day (sums to 1).
   *  Buyers never roll bad: once a week, every buyer of one good from the bag is bad instead
   *  (`rollBadDay` in run.ts). A bad buyer pays $1 under the good's great seller price
   *  (strawberry: the great seller price), so selling to one loses unless you bought at amazing. */
  dealWeights: { good: 0.5, great: 0.3, amazing: 0.2 } as Partial<Record<Tier, number>>,
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
  stockRange: { food: [3, 3], treasure: [2, 3], music: [1, 3], clothing: [1, 1] } as Record<string, [number, number]>,
  /** Each week's quota, in order (one per 7 days; the last is due on the run's last day). Cash is
   *  reset to the area's starting cash after each one, so each is met from that. */
  quotas: [25, 30, 35, 60, 70, 80, 150, 190, 250],
  /** A met quota pays one bonus star for each of these it's beaten by (0.1 = 10% over). */
  bonusSteps: [0.1, 0.25, 0.5],
  /** The star Dealer. */
  dealer: {
    /** Chance he shows up on a given day, after his guaranteed first visit. */
    chance: 0.5,
    /** Distinct deals offered per visit. */
    offers: 3,
    /** Deal kinds he doesn't offer for now (stamps already owned keep working). */
    disabled: ['discount', 'discountAll', 'buyerStock', 'buyerStockAll','lastCall'] as DealerDeal['kind'][],
    /** His first visit after each met quota has at least one deal costing this many stars or fewer. */
    cheapAfterQuota: 5,
    /** Star cost per deal kind, the same for every rank (bag deals use bagCosts). Every deal can be
     *  bought once per run. */
    cost: {
      bag: 3, discount: 3, luck: 3, stock: 2, buyerStock: 3, sellBonus: 1,
      discountAll: 6, stockAll: 6, buyerStockAll: 6, luckAll: 6, tip: 7,
      dailyDiscount: 8, cantGetEnough: 8, collector: 8,
      birdsEye: 8, haggler: 8, fannyPack: 7, packedHouse: 8, cramazing: 9, mixedBag: 8, lastCall: 8,
      bigTipper: 6, fuzzyDice: 8, sleepingBag: 8, campFire: 8, monocle: 8, detour: 10, vintage: 8,
      cleanSweep: 8, flipper: 8, perfectPlanner: 6, dumpTruck: 8, nestEgg: 5, goldenGoose: 8,
    } as Record<DealerDeal['kind'], number>,
    /** Each kind's rarity (unlisted kinds are common). Each rarity has its own stamp deck. */
    rarity: {
      luckAll: 'rare', stockAll: 'rare', 
      dailyDiscount: 'rare', cantGetEnough: 'rare', collector: 'rare',tip: 'rare',
      birdsEye: 'rare', haggler: 'rare', fannyPack: 'rare', packedHouse: 'rare', cramazing: 'rare',
      mixedBag: 'rare', lastCall: 'rare', bigTipper: 'rare', fuzzyDice: 'rare', sleepingBag: 'rare',
      campFire: 'rare', monocle: 'rare', detour: 'rare', vintage: 'rare', cleanSweep: 'rare',
      flipper: 'rare', perfectPlanner: 'rare', dumpTruck: 'rare', goldenGoose: 'rare',
    } as Partial<Record<DealerDeal['kind'], Rarity>>,
    /** Chance each stamp he draws is epic or rare: `base` in week 2 (the first week he comes), plus
     *  `perWeek` for every week after. The rest are common. */
    rarityOdds: {
      epic: { base: 0.04, perWeek: 0.02 },
      rare: { base: 0.08, perWeek: 0.04 },
    } as Record<Exclude<Rarity, 'common'>, { base: number; perWeek: number }>,
    /** Star cost of bag upgrades I, II, III, IV; each unlocks after the one before. */
    bagCosts: [3, 5, 7, 9],
    /** Bag slots added by bag upgrades I, II, III, IV (8 in all). */
    bagSlots: [2, 2, 2, 2],
    /** How many ranks the ranked deals have; only the next rank is ever offered. */
    ranks: { bag: 4, stockAll: 1, buyerStockAll: 3, luckAll: 3 } as Record<RankedKind, number>,
    /** A luck deal adds this to the great and amazing weights of every seller and buyer of its good
     *  (taking both from good). */
    luckStep: 0.05,
    /** A stock deal adds this (by category) to the daily stock of every seller of its good. */
    stockStep: { food: 3, treasure: 2, music: 2, clothing: 1 } as Record<string, number>,
    /** A sellBonus deal adds this $ (by category) to every buyer's price for its good (the same in
     *  every area). */
    sellBonus: { food: 1, treasure: 1, music: 2, clothing: 3 } as Record<string, number>,
    /** The sellBonus deals' titles, by category. */
    sellBonusNames: { food: 'Foodie', treasure: 'Treasure Hunter', music: 'Music Lover', clothing: 'Fashionista' } as Record<string, string>,
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
    /** Stamp Collector: extra stamps Nox brings each visit (added to his table the moment it's bought). */
    collectorOffers: 1,
    /** Can't Get Enough: a buyer's price goes up this much after every unit sold to it (for the day). */
    cantGetEnoughStep: 1,
    /** Haggler: the first sale of the day pays this much extra (0.5 = +50%), less `hagglerStep`
     *  for every unit sold before it that day (down to nothing). Applied last, on top of everything. */
    hagglerStart: 0.3,
    hagglerStep: 0.15,
    /** Fanny Pack: $ at the end of the day per different good in the bag. */
    fannyPack: 1,
    /** Mixed Bag: $ tip for the first unit of each good sold in a day. */
    mixedBagTip: 3,
    /** Big Tipper: every tip is multiplied by this. */
    bigTipper: 3,
    /** Fuzzy Dice: chance per unit sold that the buyer jumps to an Amazing deal for the day. */
    fuzzyDiceChance: 1 / 6,
    /** Sleeping Bag: share of what the bag cost that's paid for a day without trading. */
    sleepingBag: 0.05,
    /** Monocle: added to the price multiplier of every buy and sell. */
    monocle: 0.25,
    /** Vintage: added to a unit's sell multiplier per day it's been in the bag. */
    vintagePerDay: 0.05,
    /** Clean Sweep: $ per bag slot for ending the day with an empty bag. */
    cleanSweep: 1,
    /** Flipper: $ added to the sell price of units bought yesterday. */
    flipper: 1,
    /** Cramazing: an Amazing deal's difference from the Good price is multiplied by this. */
    cramazing: 1.5,
    /** Nest Egg: $ added to the starting cash every week. */
    nestEgg: 10,
  },
};
