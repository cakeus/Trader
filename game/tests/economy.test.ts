import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { rngFor } from '../src/engine/rng';
import { CONFIG } from '../src/game/config';
import { buildData } from '../src/game/data';
import { dealActors } from '../src/game/deal';
import {
  allDeals, BAG_TIERS, buyDealerDeal, dealCost, dealEnabled, dealerBlock, dealerOfferCount, dealFromKey, dealKey, eligibleDeals, grantDeal,
  isRanked, isUniversal, rarityFallback, rarityOdds, rarityOf, rollDealer, rollRarity,
} from '../src/game/dealer';
import {
  bustlePrice, dealPrice, deckCard, deckCards, extraDemand, offerPrice, rollMarket, rollStock, rollTier, tierAt, tierPrice, tierWeights,
} from '../src/game/economy';
import {
  avgPaid, BASE_STARS, buy, buyBlock, buyPrice, buyoutOffer, buyoutPrice, buyUnits, canAct, canDetour, CAPACITY, detour, endDay,
  endOfDayPayouts, FIRST_QUOTA, guaranteedGood, hagglerMultiplier, maxBuy, maxSell, newRun, nextSellPrice, offer, quotaFor, rescueGood,
  rollBadDay, sell, sellBlock, sellPrice, sellUnits, START_CASH, takeBuyout, updateQuota, visit,
} from '../src/game/run';
import { type DealerDeal, type RunState, type SingleKind, TIERS } from '../src/game/types';
import { areaView, goodOf } from '../src/game/area';
import { eventOn, weatherOn } from '../src/game/events';
import { loadTestData } from './helpers';

const full = loadTestData();
/** Most tests play in the first area. */
const data = areaView(full, 'bay');
const DEFAULT_CONFIG = { ...CONFIG, dealWeights: { ...CONFIG.dealWeights } };
const DEFAULT_RARITY_ODDS = structuredClone(CONFIG.dealer.rarityOdds);
afterEach(() => {
  Object.assign(CONFIG, DEFAULT_CONFIG, { dealWeights: { ...DEFAULT_CONFIG.dealWeights } });
  CONFIG.dealer.rarityOdds = structuredClone(DEFAULT_RARITY_ODDS);
});

/** Only common stamps are rolled (rarer ones only come up once the commons run out). */
function commonOnly(): void {
  CONFIG.dealer.rarityOdds = { epic: { base: 0, perWeek: 0 }, rare: { base: 0, perWeek: 0 } };
}

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
  it('has, per area, 4 goods with 2 sellers and 2 buyers each, and 3 locations of 3 slots', () => {
    expect(Object.keys(full.areas)).toEqual(['bay', 'peaks', 'crossing']);
    for (const area of Object.keys(full.areas)) {
      const v = areaView(full, area);
      expect(Object.keys(v.goods)).toHaveLength(4);
      expect(Object.keys(v.actors)).toHaveLength(16);
      for (const a of Object.values(v.actors)) expect(a.goods).toHaveLength(1);
      for (const good of Object.keys(v.goods)) {
        const count = (role: string) =>
          Object.values(v.actors).filter((a) => a.role === role && a.goods.some((g) => g.good === good)).length;
        expect(count('supplier')).toBe(2);
        expect(count('buyer')).toBe(2);
      }
      expect(Object.keys(v.locations)).toHaveLength(3);
      for (const l of Object.values(v.locations)) expect(l.actorSlots).toBe(3);
    }
  });

  it.each([
    ['peaks', 2],
    ['crossing', 4],
  ])("prices each %s good at %ix its category's bay good", (area, factor) => {
    for (const c of Object.keys(full.categories))
      for (const role of ['supplier', 'buyer']) {
        const prices = (area: string) => {
          const good = goodOf(full, c, area);
          return Object.values(full.actors)
            .filter((a) => a.role === role)
            .flatMap((a) => a.goods.filter((g) => g.good === good).map((g) => g.prices))
            .map((p) => JSON.stringify(p))
            .sort();
        };
        const scaled = prices('bay')
          .map((p) => JSON.stringify(Object.fromEntries(Object.entries(JSON.parse(p)).map(([t, v]) => [t, factor * (v as number)]))))
          .sort();
        expect(prices(area)).toEqual(scaled);
      }
  });

  it('gives each area its own cast of 16 actors', () => {
    const casts = Object.keys(full.areas).map((area) => Object.keys(areaView(full, area).actors));
    for (const cast of casts) expect(cast).toHaveLength(16);
    expect(new Set(casts.flat()).size).toBe(16 * casts.length);
    for (const a of Object.values(full.actors)) expect(a.goods).toHaveLength(1);
  });

  it('rejects an actor trading more than one good', () => {
    const extra = full.actors.walter.goods[0];
    const actors = Object.values(full.actors).map((a, i) => (i === 0 ? { ...a, goods: [...a.goods, extra] } : a));
    expect(() =>
      buildData(Object.values(full.goods), actors, Object.values(full.locations), full.dealer, Object.values(full.categories), Object.values(full.areas)),
    ).toThrow(/trades 2 goods/);
  });

  it('rejects bad dealer discounts and missing dealer slots', () => {
    const goods = Object.values(full.goods);
    const actors = Object.values(full.actors);
    const locations = Object.values(full.locations);
    const cats = Object.values(full.categories);
    const areas = Object.values(full.areas);
    const badGoods = goods.map((g, i) => (i === 0 ? { ...g, dealerDiscount: -1 } : g));
    expect(() => buildData(badGoods, actors, locations, data.dealer, cats, areas)).toThrow(/dealerDiscount/);
    const noSlot = locations.map((l, i) => (i === 0 ? { ...l, dealerSlot: undefined as never } : l));
    expect(() => buildData(goods, actors, noSlot, data.dealer, cats, areas)).toThrow(/dealerSlot/);
  });

  it('rejects price lists whose tiers are not ordered in the player\'s favour', () => {
    const goods = Object.values(full.goods);
    const actors = Object.values(full.actors);
    const locations = Object.values(full.locations);
    const cats = Object.values(full.categories);
    const areas = Object.values(full.areas);
    expect(() => buildData(goods, actors, locations, data.dealer, cats, areas)).not.toThrow();
    const flip = (role: string) =>
      actors.map((a) =>
        a.role === role
          ? { ...a, goods: a.goods.map((g) => ({ ...g, prices: { ...g.prices, good: g.prices.amazing, amazing: g.prices.good } })) }
          : a,
      );
    expect(() => buildData(goods, flip('supplier'), locations, data.dealer, cats, areas)).toThrow(/good -> great -> amazing \(no bad\)/);
    expect(() => buildData(goods, flip('buyer'), locations, data.dealer, cats, areas)).toThrow(/bad -> good -> great -> amazing/);
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
          const dealt = dealActors(data, seed, day, locIds, [good]);
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
        for (const good of [undefined, 'hammer']) {
          const dealt = dealActors(data, seed, day, locIds, good ? [good] : []);
          const sigs = locIds.map((l) => sig(dealt[l]));
          expect(new Set(sigs).size).toBe(sigs.length);
        }
  });

  it('with needSeller, gives every location a seller (even the Dealer location)', () => {
    for (let seed = 0; seed < 200; seed++)
      for (let day = 1; day <= 20; day++)
        for (const dealerAt of [undefined, locIds[seed % locIds.length]]) {
          const dealt = dealActors(data, seed, day, locIds, [], dealerAt, true);
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
    s.inventory = [item('strawberry'), item('hammer'), item('strawberry'), item('hammer')];
    expect(guaranteedGood(data, s)).toBe('hammer');
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
    const bag = ['hammer', 'hammer', 'seashell', 'strawberry'];
    for (let seed = 1; seed <= 200; seed++) expect(buyersOf(nextDay(seed, bag, 100), bag).length).toBeGreaterThan(0);
  });

  it('deals in a buyer when there is no money left to buy with', () => {
    for (let seed = 1; seed <= 200; seed++) expect(buyersOf(nextDay(seed, ['old_record'], 0), ['old_record'])).not.toEqual([]);
  });

  it("leaves the deal alone when you can still buy, or already can sell, or have nothing", () => {
    const s = newRun(data, 3);
    s.inventory = [item('hammer')];
    s.cash = 100;
    expect(rescueGood(data, s, [])).toBeNull(); // room and cash to buy
    s.cash = 0;
    const toolsBuyer = Object.keys(data.actors).find(
      (id) => data.actors[id].role === 'buyer' && data.actors[id].goods.some((g) => g.good === 'hammer'),
    )!;
    expect(rescueGood(data, s, [toolsBuyer])).toBeNull(); // a buyer is already here
    expect(rescueGood(data, s, [])).toBe('hammer');
    s.inventory = [];
    expect(rescueGood(data, s, [])).toBeNull(); // nothing to sell
  });

  it('picks a random item from the bag, not always the most common', () => {
    const picked = new Set<string>();
    for (let seed = 1; seed <= 60; seed++) {
      const s = newRun(data, seed);
      s.day = 2;
      s.cash = 0;
      s.inventory = [item('hammer'), item('hammer'), item('hammer'), item('seashell')];
      picked.add(rescueGood(data, s, [])!);
    }
    expect(picked).toEqual(new Set(['hammer', 'seashell']));
  });
});

