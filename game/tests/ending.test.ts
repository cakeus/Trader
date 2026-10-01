import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { debugAdvance, debugSetQuotaMet, endDay, LAST_DAY, newRun } from '../src/game/run';
import { loadHighScore, recordHighScore } from '../src/game/save';
import type { RunState } from '../src/game/types';
import { loadTestData } from './helpers';

const data = loadTestData();

/** A run on the last day, with every quota before it met (without trading). */
function lastDay(seed: number): RunState {
  const s = newRun(data, seed);
  while (s.day < LAST_DAY) {
    debugSetQuotaMet(data, s, true);
    debugAdvance(data, s);
  }
  return s;
}

describe('the end of the run', () => {
  it('reaches the last day in the last area on its last quota', () => {
    const s = lastDay(3);
    expect(s.day).toBe(63);
    expect(s.quota.dueDay).toBe(LAST_DAY);
    expect(s.area).toBe('crossing');
    expect(s.status).toBe('active');
  });

  it('wins the run when the last quota is met, and stops there', () => {
    const s = lastDay(3);
    s.inventory = [{ good: 'sushi_roll', paid: 12, day: LAST_DAY }];
    debugSetQuotaMet(data, s, true);
    const cash = s.cash;
    expect(endDay(data, s)).toBe('won');
    expect(s.status).toBe('won');
    expect(s.stats.quotasMet).toBe(9);
    expect(s.day).toBe(LAST_DAY);
    // the bag is cashed out at cost, and the cash isn't reset: it's the score
    expect(s.cash).toBe(cash + 12);
    expect(s.inventory.length).toBe(0);
  });

  it('fails the run when the last quota is missed', () => {
    const s = lastDay(4);
    s.cash = 0;
    expect(endDay(data, s)).toBe('failed');
    expect(s.status).toBe('failed');
  });

  it('stops the debug advance at a win', () => {
    const s = lastDay(5);
    debugSetQuotaMet(data, s, true);
    debugAdvance(data, s);
    expect(s.status).toBe('won');
    expect(s.day).toBe(LAST_DAY);
  });
});

describe('high score', () => {
  beforeEach(() => {
    const store = new Map<string, string>();
    vi.stubGlobal('localStorage', {
      getItem: (k: string) => store.get(k) ?? null,
      setItem: (k: string, v: string) => void store.set(k, v),
      removeItem: (k: string) => void store.delete(k),
    });
  });
  afterEach(() => vi.unstubAllGlobals());

  it('keeps the best score and says when it is beaten', () => {
    expect(loadHighScore()).toBeNull();
    expect(recordHighScore(2000)).toEqual({ best: null, isNew: true });
    expect(recordHighScore(1800)).toEqual({ best: 2000, isNew: false });
    expect(loadHighScore()).toBe(2000);
    expect(recordHighScore(2500)).toEqual({ best: 2000, isNew: true });
    expect(loadHighScore()).toBe(2500);
  });
});
