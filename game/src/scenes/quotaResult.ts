import type { App, Scene } from '../app';
import { H, W } from '../engine/screen';
import { C, type Ui } from '../engine/ui';
import type { Quota } from '../game/types';
import { STAR_INK } from './common';

/** Shown on the morning after a quota is passed. */
export class QuotaResult implements Scene {
  constructor(private app: App, private passed: Quota) {}

  frame(ui: Ui): void {
    const next = this.app.run!.quota;
    ui.dim(0.55);
    const w = 340;
    const h = 196;
    const r = { x: (W - w) / 2, y: (H - h) / 2, w, h };
    ui.nine('panel', r);
    const bob = Math.round(Math.sin(ui.t * 4) * 2);
    ui.image('assets/ui/icon_star.png', W / 2 - 110, r.y + 20 + bob);
    ui.image('assets/ui/icon_star.png', W / 2 + 94, r.y + 20 - bob);
    ui.text('Quota met!', W / 2, r.y + 16, C.green, { align: 'center', scale: 3 });
    ui.text(`You made $${this.passed.amount} by the end of Day ${this.passed.dueDay}.`, W / 2, r.y + 58, C.ink, {
      align: 'center',
    });
    const got = this.passed.starsAwarded ?? 0;
    const early = this.passed.earlyBonus ?? 0;
    const breakdown = early > 0 ? ` (${this.passed.stars} + ${early} early)` : '';
    ui.text(`+${got} stars${breakdown}   You have ${this.app.run!.stars}`, W / 2, r.y + 76, STAR_INK, {
      align: 'center',
    });
    ui.text('Next quota:', W / 2, r.y + 104, C.inkSoft, { align: 'center' });
    ui.text(`$${next.amount} by end of Day ${next.dueDay}`, W / 2, r.y + 118, C.ink, { align: 'center', scale: 2 });
    if (ui.button({ x: W / 2 - 60, y: r.y + h - 40, w: 120, h: 26 }, 'Onward!') || ui.key('Enter')) {
      this.app.pop(this);
    }
  }
}
