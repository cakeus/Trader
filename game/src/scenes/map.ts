import type { App, Scene } from '../app';
import { H, W } from '../engine/screen';
import { C, type Rect, type TipAction, type Ui } from '../engine/ui';
import { owns } from '../game/dealer';
import { todayEvent, weatherOn } from '../game/events';
import { buyPrice, nextSellPrice, offer, visit } from '../game/run';
import type { Role, Tier } from '../game/types';
import { AreaTransition } from './arrival';
import { drawBackground, drawBag, drawHud, drawWeather } from './common';
import { EventNotice } from './event';
import { LocationScene } from './location';

/** Seconds the map must be on top (so the weather's been seen) before a new event's notice. */
const EVENT_NOTICE_DELAY = 1.5;

/** Bird's Eye price colors by deal tier. */
const TIER_COLOR: Record<Tier, string> = { bad: C.redLight, good: C.cream, great: C.greenLight, amazing: C.cyan };

export class MapScene implements Scene {
  /** Seconds this map has been the top scene. */
  private watched = 0;

  constructor(private app: App) {}

  frame(ui: Ui, dt: number): void {
    const { app } = this;
    const run = app.run!;
    // a save continued mid-move: play the arrival (its title, then the AreaArrival popup)
    if (run.moved && app.scenes.length === 1) {
      app.scenes = [new AreaTransition(app, null)];
      return;
    }
    const area = app.data.areas[run.area];
    drawBackground(ui, area.map);
    drawWeather(ui, weatherOn(app.data, run.area, run.day), area);
    this.eventNotice(ui, dt);

    for (const loc of run.locations) {
      const def = app.data.locations[loc.id];
      const { x, y } = def.mapPos;
      const lw = ui.font.measure(def.name) + 18;
      const label: Rect = { x: Math.round(x - lw / 2), y: y + 4, w: lw, h: 22 };
      const hit: Rect = { x: label.x, y: y - 20, w: lw, h: 46 };
      const hot = ui.focus(`loc:${loc.id}`, hit);
      // left on a Detour: it can't be visited again today
      const left = run.detoured === loc.id;
      const bob = hot && !left ? -Math.round(Math.abs(Math.sin(ui.t * 6)) * 3) : 0;

      if (left) ui.ctx.globalAlpha = 0.5;
      ui.image('assets/ui/icon_pin.png', x - 8, y - 17 + bob);
      ui.nine(hot && !left ? 'row_hover' : 'panel', label);
      ui.text(def.name, x, label.y + 7, left ? C.inkSoft : C.ink, { align: 'center' });
      // snowed in (Blizzard): a lumpy cap of snow on the label
      if (run.snowedAt === loc.id) {
        const { ctx } = ui;
        // frosted over, under a lumpy cap of snow with a blue shadow so it shows on the snowy map
        ctx.fillStyle = 'rgba(225,235,255,0.55)';
        ctx.fillRect(label.x + 1, label.y + 1, label.w - 2, label.h - 2);
        ctx.fillStyle = '#8898c8';
        ctx.fillRect(label.x + 1, label.y + 3, label.w - 2, 1);
        for (let sx = label.x + 5; sx < label.x + label.w - 8; sx += 9) ctx.fillRect(sx, label.y + 4, 3, 2);
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(label.x, label.y - 1, label.w, 4);
        for (let sx = label.x + 3; sx < label.x + label.w - 7; sx += 9) ctx.fillRect(sx, label.y - 3, 5, 2);
        for (let sx = label.x + 5; sx < label.x + label.w - 8; sx += 9) ctx.fillRect(sx, label.y + 3, 3, 1);
      }
      ui.ctx.globalAlpha = 1;

      const go = () => {
        visit(app.data, run, loc.id);
        app.save();
        app.sfx.play('open');
        app.goto(new LocationScene(app, loc.id));
      };
      if (hot) this.locationTooltip(ui, loc.id, loc.actorIds, left ? [] : [{ label: 'Go', onClick: go }]);
      if (!left && ui.activated(hit)) {
        go();
        return;
      }
    }

    const prompt = `Day ${run.day}`;
    const pw = ui.font.measure(prompt, 2) + 32;
    ui.nine('panel_dark', { x: W - pw - 8, y: H - 44, w: pw, h: 36 });
    ui.text(prompt, W - pw / 2 - 8, H - 33, C.cream, { align: 'center', scale: 2 });

    drawBag(app, ui, 8, H - 56);
    drawHud(app, ui);
  }

