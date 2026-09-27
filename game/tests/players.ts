/**
 * Simulated players shared by the balance sims. Each day a player picks a location,
 * buys the Dealer's deals it wants (if he's there), sells what it can, then restocks
 * greedily by expected margin. Price estimates include the run's Dealer perks
 * (discounts, better buyer odds), so players favour goods they have a bonus for.
 *
 * A Profile is a strategy a real player might try: which location to pick, which
 * Dealer deals to buy (and in what order), and which goods to favour.
 */
import { CONFIG } from '../src/game/config';
import { buyDealerDeal, dealFromKey, dealGood, isUniversal } from '../src/game/dealer';
import { buyerWeights, sellerPrice } from '../src/game/economy';
import { actorsAt, buy, maxSell, offer, sell, visit } from '../src/game/run';
import { type DealerDeal, type RunState, TIERS } from '../src/game/types';
import { loadTestData } from './helpers';

export const data = loadTestData();

/** Deals bought so far, by kind (a sim can reset and read this). */
export const SIM = {
  bought: {
    bag: 0, discount: 0, sellChance: 0, stock: 0, buyerStock: 0,
    discountAll: 0, stockAll: 0, buyerStockAll: 0, sellChanceAll: 0,
  } as Record<
    DealerDeal['kind'],
    number
  >,
};

export const clone = (s: RunState): RunState => JSON.parse(JSON.stringify(s));

/** Tier-weighted average price for an actor's good, after this run's perks: sellers
 *  apply the good's discount, buyers use the sellChance-boosted tier weights. */
export function expectedPrice(s: RunState, actorId: string, good: string): number {
  const a = data.actors[actorId];
  const ag = a.goods.find((g) => g.good === good)!;
  const seller = a.role === 'supplier';
  const w = seller ? CONFIG.dealWeights : buyerWeights(s, good);
  return TIERS.reduce((sum, t) => sum + w[t] * (seller ? sellerPrice(s, good, ag.prices[t]) : ag.prices[t]), 0);
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
}

const noBias: Bias = () => 1;

/** Expected value of visiting `loc` with the current bag (what a thoughtful player estimates). */
export function score(s: RunState, loc: string, bias: Bias = noBias): number {
  let v = 0;
  const bag = s.inventory.map((it) => it.good);
  for (const a of actorsAt(s, loc)) {
    const def = data.actors[a];
    if (def.role !== 'buyer') continue;
    for (const g of def.goods) {
      const n = bag.filter((x) => x === g.good).length;
      v += n * expectedPrice(s, a, g.good);
      for (let i = 0; i < n; i++) bag.splice(bag.indexOf(g.good), 1);
    }
  }
  // small bonus for being able to restock with something profitable
  for (const a of actorsAt(s, loc))
    if (data.actors[a].role === 'supplier')
      for (const g of data.actors[a].goods)
        v += 0.5 * bias(s, g.good) * (resale(s, g.good) - expectedPrice(s, a, g.good));
  return v;
}

const best = (s: RunState, value: (loc: string) => number) =>
  s.locations.map((l) => l.id).reduce((b, l) => (value(l) > value(b) ? l : b));

export const sensible: Policy = (s) => best(s, (l) => score(s, l));
export const random: Policy = (s, rng) => s.locations[Math.floor(rng() * s.locations.length)].id;

/** The good a Specialist has committed to: the one it owns the most per-good deals for. */
export function focusGood(s: RunState): string | null {
  const counts = new Map<string, number>();
  for (const key of s.perks.owned) {
    const good = dealGood(dealFromKey(key));
    if (good) counts.set(good, (counts.get(good) ?? 0) + 1);
  }
  let top: string | null = null;
  for (const [good, n] of counts) if (top === null || n > counts.get(top)!) top = good;
  return top;
}

/** Rough value of each deal kind for a player who wants them all (bag slots scale best). */
const DEAL_VALUE: Record<DealerDeal['kind'], number> = {
  bag: 5, sellChanceAll: 4, discountAll: 4, stockAll: 3, buyerStockAll: 3, discount: 2, sellChance: 1.5, stock: 1,
  buyerStock: 1,
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
    about: 'Buys every affordable deal in the order shown (the old sim).',
    pick: sensible,
    dealRank: () => 0,
  },
  packrat: {
    name: 'Packrat',
    about: 'Only wants bag upgrades, then all-goods deals; saves stars for them.',
    pick: sensible,
    dealRank: (_, d) => (d.kind === 'bag' ? 2 : isUniversal(d) ? 1 : null),
  },
  specialist: {
    name: 'Specialist',
    about: 'Commits to one good: buys its per-good deals and all-goods deals, and trades it harder.',
    pick: (s) => best(s, (l) => score(s, l, PROFILES.specialist.bias)),
    dealRank: (s, d) => {
      const good = dealGood(d);
      const focus = focusGood(s);
      if (good) return focus === null || good === focus ? 3 + margin(s, good) / 10 : null;
      return isUniversal(d) ? 2 : d.kind === 'bag' ? 1 : null;
    },
    bias: (s, good) => (good === focusGood(s) ? 1.5 : 1),
  },
  chaser: {
    name: 'Dealer chaser',
    about: 'Heads to the Dealer whenever it has 3+ stars, buys the best-value deals first.',
    pick: (s) =>
      best(s, (l) => score(s, l) + (s.dealer?.locationId === l && s.stars >= 3 ? 10 : 0)),
    dealRank: (_, d) => DEAL_VALUE[d.kind],
  },
};

// ------------------------------------------------------------------ trading ----

export function tradeAt(s: RunState, loc: string, profile: Profile = PROFILES.impulse): void {
  visit(s, loc);
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
  // sell: highest-paying buyer first
  const sales = actors
    .filter((a) => data.actors[a].role === 'buyer')
    .flatMap((a) => data.actors[a].goods.map((g) => ({ a, good: g.good, price: offer(s, a, g.good).price })))
    .sort((x, y) => y.price - x.price);
  for (const t of sales) sell(data, s, t.a, t.good, maxSell(s, t.a, t.good));
  if (s.day >= s.quota.dueDay) return;
  // buy: best expected margin first (scaled by the profile's bias)
  const bias = profile.bias ?? noBias;
  const buys = actors
    .filter((a) => data.actors[a].role === 'supplier')
    .flatMap((a) =>
      data.actors[a].goods.map((g) => {
        const p = offer(s, a, g.good).price;
        const r = resale(s, g.good);
        return { a, good: g.good, margin: r - p, ratio: (bias(s, g.good) * r) / p };
      }),
    )
    .filter((t) => t.margin > 0)
    .sort((x, y) => y.ratio - x.ratio);
  for (const t of buys) buy(data, s, t.a, t.good, 99);
}
