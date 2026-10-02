import type { App, Scene } from '../app';
import type { SfxName } from '../engine/audio';
import { isMobile } from '../engine/device';
import { H, W } from '../engine/screen';
import { C, type Ui } from '../engine/ui';
import { CONFIG } from '../game/config';
import { bonusTargets } from '../game/run';
import type { Quota, RunState } from '../game/types';
import { STAR_INK } from './common';

/** Seconds a money row takes to count up, and between rows. */
const COUNT_T = 0.7;
const GAP = 0.25;
/** Seconds a row takes to pop in. */
const POP_T = 0.3;
const STAR_GAP = 0.65;
/** The panel's width; where the rows start and their steps (a money or star row, the total);
 *  the footer's height (its lines, the button); and the button's height. Mobile's scale-2 text is
 *  the big font's, so its rows are further apart. On desktop the panel is a fixed `h` tall. */
const L = isMobile
  ? { w: 440, h: 0, rows: 66, step: 28, totalStep: 34, foot: 100, btnH: 30 }
  : { w: 360, h: 340, rows: 66, step: 20, totalStep: 28, foot: 76, btnH: 26 };

/** One line of the tally, shown from `at` seconds in. */
interface Row {
  at: number;
  label: string;
  /** Money counted up from 0 over COUNT_T (or shown at once when `dur` is 0), or stars. */
  money?: { value: number; plus: boolean; dur: number };
  stars?: number;
  /** The bonus stars row: it counts up a star at each of `times` (seconds in), its label moving
   *  to the step just reached. With no times, it shows faded at +0. */
  bonus?: { times: number[]; labels: string[] };
  /** The total stars earned, drawn larger. */
  total?: number;
  /** Drawn faded (no bonus stars reached). */
  missed?: boolean;
  /** Draw a divider line above it, or leave a gap above it. */
  rule?: boolean;
  gap?: boolean;
}

/** Ease-out-back: overshoots a little, then settles at 1. */
function pop(p: number): number {
  const q = Math.min(1, Math.max(0, p)) - 1;
  return 1 + 2.70158 * q * q * q + 1.70158 * q * q;
}

/** How the tally closes: its button's label and what happens after (it's popped either way), and
 *  the run it's for (the final quota's tally comes after the run has ended, so `app.run` is gone). */
export interface QuotaResultOptions {
  button?: string;
  onDone?: () => void;
  run?: RunState;
}

/** Shown on the morning after a quota is passed: a tally of how the week ended (cash on hand, the
 *  stamp payouts and the bag cashed out), then the stars it paid: the base stars, one bonus row
 *  that counts up a star per bonus step reached, and the total. A click skips to the end. The last
 *  quota's tally closes with Continue, on to the win screen. */
export class QuotaResult implements Scene {
  private rows: Row[] = [];
  /** When the footer and the button (Onward! or the given label) show. */
  private done: number;
  private start: number | null = null;
  private skipped = false;
  /** Rows whose sound has played, and when the last counting tick played. */
  private sounded = new Set<Row>();
  /** Bonus stars whose chime has played. */
  private bonusSounded = 0;
  private lastTick = 0;

  constructor(private app: App, private passed: Quota, private opts: QuotaResultOptions = {}) {
    const q = passed;
    let t = 0.45;
    const money = (label: string, value: number, plus: boolean, always = true) => {
      if (!always && value === 0) return;
      const dur = value === 0 ? 0 : COUNT_T;
      this.rows.push({ at: t, label, money: { value, plus, dur } });
      t += dur + GAP;
    };
    money('Cash on hand', q.cashBefore ?? 0, false);
    money('Stamp payouts', q.payouts ?? 0, true, false);
    money('Bag cashed out', q.cashOut ?? 0, true);
    this.rows.push({ at: t, label: `Total (quota $${q.amount})`, money: { value: q.finalCash ?? 0, plus: false, dur: 0 }, rule: true });
    t += 0.55;
    this.rows.push({ at: t, label: 'Quota met', stars: q.stars, gap: true });
    const bonus = q.bonusStars ?? 0;
    const targets = bonusTargets(q.amount);
    const labels = CONFIG.bonusSteps.map((step, i) => `Over by ${Math.round(step * 100)}% ($${targets[i]})`);
    t += STAR_GAP;
    const times = Array.from({ length: bonus }, (_, i) => t + i * STAR_GAP);
    this.rows.push({ at: t, label: labels[0], bonus: { times, labels }, missed: bonus === 0 });
    t += Math.max(1, bonus) * STAR_GAP + 0.15;
    this.rows.push({ at: t, label: 'Stars earned', total: q.starsAwarded ?? q.stars + bonus, rule: true });
    this.done = t + 0.5;
  }

