import type { App, Scene } from '../app';
import { H, W } from '../engine/screen';
import { C, type Rect, type Ui } from '../engine/ui';
import { allDeals, dealEnabled, describeDeal, owns, rarityOf } from '../game/dealer';
import type { DealerDeal } from '../game/types';
import { drawStamp, RARITY_LABEL, STAMP_SIZE } from './stampArt';

const COLS = 6;
const PITCH = STAMP_SIZE + 6;

/** The stamp collection: every stamp bought from Nox this run, hover (or tap) one for what it does. */
export class StampsDialog implements Scene {
  constructor(private app: App) {}

  frame(ui: Ui): void {
    const { app } = this;
    const run = app.run!;
    ui.dim(0.45);

    // disabled stamps only count (and show) if this run already owns them
    const all = allDeals(app.data).filter((d) => dealEnabled(d) || owns(run, d));
    const mine = all.filter((d) => owns(run, d));
    const rows = Math.max(1, Math.ceil(mine.length / COLS));
    const gridW = COLS * PITCH - 6;
    const w = gridW + 40;
    const h = 72 + rows * PITCH + 34;
    const r: Rect = { x: (W - w) / 2, y: (H - h) / 2, w, h };
    ui.nine('panel', r);
    ui.text('Stamps', W / 2, r.y + 14, C.ink, { align: 'center', scale: 2 });
    ui.text(`${mine.length} of ${all.length} collected`, W / 2, r.y + 36, C.inkSoft, { align: 'center' });

    const gx = r.x + 20;
    const gy = r.y + 56;
    ui.nine('row', { x: gx - 6, y: gy - 6, w: gridW + 12, h: rows * PITCH + 6 });
    if (mine.length === 0) {
      ui.text('No stamps yet.', W / 2, gy + 8, C.inkSoft, { align: 'center' });
      ui.text(`Earn stars and visit ${app.data.dealer.name.split(' ')[0]}.`, W / 2, gy + 22, C.inkSoft, { align: 'center' });
    }
    mine.forEach((deal, i) => {
      const x = gx + (i % COLS) * PITCH;
      const y = gy + Math.floor(i / COLS) * PITCH;
      const hit: Rect = { x, y, w: STAMP_SIZE, h: STAMP_SIZE };
      const hot = ui.focus(`stamp:${i}`, hit);
      drawStamp(app, ui, deal, x, y - (hot ? 2 : 0));
      if (hot) this.tooltip(ui, deal);
    });

    const close = ui.button({ x: W / 2 - 38, y: r.y + h - 30, w: 76, h: 22 }, 'Close');
    if (close || ui.key('Escape') || ui.clickedOutside(r)) app.pop(this);
  }

  private tooltip(ui: Ui, deal: DealerDeal): void {
    const { title, body } = describeDeal(this.app.data, deal, this.app.area);
    const rarity = RARITY_LABEL[rarityOf(deal)];
    const titleW = ui.font.measure(title) + (rarity ? 8 + ui.font.measure(rarity.text) : 0);
    const w = Math.max(titleW, ui.font.measure(body)) + 16;
    ui.tooltip(w, 36, (x, y) => {
      ui.text(title, x, y + 1, C.gold);
      if (rarity) ui.text(rarity.text, x + 8 + ui.font.measure(title), y + 1, rarity.light);
      ui.text(body, x, y + 13, C.muted);
    });
  }
}
