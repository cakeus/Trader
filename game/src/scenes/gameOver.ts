import type { App, Scene } from '../app';
import { isMobile } from '../engine/device';
import { seedLabel } from '../engine/rng';
import { H, W } from '../engine/screen';
import { C, type Rect, type Ui } from '../engine/ui';
import type { RunState } from '../game/types';
import { drawBackground, drawRunStats } from './common';
import { MainMenu, startNewRun } from './mainMenu';
import { drawRunStamps } from './stamps';

export class GameOver implements Scene {
  constructor(private app: App, private run: RunState) {}

  frame(ui: Ui): void {
    const { run } = this;
    drawBackground(ui, this.app.data.areas[run.area]?.map ?? 'assets/bg/map.png');
    ui.dim(0.7);
    const r = endPanel(ui);
    // the run on the left, its stamps at the bottom right
    const cx = r.x + END_LEFT;
    ui.text('Out of luck...', W / 2, r.y + 16, C.red, { align: 'center', scale: 3 });
    ui.text(`You needed $${run.quota.amount} by the end of Day ${run.quota.dueDay},`, cx, r.y + 64, C.ink, {
      align: 'center',
    });
    ui.text(`but ended the week with $${run.cash}.`, cx, r.y + 64 + ui.lh, C.ink, { align: 'center' });
    const y = drawRunStats(ui, run, cx, r.y + 80 + 2 * ui.lh);
    ui.text(`Seed ${seedLabel(run.seed)}`, cx, y + ui.lh, C.muted, { align: 'center' });
    endStamps(this.app, ui, run, r);
    endButtons(this.app, ui, r);
  }
}

/** Where the end screens' left column (the run's result and stats) is centred, from the panel's left. */
export const END_LEFT = 165;

/** The end screens' panel, centred (taller on mobile, for the big font). */
export function endPanel(ui: Ui): Rect {
  const w = isMobile ? 620 : 600;
  const h = isMobile ? 350 : 300;
  const r = { x: (W - w) / 2, y: (H - h) / 2, w, h };
  ui.nine('panel', r);
  return r;
}

/** The run's stamps at the bottom right of an end screen's panel, above the buttons. */
export function endStamps(app: App, ui: Ui, run: RunState, r: Rect): void {
  drawRunStamps(app, ui, run, r.x + r.w - 20, r.y + r.h - END_FOOT - 10, 6, 4);
}

/** The buttons' height, and the band they sit in at the bottom of the panel. */
const END_BTN_H = isMobile ? 30 : 26;
const END_FOOT = END_BTN_H + 14;

/** Play Again and Main Menu, side by side at the bottom of the panel `r` (Enter goes to the menu). */
export function endButtons(app: App, ui: Ui, r: Rect): void {
  const y = r.y + r.h - END_FOOT;
  if (ui.button({ x: W / 2 - 145, y, w: 140, h: END_BTN_H }, 'Play Again')) {
    startNewRun(app);
  } else if (ui.button({ x: W / 2 + 5, y, w: 140, h: END_BTN_H }, 'Main Menu') || ui.key('Enter')) {
    app.goto(new MainMenu(app));
  }
}
