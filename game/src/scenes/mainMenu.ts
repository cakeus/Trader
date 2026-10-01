import type { App, Scene } from '../app';
import { randomSeed } from '../engine/rng';
import { H, W } from '../engine/screen';
import { C, type Ui } from '../engine/ui';
import { newRun } from '../game/run';
import { loadHighScore, loadRun } from '../game/save';
import { areasInOrder } from '../game/area';
import { Confirm, drawBackground, drawWeather } from './common';
import { LocationScene } from './location';
import { MapScene } from './map';

// goods floating around the title: home spots, and how they shy away from the cursor
const SPOTS = [
  [150, 76], [458, 70], [118, 150], [490, 146], [206, 30], [404, 26],
];
const PUSH_RADIUS = 60; // cursor starts pushing within this many px of a good's centre
const PUSH = 4800; // push strength at the cursor, fading to 0 at PUSH_RADIUS
const SPRING = 40; // pull back toward the home spot
const DAMPING = 7; // velocity decay per second
const STEP = 1 / 120;

/** Start a fresh run on a new seed and go to its map. */
export function startNewRun(app: App): void {
  app.run = newRun(app.data, randomSeed());
  app.save();
  app.sfx.play('day');
  app.goto(new MapScene(app));
}

interface Floater {
  x: number; // offset from home
  y: number;
  vx: number;
  vy: number;
}

export class MainMenu implements Scene {
  private hasSave: boolean;
  private highScore = loadHighScore();
  private floaters: Floater[] = SPOTS.map(() => ({ x: 0, y: 0, vx: 0, vy: 0 }));
  private lastT = -1;
  private acc = 0;

  constructor(private app: App) {
    const saved = loadRun();
    this.hasSave = saved !== null;
    // the saved run's area sets the scene (map, weather and music)
    app.titleArea = saved?.area ?? null;
  }

  frame(ui: Ui): void {
    const { data } = this.app;
    const area = (this.app.titleArea && data.areas[this.app.titleArea]) || areasInOrder(data)[0];
    drawBackground(ui, area.map);
    drawWeather(ui, area.weather, area);
    ui.dim(0.5);

    // goods bobbing around the title, nudged aside by the cursor
    this.stepFloaters(ui);
    const goods = Object.values(this.app.data.goods);
    SPOTS.forEach(([x, y], i) => {
      const g = goods[i % goods.length];
      const f = this.floaters[i];
      const bob = Math.sin(ui.t * 1.8 + i * 1.3) * 3;
      ui.image(g.icon, Math.round(x + f.x), Math.round(y + f.y + bob));
    });

    ui.text('Higgle', W / 2, 78, C.gold, { align: 'center', scale: 6, shadow: C.shadow });
    ui.text('a tiny trading game', W / 2, 138, C.cream, { align: 'center', shadow: C.shadow });

    const bx = W / 2 - 80;
    if (ui.button({ x: bx, y: 214, w: 160, h: 30 }, 'New Run')) this.newRun();
    if (ui.button({ x: bx, y: 254, w: 160, h: 30 }, 'Continue', { disabled: !this.hasSave })) this.continue();
    if (this.highScore !== null) {
      ui.text(`High score $${this.highScore}`, W / 2, 298, C.cream, { align: 'center', shadow: C.shadow });
    }

    ui.text('v0.1 prototype', W / 2, H - 20, C.muted, { align: 'center' });
  }

  /** Spring each good back home while the cursor pushes it away, so it slides around the cursor. */
  private stepFloaters(ui: Ui): void {
    if (this.lastT >= 0) this.acc = Math.min(this.acc + ui.t - this.lastT, 0.1);
    this.lastT = ui.t;
    const { x: mx, y: my } = ui.input;
    const hasMouse = mx >= 0 && my >= 0;
    const decay = Math.exp(-DAMPING * STEP);
    for (; this.acc >= STEP; this.acc -= STEP) {
      this.floaters.forEach((f, i) => {
        let ax = -SPRING * f.x;
        let ay = -SPRING * f.y;
        if (hasMouse) {
          let dx = SPOTS[i][0] + 16 + f.x - mx;
          let dy = SPOTS[i][1] + 16 + f.y - my;
          let d = Math.hypot(dx, dy);
          if (d < 0.5) {
            // cursor dead centre: pick a stable direction per good
            dx = Math.cos(i * 2.4);
            dy = Math.sin(i * 2.4);
            d = 1;
          }
          if (d < PUSH_RADIUS) {
            const push = PUSH * (1 - d / PUSH_RADIUS);
            ax += (dx / d) * push;
            ay += (dy / d) * push;
          }
        }
        f.vx = (f.vx + ax * STEP) * decay;
        f.vy = (f.vy + ay * STEP) * decay;
        f.x += f.vx * STEP;
        f.y += f.vy * STEP;
      });
    }
  }

  private newRun(): void {
    const start = () => startNewRun(this.app);
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
