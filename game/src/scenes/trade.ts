import type { App, Scene } from '../app';
import { isMobile } from '../engine/device';
import { H, W } from '../engine/screen';
import { C, type Rect, type Ui } from '../engine/ui';
import { CONFIG } from '../game/config';
import { buy, buyBlock, buyPrice, countOf, demandApplies, maxBuy, maxSell, nextSellPrice, offer, sellBlock, sellUnits, type TradeBlock } from '../game/run';
import { drawBag, drawPortrait } from './common';

const REASON: Record<Exclude<TradeBlock, null>, string> = {
  soldOut: 'Sold out',
  noCash: 'Not enough cash',
  bagFull: 'Bag is full',
  noneOwned: 'You have none',
  noDemand: 'Wants no more',
};

/** Laid out like the Dealer's dialog (`dealer.ts`), wider and taller on mobile. */
const L = isMobile
  ? { w: 600, rowH: 48, title: 7, body: 25, sub: 46, blurb: 64, closeW: 90, closeH: 30, foot: 36 }
  : { w: 420, rowH: 44, title: 9, body: 24, sub: 38, blurb: 54, closeW: 76, closeH: 22, foot: 28 };
const ROW_H = L.rowH;

/** Modal buy/sell window for one actor. Click = 1 unit, shift-click = as many as possible. */
export class TradeDialog implements Scene {
  constructor(private app: App, private actorId: string) {}

  frame(ui: Ui): void {
    const { app, actorId } = this;
    const run = app.run!;
    const actor = app.view.actors[actorId];
    const selling = actor.role === 'supplier';
    ui.dim(0.45);

    const w = L.w;
    const avail = w - 114;
    // the rows start under the blurb (on desktop, at 100 whatever its length)
    const blurbH = ui.font.wrap(actor.blurb, avail).length * ui.font.lineHeight;
    const top = isMobile ? Math.max(100, L.blurb + blurbH + 8) : 100;
    const h = top + 12 + actor.goods.length * (ROW_H + 4) + L.foot + 8;
    const r: Rect = { x: (W - w) / 2, y: Math.max(40, (H - 60 - h) / 2), w, h };
    ui.nine('panel', r);

    // header
    ui.nine('row', { x: r.x + 14, y: r.y + 14, w: 72, h: 72 });
    drawPortrait(ui, actor, r.x + 18, r.y + 18);
    const tx = r.x + 100;
    const nameScale = ui.font.measure(actor.name, 2) <= avail ? 2 : 1;
    ui.text(actor.name, tx, r.y + 16, C.ink, { scale: nameScale });
    ui.text(selling ? 'Sells to you' : 'Buys from you', tx, r.y + L.sub, selling ? C.green : '#3a6aa8');
    ui.para(actor.blurb, tx, r.y + L.blurb, avail, C.inkSoft);

    // rows
    actor.goods.forEach((ag, i) => {
      const good = app.data.goods[ag.good];
      const o = offer(run, actorId, ag.good);
      const row: Rect = { x: r.x + 14, y: r.y + top + i * (ROW_H + 4), w: r.w - 28, h: ROW_H };
      const block = selling ? buyBlock(run, actorId, ag.good) : sellBlock(run, actorId, ag.good);
      const hot = ui.hover(row);
      ui.nine(hot && !block ? 'row_hover' : 'row', row);
      ui.image(good.icon, row.x + 6, row.y + 6 + (ROW_H - 44) / 2);
      ui.text(good.name, row.x + 46, row.y + L.title, C.ink);
      const qty = selling ? (CONFIG.limitStock ? `Stock: ${o.left}   ` : '') : demandApplies(o) ? `Wants: ${o.left}   ` : '';
      ui.text(`${qty}You have: ${countOf(run, ag.good)}`, row.x + 46, row.y + L.body, C.inkSoft);

      const right = row.x + row.w - 10;
      const mid = row.y + Math.floor(ROW_H / 2);
      if (block) {
        ui.text(REASON[block], right, mid - Math.ceil(ui.font.cap() / 2) - 1, C.red, { align: 'right' });
      } else {
        const verb = selling ? 'Buy' : 'Sell';
        const price = selling ? buyPrice(run, o) : nextSellPrice(run, o, ag.good);
        ui.text(`${verb} $${price}`, right, mid - Math.ceil(ui.font.cap(2) / 2) - 3, C.ink, { align: 'right', scale: 2 });
      }

      if (ui.clicked(row)) tradeWith(app, ui, actorId, ag.good);
    });

    // footer
    const fy = r.y + r.h - L.foot;
    if (!isMobile) ui.text('Click: 1   Shift+click: max', r.x + 16, fy + 6, C.inkSoft);
    const close = ui.button({ x: r.x + r.w - L.closeW - 14, y: fy - 2, w: L.closeW, h: L.closeH }, 'Close');
    if (close || ui.key('Escape') || ui.clickedOutside(r)) {
      app.pop(this);
    }

    drawBag(app, ui, 8, H - 56);
  }

}

/** Trade one unit (`max`, by default shift: as many as possible) of `good` with an actor, with sfx and floaters. */
export function tradeWith(app: App, ui: Ui, actorId: string, good: string, max = ui.shift): void {
  const run = app.run!;
  const selling = app.data.actors[actorId].role === 'supplier';
  const block = selling ? buyBlock(run, actorId, good) : sellBlock(run, actorId, good);
  const mx = ui.input.x;
  const my = ui.input.y;
  if (block) {
    app.sfx.play('deny');
    ui.floater(REASON[block], mx, my - 12, C.redLight);
    return;
  }
  const cash = run.cash;
  if (selling) {
    buy(app.data, run, actorId, good, max ? maxBuy(run, actorId, good) : 1);
    app.sfx.play('buy');
    ui.floater(`-$${cash - run.cash}`, mx, my - 12, C.redLight);
  } else {
    const sale = sellUnits(app.data, run, actorId, good, max ? maxSell(run, actorId, good) : 1);
    app.sfx.play('sell');
    ui.floater(`+$${run.cash - cash - sale.tips}`, mx, my - 12, C.gold);
    // stacked a line apart
    const step = ui.lh + 2;
    if (sale.tips) ui.floater(`+$${sale.tips} tip!`, mx, my - 12 - step, C.cyan);
    if (sale.lucky) ui.floater('Lucky dice! Amazing deal', mx, my - 12 - (sale.tips ? 2 : 1) * step, C.cyan);
  }
  app.save();
}

/** Click-the-actor trading: pick the good to trade (buyers prefer one you actually hold). */
export function quickTrade(app: App, ui: Ui, actorId: string, max = ui.shift): void {
  const run = app.run!;
  const actor = app.view.actors[actorId];
  const goods = actor.goods.map((g) => g.good);
  const good =
    actor.role === 'buyer' ? (goods.find((g) => sellBlock(run, actorId, g) === null) ?? goods[0]) : goods[0];
  if (good) tradeWith(app, ui, actorId, good, max);
}
