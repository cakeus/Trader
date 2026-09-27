import { rngFor } from '../engine/rng';
import { CONFIG } from './config';
import { dealActors } from './deal';
import { dealerBlock, rollDealer } from './dealer';
import { deckCards, offerKey, rollMarket, sellerPrice } from './economy';
import type { EndDayResult, GameData, Offer, Quota, RunState } from './types';

export const START_CASH = 10;
export const CAPACITY = 4;
export const FIRST_QUOTA = 20;
export const QUOTA_DAYS = 7;
export const RUN_LOCATIONS = 3;
/** Base stars for meeting any quota. */
export const BASE_STARS = 5;
/** Bonus stars per day a quota is met early. */
export const EARLY_STAR = 1;

export function quotaFor(index: number): Quota {
  return {
    index,
    amount: Math.round((FIRST_QUOTA * CONFIG.quotaGrowth ** index) / 5) * 5,
    dueDay: QUOTA_DAYS * (index + 1),
    met: false,
    stars: BASE_STARS,
  };
}

export function newRun(data: GameData, seed: number): RunState {
  const r = rngFor(seed, 'setup');
  const locations = r
    .shuffle(Object.keys(data.locations))
    .slice(0, RUN_LOCATIONS)
    .map((id) => ({ id, actorIds: [] as string[] }));
  const state: RunState = {
    version: 10,
    seed,
    day: 1,
    cash: START_CASH,
    capacity: CAPACITY,
    inventory: [],
    locations,
    quota: quotaFor(0),
    visited: null,
    market: {},
    deck: { supplier: 0, buyer: 0 },
    stats: { bought: 0, sold: 0, quotasMet: 0, starsEarned: 0 },
    stars: 0,
    perks: {
      discounts: {}, luck: {}, stock: {}, buyerStock: {},
      discountAll: 0, stockAll: 0, buyerStockAll: 0, luckAll: 0, owned: [],
    },
    dealer: null,
    dealerSeen: false,
    status: 'active',
  };
  startDay(data, state);
  updateQuota(state);
  return state;
}

/** See whether the Dealer visits (he takes one actor's spot at his location), deal today's actors
 *  to locations, and roll their deals.
 *  On a quota's due day, a buyer of the player's most common bag good is guaranteed to be present.
 *  On other days, if the player can't buy anything, a buyer of something in the bag is (see rescueGood).
 *  With an empty bag, no location has only buyers. */
function startDay(data: GameData, state: RunState): void {
  state.dealer = rollDealer(data, state);
  const ids = state.locations.map((l) => l.id);
  const dealerAt = state.dealer?.locationId;
  // with an empty bag, a buyers-only location has nothing for the player, so it's rerolled
  const needSeller = state.inventory.length === 0;
  const deal = (buyerOf?: string) => dealActors(data, state.seed, state.day, ids, buyerOf, dealerAt, needSeller);
  let dealt: Record<string, string[]>;
  if (state.day === state.quota.dueDay) {
    dealt = deal(guaranteedGood(data, state) ?? undefined);
  } else {
    dealt = deal();
    const rescue = rescueGood(data, state, Object.values(dealt).flat());
    if (rescue) dealt = deal(rescue);
  }
  for (const loc of state.locations) loc.actorIds = dealt[loc.id];
  state.market = rollMarket(data, state);
}

/** The bag good that gets a guaranteed buyer on due day: the most common one; ties go to
 *  the good with the higher baseline sell price (best Good-tier buyer price), then by id.
 *  Null when the bag is empty. */
export function guaranteedGood(data: GameData, state: RunState): string | null {
  const counts = new Map<string, number>();
  for (const it of state.inventory) counts.set(it.good, (counts.get(it.good) ?? 0) + 1);
  const sellPrice = (good: string) =>
    Math.max(
      0,
      ...Object.values(data.actors)
        .filter((a) => a.role === 'buyer')
        .flatMap((a) => a.goods.filter((g) => g.good === good).map((g) => g.prices.good)),
    );
  let best: string | null = null;
  for (const [good, n] of counts) {
    if (best === null) {
      best = good;
      continue;
    }
    const bn = counts.get(best)!;
    const better =
      n > bn || (n === bn && (sellPrice(good) > sellPrice(best) || (sellPrice(good) === sellPrice(best) && good < best)));
    if (better) best = good;
  }
  return best;
}

