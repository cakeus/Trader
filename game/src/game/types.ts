export type Role = 'supplier' | 'buyer';

export interface GoodDef {
  id: string;
  name: string;
  icon: string;
  /** 8x8 icon for compact lists. */
  iconSmall: string;
  /** 16x16 icon for the map tooltip. */
  iconMedium: string;
  blurb: string;
  /** Its category (`categories.json`): stamps apply per category, so they carry across areas. */
  category: string;
  /** The area it's traded in (`areas.json`). */
  area: string;
  /** Dollars off this good's seller prices once the Dealer's discount is bought. */
  dealerDiscount: number;
}

/** A kind of good with one good in every area (Food: Strawberry, Hot Cocoa). */
export interface CategoryDef {
  id: string;
  name: string;
}

/** A region with its own map, locations and goods. The run moves on to the next one on `fromDay`. */
export interface AreaDef {
  id: string;
  name: string;
  blurb: string;
  map: string;
  /** Background music, looped while the run is here (the first area's also plays on the title screen). */
  music: string;
  fromDay: number;
  /** Animated weather drawn over the map. */
  weather?: 'snow';
}

/** Deal tier rolled per actor/good each day. */
export type Tier = 'bad' | 'good' | 'great' | 'amazing';
export const TIERS: Tier[] = ['bad', 'good', 'great', 'amazing'];

/** One good an actor trades. Each day a tier is rolled and its price applies (only buyers have
 *  a bad price). qty = daily stock (suppliers) or daily demand (buyers). */
export interface ActorGood {
  good: string;
  prices: Record<Exclude<Tier, 'bad'>, number> & { bad?: number };
  qtyMin: number;
  qtyMax: number;
}

/** An actor trades one good (`goods` has one entry), so it belongs to that good's area. */
export interface ActorDef {
  id: string;
  name: string;
  role: Role;
  portrait: string;
  blurb: string;
  goods: ActorGood[];
}

export interface Point {
  x: number;
  y: number;
}

export interface LocationDef {
  id: string;
  name: string;
  area: string;
  blurb: string;
  background: string;
  mapPos: Point;
  /** Actors dealt here each day. */
  actorSlots: number;
  /** Screen positions (top-left of the actor card) for each slot. */
  slots: Point[];
  /** Where the Dealer stood when he was a 4th card; only used for days saved before he took an actor's spot. */
  dealerSlot: Point;
}

/** The star Dealer: not a trader, so he lives outside `actors`. */
export interface DealerDef {
  id: string;
  name: string;
  portrait: string;
  blurb: string;
}

export interface GameData {
  goods: Record<string, GoodDef>;
  actors: Record<string, ActorDef>;
  locations: Record<string, LocationDef>;
  dealer: DealerDef;
  categories: Record<string, CategoryDef>;
  areas: Record<string, AreaDef>;
}

/** Today's terms for one actor + good. */
export interface Offer {
  tier: Tier;
  price: number;
  /** Remaining stock (supplier) or remaining demand (buyer). */
  left: number;
}

export interface Quota {
  index: number;
  amount: number;
  dueDay: number;
  /** Latches true once cash reaches `amount`, even if cash later drops. */
  met: boolean;
  /** Base stars for meeting this quota. */
  stars: number;
  /** Set when the quota is met: total stars given, and how many of them were the early bonus. */
  starsAwarded?: number;
  earlyBonus?: number;
  /** Met, but the stars aren't paid until the end of the due day. */
  starsPending?: boolean;
}

export interface RunLocation {
  id: string;
  /** Actors present today; re-dealt every day. */
  actorIds: string[];
}

export interface RunStats {
  bought: number;
  sold: number;
  quotasMet: number;
  starsEarned: number;
}

export interface BagItem {
  good: string;
  paid: number;
  day: number;
}

/** Deal kinds bought in ranks (I, II, III...); each rank needs the one before. */
export type RankedKind = 'bag' | 'stockAll' | 'buyerStockAll' | 'luckAll';
/** Deal kinds that come once per category (they apply to that category's good in every area). */
export type CategoryKind = 'discount' | 'stock' | 'buyerStock' | 'luck';

/** One upgrade (stamp) the Dealer can sell. */
export type DealerDeal =
  | { kind: RankedKind; tier: number }
  | { kind: CategoryKind; category: string }
  | { kind: 'discountAll' };

/** One of the Dealer's offers today. */
export interface DealerOffer {
  deal: DealerDeal;
  cost: number;
  sold: boolean;
}

/** Today's Dealer visit. */
export interface DealerVisit {
  locationId: string;
  /** Distinct deals, each bought separately. */
  offers: DealerOffer[];
}

/** Permanent upgrades bought from the Dealer this run. */
export interface Perks {
  /** Per category: 1 once its discount is bought (sellers take each good's `dealerDiscount` off). */
  discounts: Record<string, number>;
  /** Added to sellers' and buyers' great and amazing weights (taken twice from bad, then good), per category. */
  luck: Record<string, number>;
  /** Extra daily stock for every seller, per category. */
  stock: Record<string, number>;
  /** Extra daily demand for every buyer, per category. */
  buyerStock: Record<string, number>;
  /** Dollars off every seller price, extra daily stock for every seller, and extra daily demand
   *  for every buyer (the all-goods deals). */
  discountAll: number;
  stockAll: number;
  buyerStockAll: number;
  /** Added to every seller's and buyer's great and amazing weights (the all-goods luck deal). */
  luckAll: number;
  /** Keys (`dealKey`) of every deal bought this run; each deal can be bought only once. */
  owned: string[];
}

/** The move to a new area, shown on the arrival screen until dismissed. */
export interface AreaMove {
  area: string;
  /** Units left in the bag, bought back at what was paid for them. */
  units: number;
  refund: number;
}

export interface RunState {
  version: 12;
  seed: number;
  /** The area the run is in (`areas.json`). */
  area: string;
  /** Set when the run moves to a new area, until the arrival screen is dismissed. */
  moved?: AreaMove | null;
  day: number;
  cash: number;
  capacity: number;
  /** One unit per slot; no stacking. */
  inventory: BagItem[];
  locations: RunLocation[];
  quota: Quota;
  /** Location chosen for today, or null while still on the map. */
  visited: string | null;
  /** Today's offers keyed by `${actorId}:${goodId}`. */
  market: Record<string, Offer>;
  /** Tier deck cards used so far this quota, per role (CONFIG.tierDeck); the decks come from the seed. */
  deck: Record<Role, number>;
  stats: RunStats;
  /** Unspent stars. */
  stars: number;
  perks: Perks;
  /** Where the Dealer is today, or null if he isn't around. */
  dealer: DealerVisit | null;
  /** Has the Dealer made his (guaranteed) first visit yet? */
  dealerSeen: boolean;
  /** Set when a quota is met: the Dealer's next visit includes a deal costing at most
   *  CONFIG.dealer.cheapAfterQuota. Optional so saves from before it still load. */
  dealerCheapOwed?: boolean;
  status: 'active' | 'failed';
}

export type EndDayResult = 'next' | 'quotaPassed' | 'failed';
