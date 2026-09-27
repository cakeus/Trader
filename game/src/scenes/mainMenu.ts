import type { App, Scene } from '../app';
import { randomSeed } from '../engine/rng';
import { H, W } from '../engine/screen';
import { C, type Ui } from '../engine/ui';
import { newRun } from '../game/run';
import { loadRun } from '../game/save';
import { Confirm, drawBackground } from './common';
import { LocationScene } from './location';
import { MapScene } from './map';

export class MainMenu implements Scene {
  private hasSave: boolean;

  constructor(private app: App) {
    this.hasSave = loadRun() !== null;
  }

  frame(ui: Ui): void {
    drawBackground(ui, 'assets/bg/map.png');
    ui.dim(0.5);

    // goods bobbing around the title
    const goods = Object.values(this.app.data.goods);
    const spots = [
      [150, 76], [458, 70], [118, 150], [490, 146], [206, 30], [404, 26],
    ];
    spots.forEach(([x, y], i) => {
      const g = goods[i % goods.length];
      ui.image(g.icon, x, y + Math.round(Math.sin(ui.t * 1.8 + i * 1.3) * 3));
    });

    ui.text('Trader', W / 2, 78, C.gold, { align: 'center', scale: 6, shadow: C.shadow });
    ui.text('a tiny trading roguelike', W / 2, 138, C.cream, { align: 'center', shadow: C.shadow });

    const bx = W / 2 - 80;
    if (ui.button({ x: bx, y: 214, w: 160, h: 30 }, 'New Run')) this.newRun();
    if (ui.button({ x: bx, y: 254, w: 160, h: 30 }, 'Continue', { disabled: !this.hasSave })) this.continue();

    ui.text('v0.1 prototype', W / 2, H - 20, C.muted, { align: 'center' });
  }

  private newRun(): void {
    const start = () => {
      const app = this.app;
      app.run = newRun(app.data, randomSeed());
      app.save();
      app.sfx.play('day');
      app.goto(new MapScene(app));
    };
    if (this.hasSave) {
      this.app.push(new Confirm(this.app, 'Start fresh?', 'Your current run will be lost.', 'New Run', start));
    } else {
      start();
    }
  }

  private continue(): void {
    const app = this.app;
    app.run = loadRun();
    if (!app.run) return;
    app.goto(app.run.visited ? new LocationScene(app, app.run.visited) : new MapScene(app));
  }
}
