import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { rngFor } from '../src/engine/rng';
import { CONFIG } from '../src/game/config';
import { buildData } from '../src/game/data';
import { dealActors } from '../src/game/deal';
import {
  allDeals, BAG_TIERS, buyDealerDeal, dealCost, dealEnabled, dealerBlock, dealFromKey, dealKey, eligibleDeals, isRanked, isUniversal, rollDealer,
} from '../src/game/dealer';
import { deckCard, deckCards, extraDemand, rollMarket, rollStock, rollTier, tierAt, tierPrice, tierWeights } from '../src/game/economy';
import {
  avgPaid, BASE_STARS, buy, buyBlock, buyoutOffer, buyoutPrice, canAct, CAPACITY, endDay, FIRST_QUOTA, guaranteedGood, newRun, offer, quotaFor, rescueGood, sell, sellBlock, takeBuyout,
  START_CASH, updateQuota, visit,
} from '../src/game/run';
import { type DealerDeal, type RunState, TIERS } from '../src/game/types';
import { loadTestData } from './helpers';

const data = loadTestData();
const DEFAULT_CONFIG = { ...CONFIG, dealWeights: { ...CONFIG.dealWeights }, buyerDealWeights: { ...CONFIG.buyerDealWeights } };
afterEach(() => {
  Object.assign(CONFIG, DEFAULT_CONFIG, {
    dealWeights: { ...DEFAULT_CONFIG.dealWeights },
    buyerDealWeights: { ...DEFAULT_CONFIG.buyerDealWeights },
  });
});

/** Make sure an actor of `role` trading `good` is present today
 *  (sellers are swapped into the first location, buyers into the second). */
function withActor(s: RunState, role: 'supplier' | 'buyer', good: string): string {
  for (const l of s.locations)
    for (const id of l.actorIds)
      if (data.actors[id].role === role && data.actors[id].goods.some((g) => g.good === good)) return id;
  const id = Object.keys(data.actors).find(
    (a) => data.actors[a].role === role && data.actors[a].goods.some((g) => g.good === good),
  )!;
  s.locations[role === 'supplier' ? 0 : 1].actorIds[0] = id;
  s.market = rollMarket(data, s);
  return id;
}

describe('data', () => {
  it('has 4 goods with 2 sellers and 2 buyers each, and 3 locations of 3 slots', () => {
    expect(Object.keys(data.goods)).toHaveLength(4);
    expect(Object.keys(data.actors)).toHaveLength(16);
    for (const good of Object.keys(data.goods)) {
      const count = (role: string) =>
        Object.values(data.actors).filter((a) => a.role === role && a.goods.some((g) => g.good === good)).length;
      expect(count('supplier')).toBe(2);
      expect(count('buyer')).toBe(2);
    }
    expect(Object.keys(data.locations)).toHaveLength(3);
    for (const l of Object.values(data.locations)) expect(l.actorSlots).toBe(3);
  });

  it('rejects bad dealer discounts and missing dealer slots', () => {
    const goods = Object.values(data.goods);
    const actors = Object.values(data.actors);
    const locations = Object.values(data.locations);
    const badGoods = goods.map((g, i) => (i === 0 ? { ...g, dealerDiscount: -1 } : g));
    expect(() => buildData(badGoods, actors, locations, data.dealer)).toThrow(/dealerDiscount/);
    const noSlot = locations.map((l, i) => (i === 0 ? { ...l, dealerSlot: undefined as never } : l));
    expect(() => buildData(goods, actors, noSlot, data.dealer)).toThrow(/dealerSlot/);
  });

  it('rejects price lists whose tiers are not ordered in the player\'s favour', () => {
    const goods = Object.values(data.goods);
    const actors = Object.values(data.actors);
    const locations = Object.values(data.locations);
    expect(() => buildData(goods, actors, locations, data.dealer)).not.toThrow();
    const flip = (role: string) =>
      actors.map((a) =>
        a.role === role
          ? { ...a, goods: a.goods.map((g) => ({ ...g, prices: { ...g.prices, good: g.prices.amazing, amazing: g.prices.good } })) }
          : a,
      );
    expect(() => buildData(goods, flip('supplier'), locations, data.dealer)).toThrow(/good -> great -> amazing \(no bad\)/);
    expect(() => buildData(goods, flip('buyer'), locations, data.dealer)).toThrow(/bad -> good -> great -> amazing/);
  });
});

describe('daily deal', () => {
  const locIds = Object.keys(data.locations);

  it('fills every location, never repeats an actor, and has each good on at most one actor per place', () => {
    for (let seed = 1; seed <= 60; seed++) {
      for (let day = 1; day <= 30; day++) {
        const dealt = dealActors(data, seed, day, locIds);
        const all = Object.values(dealt).flat();
        expect(new Set(all).size).toBe(all.length);
        for (const locId of locIds) {
          const here = dealt[locId];
          expect(here).toHaveLength(3);
          // covers buy+sell of a good, two buyers of a good, and two sellers of a good
          const goods = here.flatMap((id) => data.actors[id].goods.map((g) => g.good));
          expect(new Set(goods).size).toBe(goods.length);
        }
      }
    }
  });

  it('guarantees a buyer of the required good while keeping all other rules', () => {
    for (const good of Object.keys(data.goods)) {
      for (let seed = 1; seed <= 30; seed++) {
        for (let day = 1; day <= 10; day++) {
          const dealt = dealActors(data, seed, day, locIds, good);
          const all = Object.values(dealt).flat();
          expect(new Set(all).size).toBe(all.length);
          expect(all.some((id) => data.actors[id].role === 'buyer' && data.actors[id].goods.some((g) => g.good === good))).toBe(true);
          for (const locId of locIds) {
            expect(dealt[locId]).toHaveLength(3);
            const goods = dealt[locId].flatMap((id) => data.actors[id].goods.map((g) => g.good));
            expect(new Set(goods).size).toBe(goods.length);
          }
        }
      }
    }
  });

  it('never gives two locations the same goods to buy and sell', () => {
    const sig = (ids: string[]) =>
      ['buyer', 'supplier']
        .map((r) => ids.filter((id) => data.actors[id].role === r).flatMap((id) => data.actors[id].goods.map((g) => g.good)).sort().join(','))
        .join('|');
    for (let seed = 0; seed < 300; seed++)
      for (let day = 1; day <= 20; day++)
        for (const good of [undefined, 'tools']) {
          const dealt = dealActors(data, seed, day, locIds, good);
          const sigs = locIds.map((l) => sig(dealt[l]));
          expect(new Set(sigs).size).toBe(sigs.length);
        }
  });

  it('with needSeller, gives every location a seller (even the Dealer location)', () => {
    for (let seed = 0; seed < 200; seed++)
      for (let day = 1; day <= 20; day++)
        for (const dealerAt of [undefined, locIds[seed % locIds.length]]) {
          const dealt = dealActors(data, seed, day, locIds, undefined, dealerAt, true);
          for (const locId of locIds) expect(dealt[locId].some((id) => data.actors[id].role === 'supplier')).toBe(true);
        }
  });

  it('is deterministic per (seed, day) and changes between days', () => {
    expect(dealActors(data, 5, 3, locIds)).toEqual(dealActors(data, 5, 3, locIds));
    const days = new Set(Array.from({ length: 10 }, (_, d) => JSON.stringify(dealActors(data, 5, d + 1, locIds))));
    expect(days.size).toBeGreaterThan(1);
  });

  it('re-deals actors at the start of each day', () => {
    const s = newRun(data, 77);
    const seen = new Set<string>();
    for (let d = 0; d < 10; d++) {
      seen.add(JSON.stringify(s.locations.map((l) => l.actorIds)));
      for (const l of s.locations) for (const id of l.actorIds) expect(s.market[`${id}:${data.actors[id].goods[0].good}`]).toBeDefined();
      endDay(data, s);
      if (s.status === 'failed') break;
    }
    expect(seen.size).toBeGreaterThan(1);
  });
});

