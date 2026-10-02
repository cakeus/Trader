import type { App, Scene } from '../app';
import { isMobile } from '../engine/device';
import { H, W } from '../engine/screen';
import { C, type Rect, type Ui } from '../engine/ui';
import { allDeals, dealEnabled, describeDeal, owns, rarityOf } from '../game/dealer';
import type { DealerDeal, RunState } from '../game/types';
import { drawStamp, RARITY_LABEL, STAMP_SIZE } from './stampArt';

const COLS = 6;
const PITCH = STAMP_SIZE + 6;
/** Mobile's big font pushes the subtitle and grid down, and the Close button is bigger. */
const L = isMobile ? { sub: 42, grid: 62, closeW: 90, closeH: 30, foot: 36 } : { sub: 36, grid: 56, closeW: 76, closeH: 22, foot: 30 };

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
    const h = L.grid + 16 + rows * PITCH + L.foot + 4;
    const r: Rect = { x: (W - w) / 2, y: (H - h) / 2, w, h };
    ui.nine('panel', r);
    ui.text('Stamps', W / 2, r.y + 14, C.ink, { align: 'center', scale: 2 });
    ui.text(`${mine.length} of ${all.length} collected`, W / 2, r.y + L.sub, C.inkSoft, { align: 'center' });

    const gx = r.x + 20;
    const gy = r.y + L.grid;
    ui.nine('row', { x: gx - 6, y: gy - 6, w: gridW + 12, h: rows * PITCH + 6 });
    if (mine.length === 0) {
      ui.text('No stamps yet.', W / 2, gy + 8, C.inkSoft, { align: 'center' });
      ui.text(`Earn stars and visit ${app.data.dealer.name.split(' ')[0]}.`, W / 2, gy + 8 + ui.lh + 2, C.inkSoft, { align: 'center' });
    }
    mine.forEach((deal, i) => {
      const x = gx + (i % COLS) * PITCH;
      const y = gy + Math.floor(i / COLS) * PITCH;
      const hit: Rect = { x, y, w: STAMP_SIZE, h: STAMP_SIZE };
      const hot = ui.focus(`stamp:${i}`, hit);
      drawStamp(app, ui, deal, x, y - (hot ? 2 : 0));
      if (hot) stampTooltip(app, ui, deal, app.area);
    });

    const close = ui.button({ x: W / 2 - L.closeW / 2, y: r.y + h - L.foot, w: L.closeW, h: L.closeH }, 'Close');
    if (close || ui.key('Escape') || ui.clickedOutside(r)) app.pop(this);
  }
}

/** A stamp's tooltip: its title, rarity and what it does (described for `area`). */
export function stampTooltip(app: App, ui: Ui, deal: DealerDeal, area: string): void {
  const { title, body } = describeDeal(app.data, deal, area);
  const rarity = RARITY_LABEL[rarityOf(deal)];
  const titleW = ui.font.measure(title) + (rarity ? 8 + ui.font.measure(rarity.text) : 0);
  const w = Math.max(titleW, ui.font.measure(body)) + 16;
  // the body wraps on mobile's sheet (it's one line on desktop)
  const lines = ui.touch ? ui.font.wrap(body, ui.tipWidth(w)) : [body];
  ui.tooltip(w, 12 + (1 + lines.length) * ui.lh, (x, y) => {
    ui.text(title, x, y + 1, C.gold);
    if (rarity) ui.text(rarity.text, x + 8 + ui.font.measure(title), y + 1, rarity.light);
    lines.forEach((l, i) => ui.text(l, x, y + 1 + (i + 1) * ui.lh, C.muted));
  });
}

const END_PITCH = STAMP_SIZE + 2;

/** An ended run's stamps (the end screens): a grid `cols` wide whose bottom-right corner is at
 *  (`right`, `bottom`), filling up from the bottom row, at most `maxRows` rows (the rest shown as
 *  "+N more"), under a "Stamps" label. Hover (or tap) one for its tooltip. */
export function drawRunStamps(
  app: App, ui: Ui, run: RunState, right: number, bottom: number, cols: number, maxRows: number,
): void {
  const mine = allDeals(app.data).filter((d) => owns(run, d));
  const fits = cols * maxRows;
  const shown = mine.length > fits ? mine.slice(0, fits - 1) : mine;
  const rows = Math.max(1, Math.ceil((shown.length + (shown.length < mine.length ? 1 : 0)) / cols));
  const gridW = cols * END_PITCH - 2;
  const x0 = right - gridW;
  const y0 = bottom - rows * END_PITCH + 2;
  ui.text(`Stamps (${mine.length})`, x0, y0 - ui.lh - 2, C.inkSoft);
  if (mine.length === 0) {
    ui.text('None this run.', x0, y0, C.muted);
    return;
  }
  let hotDeal: DealerDeal | null = null;
  shown.forEach((deal, i) => {
    const x = x0 + (i % cols) * END_PITCH;
    const y = y0 + Math.floor(i / cols) * END_PITCH;
    const hot = ui.focus(`endStamp:${i}`, { x, y, w: STAMP_SIZE, h: STAMP_SIZE });
    drawStamp(app, ui, deal, x, y - (hot ? 2 : 0), run.area);
    if (hot) hotDeal = deal;
  });
  if (shown.length < mine.length) {
    const i = shown.length;
    const x = x0 + (i % cols) * END_PITCH;
    const y = y0 + Math.floor(i / cols) * END_PITCH;
    ui.text(`+${mine.length - shown.length}`, x + STAMP_SIZE / 2, y + Math.floor((STAMP_SIZE - ui.font.cap()) / 2) - 1, C.inkSoft, { align: 'center' });
  }
  // drawn last so it sits over the stamps after it
  if (hotDeal) stampTooltip(app, ui, hotDeal, run.area);
}
