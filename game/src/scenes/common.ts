import type { App, Scene } from '../app';
import { H, W } from '../engine/screen';
import { C, type Rect, type Ui } from '../engine/ui';
import { daysLeft } from '../game/run';
import type { ActorDef, Role, RunState, Weather, WeatherSpots } from '../game/types';
import { PauseMenu } from './pause';
import { StampsDialog } from './stamps';

export const HUD_H = 30;
/** Star gold that still reads on the paper panel. */
export const STAR_INK = '#b8761c';

export function drawBackground(ui: Ui, path: string): void {
  if (ui.image(path, 0, 0)) return;
  const g = ui.ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, '#8fd0e8');
  g.addColorStop(1, '#f5d8b0');
  ui.ctx.fillStyle = g;
  ui.ctx.fillRect(0, 0, W, H);
}

const SNOW_FLAKES = 540;
/** How far the flake count swings above and below `SNOW_FLAKES` over time. */
const SNOW_GUST = 0.29;
/** Flakes near the current count fade in and out over this many indices instead of popping. */
const SNOW_FADE = 40;
/** The Blizzard's snow: this many times the flakes, falling this many times as fast. */
const BLIZZARD_DENSITY = 5;
const BLIZZARD_SPEED = 3;

/** Falling pixel snow (`density` times the flakes, `pace` times as fast). Stateless: each flake's
 *  position is a function of its index and `ui.t`. */
export function drawSnow(ui: Ui, density = 1, pace = 1): void {
  const { ctx } = ui;
  const flakes = SNOW_FLAKES * density;
  // slow, irregular gusts: two out-of-step waves, together in -1..1
  const gust = 0.7 * Math.sin((ui.t * Math.PI * 2) / 37) + 0.3 * Math.sin((ui.t * Math.PI * 2) / 13 + 1.7);
  const count = flakes * (1 + SNOW_GUST * gust);
  const max = Math.ceil(flakes * (1 + SNOW_GUST));
  for (let i = 0; i < max; i++) {
    const vis = Math.min(1, (count - i) / SNOW_FADE);
    if (vis <= 0) break;
    // cheap per-flake hashes in 0..1
    const r1 = (Math.sin(i * 12.9898) * 43758.5453) % 1;
    const r2 = (Math.sin(i * 78.233) * 12543.917) % 1;
    const r3 = (Math.sin(i * 39.425) * 24634.634) % 1;
    const a = Math.abs(r1), b = Math.abs(r2), c = Math.abs(r3);
    // three depth layers: far flakes are small and slow
    const layer = i % 3;
    const size = layer === 2 ? 2 : 1;
    const speed = (14 + layer * 10 + c * 8) * pace;
    const drift = 6 + layer * 4;
    const y = ((b * (H + 20) + ui.t * speed) % (H + 20)) - 10;
    const x = (((a * W + Math.sin(ui.t * (0.6 + c * 0.6) * pace + i) * drift - ui.t * 4 * pace) % W) + W) % W;
    const fx = Math.round(x), fy = Math.round(y);
    ctx.globalAlpha = vis;
    // the big near flakes get a faint 1px shadow below so they read against pale snow
    if (layer === 2) {
      ctx.fillStyle = 'rgba(80,92,150,0.2)';
      ctx.fillRect(fx, fy + size, size, 1);
    }
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(fx, fy, size, size);
  }
  ctx.globalAlpha = 1;
}

const RAIN_DROPS = 300;
/** How far the drop count swings above and below `RAIN_DROPS` over time. */
const RAIN_GUST = 0.25;
const RAIN_SPLASHES = 36;

/** A cheap hash of two numbers in 0..1. */
function hash(i: number, k: number): number {
  return Math.abs((Math.sin(i * 12.9898 + k * 78.233) * 43758.5453) % 1);
}

/** A stormy tint and slanted pixel rain, with little splashes on the ground. Stateless like
 *  `drawSnow`: each drop's position is a function of its index and `ui.t`. */
