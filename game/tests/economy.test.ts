import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { rngFor } from '../src/engine/rng';
import { CONFIG } from '../src/game/config';
import { buildData } from '../src/game/data';
import { dealActors } from '../src/game/deal';
import { rollMarket, rollTier } from '../src/game/economy';
import {
  avgPaid, buy, buyBlock, CAPACITY, endDay, FIRST_QUOTA, guaranteedGood, newRun, offer, quotaFor, sell, sellBlock,
  START_CASH,
} from '../src/game/run';
import { type RunState, TIERS } from '../src/game/types';
import { loadTestData } from './helpers';

const data = loadTestData();
const DEFAULT_CONFIG = { ...CONFIG, dealWeights: { ...CONFIG.dealWeights } };
afterEach(() => {
  Object.assign(CONFIG, DEFAULT_CONFIG, { dealWeights: { ...DEFAULT_CONFIG.dealWeights } });
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

  it('rejects price lists whose tiers are not ordered in the player\'s favour', () => {
    const goods = Object.values(data.goods);
    const actors = Object.values(data.actors);
    const locations = Object.values(data.locations);
    expect(() => buildData(goods, actors, locations)).not.toThrow();
    const flip = (role: string) =>
      actors.map((a) =>
        a.role === role
          ? { ...a, goods: a.goods.map((g) => ({ ...g, prices: { good: g.prices.amazing, great: g.prices.great, amazing: g.prices.good } })) }
          : a,
      );
    expect(() => buildData(goods, flip('supplier'), locations)).toThrow(/good -> great -> amazing/);
    expect(() => buildData(goods, flip('buyer'), locations)).toThrow(/good -> great -> amazing/);
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

describe('deal tiers', () => {
  it('roll roughly in proportion to CONFIG.dealWeights', () => {
    const r = rngFor(1, 'tier-test');
    const counts = { good: 0, great: 0, amazing: 0 };
    const n = 20000;
    for (let i = 0; i < n; i++) counts[rollTier(r)]++;
    for (const t of TIERS) expect(counts[t] / n).toBeCloseTo(CONFIG.dealWeights[t], 1);
  });

  it('respect a changed weighting', () => {
    CONFIG.dealWeights = { good: 0, great: 0, amazing: 1 };
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
            expect(o.price).toBe(ag.prices[o.tier]);
            expect(o.left).toBeGreaterThanOrEqual(ag.qtyMin);
            expect(o.left).toBeLessThanOrEqual(ag.qtyMax);
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
    expect(s.quota).toEqual({ index: 0, amount: FIRST_QUOTA, dueDay: 7, met: false });
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

describe('stock limits (when enabled)', () => {
  beforeEach(() => {
    CONFIG.limitStock = true;
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
    expect(s.quota.amount).toBe(FIRST_QUOTA * 2);
    expect(s.quota.dueDay).toBe(14);
  });

  it('fails the run when the due day ends unmet', () => {
    const s = newRun(data, 12);
    for (let d = 1; d < 7; d++) endDay(data, s);
    expect(endDay(data, s)).toBe('failed');
    expect(s.status).toBe('failed');
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
