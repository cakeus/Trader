export type Role = 'supplier' | 'buyer';

export interface GoodDef {
  id: string;
  name: string;
  icon: string;
  /** 8x8 icon for compact lists. */
  iconSmall: string;
  blurb: string;
}

/** Deal tier rolled per actor/good each day. */
export type Tier = 'good' | 'great' | 'amazing';
export const TIERS: Tier[] = ['good', 'great', 'amazing'];

/** One good an actor trades. Each day a tier is rolled and its price applies.
 *  qty = daily stock (suppliers) or daily demand (buyers). */
export interface ActorGood {
  good: string;
  prices: Record<Tier, number>;
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
}

export interface GameData {
  goods: Record<string, GoodDef>;
  actors: Record<string, ActorDef>;
  locations: Record<string, LocationDef>;
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
}

export interface BagItem {
  good: string;
  paid: number;
  day: number;
}

export interface RunState {
  version: 3;
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
  stats: RunStats;
  status: 'active' | 'failed';
}

export type EndDayResult = 'next' | 'quotaPassed' | 'failed';