  frame(ui: Ui): void {
    const { app } = this;
    const run = this.opts.run ?? app.run!;
    if (this.start === null) this.start = ui.t;
    const skip = { x: 0, y: 0, w: W, h: H };
    // the first click (or Enter) skips to the end; the next one goes on
    let skipping = false;
    if (!this.skipped && ui.t - this.start < this.done && (ui.clicked(skip) || ui.key('Enter') || ui.key(' '))) {
      this.skipped = true;
      skipping = true;
    }
    const e = this.skipped ? Infinity : ui.t - this.start;
    this.playSounds(e);

    ui.dim(0.55);
    const w = L.w;
    const h = L.h || this.rowsHeight() + L.rows + L.foot;
    const r = { x: (W - w) / 2, y: (H - h) / 2, w, h };
    ui.nine('panel', r);

    // the title pops in, flags bobbing either side
    const bob = Math.round(Math.sin(ui.t * 4) * 2);
    this.scaled(ui, pop(e / POP_T), W / 2, r.y + 26, () =>
      ui.text('Quota met!', W / 2, r.y + 16, C.green, { align: 'center', scale: 3 }),
    );
    if (e > POP_T) {
      ui.image('assets/ui/icon_flag.png', W / 2 - 120, r.y + 18 + bob);
      ui.image('assets/ui/icon_flag.png', W / 2 + 104, r.y + 18 - bob);
    }
    ui.text(`Week ${this.passed.index + 1}, Day ${this.passed.dueDay}`, W / 2, r.y + 46, C.inkSoft, { align: 'center' });

    const lx = r.x + 40;
    const rx = r.x + w - 40;
    let y = r.y + L.rows;
    for (const row of this.rows) {
      if (row.gap) y += 8;
      if (row.rule) {
        if (e >= row.at) {
          ui.ctx.fillStyle = 'rgba(74,46,62,0.35)';
          ui.ctx.fillRect(lx, y + 1, rx - lx, 1);
        }
        y += 6;
      }
      if (e >= row.at) this.drawRow(ui, row, e, lx, rx, y);
      y += row.total !== undefined ? L.totalStep : L.step;
    }

    if (e >= this.done && !skipping) {
      const half = Math.round((ui.font.lineHeight + 5) / 2);
      // mobile's footer starts just under the rows
      const fy = isMobile ? r.y + h - L.foot + 6 + half : r.y + h - L.foot;
      if (this.passed.rollover)
        ui.text(`Golden Goose carries $${this.passed.rollover} into next week.`, W / 2, fy - half, C.gold, { align: 'center' });
      ui.text(`You have ${run.stars} star${run.stars === 1 ? '' : 's'}.`, W / 2, fy + half, C.inkSoft, { align: 'center' });
      if (ui.button({ x: W / 2 - 60, y: r.y + h - L.btnH - 14, w: 120, h: L.btnH }, this.opts.button ?? 'Onward!') || ui.key('Enter')) {
        app.pop(this);
        this.opts.onDone?.();
      }
    }
  }

