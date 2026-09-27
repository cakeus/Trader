import type { App, Scene } from '../app';
import { H, W } from '../engine/screen';
import { C, type Rect, type Ui } from '../engine/ui';
import { buyDealerDeal, type DealerBlock, dealerBlock, dealGood, describeDeal, isRare } from '../game/dealer';
import type { DealerDeal } from '../game/types';
import { drawBag, drawPortrait, STAR_INK } from './common';

const ROW_H = 44;
/** Rare-deal label on the paper panel. */
const RARE_INK = '#8a4ab8';

const REASON: Record<Exclude<DealerBlock, null>, string> = {
  sold: 'Sold',
  noStars: 'Not enough stars',
};

/** 16x16 UI icon for deals that aren't about a specific good. */
const DEAL_ICON: Partial<Record<DealerDeal['kind'], string>> = {
  bag: 'assets/ui/icon_bag.png',
};

/** The Dealer's window, laid out like the trade dialog: one row per deal, click a row to buy it. */
export class DealerDialog implements Scene {
  constructor(private app: App) {}

  frame(ui: Ui): void {
    const { app } = this;
    const run = app.run!;
    const visit = run.dealer;
    if (!visit) {
      app.pop(this);
      return;
    }
    const dealer = app.data.dealer;
    ui.dim(0.45);

    const w = 420;
    const h = 112 + visit.offers.length * (ROW_H + 4) + 36;
    const r: Rect = { x: (W - w) / 2, y: Math.max(40, (H - 60 - h) / 2), w, h };
    ui.nine('panel', r);

    // header
    ui.nine('row', { x: r.x + 14, y: r.y + 14, w: 72, h: 72 });
    drawPortrait(ui, dealer, r.x + 18, r.y + 18);
    const tx = r.x + 100;
    const avail = r.w - 114;
    const nameScale = ui.font.measure(dealer.name, 2) <= avail ? 2 : 1;
    ui.text(dealer.name, tx, r.y + 16, C.ink, { scale: nameScale });
    ui.text('Trades for stars', tx, r.y + 38, STAR_INK);
    ui.para(dealer.blurb, tx, r.y + 54, avail, C.inkSoft);

    // rows
    visit.offers.forEach((o, i) => {
      const deal = describeDeal(app.data, o.deal);
      const row: Rect = { x: r.x + 14, y: r.y + 100 + i * (ROW_H + 4), w: r.w - 28, h: ROW_H };
      const block = dealerBlock(run, i);
      const hot = ui.hover(row);
      ui.nine(hot && !block ? 'row_hover' : 'row', row);
      const good = dealGood(o.deal);
      if (good) ui.image(app.data.goods[good].icon, row.x + 6, row.y + 6);
      else if (isRare(o.deal))
        Object.values(app.data.goods).slice(0, 4).forEach((g, j) => {
          ui.image(g.iconSmall, row.x + 11 + (j % 2) * 13, row.y + 11 + Math.floor(j / 2) * 13);
        });
      else ui.image(DEAL_ICON[o.deal.kind]!, row.x + 14, row.y + 14);
      ui.text(deal.title, row.x + 46, row.y + 9, o.sold ? C.inkSoft : C.ink);
      if (isRare(o.deal)) ui.text('Rare', row.x + 52 + ui.font.measure(deal.title), row.y + 9, RARE_INK);
      ui.text(deal.body, row.x + 46, row.y + 24, C.inkSoft);

      const right = row.x + row.w - 10;
      if (block) {
        ui.text(REASON[block], right, row.y + 17, block === 'sold' ? C.inkSoft : C.red, { align: 'right' });
      } else {
        ui.image('assets/ui/icon_star.png', right - 16, row.y + 14);
        ui.text(`${o.cost}`, right - 20, row.y + 12, C.ink, { align: 'right', scale: 2 });
      }

      if (ui.clicked(row)) this.buy(ui, i);
    });

    // footer
    const fy = r.y + r.h - 28;
    ui.image('assets/ui/icon_star.png', r.x + 14, fy + 2);
    ui.text(`You have ${run.stars} star${run.stars === 1 ? '' : 's'}`, r.x + 34, fy + 6, STAR_INK);
    const close = ui.button({ x: r.x + r.w - 90, y: fy - 2, w: 76, h: 22 }, 'Close');
    if (close || ui.key('Escape') || ui.clickedOutside(r)) app.pop(this);

    drawBag(app, ui, 8, H - 56);
  }

  private buy(ui: Ui, index: number): void {
    const { app } = this;
    const run = app.run!;
    const block = dealerBlock(run, index);
    if (block) {
      app.sfx.play('deny');
      ui.floater(REASON[block], ui.input.x, ui.input.y - 12, C.redLight);
      return;
    }
    const offer = run.dealer!.offers[index];
    buyDealerDeal(app.data, run, index);
    app.sfx.play('quota');
    ui.floater(`-${offer.cost} stars`, ui.input.x, ui.input.y - 12, C.gold);
    app.save();
  }
}
