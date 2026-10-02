import type { App, Scene } from '../app';
import { isMobile } from '../engine/device';
import { seedLabel } from '../engine/rng';
import { H, W } from '../engine/screen';
import { C, type Rect, type Ui } from '../engine/ui';
import {
  debugAdvance, debugAdvanceDay, debugGotoNextArea, debugNextArea, debugSetQuotaMet, updateQuota,
} from '../game/run';
import { describeDeal, eligibleDeals, grantDeal } from '../game/dealer';
import { Confirm } from './common';
import { MainMenu } from './mainMenu';
import { showDayEnd } from './location';
import { MapScene } from './map';
import { showVictory } from './victory';

const MENU_W = 240;
/** A row's pitch, and its buttons' height (bigger on mobile, for fingers). */
const ROW = isMobile ? 38 : 34;
const BTN_H = isMobile ? 30 : 26;
/** Where the rows start, under the scale-2 title. */
const TOP = isMobile ? 50 : 44;
/** The pause menu's bottom band, for the seed. */
const SEED_H = isMobile ? 26 : 22;

/** A centred panel with a title, `rows` buttons high, plus `extra` pixels at the bottom. */
function menuPanel(
  ui: Ui, title: string, rows: number, extra = 0, width = MENU_W,
): { r: Rect; x: number; w: number; y: number } {
  const h = TOP + rows * ROW + 12 + extra;
  const r = { x: (W - width) / 2, y: (H - h) / 2, w: width, h };
  ui.nine('panel', r);
  ui.text(title, W / 2, r.y + 16, C.ink, { align: 'center', scale: 2 });
  return { r, x: r.x + 30, w: width - 60, y: r.y + TOP };
}

export class PauseMenu implements Scene {
  constructor(private app: App) {}

  frame(ui: Ui): void {
    const { app } = this;
    ui.dim(0.6);
    // a submenu on top takes the panel's place
    if (!ui.active && this.app.scenes.at(-1) instanceof SubMenu) return;
    const debug = import.meta.env.DEV;
    const { r, x, w, y: top } = menuPanel(ui, 'Paused', debug ? 5 : 4, SEED_H);
    let y = top;
    const row = (label: string) => {
      const hit = ui.button({ x, y, w, h: BTN_H }, label);
      y += ROW;
      return hit;
    };

    if (row('Resume') || ui.key('Escape')) {
      app.pop(this);
      return;
    }
    if (row('Options')) app.push(new OptionsMenu(app));
    if (row('Save & Quit to Title')) {
      app.save();
      app.run = null;
      app.goto(new MainMenu(app));
      return;
    }
    if (row('Abandon Run')) {
      app.push(
        new Confirm(app, 'Abandon run?', 'This run will be gone for good.', 'Abandon', () => {
          app.endRun();
          app.goto(new MainMenu(app));
        }),
      );
    }
    if (debug && row('Debug')) app.push(new DebugMenu(app));
    if (app.run) ui.text(`Seed ${seedLabel(app.run.seed)}`, W / 2, r.y + r.h - SEED_H, C.inkSoft, { align: 'center' });
  }
}

/** A menu opened from the pause menu, drawn in its place. */
abstract class SubMenu implements Scene {
  constructor(protected app: App) {}
  abstract frame(ui: Ui): void;
}

/** Sound, music and display options (kept in `app.settings`). */
export class OptionsMenu extends SubMenu {
  frame(ui: Ui): void {
    const { app } = this;
    const s = app.settings;
    const { x, w, y: top } = menuPanel(ui, 'Options', isMobile ? 3 : 4);
    let y = top;
    const row = (label: string) => {
      const hit = ui.button({ x, y, w, h: BTN_H }, label);
      y += ROW;
      return hit;
    };
    const onOff = (b: boolean) => (b ? 'On' : 'Off');

    if (row(`Sound: ${onOff(s.sound)}`)) {
      s.sound = !s.sound;
      app.applySettings();
    }
    if (row(`Music: ${onOff(s.music)}`)) {
      s.music = !s.music;
      app.applySettings();
    }
    // phones always stretch (`applySettings`), so there's nothing to choose
    if (!isMobile && row(`Stretch to Fit: ${onOff(s.stretch)}`)) {
      s.stretch = !s.stretch;
      app.applySettings();
    }
    if (row('Back') || ui.key('Escape')) app.pop(this);
  }
}

