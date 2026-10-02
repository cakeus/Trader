import type { App, Scene } from '../app';
import { isMobile } from '../engine/device';
import { H, W } from '../engine/screen';
import { C, type Rect, type Ui } from '../engine/ui';
import { buyDealerDeal, type DealerBlock, dealerBlock, describeDeal, rarityOf } from '../game/dealer';
import { drawBag, drawPortrait, STAR_INK } from './common';
import { drawStamp, RARITY_LABEL } from './stampArt';

/** The dialog's layout: its width, a row's height and where its title and body sit, the
 *  subtitle's and blurb's y, and the Close button. Mobile's big font needs more room. */
const L = isMobile
  ? { w: 600, rowH: 48, title: 7, body: 25, sub: 46, blurb: 64, closeW: 90, closeH: 30, foot: 36 }
  : { w: 420, rowH: 44, title: 9, body: 24, sub: 38, blurb: 54, closeW: 76, closeH: 22, foot: 28 };
const ROW_H = L.rowH;

const REASON: Record<Exclude<DealerBlock, null>, string> = {
  sold: 'Sold',
  noStars: 'Not enough stars',
};

/** The Dealer's window, laid out like the trade dialog: one row per stamp, click a row to buy it. */
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

    const w = L.w;
    const tx = 100;
    const avail = w - 114;
    // the rows start under the blurb (on desktop, at 100 whatever its length)
    const blurbH = ui.font.wrap(dealer.blurb, avail).length * ui.font.lineHeight;
    const top = isMobile ? Math.max(100, L.blurb + blurbH + 8) : 100;
    const h = top + 12 + visit.offers.length * (ROW_H + 4) + L.foot + 8;
    const r: Rect = { x: (W - w) / 2, y: Math.max(40, (H - 60 - h) / 2), w, h };
    ui.nine('panel', r);

    // header
    ui.nine('row', { x: r.x + 14, y: r.y + 14, w: 72, h: 72 });
    drawPortrait(ui, dealer, r.x + 18, r.y + 18);
    const nameScale = ui.font.measure(dealer.name, 2) <= avail ? 2 : 1;
    ui.text(dealer.name, r.x + tx, r.y + 16, C.ink, { scale: nameScale });
    ui.text('Trades stamps for stars', r.x + tx, r.y + L.sub, STAR_INK);
    ui.para(dealer.blurb, r.x + tx, r.y + L.blurb, avail, C.inkSoft);

    // rows
    visit.offers.forEach((o, i) => {
      const deal = describeDeal(app.data, o.deal, run.area);
      const row: Rect = { x: r.x + 14, y: r.y + top + i * (ROW_H + 4), w: r.w - 28, h: ROW_H };
      const block = dealerBlock(run, i);
      const hot = ui.hover(row);
      ui.nine(hot && !block ? 'row_hover' : 'row', row);
      drawStamp(app, ui, o.deal, row.x + 1, row.y + 1 + (ROW_H - 44) / 2);
      ui.text(deal.title, row.x + 50, row.y + L.title, o.sold ? C.inkSoft : C.ink);
      const rarity = RARITY_LABEL[rarityOf(o.deal)];
      if (rarity) ui.text(rarity.text, row.x + 58 + ui.font.measure(deal.title), row.y + L.title, o.sold ? C.inkSoft : rarity.dark);
      ui.text(deal.body, row.x + 50, row.y + L.body, C.inkSoft);

      const right = row.x + row.w - 10;
      const mid = row.y + Math.floor(ROW_H / 2);
      if (block === 'sold') {
        ui.text(REASON[block], right, mid - Math.ceil(ui.font.cap() / 2) - 1, C.inkSoft, { align: 'right' });
      } else {
        // the cost, in red when you can't afford it
        ui.image('assets/ui/icon_star.png', right - 16, mid - 8);
        ui.text(`${o.cost}`, right - 20, mid - Math.ceil(ui.font.cap(2) / 2) - 3, block ? C.red : C.ink, { align: 'right', scale: 2 });
      }

      if (ui.clicked(row)) this.buy(ui, i);
    });

    // footer
    const fy = r.y + r.h - L.foot;
    const cy = fy - 2 + Math.floor(L.closeH / 2);
    ui.image('assets/ui/icon_star.png', r.x + 14, cy - 7);
    ui.text(`You have ${run.stars} star${run.stars === 1 ? '' : 's'}`, r.x + 34, cy - Math.ceil(ui.font.cap() / 2) + 1, STAR_INK);
    const close = ui.button({ x: r.x + r.w - L.closeW - 14, y: fy - 2, w: L.closeW, h: L.closeH }, 'Close');
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