describe('due-day buyer guarantee', () => {
  const item = (good: string) => ({ good, paid: 1, day: 1 });
  const hasBuyer = (s: RunState, good: string) =>
    s.locations.some((l) =>
      l.actorIds.some((id) => data.actors[id].role === 'buyer' && data.actors[id].goods.some((g) => g.good === good)),
    );

  it('picks the most common bag good', () => {
    const s = newRun(data, 1);
    s.inventory = [item('seashell'), item('old_record'), item('seashell')];
    expect(guaranteedGood(data, s)).toBe('seashell');
  });

  it('breaks ties by the higher sell price', () => {
    const s = newRun(data, 1);
    s.inventory = [item('strawberry'), item('tools'), item('strawberry'), item('tools')];
    expect(guaranteedGood(data, s)).toBe('tools');
  });

  it('guarantees nothing for an empty bag', () => {
    expect(guaranteedGood(data, newRun(data, 1))).toBeNull();
  });

  it('places a buyer of that good on the due day', () => {
    for (let seed = 1; seed <= 40; seed++) {
      const s = newRun(data, seed);
      s.cash = FIRST_QUOTA; // survive to day 7
      for (let d = 1; d < 6; d++) endDay(data, s);
      s.inventory = [item('old_record'), item('old_record'), item('strawberry')];
      endDay(data, s);
      expect(s.day).toBe(s.quota.dueDay);
      expect(hasBuyer(s, 'old_record')).toBe(true);
    }
  });
});

describe('stuck-day sell guarantee', () => {
  const item = (good: string) => ({ good, paid: 1, day: 1 });
  const buyersOf = (s: RunState, goods: string[]) =>
    s.locations.flatMap((l) => l.actorIds).filter(
      (id) => data.actors[id].role === 'buyer' && data.actors[id].goods.some((g) => goods.includes(g.good)),
    );
  /** A run on a non-due day, ending the day with `bag` and `cash`. */
  function nextDay(seed: number, bag: string[], cash: number): RunState {
    const s = newRun(data, seed);
    s.inventory = bag.map(item);
    s.cash = cash;
    endDay(data, s);
    expect(s.day).toBeLessThan(s.quota.dueDay);
    return s;
  }

  it('deals in a buyer for something in a full bag', () => {
    const bag = ['tools', 'tools', 'seashell', 'strawberry'];
    for (let seed = 1; seed <= 200; seed++) expect(buyersOf(nextDay(seed, bag, 100), bag).length).toBeGreaterThan(0);
  });

  it('deals in a buyer when there is no money left to buy with', () => {
    for (let seed = 1; seed <= 200; seed++) expect(buyersOf(nextDay(seed, ['old_record'], 0), ['old_record'])).not.toEqual([]);
  });

  it("leaves the deal alone when you can still buy, or already can sell, or have nothing", () => {
    const s = newRun(data, 3);
    s.inventory = [item('tools')];
    s.cash = 100;
    expect(rescueGood(data, s, [])).toBeNull(); // room and cash to buy
    s.cash = 0;
    const toolsBuyer = Object.keys(data.actors).find(
      (id) => data.actors[id].role === 'buyer' && data.actors[id].goods.some((g) => g.good === 'tools'),
    )!;
    expect(rescueGood(data, s, [toolsBuyer])).toBeNull(); // a buyer is already here
    expect(rescueGood(data, s, [])).toBe('tools');
    s.inventory = [];
    expect(rescueGood(data, s, [])).toBeNull(); // nothing to sell
  });

  it('picks a random item from the bag, not always the most common', () => {
    const picked = new Set<string>();
    for (let seed = 1; seed <= 60; seed++) {
      const s = newRun(data, seed);
      s.day = 2;
      s.cash = 0;
      s.inventory = [item('tools'), item('tools'), item('tools'), item('seashell')];
      picked.add(rescueGood(data, s, [])!);
    }
    expect(picked).toEqual(new Set(['tools', 'seashell']));
  });
});

describe('deal tiers', () => {
  it('roll seller stock roughly in proportion to CONFIG.stockWeights', () => {
    const counts: Record<number, number> = { 1: 0, 2: 0, 3: 0 };
    const n = 20000;
    for (let i = 0; i < n; i++) counts[rollStock(rngFor(i, 'stock'))]++;
    for (const q of [1, 2, 3]) expect(counts[q] / n).toBeCloseTo(CONFIG.stockWeights[q], 1);
  });

  it('roll roughly in proportion to CONFIG.dealWeights', () => {
    const r = rngFor(1, 'tier-test');
    const counts = { bad: 0, good: 0, great: 0, amazing: 0 };
    const n = 20000;
    for (let i = 0; i < n; i++) counts[rollTier(r)]++;
    for (const t of TIERS) expect(counts[t] / n).toBeCloseTo(CONFIG.dealWeights[t] ?? 0, 1);
  });

  it('roll buyers roughly in proportion to CONFIG.buyerDealWeights', () => {
    const r = rngFor(3, 'tier-test');
    const counts = { bad: 0, good: 0, great: 0, amazing: 0 };
    const n = 20000;
    for (let i = 0; i < n; i++) counts[rollTier(r, CONFIG.buyerDealWeights)]++;
    for (const t of TIERS) expect(counts[t] / n).toBeCloseTo(CONFIG.buyerDealWeights[t], 1);
  });

  it('never roll a bad deal for a seller, and price a bad buyer at or below the great seller price', () => {
    expect(CONFIG.dealWeights.bad ?? 0).toBe(0);
    for (const good of Object.keys(data.goods)) {
      const of = (role: string) => Object.values(data.actors).filter((a) => a.role === role).flatMap((a) => a.goods.filter((g) => g.good === good));
      for (const s of of('supplier')) expect(s.prices.bad).toBeUndefined();
      for (const b of of('buyer')) for (const s of of('supplier')) expect(b.prices.bad).toBeLessThanOrEqual(s.prices.great);
    }
  });

  it('respect a changed weighting', () => {
    CONFIG.dealWeights = { bad: 0, good: 0, great: 0, amazing: 1 };
    CONFIG.buyerDealWeights = { bad: 0, good: 0, great: 0, amazing: 1 };
    const r = rngFor(2, 'tier-test');
    for (let i = 0; i < 100; i++) expect(rollTier(r)).toBe('amazing');
  });

  it('set the offer price from the rolled tier', () => {
    for (let seed = 0; seed < 40; seed++) {
      const s = newRun(data, seed);
      for (const l of s.locations)
        for (const id of l.actorIds)
          for (const ag of data.actors[id].goods) {
            const o = offer(s, id, ag.good);
            expect(o.price).toBe(tierPrice(ag.prices, o.tier));
            const seller = data.actors[id].role === 'supplier';
            expect(o.left).toBeGreaterThanOrEqual(seller ? 1 : ag.qtyMin);
            expect(o.left).toBeLessThanOrEqual(seller ? 3 : ag.qtyMax);
          }
    }
  });

  it('market is deterministic for a seed and day', () => {
    expect(rollMarket(data, newRun(data, 1234))).toEqual(rollMarket(data, newRun(data, 1234)));
  });
});

