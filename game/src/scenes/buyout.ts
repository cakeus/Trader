import type { App, Scene } from '../app';
import { H, W } from '../engine/screen';
import { C, type Ui } from '../engine/ui';
import { owns } from '../game/dealer';
import { buyoutOffer, endOfDayPayouts, payoutTotal, takeBuyout } from '../game/run';

/** End Day on an unmet quota's due day with goods in the bag: offer to buy the whole bag at
 *  Bad-deal prices, then end the day either way (or go back to trading). */
export class BuyoutDialog implements Scene {
  constructor(private app: App, private onEnd: () => void) {}

  frame(ui: Ui): void {
    const { app } = this;
    const run = app.run!;
    const total = buyoutOffer(app.data, run) ?? 0;
    const n = run.inventory.length;
    // tonight's stamp payouts count toward the quota too
    const short = run.quota.amount - run.cash - payoutTotal(endOfDayPayouts(run));
    // with the bag sold, the payouts change (Clean Sweep pays, Fanny Pack doesn't)
    const payoutAfter = payoutTotal(endOfDayPayouts({ ...run, inventory: [] }));
    const after = run.quota.amount - run.cash - total - payoutAfter;
    ui.dim(0.55);

    const w = 360;
    const prices = owns(run, { kind: 'lastCall' }) ? 'Amazing' : 'Bad-deal';
    const body = `The quota is due tonight and you're $${short} short. A late-night buyer offers to take your whole bag at ${prices} prices.`;
    const lines = ui.font.wrap(body, w - 40);
    const h = 150 + lines.length * ui.font.lineHeight;
    const r = { x: (W - w) / 2, y: (H - h) / 2, w, h };
    ui.nine('panel', r);
    ui.text('Last chance!', W / 2, r.y + 16, C.ink, { align: 'center', scale: 2 });
    lines.forEach((l, i) => ui.text(l, W / 2, r.y + 44 + i * ui.font.lineHeight, C.inkSoft, { align: 'center' }));

    const oy = r.y + 52 + lines.length * ui.font.lineHeight;
    ui.text(`${n} item${n === 1 ? '' : 's'} for $${total}`, W / 2, oy, C.ink, { align: 'center', scale: 2 });
    const verdict = after <= 0 ? 'That covers the quota!' : `You'd still be $${after} short.`;
    ui.text(verdict, W / 2, oy + 24, after <= 0 ? C.green : C.red, { align: 'center' });

    const by = r.y + h - 36;
    if (ui.button({ x: W / 2 - 165, y: by, w: 100, h: 24 }, 'Back') || ui.key('Escape')) app.pop(this);
    if (ui.button({ x: W / 2 - 55, y: by, w: 100, h: 24 }, 'End Day')) {
      app.pop(this);
      this.onEnd();
    }
    if (ui.button({ x: W / 2 + 55, y: by, w: 110, h: 24 }, `Sell for $${total}`)) {
      app.pop(this);
      takeBuyout(app.data, run);
      app.sfx.play('sell');
      app.save();
      this.onEnd();
    }
  }
}
