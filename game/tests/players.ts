/**
 * Simulated players shared by the balance sims. Each day a player picks a location,
 * buys the Dealer's deals it wants (if he's there), sells what it can, then restocks
 * greedily by expected margin. Price estimates include the run's Dealer perks
 * (discounts, better buyer odds), so players favour goods they have a bonus for.
 *
 * A Profile is a strategy a real player might try: which location to pick, which
 * Dealer deals to buy (and in what order), and which goods to favour.
 */
import { areaView } from '../src/game/area';
import { buyDealerDeal, dealCost, dealFromKey, dealGood, isUniversal, owns } from '../src/game/dealer';
import { CONFIG } from '../src/game/config';
import { eventOn } from '../src/game/events';
import { dealPrice, sellerPrice, tierWeights } from '../src/game/economy';
import { actorsAt, buy, buyPrice, countOf, freeSlots, fullBuyPrice, maxBuy, maxSell, nextSellPrice, offer, sell, visit } from '../src/game/run';
import { type DealerDeal, type RunState, type SingleKind, TIERS } from '../src/game/types';
import { loadTestData } from './helpers';

export const data = loadTestData();

/** Deals bought so far, by kind (a sim can reset and read this). */
export const SIM = {
  bought: Object.fromEntries(Object.keys(CONFIG.dealer.cost).map((k) => [k, 0])) as Record<DealerDeal['kind'], number>,
};

export const clone = (s: RunState): RunState => JSON.parse(JSON.stringify(s));

/** Tier-weighted average price for an actor's good, after this run's perks: sellers
 *  apply the good's discount, both use the luck-boosted tier weights and Cramazing's Amazing
 *  prices, and the Monocle raises both. */
export function expectedPrice(s: RunState, actorId: string, good: string): number {
  const a = data.actors[actorId];
  const ag = a.goods.find((g) => g.good === good)!;
  const seller = a.role === 'supplier';
  const w = tierWeights(data, s, good, a.role);
  const monocle = owns(s, { kind: 'monocle' }) ? 1 + CONFIG.dealer.monocle : 1;
  return monocle * TIERS.filter((t) => w[t]).reduce((sum, t) => {
    const p = dealPrice(s, ag.prices, t);
    return sum + w[t]! * (seller ? sellerPrice(data, s, good, p) : p);
  }, 0);
}

/** Expected resale price for a good. Actors are re-dealt daily, so average over every buyer of it. */
export function resale(s: RunState, good: string): number {
  const buyers = Object.keys(data.actors).filter(
    (id) => data.actors[id].role === 'buyer' && data.actors[id].goods.some((g) => g.good === good),
  );
  return buyers.reduce((sum, id) => sum + expectedPrice(s, id, good), 0) / buyers.length;
}

/** Expected profit per unit of a good (average resale minus average seller price). */
function margin(s: RunState, good: string): number {
  const sellers = Object.keys(data.actors).filter(
    (id) => data.actors[id].role === 'supplier' && data.actors[id].goods.some((g) => g.good === good),
  );
  return resale(s, good) - sellers.reduce((sum, id) => sum + expectedPrice(s, id, good), 0) / sellers.length;
}

// ---------------------------------------------------------------- profiles ----

export type Policy = (s: RunState, rng: () => number) => string;
type Bias = (s: RunState, good: string) => number;

export interface Profile {
  name: string;
  about: string;
  pick: Policy;
  /** Priority of buying a Dealer deal (higher first); null = never buy it. */
  dealRank: (s: RunState, deal: DealerDeal) => number | null;
  /** Multiplier on how much a good is wanted when choosing what to buy and where to go. */
  bias?: Bias;
  /** Never sell a unit for less than was paid for it, except on an unmet quota's due day. */
  noLoss?: boolean;
  /** The stamp this profile is built around: the sims swap it into Nox's first offers until it's
   *  bought (see forceStamp). */
  force?: SingleKind;
  /** Extra cash from selling `n` units of a good to one buyer in one go (on top of the price),
   *  which the profile's buying and route choices try to set up. */
  stackValue?: (n: number) => number;
  /** Once stacking (see stackValue), hold a good until this many units can go to one buyer (see
   *  wouldSell). */
  holdStacks?: number;
  /** Buys the same way when buyers are capped (the Rainstorm); every other profile then buys fewer,
   *  pricier units (see tradeAt). */
  ignoresRain?: boolean;
  /** Spend the day's first buy (half price with the Daily Discount) on the unit that saves most. */
  discountFirst?: boolean;
}

