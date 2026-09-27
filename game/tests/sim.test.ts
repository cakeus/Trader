/**
 * Balance simulation for the first quota ($10 -> $25 by day 7).
 * Players visit one location per day, sell what they can, then restock
 * greedily by expected margin. Location choice differs per policy.
 */
import { describe, expect, it } from 'vitest';
import { rngFor } from '../src/engine/rng';
import { CONFIG } from '../src/game/config';
import { actorsAt, buy, endDay, maxSell, newRun, offer, sell, visit } from '../src/game/run';
import { type GameData, type RunState, TIERS } from '../src/game/types';
import { loadTestData } from './helpers';

const data = loadTestData();
const SEEDS = 120;

const clone = (s: RunState): RunState => JSON.parse(JSON.stringify(s));

/** Tier-weighted average price for an actor's good. */
function expectedPrice(d: GameData, actorId: string, good: string): number {
  const ag = d.actors[actorId].goods.find((g) => g.good === good)!;
  return TIERS.reduce((sum, t) => sum + CONFIG.dealWeights[t] * ag.prices[t], 0);
}

/** Expected resale price for a good. Actors are re-dealt daily, so average over every buyer of it. */
function resale(good: string): number {
  const buyers = Object.keys(data.actors).filter(
    (id) => data.actors[id].role === 'buyer' && data.actors[id].goods.some((g) => g.good === good),
  );
  return buyers.reduce((sum, id) => sum + expectedPrice(data, id, good), 0) / buyers.length;
}

function tradeAt(s: RunState, loc: string): void {
  visit(s, loc);
  const actors = actorsAt(s, loc);
  // sell: highest-paying buyer first
  const sales = actors
    .filter((a) => data.actors[a].role === 'buyer')
    .flatMap((a) => data.actors[a].goods.map((g) => ({ a, good: g.good, price: offer(s, a, g.good).price })))
    .sort((x, y) => y.price - x.price);
  for (const t of sales) sell(data, s, t.a, t.good, maxSell(s, t.a, t.good));
  if (s.day >= s.quota.dueDay) return;
  // buy: best expected margin first
  const buys = actors
    .filter((a) => data.actors[a].role === 'supplier')
    .flatMap((a) =>
      data.actors[a].goods.map((g) => {
        const p = offer(s, a, g.good).price;
        return { a, good: g.good, margin: resale(g.good) - p, ratio: resale(g.good) / p };
      }),
    )
    .filter((t) => t.margin > 0)
    .sort((x, y) => y.ratio - x.ratio);
  for (const t of buys) buy(data, s, t.a, t.good, 99);
}

/** Expected value of visiting `loc` with the current bag (what a thoughtful player estimates). */
function score(s: RunState, loc: string): number {
  let v = 0;
  const bag = s.inventory.map((it) => it.good);
  for (const a of actorsAt(s, loc)) {
    const def = data.actors[a];
    if (def.role !== 'buyer') continue;
    for (const g of def.goods) {
      const n = bag.filter((x) => x === g.good).length;
      v += n * expectedPrice(data, a, g.good);
      for (let i = 0; i < n; i++) bag.splice(bag.indexOf(g.good), 1);
    }
  }
  // small bonus for being able to restock with something profitable
  for (const a of actorsAt(s, loc))
    if (data.actors[a].role === 'supplier')
      for (const g of data.actors[a].goods) v += 0.5 * (resale(g.good) - expectedPrice(data, a, g.good));
  return v;
}

type Policy = (s: RunState, rng: () => number) => string;

const sensible: Policy = (s) => {
  const locs = s.locations.map((l) => l.id);
  return locs.reduce((b, l) => (score(s, l) > score(s, b) ? l : b));
};
const random: Policy = (s, rng) => s.locations[Math.floor(rng() * s.locations.length)].id;

function playQuota1(seed: number, policy: Policy): { met: boolean; cash: number; metDay: number } {
  const s = newRun(data, seed);
  const r = rngFor(seed, 'sim');
  let metDay = 0;
  while (s.day <= 7) {
    tradeAt(s, policy(s, () => r.next()));
    if (s.quota.met && !metDay) metDay = s.day;
    if (s.day === 7) break;
    endDay(data, s);
  }
  return { met: s.quota.met, cash: s.cash, metDay };
}

function oracle(seed: number): { met: boolean; best: number } {
  let best = 0;
  let met = false;
  const locs = newRun(data, seed).locations.map((l) => l.id);
  const rec = (s: RunState) => {
    for (const l of locs) {
      const c = clone(s);
      tradeAt(c, l);
      if (c.quota.met) met = true;
      if (c.day === 7) {
        best = Math.max(best, c.cash);
      } else {
        endDay(data, c);
        rec(c);
      }
    }
  };
  rec(newRun(data, seed));
  return { met, best };
}

describe('balance: first quota', () => {
  it('is reachable with good play but hard', () => {
    let oracleMet = 0;
    let sensibleMet = 0;
    let randomMet = 0;
    let oracleCash = 0;
    let sensibleCash = 0;
    let metDaySum = 0;
    for (let seed = 1; seed <= SEEDS; seed++) {
      const o = oracle(seed);
      const p = playQuota1(seed, sensible);
      const q = playQuota1(seed, random);
      oracleMet += +o.met;
      oracleCash += o.best;
      sensibleMet += +p.met;
      sensibleCash += p.cash;
      if (p.met) metDaySum += p.metDay;
      randomMet += +q.met;
    }
    const pct = (n: number) => `${Math.round((100 * n) / SEEDS)}%`;
    console.log(
      `oracle met ${pct(oracleMet)} (avg best cash $${(oracleCash / SEEDS).toFixed(1)}) | ` +
        `sensible met ${pct(sensibleMet)} (avg cash $${(sensibleCash / SEEDS).toFixed(1)}, ` +
        `avg met day ${(metDaySum / Math.max(1, sensibleMet)).toFixed(1)}) | random met ${pct(randomMet)}`,
    );
    // target: hard but fair
    expect(oracleMet / SEEDS).toBeGreaterThanOrEqual(0.9);
    expect(randomMet).toBeLessThan(sensibleMet);
    expect(randomMet / SEEDS).toBeLessThan(0.15);
  });
});
