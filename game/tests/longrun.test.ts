/**
 * Long-run balance sim (log only): how far do simulated players get?
 * Runs every strategy profile in players.ts (plus a random player) and prints the
 * share of runs still alive after each quota, with star and deal stats.
 *
 *   npm run sim                         # defaults below
 *   RUNS=1000 DAYS=49 npm run sim       # more runs / longer horizon
 *   GROWTH=2,1.75,1.5 npm run sim       # compare quota growth factors
 *   DEALER=0.5 npm run sim              # Dealer visit chance per day
 *   DISABLED=discount npm run sim       # stamp kinds Nox won't offer (empty = all on)
 *   DECK=0 npm run sim                  # roll deal tiers independently instead of from the deck
 *   WEEK1BAD=0.2 npm run sim            # bad buyer weight during the first quota (the rest is good)
 */
import { describe, expect, it } from 'vitest';
import { rngFor } from '../src/engine/rng';
import { CONFIG } from '../src/game/config';
import { endDay, newRun, QUOTA_DAYS, quotaFor, takeBuyout } from '../src/game/run';
import type { DealerDeal } from '../src/game/types';
import { data, PROFILES, type Profile, random, SIM, tradeAt } from './players';

const env = (k: string) => (typeof process !== 'undefined' ? process.env[k] : undefined);
const RUNS = Number(env('RUNS') ?? 500);
const DAYS = Number(env('DAYS') ?? 35);
const GROWTH = (env('GROWTH') ?? String(CONFIG.quotaGrowth)).split(',').map(Number);
const DEALER = Number(env('DEALER') ?? CONFIG.dealer.chance);
const DECK = env('DECK') !== '0';
const WEEK1BAD = Number(env('WEEK1BAD') ?? CONFIG.firstQuotaBuyerDealWeights.bad);
const DISABLED = (env('DISABLED')?.split(',').filter(Boolean) ?? CONFIG.dealer.disabled) as DealerDeal['kind'][];

interface Summary {
  alive: number[];
  lastDay: number;
  stars: number;
  spent: number;
  /** Cash on hand after each day's trading, summed over every day played. */
  cash: number;
  days: number;
  deals: Record<DealerDeal['kind'], number>;
  /** Runs that met the first quota on each day (index = day), or missed it (index 0). */
  firstMet: number[];
  /** Cash after day 7's trading, per run. */
  day7: number[];
}

function simulate(profile: Profile): Summary {
  const quotas = Math.floor(DAYS / QUOTA_DAYS);
  for (const k of Object.keys(SIM.bought) as DealerDeal['kind'][]) SIM.bought[k] = 0;
  const sum: Summary = { alive: Array(quotas).fill(0), lastDay: 0, stars: 0, spent: 0, cash: 0, days: 0, deals: { ...SIM.bought }, firstMet: Array(QUOTA_DAYS + 1).fill(0), day7: [] };
  for (let seed = 1; seed <= RUNS; seed++) {
    const s = newRun(data, seed);
    const r = rngFor(seed, 'sim');
    let firstDay = 0;
    while (s.day <= DAYS) {
      tradeAt(s, profile.pick(s, () => r.next()), profile);
      takeBuyout(data, s); // only offered on an unmet quota's due day, and turning it down fails the run
      if (!firstDay && s.quota.index === 0 && s.quota.met) firstDay = s.day;
      if (s.day === QUOTA_DAYS) sum.day7.push(s.cash);
      sum.cash += s.cash;
      sum.days++;
      if (endDay(data, s) === 'failed') break;
    }
    for (let q = 0; q < Math.min(quotas, s.stats.quotasMet); q++) sum.alive[q]++;
    sum.firstMet[firstDay]++;
    sum.lastDay += Math.min(s.day, DAYS);
    sum.stars += s.stats.starsEarned;
    sum.spent += s.stats.starsEarned - s.stars;
  }
  sum.deals = { ...SIM.bought };
  return sum;
}

const RANDOM: Profile = { ...PROFILES.impulse, name: 'Random', about: 'Random location, impulse deals.', pick: random };

