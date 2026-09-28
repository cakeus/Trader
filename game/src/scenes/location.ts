import type { App, Scene } from '../app';
import { H, W } from '../engine/screen';
import { C, type Rect, type Ui } from '../engine/ui';
import { CONFIG } from '../game/config';
import { describeDeal } from '../game/dealer';
import { actorsAt, avgPaid, buyoutOffer, canAct, endDay, offer } from '../game/run';
import type { Point, Quota, Role, Tier } from '../game/types';
import { BuyoutDialog } from './buyout';
import { DealerDialog } from './dealer';
import { Confirm, drawBackground, drawBag, drawHud, drawPortrait, HUD_H } from './common';
import { GameOver } from './gameOver';
import { MapScene } from './map';
import { QuotaResult } from './quotaResult';
import { AreaTransition } from './arrival';
import { quickTrade, TradeDialog } from './trade';

const DEAL_LABEL: Record<Tier, { text: string; color: string } | undefined> = {
  bad: { text: 'Bad deal', color: C.redLight },
  good: undefined,
  great: { text: 'Great deal', color: C.greenLight },
  amazing: { text: 'Amazing deal', color: C.cyan },
};

export const CARD_W = 108;
export const CARD_H = 104;
/** Seconds with nothing left to do before the End Day button starts glowing. */
const NUDGE_AFTER = 5;