/** Dev-build shortcuts for testing a run. */
class DebugMenu extends SubMenu {
  /** Which stamp "Give" hands out (an index into the ones not owned yet). */
  private pick = 0;

  frame(ui: Ui): void {
    const { app } = this;
    const run = app.run!;
    const { x, w, y: top } = menuPanel(ui, 'Debug', 7, 0, isMobile ? 360 : 300);
    let y = top;
    const q = run.quota;
    if (ui.button({ x, y, w, h: BTN_H }, q.met ? 'Mark Quota Incomplete' : 'Mark Quota Complete')) {
      debugSetQuotaMet(app.data, run, !q.met);
      app.save();
    }
    y += ROW;

    const day = debugAdvanceDay(run);
    const label = day === null ? 'Advance (quota not met)' : `Advance to Day ${day}`;
    if (ui.button({ x, y, w, h: BTN_H }, label, { disabled: day === null })) {
      const prevArea = run.area;
      const passed = debugAdvance(app.data, run);
      if (run.status === 'won') showVictory(app, run);
      else showDayEnd(app, passed, prevArea);
      return;
    }
    y += ROW;

    const next = debugNextArea(app.data, run);
    const nextLabel = next ? `Go to ${app.data.areas[next].name}` : 'Next Area (none)';
    if (ui.button({ x, y, w, h: BTN_H }, nextLabel, { disabled: next === null })) {
      debugGotoNextArea(app.data, run);
      app.save();
      app.goto(new MapScene(app));
      return;
    }
    y += ROW;

    // a label, then small buttons that add to (or reset) a number
    const adjust = (text: string, steps: number[], apply: (n: number | null) => void) => {
      ui.text(text, x, ui.vcenter(y, BTN_H), C.ink);
      const bw = 44;
      let bx = x + w - (steps.length + 1) * (bw + 4) + 4 - 8;
      for (const n of steps) {
        if (ui.button({ x: bx, y, w: bw, h: BTN_H }, `+${n}`)) apply(n);
        bx += bw + 4;
      }
      if (ui.button({ x: bx, y, w: bw + 8, h: BTN_H }, 'Reset')) apply(null);
      y += ROW;
    };
    adjust(`Cash $${run.cash}`, [5, 20], (n) => {
      run.cash = n === null ? 0 : run.cash + n;
      updateQuota(app.data, run);
      app.save();
    });
    adjust(`Stars ${run.stars}`, [1, 5], (n) => {
      run.stars = n === null ? 0 : run.stars + n;
      app.save();
    });

    // pick a stamp with the arrows, then give it for free
    const deals = eligibleDeals(app.data, run);
    if (deals.length > 0) {
      this.pick = ((this.pick % deals.length) + deals.length) % deals.length;
      const deal = deals[this.pick];
      if (ui.button({ x, y, w: BTN_H, h: BTN_H }, '<')) this.pick--;
      if (ui.button({ x: x + BTN_H + 4, y, w: w - 2 * BTN_H - 8, h: BTN_H }, `Give ${describeDeal(app.data, deal, run.area).title}`)) {
        grantDeal(app.data, run, deal);
        app.save();
      }
      if (ui.button({ x: x + w - BTN_H, y, w: BTN_H, h: BTN_H }, '>')) this.pick++;
    } else {
      ui.button({ x, y, w, h: BTN_H }, 'Every stamp owned', { disabled: true });
    }
    y += ROW;

    if (ui.button({ x, y, w, h: BTN_H }, 'Back') || ui.key('Escape')) app.pop(this);
  }
}
