/**
 * Long-run balance sim (log only): how far do simulated players get?
 * Runs every strategy profile in players.ts (plus a random player) and prints the
 * share of runs still alive after each quota, with star and deal stats.
 *
 *   npm run sim                         # defaults below
 *   RUNS=1000 DAYS=49 npm run sim       # more runs / longer horizon
 *   QUOTAS='20,25,30;20,30,40' npm run sim  # compare quota tables (';' between tables)
 *   DEALER=0.5 npm run sim              # Dealer visit chance per day
 *   DISABLED=discount npm run sim       # stamp kinds Nox won't offer (empty = all on)
 *   DECK=0 npm run sim                  # roll deal tiers independently instead of from the deck
 *   HOLD=3 npm run sim                  # CGE focus holds a good until it can sell 3 to one buyer
 *   RAIN=0 npm run sim                  # profiles ignore the Rainstorm's buyer cap when buying
 *   FIREWORKS=0 DAYS=63 npm run sim     # turn Lantern Crossing's Fireworks Night off
 *   BLIZZARD=0 npm run sim              # turn Frostpine Peaks' Blizzard off
 *   START=1.5 npm run sim               # multiply every area's starting cash (rounded)
 */
import { describe, expect, it } from 'vitest';
import { rngFor } from '../src/engine/rng';
import { CONFIG } from '../src/game/config';
import { endDay, newRun, QUOTA_DAYS, quotaFor } from '../src/game/run';
import type { DealerDeal } from '../src/game/types';
import { data, forceStamp, PROFILES, type Profile, random, SIM, tradeAt } from './players';

const env = (k: string) => (typeof process !== 'undefined' ? process.env[k] : undefined);
const RUNS = Number(env('RUNS') ?? 500);
const DAYS = Number(env('DAYS') ?? 35);
const QUOTA_SETS = (env('QUOTAS') ?? CONFIG.quotas.join(',')).split(';').map((t) => t.split(',').map(Number));
const DEALER = Number(env('DEALER') ?? CONFIG.dealer.chance);
const DECK = env('DECK') !== '0';
if (env('BLIZZARD') === '0') data.areas.peaks.events = data.areas.peaks.events?.filter((e) => e.id !== 'blizzard');
if (env('FIREWORKS') === '0') data.areas.crossing.events = data.areas.crossing.events?.filter((e) => e.id !== 'fireworks');
const START = Number(env('START') ?? 1);
if (START !== 1) for (const a of Object.values(data.areas)) a.startCash = Math.round(a.startCash * START);
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
  /** The bag after each day's trading, per week (index = week − 1), over every run-day played. */
  bag: BagStats[];
}

/** Min / max / sum of the units in the bag and what was paid for them, over `n` run-days. */
interface BagStats {
  n: number;
  items: { min: number; max: number; sum: number };
  value: { min: number; max: number; sum: number };
}

const newBagStats = (): BagStats => ({
  n: 0,
  items: { min: Infinity, max: -Infinity, sum: 0 },
  value: { min: Infinity, max: -Infinity, sum: 0 },
});

function addTo(m: { min: number; max: number; sum: number }, x: number): void {
  m.min = Math.min(m.min, x);
  m.max = Math.max(m.max, x);
  m.sum += x;
}