export function drawRain(ui: Ui): void {
  const { ctx } = ui;
  ui.dim(0.14, '40,52,84');
  const gust = 0.6 * Math.sin((ui.t * Math.PI * 2) / 29) + 0.4 * Math.sin((ui.t * Math.PI * 2) / 11 + 0.9);
  const count = RAIN_DROPS * (1 + RAIN_GUST * gust);
  const span = H + 30;
  ctx.fillStyle = '#dce8ff';
  for (let i = 0; i < count; i++) {
    const a = hash(i, 1), b = hash(i, 2), c = hash(i, 3);
    // three depth layers: far drops are short, faint and slower
    const layer = i % 3;
    const segs = layer + 1; // 3px segments, each stepping 1px across
    const speed = 250 + layer * 90 + c * 60;
    const fall = (b * span + ui.t * speed) % span;
    const y = Math.round(fall) - 10;
    // the wind slants every drop 1px across per 3px down
    const x = Math.round((((a * W + fall / 3) % W) + W) % W);
    ctx.globalAlpha = (0.22 + layer * 0.18) * Math.min(1, count - i);
    for (let j = 0; j < segs; j++) ctx.fillRect(x - j, y - 3 * j - 2, 1, 3);
  }
  // splashes: each flicks up at a fresh spot on the lower half of the screen once per cycle
  for (let i = 0; i < RAIN_SPLASHES; i++) {
    const period = 0.5 + hash(i, 4) * 0.7;
    const cyc = ui.t / period + hash(i, 5);
    const age = (cyc % 1) * period;
    if (age > 0.14) continue;
    const n = Math.floor(cyc);
    const x = Math.round(hash(i, n + 6) * W);
    const y = Math.round(H * 0.4 + hash(i, n + 7) * H * 0.6);
    ctx.globalAlpha = 0.55 * (1 - age / 0.14);
    if (age < 0.05) {
      ctx.fillRect(x, y, 1, 1);
    } else {
      ctx.fillRect(x - 1, y - 1, 1, 1);
      ctx.fillRect(x + 1, y - 1, 1, 1);
      ctx.fillRect(x - 2, y, 1, 1);
      ctx.fillRect(x + 2, y, 1, 1);
    }
  }
  ctx.globalAlpha = 1;
}

const LANTERN_MOTES = 90;
const MOTE_COLORS = ['#ffe3a8', '#ffe3a8', '#ffb45e', '#ffb45e', '#ff7a5c'];

/** Stars baked into the background brighten now and then, each on its own slow cycle; a few get a
 *  1px cross flare at their peak. */
function drawTwinkles(ui: Ui, stars: [number, number][]): void {
  const { ctx } = ui;
  ctx.fillStyle = '#fff4d6';
  stars.forEach(([x, y], i) => {
    const period = 4 + hash(i, 21) * 6;
    const phase = ((ui.t / period + hash(i, 22)) % 1) * Math.PI * 2;
    const v = Math.max(0, Math.sin(phase)) ** 6;
    if (v < 0.03) return;
    ctx.globalAlpha = 0.9 * v;
    ctx.fillRect(x, y, 1, 1);
    if (v > 0.6 && hash(i, 23) < 0.3) {
      ctx.globalAlpha = ((v - 0.6) / 0.4) * 0.55;
      ctx.fillRect(x - 1, y, 1, 1);
      ctx.fillRect(x + 1, y, 1, 1);
      ctx.fillRect(x, y - 1, 1, 1);
      ctx.fillRect(x, y + 1, 1, 1);
    }
  });
  ctx.globalAlpha = 1;
}

/** Warm lantern motes drifting slowly up and swaying, each pulsing gently; a few have a faint halo. */
function drawMotes(ui: Ui): void {
  const { ctx } = ui;
  const span = H + 20;
  for (let i = 0; i < LANTERN_MOTES; i++) {
    const a = hash(i, 11), b = hash(i, 12), c = hash(i, 13);
    const speed = 5 + c * 9;
    const y = Math.round(H + 10 - ((b * span + ui.t * speed) % span));
    const x = Math.round((((a * W + Math.sin(ui.t * (0.4 + c * 0.5) + i) * 7) % W) + W) % W);
    const pulse = 0.5 + 0.5 * Math.sin(ui.t * (0.8 + c * 1.2) + i * 2.1);
    const alpha = 0.18 + 0.4 * pulse;
    ctx.fillStyle = MOTE_COLORS[i % MOTE_COLORS.length];
    if (i % 7 === 0) {
      ctx.globalAlpha = alpha * 0.25;
      ctx.fillRect(x - 1, y - 1, 3, 3);
    }
    ctx.globalAlpha = alpha;
    ctx.fillRect(x, y, 1, 1);
  }
  ctx.globalAlpha = 1;
}