const noBias: Bias = () => 1;

/** Expected value of visiting `loc` with the current bag (what a thoughtful player estimates). */
export function score(s: RunState, loc: string, bias: Bias = noBias): number {
  const { actors } = areaView(data, s.area);
  let v = 0;
  const bag = s.inventory.map((it) => it.good);
  for (const a of actorsAt(s, loc)) {
    const def = actors[a];
    if (def.role !== 'buyer') continue;
    for (const g of def.goods) {
      const n = bag.filter((x) => x === g.good).length;
      v += n * expectedPrice(s, a, g.good);
      for (let i = 0; i < n; i++) bag.splice(bag.indexOf(g.good), 1);
    }
  }
  // small bonus for being able to restock with something profitable
  for (const a of actorsAt(s, loc))
    if (actors[a].role === 'supplier')
      for (const g of actors[a].goods)
        v += 0.5 * bias(s, g.good) * (resale(s, g.good) - expectedPrice(s, a, g.good));
  return v;
}

/** The location worth the most. A snowed-in one (Blizzard) can't be seen from the map, so it's
 *  valued at the average of the others. */
const best = (s: RunState, value: (loc: string) => number) => {
  const ids = s.locations.map((l) => l.id);
  const seen = ids.filter((l) => l !== s.snowedAt);
  const known = new Map(seen.map((l) => [l, value(l)]));
  const guess = seen.length > 0 ? [...known.values()].reduce((a, b) => a + b, 0) / seen.length : 0;
  const v = (l: string) => known.get(l) ?? guess;
  return ids.reduce((b, l) => (v(l) > v(b) ? l : b));
};

export const sensible: Policy = (s) => best(s, (l) => score(s, l));
export const random: Policy = (s, rng) => s.locations[Math.floor(rng() * s.locations.length)].id;

/** The good a Specialist has committed to: the area's good of the category it owns the most deals for. */
export function focusGood(s: RunState): string | null {
  const counts = new Map<string, number>();
  for (const key of s.perks.owned) {
    const good = dealGood(data, dealFromKey(key), s.area);
    if (good) counts.set(good, (counts.get(good) ?? 0) + 1);
  }
  let top: string | null = null;
  for (const [good, n] of counts) if (top === null || n > counts.get(top)!) top = good;
  return top;
}

/** Sims: set RAIN=0 to have every profile ignore the Rainstorm's cap when buying. */
const RAIN_AWARE = process.env.RAIN !== '0';

/** The three stamps a focus profile picks one of. */
const FOCUS_STAMPS: SingleKind[] = ['dailyDiscount', 'tip', 'cantGetEnough'];

/** Sims: while the profile's forced stamp isn't owned, it's the first of Nox's offers whenever he
 *  visits (in place of whatever was there; a duplicate is dropped). */
export function forceStamp(s: RunState, profile: Profile): void {
  const kind = profile.force;
  if (!kind || !s.dealer || owns(s, { kind })) return;
  const deal: DealerDeal = { kind };
  const offers = s.dealer.offers.filter((o) => o.deal.kind !== kind);
  s.dealer.offers = [{ deal, cost: dealCost(deal), sold: false }, ...offers].slice(0, s.dealer.offers.length);
}

/** The good a stacking profile is building up: the one it holds most of. */
function stackGood(s: RunState): string | null {
  let top: string | null = null;
  for (const it of s.inventory) if (top === null || countOf(s, it.good) > countOf(s, top)) top = it.good;
  return top;
}

/** Whether a profile sells `n` units of a good to a buyer now, rather than holding them for a
 *  bigger stack: always, unless it holds stacks (holdStacks, once its stamp is owned). Then it sells
 *  once the stack is big enough, when the bag is full, when the quota is due within a day and not
 *  yet met, when it's short of cash to keep buying, or when the buyer is capped (the Rainstorm). */