describe('trading', () => {
  it('starts with the configured cash, capacity and quota', () => {
    const s = newRun(data, 7);
    expect(s.cash).toBe(START_CASH);
    expect(s.capacity).toBe(CAPACITY);
    expect(s.quota).toEqual({ index: 0, amount: FIRST_QUOTA, dueDay: 7, met: false, stars: BASE_STARS });
  });

  it('buy/sell move cash and inventory, recording what was paid', () => {
    const s = newRun(data, 99);
    const sup = withActor(s, 'supplier', 'strawberry');
    const buyer = withActor(s, 'buyer', 'strawberry');
    const o = offer(s, sup, 'strawberry');
    expect(buy(data, s, sup, 'strawberry', 1)).toBe(1);
    expect(s.cash).toBe(START_CASH - o.price);
    expect(s.inventory).toEqual([{ good: 'strawberry', paid: o.price, day: 1 }]);

    const sp = offer(s, buyer, 'strawberry').price;
    expect(sell(data, s, buyer, 'strawberry', 5)).toBe(1);
    expect(s.cash).toBe(START_CASH - o.price + sp);
    expect(s.inventory).toEqual([]);
    expect(sellBlock(s, buyer, 'strawberry')).toBe('noneOwned');
  });

  it('suppliers cannot buy and buyers cannot sell', () => {
    const s = newRun(data, 5);
    const sup = withActor(s, 'supplier', 'seashell');
    const buyer = withActor(s, 'buyer', 'seashell');
    expect(sell(data, s, sup, 'seashell')).toBe(0);
    expect(buy(data, s, buyer, 'seashell')).toBe(0);
  });

  it('sells the oldest unit first', () => {
    const s = newRun(data, 21);
    const buyer = withActor(s, 'buyer', 'seashell');
    s.inventory = [
      { good: 'seashell', paid: 1, day: 1 },
      { good: 'strawberry', paid: 2, day: 1 },
      { good: 'seashell', paid: 3, day: 2 },
    ];
    sell(data, s, buyer, 'seashell');
    expect(s.inventory).toEqual([
      { good: 'strawberry', paid: 2, day: 1 },
      { good: 'seashell', paid: 3, day: 2 },
    ]);
  });

  it('with stock limits off, buying ignores stock (still bounded by cash and bag)', () => {
    CONFIG.limitStock = false;
    const s = newRun(data, 3);
    s.cash = 1000;
    const sup = withActor(s, 'supplier', 'strawberry');
    s.market[`${sup}:strawberry`].left = 0;
    expect(buyBlock(s, sup, 'strawberry')).toBeNull();
    expect(buy(data, s, sup, 'strawberry', 50)).toBe(CAPACITY);
  });

  it('averages the price paid for bag units of a good', () => {
    const s = newRun(data, 41);
    expect(avgPaid(s, 'seashell')).toBeNull();
    s.inventory = [
      { good: 'seashell', paid: 2, day: 1 },
      { good: 'strawberry', paid: 9, day: 1 },
      { good: 'seashell', paid: 3, day: 2 },
    ];
    expect(avgPaid(s, 'seashell')).toBe(2.5);
  });

  it('respects bag capacity (one slot per unit)', () => {
    const s = newRun(data, 3);
    s.cash = 1000;
    const sup = withActor(s, 'supplier', 'strawberry');
    s.market[`${sup}:strawberry`].left = 99;
    expect(buy(data, s, sup, 'strawberry', 50)).toBe(CAPACITY);
    expect(s.inventory).toHaveLength(CAPACITY);
    expect(buyBlock(s, sup, 'strawberry')).toBe('bagFull');
  });

  it('respects cash', () => {
    const s = newRun(data, 3);
    s.cash = 0;
    const sup = withActor(s, 'supplier', 'old_record');
    expect(buyBlock(s, sup, 'old_record')).toBe('noCash');
    expect(buy(data, s, sup, 'old_record')).toBe(0);
  });
});

describe('stock and demand limits (when enabled)', () => {
  beforeEach(() => {
    CONFIG.limitStock = true;
    CONFIG.limitDemand = true;
  });

  it('buying depletes stock and blocks when sold out', () => {
    const s = newRun(data, 99);
    s.cash = 1000;
    const sup = withActor(s, 'supplier', 'strawberry');
    const left = offer(s, sup, 'strawberry').left;
    expect(buy(data, s, sup, 'strawberry', 99)).toBe(Math.min(left, CAPACITY));
    if (left <= CAPACITY) expect(buyBlock(s, sup, 'strawberry')).toBe('soldOut');
  });

  it('selling depletes demand', () => {
    const s = newRun(data, 99);
    const buyer = withActor(s, 'buyer', 'strawberry');
    s.market[`${buyer}:strawberry`].left = 1;
    s.inventory = [
      { good: 'strawberry', paid: 1, day: 1 },
      { good: 'strawberry', paid: 1, day: 1 },
    ];
    expect(sell(data, s, buyer, 'strawberry', 5)).toBe(1);
    expect(sellBlock(s, buyer, 'strawberry')).toBe('noDemand');
  });
});

describe('unlimited demand (the default)', () => {
  it('buyers take every unit you have, however many they rolled', () => {
    expect(CONFIG.limitDemand).toBe(false);
    const s = newRun(data, 99);
    const buyer = withActor(s, 'buyer', 'strawberry');
    s.market[`${buyer}:strawberry`].left = 0;
    s.inventory = Array.from({ length: 4 }, () => ({ good: 'strawberry', paid: 1, day: 1 }));
    expect(sellBlock(s, buyer, 'strawberry')).toBeNull();
    expect(sell(data, s, buyer, 'strawberry', 99)).toBe(4);
    expect(s.inventory).toEqual([]);
  });
});

