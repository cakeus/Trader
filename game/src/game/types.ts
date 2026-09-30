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

/** Animated weather drawn over the map and the locations. `lanterns` is drifting lantern light
 *  (plus fireflies and twinkling stars where a place has them); `fireworks` adds bursts above it;
 *  `blizzard` is the snow, thicker and faster. */
export type Weather = 'snow' | 'blizzard' | 'rain' | 'lanterns' | 'fireworks';

/** A place's night-sky extras (on the map: its area; at a location: that location), used by the
 *  lantern weather. */
export interface WeatherSpots {
  /** Path of a JSON list of `[x, y]` stars baked into the background, written by its art script. */
  stars?: string;
  /** The stars, loaded from `stars` by `loadData`. */
  starPoints?: [number, number][];
  /** Where fireflies wander (over greenery). */
  fireflies?: { x: number; y: number; w: number; h: number };
}

/** One location a day is bustling (Fireworks Night): an extra actor and better prices both ways. */
export interface Bustling {
  /** Extra actors dealt there. */
  extraActors: number;
  /** Buyers there pay this much more (0.25 = +25%). */
  buyBonus: number;
  /** Sellers there charge this much less. */
  sellDiscount: number;
}

/** Something that happens in an area from `fromDay` until the run leaves it. */
export interface AreaEvent {
  id: string;
  /** Title of the notice shown the first morning it's on. */
  name: string;
  blurb: string;
  fromDay: number;
  /** Replaces the area's weather while it lasts. */
  weather?: Weather;
  /** Every buyer takes at most this many units of its good a day. */
  buyerLimit?: number;
  /** One location a day is bustling. */
  bustling?: Bustling;
  /** One location a day is snowed in: the map doesn't show what's there until you go. */
  snowedIn?: boolean;
}

/** A region with its own map, locations and goods. The run moves on to the next one on `fromDay`. */
export interface AreaDef extends WeatherSpots {
  id: string;
  name: string;
  blurb: string;
  map: string;
  /** Background music, looped while the run is here (the first area's also plays on the title screen). */
  music: string;
  fromDay: number;
  /** Animated weather drawn over the map. */
  weather?: Weather;
  /** Events that start partway through the stay (the latest one started is the one on). */
  events?: AreaEvent[];
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

export interface LocationDef extends WeatherSpots {
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
  /** A buyer whose demand today's event caps (at `left`), even with CONFIG.limitDemand off. */
  capped?: boolean;
  /** The price includes today's bustling bonus or discount (Fireworks Night). */
  bustling?: boolean;
  /** Units sold to this buyer today, and whether it has paid the Tip Jar stamp's tip. */
  sold?: number;
  tipped?: boolean;
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
  /** Total sale price minus what was paid, over every unit sold (optional: older saves). */
  profit?: number;
  /** What was lost on units sold below what was paid. */
  losses?: number;
  /** Sales today, and the most made on a single day. */
  daySales?: number;
  bestDaySales?: number;
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
/** Deal kinds that come once, with no rank or category. */
export type SingleKind =
  | 'discountAll' | 'dailyDiscount' | 'tip' | 'cantGetEnough' | 'collector'
  | 'birdsEye' | 'haggler' | 'fannyPack' | 'packedHouse' | 'cramazing' | 'mixedBag' | 'lastCall'
  | 'bigTipper' | 'fuzzyDice' | 'sleepingBag' | 'campFire' | 'monocle' | 'detour' | 'vintage'
  | 'cleanSweep' | 'flipper' | 'perfectPlanner' | 'dumpTruck';

/** How rare a stamp is: rarer ones come up more often as the weeks go by (CONFIG.dealer.rarityOdds). */
export type Rarity = 'common' | 'rare' | 'epic';
export const RARITIES: Rarity[] = ['common', 'rare', 'epic'];

/** One upgrade (stamp) the Dealer can sell. */
export type DealerDeal =
  | { kind: RankedKind; tier: number }
  | { kind: CategoryKind; category: string }
  | { kind: SingleKind };

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
  /** Dollars off every seller price and extra daily demand for every buyer (the all-goods deals). */
  discountAll: number;
  buyerStockAll: number;
  /** Overflowing Supply ranks owned: each multiplies sellers' stock by CONFIG.dealer.stockAll. */
  stockAll: number;
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
  version: 13;
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
  /** Has anything been bought today? (The Daily Discount stamp halves the first buy.) Optional so
   *  older saves still load. */
  boughtToday?: boolean;
  /** Has the Dealer made his (guaranteed) first visit yet? */
  dealerSeen: boolean;
  /** Set when a quota is met: the Dealer's next visit includes a deal costing at most
   *  CONFIG.dealer.cheapAfterQuota. Optional so saves from before it still load. */
  dealerCheapOwed?: boolean;
  /** The Dealer's stamp decks, one per rarity: the cards not yet drawn, in order (see rollDealer). */
  stampDecks?: Partial<Record<Rarity, string[]>>;
  /** Units sold today (Haggler), and the goods sold today (Mixed Bag). */
  soldToday?: number;
  soldGoodsToday?: string[];
  /** The location left by today's Detour, or null. */
  detoured?: string | null;
  /** The location with an extra actor today (Packed House), or null. */
  packedAt?: string | null;
  /** The bustling location today (Fireworks Night), or null. Optional so older saves still load. */
  bustlingAt?: string | null;
  /** The snowed-in location today (Blizzard), or null. Optional so older saves still load. */
  snowedAt?: string | null;
  /** The good whose buyers are all bad today (the weekly bad day), or null, and the last week
   *  (0-based) that had one. Optional so older saves still load. */
  badGood?: string | null;
  badWeek?: number;
  /** Ids of the area events whose notice has been shown. Optional so older saves still load. */
  eventsSeen?: string[];
  status: 'active' | 'failed';
}

export type EndDayResult = 'next' | 'quotaPassed' | 'failed';