function wouldSell(s: RunState, profile: Profile, good: string, n: number, capped = false): boolean {
  const hold = profile.holdStacks;
  if (!hold || !stacking(s, profile) || n >= hold || freeSlots(s) === 0 || capped) return true;
  if (!s.quota.met && s.day >= s.quota.dueDay - 1) return true;
  const paid = s.inventory.find((it) => it.good === good)?.paid ?? 0;
  return s.cash < paid;
}

/** Whether a profile's stackValue applies yet (once it owns its stamp). */
function stacking(s: RunState, profile: Profile): boolean {
  return !!profile.stackValue && (!profile.force || owns(s, { kind: profile.force }));
}

/** Expected value of `loc` for a focus profile: the usual score, the stamp's extra cash from
 *  selling what's held there, the Daily Discount's best saving, and the Dealer (always while its
 *  stamp is unowned, otherwise with 3+ stars, like the Dealer chaser). */
function focusScore(s: RunState, loc: string, profile: Profile): number {
  const { actors } = areaView(data, s.area);
  let v = score(s, loc);
  let saving = 0;
  for (const a of actorsAt(s, loc)) {
    const def = actors[a];
    for (const g of def.goods) {
      if (def.role === 'buyer' && stacking(s, profile)) {
        const n = countOf(s, g.good);
        // a buyer it would hold back from is worth nothing today
        if (wouldSell(s, profile, g.good, n, offer(s, a, g.good).capped)) v += profile.stackValue!(n);
        else v -= n * expectedPrice(s, a, g.good);
      }
      if (def.role === 'supplier' && profile.discountFirst && owns(s, { kind: 'dailyDiscount' })) {
        const o = offer(s, a, g.good);
        if (resale(s, g.good) > buyPrice(s, o)) saving = Math.max(saving, fullBuyPrice(s, o) - buyPrice(s, o));
      }
    }
  }
  v += saving;
  const wanted = profile.force && !owns(s, { kind: profile.force }) ? 100 : s.stars >= 3 ? 10 : 0;
  return v + (s.dealer?.locationId === loc ? wanted : 0);
}

/** A profile built around one of the new stamps: it's forced into Nox's first visit and bought,
 *  the other two are never bought, and other deals are bought like the Dealer chaser. */
function focus(kind: SingleKind, name: string, about: string, extra: Partial<Profile>): Profile {
  const profile: Profile = {
    name,
    about,
    pick: (s) => best(s, (l) => focusScore(s, l, profile)),
    dealRank: (_, d) => (d.kind === kind ? 100 : FOCUS_STAMPS.includes(d.kind as SingleKind) ? null : DEAL_VALUE[d.kind]),
    force: kind,
    ...extra,
  };
  return profile;
}

/** Rough value of each deal kind for a player who wants them all (bag slots scale best). */
const DEAL_VALUE: Record<DealerDeal['kind'], number> = {
  bag: 5, luckAll: 4, discountAll: 4, stockAll: 3, buyerStockAll: 3, discount: 2, luck: 1.5, stock: 1,
  buyerStock: 1, dailyDiscount: 3, tip: 3, cantGetEnough: 3, collector: 2,
  // the rares (the sims don't use Bird's Eye's or Detour's information, so they're worth little)
  monocle: 3, campFire: 3, mixedBag: 2.5, cramazing: 2, haggler: 2, fannyPack: 2, packedHouse: 2,
  bigTipper: 2, fuzzyDice: 2, flipper: 2, perfectPlanner: 2, dumpTruck: 2, vintage: 1.5, lastCall: 1,
  cleanSweep: 1, birdsEye: 0.5, sleepingBag: 0.5, detour: 0.5,
};

