/**
 * Long-run balance sim (log only): how far do simulated players get?
 * Runs every strategy profile in players.ts (plus a random player) and prints the
 * share of runs still alive after each quota, with star and deal stats.
 *
 *   npm run sim                         # defaults below
 *   RUNS=1000 DAYS=49 npm run sim       # more runs / longer horizon
 *   GROWTH=2,1.75,1.5 npm run sim       # compare quota growth factors
 *   DEALER=0.5 npm run sim              # Dealer visit chance per day
 */
import { describe, expect, it } from 'vitest';
import { rngFor } from '../src/engine/rng';
import { CONFIG } from '../src/game/config';
import { endDay, newRun, QUOTA_DAYS, quotaFor } from '../src/game/run';
import type { DealerDeal } from '../src/game/types';
import { data, PROFILES, type Profile, random, SIM, tradeAt } from './players';

const env = (k: string) => (typeof process !== 'undefined' ? process.env[k] : undefined);
const RUNS = Number(env('RUNS') ?? 500);
const DAYS = Number(env('DAYS') ?? 35);
const GROWTH = (env('GROWTH') ?? String(CONFIG.quotaGrowth)).split(',').map(Number);
const DEALER = Number(env('DEALER') ?? CONFIG.dealer.chance);

interface Summary {
  alive: number[];
  lastDay: number;
  stars: number;
  spent: number;
  deals: Record<DealerDeal['kind'], number>;
}

function simulate(profile: Profile): Summary {
  const quotas = Math.floor(DAYS / QUOTA_DAYS);
  for (const k of Object.keys(SIM.bought) as DealerDeal['kind'][]) SIM.bought[k] = 0;
  const sum: Summary = { alive: Array(quotas).fill(0), lastDay: 0, stars: 0, spent: 0, deals: { ...SIM.bought } };
  for (let seed = 1; seed <= RUNS; seed++) {
    const s = newRun(data, seed);
    const r = rngFor(seed, 'sim');
    while (s.day <= DAYS) {
      tradeAt(s, profile.pick(s, () => r.next()), profile);
      if (endDay(data, s) === 'failed') break;
    }
    for (let q = 0; q < Math.min(quotas, s.stats.quotasMet); q++) sum.alive[q]++;
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
    const saved = { growth: CONFIG.quotaGrowth, dealer: CONFIG.dealer.chance };
    CONFIG.dealer.chance = DEALER;
    const avg = (n: number) => (n / RUNS).toFixed(1);
    const profiles = [...Object.values(PROFILES), RANDOM];
    for (const g of GROWTH) {
      CONFIG.quotaGrowth = g;
      const amounts = Array.from({ length: Math.floor(DAYS / QUOTA_DAYS) }, (_, i) => `$${quotaFor(i).amount}`);
      console.log(`\nquota growth x${g}: ${amounts.join(', ')}  (${RUNS} runs, to day ${DAYS}, dealer ${DEALER * 100}%)`);
      console.log(
        'profile        | ' + amounts.map((_, q) => `day ${String(QUOTA_DAYS * (q + 1)).padEnd(3)}`).join(' | ') +
          ' | end day | stars got/spent | deals/run: bag disc stock dem sell all',
      );
      for (const p of profiles) {
        const s = simulate(p);
        const cols = s.alive.map((n) => `${((100 * n) / RUNS).toFixed(1)}%`.padStart(7)).join(' | ');
        const d = s.deals;
        console.log(
          `${p.name.padEnd(14)} | ${cols} | ${(s.lastDay / RUNS).toFixed(1).padStart(7)} |` +
            ` ${avg(s.stars).padStart(6)} / ${avg(s.spent).padEnd(6)} |` +
            ` ${[d.bag, d.discount, d.stock, d.buyerStock, d.sellChance, d.discountAll + d.stockAll + d.buyerStockAll + d.sellChanceAll].map(avg).join('  ')}`,
        );
      }
    }
    CONFIG.quotaGrowth = saved.growth;
    CONFIG.dealer.chance = saved.dealer;
    expect(true).toBe(true);
  });
});