describe('quota', () => {
  it('latches when reached even if cash drops afterwards', () => {
    const s = newRun(data, 11);
    const buyer = withActor(s, 'buyer', 'old_record');
    s.inventory = [{ good: 'old_record', paid: 4, day: 1 }];
    s.cash = FIRST_QUOTA;
    s.market[`${buyer}:old_record`].left = 1;
    sell(data, s, buyer, 'old_record');
    expect(s.quota.met).toBe(true);
    s.cash = 0;
    for (let d = 1; d < 7; d++) expect(endDay(data, s)).toBe('next');
    expect(s.day).toBe(7);
    expect(endDay(data, s)).toBe('quotaPassed');
    expect(s.day).toBe(8);
    expect(s.quota).toEqual({ ...quotaFor(1), met: false });
    expect(s.quota.amount).toBe(Math.round((FIRST_QUOTA * CONFIG.quotaGrowth) / 5) * 5);
    expect(s.quota.dueDay).toBe(14);
  });

  it('fails the run when the due day ends unmet', () => {
    const s = newRun(data, 12);
    for (let d = 1; d < 7; d++) endDay(data, s);
    expect(endDay(data, s)).toBe('failed');
    expect(s.status).toBe('failed');
  });

  it('offers to buy the bag at Bad-deal prices only on an unmet due day', () => {
    const s = newRun(data, 12);
    s.inventory = [{ good: 'tools', paid: 10, day: 1 }, { good: 'strawberry', paid: 3, day: 1 }];
    s.cash = 0;
    expect(buyoutOffer(data, s)).toBeNull(); // not the due day yet
    for (let d = 1; d < 7; d++) endDay(data, s);
    s.inventory = [{ good: 'tools', paid: 10, day: 1 }, { good: 'strawberry', paid: 3, day: 1 }];
    s.cash = FIRST_QUOTA - buyoutPrice(data, 'tools') - buyoutPrice(data, 'strawberry');
    expect(buyoutPrice(data, 'tools')).toBe(8);
    expect(buyoutOffer(data, s)).toBe(10);
    expect(takeBuyout(data, s)).toBe(10);
    expect(s.inventory).toEqual([]);
    expect(s.cash).toBe(FIRST_QUOTA);
    expect(s.quota.met).toBe(true);
    expect(buyoutOffer(data, s)).toBeNull();
    expect(endDay(data, s)).toBe('quotaPassed');
  });

  it('makes no buyout offer with an empty bag or a met quota', () => {
    const s = newRun(data, 12);
    for (let d = 1; d < 7; d++) endDay(data, s);
    s.inventory = [];
    s.cash = 0;
    expect(buyoutOffer(data, s)).toBeNull();
    expect(takeBuyout(data, s)).toBe(0);
    s.inventory = [{ good: 'seashell', paid: 4, day: 1 }];
    s.cash = FIRST_QUOTA;
    expect(buyoutOffer(data, s)).toBeNull();
  });

  it('new day resets the visit and rerolls the market', () => {
    const s = newRun(data, 13);
    s.visited = s.locations[0].id;
    const before = JSON.stringify(s.market);
    endDay(data, s);
    expect(s.visited).toBeNull();
    expect(JSON.stringify(s.market)).not.toBe(before);
  });
});

/** Meet the current quota right now by handing over the cash. */
function meetQuota(s: RunState): void {
  s.cash = s.quota.amount;
  updateQuota(s);
}

/** Meet the current quota and play out the days until it ends: the next morning, with its stars paid. */
function passQuota(s: RunState): void {
  meetQuota(s);
  while (endDay(data, s) !== 'quotaPassed');
}

describe('stars', () => {
  it('every quota has the same base stars', () => {
    expect([0, 1, 2, 3, 6].map((i) => quotaFor(i).stars)).toEqual(Array(5).fill(BASE_STARS));
  });

  it('are paid once, when the quota ends, plus 1 per day it was met early', () => {
    const s = newRun(data, 21);
    endDay(data, s); // day 2, 5 days early
    meetQuota(s);
    expect(s.quota.earlyBonus).toBe(5);
    expect(s.quota.starsAwarded).toBe(BASE_STARS + 5);
    expect(s.stars).toBe(0); // not yet
    s.cash += 100;
    updateQuota(s);
    while (s.day < s.quota.dueDay) {
      endDay(data, s);
      expect(s.stars).toBe(0);
    }
    expect(endDay(data, s)).toBe('quotaPassed');
    expect(s.stars).toBe(BASE_STARS + 5);
    expect(s.stats.starsEarned).toBe(BASE_STARS + 5);
    endDay(data, s);
    expect(s.stars).toBe(BASE_STARS + 5);
  });

  it("don't pay again for a save whose quota was paid under the old rules", () => {
    const s = newRun(data, 23);
    meetQuota(s);
    delete s.quota.starsPending; // as in a save from before stars were delayed
    while (endDay(data, s) !== 'quotaPassed');
    expect(s.stars).toBe(0);
  });

  it('give no bonus when met on the due day', () => {
    const s = newRun(data, 22);
    while (s.day < s.quota.dueDay) endDay(data, s);
    meetQuota(s);
    expect(s.quota.earlyBonus).toBe(0);
    endDay(data, s);
    expect(s.stars).toBe(BASE_STARS);
  });
});