/** Fireflies wandering over greenery: each fades in, glows a moment, fades out, then stays dark a while. */
function drawFireflies(ui: Ui, r: NonNullable<WeatherSpots['fireflies']>): void {
  const { ctx } = ui;
  const n = Math.max(6, Math.min(24, Math.round((r.w * r.h) / 1500)));
  for (let i = 0; i < n; i++) {
    const a = hash(i, 31), b = hash(i, 32), c = hash(i, 33);
    const period = 3 + c * 3;
    const f = (ui.t / period + hash(i, 34)) % 1;
    const v = f < 0.15 ? f / 0.15 : f < 0.45 ? 1 : f < 0.6 ? 1 - (f - 0.45) / 0.15 : 0;
    if (v <= 0) continue;
    const x = Math.round(r.x + a * r.w + Math.sin(ui.t * (0.2 + 0.2 * c) + i) * 10);
    const y = Math.round(r.y + b * r.h + Math.cos(ui.t * (0.17 + 0.15 * c) + i * 1.3) * 6);
    ctx.fillStyle = '#b8e05a';
    ctx.globalAlpha = 0.22 * v;
    ctx.fillRect(x - 1, y - 1, 3, 3);
    ctx.fillStyle = '#e4f78a';
    ctx.globalAlpha = 0.95 * v;
    ctx.fillRect(x, y, 1, 1);
  }
  ctx.globalAlpha = 1;
}

/** Lantern Crossing's night: twinkling stars, drifting lantern light, and fireflies where there's greenery. */
export function drawLanterns(ui: Ui, spots?: WeatherSpots): void {
  if (spots?.starPoints) drawTwinkles(ui, spots.starPoints);
  drawMotes(ui);
  if (spots?.fireflies) drawFireflies(ui, spots.fireflies);
}

const FIREWORK_SLOTS = 3;
const FIREWORK_SPARKS = 26;
const FIREWORK_COLORS = ['#ff8a7a', '#ffd24a', '#8fe0ff', '#b8f07a', '#ffb0e0', '#ffe8b0'];
/** Seconds a shell takes to rise, and its sparks to spread and fade. */
const SHELL_RISE = 0.6;
const SPARK_LIFE = 1.8;

/** Occasional firework bursts high in the sky: a shell rises, then 1px sparks spread out, fall a
 *  little and fade. Stateless, like the other weather. */
function drawFireworkBursts(ui: Ui): void {
  const { ctx } = ui;
  for (let k = 0; k < FIREWORK_SLOTS; k++) {
    const period = 4.5 + hash(k, 41) * 3;
    const cyc = ui.t / period + hash(k, 42);
    const n = Math.floor(cyc);
    // some cycles stay dark, so the bursts don't come like clockwork
    if (hash(k * 97 + n, 43) < 0.3) continue;
    const age = (cyc % 1) * period;
    if (age > SHELL_RISE + SPARK_LIFE) continue;
    const cx = 60 + hash(k * 97 + n, 44) * (W - 120);
    const cy = 52 + hash(k * 97 + n, 45) * 100;
    const color = FIREWORK_COLORS[Math.floor(hash(k * 97 + n, 46) * FIREWORK_COLORS.length)];
    ctx.fillStyle = color;
    if (age < SHELL_RISE) {
      const p = age / SHELL_RISE;
      ctx.globalAlpha = 0.8;
      ctx.fillRect(Math.round(cx), Math.round(cy + 70 * (1 - p * (2 - p))), 1, 2);
      continue;
    }
    const s = age - SHELL_RISE;
    const spread = (1 - Math.exp(-s * 2.4)) / 2.4;
    const speed = 36 + hash(k * 97 + n, 47) * 16;
    ctx.globalAlpha = Math.max(0, 1 - s / SPARK_LIFE) * 0.9;
    for (let j = 0; j < FIREWORK_SPARKS; j++) {
      const ang = (j / FIREWORK_SPARKS) * Math.PI * 2 + hash(j, n) * 0.2;
      const d = speed * spread * (0.8 + 0.2 * hash(j, n + 1));
      ctx.fillRect(Math.round(cx + Math.cos(ang) * d), Math.round(cy + Math.sin(ang) * d + 10 * s * s), 1, 1);
    }
    // a bright flash in the middle as it bursts
    if (s < 0.15) {
      ctx.globalAlpha = 1 - s / 0.15;
      ctx.fillStyle = '#fff4e4';
      ctx.fillRect(Math.round(cx) - 1, Math.round(cy) - 1, 3, 3);
    }
  }
  ctx.globalAlpha = 1;
}