/** The lowest price any seller could charge today (its best tier, after the Dealer's discounts). */
function cheapestSellerPrice(data: GameData, state: RunState): number {
  return Math.min(
    ...Object.values(data.actors)
      .filter((a) => a.role === 'supplier')
      .flatMap((a) => a.goods.map((g) => sellerPrice(state, g.good, Math.min(...Object.values(g.prices))))),
  );
}

/** The non-due-day guarantee: if the player can't buy anything (bag full, or not enough cash for
 *  even the cheapest possible seller) and none of `dealtIds` buys anything in the bag, a random
 *  bag item's good gets a buyer dealt in. Null when there's nothing to rescue. Deterministic for
 *  (seed, day, bag). */
export function rescueGood(data: GameData, state: RunState, dealtIds: string[]): string | null {
  if (state.inventory.length === 0) return null;
  if (freeSlots(state) > 0 && state.cash >= cheapestSellerPrice(data, state)) return null;
  const bag = new Set(state.inventory.map((it) => it.good));
  const canSell = dealtIds.some((id) => {
    const a = data.actors[id];
    return a.role === 'buyer' && a.goods.some((g) => bag.has(g.good));
  });
  if (canSell) return null;
  const r = rngFor(state.seed, 'rescue', state.day);
  return state.inventory[r.int(0, state.inventory.length - 1)].good;
}

/** Commit to today's location. Its offers use up the tier deck cards they were dealt. */
export function visit(data: GameData, state: RunState, locationId: string): void {
  if (state.visited !== null) return;
  state.visited = locationId;
  const used = deckCards(data, state, locationId);
  state.deck.supplier += used.supplier;
  state.deck.buyer += used.buyer;
}

export function actorsAt(state: RunState, locationId: string): string[] {
  return state.locations.find((l) => l.id === locationId)?.actorIds ?? [];
}

export function offer(state: RunState, actorId: string, goodId: string): Offer {
  return state.market[offerKey(actorId, goodId)] ?? { tier: 'good', price: 0, left: 0 };
}

export function countOf(state: RunState, goodId: string): number {
  return state.inventory.filter((it) => it.good === goodId).length;
}

/** Average price paid for the units of a good in the bag, or null if none. */
export function avgPaid(state: RunState, goodId: string): number | null {
  const items = state.inventory.filter((it) => it.good === goodId);
  if (items.length === 0) return null;
  return items.reduce((sum, it) => sum + it.paid, 0) / items.length;
}

export function freeSlots(state: RunState): number {
  return state.capacity - state.inventory.length;
}

export type TradeBlock = 'soldOut' | 'noCash' | 'bagFull' | 'noneOwned' | 'noDemand' | null;

export function buyBlock(state: RunState, actorId: string, goodId: string): TradeBlock {
  const o = offer(state, actorId, goodId);
  if (CONFIG.limitStock && o.left <= 0) return 'soldOut';
  if (freeSlots(state) <= 0) return 'bagFull';
  if (state.cash < o.price) return 'noCash';
  return null;
}

export function sellBlock(state: RunState, actorId: string, goodId: string): TradeBlock {
  const o = offer(state, actorId, goodId);
  if (CONFIG.limitDemand && o.left <= 0) return 'noDemand';
  if (countOf(state, goodId) <= 0) return 'noneOwned';
  return null;
}

export function maxBuy(state: RunState, actorId: string, goodId: string): number {
  const o = offer(state, actorId, goodId);
  if (o.price <= 0) return 0;
  const n = Math.min(freeSlots(state), Math.floor(state.cash / o.price));
  return Math.max(0, CONFIG.limitStock ? Math.min(n, o.left) : n);
}

export function maxSell(state: RunState, actorId: string, goodId: string): number {
  const n = countOf(state, goodId);
  return Math.max(0, CONFIG.limitDemand ? Math.min(n, offer(state, actorId, goodId).left) : n);
}

/** Whether there's anything left to do at a location today: a good you can buy, a good you can
 *  sell, or (if the Dealer is here) a deal you can afford. */
export function canAct(data: GameData, state: RunState, locationId: string): boolean {
  const trade = actorsAt(state, locationId).some((id) => {
    const a = data.actors[id];
    const block = a.role === 'supplier' ? buyBlock : sellBlock;
    return a.goods.some((g) => block(state, id, g.good) === null);
  });
  const dealer = state.dealer?.locationId === locationId && state.dealer.offers.some((_, i) => dealerBlock(state, i) === null);
  return trade || dealer;
}

