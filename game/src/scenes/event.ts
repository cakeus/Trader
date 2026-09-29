import type { App, Scene } from '../app';
import { H, W } from '../engine/screen';
import { C, type Ui } from '../engine/ui';
import type { AreaEvent } from '../game/types';

/** Shown the first morning an area event is on (after its weather has been seen for a moment):
 *  what's happening, and the rule it brings. */
export class EventNotice implements Scene {
  constructor(private app: App, private event: AreaEvent) {
    app.sfx.play('lastDay');
  }

  frame(ui: Ui): void {
    const { event } = this;
    ui.dim(0.45);
    const w = 340;
    const blurb = ui.font.wrap(event.blurb, w - 40);
    const rule = event.buyerLimit === undefined ? null : `Buyers take at most ${event.buyerLimit} of a good per day.`;
    const h = 108 + blurb.length * ui.font.lineHeight + (rule ? 30 : 0);
    const r = { x: (W - w) / 2, y: (H - h) / 2, w, h };
    ui.nine('panel', r);
    const bob = Math.round(Math.sin(ui.t * 3) * 2);
    ui.text(event.name, W / 2, r.y + 16 + bob, C.plum, { align: 'center', scale: 3 });
    let y = r.y + 56;
    blurb.forEach((l, i) => ui.text(l, W / 2, y + i * ui.font.lineHeight, C.inkSoft, { align: 'center' }));
    y += blurb.length * ui.font.lineHeight + 8;
    if (rule) {
      // the rule on a dark strip, so it stands out from the story
      const rw = ui.font.measure(rule) + 24;
      ui.nine('panel_dark', { x: (W - rw) / 2, y, w: rw, h: 22 });
      ui.text(rule, W / 2, y + 6, C.sky, { align: 'center' });
    }
    if (ui.button({ x: W / 2 - 60, y: r.y + h - 36, w: 120, h: 26 }, 'Got it') || ui.key('Enter') || ui.key('Escape')) {
      this.app.pop(this);
    }
  }
}