/** Fireworks Night: the lantern night, with firework bursts in the sky above it. */
export function drawFireworks(ui: Ui, spots?: WeatherSpots): void {
  if (spots?.starPoints) drawTwinkles(ui, spots.starPoints);
  drawFireworkBursts(ui);
  drawMotes(ui);
  if (spots?.fireflies) drawFireflies(ui, spots.fireflies);
}

/** Draw an area's (or today's event's) weather, if any. `spots` is where it's drawn (the area on
 *  the map, or the location): its stars and fireflies. */
export function drawWeather(ui: Ui, weather: Weather | undefined, spots?: WeatherSpots): void {
  if (weather === 'snow') drawSnow(ui);
  else if (weather === 'blizzard') drawSnow(ui, BLIZZARD_DENSITY, BLIZZARD_SPEED);
  else if (weather === 'rain') drawRain(ui);
  else if (weather === 'lanterns') drawLanterns(ui, spots);
  else if (weather === 'fireworks') drawFireworks(ui, spots);
}

export function drawPortrait(ui: Ui, actor: Pick<ActorDef, 'portrait' | 'name'> & { role?: Role }, x: number, y: number): void {
  if (ui.image(actor.portrait, x, y)) return;
  ui.ctx.fillStyle = actor.role === 'supplier' ? '#8ecf8a' : actor.role === 'buyer' ? '#8ab8e8' : '#e8c86a';
  ui.ctx.fillRect(x, y, 64, 64);
  ui.text(actor.name[0], x + 32, y + 18, C.ink, { align: 'center', scale: 4 });
}

/** Top bar: day, cash, bag, stars, quota, and the Stamps and Menu buttons (Esc also opens the menu).
 *  Also plays the "Last Day!" announcement once on an unmet quota's due day. */
export function drawHud(app: App, ui: Ui): void {
  const run = app.run!;
  const key = `${run.seed}:${run.day}`;
  if (run.day === run.quota.dueDay && !run.quota.met && app.announced !== key) {
    app.announced = key;
    ui.announce('Last Day!');
    app.sfx.play('lastDay');
  }
  ui.nine('panel_dark', { x: -8, y: -8, w: W + 16, h: HUD_H + 8 });
  const ty = 11;
  ui.image('assets/ui/icon_calendar.png', 8, 6);
  ui.text(`Day ${run.day}`, 28, ty, C.cream);
  ui.image('assets/ui/icon_coin.png', 88, 6);
  ui.text(`$${run.cash}`, 108, ty, C.gold);
  ui.image('assets/ui/icon_bag.png', 158, 6);
  ui.text(`${run.inventory.length}/${run.capacity}`, 178, ty, C.cream);
  ui.image('assets/ui/icon_star.png', 216, 6);
  ui.text(`${run.stars}`, 236, ty, C.gold);

  const q = run.quota;
  const qx = 262;
  ui.image('assets/ui/icon_flag.png', qx, 6);
  const label = `Quota $${q.amount} by Day ${q.dueDay}`;
  ui.text(label, qx + 20, ty, C.cream);
  const sx = qx + 26 + ui.font.measure(label);
  if (q.met) {
    ui.image('assets/ui/icon_check.png', sx, 6);
    ui.text('Met!', sx + 18, ty, C.greenLight);
  } else {
    const left = daysLeft(run);
    const txt = left <= 0 ? 'due today!' : left === 1 ? '1 day left' : `${left} days left`;
    ui.text(txt, sx, ty, left <= 1 ? C.redLight : C.muted);
  }

  if (ui.button({ x: W - 134, y: 5, w: 62, h: 20 }, 'Stamps')) {
    app.sfx.play('open');
    app.push(new StampsDialog(app));
  }
  if (ui.button({ x: W - 66, y: 5, w: 60, h: 20 }, 'Menu') || ui.key('Escape')) {
    app.push(new PauseMenu(app));
  }
}