describe('dealer', () => {
  it('never visits before any stars are earned', () => {
    for (let seed = 0; seed < 30; seed++) {
      const s = newRun(data, seed);
      for (let d = 1; d < 7; d++) {
        expect(s.dealer).toBeNull();
        endDay(data, s);
      }
    }
  });

  it('is guaranteed the morning after the first stars, at a run location', () => {
    for (let seed = 0; seed < 50; seed++) {
      const s = newRun(data, seed);
      meetQuota(s);
      // stars aren't paid until the quota ends, so he doesn't come before that
      while (s.day < s.quota.dueDay) {
        expect(s.dealer).toBeNull();
        endDay(data, s);
      }
      expect(s.dealer).toBeNull();
      endDay(data, s);
      expect(s.dealer).not.toBeNull();
      expect(s.locations.map((l) => l.id)).toContain(s.dealer!.locationId);
      expect(s.dealer!.offers).toHaveLength(CONFIG.dealer.offers);
      expect(s.dealer!.offers.every((o) => !o.sold)).toBe(true);
      expect(s.dealerSeen).toBe(true);
    }
  });

  /** Share of days the dealer visits after his first visit; also checks determinism. */
  function visitRate(): number {
    let visits = 0;
    let days = 0;
    for (let seed = 0; seed < 40; seed++) {
      const s = newRun(data, seed);
      passQuota(s);
      const a = JSON.parse(JSON.stringify(s)) as RunState;
      for (let d = 0; d < 5; d++) {
        endDay(data, s);
        endDay(data, a);
        expect(a.dealer).toEqual(s.dealer);
        visits += +(s.dealer !== null);
        days++;
      }
    }
    return visits / days;
  }

  it('then visits with CONFIG.dealer.chance per day, deterministically', () => {
    const saved = CONFIG.dealer.chance;
    try {
      CONFIG.dealer.chance = 1;
      expect(visitRate()).toBe(1);
      CONFIG.dealer.chance = 0.5;
      const rate = visitRate();
      expect(rate).toBeGreaterThan(0.35);
      expect(rate).toBeLessThan(0.65);
    } finally {
      CONFIG.dealer.chance = saved;
    }
  });

  /** A run where the dealer is here today, offering `deals`, with `stars` to spend. */
  function withDealer(seed: number, deals: DealerDeal[], stars = 10): RunState {
    const s = newRun(data, seed);
    s.stars = stars;
    s.dealer = {
      locationId: s.locations[0].id,
      offers: deals.map((deal) => ({ deal, cost: CONFIG.dealer.cost[deal.kind], sold: false })),
    };
    return s;
  }

  it("takes one actor's spot at his location", () => {
    let seen = 0;
    for (let seed = 0; seed < 40; seed++) {
      const s = newRun(data, seed);
      passQuota(s);
      for (let d = 0; d < 5; d++) {
        for (const l of s.locations) {
          const slots = data.locations[l.id].actorSlots;
          expect(l.actorIds).toHaveLength(s.dealer?.locationId === l.id ? slots - 1 : slots);
        }
        seen += +(s.dealer !== null);
        endDay(data, s);
      }
    }
    expect(seen).toBeGreaterThan(0);
  });

  it('offers distinct deals', () => {
    for (let seed = 0; seed < 40; seed++) {
      const s = newRun(data, seed);
      passQuota(s);
      const keys = s.dealer!.offers.map((o) => JSON.stringify(o.deal));
      expect(new Set(keys).size).toBe(keys.length);
    }
  });

  it('blocks buying without enough stars, and sells each offer only once', () => {
    const s = withDealer(1, [{ kind: 'bag', tier: 1 }, { kind: 'luck', good: 'tools' }], 2);
    expect(dealerBlock(s, 0)).toBe('noStars');
    expect(buyDealerDeal(data, s, 0)).toBe(false);
    s.stars = 7;
    expect(buyDealerDeal(data, s, 0)).toBe(true);
    expect(s.stars).toBe(4);
    expect(dealerBlock(s, 0)).toBe('sold');
    expect(buyDealerDeal(data, s, 0)).toBe(false);
    expect(s.stars).toBe(4);
    // the other offer is still for sale
    expect(buyDealerDeal(data, s, 1)).toBe(true);
    expect(s.stars).toBe(4 - CONFIG.dealer.cost.luck);
    expect(dealerBlock(s, 5)).toBe('sold');
  });

  it('every deal is one time only: bought deals are never offered again', () => {
    const s = newRun(data, 8);
    const pool = eligibleDeals(data, s);
    s.dealer = { locationId: s.locations[0].id, offers: pool.map((deal) => ({ deal, cost: 0, sold: false })) };
    pool.forEach((_, i) => buyDealerDeal(data, s, i));
    const left = eligibleDeals(data, s);
    for (const d of pool) if (!isRanked(d)) expect(left).not.toContainEqual(d);
  });

  it('bag upgrades come one at a time, each after the one before, then stop', () => {
    const s = newRun(data, 2);
    const bags = () => eligibleDeals(data, s).filter((d) => d.kind === 'bag');
    for (let tier = 1; tier <= BAG_TIERS; tier++) {
      expect(bags()).toEqual([{ kind: 'bag', tier }]);
      s.dealer = { locationId: s.locations[0].id, offers: [{ deal: bags()[0], cost: dealCost(bags()[0]), sold: false }] };
      s.stars = 99;
      buyDealerDeal(data, s, 0);
      expect(s.capacity).toBe(CAPACITY + tier);
    }
    expect(bags()).toEqual([]);
    expect(CONFIG.dealer.bagCosts.map((_, i) => dealCost({ kind: 'bag', tier: i + 1 }))).toEqual(CONFIG.dealer.bagCosts);
  });

  it('discount lowers sellers of that good right away (floor $1), not buyers, and is not offered again', () => {
    const s = withDealer(3, [{ kind: 'discount', good: 'tools' }]);
    const seller = withActor(s, 'supplier', 'tools');
    const buyer = withActor(s, 'buyer', 'tools');
    const sellerBefore = offer(s, seller, 'tools').price;
    const buyerBefore = offer(s, buyer, 'tools').price;
    buyDealerDeal(data, s, 0);
    expect(offer(s, seller, 'tools').price).toBe(Math.max(1, sellerBefore - data.goods.tools.dealerDiscount));
    expect(offer(s, buyer, 'tools').price).toBe(buyerBefore);
    expect(eligibleDeals(data, s)).not.toContainEqual({ kind: 'discount', good: 'tools' });
    // later days keep the discount
    for (let d = 0; d < 5; d++) {
      endDay(data, s);
      for (const l of s.locations)
        for (const id of l.actorIds)
          for (const ag of data.actors[id].goods)
            if (ag.good === 'tools' && data.actors[id].role === 'supplier') {
              const o = offer(s, id, 'tools');
              expect(o.price).toBe(Math.max(1, tierPrice(ag.prices, o.tier) - data.goods.tools.dealerDiscount));
            }
    }
  });

  it('stock deal adds daily stock to sellers of that good (today too), not buyers, once', () => {
    const s = withDealer(7, [{ kind: 'stock', good: 'seashell' }]);
    const seller = withActor(s, 'supplier', 'seashell');
    const buyer = withActor(s, 'buyer', 'seashell');
    const sellerBefore = offer(s, seller, 'seashell').left;
    const buyerBefore = offer(s, buyer, 'seashell').left;
    buyDealerDeal(data, s, 0);
    expect(offer(s, seller, 'seashell').left).toBe(sellerBefore + CONFIG.dealer.stockStep);
    expect(offer(s, buyer, 'seashell').left).toBe(buyerBefore);
    expect(eligibleDeals(data, s)).not.toContainEqual({ kind: 'stock', good: 'seashell' });
    expect(eligibleDeals(data, s)).toContainEqual({ kind: 'stock', good: 'tools' });
    // later days keep the extra stock
    for (let d = 0; d < 5; d++) {
      endDay(data, s);
      for (const l of s.locations)
        for (const id of l.actorIds)
          for (const ag of data.actors[id].goods)
            if (ag.good === 'seashell' && data.actors[id].role === 'supplier') {
              const left = offer(s, id, 'seashell').left;
              expect(left).toBeGreaterThanOrEqual(1 + CONFIG.dealer.stockStep);
              expect(left).toBeLessThanOrEqual(3 + CONFIG.dealer.stockStep);
            }
    }
  });

  it('all-goods deals hit every good and stack with the per-good ones', () => {
    const s = withDealer(9, [
      { kind: 'discount', good: 'tools' },
      { kind: 'discountAll' },
      { kind: 'stock', good: 'tools' },
      { kind: 'stockAll', tier: 1 },
    ], 99);
    const tools = withActor(s, 'supplier', 'tools');
    const berry = withActor(s, 'supplier', 'strawberry');
    const before = { tools: offer(s, tools, 'tools'), berry: offer(s, berry, 'strawberry') };
    const was = { tp: before.tools.price, tl: before.tools.left, bp: before.berry.price, bl: before.berry.left };
    s.dealer!.offers.forEach((_, i) => buyDealerDeal(data, s, i));
    const { discountAll, stockAll, stockStep } = CONFIG.dealer;
    expect(offer(s, tools, 'tools').price).toBe(Math.max(1, was.tp - data.goods.tools.dealerDiscount - discountAll));
    expect(offer(s, tools, 'tools').left).toBe(was.tl + stockStep + stockAll);
    expect(offer(s, berry, 'strawberry').price).toBe(Math.max(1, was.bp - discountAll));
    expect(offer(s, berry, 'strawberry').left).toBe(was.bl + stockAll);
    // the next Overflowing Supply rank is up; the other all-goods deals are still at rank I
    expect(eligibleDeals(data, s).filter(isUniversal)).toEqual(
      [
        { kind: 'stockAll', tier: 2 },
        { kind: 'buyerStockAll', tier: 1 },
        { kind: 'luckAll', tier: 1 },
      ].filter((d) => dealEnabled(d as DealerDeal)),
    );
  });

  it('picks each kind of deal evenly, then the good within it', () => {
    const kinds = new Map<string, number>();
    const stockGoods = new Map<string, number>();
    const seeds = 900;
    for (let seed = 0; seed < seeds; seed++) {
      const s = newRun(data, seed);
      s.stats.starsEarned = 1;
      // the first offer is drawn from the full pool, so every kind has the same chance
      const first = rollDealer(data, s)!.offers[0].deal;
      kinds.set(first.kind, (kinds.get(first.kind) ?? 0) + 1);
      if (first.kind === 'stock') stockGoods.set(first.good, (stockGoods.get(first.good) ?? 0) + 1);
    }
    const all = new Set(allDeals(data).filter(dealEnabled).map((d) => d.kind));
    expect(kinds.size).toBe(all.size);
    const even = seeds / all.size;
    for (const n of kinds.values()) {
      expect(n).toBeGreaterThan(even * 0.6);
      expect(n).toBeLessThan(even * 1.4);
    }
    // stock (one per good) is as likely as stockAll (one deal)
    expect(Math.abs(kinds.get('stock')! - kinds.get('stockAll')!)).toBeLessThan(even * 0.6);
    expect(stockGoods.size).toBe(Object.keys(data.goods).length);
  });

  it('ranked all-goods deals come one rank at a time and stack', () => {
    const saved = CONFIG.dealer.disabled;
    CONFIG.dealer.disabled = []; // exercise every ranked kind, even ones switched off for now
    const s = newRun(data, 11);
    const berry = withActor(s, 'supplier', 'strawberry');
    const was = offer(s, berry, 'strawberry').left;
    for (const kind of ['stockAll', 'buyerStockAll', 'luckAll'] as const) {
      for (let tier = 1; tier <= CONFIG.dealer.ranks[kind]; tier++) {
        const next = eligibleDeals(data, s).filter((d) => d.kind === kind);
        expect(next).toEqual([{ kind, tier }]);
        s.dealer = { locationId: s.locations[0].id, offers: [{ deal: next[0], cost: 0, sold: false }] };
        buyDealerDeal(data, s, 0);
      }
      expect(eligibleDeals(data, s).filter((d) => d.kind === kind)).toEqual([]);
    }
    const { ranks } = CONFIG.dealer;
    expect(s.perks.stockAll).toBe(ranks.stockAll * CONFIG.dealer.stockAll);
    expect(offer(s, berry, 'strawberry').left).toBe(was + ranks.stockAll * CONFIG.dealer.stockAll);
    expect(s.perks.buyerStockAll).toBe(ranks.buyerStockAll * CONFIG.dealer.buyerStockAll);
    expect(s.perks.luckAll).toBeCloseTo(ranks.luckAll * CONFIG.dealer.luckAll);
    CONFIG.dealer.disabled = saved;
  });

  it("demand deals raise buyers' daily demand, today and from then on", () => {
    const s = withDealer(12, [{ kind: 'buyerStock', good: 'seashell' }, { kind: 'buyerStockAll', tier: 1 }], 99);
    const shell = withActor(s, 'buyer', 'seashell');
    const tools = withActor(s, 'buyer', 'tools');
    const seller = withActor(s, 'supplier', 'tools');
    const was = { shell: offer(s, shell, 'seashell').left, tools: offer(s, tools, 'tools').left, seller: offer(s, seller, 'tools').left };
    s.dealer!.offers.forEach((_, i) => buyDealerDeal(data, s, i));
    const { buyerStockStep: step, buyerStockAll: all } = CONFIG.dealer;
    expect(offer(s, shell, 'seashell').left).toBe(was.shell + step + all);
    expect(offer(s, tools, 'tools').left).toBe(was.tools + all);
    expect(offer(s, seller, 'tools').left).toBe(was.seller); // sellers untouched
    expect(extraDemand(s, 'seashell')).toBe(step + all);
    expect(extraDemand(s, 'tools')).toBe(all);
    // tomorrow's buyers roll their demand with the bonus
    s.quota.dueDay = 9999;
    endDay(data, s);
    for (const l of s.locations)
      for (const id of l.actorIds) {
        const a = data.actors[id];
        if (a.role !== 'buyer') continue;
        for (const ag of a.goods)
          expect(offer(s, id, ag.good).left).toBeGreaterThanOrEqual(ag.qtyMin + extraDemand(s, ag.good));
      }
  });

  it('brings a cheap deal on his first visit after each met quota', () => {
    const saved = CONFIG.dealer.weight;
    // make the pricey all-goods deals overwhelmingly likely, so the guarantee has to do the work
    CONFIG.dealer.weight = { discountAll: 1000, stockAll: 1000, buyerStockAll: 1000, luckAll: 1000 };
    try {
      for (let seed = 0; seed < 60; seed++) {
        const s = newRun(data, seed);
        meetQuota(s);
        expect(s.dealerCheapOwed).toBeFalsy(); // owed once the stars are paid
        passQuota(s);
        let visit = s.dealer;
        for (let d = 0; d < 20 && !visit; d++) {
          s.quota.dueDay = 9999;
          endDay(data, s);
          visit = s.dealer;
        }
        expect(visit!.offers.some((o) => o.cost <= CONFIG.dealer.cheapAfterQuota)).toBe(true);
        expect(s.dealerCheapOwed).toBe(false);
      }
    } finally {
      CONFIG.dealer.weight = saved;
    }
  });

  it('stays away once everything has been bought', () => {
    const s = newRun(data, 10);
    s.stats.starsEarned = 1;
    for (let i = 0; i < 10; i++) {
      const pool = eligibleDeals(data, s);
      if (pool.length === 0) break;
      s.dealer = { locationId: s.locations[0].id, offers: pool.map((deal) => ({ deal, cost: 0, sold: false })) };
      pool.forEach((_, j) => buyDealerDeal(data, s, j));
    }
    expect(eligibleDeals(data, s)).toEqual([]);
    s.dealerSeen = false; // even the guaranteed visit
    expect(rollDealer(data, s)).toBeNull();
  });

  it("luck shifts that good's seller and buyer tiers towards great/amazing, not other goods", () => {
    const s = withDealer(4, [{ kind: 'luck', good: 'seashell' }]);
    s.quota = quotaFor(1); // past the first quota's gentler buyers
    buyDealerDeal(data, s, 0);
    const step = CONFIG.dealer.luckStep;
    const buyer = CONFIG.buyerDealWeights;
    const seller = CONFIG.dealWeights;
    // buyers: bad pays for both
    const w = tierWeights(s, 'seashell', 'buyer');
    expect(w.bad).toBeCloseTo(buyer.bad - 2 * step);
    expect(w.good).toBeCloseTo(buyer.good);
    expect(w.great).toBeCloseTo(buyer.great + step);
    expect(w.amazing).toBeCloseTo(buyer.amazing + step);
    // sellers have no bad, so good pays
    const sw = tierWeights(s, 'seashell', 'supplier');
    expect(sw.bad).toBeUndefined();
    expect(sw.good).toBeCloseTo(seller.good! - 2 * step);
    expect(sw.great).toBeCloseTo(seller.great! + step);
    expect(sw.amazing).toBeCloseTo(seller.amazing! + step);
    expect(tierWeights(s, 'tools', 'buyer')).toEqual(buyer);
    expect(tierWeights(s, 'tools', 'supplier')).toEqual(seller);
    expect(eligibleDeals(data, s)).not.toContainEqual({ kind: 'luck', good: 'seashell' });
    expect(eligibleDeals(data, s)).toContainEqual({ kind: 'luck', good: 'tools' });
    const counts = { shellBuyer: { bad: 0, n: 0 }, otherBuyer: { bad: 0, n: 0 }, shellSeller: { good: 0, n: 0 }, otherSeller: { good: 0, n: 0 } };
    for (let d = 0; d < 400; d++) {
      s.quota.dueDay = 9999; // keep the run alive
      visit(data, s, s.locations[0].id); // use up the tier deck cards, as a player would
      endDay(data, s);
      for (const l of s.locations)
        for (const id of l.actorIds)
          for (const ag of data.actors[id].goods) {
            const tier = offer(s, id, ag.good).tier;
            const shell = ag.good === 'seashell';
            if (data.actors[id].role === 'supplier') {
              const c = shell ? counts.shellSeller : counts.otherSeller;
              c.n++;
              c.good += +(tier === 'good');
            } else {
              const c = shell ? counts.shellBuyer : counts.otherBuyer;
              c.n++;
              c.bad += +(tier === 'bad');
            }
          }
    }
    expect(counts.shellBuyer.bad / counts.shellBuyer.n).toBeCloseTo(w.bad!, 1);
    expect(counts.otherBuyer.bad / counts.otherBuyer.n).toBeCloseTo(buyer.bad, 1);
    expect(counts.shellSeller.good / counts.shellSeller.n).toBeCloseTo(sw.good!, 1);
    expect(counts.otherSeller.good / counts.otherSeller.n).toBeCloseTo(seller.good!, 1);
  });

  it('keeps bad buyers until the second rank of all-goods luck', () => {
    const s = newRun(data, 1);
    s.quota = quotaFor(1);
    s.perks.luckAll = CONFIG.dealer.luckAll;
    expect(tierWeights(s, 'tools', 'buyer').bad).toBeGreaterThan(0);
    s.perks.luckAll = 2 * CONFIG.dealer.luckAll;
    expect(tierWeights(s, 'tools', 'buyer').bad).toBeCloseTo(0);
  });

  it('all-goods luck is at least as strong, hits every good, and stacks with the per-good one', () => {
    const s = withDealer(5, [{ kind: 'luck', good: 'tools' }, { kind: 'luckAll', tier: 1 }], 20);
    s.quota = quotaFor(1);
    s.dealer!.offers.forEach((_, i) => expect(buyDealerDeal(data, s, i)).toBe(true));
    const { luckStep: step, luckAll: all } = CONFIG.dealer;
    expect(all).toBeGreaterThanOrEqual(step);
    const base = CONFIG.buyerDealWeights;
    // bad pays first, then good
    const after = (s: number) => {
      const bad = Math.max(0, base.bad - 2 * s);
      return { bad, good: base.good - (2 * s - (base.bad - bad)) };
    };
    const bw = (good: string) => tierWeights(s, good, 'buyer');
    expect(bw('tools').great).toBeCloseTo(base.great + step + all);
    expect(bw('tools').bad).toBeCloseTo(after(step + all).bad);
    expect(bw('tools').good).toBeCloseTo(after(step + all).good);
    expect(tierWeights(s, 'tools', 'supplier').good).toBeCloseTo(CONFIG.dealWeights.good! - 2 * (step + all));
    for (const good of ['strawberry', 'seashell', 'old_record']) {
      expect(bw(good).amazing).toBeCloseTo(base.amazing + all);
      expect(bw(good).bad).toBeCloseTo(after(all).bad);
      expect(bw(good).good).toBeCloseTo(after(all).good);
      expect(tierWeights(s, good, 'supplier').amazing).toBeCloseTo(CONFIG.dealWeights.amazing! + all);
    }
    // every rank plus the per-good one still leaves some chance of a plain good deal on both sides
    s.perks.luckAll = CONFIG.dealer.ranks.luckAll * all;
    for (const good of Object.keys(data.goods)) {
      s.perks.luck[good] = step;
      expect(bw(good).good).toBeGreaterThan(0);
      expect(tierWeights(s, good, 'supplier').good).toBeGreaterThan(0);
    }
  });
});