describe('balance: long run', () => {
  it('reports survival after each quota for every profile (log only)', () => {
    const saved = {
      growth: CONFIG.quotaGrowth, dealer: CONFIG.dealer.chance, disabled: CONFIG.dealer.disabled,
      deck: CONFIG.tierDeck, week1: CONFIG.firstQuotaBuyerDealWeights,
    };
    const base = CONFIG.buyerDealWeights;
    CONFIG.tierDeck = DECK;
    CONFIG.firstQuotaBuyerDealWeights = { ...base, bad: WEEK1BAD, good: base.good + base.bad - WEEK1BAD };
    CONFIG.dealer.chance = DEALER;
    CONFIG.dealer.disabled = DISABLED;
    const avg = (n: number) => (n / RUNS).toFixed(1);
    const profiles = [...Object.values(PROFILES), RANDOM];
    for (const g of GROWTH) {
      CONFIG.quotaGrowth = g;
      const amounts = Array.from({ length: Math.floor(DAYS / QUOTA_DAYS) }, (_, i) => `$${quotaFor(i).amount}`);
      console.log(`\nquota growth x${g}: ${amounts.join(', ')}  (${RUNS} runs, to day ${DAYS}, dealer ${DEALER * 100}%, tier deck ${DECK ? 'on' : 'off'}, week-1 bad buyers ${WEEK1BAD * 100}%, stamps off: ${DISABLED.join(', ') || 'none'})`);
      console.log(
        'profile        | ' + amounts.map((_, q) => `day ${String(QUOTA_DAYS * (q + 1)).padEnd(3)}`).join(' | ') +
          ' | end day | avg cash | stars got/spent | deals/run: bag disc stock dem luck all',
      );
      const firstMet: [string, number[]][] = [];
      const day7: [string, number[]][] = [];
      for (const p of profiles) {
        const s = simulate(p);
        firstMet.push([p.name, s.firstMet]);
        day7.push([p.name, s.day7]);
        const cols = s.alive.map((n) => `${((100 * n) / RUNS).toFixed(1)}%`.padStart(7)).join(' | ');
        const d = s.deals;
        console.log(
          `${p.name.padEnd(14)} | ${cols} | ${(s.lastDay / RUNS).toFixed(1).padStart(7)} |` +
            ` ${`$${(s.cash / s.days).toFixed(1)}`.padStart(8)} |` +
            ` ${avg(s.stars).padStart(6)} / ${avg(s.spent).padEnd(6)} |` +
            ` ${[d.bag, d.discount, d.stock, d.buyerStock, d.luck, d.discountAll + d.stockAll + d.buyerStockAll + d.luckAll].map(avg).join('  ')}`,
        );
      }
      console.log(`
day the first quota ($${amounts[0].slice(1)}) was met, share of runs:`);
      // profiles only differ once the Dealer shows up, so identical histograms share one chart
      const groups = new Map<string, { names: string[]; counts: number[] }>();
      for (const [name, counts] of firstMet) {
        const g = groups.get(counts.join()) ?? { names: [], counts };
        g.names.push(name);
        groups.set(counts.join(), g);
      }
      for (const { names, counts } of groups.values()) {
        console.log(`
${names.join(', ')}`);
        const rows = [...counts.slice(1).map((n, i) => [`day ${i + 1}`, n] as const), ['missed', counts[0]] as const];
        for (const [label, n] of rows) {
          const share = n / RUNS;
          console.log(`  ${label.padEnd(6)} ${`${(100 * share).toFixed(1)}%`.padStart(6)} ${'#'.repeat(Math.round(share * 60))}`);
        }
      }
      // the spread of day-7 cash: how predictable the first quota is (identical profiles share a line)
      console.log(`
cash after day ${QUOTA_DAYS}'s trading (runs that got there): p10 / p25 / p50 / p75 / p90, and the standard deviation`);
      const spread = new Map<string, string[]>();
      for (const [name, cash] of day7) {
        const c = cash.slice().sort((a, b) => a - b);
        const q = (f: number) => `$${c[Math.min(c.length - 1, Math.floor(f * c.length))]}`.padStart(4);
        const mean = c.reduce((a, b) => a + b, 0) / c.length;
        const sd = Math.sqrt(c.reduce((a, b) => a + (b - mean) ** 2, 0) / c.length);
        const line = `${[0.1, 0.25, 0.5, 0.75, 0.9].map(q).join(' / ')}   sd $${sd.toFixed(1)}`;
        spread.set(line, [...(spread.get(line) ?? []), name]);
      }
      for (const [line, names] of spread) console.log(`  ${line}   ${names.join(', ')}`);
    }
    CONFIG.tierDeck = saved.deck;
    CONFIG.firstQuotaBuyerDealWeights = saved.week1;
    CONFIG.quotaGrowth = saved.growth;
    CONFIG.dealer.chance = saved.dealer;
    CONFIG.dealer.disabled = saved.disabled;
    expect(true).toBe(true);
  });
});
