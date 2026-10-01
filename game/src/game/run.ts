import { rngFor } from '../engine/rng';
import { areaFor, areasInOrder, areaView } from './area';
import { CONFIG } from './config';
import { dealActors } from './deal';
import { dealerBlock, owns, rollDealer } from './dealer';
import { dealPrice, deckCards, offerKey, offerPrice, rollMarket, sellerPrice } from './economy';
import { todayEvent } from './events';
import type { BagItem, EndDayResult, GameData, Offer, Quota, RunState, SingleKind } from './types';

export const CAPACITY = 4;
export const QUOTA_DAYS = 7;
export const RUN_LOCATIONS = 3;
/** The run's last day: meeting the quota due then wins the run. */
export const LAST_DAY = 63;
/** Base stars for meeting any quota. */
export const BASE_STARS = 5;

/** Quota `index` (0-based, one a week) from CONFIG.quotas (past its end, the last one's). */
export function quotaFor(index: number): Quota {
  const q = CONFIG.quotas;
  return {
    index,
    amount: q[Math.min(index, q.length - 1)],
    dueDay: QUOTA_DAYS * (index + 1),
    met: false,
    stars: BASE_STARS,
  };
}

/** The run's locations in an area: RUN_LOCATIONS of them, shuffled by the seed. The first area
 *  keeps the seed's original shuffle. */
function pickLocations(data: GameData, seed: number, area: string, first: boolean) {
  const r = first ? rngFor(seed, 'setup') : rngFor(seed, 'setup', area);
  return r
    .shuffle(Object.keys(areaView(data, area).locations))
    .slice(0, RUN_LOCATIONS)
    .map((id) => ({ id, actorIds: [] as string[] }));
}

/** The cash a week starts with in an area: its `startCash`, plus Nest Egg (Golden Goose's
 *  rollover is added on top at the weekly reset, in `endDay`). */
export function startingCash(data: GameData, state: RunState, area: string): number {
  return data.areas[area].startCash + (has(state, 'nestEgg') ? CONFIG.dealer.nestEgg : 0);
}

