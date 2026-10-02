import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';

const meta = (name: string) =>
  JSON.parse(readFileSync(new URL(`../public/assets/font/${name}.json`, import.meta.url), 'utf8')) as {
    height: number;
    baseline: number;
    glyphs: Record<string, unknown>;
  };

describe('fonts', () => {
  it("the big (mobile) font has exactly the small font's glyphs", () => {
    expect(Object.keys(meta('font_lg').glyphs).sort()).toEqual(Object.keys(meta('font').glyphs).sort());
  });

  it('the big font is about 1.5x the small one', () => {
    const small = meta('font');
    const big = meta('font_lg');
    expect(big.baseline / small.baseline).toBeGreaterThanOrEqual(1.4);
    expect(big.baseline / small.baseline).toBeLessThanOrEqual(1.5);
  });
});