export const PROFILES: Record<string, Profile> = {
  frugal: {
    name: 'Frugal',
    about: 'Plays the market well, ignores the Dealer entirely.',
    pick: sensible,
    dealRank: () => null,
  },
  impulse: {
    name: 'Impulse',
    about: 'Buys every affordable deal, bag upgrades first, then in the order shown.',
    pick: sensible,
    dealRank: (_, d) => (d.kind === 'bag' ? 1 : 0),
  },
  packrat: {
    name: 'Packrat',
    about: 'Only wants bag upgrades, then all-goods deals; saves stars for them.',
    pick: sensible,
    dealRank: (_, d) => (d.kind === 'bag' ? 2 : isUniversal(d) ? 1 : null),
  },
  specialist: {
    name: 'Specialist',
    about:
      'Commits to one good: buys bags, its per-good deals and all-goods deals, trades it harder, and visits the Dealer when it can also trade that good there.',
    pick: (s) =>
      best(s, (l) => {
        const focus = focusGood(s);
        const here = actorsAt(s, l).map((a) => data.actors[a]);
        const trades = (role: string, good: string) => here.some((a) => a.role === role && a.goods.some((g) => g.good === good));
        const holding = (good: string) => s.inventory.some((it) => it.good === good);
        // go where the focus good can be restocked (filling the free slots), on top of the usual score
        const restock = focus !== null && trades('supplier', focus);
        const room = s.capacity - s.inventory.length;
        // the Dealer is worth the trip if there's also something to trade there: the focus good
        // (buying it, or selling what's held), or before committing, a buyer for anything in the bag
        const wanted =
          focus !== null
            ? restock || (holding(focus) && trades('buyer', focus))
            : s.inventory.some((it) => trades('buyer', it.good));
        const dealer = s.dealer?.locationId === l && s.stars >= 3 && wanted ? 10 : 0;
        return score(s, l, PROFILES.specialist.bias) + (restock ? room * Math.max(0, margin(s, focus!)) : 0) + dealer;
      }),
    dealRank: (s, d) => {
      if (d.kind === 'bag') return 10; // more slots help every strategy
      const good = dealGood(data, d, s.area);
      const focus = focusGood(s);
      if (good) return focus === null || good === focus ? 3 + margin(s, good) / 10 : null;
      return isUniversal(d) ? 2 : null;
    },
    // strong enough that the focus good is bought first whenever it turns a profit
    bias: (s, good) => (good === focusGood(s) ? 3 : 1),
  },
  patient: {
    name: 'Patient',
    about: 'Like Impulse, but never sells a unit below what it paid (unless the quota is due today).',
    pick: sensible,
    dealRank: (_, d) => (d.kind === 'bag' ? 1 : 0),
    noLoss: true,
  },
  discountFocus: focus('dailyDiscount', 'Discount focus',
    'Built around Daily Discount: spends the half-price first buy on the unit that saves most.',
    { discountFirst: true }),
  tipFocus: focus('tip', 'Tip focus',
    'Built around Tip Jar: buys goods in pairs and heads for buyers it can sell 2 to.',
    { stackValue: (n) => (n >= CONFIG.dealer.tipAfter ? CONFIG.dealer.tip : 0) }),
  moreFocus: focus('cantGetEnough', 'CGE focus',
    "Built around Can't Get Enough: stacks one good and sells the whole stack to one buyer.",
    {
      stackValue: (n) => (CONFIG.dealer.cantGetEnoughStep * n * (n - 1)) / 2,
      // holding back small stacks (HOLD=3 in the sim) loses: stacks are limited by seller stock and
      // bag size, not by selling early, so holding only delays cash (day 35: 55% off, 48% at 3, 41% at 4)
      holdStacks: Number(process.env.HOLD ?? 0),
      // restock the good it's stacking first
      bias: (s, good) => (owns(s, { kind: 'cantGetEnough' }) && good === stackGood(s) ? 3 : 1),
      // bigger stacks need more stock to buy: the stock stamps come right after bag upgrades
      dealRank: (_, d) =>
        d.kind === 'cantGetEnough' ? 100 : FOCUS_STAMPS.includes(d.kind as SingleKind) ? null
          : d.kind === 'stock' || d.kind === 'stockAll' ? 4.5 : DEAL_VALUE[d.kind],
    }),
  chaser: {
    name: 'Dealer chaser',
    about: 'Heads to the Dealer whenever it has 3+ stars, buys the best-value deals first.',
    pick: (s) =>
      best(s, (l) => score(s, l) + (s.dealer?.locationId === l && s.stars >= 3 ? 10 : 0)),
    dealRank: (_, d) => DEAL_VALUE[d.kind],
  },
};

