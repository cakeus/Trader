import type { App, Scene } from '../app';
import { H, W } from '../engine/screen';
import { C, type Rect, type Ui } from '../engine/ui';
import { visit } from '../game/run';
import { drawBackground, drawBag, drawHud } from './common';
import { LocationScene } from './location';

export class MapScene implements Scene {
  constructor(private app: App) {}

  frame(ui: Ui): void {
    const { app } = this;
    const run = app.run!;
    drawBackground(ui, 'assets/bg/map.png');

    for (const loc of run.locations) {
      const def = app.data.locations[loc.id];
      const { x, y } = def.mapPos;
      const lw = ui.font.measure(def.name) + 18;
      const label: Rect = { x: Math.round(x - lw / 2), y: y + 4, w: lw, h: 22 };
      const hit: Rect = { x: label.x, y: y - 20, w: lw, h: 46 };
      const hot = ui.hover(hit);
      const bob = hot ? -Math.round(Math.abs(Math.sin(ui.t * 6)) * 3) : 0;

      ui.image('assets/ui/icon_pin.png', x - 8, y - 17 + bob);
      ui.nine(hot ? 'row_hover' : 'panel', label);
      ui.text(def.name, x, label.y + 7, C.ink, { align: 'center' });

      if (hot) this.locationTooltip(ui, loc.id, loc.actorIds);
      if (ui.clicked(hit)) {
        visit(app.data, run, loc.id);
        app.save();
        app.sfx.play('open');
        app.goto(new LocationScene(app, loc.id));
        return;
      }
    }

    const prompt = `Day ${run.day}`;
    const pw = ui.font.measure(prompt, 2) + 32;
    ui.nine('panel_dark', { x: W - pw - 8, y: H - 44, w: pw, h: 36 });
    ui.text(prompt, W - pw / 2 - 8, H - 33, C.cream, { align: 'center', scale: 2 });

    drawBag(app, ui, 8, H - 56);
    drawHud(app, ui);
  }

  private locationTooltip(ui: Ui, locId: string, actorIds: string[]): void {
    const { data } = this.app;
    const def = data.locations[locId];
    // goods traded here, deduped, from the player's point of view
    const goodsFor = (role: 'supplier' | 'buyer') => [
      ...new Set(actorIds.filter((id) => data.actors[id].role === role).flatMap((id) => data.actors[id].goods.map((g) => g.good))),
    ];
    const cols = [
      { label: 'Buys', color: C.sky, goods: goodsFor('buyer') },
      { label: 'Sells', color: C.greenLight, goods: goodsFor('supplier') },
    ].filter((c) => c.goods.length > 0);
    const dealer = this.app.run!.dealer?.locationId === locId;

    const w = 165;
    const blurb = ui.font.wrap(def.blurb, w - 16);
    const lh = ui.font.lineHeight;
    const goodsH = cols.length > 0 ? 34 : 0;
    const h = 14 + lh + blurb.length * lh + 6 + goodsH + (dealer ? 14 : 0) + 4;
    ui.tooltip(w, h, (x, y) => {
      ui.text(def.name, x, y, C.gold);
      blurb.forEach((l, i) => ui.text(l, x, y + lh + i * lh, C.muted));
      let ry = y + lh + blurb.length * lh + 6;
      // one column per side, label centred above its row of 16x16 icons
      const colW = (w - 16) / cols.length;
      cols.forEach((c, i) => {
        const cx = x + colW * (i + 0.5);
        ui.text(c.label, cx, ry, c.color, { align: 'center' });
        const iw = c.goods.length * 18 - 2;
        c.goods.forEach((g, j) => ui.image(data.goods[g].iconMedium, cx - iw / 2 + j * 18, ry + 12));
      });
      ry += goodsH;
      if (dealer) {
        ui.image('assets/ui/icon_star.png', x - 2, ry - 2);
        ui.text(`${data.dealer.name} is here!`, x + 16, ry + 2, C.gold);
      }
    });
  }
}
