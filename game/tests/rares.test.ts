/**
 * Rare stamp value sim (log only): how much cash does each rare add per day, by area?
 *
 * Every run is played by the Impulse trader to day DAYS with quotas forced met (so every run sees
 * every area) and Nox switched off. Instead, each run is given COMMONS random common stamps a week
 * (days 8, 15, 22, …; seeded by the run only, so every variant of a run gets the same ones). The
 * baseline has only those; each rare variant is the same seed plus that rare on day 8. Profit is
 * the day's change in net worth (cash plus what the bag cost), so holding goods overnight and the
 * area move's buyback don't count. The rare's value is its variant's average daily profit minus
 * the baseline's, over the same seeds and days (from day 8).
 *
 *   npm run rares
 *   RUNS=1000 COMMONS=2 npm run rares
 */
import { describe, expect, it } from 'vitest';
import { rngFor } from '../src/engine/rng';
import { CONFIG } from '../src/game/config';
import { allDeals, dealEnabled, eligibleDeals, grantDeal, rarityOf } from '../src/game/dealer';
import { debugSetQuotaMet, endDay, newRun } from '../src/game/run';
import type { RunState, SingleKind } from '../src/game/types';
import { data, PROFILES, tradeAt } from './players';

const env = (k: string) => process.env[k];
const RUNS = Number(env('RUNS') ?? 500);
const DAYS = Number(env('DAYS') ?? 63);
const COMMONS = Number(env('COMMONS') ?? 1);
const GRANT_DAY = 8;

const AREAS = Object.values(data.areas).sort((a, b) => a.fromDay - b.fromDay).map((a) => a.id);

interface Tally {
  /** Summed daily profit and days counted, per area (days from GRANT_DAY on). */
  profit: Record<string, number>;
  days: Record<string, number>;
  /** Summed cash after the day's trading, per area (is cash what limits buying?). */
  cash: Record<string, number>;
  /** Each run's total profit over the counted days (for the paired standard error). */
  runs: number[];
}

const worth = (s: RunState) => s.cash + s.inventory.reduce((v, it) => v + it.paid, 0);

function play(seed: number, rare: SingleKind | null, t: Tally): void {
  const s = newRun(data, seed);
  s.dealerSeen = true; // with chance 0, no guaranteed first visit either
  const commons = rngFor(seed, 'commons');
  const profile = PROFILES.impulse;
  let total = 0;
  while (s.day <= DAYS) {
    if (s.day >= GRANT_DAY && (s.day - GRANT_DAY) % 7 === 0)
      for (let i = 0; i < COMMONS; i++) {
        const pool = eligibleDeals(data, s).filter((d) => rarityOf(d) === 'common');
        if (pool.length) grantDeal(data, s, pool[commons.int(0, pool.length - 1)]);
      }
    if (rare && s.day === GRANT_DAY) grantDeal(data, s, { kind: rare });
    const area = s.area;
    const before = worth(s);
    tradeAt(s, profile.pick(s, Math.random), profile);
    const cash = s.cash;
    if (s.day >= s.quota.dueDay) debugSetQuotaMet(s, true);
    const day = s.day;
    endDay(data, s);
    if (day >= GRANT_DAY) {
      t.profit[area] += worth(s) - before; // the area move's buyback is at cost, so it nets out
      t.days[area]++;
      t.cash[area] += cash;
      total += worth(s) - before;
    }
    if (s.status !== 'active') break; // won on the last day
  }
  t.runs.push(total);
}

const emptyTally = (): Tally => {
  const z = () => Object.fromEntries(AREAS.map((a) => [a, 0]));
  return { profit: z(), days: z(), cash: z(), runs: [] };
};

describe('balance: rare stamp value', () => {
  it('reports each rare\'s extra profit per day by area (log only)', () => {
    const saved = { chance: CONFIG.dealer.chance };
    CONFIG.dealer.chance = 0;
    const rares = allDeals(data)
      .filter((d) => rarityOf(d) === 'rare' && dealEnabled(d))
      .map((d) => d.kind as SingleKind);
    const run = (rare: SingleKind | null) => {
      const t = emptyTally();
      for (let seed = 1; seed <= RUNS; seed++) play(seed, rare, t);
      return t;
    };
    const base = run(null);
    const per = (t: Tally, a: string) => t.profit[a] / t.days[a];
    const avgAll = (t: Tally) =>
      AREAS.reduce((v, a) => v + t.profit[a], 0) / AREAS.reduce((v, a) => v + t.days[a], 0);
    const rows = rares.map((kind) => ({ kind, t: run(kind) }));
    rows.sort((x, y) => avgAll(y.t) - avgAll(x.t));

    const fmt = (x: number) => `${x >= 0 ? '+' : '-'}$${Math.abs(x).toFixed(2)}`.padStart(8);
    const pct = (x: number, b: number) => `${x >= 0 ? '+' : '-'}${Math.abs((100 * x) / b).toFixed(0)}%`.padStart(5);
    console.log(`\nrare stamp value: ${RUNS} runs to day ${DAYS}, Impulse trader, quotas forced, no Nox,`
      + ` ${COMMONS} random common(s) a week from day ${GRANT_DAY}, rare granted on day ${GRANT_DAY}`);
    console.log(`baseline profit/day: ${AREAS.map((a) => `${a} $${per(base, a).toFixed(2)}`).join(', ')}, all $${avgAll(base).toFixed(2)}`);
    console.log(`baseline cash after trading: ${AREAS.map((a) => `${a} $${(base.cash[a] / base.days[a]).toFixed(0)}`).join(', ')}`);
    console.log('extra profit per day vs baseline (and % of baseline)');
    // standard error of the all-days difference, paired by seed
    const daysPerRun = AREAS.reduce((v, a) => v + base.days[a], 0) / RUNS;
    const se = (t: Tally) => {
      const d = t.runs.map((x, i) => (x - base.runs[i]) / daysPerRun);
      const m = d.reduce((a, b) => a + b, 0) / d.length;
      return Math.sqrt(d.reduce((a, b) => a + (b - m) ** 2, 0) / (d.length - 1) / d.length);
    };
    console.log('rare            | ' + AREAS.map((a) => a.padEnd(14)).join(' | ') + ' | all days       | ±se');
    for (const { kind, t } of rows) {
      const cells = AREAS.map((a) => {
        const d = per(t, a) - per(base, a);
        return `${fmt(d)} ${pct(d, per(base, a))}`;
      });
      const d = avgAll(t) - avgAll(base);
      console.log(`${kind.padEnd(15)} | ${cells.join(' | ')} | ${fmt(d)} ${pct(d, avgAll(base))} | ${se(t).toFixed(2)}`);
    }
    CONFIG.dealer.chance = saved.chance;
    expect(true).toBe(true);
  }, 1_800_000);
});