/** Buy up to `qty` units; returns how many were bought. */
export function buy(data: GameData, state: RunState, actorId: string, goodId: string, qty = 1): number {
  if (data.actors[actorId]?.role !== 'supplier') return 0;
  const n = Math.min(qty, maxBuy(state, actorId, goodId));
  if (n <= 0) return 0;
  const o = offer(state, actorId, goodId);
  for (let i = 0; i < n; i++) state.inventory.push({ good: goodId, paid: o.price, day: state.day });
  if (CONFIG.limitStock) o.left -= n;
  state.cash -= n * o.price;
  state.stats.bought += n;
  return n;
}

/** Sell up to `qty` units (oldest first); returns how many were sold. */
export function sell(data: GameData, state: RunState, actorId: string, goodId: string, qty = 1): number {
  if (data.actors[actorId]?.role !== 'buyer') return 0;
  const n = Math.min(qty, maxSell(state, actorId, goodId));
  const o = offer(state, actorId, goodId);
  for (let i = 0; i < n; i++) state.inventory.splice(state.inventory.findIndex((it) => it.good === goodId), 1);
  if (CONFIG.limitDemand) o.left -= n;
  state.cash += n * o.price;
  state.stats.sold += n;
  updateQuota(state);
  return n;
}

/** Latch the quota as met once cash reaches it, awarding its stars plus the early bonus.
 *  Returns true if it just became met. */
export function updateQuota(state: RunState): boolean {
  const q = state.quota;
  if (!q.met && state.cash >= q.amount) {
    q.met = true;
    // the early bonus counts from the day it's met, but the stars are paid when the quota ends
    q.earlyBonus = EARLY_STAR * Math.max(0, q.dueDay - state.day);
    q.starsAwarded = q.stars + q.earlyBonus;
    q.starsPending = true;
    return true;
  }
  return false;
}

/** Pay a met quota's stars (at the end of its due day). Saves from before stars were delayed
 *  have no `starsPending` and were already paid. */
function payStars(state: RunState, q: Quota): void {
  if (!q.starsPending) return;
  q.starsPending = false;
  state.stars += q.starsAwarded ?? 0;
  state.stats.starsEarned += q.starsAwarded ?? 0;
  state.dealerCheapOwed = true;
}

/** What the last-chance buyout pays for one unit of a good: its lowest Bad-tier buyer price. */
export function buyoutPrice(data: GameData, goodId: string): number {
  const prices = Object.values(data.actors).flatMap((a) =>
    a.role === 'buyer' ? a.goods.filter((g) => g.good === goodId).map((g) => g.prices.bad ?? g.prices.good) : [],
  );
  return prices.length ? Math.min(...prices) : 0;
}

/** On an unmet quota's due day, with cash short of it and goods in the bag, the whole bag can be
 *  sold off at Bad-deal prices before the day ends. Returns the total it would pay, or null. */
export function buyoutOffer(data: GameData, state: RunState): number | null {
  const q = state.quota;
  if (state.day < q.dueDay || q.met || state.cash >= q.amount || state.inventory.length === 0) return null;
  return state.inventory.reduce((sum, it) => sum + buyoutPrice(data, it.good), 0);
}

/** Sell the whole bag at the buyout price. Returns the cash received (0 if there's no offer). */
export function takeBuyout(data: GameData, state: RunState): number {
  const total = buyoutOffer(data, state);
  if (total === null) return 0;
  state.stats.sold += state.inventory.length;
  state.inventory = [];
  state.cash += total;
  updateQuota(state);
  return total;
}

export function daysLeft(state: RunState): number {
  return state.quota.dueDay - state.day;
}

export function endDay(data: GameData, state: RunState): EndDayResult {
  let result: EndDayResult = 'next';
  updateQuota(state);
  if (state.day >= state.quota.dueDay) {
    if (!state.quota.met) {
      state.status = 'failed';
      return 'failed';
    }
    state.stats.quotasMet++;
    payStars(state, state.quota);
    state.quota = quotaFor(state.quota.index + 1);
    state.deck = { supplier: 0, buyer: 0 }; // a fresh tier deck for each quota
    // p2: every 3rd quota (index % 3 === 2) will start a rule-changing event here.
    result = 'quotaPassed';
  }
  state.day++;
  state.visited = null;
  startDay(data, state);
  updateQuota(state);
  return result;
}
