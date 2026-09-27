/**
 * Balance simulation for the first quota ($10 -> $25 by day 7).
 * The players live in players.ts; the long-run sim is longrun.test.ts.
 */
import { describe, expect, it } from 'vitest';
import { rngFor } from '../src/engine/rng';
import { endDay, newRun } from '../src/game/run';
import type { RunState } from '../src/game/types';
import { clone, data, type Policy, random, sensible, tradeAt } from './players';

const SEEDS = 120;

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
