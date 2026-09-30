import type { App, Scene } from '../app';
import { H, W } from '../engine/screen';
import { C, type Rect, type TipAction, type Ui } from '../engine/ui';
import { CONFIG } from '../game/config';
import { todayEvent, weatherOn } from '../game/events';
import { owns } from '../game/dealer';
import {
  actorsAt, avgPaid, buyBlock, buyDiscountStamp, flipperBonus, buyoutOffer, buyPrice, canAct, canDetour, demandApplies, detour, endDay, endOfDayPayouts,
  fullBuyPrice, hagglerMultiplier, nextSellPrice, offer, payoutTotal, sellBlock, sellBonus,
} from '../game/run';
import type { Quota, Role, Tier } from '../game/types';
import { BuyoutDialog } from './buyout';
import { DealerDialog } from './dealer';
import { Confirm, drawBackground, drawBag, drawHud, drawPortrait, drawWeather, HUD_H } from './common';
import { GameOver } from './gameOver';
import { showVictory } from './victory';
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
    drawWeather(ui, weatherOn(app.data, run.area, run.day), def);

    const nw = ui.font.measure(def.name, 2) + 28;
    ui.nine('panel_dark', { x: 8, y: HUD_H + 8, w: nw, h: 32 });
    ui.text(def.name, 8 + nw / 2, HUD_H + 17, C.cream, { align: 'center', scale: 2 });

    actorsAt(run, this.locId).forEach((id, i) => {
      const actor = app.data.actors[id];
      const seller = actor.role === 'supplier';
      const open = () => {
        app.sfx.play('open');
        app.push(new TradeDialog(app, id));
      };
      // a Packed House's extra actor stands where the Dealer used to
      const base: Rect = { ...(def.slots[i] ?? def.dealerSlot), w: CARD_W, h: CARD_H };
      const hot = ui.focus(`actor:${id}`, base);
      this.card(ui, actor, base, i, seller ? 'Seller' : 'Buyer', seller ? C.greenLight : C.sky, hot);
      if (hot) {
        // touch screens trade one unit at a time from a button under the tooltip
        const verb = seller ? 'Buy' : 'Sell';
        // grayed out when nothing can be bought from (or sold to) this actor right now
        const block = seller ? buyBlock : sellBlock;
        const disabled = !actor.goods.some((g) => block(run, id, g.good) === null);
        const actions: TipAction[] = CONFIG.quickTrade
          ? [{ label: `${verb} 1`, onClick: () => quickTrade(app, ui, id, false), disabled }]
          : [{ label: 'Trade', onClick: open }];
        this.actorTooltip(ui, id, actions);
      }
      if (ui.activated(base)) {
        if (CONFIG.quickTrade) quickTrade(app, ui, id);
        else open();
      }
    });

    if (run.dealer?.locationId === this.locId) {
      // he stands in the spot an actor would have taken (days dealt before that use dealerSlot)
      const n = actorsAt(run, this.locId).length;
      const pos = n < def.actorSlots ? def.slots[n] : def.dealerSlot;
      const open = () => {
        app.sfx.play('open');
        app.push(new DealerDialog(app));
      };
      const base: Rect = { ...pos, w: CARD_W, h: CARD_H };
      const hot = ui.focus('dealer', base);
      this.card(ui, app.data.dealer, base, n, 'Stamps', C.gold, hot);
      if (hot) this.dealerTooltip(ui, [{ label: 'Open', onClick: open }]);
      if (ui.activated(base)) open();
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
    const detouring = canDetour(run);
    if (ui.button(endBtn, detouring ? 'Detour' : 'End Day', { scale: 2 })) {
      if (detouring) this.detour();
      else this.tryEndDay();
    }
    if (ui.hover(endBtn)) this.endDayTooltip(ui, detouring);
    drawHud(app, ui);
  }

  /** A bobbing portrait card with a tag above it, at `base` (its hit rect, without the bob). */
  private card(ui: Ui, who: { portrait: string; name: string; role?: Role }, base: Rect, i: number, tag: string, tagColor: string, hot: boolean): void {
    const bob = Math.round(Math.sin(ui.t * 2 + i * 1.7) * 2) - (hot ? 3 : 0);
    const r = { ...base, y: base.y + bob };

    ui.nine(hot ? 'row_hover' : 'panel', r);
    drawPortrait(ui, who, r.x + (CARD_W - 64) / 2, r.y + 8);
    const lines = ui.font.wrap(who.name, CARD_W - 12).slice(0, 2);
    lines.forEach((l, j) => ui.text(l, r.x + CARD_W / 2, r.y + 76 + j * 11, C.ink, { align: 'center' }));

    const tw = ui.font.measure(tag) + 14;
    ui.nine('panel_dark', { x: r.x + (CARD_W - tw) / 2, y: r.y - 12, w: tw, h: 18 });
    ui.text(tag, r.x + CARD_W / 2, r.y - 7, tagColor, { align: 'center' });
  }

  private dealerTooltip(ui: Ui, actions: TipAction[]): void {
    const { name } = this.app.data.dealer;
    const desc = 'Sell Stamps for Stars';
    const w = 16 + Math.max(ui.font.measure(name), ui.font.measure(desc));
    ui.tooltip(w, 30, (x, y) => {
      ui.text(name, x, y, C.gold);
      ui.text(desc, x, y + 12, C.muted);
    }, actions);
  }

  private actorTooltip(ui: Ui, actorId: string, actions: TipAction[]): void {
    const data = this.app.view;
    const run = this.app.run!;
    const a = data.actors[actorId];
    const seller = a.role === 'supplier';
    // text lines per good: name + price (+ deal label), stock/demand, avg paid (buyers)
    const event = todayEvent(data, run);
    const capLabel = event?.weather === 'rain' ? 'Raining' : event?.name.replace(/!$/, '');
    const rows = a.goods.map((g) => {
      const o = offer(run, actorId, g.good);
      const deal = DEAL_LABEL[o.tier];
      // the price of the next unit, after the stamps
      const price = seller ? fullBuyPrice(run, o) : nextSellPrice(run, o, g.good);
      const lines: { text: string; color: string; suffix?: string; suffixColor?: string }[] = [
        { text: `${data.goods[g.good].name}  $${price}`, color: C.cream, suffix: deal?.text, suffixColor: deal?.color },
      ];
      const bustle = event?.bustling;
      if (o.bustling && bustle) {
        const pct = Math.round((seller ? bustle.sellDiscount : bustle.buyBonus) * 100);
        lines.push({ text: `Bustling (${seller ? '-' : '+'}${pct}%)`, color: C.festive });
      }
      if (seller ? CONFIG.limitStock : demandApplies(o)) {
        if (!seller && o.capped) {
          const text = o.left > 0 ? `${capLabel} (buys ${o.left})` : `${capLabel} (can't buy more)`;
          lines.push({ text, color: o.left > 0 ? C.cyan : C.redLight });
        } else {
          const qty = seller ? `${o.left} in stock` : o.left > 0 ? `wants ${o.left}` : 'wants no more';
          lines.push({ text: qty, color: o.left > 0 ? C.muted : C.redLight });
        }
      }
      // stamp perks: the Daily Discount's half-price first buy, Camp Fire's half-price second one,
      // and Tip Jar's progress
      const cheaper = buyDiscountStamp(run);
      if (seller && cheaper && buyPrice(run, o) < price) {
        const label = cheaper === 'dailyDiscount' ? 'Daily Discount: first one' : 'Camp Fire: next one';
        lines.push({ text: `${label} $${buyPrice(run, o)}`, color: C.cyan });
      }
      if (!seller) {
        // what's raising (or, with Haggler, cutting) the next sale's price
        const item = run.inventory.find((it) => it.good === g.good);
        const bonus = item ? sellBonus(run, item) : 0;
        const flip = item ? flipperBonus(run, item) : 0;
        const haggle = hagglerMultiplier(run);
        const parts = [
          ...(bonus ? [`+${Math.round(bonus * 100)}%`] : []),
          ...(flip ? [`+$${flip}`] : []),
          ...(owns(run, { kind: 'haggler' }) ? [`Haggler x${haggle}`] : []),
        ];
        if (parts.length) lines.push({ text: `Stamps: ${parts.join(', ')}`, color: haggle < 1 ? C.redLight : C.cyan });
      }
      if (!seller && owns(run, { kind: 'cantGetEnough' })) lines.push({ text: `+$${CONFIG.dealer.cantGetEnoughStep} after each sale`, color: C.cyan });
      if (!seller && owns(run, { kind: 'tip' })) {
        const { tip, tipAfter } = CONFIG.dealer;
        const more = tipAfter - (o.sold ?? 0);
        const text = o.tipped ? `Tipped $${tip} today` : `Tip: +$${tip} after ${more} more sold`;
        lines.push({ text, color: o.tipped ? C.muted : C.cyan });
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
    }, actions);
  }

  /** What the End Day button does: the Detour, or the stamps that pay out tonight. */
  private endDayTooltip(ui: Ui, detouring: boolean): void {
    const run = this.app.run!;
    const lines: { text: string; color: string }[] = [];
    if (detouring) {
      lines.push({ text: 'Detour: go to another place today', color: C.gold });
      lines.push({ text: 'Only until you buy or sell something', color: C.muted });
    } else {
      const p = endOfDayPayouts(run);
      if (p.fannyPack) lines.push({ text: `Fanny Pack: +$${p.fannyPack}`, color: C.greenLight });
      if (p.sleepingBag) lines.push({ text: `Sleeping Bag: +$${p.sleepingBag}`, color: C.greenLight });
      if (p.cleanSweep) lines.push({ text: `Clean Sweep: +$${p.cleanSweep}`, color: C.greenLight });
      if (lines.length > 1) lines.push({ text: `Total tonight: +$${payoutTotal(p)}`, color: C.gold });
    }
    if (lines.length === 0) return;
    const w = 16 + Math.max(...lines.map((l) => ui.font.measure(l.text)));
    ui.tooltip(w, 6 + lines.length * 12, (x, y) => lines.forEach((l, i) => ui.text(l.text, x, y + i * 12, l.color)));
  }

  /** Leave for a second location (the Detour stamp). */
  private detour(): void {
    const { app } = this;
    detour(app.run!);
    app.save();
    app.sfx.play('open');
    app.goto(new MapScene(app));
  }

  private tryEndDay(): void {
    const { app } = this;
    const run = app.run!;
    if (buyoutOffer(app.data, run) !== null) {
      app.push(new BuyoutDialog(app, () => this.doEndDay()));
    } else if (run.day >= run.quota.dueDay && !run.quota.met && run.cash + payoutTotal(endOfDayPayouts(run)) < run.quota.amount) {
      const short = run.quota.amount - run.cash - payoutTotal(endOfDayPayouts(run));
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
    if (res === 'won') {
      showVictory(app, run);
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
