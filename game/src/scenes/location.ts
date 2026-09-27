import type { App, Scene } from '../app';
import { H, W } from '../engine/screen';
import { C, type Rect, type Ui } from '../engine/ui';
import { CONFIG } from '../game/config';
import { actorsAt, avgPaid, endDay, offer } from '../game/run';
import type { Tier } from '../game/types';
import { Confirm, drawBackground, drawBag, drawHud, drawPortrait, HUD_H } from './common';
import { GameOver } from './gameOver';
import { MapScene } from './map';
import { QuotaResult } from './quotaResult';
import { quickTrade, TradeDialog } from './trade';

const DEAL_LABEL: Record<Tier, { text: string; color: string } | undefined> = {
  good: undefined,
  great: { text: 'Great deal', color: C.greenLight },
  amazing: { text: 'Amazing deal', color: C.cyan },
};

export const CARD_W = 108;
export const CARD_H = 104;

export class LocationScene implements Scene {
  constructor(private app: App, private locId: string) {}

  frame(ui: Ui): void {
    const { app } = this;
    const run = app.run!;
    const def = app.data.locations[this.locId];
    drawBackground(ui, def.background);

    const nw = ui.font.measure(def.name, 2) + 28;
    ui.nine('panel_dark', { x: 8, y: HUD_H + 8, w: nw, h: 32 });
    ui.text(def.name, 8 + nw / 2, HUD_H + 17, C.cream, { align: 'center', scale: 2 });

    actorsAt(run, this.locId).forEach((id, i) => {
      const actor = app.data.actors[id];
      const slot = def.slots[i];
      const base: Rect = { x: slot.x, y: slot.y, w: CARD_W, h: CARD_H };
      const hot = ui.hover(base);
      const bob = Math.round(Math.sin(ui.t * 2 + i * 1.7) * 2) - (hot ? 3 : 0);
      const r = { ...base, y: base.y + bob };

      ui.nine(hot ? 'row_hover' : 'panel', r);
      drawPortrait(ui, actor, r.x + (CARD_W - 64) / 2, r.y + 8);
      const lines = ui.font.wrap(actor.name, CARD_W - 12).slice(0, 2);
      lines.forEach((l, j) => ui.text(l, r.x + CARD_W / 2, r.y + 76 + j * 11, C.ink, { align: 'center' }));

      // role tag above the card
      const tag = actor.role === 'supplier' ? 'Seller' : 'Buyer';
      const tw = ui.font.measure(tag) + 14;
      ui.nine('panel_dark', { x: r.x + (CARD_W - tw) / 2, y: r.y - 12, w: tw, h: 18 });
      ui.text(tag, r.x + CARD_W / 2, r.y - 7, actor.role === 'supplier' ? C.greenLight : C.sky, { align: 'center' });

      if (hot) this.actorTooltip(ui, id);
      if (ui.clicked(base)) {
        if (CONFIG.quickTrade) {
          quickTrade(app, ui, id);
        } else {
          app.sfx.play('open');
          app.push(new TradeDialog(app, id));
        }
      }
    });

    drawBag(app, ui, 8, H - 56);
    if (ui.button({ x: W - 136, y: H - 50, w: 128, h: 38 }, 'End Day', { scale: 2 })) this.tryEndDay();
    drawHud(app, ui);
  }

  private actorTooltip(ui: Ui, actorId: string): void {
    const { data } = this.app;
    const run = this.app.run!;
    const a = data.actors[actorId];
    const seller = a.role === 'supplier';
    // text lines per good: name + price (+ deal label), stock/demand, avg paid (buyers)
    const rows = a.goods.map((g) => {
      const o = offer(run, actorId, g.good);
      const deal = DEAL_LABEL[o.tier];
      const lines: { text: string; color: string; suffix?: string; suffixColor?: string }[] = [
        { text: `${data.goods[g.good].name}  $${o.price}`, color: C.cream, suffix: deal?.text, suffixColor: deal?.color },
      ];
      if (CONFIG.limitStock) {
        const qty = seller ? `${o.left} in stock` : o.left > 0 ? `wants ${o.left}` : 'wants no more';
        lines.push({ text: qty, color: o.left > 0 ? C.muted : C.redLight });
      }
      const avg = seller ? null : avgPaid(run, g.good);
      if (avg !== null) {
        const shown = avg.toFixed(1).replace(/\.0$/, '');
        lines.push({ text: `Average paid: $${shown}`, color: C.gold });
      }
      return { good: g.good, lines, h: Math.max(34, lines.length * 12 + 4) };
    });

    const lineW = (l: { text: string; suffix?: string }) =>
      ui.font.measure(l.text) + (l.suffix ? ui.font.measure(`  ${l.suffix}`) : 0);
    const w = Math.max(210, 52 + Math.max(...rows.flatMap((r) => r.lines.map(lineW))));
    const h = 30 + rows.reduce((sum, r) => sum + r.h, 0);
    ui.tooltip(w, h, (x, y) => {
      ui.text(a.name, x, y, C.gold);
      ui.text(seller ? 'Sells:' : 'Buys:', x, y + 12, C.muted);
      let gy = y + 24;
      for (const r of rows) {
        ui.image(data.goods[r.good].icon, x - 2, gy);
        const ty = gy + Math.max(0, Math.floor((32 - r.lines.length * 12) / 2)) + 2;
        r.lines.forEach((l, i) => {
          ui.text(l.text, x + 36, ty + i * 12, l.color);
          if (l.suffix) ui.text(l.suffix, x + 36 + ui.font.measure(`${l.text}  `), ty + i * 12, l.suffixColor ?? C.muted);
        });
        gy += r.h;
      }
    });
  }

  private tryEndDay(): void {
    const { app } = this;
    const run = app.run!;
    if (run.day >= run.quota.dueDay && !run.quota.met && run.cash < run.quota.amount) {
      const short = run.quota.amount - run.cash;
      app.push(
        new Confirm(app, 'Last day!', `The quota is due tonight and you're $${short} short. End the day anyway?`,
          'End Day', () => this.doEndDay()),
      );
    } else {
      this.doEndDay();
    }
  }

  private doEndDay(): void {
    const { app } = this;
    const run = app.run!;
    const prev = run.quota;
    const res = endDay(app.data, run);
    if (res === 'failed') {
      app.endRun();
      app.sfx.play('fail');
      app.goto(new GameOver(app, run));
      return;
    }
    app.save();
    app.goto(new MapScene(app));
    if (res === 'quotaPassed') {
      app.sfx.play('quota');
      app.push(new QuotaResult(app, prev));
    } else {
      app.sfx.play('day');
    }
  }
}