describe('stamps', () => {
  it('never offers disabled kinds, and offers them again once re-enabled', () => {
    const saved = CONFIG.dealer.disabled;
    try {
      CONFIG.dealer.disabled = ['discount', 'discountAll'];
      const s = newRun(data, 1);
      const kinds = (pool: DealerDeal[]) => new Set(pool.map((d) => d.kind));
      expect(kinds(eligibleDeals(data, s))).not.toContain('discount');
      expect(kinds(eligibleDeals(data, s))).not.toContain('discountAll');
      CONFIG.dealer.disabled = [];
      expect(kinds(eligibleDeals(data, s))).toContain('discount');
      expect(kinds(eligibleDeals(data, s))).toContain('discountAll');
    } finally {
      CONFIG.dealer.disabled = saved;
    }
  });

  it('dealFromKey inverts dealKey for every deal', () => {
    for (const d of allDeals(data)) expect(dealFromKey(dealKey(d))).toEqual(d);
  });

  it('eligibleDeals is every unowned deal, with only the first rank of ranked ones', () => {
    const s = newRun(data, 1);
    const pool = eligibleDeals(data, s);
    expect(pool.filter((d) => d.kind === 'bag')).toEqual([{ kind: 'bag', tier: 1 }]);
    const extraRanks = Object.entries(CONFIG.dealer.ranks)
      .filter(([kind]) => dealEnabled({ kind: kind as 'bag', tier: 1 }))
      .reduce((sum, [, n]) => sum + n - 1, 0);
    expect(pool).toHaveLength(allDeals(data).filter(dealEnabled).length - extraRanks);
    expect(BAG_TIERS).toBe(CONFIG.dealer.ranks.bag);
  });
});