  /** How tall the rows are, with their gaps and rules. */
  private rowsHeight(): number {
    return this.rows.reduce((sum, row) => sum + (row.gap ? 8 : 0) + (row.rule ? 6 : 0) + (row.total !== undefined ? L.totalStep : L.step), 0);
  }

  private drawRow(ui: Ui, row: Row, e: number, lx: number, rx: number, y: number): void {
    let age = e - row.at;
    const faded = row.missed === true;
    const ink = faded ? C.muted : C.ink;
    ui.ctx.save();
    ui.ctx.globalAlpha = Math.min(1, age / 0.15);
    let label = row.label;
    let stars = row.stars;
    if (row.bonus) {
      // count up a star per step reached; the label follows the step, and each star re-pops
      const k = row.bonus.times.filter((at) => e >= at).length;
      if (k > 0) {
        label = row.bonus.labels[k - 1];
        age = e - row.bonus.times[k - 1];
      }
      stars = k;
    }
    // mobile's big scale-2 text is as tall as the scale-3 total, so it sits at the same y
    if (row.total !== undefined) {
      ui.text(label, lx, isMobile ? y + 1 : y + 7, C.ink, { scale: 2 });
      this.scaled(ui, pop(age / POP_T), rx - 12, y + 10, () => {
        ui.text(`${row.total}`, rx - 28, y, STAR_INK, { align: 'right', scale: 3 });
        ui.image('assets/ui/icon_star24.png', rx - 24, y - 2);
      });
      ui.ctx.restore();
      return;
    }
    // the label centred on the scale-2 numbers
    ui.text(label, lx, y + Math.round((ui.font.cap(2) - ui.font.cap()) / 2), faded ? C.muted : C.inkSoft);
    if (row.money) {
      const m = row.money;
      const p = m.dur === 0 ? 1 : Math.min(1, age / m.dur);
      const eased = 1 - (1 - p) ** 2;
      const v = Math.round(m.value * eased);
      const color = m.plus ? C.green : ink;
      const s = pop(age / POP_T);
      this.scaled(ui, s, rx, y + 7, () => ui.text(`${m.plus ? '+' : ''}$${v}`, rx, y, color, { align: 'right', scale: 2 }));
    } else if (stars !== undefined) {
      const s = faded ? 1 : pop(age / POP_T);
      const text = `+${stars}`;
      this.scaled(ui, s, rx - 8, y + 7, () => {
        ui.text(text, rx - 20, y, faded ? C.muted : STAR_INK, { align: 'right', scale: 2 });
        if (faded) ui.ctx.globalAlpha *= 0.4;
        ui.image('assets/ui/icon_star16.png', rx - 16, y - 2 + Math.round((ui.font.cap(2) - 14) / 2));
      });
    }
    ui.ctx.restore();
  }

  /** Draw with a scale about (cx, cy). */
  private scaled(ui: Ui, s: number, cx: number, cy: number, draw: () => void): void {
    if (s <= 0.01) return;
    const ctx = ui.ctx;
    ctx.save();
    ctx.translate(cx, cy);
    ctx.scale(s, s);
    ctx.translate(-cx, -cy);
    draw();
    ctx.restore();
  }

  /** The row sounds: a tick while money counts up, a chime per star row. */
  private playSounds(e: number): void {
    if (this.skipped) return;
    const play = (n: SfxName) => this.app.sfx.play(n);
    for (const row of this.rows) {
      if (e < row.at || row.missed) continue;
      if (row.bonus) {
        const k = row.bonus.times.filter((at) => e >= at).length;
        if (k > this.bonusSounded) {
          this.bonusSounded = k;
          play('star');
        }
        continue;
      }
      if (!this.sounded.has(row)) {
        this.sounded.add(row);
        if (row.stars !== undefined) play('star');
        else if (row.total !== undefined) play('quota');
        else if (row.rule) play('sell');
      }
      const m = row.money;
      if (m && m.dur > 0 && e < row.at + m.dur && e - this.lastTick >= 0.07) {
        this.lastTick = e;
        play('tick');
      }
    }
  }
}
