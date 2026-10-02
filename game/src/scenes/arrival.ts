import type { App, Scene } from '../app';
import { MUSIC_FADE } from '../engine/audio';
import { H, W } from '../engine/screen';
import { C, type Ui } from '../engine/ui';
import { goodOf } from '../game/area';
import { weatherOn } from '../game/events';
import { startingCash } from '../game/run';
import type { Quota } from '../game/types';
import { drawBackground, drawWeather } from './common';
import { MapScene } from './map';
import { QuotaResult } from './quotaResult';

const FADE_OUT = 0.9; // old area fading to dark
const FADE_IN = 1.2; // new area fading up from dark
const TITLE_HOLD = 3.6; // the name stays up this long after the fade-in starts (a click skips ahead)
const TITLE_OUT = 0.5; // the name fading away
const MUSIC_IN = 0.8; // the new area's music fading up

type Phase = 'quota' | 'fadeOut' | 'title';

/** The move to a new area. The quota result is shown over the old area's map, which then fades
 *  to dark; the new area's map fades up under its name in big letters, and then the map and the
 *  `AreaArrival` popup take over. Continuing a save mid-move starts at the title. */
export class AreaTransition implements Scene {
  private phase: Phase;
  private t = 0;
  private leaving = -1;

  constructor(private app: App, private from: string | null, private passed: Quota | null = null) {
    this.phase = from ? 'quota' : 'title';
    // keep the old area's music until the fade to dark
    app.musicArea = from ?? undefined;
    if (!from) this.startTitle();
  }

  private startTitle(): void {
    this.phase = 'title';
    this.t = 0;
    // the new area's music comes up quickly, with its name
    this.app.musicArea = undefined;
    this.app.musicFade = MUSIC_IN;
    this.app.sfx.play('day');
  }

  frame(ui: Ui, dt: number): void {
    const { app } = this;
    const run = app.run!;
    this.t += dt;

    if (this.phase !== 'title') {
      const old = app.data.areas[this.from!];
      drawBackground(ui, old.map);
      // the old area's weather on its last day
      drawWeather(ui, weatherOn(app.data, this.from!, run.day - 1), old);
      if (this.phase === 'quota') {
        // show the quota result on the first frame (the constructor runs before `app.goto`
        // replaces the stack), then wait for it to be closed
        if (this.passed) {
          app.push(new QuotaResult(app, this.passed));
          this.passed = null;
        } else if (ui.active) {
          this.phase = 'fadeOut';
          this.t = 0;
          // the old area's music fades out with its map
          app.musicArea = null;
          app.musicFade = FADE_OUT;
        }
        return;
      }
      ui.dim(Math.min(1, this.t / FADE_OUT), '26,20,38');
      if (this.t >= FADE_OUT) this.startTitle();
      return;
    }

    const area = app.data.areas[run.area];
    drawBackground(ui, area.map);
    drawWeather(ui, weatherOn(app.data, run.area, run.day), area);
    ui.dim(Math.max(0, 1 - this.t / FADE_IN), '26,20,38');

    if (this.leaving < 0 && (this.t >= TITLE_HOLD || (this.t > 0.6 && (ui.clicked({ x: 0, y: 0, w: W, h: H }) || ui.key('Enter')))))
      this.leaving = this.t;
    const out = this.leaving < 0 ? 1 : Math.max(0, 1 - (this.t - this.leaving) / TITLE_OUT);
    // the name fades in and rises a little, just after the map starts coming up
    const p = Math.min(1, Math.max(0, (this.t - 0.4) / 0.8));
    const alpha = p * out;
    const rise = Math.round((1 - p) * (1 - p) * 16);
    const { ctx } = ui;
    ctx.fillStyle = `rgba(20,14,32,${0.55 * alpha})`;
    ctx.fillRect(0, H / 2 - 38, W, 76);
    ctx.save();
    ctx.globalAlpha = alpha;
    const scale = 5;
    const y = H / 2 - Math.round(ui.font.cap(scale) / 2) + rise;
    for (const [dx, dy] of [[-2, 0], [2, 0], [0, -2], [0, 3], [2, 3], [-2, 3]])
      ui.text(area.name, W / 2 + dx, y + dy, C.shadow, { align: 'center', scale });
    ui.text(area.name, W / 2, y, C.gold, { align: 'center', scale });
    ctx.restore();

    if (this.leaving >= 0 && out <= 0) {
      // no fade here: the new map is already on screen
      app.musicFade = MUSIC_FADE;
      app.scenes = [new MapScene(app), new AreaArrival(app)];
    }
  }
}

/** Shown the first morning in a new area: what's traded here now (each category's old good and
 *  its new counterpart), and what the bag buyback paid. Dismissing it clears `run.moved`. */
export class AreaArrival implements Scene {
  constructor(private app: App) {}

  frame(ui: Ui): void {
    const { app } = this;
    const run = app.run!;
    const moved = run.moved;
    if (!moved) {
      app.pop(this);
      return;
    }
    const { data } = app;
    const area = data.areas[moved.area];
    const cats = Object.values(data.categories);

    ui.dim(0.55);
    const w = 380;
    const blurb = ui.font.wrap(area.blurb, w - 40);
    const h = 144 + blurb.length * 12 + cats.length * 22 + 44;
    const r = { x: (W - w) / 2, y: (H - h) / 2, w, h };
    ui.nine('panel', r);
    ui.text('Welcome to', W / 2, r.y + 14, C.inkSoft, { align: 'center' });
    ui.text(area.name, W / 2, r.y + 28, C.ink, { align: 'center', scale: 3 });
    let y = r.y + 64;
    blurb.forEach((l, i) => ui.text(l, W / 2, y + i * 12, C.inkSoft, { align: 'center' }));
    y += blurb.length * 12 + 10;

    ui.text('This area contains new items to trade.', W / 2, y, C.ink, { align: 'center' });
    y += 18;
    // one row per category: its good here
    for (const c of cats) {
      const good = data.goods[goodOf(data, c.id, area.id)];
      ui.text(c.name, r.x + 100, y + 4, C.inkSoft);
      ui.image(good.iconMedium, r.x + 180, y);
      ui.text(good.name, r.x + 200, y + 4, C.ink);
      y += 22;
    }
    y += 6;
    const bag =
      moved.units > 0
        ? `Your ${moved.units} leftover good${moved.units === 1 ? ' was' : 's were'} sold for $${moved.refund}.`
        : (area.welcome ?? 'Prices are higher here. Good luck!');
    ui.text(bag, W / 2, y, moved.units > 0 ? C.green : C.inkSoft, { align: 'center' });
    y += 16;
    ui.text(`You now start each week with $${startingCash(data, run, area.id)}.`, W / 2, y, C.ink, { align: 'center' });

    if (ui.button({ x: W / 2 - 60, y: r.y + h - 36, w: 120, h: 26 }, 'Onward!') || ui.key('Enter')) {
      run.moved = null;
      app.save();
      app.pop(this);
    }
  }
}
