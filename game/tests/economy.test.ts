import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { rngFor } from '../src/engine/rng';
import { CONFIG } from '../src/game/config';
import { buildData } from '../src/game/data';
import { dealActors } from '../src/game/deal';
import { buyDealerDeal, dealerBlock, eligibleDeals, rollDealer } from '../src/game/dealer';
import { buyerWeights, rollMarket, rollTier } from '../src/game/economy';
import {
  avgPaid, buy, buyBlock, CAPACITY, endDay, FIRST_QUOTA, guaranteedGood, newRun, offer, quotaFor, sell, sellBlock,
  START_CASH, updateQuota,
} from '../src/game/run';
import { type DealerDeal, type RunState, TIERS } from '../src/game/types';
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
          ? { ...a, goods: a.goods.map((g) => ({ ...g, prices: { good: g.prices.amazing, great: g.prices.great, amazing: g.prices.good } })) }
          : a,
      );
    expect(() => buildData(goods, flip('supplier'), locations, data.dealer)).toThrow(/good -> great -> amazing/);
    expect(() => buildData(goods, flip('buyer'), locations, data.dealer)).toThrow(/good -> great -> amazing/);
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
    expect(s.quota).toEqual({ index: 0, amount: FIRST_QUOTA, dueDay: 7, met: false, stars: 3 });
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

/** Meet the current quota right now by handing over the cash. */
function meetQuota(s: RunState): void {
  s.cash = s.quota.amount;
  updateQuota(s);
}

describe('stars', () => {
  it('base stars follow the quota schedule: 3, then 6 from quota 2 on', () => {
    expect([0, 1, 2, 3, 6].map((i) => quotaFor(i).stars)).toEqual([3, 6, 6, 6, 6]);
  });

  it('are awarded once when the quota is met, plus 1 per day early', () => {
    const s = newRun(data, 21);
    endDay(data, s); // day 2, 5 days early
    meetQuota(s);
    expect(s.quota.earlyBonus).toBe(5);
    expect(s.quota.starsAwarded).toBe(8);
    expect(s.stars).toBe(8);
    s.cash += 100;
    updateQuota(s);
    expect(s.stars).toBe(8);
    expect(s.stats.starsEarned).toBe(8);
  });

  it('give no bonus when met on the due day', () => {
    const s = newRun(data, 22);
    while (s.day < s.quota.dueDay) endDay(data, s);
    meetQuota(s);
    expect(s.quota.earlyBonus).toBe(0);
    expect(s.stars).toBe(3);
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
      expect(s.dealer).toBeNull(); // not the same day
      endDay(data, s);
      expect(s.dealer).not.toBeNull();
      expect(s.locations.map((l) => l.id)).toContain(s.dealer!.locationId);
      expect(s.dealer!.sold).toBe(false);
      expect(s.dealerSeen).toBe(true);
    }
  });

  it('then visits about half the days, deterministically', () => {
    let visits = 0;
    let days = 0;
    for (let seed = 0; seed < 40; seed++) {
      const s = newRun(data, seed);
      meetQuota(s);
      endDay(data, s);
      const a = JSON.parse(JSON.stringify(s)) as RunState;
      for (let d = 0; d < 5; d++) {
        endDay(data, s);
        endDay(data, a);
        expect(a.dealer).toEqual(s.dealer);
        visits += +(s.dealer !== null);
        days++;
      }
    }
    expect(visits / days).toBeGreaterThan(0.35);
    expect(visits / days).toBeLessThan(0.65);
  });

  /** A run where the dealer is here today, offering `deal`, with `stars` to spend. */
  function withDealer(seed: number, deal: DealerDeal, stars = 10): RunState {
    const s = newRun(data, seed);
    s.stars = stars;
    s.dealer = { locationId: s.locations[0].id, deal, cost: CONFIG.dealer.cost[deal.kind], sold: false };
    return s;
  }

  it('blocks buying without enough stars, and sells only once a visit', () => {
    const s = withDealer(1, { kind: 'bag' }, 2);
    expect(dealerBlock(s)).toBe('noStars');
    expect(buyDealerDeal(data, s)).toBe(false);
    s.stars = 7;
    expect(buyDealerDeal(data, s)).toBe(true);
    expect(s.stars).toBe(4);
    expect(dealerBlock(s)).toBe('sold');
    expect(buyDealerDeal(data, s)).toBe(false);
    expect(s.stars).toBe(4);
  });

  it('bag deal adds a slot', () => {
    const s = withDealer(2, { kind: 'bag' });
    buyDealerDeal(data, s);
    expect(s.capacity).toBe(CAPACITY + 1);
  });

  it('discount lowers sellers of that good right away (floor $1), not buyers, and is not offered again', () => {
    const s = withDealer(3, { kind: 'discount', good: 'tools' });
    const seller = withActor(s, 'supplier', 'tools');
    const buyer = withActor(s, 'buyer', 'tools');
    const sellerBefore = offer(s, seller, 'tools').price;
    const buyerBefore = offer(s, buyer, 'tools').price;
    buyDealerDeal(data, s);
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
              expect(o.price).toBe(Math.max(1, ag.prices[o.tier] - data.goods.tools.dealerDiscount));
            }
    }
  });

  it('sellChance shifts buyer tiers towards great/amazing, but not sellers', () => {
    const s = withDealer(4, { kind: 'sellChance' });
    buyDealerDeal(data, s);
    s.dealer!.sold = false;
    buyDealerDeal(data, s);
    expect(s.perks.sellChance).toBeCloseTo(0.1);
    const w = buyerWeights(s);
    expect(w.good).toBeCloseTo(0.3);
    expect(w.great).toBeCloseTo(0.4);
    expect(w.amazing).toBeCloseTo(0.3);
    const counts = { buyer: { good: 0, n: 0 }, supplier: { good: 0, n: 0 } };
    for (let d = 0; d < 300; d++) {
      s.quota.dueDay = 9999; // keep the run alive
      endDay(data, s);
      for (const l of s.locations)
        for (const id of l.actorIds)
          for (const ag of data.actors[id].goods) {
            const c = counts[data.actors[id].role];
            c.n++;
            c.good += +(offer(s, id, ag.good).tier === 'good');
          }
    }
    expect(counts.buyer.good / counts.buyer.n).toBeCloseTo(0.3, 1);
    expect(counts.supplier.good / counts.supplier.n).toBeCloseTo(0.5, 1);
  });

  it("stops offering sellChance once buyers' good weight would drop below the minimum", () => {
    const s = newRun(data, 5);
    const has = () => eligibleDeals(data, s).some((d) => d.kind === 'sellChance');
    let bought = 0;
    while (has()) {
      s.perks.sellChance += CONFIG.dealer.sellChanceStep;
      bought++;
    }
    expect(bought).toBe(4);
    expect(buyerWeights(s).good).toBeCloseTo(CONFIG.dealer.minGoodWeight);
  });

  it('never offers a discount on a good that already has one', () => {
    const s = newRun(data, 6);
    s.stats.starsEarned = 1;
    for (const g of Object.keys(data.goods)) s.perks.discounts[g] = 1;
    for (let d = 1; d < 60; d++) {
      s.day = d;
      const v = rollDealer(data, s);
      if (v) expect(v.deal.kind).not.toBe('discount');
    }
  });
});
