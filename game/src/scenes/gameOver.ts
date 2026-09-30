import type { App, Scene } from '../app';
import { seedLabel } from '../engine/rng';
import { H, W } from '../engine/screen';
import { C, type Ui } from '../engine/ui';
import type { RunState } from '../game/types';
import { drawBackground, drawRunStats } from './common';
import { MainMenu, startNewRun } from './mainMenu';

export class GameOver implements Scene {
  constructor(private app: App, private run: RunState) {}

  frame(ui: Ui): void {
    const { run } = this;
    drawBackground(ui, this.app.data.areas[run.area]?.map ?? 'assets/bg/map.png');
    ui.dim(0.7);
    const w = 380;
    const h = 250;
    const r = { x: (W - w) / 2, y: (H - h) / 2, w, h };
    ui.nine('panel', r);
    ui.text('Out of luck...', W / 2, r.y + 16, C.red, { align: 'center', scale: 3 });
    ui.text(`You needed $${run.quota.amount} by the end of Day ${run.quota.dueDay},`, W / 2, r.y + 56, C.ink, {
      align: 'center',
    });
    ui.text(`but only had $${run.cash}.`, W / 2, r.y + 68, C.ink, { align: 'center' });
    drawRunStats(ui, run, W / 2, r.y + 92);
    ui.text(`Seed ${seedLabel(run.seed)}`, W / 2, r.y + 176, C.muted, { align: 'center' });
    endButtons(this.app, ui, r.y + h - 40);
  }
}

/** Play Again and Main Menu, side by side at `y` (Enter goes to the menu). */
export function endButtons(app: App, ui: Ui, y: number): void {
  if (ui.button({ x: W / 2 - 145, y, w: 140, h: 26 }, 'Play Again')) {
    startNewRun(app);
  } else if (ui.button({ x: W / 2 + 5, y, w: 140, h: 26 }, 'Main Menu') || ui.key('Enter')) {
    app.goto(new MainMenu(app));
  }
}
