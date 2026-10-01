import type { App, Scene } from '../app';
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
    ui.text(`but ended the week with $${run.cash}.`, cx, r.y + 76, C.ink, { align: 'center' });
    const y = drawRunStats(ui, run, cx, r.y + 104);
    ui.text(`Seed ${seedLabel(run.seed)}`, cx, y + 12, C.muted, { align: 'center' });
    endStamps(this.app, ui, run, r);
    endButtons(this.app, ui, r.y + r.h - 40);
  }
}

/** Where the end screens' left column (the run's result and stats) is centred, from the panel's left. */
export const END_LEFT = 165;

/** The end screens' panel, centred. */
export function endPanel(ui: Ui): Rect {
  const w = 600;
  const h = 300;
  const r = { x: (W - w) / 2, y: (H - h) / 2, w, h };
  ui.nine('panel', r);
  return r;
}

/** The run's stamps at the bottom right of an end screen's panel, above the buttons. */
export function endStamps(app: App, ui: Ui, run: RunState, r: Rect): void {
  drawRunStamps(app, ui, run, r.x + r.w - 20, r.y + r.h - 50, 6, 4);
}

/** Play Again and Main Menu, side by side at `y` (Enter goes to the menu). */
export function endButtons(app: App, ui: Ui, y: number): void {
  if (ui.button({ x: W / 2 - 145, y, w: 140, h: 26 }, 'Play Again')) {
    startNewRun(app);
  } else if (ui.button({ x: W / 2 + 5, y, w: 140, h: 26 }, 'Main Menu') || ui.key('Enter')) {
    app.goto(new MainMenu(app));
  }
}