export class LocationScene implements Scene {
  /** ui.t when the player last ran out of things to do here, or null if they still can act. */
  private stuckSince: number | null = null;

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
      const seller = actor.role === 'supplier';
      const base = this.card(ui, actor, def.slots[i], i, seller ? 'Seller' : 'Buyer', seller ? C.greenLight : C.sky);
      if (ui.hover(base)) this.actorTooltip(ui, id);
      if (ui.clicked(base)) {
        if (CONFIG.quickTrade) {
          quickTrade(app, ui, id);
        } else {
          app.sfx.play('open');
          app.push(new TradeDialog(app, id));
        }
      }
    });

    if (run.dealer?.locationId === this.locId) {
      // he stands in the spot an actor would have taken (days dealt before that use dealerSlot)
      const n = actorsAt(run, this.locId).length;
      const pos = n < def.actorSlots ? def.slots[n] : def.dealerSlot;
      const base = this.card(ui, app.data.dealer, pos, n, 'Stamps', C.gold);
      if (ui.hover(base)) this.dealerTooltip(ui);
      if (ui.clicked(base)) {
        app.sfx.play('open');
        app.push(new DealerDialog(app));
      }
    }

    drawBag(app, ui, 8, H - 56);
    const endBtn: Rect = { x: W - 136, y: H - 50, w: 128, h: 38 };
    if (canAct(app.data, run, this.locId)) this.stuckSince = null;
    else this.stuckSince ??= ui.t;
    if (this.stuckSince !== null && ui.t - this.stuckSince >= NUDGE_AFTER) {
      const pulse = 0.5 + 0.5 * Math.sin((ui.t - this.stuckSince - NUDGE_AFTER) * 5 - Math.PI / 2);
      endBtn.y -= Math.round(pulse);
      // soft outer halo and a brighter inner ring, both breathing with the pulse
      const glow = (g: number, alpha: number) => {
        ui.ctx.fillStyle = `rgba(255,226,120,${alpha})`;
        ui.ctx.fillRect(endBtn.x - g, endBtn.y - g + 2, endBtn.w + g * 2, endBtn.h + g * 2 - 4);
        ui.ctx.fillRect(endBtn.x - g + 2, endBtn.y - g, endBtn.w + g * 2 - 4, endBtn.h + g * 2);
      };
      glow(4 + Math.round(pulse * 4), 0.15 + 0.3 * pulse);
      glow(2 + Math.round(pulse * 1), 0.45 + 0.45 * pulse);
    }
    if (ui.button(endBtn, 'End Day', { scale: 2 })) this.tryEndDay();
    drawHud(app, ui);
  }

  /** A bobbing portrait card with a tag above it. Returns its hit rect (without the bob). */
  private card(ui: Ui, who: { portrait: string; name: string; role?: Role }, pos: Point, i: number, tag: string, tagColor: string): Rect {
    const base: Rect = { x: pos.x, y: pos.y, w: CARD_W, h: CARD_H };
    const hot = ui.hover(base);
    const bob = Math.round(Math.sin(ui.t * 2 + i * 1.7) * 2) - (hot ? 3 : 0);
    const r = { ...base, y: base.y + bob };

    ui.nine(hot ? 'row_hover' : 'panel', r);
    drawPortrait(ui, who, r.x + (CARD_W - 64) / 2, r.y + 8);
    const lines = ui.font.wrap(who.name, CARD_W - 12).slice(0, 2);
    lines.forEach((l, j) => ui.text(l, r.x + CARD_W / 2, r.y + 76 + j * 11, C.ink, { align: 'center' }));

    const tw = ui.font.measure(tag) + 14;
    ui.nine('panel_dark', { x: r.x + (CARD_W - tw) / 2, y: r.y - 12, w: tw, h: 18 });
    ui.text(tag, r.x + CARD_W / 2, r.y - 7, tagColor, { align: 'center' });
    return base;
  }

  private dealerTooltip(ui: Ui): void {
    const { data } = this.app;
    const run = this.app.run!;
    const rows = run.dealer!.offers.map((o) => ({
      title: describeDeal(data, o.deal, run.area).title,
      note: o.sold ? 'Sold' : `${o.cost} stars`,
      color: o.sold ? C.muted : run.stars < o.cost ? C.redLight : C.gold,
    }));
    const w = Math.max(200, 32 + Math.max(...rows.map((r) => ui.font.measure(`${r.title}  ${r.note}`))));
    ui.tooltip(w, 30 + rows.length * 12 + 18, (x, y) => {
      ui.text(data.dealer.name, x, y, C.gold);
      ui.text('Stamps:', x, y + 12, C.muted);
      rows.forEach((r, i) => {
        ui.text(r.title, x, y + 24 + i * 12, r.color === C.muted ? C.muted : C.cream);
        ui.text(r.note, x + w - 16, y + 24 + i * 12, r.color, { align: 'right' });
      });
      ui.text(`You have ${run.stars} stars`, x, y + 28 + rows.length * 12, C.muted);
    });
  }

  private actorTooltip(ui: Ui, actorId: string): void {
    const data = this.app.view;
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
      if (seller ? CONFIG.limitStock : CONFIG.limitDemand) {
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
    if (buyoutOffer(app.data, run) !== null) {
      app.push(new BuyoutDialog(app, () => this.doEndDay()));
    } else if (run.day >= run.quota.dueDay && !run.quota.met && run.cash < run.quota.amount) {
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
    const prevArea = run.area;
    const res = endDay(app.data, run);
    if (res === 'failed') {
      app.endRun();
      app.sfx.play('fail');
      app.goto(new GameOver(app, run));
      return;
    }
    showDayEnd(app, res === 'quotaPassed' ? prev : null, prevArea);
  }
}

/** After ending the day (or days): save, then go to the new day's map, with the quota result
 *  when `passed` ended, or to the area transition when the run moved from `prevArea`. */
export function showDayEnd(app: App, passed: Quota | null, prevArea: string): void {
  app.save();
  if (app.run!.area !== prevArea) {
    // the quota result plays over the old area, then the move to the new one
    app.sfx.play('quota');
    app.goto(new AreaTransition(app, prevArea, passed));
    return;
  }
  app.goto(new MapScene(app));
  if (passed) {
    app.sfx.play('quota');
    app.push(new QuotaResult(app, passed));
  } else {
    app.sfx.play('day');
  }
}
