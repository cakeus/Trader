import type { App, Scene } from '../app';
import { isMobile } from '../engine/device';
import { H, W } from '../engine/screen';
import { C, type Ui } from '../engine/ui';
import type { AreaEvent } from '../game/types';

/** An event's rule in one line, for its notice. */
function eventRule(event: AreaEvent): string | null {
  if (event.buyerLimit !== undefined) return `Buyers take at most ${event.buyerLimit} of a good per day.`;
  const b = event.bustling;
  if (b) {
    const pct = (f: number) => `${Math.round(f * 100)}%`;
    return `Bustling: +${b.extraActors} trader, buyers +${pct(b.buyBonus)}, sellers -${pct(b.sellDiscount)}.`;
  }
  if (event.snowedIn) return 'One spot a day is snowed in and hidden on the map.';
  return null;
}

/** Shown the first morning an area event is on (after its weather has been seen for a moment):
 *  what's happening, and the rule it brings. */
export class EventNotice implements Scene {
  constructor(private app: App, private event: AreaEvent) {
    app.sfx.play('lastDay');
  }

  frame(ui: Ui): void {
    const { event } = this;
    ui.dim(0.45);
    const w = isMobile ? 440 : 340;
    const btnH = isMobile ? 30 : 26;
    const blurb = ui.font.wrap(event.blurb, w - 40);
    const ruleText = eventRule(event);
    // the rule's strip, wrapped to fit the panel (one line on desktop)
    const rule = ruleText === null ? [] : isMobile ? ui.font.wrap(ruleText, w - 64) : [ruleText];
    const ruleH = 10 + rule.length * ui.lh;
    const h = 82 + btnH + blurb.length * ui.font.lineHeight + (rule.length > 0 ? ruleH + 8 : 0);
    const r = { x: (W - w) / 2, y: (H - h) / 2, w, h };
    ui.nine('panel', r);
    const bob = Math.round(Math.sin(ui.t * 3) * 2);
    ui.text(event.name, W / 2, r.y + 16 + bob, C.plum, { align: 'center', scale: 3 });
    let y = r.y + 56;
    blurb.forEach((l, i) => ui.text(l, W / 2, y + i * ui.font.lineHeight, C.inkSoft, { align: 'center' }));
    y += blurb.length * ui.font.lineHeight + 8;
    if (rule.length > 0) {
      // the rule on a dark strip, so it stands out from the story
      const rw = Math.max(...rule.map((l) => ui.font.measure(l))) + 24;
      ui.nine('panel_dark', { x: (W - rw) / 2, y, w: rw, h: ruleH });
      rule.forEach((l, i) => ui.text(l, W / 2, y + 6 + (isMobile ? 1 : 0) + i * ui.lh, C.sky, { align: 'center' }));
    }
    if (ui.button({ x: W / 2 - 60, y: r.y + h - btnH - 10, w: 120, h: btnH }, 'Got it') || ui.key('Enter') || ui.key('Escape')) {
      this.app.pop(this);
    }
  }
}