// ------------------------------------------------------------------ trading ----

/** How many units of a good can be sold at `price` without a loss. Sales take the oldest unit
 *  first, so stop at the first one that was bought for more. */
function lossFree(s: RunState, good: string, price: number): number {
  const units = s.inventory.filter((it) => it.good === good);
  const n = units.findIndex((it) => it.paid > price);
  return n === -1 ? units.length : n;
}

export function tradeAt(s: RunState, loc: string, profile: Profile = PROFILES.impulse): void {
  visit(data, s, loc);
  // buy the most wanted affordable deal, re-ranking after each purchase (a deal can change what's wanted)
  for (const dealer = s.dealer; dealer?.locationId === loc; ) {
    const next = dealer.offers
      .map((o, i) => ({ o, i, rank: profile.dealRank(s, o.deal) }))
      .filter((w) => w.rank !== null && !w.o.sold && w.o.cost <= s.stars)
      .sort((x, y) => y.rank! - x.rank!)[0];
    if (!next || !buyDealerDeal(data, s, next.i)) break;
    SIM.bought[next.o.deal.kind]++;
  }
  const actors = actorsAt(s, loc);
  const defs = areaView(data, s.area).actors;
  // sell: highest-paying buyer first
  const sales = actors
    .filter((a) => defs[a].role === 'buyer')
    .flatMap((a) => defs[a].goods.map((g) => ({ a, good: g.good, price: nextSellPrice(s, offer(s, a, g.good), g.good) })))
    .sort((x, y) => y.price - x.price);
  const desperate = !s.quota.met && s.day >= s.quota.dueDay;
  for (const t of sales) {
    if (!wouldSell(s, profile, t.good, maxSell(s, t.a, t.good), offer(s, t.a, t.good).capped)) continue;
    sell(data, s, t.a, t.good, profile.noLoss && !desperate ? lossFree(s, t.good, t.price) : maxSell(s, t.a, t.good));
  }
  if (s.day >= s.quota.dueDay) return;
  const sellers = actors.filter((a) => defs[a].role === 'supplier').flatMap((a) => defs[a].goods.map((g) => ({ a, good: g.good })));
  // the Daily Discount: the first unit goes to whatever saves the most (and still turns a profit)
  if (profile.discountFirst && owns(s, { kind: 'dailyDiscount' }) && !s.boughtToday) {
    const first = sellers
      .filter((t) => maxBuy(s, t.a, t.good) > 0 && resale(s, t.good) > buyPrice(s, offer(s, t.a, t.good)))
      .sort((x, y) => fullBuyPrice(s, offer(s, y.a, y.good)) - fullBuyPrice(s, offer(s, x.a, x.good)))[0];
    if (first) buy(data, s, first.a, first.good, 1);
  }
  // when buyers will be capped from tomorrow (the Rainstorm), a buyer takes only `limit` a day, so
  // buy fewer, pricier units: rank by profit per unit instead of per dollar, and hold at most
  // `limit` of any good
  const limit = profile.ignoresRain || !RAIN_AWARE ? undefined : eventOn(data, s.area, s.day + 1)?.buyerLimit;
  // buy: best expected margin first (scaled by the profile's bias, plus any stack value the
  // profile's stamp adds for holding more of the same good)
  const bias = profile.bias ?? noBias;
  const stack = stacking(s, profile) ? profile.stackValue : undefined;
  const room = (good: string) => (limit === undefined ? 99 : Math.max(0, limit - countOf(s, good)));
  const buys = sellers
    .map(({ a, good }) => {
      const p = fullBuyPrice(s, offer(s, a, good));
      const held = countOf(s, good);
      const k = Math.max(1, Math.min(maxBuy(s, a, good), freeSlots(s), room(good)));
      const extra = stack ? (stack(held + k) - stack(held)) / k : 0;
      const r = resale(s, good) + extra;
      return { a, good, margin: r - p, ratio: (bias(s, good) * r) / p, value: bias(s, good) * (r - p) };
    })
    .filter((t) => t.margin > 0)
    .sort((x, y) => (limit === undefined ? y.ratio - x.ratio : y.value - x.value));
  for (const t of buys) buy(data, s, t.a, t.good, room(t.good));
}