describe('canAct', () => {
  it('is false with no cash and an empty bag, true with cash for a seller here', () => {
    const s = newRun(data, 3);
    const seller = withActor(s, 'supplier', 'strawberry');
    const loc = s.locations.find((l) => l.actorIds.includes(seller))!.id;
    s.dealer = null;
    s.cash = 0;
    s.inventory = [];
    expect(canAct(data, s, loc)).toBe(false);
    s.cash = 1000;
    expect(canAct(data, s, loc)).toBe(true);
  });

  it('is true when the Dealer is here with an affordable deal', () => {
    const s = newRun(data, 3);
    const loc = s.locations[0].id;
    s.cash = 0;
    s.inventory = [];
    s.stars = 10;
    s.dealer = { locationId: loc, offers: [{ deal: { kind: 'stockAll', tier: 1 }, cost: 6, sold: false }] };
    expect(canAct(data, s, loc)).toBe(true);
    s.stars = 2;
    expect(canAct(data, s, loc)).toBe(false);
  });
});

describe('tier deck', () => {
  const cycle = (seed: number, role: 'supplier' | 'buyer', quota: number, c: number, weights: Partial<Record<(typeof TIERS)[number], number>>) => {
    const counts: Record<string, number> = { bad: 0, good: 0, great: 0, amazing: 0 };
    for (let i = 0; i < CONFIG.deckSize; i++) counts[tierAt(deckCard(seed, role, quota, c * CONFIG.deckSize + i), weights)]++;
    return counts;
  };

  it('deals every cycle to the tier weights: whole cards exactly, the rest split between neighbours', () => {
    expect(CONFIG.deckSize).toBe(10);
    for (let seed = 1; seed <= 30; seed++) {
      for (const [q, c] of [[0, 0], [0, 1], [3, 2]]) {
        const w1 = cycle(seed, 'buyer', q, c, CONFIG.firstQuotaBuyerDealWeights); // 1 / 5 / 2.5 / 1.5
        expect(w1.bad).toBe(1);
        expect(w1.good).toBe(5);
        expect([2, 3]).toContain(w1.great);
        expect(w1.great + w1.amazing).toBe(4);
        const later = cycle(seed, 'buyer', q, c, CONFIG.buyerDealWeights); // 2 / 4 / 2.5 / 1.5
        expect(later.bad).toBe(2);
        expect(later.good).toBe(4);
        expect(later.great + later.amazing).toBe(4);
        expect(cycle(seed, 'supplier', q, c, CONFIG.dealWeights)).toEqual({ bad: 0, good: 5, great: 3, amazing: 2 });
      }
    }
  });

  it('is right on average for weights that split a card', () => {
    let great = 0;
    for (let seed = 1; seed <= 400; seed++) great += cycle(seed, 'buyer', 0, 0, CONFIG.buyerDealWeights).great;
    expect(great / 400).toBeCloseTo(2.5, 0);
  });

  it('shuffles each cycle and each quota differently', () => {
    const order = (q: number, c: number) => Array.from({ length: CONFIG.deckSize }, (_, i) => deckCard(7, 'buyer', q, c * CONFIG.deckSize + i));
    expect(order(0, 0)).not.toEqual(order(0, 1));
    expect(order(0, 0)).not.toEqual(order(1, 0));
    expect(order(0, 0)).toEqual(order(0, 0));
  });

  it('gives the first quota half the bad buyers, then the normal weights', () => {
    const s = newRun(data, 1);
    expect(tierWeights(s, 'tools', 'buyer')).toEqual(CONFIG.firstQuotaBuyerDealWeights);
    expect(tierWeights(s, 'tools', 'supplier')).toEqual(CONFIG.dealWeights);
    s.quota = quotaFor(1);
    expect(tierWeights(s, 'tools', 'buyer')).toEqual(CONFIG.buyerDealWeights);
  });

  it('only the visited location uses up cards, and it gets the next ones in order', () => {
    const s = newRun(data, 21);
    const loc = s.locations[0];
    const before = { ...s.deck };
    // every location reads from the same deck position
    for (const l of s.locations) {
      const next = { ...s.deck };
      for (const id of l.actorIds) {
        const a = data.actors[id];
        for (const ag of a.goods) {
          const u = deckCard(s.seed, a.role, s.quota.index, next[a.role]++);
          expect(offer(s, id, ag.good).tier).toBe(tierAt(u, tierWeights(s, ag.good, a.role)));
        }
      }
    }
    visit(data, s, loc.id);
    const used = deckCards(data, s, loc.id);
    expect(used.supplier + used.buyer).toBeGreaterThan(0);
    expect(s.deck).toEqual({ supplier: before.supplier + used.supplier, buyer: before.buyer + used.buyer });
    visit(data, s, s.locations[1].id); // already committed today: no change
    expect(s.deck).toEqual({ supplier: before.supplier + used.supplier, buyer: before.buyer + used.buyer });
    endDay(data, s);
    expect(s.deck).toEqual({ supplier: before.supplier + used.supplier, buyer: before.buyer + used.buyer });
  });

  it('starts a fresh deck when a quota is passed', () => {
    const s = newRun(data, 22);
    while (s.day < s.quota.dueDay) {
      visit(data, s, s.locations[0].id);
      endDay(data, s);
    }
    expect(s.deck.supplier + s.deck.buyer).toBeGreaterThan(0);
    s.cash = s.quota.amount;
    expect(endDay(data, s)).toBe('quotaPassed');
    expect(s.deck).toEqual({ supplier: 0, buyer: 0 });
  });

  it('rolls independently when switched off', () => {
    const saved = CONFIG.tierDeck;
    try {
      CONFIG.tierDeck = false;
      const a = newRun(data, 30);
      const b = newRun(data, 30);
      b.deck = { supplier: 7, buyer: 3 };
      expect(rollMarket(data, b)).toEqual(rollMarket(data, a));
    } finally {
      CONFIG.tierDeck = saved;
    }
  });
});
