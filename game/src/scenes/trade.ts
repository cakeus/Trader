import type { App, Scene } from '../app';
import { H, W } from '../engine/screen';
import { C, type Rect, type Ui } from '../engine/ui';
import { CONFIG } from '../game/config';
import { buy, buyBlock, buyPrice, countOf, demandApplies, maxBuy, maxSell, offer, sell, sellBlock, type TradeBlock } from '../game/run';
import { drawBag, drawPortrait } from './common';

const REASON: Record<Exclude<TradeBlock, null>, string> = {
  soldOut: 'Sold out',
  noCash: 'Not enough cash',
  bagFull: 'Bag is full',
  noneOwned: 'You have none',
  noDemand: 'Wants no more',
};

const ROW_H = 44;

/** Modal buy/sell window for one actor. Click = 1 unit, shift-click = as many as possible. */
export class TradeDialog implements Scene {
  constructor(private app: App, private actorId: string) {}

  frame(ui: Ui): void {
    const { app, actorId } = this;
    const run = app.run!;
    const actor = app.view.actors[actorId];
    const selling = actor.role === 'supplier';
    ui.dim(0.45);

    const w = 420;
    const h = 112 + actor.goods.length * (ROW_H + 4) + 36;
    const r: Rect = { x: (W - w) / 2, y: Math.max(40, (H - 60 - h) / 2), w, h };
    ui.nine('panel', r);

    // header
    ui.nine('row', { x: r.x + 14, y: r.y + 14, w: 72, h: 72 });
    drawPortrait(ui, actor, r.x + 18, r.y + 18);
    const tx = r.x + 100;
    const avail = r.w - 114;
    const nameScale = ui.font.measure(actor.name, 2) <= avail ? 2 : 1;
    ui.text(actor.name, tx, r.y + 16, C.ink, { scale: nameScale });
    ui.text(selling ? 'Sells to you' : 'Buys from you', tx, r.y + 38, selling ? C.green : '#3a6aa8');
    ui.para(actor.blurb, tx, r.y + 54, avail, C.inkSoft);

    // rows
    actor.goods.forEach((ag, i) => {
      const good = app.data.goods[ag.good];
      const o = offer(run, actorId, ag.good);
      const row: Rect = { x: r.x + 14, y: r.y + 100 + i * (ROW_H + 4), w: r.w - 28, h: ROW_H };
      const block = selling ? buyBlock(run, actorId, ag.good) : sellBlock(run, actorId, ag.good);
      const hot = ui.hover(row);
      ui.nine(hot && !block ? 'row_hover' : 'row', row);
      ui.image(good.icon, row.x + 6, row.y + 6);
      ui.text(good.name, row.x + 46, row.y + 9, C.ink);
      const qty = selling ? (CONFIG.limitStock ? `Stock: ${o.left}   ` : '') : demandApplies(o) ? `Wants: ${o.left}   ` : '';
      ui.text(`${qty}You have: ${countOf(run, ag.good)}`, row.x + 46, row.y + 24, C.inkSoft);

      const right = row.x + row.w - 10;
      if (block) {
        ui.text(REASON[block], right, row.y + 17, C.red, { align: 'right' });
      } else {
        const verb = selling ? 'Buy' : 'Sell';
        ui.text(`${verb} $${selling ? buyPrice(run, o) : o.price}`, right, row.y + 12, C.ink, { align: 'right', scale: 2 });
      }

      if (ui.clicked(row)) tradeWith(app, ui, actorId, ag.good);
    });

    // footer
    const fy = r.y + r.h - 28;
    ui.text('Click: 1   Shift+click: max', r.x + 16, fy + 6, C.inkSoft);
    const close = ui.button({ x: r.x + r.w - 90, y: fy - 2, w: 76, h: 22 }, 'Close');
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
  const o = offer(run, actorId, good);
  const wasMet = run.quota.met;
  const cash = run.cash;
  if (selling) {
    buy(app.data, run, actorId, good, max ? maxBuy(run, actorId, good) : 1);
    app.sfx.play('buy');
    ui.floater(`-$${cash - run.cash}`, mx, my - 12, C.redLight);
  } else {
    const tipped = o.tipped;
    sell(app.data, run, actorId, good, max ? maxSell(run, actorId, good) : 1);
    app.sfx.play('sell');
    const tip = o.tipped && !tipped ? CONFIG.dealer.tip : 0;
    ui.floater(`+$${run.cash - cash - tip}`, mx, my - 12, C.gold);
    if (tip) ui.floater(`+$${tip} tip!`, mx, my - 26, C.cyan);
  }
  if (!wasMet && run.quota.met) {
    app.sfx.play('quota');
    ui.toast('Quota reached!');
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