export function newRun(data: GameData, seed: number): RunState {
  const area = areaFor(data, 1);
  const locations = pickLocations(data, seed, area, true);
  const state: RunState = {
    version: 15,
    seed,
    area,
    moved: null,
    day: 1,
    cash: data.areas[area].startCash,
    capacity: CAPACITY,
    inventory: [],
    locations,
    quota: quotaFor(0),
    visited: null,
    market: {},
    deck: { supplier: 0, buyer: 0 },
    stats: { bought: 0, sold: 0, quotasMet: 0, starsEarned: 0, profit: 0, losses: 0, daySales: 0, bestDaySales: 0 },
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
  updateQuota(data, state);
  return state;
}

/** Does the run own this one-time stamp? */
function has(state: RunState, kind: SingleKind): boolean {
  return owns(state, { kind });
}

/** See whether the Dealer visits (he takes one actor's spot at his location), deal today's actors
 *  to locations, and roll their deals.
 *  On a quota's due day (and every day with the Dump Truck stamp), a buyer of the player's most
 *  common bag good is guaranteed to be present; with Perfect Planner, one of the priciest bag good.
 *  On other days, if the player can't buy anything, a buyer of something in the bag is (see rescueGood).
 *  With an empty bag, no location has only buyers. With Packed House, one location gets an extra actor.
 *  During Fireworks Night, one location is bustling (picked first): it gets the event's extra actors,
 *  and neither the Dealer nor Packed House's extra actor goes there. During the Blizzard, one
 *  location is snowed in (hidden on the map; it doesn't change the deal). */
function startDay(data: GameData, state: RunState): void {
  data = areaView(data, state.area);
  const ids = state.locations.map((l) => l.id);
  const bustling = todayEvent(data, state)?.bustling;
  state.bustlingAt = bustling ? ids[rngFor(state.seed, 'bustling', state.day).int(0, ids.length - 1)] : null;
  state.snowedAt = todayEvent(data, state)?.snowedIn
    ? ids[rngFor(state.seed, 'snowed', state.day).int(0, ids.length - 1)]
    : null;
  state.dealer = rollDealer(data, state);
  const dealerAt = state.dealer?.locationId;
  const packable = ids.filter((id) => id !== state.bustlingAt);
  state.packedAt =
    has(state, 'packedHouse') && packable.length > 0
      ? packable[rngFor(state.seed, 'packed', state.day).int(0, packable.length - 1)]
      : null;
  const extra: Record<string, number> = {};
  if (state.packedAt) extra[state.packedAt] = 1;
  if (state.bustlingAt && bustling) extra[state.bustlingAt] = bustling.extraActors;
  // with an empty bag, a buyers-only location has nothing for the player, so it's rerolled
  const needSeller = state.inventory.length === 0;
  const due = state.day === state.quota.dueDay;
  const needs: string[] = [];
  const common = guaranteedGood(data, state);
  if (common && (due || has(state, 'dumpTruck'))) needs.push(common);
  const priciest = plannerGood(data, state);
  if (priciest && has(state, 'perfectPlanner')) needs.push(priciest);
  const deal = (more: string[] = []) =>
    dealActors(data, state.seed, state.day, ids, [...needs, ...more], dealerAt, needSeller, extra);
  let dealt = deal();
  if (!due) {
    const rescue = rescueGood(data, state, Object.values(dealt).flat());
    if (rescue) dealt = deal([rescue]);
  }
  for (const loc of state.locations) loc.actorIds = dealt[loc.id];
  state.badGood = rollBadDay(data, state);
  if (state.badGood) state.badWeek = Math.floor((state.day - 1) / QUOTA_DAYS);
  state.market = rollMarket(data, state);
}

/** The weekly bad day: each week (days 7w+1 to 7w+7) has a day picked ahead of time from the
 *  seed, from its 2nd to its 6th (not the 1st, when the bag is usually empty and it would just
 *  move to the 2nd, nor the last). On it, every buyer of a random good from the bag is a bad deal. With an
 *  empty bag it moves to the next day, but never into the week's last day, and a week whose bag
 *  stays empty has none. No bad day while an area event is on (each area's last week).
 *  Returns today's bad good, or null. */
export function rollBadDay(data: GameData, state: RunState): string | null {
  const week = Math.floor((state.day - 1) / QUOTA_DAYS);
  const first = week * QUOTA_DAYS + 1;
  const last = first + QUOTA_DAYS - 2;
  const planned = rngFor(state.seed, 'badDay', week).int(first + 1, last);
  if (state.day < planned || state.day > last || state.badWeek === week) return null;
  if (todayEvent(data, state) || state.inventory.length === 0) return null;
  const goods = [...new Set(state.inventory.map((it) => it.good))].sort();
  return goods[rngFor(state.seed, 'badGood', state.day).int(0, goods.length - 1)];
}

/** The bag good that gets a guaranteed buyer on due day: the most common one; ties go to
 *  the good with the higher baseline sell price (best Good-tier buyer price), then by id.
 *  Null when the bag is empty. */
export function guaranteedGood(data: GameData, state: RunState): string | null {
  data = areaView(data, state.area);
  const counts = new Map<string, number>();
  for (const it of state.inventory) counts.set(it.good, (counts.get(it.good) ?? 0) + 1);
  const sellPrice = (good: string) => goodSellPrice(data, good);
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

/** The good a buyer normally pays most for (its best Good-tier buyer price). */
function goodSellPrice(data: GameData, good: string): number {
  return Math.max(
    0,
    ...Object.values(data.actors)
      .filter((a) => a.role === 'buyer')
      .flatMap((a) => a.goods.filter((g) => g.good === good).map((g) => g.prices.good)),
  );
}

/** Perfect Planner's good: the bag good with the highest Good-tier buyer price (ties by id).
 *  Null when the bag is empty. */
export function plannerGood(data: GameData, state: RunState): string | null {
  data = areaView(data, state.area);
  const goods = [...new Set(state.inventory.map((it) => it.good))].sort();
  let best: string | null = null;
  for (const g of goods) if (best === null || goodSellPrice(data, g) > goodSellPrice(data, best)) best = g;
  return best;
}

/** The lowest price any seller could charge today (its best tier, after the Dealer's discounts,
 *  and halved while the Daily Discount is unused). */
function cheapestSellerPrice(data: GameData, state: RunState): number {
  data = areaView(data, state.area);
  const price = Math.min(
    ...Object.values(data.actors)
      .filter((a) => a.role === 'supplier')
      .flatMap((a) => a.goods.map((g) => sellerPrice(data, state, g.good, Math.min(...Object.values(g.prices))))),
  );
  return buyPrice(state, { tier: 'good', price, left: 0 });
}

/** The non-due-day guarantee: if the player can't buy anything (bag full, or not enough cash for
 *  even the cheapest possible seller) and none of `dealtIds` buys anything in the bag, a random
 *  bag item's good gets a buyer dealt in. Null when there's nothing to rescue. Deterministic for
 *  (seed, day, bag). */
export function rescueGood(data: GameData, state: RunState, dealtIds: string[]): string | null {
  if (state.inventory.length === 0) return null;
  if (freeSlots(state) > 0 && state.cash >= cheapestSellerPrice(data, state)) return null;
  data = areaView(data, state.area);
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
  if (state.visited !== null || state.detoured === locationId) return;
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

/** What the Monocle stamp adds to every buy and sell price multiplier. */
function monocle(state: RunState): number {
  return has(state, 'monocle') ? CONFIG.dealer.monocle : 0;
}

/** What a unit from a seller's offer costs, before the Daily Discount: its price, raised by the
 *  Monocle (rounded, min $1). */
export function fullBuyPrice(state: RunState, o: Offer): number {
  return Math.max(1, Math.round(o.price * (1 + monocle(state))));
}

/** Units bought so far today (saves from before the count only know whether anything was). */
function unitsBoughtToday(state: RunState): number {
  return state.unitsBoughtToday ?? (state.boughtToday ? 1 : 0);
}

/** What a unit from a seller's offer costs when `before` units have already been bought today: with
 *  the Daily Discount stamp the day's first unit is half price, and with Camp Fire the second is
 *  (rounded up, min $1). */
function unitPrice(state: RunState, o: Offer, before: number): number {
  const p = fullBuyPrice(state, o);
  const half = (before === 0 && has(state, 'dailyDiscount')) || (before === 1 && has(state, 'campFire'));
  return half ? Math.max(1, Math.ceil(p / 2)) : p;
}

/** What the next unit bought from a seller's offer costs (see unitPrice). */
export function buyPrice(state: RunState, o: Offer): number {
  return unitPrice(state, o, unitsBoughtToday(state));
}

/** The stamp that makes the next unit bought cheaper today, if any. */
export function buyDiscountStamp(state: RunState): 'dailyDiscount' | 'campFire' | null {
  const before = unitsBoughtToday(state);
  if (before === 0 && has(state, 'dailyDiscount')) return 'dailyDiscount';
  if (before === 1 && has(state, 'campFire')) return 'campFire';
  return null;
}

/** The Haggler stamp's multiplier on the next sale today: 1 + hagglerStart, less hagglerStep per
 *  unit already sold today, never below 0. */
export function hagglerMultiplier(state: RunState): number {
  if (!has(state, 'haggler')) return 1;
  const { hagglerStart, hagglerStep } = CONFIG.dealer;
  return Math.max(0, 1 + hagglerStart - hagglerStep * (state.soldToday ?? 0));
}

/** The bonuses added to a bag unit's sell price multiplier: Monocle and Vintage (per day in the
 *  bag). */
export function sellBonus(state: RunState, item: BagItem): number {
  let bonus = monocle(state);
  if (has(state, 'vintage')) bonus += CONFIG.dealer.vintagePerDay * Math.max(0, state.day - item.day);
  return bonus;
}

/** The $ the Flipper stamp adds to a bag unit's sell price (for units bought yesterday). */
export function flipperBonus(state: RunState, item: BagItem): number {
  return has(state, 'flipper') && item.day === state.day - 1 ? CONFIG.dealer.flipper : 0;
}

/** What a buyer's offer pays for one bag unit: its price times 1 + `sellBonus` (rounded), plus
 *  Flipper's $, then times Haggler's multiplier (rounded). */
export function sellPrice(state: RunState, o: Offer, item: BagItem): number {
  const base = Math.round(o.price * (1 + sellBonus(state, item))) + flipperBonus(state, item);
  return Math.round(base * hagglerMultiplier(state));
}

/** What selling one unit of a good to a buyer's offer pays right now (the oldest unit in the bag
 *  goes first; with none, a unit bought today). */
export function nextSellPrice(state: RunState, o: Offer, goodId: string): number {
  const item = state.inventory.find((it) => it.good === goodId) ?? { good: goodId, paid: 0, day: state.day };
  return sellPrice(state, o, item);
}

export type TradeBlock = 'soldOut' | 'noCash' | 'bagFull' | 'noneOwned' | 'noDemand' | null;

export function buyBlock(state: RunState, actorId: string, goodId: string): TradeBlock {
  const o = offer(state, actorId, goodId);
  if (CONFIG.limitStock && o.left <= 0) return 'soldOut';
  if (freeSlots(state) <= 0) return 'bagFull';
  if (state.cash < buyPrice(state, o)) return 'noCash';
  return null;
}

/** Whether a buyer's demand limits sales today: always with CONFIG.limitDemand, otherwise only
 *  when today's event caps it. */
export function demandApplies(o: Offer): boolean {
  return CONFIG.limitDemand || !!o.capped;
}

export function sellBlock(state: RunState, actorId: string, goodId: string): TradeBlock {
  const o = offer(state, actorId, goodId);
  if (demandApplies(o) && o.left <= 0) return 'noDemand';
  if (countOf(state, goodId) <= 0) return 'noneOwned';
  return null;
}

export function maxBuy(state: RunState, actorId: string, goodId: string): number {
  const o = offer(state, actorId, goodId);
  if (o.price <= 0) return 0;
  const cap = Math.max(0, CONFIG.limitStock ? Math.min(freeSlots(state), o.left) : freeSlots(state));
  const before = unitsBoughtToday(state);
  let cash = state.cash;
  let n = 0;
  while (n < cap && cash >= unitPrice(state, o, before + n)) cash -= unitPrice(state, o, before + n++);
  return n;
}

export function maxSell(state: RunState, actorId: string, goodId: string): number {
  const n = countOf(state, goodId);
  const o = offer(state, actorId, goodId);
  return Math.max(0, demandApplies(o) ? Math.min(n, o.left) : n);
}

/** Whether there's anything left to do at a location today: a good you can buy, a good you can
 *  sell, or (if the Dealer is here) a deal you can afford. */
export function canAct(data: GameData, state: RunState, locationId: string): boolean {
  data = areaView(data, state.area);
  const trade = actorsAt(state, locationId).some((id) => {
    const a = data.actors[id];
    const block = a.role === 'supplier' ? buyBlock : sellBlock;
    return a.goods.some((g) => block(state, id, g.good) === null);
  });
  const dealer = state.dealer?.locationId === locationId && state.dealer.offers.some((_, i) => dealerBlock(state, i) === null);
  return trade || dealer;
}

/** Buy up to `qty` units, each at `buyPrice` (the Daily Discount and Camp Fire halve the day's
 *  first and second units); returns how many were bought. */
export function buy(data: GameData, state: RunState, actorId: string, goodId: string, qty = 1): number {
  if (data.actors[actorId]?.role !== 'supplier') return 0;
  const n = Math.min(qty, maxBuy(state, actorId, goodId));
  const o = offer(state, actorId, goodId);
  for (let i = 0; i < n; i++) {
    const paid = buyPrice(state, o);
    state.inventory.push({ good: goodId, paid, day: state.day });
    state.cash -= paid;
    state.unitsBoughtToday = unitsBoughtToday(state) + 1;
    state.boughtToday = true;
  }
  if (CONFIG.limitStock) o.left -= n;
  state.stats.bought += n;
  return n;
}

/** What a sale did: units sold, tips paid, and whether Fuzzy Dice turned the buyer Amazing. */
export interface Sale {
  n: number;
  tips: number;
  lucky: boolean;
}

/** Sell up to `qty` units (oldest first); returns how many were sold. */
export function sell(data: GameData, state: RunState, actorId: string, goodId: string, qty = 1): number {
  return sellUnits(data, state, actorId, goodId, qty).n;
}

/** Sell up to `qty` units (oldest first), each at `sellPrice`. Stamps:
 *  - Can't Get Enough: the buyer's price goes up CONFIG.dealer.cantGetEnoughStep after every unit
 *    (for the rest of the day).
 *  - Fuzzy Dice: after every unit, a CONFIG.dealer.fuzzyDiceChance roll turns the buyer Amazing
 *    for the rest of the day.
 *  - Tip Jar: the buyer tips CONFIG.dealer.tip once it has bought tipAfter units today.
 *  - Mixed Bag: the first sale of each good in a day tips CONFIG.dealer.mixedBagTip.
 *  - Big Tipper multiplies every tip. */
export function sellUnits(data: GameData, state: RunState, actorId: string, goodId: string, qty = 1): Sale {
  const sale: Sale = { n: 0, tips: 0, lucky: false };
  const actor = data.actors[actorId];
  if (actor?.role !== 'buyer') return sale;
  const n = Math.min(qty, maxSell(state, actorId, goodId));
  if (n <= 0) return sale;
  const o = offer(state, actorId, goodId);
  const d = CONFIG.dealer;
  const prices = actor.goods.find((g) => g.good === goodId)!.prices;
  for (let i = 0; i < n; i++) {
    const idx = state.inventory.findIndex((it) => it.good === goodId);
    const price = sellPrice(state, o, state.inventory[idx]);
    const [it] = state.inventory.splice(idx, 1);
    recordSale(state, it.paid, price);
    state.cash += price;
    state.soldToday = (state.soldToday ?? 0) + 1;
    o.sold = (o.sold ?? 0) + 1;
    if (has(state, 'cantGetEnough')) o.price += d.cantGetEnoughStep;
    if (has(state, 'fuzzyDice') && o.tier !== 'amazing' &&
        rngFor(state.seed, 'dice', state.day, actorId, goodId, o.sold).next() < d.fuzzyDiceChance) {
      // keeps any Can't Get Enough raises
      o.price += offerPrice(data, state, goodId, 'buyer', prices, 'amazing', o.bustling) -
        offerPrice(data, state, goodId, 'buyer', prices, o.tier, o.bustling);
      o.tier = 'amazing';
      sale.lucky = true;
    }
  }
  sale.n = n;
  if (demandApplies(o)) o.left -= n;
  if (!o.tipped && (o.sold ?? 0) >= d.tipAfter && has(state, 'tip')) {
    o.tipped = true;
    sale.tips += payTip(state, d.tip);
  }
  const soldGoods = (state.soldGoodsToday ??= []);
  if (!soldGoods.includes(goodId)) {
    soldGoods.push(goodId);
    if (has(state, 'mixedBag')) sale.tips += payTip(state, d.mixedBagTip);
  }
  updateQuota(data, state);
  return sale;
}

/** Pay a tip (times Big Tipper's multiplier, if owned); returns what was paid. */
function payTip(state: RunState, amount: number): number {
  const tip = amount * (has(state, 'bigTipper') ? CONFIG.dealer.bigTipper : 1);
  state.cash += tip;
  const st = state.stats;
  st.profit = (st.profit ?? 0) + tip;
  st.daySales = (st.daySales ?? 0) + tip;
  st.bestDaySales = Math.max(st.bestDaySales ?? 0, st.daySales);
  return tip;
}

/** Has anything been bought or sold today? */
export function tradedToday(state: RunState): boolean {
  return !!state.boughtToday || (state.soldToday ?? 0) > 0;
}

/** With the Detour stamp: nothing traded yet today at the first location, so the player can
 *  go to a second one instead of ending the day. */
export function canDetour(state: RunState): boolean {
  return has(state, 'detour') && state.visited !== null && !state.detoured && !tradedToday(state);
}

/** Leave today's location for another one (see canDetour). */
export function detour(state: RunState): void {
  if (!canDetour(state)) return;
  state.detoured = state.visited;
  state.visited = null;
}

/** The end-of-day payouts from stamps, if the day ended now. */
export interface Payouts {
  /** Fanny Pack: per different good in the bag. */
  fannyPack: number;
  /** Sleeping Bag: a share of what the bag cost, for a day without trading. */
  sleepingBag: number;
  /** Clean Sweep: per bag slot, for an empty bag. */
  cleanSweep: number;
}

export function endOfDayPayouts(state: RunState): Payouts {
  const d = CONFIG.dealer;
  const bag = state.inventory;
  return {
    fannyPack: has(state, 'fannyPack') ? d.fannyPack * new Set(bag.map((it) => it.good)).size : 0,
    sleepingBag:
      has(state, 'sleepingBag') && !tradedToday(state)
        ? Math.round(d.sleepingBag * bag.reduce((sum, it) => sum + it.paid, 0))
        : 0,
    cleanSweep: has(state, 'cleanSweep') && bag.length === 0 ? d.cleanSweep * state.capacity : 0,
  };
}

export function payoutTotal(p: Payouts): number {
  return p.fannyPack + p.sleepingBag + p.cleanSweep;
}

/** Count one unit sold at `price` (bought for `paid`) in the run stats. */
function recordSale(state: RunState, paid: number, price: number): void {
  const s = state.stats;
  s.sold++;
  s.profit = (s.profit ?? 0) + price - paid;
  s.losses = (s.losses ?? 0) + Math.max(0, paid - price);
  s.daySales = (s.daySales ?? 0) + price;
  s.bestDaySales = Math.max(s.bestDaySales ?? 0, s.daySales);
}

/** What the quota counts right now: cash, plus the bag cashed out at the end of the week, plus
 *  tonight's stamp payouts. */
export function quotaTotal(data: GameData, state: RunState): number {
  return state.cash + cashOutValue(data, state) + payoutTotal(endOfDayPayouts(state));
}

/** Update whether the quota is reached right now (`quotaTotal`; it's judged for good at the end
 *  of the due day). Returns true if it just became reached. */
export function updateQuota(data: GameData, state: RunState): boolean {
  const q = state.quota;
  const was = q.met;
  q.met = quotaTotal(data, state) >= q.amount;
  return q.met && !was;
}

/** The cash needed for each bonus star: CONFIG.bonusSteps above `amount`, rounded up. */
export function bonusTargets(amount: number): number[] {
  return CONFIG.bonusSteps.map((step) => Math.ceil(amount * (1 + step)));
}

/** Bonus stars for ending a quota with `cash`: one per bonus target reached. */
export function bonusStars(amount: number, cash: number): number {
  return bonusTargets(amount).filter((t) => cash >= t).length;
}

/** What the end-of-week cash-out pays for one bag unit: what was paid for it, or with the Last
 *  Call stamp the good's lowest Amazing buyer price (from any area's buyers of it, with
 *  Cramazing) when that's more. */
export function cashOutPrice(data: GameData, item: BagItem, state: RunState): number {
  if (!has(state, 'lastCall')) return item.paid;
  const prices = Object.values(data.actors).flatMap((a) =>
    a.role === 'buyer'
      ? a.goods.filter((g) => g.good === item.good).map((g) => dealPrice(state, g.prices, 'amazing'))
      : [],
  );
  return Math.max(item.paid, prices.length ? Math.min(...prices) : 0);
}

/** Pay a met quota's stars (at the end of its due day). */
function payStars(state: RunState, q: Quota): void {
  state.stars += q.starsAwarded ?? 0;
  state.stats.starsEarned += q.starsAwarded ?? 0;
  state.dealerCheapOwed = true;
}

/** What the whole bag would be cashed out for. */
export function cashOutValue(data: GameData, state: RunState): number {
  return state.inventory.reduce((sum, it) => sum + cashOutPrice(data, it, state), 0);
}

/** A sale worth making before the week ends: a buyer at the location pays more for a bag good
 *  than its oldest unit would cash out for. */
export interface BetterSale {
  good: string;
  actorId: string;
  price: number;
  cashOut: number;
}

/** Per bag good, the best sale at a location that beats the end-of-week cash-out (none when every
 *  buyer there pays no more than the cash-out). */
export function betterSales(data: GameData, state: RunState, locationId: string): BetterSale[] {
  const view = areaView(data, state.area);
  const best = new Map<string, BetterSale>();
  for (const actorId of actorsAt(state, locationId)) {
    const a = view.actors[actorId];
    if (a?.role !== 'buyer') continue;
    for (const { good } of a.goods) {
      if (sellBlock(state, actorId, good) !== null) continue;
      const item = state.inventory.find((it) => it.good === good)!;
      const price = sellPrice(state, offer(state, actorId, good), item);
      const cashOut = cashOutPrice(data, item, state);
      if (price > cashOut && price > (best.get(good)?.price ?? -1)) best.set(good, { good, actorId, price, cashOut });
    }
  }
  return [...best.values()];
}

/** End of the week: the whole bag is sold at `cashOutPrice`. Returns the cash received. */
function cashOut(data: GameData, state: RunState): number {
  let total = 0;
  for (const it of state.inventory) {
    const price = cashOutPrice(data, it, state);
    recordSale(state, it.paid, price);
    total += price;
  }
  state.inventory = [];
  state.cash += total;
  return total;
}

export function daysLeft(state: RunState): number {
  return state.quota.dueDay - state.day;
}

export function endDay(data: GameData, state: RunState): EndDayResult {
  let result: EndDayResult = 'next';
  const q = state.quota;
  const due = state.day >= q.dueDay;
  if (due) q.cashBefore = state.cash;
  // stamp payouts land before the quota is judged (and work on the bag before it's cashed out)
  const payout = payoutTotal(endOfDayPayouts(state));
  state.cash += payout;
  state.stats.profit = (state.stats.profit ?? 0) + payout;
  if (due) {
    // the end of the week: the bag is cashed out, and the quota is judged on what that leaves
    q.payouts = payout;
    q.cashOut = cashOut(data, state);
    q.finalCash = state.cash;
    q.met = state.cash >= q.amount;
    if (!q.met) {
      state.status = 'failed';
      return 'failed';
    }
    state.stats.quotasMet++;
    q.bonusStars = bonusStars(q.amount, state.cash);
    q.starsAwarded = q.stars + q.bonusStars;
    payStars(state, q);
    if (state.day >= LAST_DAY) {
      // the last quota: the run is won, and ends here (the score is the final cash)
      state.status = 'won';
      return 'won';
    }
    state.quota = quotaFor(q.index + 1);
    state.deck = { supplier: 0, buyer: 0 }; // a fresh tier deck for each quota
    // a new week starts from the starting cash of wherever it's spent, plus (with Golden Goose)
    // whatever the week ended with above its quota
    const rollover = has(state, 'goldenGoose') ? state.cash - q.amount : 0;
    if (rollover > 0) q.rollover = rollover;
    state.cash = startingCash(data, state, areaFor(data, state.day + 1)) + rollover;
    result = 'quotaPassed';
  }
  // only ever forward (a debug jump can put the run ahead of its day's area)
  const next = areaFor(data, state.day + 1);
  const order = areasInOrder(data).map((a) => a.id);
  if (order.indexOf(next) > order.indexOf(state.area)) moveArea(data, state, next);
  state.day++;
  state.visited = null;
  state.boughtToday = false;
  state.unitsBoughtToday = 0;
  state.soldToday = 0;
  state.soldGoodsToday = [];
  state.detoured = null;
  state.stats.daySales = 0;
  startDay(data, state);
  updateQuota(data, state);
  return result;
}

/** Move the run to a new area (between days): the bag is bought back at what was paid for it,
 *  and the run gets that area's locations and a fresh tier deck. `moved` is kept for the arrival
 *  screen. */
export function moveArea(data: GameData, state: RunState, area: string): void {
  const units = state.inventory.length;
  const refund = state.inventory.reduce((sum, it) => sum + it.paid, 0);
  state.cash += refund;
  state.stats.sold += units;
  state.inventory = [];
  state.area = area;
  state.locations = pickLocations(data, state.seed, area, false);
  state.deck = { supplier: 0, buyer: 0 };
  state.dealer = null;
  state.moved = { area, units, refund };
}

/** Debug: top cash up so the quota is reached, or lower it to $1 short (not below $0). */
export function debugSetQuotaMet(data: GameData, state: RunState, met: boolean): void {
  const gap = state.quota.amount - quotaTotal(data, state);
  if (met) state.cash += Math.max(0, gap);
  else if (gap <= 0) state.cash = Math.max(0, state.cash + gap - 1);
  updateQuota(data, state);
}

/** Debug: the area after the current one, or null in the last area. */
export function debugNextArea(data: GameData, state: RunState): string | null {
  const areas = areasInOrder(data);
  const i = areas.findIndex((a) => a.id === state.area);
  return areas[i + 1]?.id ?? null;
}

/** Debug: move to the next area today, without touching the day or quota. The bag is bought
 *  back at what was paid, with no arrival screen, and today is re-dealt there. */
export function debugGotoNextArea(data: GameData, state: RunState): void {
  const next = debugNextArea(data, state);
  if (!next) return;
  moveArea(data, state, next);
  state.moved = null;
  state.visited = null;
  startDay(data, state);
  updateQuota(data, state);
}

/** Debug: the day "advance" goes to: the current quota's due day, or the next one's when it's
 *  already due. Null when that would mean ending an unmet quota's due day. */
export function debugAdvanceDay(state: RunState): number | null {
  const q = state.quota;
  if (state.day < q.dueDay) return q.dueDay;
  return q.met ? quotaFor(q.index + 1).dueDay : null;
}

/** Debug: end days without trading until `debugAdvanceDay` (or the run is won). Returns the
 *  quota passed on the way, if any. */
export function debugAdvance(data: GameData, state: RunState): Quota | null {
  const day = debugAdvanceDay(state);
  let passed: Quota | null = null;
  while (day !== null && state.day < day) {
    const q = state.quota;
    const res = endDay(data, state);
    if (res === 'quotaPassed') passed = q;
    if (res === 'won') break;
  }
  return passed;
}
