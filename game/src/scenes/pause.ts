import type { App, Scene } from '../app';
import { seedLabel } from '../engine/rng';
import { H, W } from '../engine/screen';
import { C, type Ui } from '../engine/ui';
import { Confirm } from './common';
import { MainMenu } from './mainMenu';

export class PauseMenu implements Scene {
  constructor(private app: App) {}

  frame(ui: Ui): void {
    const { app } = this;
    ui.dim(0.6);
    const w = 240;
    const h = 224;
    const r = { x: (W - w) / 2, y: (H - h) / 2, w, h };
    ui.nine('panel', r);
    ui.text('Paused', W / 2, r.y + 16, C.ink, { align: 'center', scale: 2 });

    const bx = r.x + 30;
    const bw = w - 60;
    let y = r.y + 44;
    if (ui.button({ x: bx, y, w: bw, h: 26 }, 'Resume') || ui.key('Escape')) {
      app.pop(this);
      return;
    }
    y += 34;
    if (ui.button({ x: bx, y, w: bw, h: 26 }, `Sound: ${app.sfx.muted ? 'Off' : 'On'}`)) {
      app.sfx.muted = !app.sfx.muted;
    }
    y += 34;
    if (ui.button({ x: bx, y, w: bw, h: 26 }, 'Save & Quit to Title')) {
      app.save();
      app.run = null;
      app.goto(new MainMenu(app));
      return;
    }
    y += 34;
    if (ui.button({ x: bx, y, w: bw, h: 26 }, 'Abandon Run')) {
      app.push(
        new Confirm(app, 'Abandon run?', 'This run will be gone for good.', 'Abandon', () => {
          app.endRun();
          app.goto(new MainMenu(app));
        }),
      );
    }
    if (app.run) ui.text(`Seed ${seedLabel(app.run.seed)}`, W / 2, r.y + h - 22, C.inkSoft, { align: 'center' });
  }
}