function simulate(profile: Profile): Summary {
  const quotas = Math.floor(DAYS / QUOTA_DAYS);
  for (const k of Object.keys(SIM.bought) as DealerDeal['kind'][]) SIM.bought[k] = 0;
  const sum: Summary = { alive: Array(quotas).fill(0), lastDay: 0, stars: 0, spent: 0, cash: 0, days: 0, deals: { ...SIM.bought }, firstMet: Array(QUOTA_DAYS + 1).fill(0), day7: [],
    bag: Array.from({ length: Math.ceil(DAYS / QUOTA_DAYS) }, newBagStats) };
  for (let seed = 1; seed <= RUNS; seed++) {
    const s = newRun(data, seed);
    const r = rngFor(seed, 'sim');
    let firstDay = 0;
    while (s.day <= DAYS) {
      forceStamp(s, profile);
      tradeAt(s, profile.pick(s, () => r.next()), profile);
      if (!firstDay && s.quota.index === 0 && s.quota.met) firstDay = s.day;
      if (s.day === QUOTA_DAYS) sum.day7.push(s.cash);
      // the bag after the day's trading (before endDay, which empties it on an area move)
      const week = sum.bag[Math.floor((s.day - 1) / QUOTA_DAYS)];
      week.n++;
      addTo(week.items, s.inventory.length);
      addTo(week.value, s.inventory.reduce((v, it) => v + it.paid, 0));
      sum.cash += s.cash;
      sum.days++;
      endDay(data, s);
      if (s.status !== 'active') break;
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

const sum0 = (bags: [string, BagStats[]][]) => bags[0]?.[1] ?? [];

const RANDOM: Profile = { ...PROFILES.impulse, name: 'Random', about: 'Random location, impulse deals.', pick: random, ignoresRain: true };

describe('balance: long run', () => {
  it('reports survival after each quota for every profile (log only)', () => {
    const saved = {
      quotas: CONFIG.quotas, dealer: CONFIG.dealer.chance, disabled: CONFIG.dealer.disabled,
      deck: CONFIG.tierDeck,
    };
    CONFIG.tierDeck = DECK;
    CONFIG.dealer.chance = DEALER;
    CONFIG.dealer.disabled = DISABLED;
    const avg = (n: number) => (n / RUNS).toFixed(1);
    const profiles = [...Object.values(PROFILES), RANDOM];
    for (const g of QUOTA_SETS) {
      CONFIG.quotas = g;
      const amounts = Array.from({ length: Math.floor(DAYS / QUOTA_DAYS) }, (_, i) => `$${quotaFor(i).amount}`);
      console.log(`\nquotas: ${amounts.join(', ')}  (${RUNS} runs, to day ${DAYS}, dealer ${DEALER * 100}%, tier deck ${DECK ? 'on' : 'off'}, stamps off: ${DISABLED.join(', ') || 'none'})`);
      console.log(
        'profile        | ' + amounts.map((_, q) => `day ${String(QUOTA_DAYS * (q + 1)).padEnd(3)}`).join(' | ') +
          ' | end day | avg cash | stars got/spent | deals/run: bag disc stock dem luck all',
      );
      const firstMet: [string, number[]][] = [];
      const day7: [string, number[]][] = [];
      const bags: [string, BagStats[]][] = [];
      for (const p of profiles) {
        const s = simulate(p);
        firstMet.push([p.name, s.firstMet]);
        day7.push([p.name, s.day7]);
        bags.push([p.name, s.bag]);
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
      // what players carry overnight, by week: units in the bag and what was paid for them
      for (const [what, key, $] of [['units in the bag', 'items', ''], ['value in the bag (what was paid)', 'value', '$']] as const) {
        console.log(`
${what} after each day's trading, by week: avg (min–max), over the run-days played that week`);
        console.log('profile        | ' + sum0(bags).map((_, w) => `days ${w * QUOTA_DAYS + 1}–${(w + 1) * QUOTA_DAYS}`.padEnd(15)).join(' | '));
        for (const [name, weeks] of bags) {
          const cells = weeks.map((b) => {
            const m = b[key];
            return (b.n ? `${$}${(m.sum / b.n).toFixed(1)} (${$}${m.min}–${$}${m.max})` : '-').padEnd(15);
          });
          console.log(`${name.padEnd(14)} | ${cells.join(' | ')}`);
        }
      }
    }
    CONFIG.tierDeck = saved.deck;
    CONFIG.quotas = saved.quotas;
    CONFIG.dealer.chance = saved.dealer;
    CONFIG.dealer.disabled = saved.disabled;
    expect(true).toBe(true);
  }, 120_000);
});
