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
  /** Dollars off this good's seller prices once the Dealer's discount is bought. */
  dealerDiscount: number;
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
  blurb: string;
  background: string;
  mapPos: Point;
  /** Actors dealt here each day. */
  actorSlots: number;
  /** Screen positions (top-left of the actor card) for each slot. */
  slots: Point[];
  /** Screen position (top-left of the card) for the Dealer when he visits. */
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
/** Deal kinds that come once per good. */
export type GoodKind = 'discount' | 'stock' | 'buyerStock' | 'luck';

/** One upgrade (stamp) the Dealer can sell. */
export type DealerDeal =
  | { kind: RankedKind; tier: number }
  | { kind: GoodKind; good: string }
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
  /** Dollars off seller prices, per good. */
  discounts: Record<string, number>;
  /** Added to sellers' and buyers' great and amazing weights (taken twice from bad, then good), per good. */
  luck: Record<string, number>;
  /** Extra daily stock for every seller, per good. */
  stock: Record<string, number>;
  /** Extra daily demand for every buyer, per good. */
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

export interface RunState {
  version: 10;
  seed: number;
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