describe('deal tiers', () => {
  it("roll seller stock evenly over its category's CONFIG.stockRange", () => {
    const n = 20000;
    for (const c of Object.keys(data.categories)) {
      const [min, max] = CONFIG.stockRange[c];
      const counts: Record<number, number> = {};
      for (let i = 0; i < n; i++) {
        const q = rollStock(rngFor(i, 'stock'), c);
        counts[q] = (counts[q] ?? 0) + 1;
      }
      expect(Object.keys(counts).map(Number).sort()).toEqual(Array.from({ length: max - min + 1 }, (_, i) => min + i));
      for (let q = min; q <= max; q++) expect(counts[q] / n).toBeCloseTo(1 / (max - min + 1), 1);
    }
  });

  it('roll roughly in proportion to CONFIG.dealWeights', () => {
    const r = rngFor(1, 'tier-test');
    const counts = { bad: 0, good: 0, great: 0, amazing: 0 };
    const n = 20000;
    for (let i = 0; i < n; i++) counts[rollTier(r)]++;
    for (const t of TIERS) expect(counts[t] / n).toBeCloseTo(CONFIG.dealWeights[t] ?? 0, 1);
  });

  it('give buyers the same weights as sellers, with no bad tier, in every quota', () => {
    const s = newRun(data, 1);
    for (const q of [0, 1, 4]) {
      s.quota = quotaFor(q);
      expect(tierWeights(data, s, 'hammer', 'buyer')).toEqual(CONFIG.dealWeights);
      expect(tierWeights(data, s, 'hammer', 'supplier')).toEqual(CONFIG.dealWeights);
    }
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

describe('rainstorm event (Blossom Bay, day 15 on)', () => {
  const rain = full.areas.bay.events!.find((e) => e.id === 'rainstorm')!;
  const buyerOffers = (s: RunState, d = data) =>
    Object.entries(s.market).filter(([k]) => d.actors[k.split(':')[0]].role === 'buyer').map(([, o]) => o);

  it('starts on day 15 and lasts until the move, with rain instead of the area weather', () => {
    expect(rain.fromDay).toBe(15);
    expect(eventOn(full, 'bay', 14)).toBeNull();
    expect(eventOn(full, 'bay', 15)?.id).toBe('rainstorm');
    expect(eventOn(full, 'bay', 21)?.id).toBe('rainstorm');
    expect(weatherOn(full, 'bay', 14)).toBeUndefined();
    expect(weatherOn(full, 'bay', 15)).toBe('rain');
    expect(weatherOn(full, 'bay', 21)).toBe('rain');
    expect(weatherOn(full, 'peaks', 22)).toBe('snow');
    expect(eventOn(full, 'peaks', 22)).toBeNull();
  });

  it('caps every buyer at buyerLimit a day, even with unlimited demand', () => {
    expect(CONFIG.limitDemand).toBe(false);
    const s = newRun(data, 99);
    s.day = 15;
    s.market = rollMarket(data, s);
    const buyer = withActor(s, 'buyer', 'strawberry');
    for (const o of buyerOffers(s)) expect(o).toMatchObject({ capped: true, left: rain.buyerLimit });
    s.inventory = Array.from({ length: 4 }, () => ({ good: 'strawberry', paid: 1, day: 15 }));
    expect(maxSell(s, buyer, 'strawberry')).toBe(rain.buyerLimit);
    expect(sell(data, s, buyer, 'strawberry', 99)).toBe(rain.buyerLimit);
    expect(s.inventory).toHaveLength(4 - rain.buyerLimit!);
    expect(sellBlock(s, buyer, 'strawberry')).toBe('noDemand');
    expect(maxSell(s, buyer, 'strawberry')).toBe(0);
  });

  it('leaves buyers uncapped before day 15 and in the peaks', () => {
    const s = newRun(data, 99);
    s.day = 14;
    s.market = rollMarket(data, s);
    for (const o of buyerOffers(s)) expect(o.capped).toBeUndefined();
    s.area = 'peaks';
    s.day = 22;
    s.locations = Object.keys(areaView(full, 'peaks').locations).map((id) => ({ id, actorIds: [] as string[] }));
    const peaks = areaView(full, 'peaks');
    const buyers = Object.keys(peaks.actors).filter((id) => peaks.actors[id].role === 'buyer');
    s.locations[0].actorIds = buyers.slice(0, 3);
    s.market = rollMarket(full, s);
    const offers = buyerOffers(s, peaks);
    expect(offers).toHaveLength(3);
    for (const o of offers) expect(o.capped).toBeUndefined();
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
    s.inventory = [{ good: 'hammer', paid: 10, day: 1 }, { good: 'strawberry', paid: 3, day: 1 }];
    s.cash = 0;
    expect(buyoutOffer(data, s)).toBeNull(); // not the due day yet
    for (let d = 1; d < 7; d++) endDay(data, s);
    s.inventory = [{ good: 'hammer', paid: 10, day: 1 }, { good: 'strawberry', paid: 3, day: 1 }];
    s.cash = FIRST_QUOTA - buyoutPrice(data, 'hammer') - buyoutPrice(data, 'strawberry');
    expect(buyoutPrice(data, 'hammer')).toBe(8);
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
    const s = withDealer(1, [{ kind: 'bag', tier: 1 }, { kind: 'luck', category: 'tools' }], 2);
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
      expect(s.capacity).toBe(CAPACITY + CONFIG.dealer.bagSlots.slice(0, tier).reduce((a, b) => a + b, 0));
    }
    expect(bags()).toEqual([]);
    expect(CONFIG.dealer.bagCosts.map((_, i) => dealCost({ kind: 'bag', tier: i + 1 }))).toEqual(CONFIG.dealer.bagCosts);
  });

  it('discount lowers sellers of that good right away (floor $1), not buyers, and is not offered again', () => {
    const s = withDealer(3, [{ kind: 'discount', category: 'tools' }]);
    const seller = withActor(s, 'supplier', 'hammer');
    const buyer = withActor(s, 'buyer', 'hammer');
    const sellerBefore = offer(s, seller, 'hammer').price;
    const buyerBefore = offer(s, buyer, 'hammer').price;
    buyDealerDeal(data, s, 0);
    expect(offer(s, seller, 'hammer').price).toBe(Math.max(1, sellerBefore - data.goods.hammer.dealerDiscount));
    expect(offer(s, buyer, 'hammer').price).toBe(buyerBefore);
    expect(eligibleDeals(data, s)).not.toContainEqual({ kind: 'discount', category: 'tools' });
    // later days keep the discount
    for (let d = 0; d < 5; d++) {
      endDay(data, s);
      for (const l of s.locations)
        for (const id of l.actorIds)
          for (const ag of data.actors[id].goods)
            if (ag.good === 'hammer' && data.actors[id].role === 'supplier') {
              const o = offer(s, id, 'hammer');
              expect(o.price).toBe(Math.max(1, tierPrice(ag.prices, o.tier) - data.goods.hammer.dealerDiscount));
            }
    }
  });

  it('daily discount halves the first unit bought each day (rounded up, min $1)', () => {
    const s = withDealer(3, [{ kind: 'dailyDiscount' }]);
    buyDealerDeal(data, s, 0);
    const seller = withActor(s, 'supplier', 'hammer');
    const o = offer(s, seller, 'hammer');
    o.left = 3;
    s.cash = o.price + Math.ceil(o.price / 2);
    expect(maxBuy(s, seller, 'hammer')).toBe(2);
    expect(buy(data, s, seller, 'hammer', 2)).toBe(2);
    expect(s.inventory.map((it) => it.paid)).toEqual([Math.ceil(o.price / 2), o.price]);
    expect(s.cash).toBe(0);
    // used up for today, back tomorrow
    expect(buyPrice(s, o)).toBe(o.price);
    endDay(data, s);
    expect(buyPrice(s, { tier: 'good', price: 5, left: 1 })).toBe(3);
    expect(buyPrice(s, { tier: 'good', price: 1, left: 1 })).toBe(1);
  });

  it('tip jar: a buyer tips once it has bought 2 today, once per day', () => {
    const s = withDealer(3, [{ kind: 'tip' }]);
    buyDealerDeal(data, s, 0);
    const buyer = withActor(s, 'buyer', 'seashell');
    const price = offer(s, buyer, 'seashell').price;
    s.inventory = Array.from({ length: 4 }, () => ({ good: 'seashell', paid: 1, day: 1 }));
    const cash = s.cash;
    sell(data, s, buyer, 'seashell', 1);
    expect(s.cash).toBe(cash + price);
    sell(data, s, buyer, 'seashell', 1);
    expect(s.cash).toBe(cash + 2 * price + CONFIG.dealer.tip);
    sell(data, s, buyer, 'seashell', 2);
    expect(s.cash).toBe(cash + 4 * price + CONFIG.dealer.tip);
    // without the stamp, no tip
    const t = newRun(data, 3);
    const b2 = withActor(t, 'buyer', 'seashell');
    t.inventory = Array.from({ length: 2 }, () => ({ good: 'seashell', paid: 1, day: 1 }));
    const c2 = t.cash;
    sell(data, t, b2, 'seashell', 2);
    expect(t.cash).toBe(c2 + 2 * offer(t, b2, 'seashell').price);
  });

  it('stamp collector: adds a stamp to his table right away, and one more every visit after', () => {
    commonOnly();
    const s = newRun(data, 21);
    s.stats.starsEarned = 1;
    s.stars = 99;
    s.stampDecks = { common: ['tip', 'luck:food', 'stock:music', 'bag'] };
    s.dealer = rollDealer(data, s)!;
    expect(s.dealer.offers.map((o) => dealKey(o.deal))).toEqual(['tip', 'luck:food', 'stock:music']);
    s.dealer.offers.unshift({ deal: { kind: 'collector' }, cost: 0, sold: false });
    expect(buyDealerDeal(data, s, 0)).toBe(true);
    // the next card joins today's visit
    expect(s.dealer.offers.map((o) => dealKey(o.deal))).toEqual(['collector', 'tip', 'luck:food', 'stock:music', 'bag:1']);
    expect(s.stampDecks.common).toEqual([]);
    expect(dealerOfferCount(s)).toBe(CONFIG.dealer.offers + CONFIG.dealer.collectorOffers);
    // later visits bring the extra stamp too
    s.day++;
    const visit = rollDealer(data, s)!;
    expect(visit.offers).toHaveLength(CONFIG.dealer.offers + CONFIG.dealer.collectorOffers);
    expect(new Set(visit.offers.map((o) => dealKey(o.deal))).size).toBe(visit.offers.length);
  });

  it("can't get enough: a buyer pays more after every unit sold to it today", () => {
    const s = withDealer(3, [{ kind: 'cantGetEnough' }]);
    buyDealerDeal(data, s, 0);
    const buyer = withActor(s, 'buyer', 'seashell');
    const price = offer(s, buyer, 'seashell').price;
    s.inventory = Array.from({ length: 3 }, () => ({ good: 'seashell', paid: 1, day: 1 }));
    const cash = s.cash;
    sell(data, s, buyer, 'seashell', 1);
    expect(s.cash).toBe(cash + price);
    const step = CONFIG.dealer.cantGetEnoughStep;
    expect(offer(s, buyer, 'seashell').price).toBe(price + step);
    sell(data, s, buyer, 'seashell', 2);
    expect(s.cash).toBe(cash + 3 * price + 3 * step);
    expect(s.stats.profit).toBe(3 * price + 3 * step - 3);
  });

  it('stock deal adds daily stock to sellers of that good (today too), not buyers, once', () => {
    const s = withDealer(7, [{ kind: 'stock', category: 'treasure' }]);
    const seller = withActor(s, 'supplier', 'seashell');
    const buyer = withActor(s, 'buyer', 'seashell');
    const sellerBefore = offer(s, seller, 'seashell').left;
    const buyerBefore = offer(s, buyer, 'seashell').left;
    buyDealerDeal(data, s, 0);
    expect(offer(s, seller, 'seashell').left).toBe(sellerBefore + CONFIG.dealer.stockStep.treasure);
    expect(offer(s, buyer, 'seashell').left).toBe(buyerBefore);
    expect(eligibleDeals(data, s)).not.toContainEqual({ kind: 'stock', category: 'treasure' });
    expect(eligibleDeals(data, s)).toContainEqual({ kind: 'stock', category: 'tools' });
    // later days keep the extra stock
    for (let d = 0; d < 5; d++) {
      endDay(data, s);
      for (const l of s.locations)
        for (const id of l.actorIds)
          for (const ag of data.actors[id].goods)
            if (ag.good === 'seashell' && data.actors[id].role === 'supplier') {
              const left = offer(s, id, 'seashell').left;
              expect(left).toBeGreaterThanOrEqual(CONFIG.stockRange.treasure[0] + CONFIG.dealer.stockStep.treasure);
              expect(left).toBeLessThanOrEqual(CONFIG.stockRange.treasure[1] + CONFIG.dealer.stockStep.treasure);
            }
    }
  });

  it('all-goods deals hit every good and stack with the per-good ones', () => {
    const s = withDealer(9, [
      { kind: 'discount', category: 'tools' },
      { kind: 'discountAll' },
      { kind: 'stock', category: 'tools' },
      { kind: 'stockAll', tier: 1 },
    ], 99);
    const tools = withActor(s, 'supplier', 'hammer');
    const berry = withActor(s, 'supplier', 'strawberry');
    const before = { tools: offer(s, tools, 'hammer'), berry: offer(s, berry, 'strawberry') };
    const was = { tp: before.tools.price, tl: before.tools.left, bp: before.berry.price, bl: before.berry.left };
    s.dealer!.offers.forEach((_, i) => buyDealerDeal(data, s, i));
    const { discountAll, stockAll, stockStep } = CONFIG.dealer;
    expect(offer(s, tools, 'hammer').price).toBe(Math.max(1, was.tp - data.goods.hammer.dealerDiscount - discountAll));
    expect(offer(s, tools, 'hammer').left).toBe((was.tl + stockStep.tools) * stockAll);
    expect(offer(s, berry, 'strawberry').price).toBe(Math.max(1, was.bp - discountAll));
    expect(offer(s, berry, 'strawberry').left).toBe(was.bl * stockAll);
    // Overflowing Supply is done; the other all-goods deals are still at rank I
    expect(eligibleDeals(data, s).filter(isUniversal)).toEqual(
      [
        { kind: 'buyerStockAll', tier: 1 },
        { kind: 'luckAll', tier: 1 },
      ].filter((d) => dealEnabled(d as DealerDeal)),
    );
  });

  it('deals common stamps from their shuffled deck, three a visit, reshuffling once it runs out', () => {
    commonOnly();
    const s = newRun(data, 5);
    s.stats.starsEarned = 1;
    const cards = allDeals(data).filter((d) => dealEnabled(d) && rarityOf(d) === 'common').length;
    const seen: string[] = [];
    // never buying anything: each cycle through the deck offers every card exactly once
    for (let day = 1; seen.length < cards * 2; day++) {
      s.day = day;
      s.dealerSeen = false; // make him come
      const visit = rollDealer(data, s)!;
      expect(visit.offers).toHaveLength(CONFIG.dealer.offers);
      const keys = visit.offers.map((o) => dealKey(o.deal));
      expect(new Set(keys).size).toBe(keys.length);
      seen.push(...keys);
    }
    for (const cycle of [seen.slice(0, cards), seen.slice(cards, cards * 2)]) {
      const counts = new Map<string, number>();
      for (const k of cycle) counts.set(k, (counts.get(k) ?? 0) + 1);
      // unowned ranked deals are always offered at rank I, once per rank
      expect(counts.get('bag:1')).toBe(CONFIG.dealer.ranks.bag);
      expect(counts.get('tip')).toBe(1);
    }
    expect(seen.slice(0, cards)).not.toEqual(seen.slice(cards, cards * 2));
  });

  it('skips cards it cannot offer yet without discarding them', () => {
    commonOnly();
    const s = newRun(data, 6);
    s.stats.starsEarned = 1;
    // two bag cards on top: only one bag rank can be offered at a time
    s.stampDecks = { common: ['bag', 'bag', 'tip', 'luck:food', 'stock:music'] };
    let visit = rollDealer(data, s)!;
    expect(visit.offers.map((o) => dealKey(o.deal))).toEqual(['bag:1', 'tip', 'luck:food']);
    expect(s.stampDecks.common).toEqual(['bag', 'stock:music']);
    s.dealer = visit;
    s.stars = 99;
    expect(buyDealerDeal(data, s, 0)).toBe(true);
    // the skipped bag card now brings the next rank
    s.day++;
    visit = rollDealer(data, s)!;
    expect(visit.offers.slice(0, 2).map((o) => dealKey(o.deal))).toEqual(['bag:2', 'stock:music']);
    // the third was dealt from a fresh shuffle of the rest (not the ones on his table, nor bag:1)
    expect(['bag:2', 'stock:music', 'bag:1']).not.toContain(dealKey(visit.offers[2].deal));
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
    expect(s.perks.stockAll).toBe(ranks.stockAll);
    expect(offer(s, berry, 'strawberry').left).toBe(was * CONFIG.dealer.stockAll ** ranks.stockAll);
    expect(s.perks.buyerStockAll).toBe(ranks.buyerStockAll * CONFIG.dealer.buyerStockAll);
    expect(s.perks.luckAll).toBeCloseTo(ranks.luckAll * CONFIG.dealer.luckAll);
    CONFIG.dealer.disabled = saved;
  });

  it("demand deals raise buyers' daily demand, today and from then on", () => {
    const s = withDealer(12, [{ kind: 'buyerStock', category: 'treasure' }, { kind: 'buyerStockAll', tier: 1 }], 99);
    const shell = withActor(s, 'buyer', 'seashell');
    const tools = withActor(s, 'buyer', 'hammer');
    const seller = withActor(s, 'supplier', 'hammer');
    const was = { shell: offer(s, shell, 'seashell').left, tools: offer(s, tools, 'hammer').left, seller: offer(s, seller, 'hammer').left };
    s.dealer!.offers.forEach((_, i) => buyDealerDeal(data, s, i));
    const { buyerStockStep: step, buyerStockAll: all } = CONFIG.dealer;
    expect(offer(s, shell, 'seashell').left).toBe(was.shell + step + all);
    expect(offer(s, tools, 'hammer').left).toBe(was.tools + all);
    expect(offer(s, seller, 'hammer').left).toBe(was.seller); // sellers untouched
    expect(extraDemand(data, s, 'seashell')).toBe(step + all);
    expect(extraDemand(data, s, 'hammer')).toBe(all);
    // tomorrow's buyers roll their demand with the bonus
    s.quota.dueDay = 9999;
    endDay(data, s);
    for (const l of s.locations)
      for (const id of l.actorIds) {
        const a = data.actors[id];
        if (a.role !== 'buyer') continue;
        for (const ag of a.goods)
          expect(offer(s, id, ag.good).left).toBeGreaterThanOrEqual(ag.qtyMin + extraDemand(data, s, ag.good));
      }
  });

  it('brings a cheap deal on his first visit after each met quota', () => {
    for (let seed = 0; seed < 60; seed++) {
        const s = newRun(data, seed);
        meetQuota(s);
        // pricey stamps on top of the deck, so the guarantee has to dig past them
        const pricey = ['stockAll', 'luckAll', 'stockAll', 'luckAll', 'stockAll', 'luckAll'];
        s.stampDecks = { common: [...pricey, 'tip', 'luck:food'] };
        expect(s.dealerCheapOwed).toBeFalsy(); // owed once the stars are paid
        passQuota(s);
        let visit = s.dealer;
        for (let d = 0; d < 20 && !visit; d++) {
          s.quota.dueDay = 9999;
          endDay(data, s);
          visit = s.dealer;
        }
        expect(visit!.offers[0].cost).toBeLessThanOrEqual(CONFIG.dealer.cheapAfterQuota);
        expect(s.dealerCheapOwed).toBe(false);
        // the pricey cards it skipped are still there, dealt next
        expect(visit!.offers.slice(1).every((o) => o.cost > CONFIG.dealer.cheapAfterQuota)).toBe(true);
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
    const s = withDealer(4, [{ kind: 'luck', category: 'treasure' }]);
    buyDealerDeal(data, s, 0);
    const step = CONFIG.dealer.luckStep;
    const seller = CONFIG.dealWeights;
    const buyer = seller;
    // good pays for both, the same on both sides
    const w = tierWeights(data, s, 'seashell', 'buyer');
    const sw = tierWeights(data, s, 'seashell', 'supplier');
    expect(w).toEqual(sw);
    expect(sw.bad).toBeUndefined();
    expect(sw.good).toBeCloseTo(seller.good! - 2 * step);
    expect(sw.great).toBeCloseTo(seller.great! + step);
    expect(sw.amazing).toBeCloseTo(seller.amazing! + step);
    expect(tierWeights(data, s, 'hammer', 'buyer')).toEqual(buyer);
    expect(tierWeights(data, s, 'hammer', 'supplier')).toEqual(seller);
    expect(eligibleDeals(data, s)).not.toContainEqual({ kind: 'luck', category: 'treasure' });
    expect(eligibleDeals(data, s)).toContainEqual({ kind: 'luck', category: 'tools' });
    const counts = { shellBuyer: { good: 0, n: 0 }, otherBuyer: { good: 0, n: 0 }, shellSeller: { good: 0, n: 0 }, otherSeller: { good: 0, n: 0 } };
    for (let d = 0; d < 400; d++) {
      s.quota.dueDay = 9999; // keep the run alive
      visit(data, s, s.locations[0].id); // use up the tier deck cards, as a player would
      endDay(data, s);
      // the run moves to the next area on day 22; the Treasure stamp covers its good there too
      for (const l of s.locations)
        for (const id of l.actorIds)
          for (const ag of areaView(full, s.area).actors[id].goods) {
            const tier = offer(s, id, ag.good).tier;
            const shell = full.goods[ag.good].category === 'treasure';
            if (full.actors[id].role === 'supplier') {
              const c = shell ? counts.shellSeller : counts.otherSeller;
              c.n++;
              c.good += +(tier === 'good');
            } else {
              const c = shell ? counts.shellBuyer : counts.otherBuyer;
              c.n++;
              c.good += +(tier === 'good');
            }
          }
    }
    // the bag stays empty, so there's no weekly bad day
    expect(counts.shellBuyer.good / counts.shellBuyer.n).toBeCloseTo(w.good!, 1);
    expect(counts.otherBuyer.good / counts.otherBuyer.n).toBeCloseTo(buyer.good!, 1);
    expect(counts.shellSeller.good / counts.shellSeller.n).toBeCloseTo(sw.good!, 1);
    expect(counts.otherSeller.good / counts.otherSeller.n).toBeCloseTo(seller.good!, 1);
  });

  it('all-goods luck is at least as strong, hits every good, and stacks with the per-good one', () => {
    const s = withDealer(5, [{ kind: 'luck', category: 'tools' }, { kind: 'luckAll', tier: 1 }], 20);
    s.dealer!.offers.forEach((_, i) => expect(buyDealerDeal(data, s, i)).toBe(true));
    const { luckStep: step, luckAll: all } = CONFIG.dealer;
    expect(all).toBeGreaterThanOrEqual(step);
    const base = CONFIG.dealWeights as Record<'good' | 'great' | 'amazing', number>;
    // good pays for both
    const after = (s: number) => ({ good: base.good - 2 * s });
    const bw = (good: string) => tierWeights(data, s, good, 'buyer');
    expect(bw('hammer').great).toBeCloseTo(base.great + step + all);
    expect(bw('hammer').bad).toBeUndefined();
    expect(bw('hammer').good).toBeCloseTo(after(step + all).good);
    expect(tierWeights(data, s, 'hammer', 'supplier').good).toBeCloseTo(CONFIG.dealWeights.good! - 2 * (step + all));
    for (const good of ['strawberry', 'seashell', 'old_record']) {
      expect(bw(good).amazing).toBeCloseTo(base.amazing + all);
      expect(bw(good).good).toBeCloseTo(after(all).good);
      expect(tierWeights(data, s, good, 'supplier').amazing).toBeCloseTo(CONFIG.dealWeights.amazing! + all);
    }
    // every rank plus the per-good one still leaves some chance of a plain good deal on both sides
    s.perks.luckAll = CONFIG.dealer.ranks.luckAll * all;
    for (const good of Object.keys(data.goods)) {
      s.perks.luck[data.goods[good].category] = step;
      expect(bw(good).good).toBeGreaterThan(0);
      expect(tierWeights(data, s, good, 'supplier').good).toBeGreaterThan(0);
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
        expect(cycle(seed, 'buyer', q, c, CONFIG.dealWeights)).toEqual({ bad: 0, good: 5, great: 3, amazing: 2 });
        expect(cycle(seed, 'supplier', q, c, CONFIG.dealWeights)).toEqual({ bad: 0, good: 5, great: 3, amazing: 2 });
        const split = cycle(seed, 'buyer', q, c, { good: 0.5, great: 0.25, amazing: 0.25 }); // 5 / 2.5 / 2.5
        expect(split.good).toBe(5);
        expect([2, 3]).toContain(split.great);
        expect(split.great + split.amazing).toBe(5);
      }
    }
  });

  it('is right on average for weights that split a card', () => {
    let great = 0;
    for (let seed = 1; seed <= 400; seed++) great += cycle(seed, 'buyer', 0, 0, { good: 0.5, great: 0.25, amazing: 0.25 }).great;
    expect(great / 400).toBeCloseTo(2.5, 0);
  });

  it('shuffles each cycle and each quota differently', () => {
    const order = (q: number, c: number) => Array.from({ length: CONFIG.deckSize }, (_, i) => deckCard(7, 'buyer', q, c * CONFIG.deckSize + i));
    expect(order(0, 0)).not.toEqual(order(0, 1));
    expect(order(0, 0)).not.toEqual(order(1, 0));
    expect(order(0, 0)).toEqual(order(0, 0));
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
          expect(offer(s, id, ag.good).tier).toBe(tierAt(u, tierWeights(data, s, ag.good, a.role)));
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

describe('areas', () => {
  /** Play a run to the end of `day` (without trading), passing every quota on the way. */
  function playTo(seed: number, day: number): RunState {
    const s = newRun(full, seed);
    while (s.day < day) {
      if (s.day === s.quota.dueDay) s.cash = Math.max(s.cash, s.quota.amount);
      endDay(full, s);
    }
    return s;
  }

  it('starts in the bay and moves to the peaks on day 22, with its locations and goods', () => {
    const s = playTo(3, 21);
    expect(s.area).toBe('bay');
    expect(s.locations.every((l) => full.locations[l.id].area === 'bay')).toBe(true);
    s.cash = s.quota.amount;
    expect(endDay(full, s)).toBe('quotaPassed');
    expect(s.day).toBe(22);
    expect(s.area).toBe('peaks');
    expect(s.locations.map((l) => full.locations[l.id].area)).toEqual(['peaks', 'peaks', 'peaks']);
    expect(s.deck).toEqual({ supplier: 0, buyer: 0 });
    for (const key of Object.keys(s.market)) expect(full.goods[key.split(':')[1]].area).toBe('peaks');
  });

  it('buys the bag back at what was paid when moving', () => {
    const s = playTo(5, 21);
    s.cash = s.quota.amount;
    s.inventory = [
      { good: 'hammer', paid: 9, day: 20 },
      { good: 'strawberry', paid: 2, day: 21 },
    ];
    const cash = s.cash;
    endDay(full, s);
    expect(s.inventory).toEqual([]);
    expect(s.cash).toBe(cash + 11);
    expect(s.moved).toEqual({ area: 'peaks', units: 2, refund: 11 });
  });

  it('moves on from the peaks to Lantern Crossing on day 43, buying the bag back', () => {
    const s = playTo(4, 42);
    expect(s.area).toBe('peaks');
    s.cash = s.quota.amount;
    s.inventory = [{ good: 'pickaxe', paid: 18, day: 42 }];
    const cash = s.cash;
    expect(endDay(full, s)).toBe('quotaPassed');
    expect(s.day).toBe(43);
    expect(s.area).toBe('crossing');
    expect(s.cash).toBe(cash + 18);
    expect(s.moved).toEqual({ area: 'crossing', units: 1, refund: 18 });
    expect(s.locations.map((l) => full.locations[l.id].area)).toEqual(['crossing', 'crossing', 'crossing']);
    for (const key of Object.keys(s.market)) expect(full.goods[key.split(':')[1]].area).toBe('crossing');
    expect(weatherOn(full, 'crossing', 43)).toBe('lanterns');
  });

  it('does not move to Lantern Crossing when the day-42 quota is missed', () => {
    const s = playTo(4, 42);
    s.cash = 0;
    s.quota.met = false;
    expect(endDay(full, s)).toBe('failed');
    expect(s.area).toBe('peaks');
  });

  it('does not move when the day-21 quota is missed', () => {
    const s = playTo(5, 21);
    s.cash = 0;
    s.quota.met = false;
    expect(endDay(full, s)).toBe('failed');
    expect(s.area).toBe('bay');
  });

  it('keeps category stamps working in the new area', () => {
    const s = playTo(8, 21);
    s.stars = 20;
    s.dealer = {
      locationId: s.locations[0].id,
      offers: [
        { deal: { kind: 'stock', category: 'food' }, cost: 3, sold: false },
        { deal: { kind: 'luck', category: 'food' }, cost: 3, sold: false },
      ],
    };
    buyDealerDeal(full, s, 0);
    buyDealerDeal(full, s, 1);
    s.cash = s.quota.amount;
    endDay(full, s);
    expect(s.area).toBe('peaks');
    const base = tierWeights(full, s, 'crystal', 'supplier');
    expect(tierWeights(full, s, 'hot_cocoa', 'supplier').great).toBeCloseTo(base.great! + CONFIG.dealer.luckStep);
    // every hot cocoa seller dealt in has the extra stock
    for (const l of s.locations)
      for (const id of l.actorIds)
        if (full.actors[id].role === 'supplier' && s.market[`${id}:hot_cocoa`])
          expect(offer(s, id, 'hot_cocoa').left).toBeGreaterThanOrEqual(CONFIG.stockRange.food[0] + CONFIG.dealer.stockStep.food);
  });

  it('offers category stamps, one per category, in either area', () => {
    const cats = allDeals(full).filter((d) => d.kind === 'stock');
    expect(cats.map((d) => dealKey(d)).sort()).toEqual(['stock:food', 'stock:music', 'stock:tools', 'stock:treasure']);
    const s = playTo(2, 22);
    expect(eligibleDeals(full, s).some((d) => dealKey(d) === 'stock:food')).toBe(true);
  });
});

describe('Fireworks Night (Lantern Crossing, day 57 on)', () => {
  const fireworks = full.areas.crossing.events!.find((e) => e.id === 'fireworks')!;
  const bust = fireworks.bustling!;
  const crossing = areaView(full, 'crossing');

  /** A run in Lantern Crossing, dealt for `day` (no quota due). */
  function crossingDay(seed: number, day: number, d = full, setup?: (s: RunState) => void): RunState {
    const s = newRun(d, seed);
    s.area = 'crossing';
    s.locations = Object.keys(crossing.locations).map((id) => ({ id, actorIds: [] as string[] }));
    s.quota = { ...quotaFor(Math.floor((day - 1) / 7)), dueDay: 9999 };
    s.day = day - 1;
    setup?.(s);
    endDay(d, s);
    return s;
  }
  const withStars = (s: RunState) => {
    s.stats.starsEarned = 5;
    s.dealerSeen = true;
  };

  it('starts on day 57 and lasts to the end of the area, with fireworks over the lantern weather', () => {
    expect(fireworks.fromDay).toBe(57);
    expect(eventOn(full, 'crossing', 56)).toBeNull();
    expect(eventOn(full, 'crossing', 57)?.id).toBe('fireworks');
    expect(eventOn(full, 'crossing', 63)?.id).toBe('fireworks');
    expect(weatherOn(full, 'crossing', 56)).toBe('lanterns');
    expect(weatherOn(full, 'crossing', 57)).toBe('fireworks');
  });

  it('makes exactly one location bustling each day, with 4 actors and no good twice', () => {
    const seen = new Set<string>();
    for (let seed = 0; seed < 30; seed++) {
      const s = crossingDay(seed, 57 + (seed % 7), full, withStars);
      expect(s.bustlingAt).toBeTruthy();
      seen.add(s.bustlingAt!);
      const loc = s.locations.find((l) => l.id === s.bustlingAt)!;
      expect(loc.actorIds).toHaveLength(crossing.locations[loc.id].actorSlots + bust.extraActors);
      const goods = loc.actorIds.map((id) => full.actors[id].goods[0].good);
      expect(new Set(goods).size).toBe(goods.length);
      for (const id of loc.actorIds) expect(s.market[`${id}:${full.actors[id].goods[0].good}`].bustling).toBe(true);
      for (const l of s.locations.filter((x) => x.id !== s.bustlingAt))
        for (const id of l.actorIds) expect(s.market[`${id}:${full.actors[id].goods[0].good}`].bustling).toBeUndefined();
    }
    expect(seen.size).toBe(3);
  });

  it('buyers pay 25% more and sellers charge 25% less there, rounded (sellers at least $1)', () => {
    for (let seed = 0; seed < 20; seed++) {
      const s = crossingDay(seed, 60);
      for (const id of s.locations.find((l) => l.id === s.bustlingAt)!.actorIds) {
        const a = full.actors[id];
        const ag = a.goods[0];
        const o = offer(s, id, ag.good);
        const base = offerPrice(full, s, ag.good, a.role, ag.prices, o.tier, false);
        const want = a.role === 'buyer' ? Math.round(base * (1 + bust.buyBonus)) : Math.max(1, Math.round(base * (1 - bust.sellDiscount)));
        expect(o.price).toBe(want);
      }
    }
    // rounding: $1 stays $1 for sellers, and halves round up
    const s = crossingDay(1, 60);
    expect(bustlePrice(full, s, 'supplier', 1)).toBe(1);
    expect(bustlePrice(full, s, 'supplier', 2)).toBe(2);
    expect(bustlePrice(full, s, 'supplier', 12)).toBe(9);
    expect(bustlePrice(full, s, 'buyer', 10)).toBe(13);
    expect(bustlePrice(full, s, 'buyer', 52)).toBe(65);
  });

  it('never puts the Dealer at the bustling location, and his visits are as likely as without the event', () => {
    const calm = buildData(
      Object.values(full.goods), Object.values(full.actors), Object.values(full.locations), full.dealer, Object.values(full.categories),
      Object.values(full.areas).map((a) => (a.id === 'crossing' ? { ...a, events: [] } : a)),
    );
    let visits = 0;
    for (let seed = 0; seed < 60; seed++) {
      const s = crossingDay(seed, 58, full, withStars);
      const c = crossingDay(seed, 58, calm, withStars);
      expect(c.bustlingAt).toBeNull();
      expect(!!s.dealer).toBe(!!c.dealer);
      if (!s.dealer) continue;
      visits++;
      expect(s.dealer.locationId).not.toBe(s.bustlingAt);
      const loc = s.locations.find((l) => l.id === s.dealer!.locationId)!;
      expect(loc.actorIds).toHaveLength(crossing.locations[loc.id].actorSlots - 1);
    }
    expect(visits).toBeGreaterThan(10);
  });

  it('puts Packed House somewhere else, so both still happen', () => {
    for (let seed = 0; seed < 20; seed++) {
      const s = crossingDay(seed, 59, full, (x) => grantDeal(full, x, { kind: 'packedHouse' }));
      expect(s.packedAt).toBeTruthy();
      expect(s.packedAt).not.toBe(s.bustlingAt);
      const packed = s.locations.find((l) => l.id === s.packedAt)!;
      const slots = crossing.locations[packed.id].actorSlots + 1 - (s.dealer?.locationId === packed.id ? 1 : 0);
      expect(packed.actorIds).toHaveLength(slots);
      expect(s.locations.find((l) => l.id === s.bustlingAt)!.actorIds).toHaveLength(4);
    }
  });

  it('keeps the due-day guarantee', () => {
    for (let seed = 0; seed < 20; seed++) {
      const s = crossingDay(seed, 63, full, (x) => {
        x.inventory = [{ good: 'paper_lantern', paid: 30, day: 62 }];
        x.quota.dueDay = 63;
        x.quota.met = true;
      });
      const buyers = s.locations.flatMap((l) => l.actorIds).filter((id) => full.actors[id].role === 'buyer');
      expect(buyers.some((id) => full.actors[id].goods[0].good === 'paper_lantern')).toBe(true);
    }
  });

  it('changes nothing before day 57', () => {
    for (let seed = 0; seed < 20; seed++) {
      const s = crossingDay(seed, 56, full, withStars);
      expect(s.bustlingAt).toBeNull();
      for (const o of Object.values(s.market)) expect(o.bustling).toBeUndefined();
      for (const l of s.locations)
        expect(l.actorIds).toHaveLength(crossing.locations[l.id].actorSlots - (s.dealer?.locationId === l.id ? 1 : 0));
    }
  });
});

describe('Blizzard (Frostpine Peaks, day 36 on)', () => {
  const peaks = areaView(full, 'peaks');
  const calm = buildData(
    Object.values(full.goods), Object.values(full.actors), Object.values(full.locations), full.dealer, Object.values(full.categories),
    Object.values(full.areas).map((a) => (a.id === 'peaks' ? { ...a, events: [] } : a)),
  );

  /** A run in Frostpine Peaks, dealt for `day` (no quota due). */
  function peaksDay(seed: number, day: number, d = full): RunState {
    const s = newRun(d, seed);
    s.area = 'peaks';
    s.locations = Object.keys(peaks.locations).map((id) => ({ id, actorIds: [] as string[] }));
    s.quota = { ...quotaFor(Math.floor((day - 1) / 7)), dueDay: 9999 };
    s.day = day - 1;
    s.stats.starsEarned = 5;
    s.dealerSeen = true;
    endDay(d, s);
    return s;
  }

  it('runs from day 36 to the end of the area, with blizzard weather', () => {
    expect(eventOn(full, 'peaks', 35)).toBeNull();
    expect(eventOn(full, 'peaks', 36)?.id).toBe('blizzard');
    expect(eventOn(full, 'peaks', 42)?.id).toBe('blizzard');
    expect(weatherOn(full, 'peaks', 35)).toBe('snow');
    expect(weatherOn(full, 'peaks', 36)).toBe('blizzard');
    expect(weatherOn(full, 'crossing', 43)).toBe('lanterns');
  });

  it('snows in one location a day (all of them over time) without changing the deal', () => {
    const seen = new Set<string>();
    for (let seed = 0; seed < 30; seed++) {
      const s = peaksDay(seed, 37);
      const c = peaksDay(seed, 37, calm);
      expect(s.locations.map((l) => l.id)).toContain(s.snowedAt);
      seen.add(s.snowedAt!);
      expect(c.snowedAt).toBeNull();
      expect(s.locations).toEqual(c.locations);
      expect(s.market).toEqual(c.market);
      expect(s.dealer).toEqual(c.dealer);
    }
    expect(seen.size).toBe(3);
  });

  it('snows nothing in before day 36', () => {
    for (let seed = 0; seed < 10; seed++) expect(peaksDay(seed, 35).snowedAt).toBeNull();
  });
});

describe('stamp rarity', () => {
  it('rare and epic odds start in week 2 and grow every week', () => {
    const w2 = rarityOdds(2);
    expect(w2.epic).toBeCloseTo(0.04);
    expect(w2.rare).toBeCloseTo(0.08);
    expect(w2.common).toBeCloseTo(0.88);
    const w4 = rarityOdds(4);
    expect(w4.epic).toBeCloseTo(0.08);
    expect(w4.rare).toBeCloseTo(0.16);
    expect(rarityOdds(1)).toEqual(w2);
    expect(rollRarity(0.03, 2)).toBe('epic');
    expect(rollRarity(0.05, 2)).toBe('rare');
    expect(rollRarity(0.5, 2)).toBe('common');
  });

  it('falls back to lower rarities, then higher ones', () => {
    expect(rarityFallback('epic')).toEqual(['epic', 'rare', 'common']);
    expect(rarityFallback('rare')).toEqual(['rare', 'common', 'epic']);
    expect(rarityFallback('common')).toEqual(['common', 'rare', 'epic']);
  });

  it('makes the old one-offs and every new stamp rare, at 8 stars', () => {
    for (const kind of ['collector', 'dailyDiscount', 'cantGetEnough', 'monocle', 'detour'] as const) {
      expect(rarityOf(kind)).toBe('rare');
      expect(CONFIG.dealer.cost[kind]).toBe(8);
    }
    expect(rarityOf('tip')).toBe('common');
    expect(rarityOf({ kind: 'bag', tier: 1 })).toBe('common');
  });

  it('draws a rare when an epic is rolled but there are none', () => {
    CONFIG.dealer.rarityOdds = { epic: { base: 1, perWeek: 0 }, rare: { base: 0, perWeek: 0 } };
    const s = newRun(data, 3);
    s.stats.starsEarned = 1;
    const visit = rollDealer(data, s)!;
    expect(visit.offers.every((o) => rarityOf(o.deal) === 'rare')).toBe(true);
  });

  it('draws commons when a rare is rolled but every rare is owned', () => {
    CONFIG.dealer.rarityOdds = { epic: { base: 0, perWeek: 0 }, rare: { base: 1, perWeek: 0 } };
    const s = newRun(data, 4);
    s.stats.starsEarned = 1;
    for (const d of allDeals(data)) if (rarityOf(d) === 'rare') grantDeal(data, s, d);
    const visit = rollDealer(data, s)!;
    expect(visit.offers).toHaveLength(CONFIG.dealer.offers + CONFIG.dealer.collectorOffers);
    expect(visit.offers.every((o) => rarityOf(o.deal) === 'common')).toBe(true);
  });
});

describe('rare stamps', () => {
  const seashells = (n: number, day: number) => Array.from({ length: n }, () => ({ good: 'seashell', paid: 1, day }));
  const give = (s: RunState, ...kinds: SingleKind[]) => kinds.forEach((kind) => grantDeal(data, s, { kind }));

  it('Haggler: +50% on the first sale of the day, 25 points less after each, down to $0', () => {
    const s = newRun(data, 1);
    give(s, 'haggler');
    const buyer = withActor(s, 'buyer', 'seashell');
    offer(s, buyer, 'seashell').price = 4;
    s.inventory = seashells(8, s.day);
    const got: number[] = [];
    for (let i = 0; i < 8; i++) {
      const cash = s.cash;
      sell(data, s, buyer, 'seashell', 1);
      got.push(s.cash - cash);
    }
    expect(got).toEqual([6, 5, 4, 3, 2, 1, 0, 0]);
    expect(hagglerMultiplier(s)).toBe(0);
    s.quota.dueDay = 9999;
    endDay(data, s);
    expect(hagglerMultiplier(s)).toBe(1.5);
  });

  it('Cramazing: doubles how far an Amazing price is from the Good one (sellers never below $1)', () => {
    const s = newRun(data, 1);
    const prices = { bad: 8, good: 10, great: 12, amazing: 13 };
    expect(dealPrice(s, prices, 'amazing')).toBe(13);
    give(s, 'cramazing');
    expect(dealPrice(s, prices, 'amazing')).toBe(16);
    expect(dealPrice(s, prices, 'great')).toBe(12);
    expect(dealPrice(s, { good: 10, great: 9, amazing: 7 }, 'amazing')).toBe(4);
    expect(dealPrice(s, { good: 3, great: 2, amazing: 1 }, 'amazing')).toBe(1);
  });

  it('Monocle: every buy and sell price is 25% higher (rounded)', () => {
    const s = newRun(data, 1);
    give(s, 'monocle');
    expect(buyPrice(s, { tier: 'good', price: 4, left: 1 })).toBe(5);
    expect(buyPrice(s, { tier: 'good', price: 10, left: 1 })).toBe(13);
    expect(nextSellPrice(s, { tier: 'good', price: 4, left: 1 }, 'seashell')).toBe(5);
  });

  it('Vintage and Flipper add to the sell price per unit', () => {
    const s = newRun(data, 1);
    s.day = 5;
    const o = { tier: 'good' as const, price: 10, left: 1 };
    give(s, 'vintage');
    expect(sellPrice(s, o, { good: 'hammer', paid: 1, day: 2 })).toBe(13);
    expect(sellPrice(s, o, { good: 'hammer', paid: 1, day: 5 })).toBe(10);
    give(s, 'flipper');
    expect(sellPrice(s, o, { good: 'hammer', paid: 1, day: 4 })).toBe(14); // +10% vintage, +25% flipper
  });

  it('Fuzzy Dice: a sale can turn the buyer Amazing for the rest of the day', () => {
    const chance = CONFIG.dealer.fuzzyDiceChance;
    CONFIG.dealer.fuzzyDiceChance = 1;
    try {
      const s = newRun(data, 1);
      give(s, 'fuzzyDice');
      const buyer = withActor(s, 'buyer', 'seashell');
      const o = offer(s, buyer, 'seashell');
      const prices = data.actors[buyer].goods[0].prices;
      o.tier = 'good';
      o.price = prices.good;
      s.inventory = seashells(2, s.day);
      const sale = sellUnits(data, s, buyer, 'seashell', 1);
      expect(sale.lucky).toBe(true);
      expect(o.tier).toBe('amazing');
      expect(o.price).toBe(prices.amazing);
      expect(sellUnits(data, s, buyer, 'seashell', 1).lucky).toBe(false); // already Amazing
    } finally {
      CONFIG.dealer.fuzzyDiceChance = chance;
    }
  });

  it("Camp Fire: the day's first unit comes with a free copy, if there's room", () => {
    const s = newRun(data, 1);
    give(s, 'campFire');
    const seller = withActor(s, 'supplier', 'strawberry');
    const o = offer(s, seller, 'strawberry');
    o.left = 5;
    const cash = s.cash;
    expect(buyUnits(data, s, seller, 'strawberry', 1)).toEqual({ n: 1, free: 1 });
    expect(s.inventory.map((it) => it.paid)).toEqual([o.price, o.price]);
    expect(s.cash).toBe(cash - o.price);
    expect(o.left).toBe(4);
    expect(buyUnits(data, s, seller, 'strawberry', 1)).toEqual({ n: 1, free: 0 });
    // shift-click never overfills the bag
    const t = newRun(data, 1);
    give(t, 'campFire');
    const ts = withActor(t, 'supplier', 'strawberry');
    offer(t, ts, 'strawberry').left = 9;
    t.cash = 99;
    buyUnits(data, t, ts, 'strawberry', maxBuy(t, ts, 'strawberry'));
    expect(t.inventory).toHaveLength(t.capacity);
  });

  it('Mixed Bag tips once per good a day, and Big Tipper triples every tip', () => {
    const s = newRun(data, 1);
    give(s, 'mixedBag');
    const shell = withActor(s, 'buyer', 'seashell');
    offer(s, shell, 'seashell').price = 4;
    s.inventory = seashells(3, s.day);
    expect(sellUnits(data, s, shell, 'seashell', 1).tips).toBe(CONFIG.dealer.mixedBagTip);
    expect(sellUnits(data, s, shell, 'seashell', 1).tips).toBe(0);
    give(s, 'bigTipper', 'tip');
    s.quota.dueDay = 9999;
    endDay(data, s);
    const b = withActor(s, 'buyer', 'seashell');
    s.inventory = seashells(2, s.day);
    const sale = sellUnits(data, s, b, 'seashell', 2);
    expect(sale.tips).toBe(CONFIG.dealer.bigTipper * (CONFIG.dealer.mixedBagTip + CONFIG.dealer.tip));
  });

  it('end-of-day payouts: Fanny Pack, Sleeping Bag and Clean Sweep', () => {
    const s = newRun(data, 1);
    give(s, 'fannyPack', 'sleepingBag', 'cleanSweep');
    expect(endOfDayPayouts(s)).toEqual({ fannyPack: 0, sleepingBag: 0, cleanSweep: s.capacity });
    s.inventory = [
      { good: 'seashell', paid: 10, day: 1 },
      { good: 'seashell', paid: 10, day: 1 },
      { good: 'hammer', paid: 10, day: 1 },
    ];
    expect(endOfDayPayouts(s)).toEqual({ fannyPack: 2, sleepingBag: 2, cleanSweep: 0 });
    s.boughtToday = true;
    expect(endOfDayPayouts(s).sleepingBag).toBe(0);
  });

  it('end-of-day payouts count toward the quota', () => {
    const s = newRun(data, 1);
    give(s, 'fannyPack');
    while (s.day < s.quota.dueDay) endDay(data, s);
    s.inventory = [{ good: 'hammer', paid: 1, day: s.day }];
    s.cash = s.quota.amount - 1;
    expect(buyoutOffer(data, s)).toBeNull(); // no need: the payout covers it
    expect(endDay(data, s)).toBe('quotaPassed');
  });

  it('Last Call: the buyout pays the lowest Amazing price (with Cramazing)', () => {
    const s = newRun(data, 1);
    expect(buyoutPrice(data, 'hammer', s)).toBe(8);
    give(s, 'lastCall');
    expect(buyoutPrice(data, 'hammer', s)).toBe(13);
    give(s, 'cramazing');
    expect(buyoutPrice(data, 'hammer', s)).toBe(16);
  });

  it('Packed House: one location has an extra actor, with no good twice', () => {
    for (let seed = 0; seed < 20; seed++) {
      const s = newRun(data, seed);
      give(s, 'packedHouse');
      s.quota.dueDay = 9999;
      endDay(data, s);
      const packed = s.locations.find((l) => l.id === s.packedAt)!;
      const slots = data.locations[packed.id].actorSlots + 1 - (s.dealer?.locationId === packed.id ? 1 : 0);
      expect(packed.actorIds).toHaveLength(slots);
      const goods = packed.actorIds.map((id) => data.actors[id].goods[0].good);
      expect(new Set(goods).size).toBe(goods.length);
    }
  });

  it('Perfect Planner and Dump Truck: a buyer for the priciest and the most common bag good', () => {
    const buyerOf = (s: RunState, good: string) =>
      s.locations.some((l) => l.actorIds.some((id) => data.actors[id].role === 'buyer' && data.actors[id].goods[0].good === good));
    for (let seed = 0; seed < 20; seed++) {
      const s = newRun(data, seed);
      give(s, 'perfectPlanner', 'dumpTruck');
      s.quota.dueDay = 9999;
      for (let d = 0; d < 5; d++) {
        s.inventory = [...seashells(3, s.day), { good: 'hammer', paid: 1, day: s.day }];
        endDay(data, s);
        expect(buyerOf(s, 'hammer')).toBe(true);
        expect(buyerOf(s, 'seashell')).toBe(true);
      }
    }
  });

  it('Detour: a second location, only before trading and only once a day', () => {
    const s = newRun(data, 1);
    give(s, 'detour');
    const [a, b] = s.locations.map((l) => l.id);
    visit(data, s, a);
    expect(canDetour(s)).toBe(true);
    detour(s);
    expect(s.visited).toBeNull();
    visit(data, s, a);
    expect(s.visited).toBeNull(); // can't go back
    visit(data, s, b);
    expect(s.visited).toBe(b);
    expect(canDetour(s)).toBe(false);
    s.quota.dueDay = 9999;
    endDay(data, s);
    visit(data, s, s.locations[0].id);
    s.boughtToday = true;
    expect(canDetour(s)).toBe(false);
  });
});

describe('weekly bad day', () => {
  const bag = (goods: string[], day: number) => goods.map((good) => ({ good, paid: 1, day }));
  const planned = (seed: number, week: number) => rngFor(seed, 'badDay', week).int(7 * week + 1, 7 * week + 6);
  /** Play days 1..last ending each day with `fill(day)` in the bag; returns each day's bad good. */
  const play = (seed: number, last: number, fill: (day: number) => string[], before?: (s: RunState) => void) => {
    const s = newRun(data, seed);
    before?.(s);
    const bad: Record<number, string | null> = { 1: s.badGood ?? null };
    while (s.day < last) {
      s.quota.dueDay = 9999; // keep the run alive
      s.inventory = bag(fill(s.day + 1), s.day);
      endDay(data, s);
      bad[s.day] = s.badGood ?? null;
      // every dealt buyer of the bad good is bad at its bad price, and nothing else is
      for (const l of s.locations)
        for (const id of l.actorIds)
          for (const ag of areaView(full, s.area).actors[id].goods) {
            const o = offer(s, id, ag.good);
            const isBad = full.actors[id].role === 'buyer' && ag.good === s.badGood;
            expect(o.tier === 'bad').toBe(isBad);
            if (isBad) expect(o.price).toBe(ag.prices.bad);
          }
    }
    return bad;
  };

  it('comes once a week on its pre-rolled day (or the first day with goods), never on the last', () => {
    for (let seed = 1; seed <= 60; seed++) {
      const bad = play(seed, 14, () => ['hammer', 'seashell']);
      for (const week of [0, 1]) {
        const days = Object.keys(bad).map(Number).filter((d) => d > 7 * week && d <= 7 * week + 7 && bad[d]);
        // day 1 always starts with an empty bag
        expect(days).toEqual([Math.max(planned(seed, week), 2)]);
        expect(['hammer', 'seashell']).toContain(bad[days[0]]);
      }
    }
  });

  it('ignores the luck stamps', () => {
    for (let seed = 1; seed <= 20; seed++) {
      const bad = play(seed, 14, () => ['strawberry'], (s) => {
        s.perks.luckAll = CONFIG.dealer.ranks.luckAll * CONFIG.dealer.luckAll;
        for (const c of Object.keys(full.categories)) s.perks.luck[c] = CONFIG.dealer.luckStep;
      });
      expect(bad[Math.max(planned(seed, 1), 8)]).toBe('strawberry');
    }
  });

  it('moves to the next day while the bag is empty, but not into the next week or its last day', () => {
    for (let seed = 1; seed <= 60; seed++) {
      const from = 8 + (seed % 7); // the bag has goods from this morning on
      const bad = play(seed, 14, (day) => (day >= from ? ['old_record'] : []));
      const want = Math.max(planned(seed, 1), from);
      const days = Object.keys(bad).map(Number).filter((d) => d >= 8 && bad[d]);
      expect(days).toEqual(want <= 13 ? [want] : []);
    }
  });

  it('never comes during an area event', () => {
    for (let seed = 1; seed <= 20; seed++) {
      const bad = play(seed, 21, () => ['hammer']);
      for (let d = 15; d <= 21; d++) expect(bad[d]).toBeNull();
    }
    const s = newRun(data, 3);
    s.inventory = bag(['hammer'], 1);
    for (const day of [15, 16, 20]) {
      s.day = day;
      delete s.badWeek;
      expect(rollBadDay(data, s)).toBeNull();
    }
  });

  it("doesn't use up tier deck cards", () => {
    let checked = 0;
    for (let seed = 1; seed <= 40 && checked < 5; seed++) {
      const s = newRun(data, seed);
      while (s.day < 13 && !s.badGood) {
        s.quota.dueDay = 9999;
        s.inventory = bag(['hammer', 'seashell', 'strawberry', 'old_record'], s.day);
        endDay(data, s);
      }
      if (!s.badGood) continue;
      for (const l of s.locations) {
        const buyers = l.actorIds
          .filter((id) => data.actors[id].role === 'buyer')
          .flatMap((id) => data.actors[id].goods)
          .filter((g) => g.good !== s.badGood).length;
        expect(deckCards(data, s, l.id).buyer).toBe(buyers);
        if (buyers < l.actorIds.filter((id) => data.actors[id].role === 'buyer').length) checked++;
      }
    }
    expect(checked).toBeGreaterThan(0);
  });
});
