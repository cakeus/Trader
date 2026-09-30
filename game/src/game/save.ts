import type { RunState } from './types';

const SAVE_KEY = 'trader.run';

export function saveRun(state: RunState): void {
  try {
    localStorage.setItem(SAVE_KEY, JSON.stringify(state));
  } catch {
    // storage unavailable (private mode etc.) — the run just won't persist
  }
}

export function loadRun(): RunState | null {
  try {
    const raw = localStorage.getItem(SAVE_KEY);
    if (!raw) return null;
    const s = JSON.parse(raw) as RunState;
    if (s.version !== 13 || s.status !== 'active') return null;
    return s;
  } catch {
    return null;
  }
}

export function clearRun(): void {
  try {
    localStorage.removeItem(SAVE_KEY);
  } catch {
    // ignore
  }
}

const HIGHSCORE_KEY = 'trader.highscore';

/** The best final cash of any won run, or null before the first win. */
export function loadHighScore(): number | null {
  try {
    const n = Number(localStorage.getItem(HIGHSCORE_KEY) ?? NaN);
    return Number.isFinite(n) ? n : null;
  } catch {
    return null;
  }
}

/** Record a won run's score. Returns the best before it, and whether this one beat it. */
export function recordHighScore(score: number): { best: number | null; isNew: boolean } {
  const best = loadHighScore();
  const isNew = best === null || score > best;
  if (isNew) {
    try {
      localStorage.setItem(HIGHSCORE_KEY, String(score));
    } catch {
      // storage unavailable — the high score just won't persist
    }
  }
  return { best, isNew };
}
