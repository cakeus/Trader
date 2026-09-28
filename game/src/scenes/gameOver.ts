import type { App, Scene } from '../app';
import { seedLabel } from '../engine/rng';
import { H, W } from '../engine/screen';
import { C, type Ui } from '../engine/ui';
import type { RunState } from '../game/types';
import { drawBackground } from './common';
import { MainMenu } from './mainMenu';

export class GameOver implements Scene {
  constructor(private app: App, private run: RunState) {}

  frame(ui: Ui): void {
    const { run } = this;
    drawBackground(ui, this.app.data.areas[run.area]?.map ?? 'assets/bg/map.png');
    ui.dim(0.7);
    const w = 380;
    const h = 220;
    const r = { x: (W - w) / 2, y: (H - h) / 2, w, h };
    ui.nine('panel', r);
    ui.text('Out of luck...', W / 2, r.y + 16, C.red, { align: 'center', scale: 3 });
    ui.text(`You needed $${run.quota.amount} by the end of Day ${run.quota.dueDay},`, W / 2, r.y + 56, C.ink, {
      align: 'center',
    });
    ui.text(`but only had $${run.cash}.`, W / 2, r.y + 68, C.ink, { align: 'center' });

    const stats = [
      ['Days traded', `${run.day}`],
      ['Quotas met', `${run.stats.quotasMet}`],
      ['Goods bought', `${run.stats.bought}`],
      ['Goods sold', `${run.stats.sold}`],
    ];
    stats.forEach(([k, v], i) => {
      const y = r.y + 92 + i * 13;
      ui.text(k, W / 2 - 90, y, C.inkSoft);
      ui.text(v, W / 2 + 90, y, C.ink, { align: 'right' });
    });
    ui.text(`Seed ${seedLabel(run.seed)}`, W / 2, r.y + 150, C.muted, { align: 'center' });

    if (ui.button({ x: W / 2 - 70, y: r.y + h - 40, w: 140, h: 26 }, 'Main Menu') || ui.key('Enter')) {
      this.app.goto(new MainMenu(this.app));
    }
  }
}