export const BAG_SLOT = 36;

/** The inventory strip (one slot per unit of capacity). */
export function drawBag(app: App, ui: Ui, x: number, y: number): void {
  const run = app.run!;
  const w = run.capacity * BAG_SLOT + 12;
  ui.nine('panel_dark', { x, y, w, h: BAG_SLOT + 12 });
  for (let i = 0; i < run.capacity; i++) {
    const r: Rect = { x: x + 6 + i * BAG_SLOT, y: y + 6, w: BAG_SLOT - 2, h: BAG_SLOT - 2 };
    const item = run.inventory[i];
    const hot = !!item && ui.focus(`bag:${i}`, r);
    ui.nine(hot ? 'row_hover' : 'row', r);
    if (!item) {
      ui.ctx.fillStyle = 'rgba(74,46,62,0.12)';
      ui.ctx.fillRect(r.x + 3, r.y + 3, r.w - 6, r.h - 6);
      continue;
    }
    const def = app.data.goods[item.good];
    ui.image(def.icon, r.x + 1, r.y + 1);
    if (hot) {
      const paid = `Paid $${item.paid} on Day ${item.day}`;
      const w2 = Math.max(ui.font.measure(def.name), ui.font.measure(paid)) + 16;
      ui.tooltip(w2, 36, (tx, ty) => {
        ui.text(def.name, tx, ty + 1, C.cream);
        ui.text(paid, tx, ty + 13, C.gold);
      });
    }
  }
}

/** Generic yes/no modal. */
export class Confirm implements Scene {
  constructor(
    private app: App,
    private title: string,
    private body: string,
    private yes: string,
    private onYes: () => void,
    private no = 'Cancel',
  ) {}

  frame(ui: Ui): void {
    ui.dim(0.55);
    const w = 320;
    const lines = ui.font.wrap(this.body, w - 40);
    const h = 96 + lines.length * ui.font.lineHeight;
    const r = { x: (W - w) / 2, y: (H - h) / 2, w, h };
    ui.nine('panel', r);
    ui.text(this.title, W / 2, r.y + 16, C.ink, { align: 'center', scale: 2 });
    lines.forEach((l, i) => ui.text(l, W / 2, r.y + 44 + i * ui.font.lineHeight, C.inkSoft, { align: 'center' }));
    const by = r.y + h - 36;
    if (ui.button({ x: W / 2 - 110, y: by, w: 100, h: 24 }, this.no) || ui.key('Escape')) this.app.pop(this);
    if (ui.button({ x: W / 2 + 10, y: by, w: 100, h: 24 }, this.yes)) {
      this.app.pop(this);
      this.onYes();
    }
  }
}

/** The run's stats as a two-column table centred on `cx`, one row per 13px from `y`. Returns
 *  the y below it. */
export function drawRunStats(ui: Ui, run: RunState, cx: number, y: number): number {
  const s = run.stats;
  const avg = s.sold > 0 ? (s.profit ?? 0) / s.sold : 0;
  const rows = [
    ['Days traded', `${run.day}`],
    ['Quotas met', `${s.quotasMet}`],
    ['Goods sold', `${s.sold}`],
    ['Avg profit', `${avg < 0 ? '-' : ''}$${Math.abs(avg).toFixed(2)}`],
    ['Total losses', `$${s.losses ?? 0}`],
    ['Best day sales', `$${s.bestDaySales ?? 0}`],
  ];
  rows.forEach(([k, v], i) => {
    ui.text(k, cx - 90, y + i * 13, C.inkSoft);
    ui.text(v, cx + 90, y + i * 13, C.ink, { align: 'right' });
  });
  return y + rows.length * 13;
}
