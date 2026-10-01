import type { App, Scene } from '../app';
import { seedLabel } from '../engine/rng';
import { W } from '../engine/screen';
import { C, type Ui } from '../engine/ui';
import { weatherOn } from '../game/events';
import { recordHighScore } from '../game/save';
import type { RunState } from '../game/types';
import { drawBackground, drawRunStats, drawWeather } from './common';
import { END_LEFT, endButtons, endPanel, endStamps } from './gameOver';
import { QuotaResult } from './quotaResult';

/** End a won run: clear the save (so a closed tab can't come back to it), show the last quota's
 *  tally over the area's map, then on Continue the win screen. */
export function showVictory(app: App, run: RunState): void {
  app.endRun();
  app.sfx.play('quota');
  app.musicArea = run.area; // the area's music plays on through the tally
  app.goto(new FinalBackdrop(app, run));
  app.push(new QuotaResult(app, run.quota, {
    run,
    button: 'Continue',
    onDone: () => {
      app.musicArea = undefined;
      app.sfx.play('quota');
      app.goto(new Victory(app, run));
    },
  }));
}

/** The area's map and weather on the last day, under the final quota's tally. */
class FinalBackdrop implements Scene {
  constructor(private app: App, private run: RunState) {}

  frame(ui: Ui): void {
    const { app, run } = this;
    const area = app.data.areas[run.area];
    drawBackground(ui, area?.map ?? 'assets/bg/map.png');
    drawWeather(ui, weatherOn(app.data, run.area, run.day), area);
  }
}

/** The win screen: the last quota met, the final cash as the score against the high score. */
export class Victory implements Scene {
  private best: number | null;
  private isNew: boolean;

  constructor(private app: App, private run: RunState) {
    // recorded once, so the comparison stays put while the screen is up
    ({ best: this.best, isNew: this.isNew } = recordHighScore(run.cash));
  }

  frame(ui: Ui): void {
    const { run, app } = this;
    const area = app.data.areas[run.area];
    drawBackground(ui, area?.map ?? 'assets/bg/map.png');
    drawWeather(ui, weatherOn(app.data, run.area, run.day), area);
    ui.dim(0.5);
    const r = endPanel(ui);
    // the run on the left, its stamps at the bottom right
    const cx = r.x + END_LEFT;
    const bob = Math.round(Math.sin(ui.t * 4) * 2);
    ui.image('assets/ui/icon_flag.png', W / 2 - 110, r.y + 20 + bob);
    ui.image('assets/ui/icon_flag.png', W / 2 + 94, r.y + 20 - bob);
    ui.text('You win!', W / 2, r.y + 16, C.gold, { align: 'center', scale: 3 });
    ui.text(`You met every quota through Day ${run.day}.`, cx, r.y + 56, C.ink, { align: 'center' });
    ui.text(`Final cash $${run.cash}`, cx, r.y + 76, C.ink, { align: 'center', scale: 2 });
    if (this.isNew) {
      ui.text('New high score!', cx, r.y + 100 + bob, C.gold, { align: 'center', scale: 2 });
      if (this.best !== null) ui.text(`Previous best $${this.best}`, cx, r.y + 122, C.inkSoft, { align: 'center' });
    } else {
      ui.text(`High score $${this.best}`, cx, r.y + 104, C.inkSoft, { align: 'center' });
    }
    const y = drawRunStats(ui, run, cx, r.y + 144);
    ui.text(`Seed ${seedLabel(run.seed)}`, cx, y + 8, C.muted, { align: 'center' });
    endStamps(app, ui, run, r);
    endButtons(app, ui, r.y + r.h - 40);
  }
}
