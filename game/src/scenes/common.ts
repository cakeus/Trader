import type { App, Scene } from '../app';
import { H, W } from '../engine/screen';
import { C, type Rect, type Ui } from '../engine/ui';
import { daysLeft } from '../game/run';
import type { ActorDef, Role } from '../game/types';
import { PauseMenu } from './pause';

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

export function drawPortrait(ui: Ui, actor: Pick<ActorDef, 'portrait' | 'name'> & { role?: Role }, x: number, y: number): void {
  if (ui.image(actor.portrait, x, y)) return;
  ui.ctx.fillStyle = actor.role === 'supplier' ? '#8ecf8a' : actor.role === 'buyer' ? '#8ab8e8' : '#e8c86a';
  ui.ctx.fillRect(x, y, 64, 64);
  ui.text(actor.name[0], x + 32, y + 18, C.ink, { align: 'center', scale: 4 });
}

/** Top bar: day, cash, bag, stars, quota, and the Menu button (Esc also opens it). */
export function drawHud(app: App, ui: Ui): void {
  const run = app.run!;
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
    ui.nine(item && ui.hover(r) ? 'row_hover' : 'row', r);
    if (!item) {
      ui.ctx.fillStyle = 'rgba(74,46,62,0.12)';
      ui.ctx.fillRect(r.x + 3, r.y + 3, r.w - 6, r.h - 6);
      continue;
    }
    const def = app.data.goods[item.good];
    ui.image(def.icon, r.x + 1, r.y + 1);
    if (ui.hover(r)) {
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
