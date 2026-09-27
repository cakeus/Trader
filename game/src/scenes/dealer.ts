import type { App, Scene } from '../app';
import { H, W } from '../engine/screen';
import { C, type Ui } from '../engine/ui';
import { buyDealerDeal, dealerBlock, describeDeal } from '../game/dealer';
import { drawPortrait, STAR_INK } from './common';

/** The Dealer's one deal of the day: spend stars on a permanent upgrade. */
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
    const deal = describeDeal(app.data, visit.deal);
    ui.dim(0.55);

    const w = 380;
    const tx = 100;
    const body = ui.font.wrap(deal.body, w - tx - 16);
    const h = Math.max(128, 56 + body.length * ui.font.lineHeight + 50);
    const r = { x: (W - w) / 2, y: (H - h) / 2, w, h };
    ui.nine('panel', r);

    ui.nine('row', { x: r.x + 14, y: r.y + 14, w: 72, h: 72 });
    drawPortrait(ui, dealer, r.x + 18, r.y + 18);
    ui.text(dealer.name, r.x + tx, r.y + 16, C.ink);
    ui.text(deal.title, r.x + tx, r.y + 32, C.ink, { scale: 2 });
    body.forEach((l, i) => ui.text(l, r.x + tx, r.y + 56 + i * ui.font.lineHeight, C.inkSoft));

    const block = dealerBlock(run);
    const by = r.y + h - 36;
    const note =
      block === 'sold' ? 'Sold out today' : `${visit.cost} stars (you have ${run.stars})`;
    ui.image('assets/ui/icon_star.png', r.x + 16, by + 4);
    ui.text(note, r.x + 36, by + 8, block ? C.red : STAR_INK);

    if (ui.button({ x: r.x + w - 176, y: by, w: 76, h: 24 }, 'Buy', { disabled: block !== null })) {
      buyDealerDeal(app.data, run);
      app.sfx.play('quota');
      ui.toast(deal.title + '!');
      app.save();
      app.pop(this);
      return;
    }
    if (ui.button({ x: r.x + w - 90, y: by, w: 76, h: 24 }, 'Close') || ui.key('Escape') || ui.clickedOutside(r)) {
      app.pop(this);
    }
  }
}