  /** The first morning of an event: once the map has been on top for a moment, explain it. */
  private eventNotice(ui: Ui, dt: number): void {
    const { app } = this;
    const run = app.run!;
    if (ui.active) this.watched += dt;
    const event = todayEvent(app.data, run);
    if (!event || run.eventsSeen?.includes(event.id) || this.watched < EVENT_NOTICE_DELAY) return;
    run.eventsSeen = [...(run.eventsSeen ?? []), event.id];
    app.save();
    app.push(new EventNotice(app, event));
  }

  private locationTooltip(ui: Ui, locId: string, actorIds: string[], actions: TipAction[]): void {
    const data = this.app.view;
    const run = this.app.run!;
    const def = data.locations[locId];
    // snowed in (Blizzard): nothing about who's here shows until you go
    const snowed = run.snowedAt === locId;
    // goods traded here, from the player's point of view (one actor per good at a location)
    const goodsFor = (role: Role) =>
      (snowed ? [] : actorIds)
        .filter((id) => data.actors[id].role === role)
        .flatMap((id) => data.actors[id].goods.map((g) => ({ actorId: id, good: g.good })));
    const cols = [
      { label: 'Buys', color: C.sky, role: 'buyer' as Role, goods: goodsFor('buyer') },
      { label: 'Sells', color: C.greenLight, role: 'supplier' as Role, goods: goodsFor('supplier') },
    ].filter((c) => c.goods.length > 0);
    const dealer = !snowed && run.dealer?.locationId === locId;
    // Bird's Eye: today's price under each good, colored by its deal
    const prices = owns(run, { kind: 'birdsEye' });
    const notes = [
      ...(run.detoured === locId ? [{ text: 'Visited today', color: C.redLight }] : []),
      ...(snowed ? [{ text: 'Snowed in! Go and see', color: C.sky }] : []),
      ...(run.packedAt === locId && !snowed ? [{ text: 'Packed house! +1 trader', color: C.cyan }] : []),
      ...(run.bustlingAt === locId ? [{ text: 'Bustling! Better prices', color: C.festive }] : []),
    ];

    const w = 165;
    const blurb = ui.font.wrap(def.blurb, w - 16);
    const lh = ui.font.lineHeight;
    const goodsH = cols.length > 0 ? 34 + (prices ? 10 : 0) : 0;
    const h = 14 + lh + blurb.length * lh + 6 + goodsH + (dealer ? 14 : 0) + notes.length * 12 + 4;
    ui.tooltip(w, h, (x, y) => {
      ui.text(def.name, x, y, C.gold);
      blurb.forEach((l, i) => ui.text(l, x, y + lh + i * lh, C.muted));
      let ry = y + lh + blurb.length * lh + 6;
      // one column per side, label centred above its row of 16x16 icons
      const colW = (w - 16) / cols.length;
      cols.forEach((c, i) => {
        const cx = x + colW * (i + 0.5);
        ui.text(c.label, cx, ry, c.color, { align: 'center' });
        const pitch = prices ? 22 : 18;
        const iw = c.goods.length * pitch - (pitch - 16);
        c.goods.forEach((g, j) => {
          const gx = cx - iw / 2 + j * pitch;
          ui.image(data.goods[g.good].iconMedium, gx, ry + 12);
          if (!prices) return;
          const o = offer(run, g.actorId, g.good);
          const p = c.role === 'supplier' ? buyPrice(run, o) : nextSellPrice(run, o, g.good);
          ui.text(`$${p}`, gx + 8, ry + 30, TIER_COLOR[o.tier], { align: 'center' });
        });
      });
      ry += goodsH;
      if (dealer) {
        ui.image('assets/ui/icon_star.png', x - 2, ry - 2);
        ui.text(`${data.dealer.name} is here!`, x + 16, ry + 2, C.gold);
        ry += 14;
      }
      notes.forEach((n, i) => ui.text(n.text, x, ry + 2 + i * 12, n.color));
    }, actions);
  }
}
