import type { Assets } from './assets';
import type { Sfx } from './audio';
import type { Font, TextOpts } from './font';
import type { Input } from './input';
import { H, W } from './screen';

export interface Rect {
  x: number;
  y: number;
  w: number;
  h: number;
}

export const C = {
  ink: '#4a2e3e',
  inkSoft: '#8a6a72',
  paper: '#fbf1dc',
  cream: '#fff4e4',
  gold: '#ffd24a',
  green: '#3f8f4a',
  greenLight: '#8ee07a',
  red: '#c8404e',
  redLight: '#ff9a8a',
  plum: '#3b2f55',
  shadow: '#1e1630',
  muted: '#b8a8c0',
  sky: '#8fd0e8',
  cyan: '#7fe8f0',
};

export type PanelKind = 'panel' | 'panel_dark' | 'row' | 'row_hover' | 'btn' | 'btn_hover' | 'btn_down' | 'btn_disabled';

interface Floater {
  text: string;
  x: number;
  y: number;
  color: string;
  age: number;
}

const CORNER = 8;
/** How long a big centre-screen announcement stays up, in seconds. */
const ANNOUNCE_T = 2.2;

/** Immediate-mode UI helpers. Only the top scene is `active` (gets hover/clicks). */
export class Ui {
  active = true;
  /** Seconds since start, for bobbing/animation. */
  t = 0;
  private overlays: (() => void)[] = [];
  private floaters: Floater[] = [];
  private toastText = '';
  private toastAge = 99;
  private announceText = '';
  private announceAge = 99;

  constructor(
    readonly ctx: CanvasRenderingContext2D,
    readonly font: Font,
    readonly assets: Assets,
    readonly input: Input,
    readonly sfx: Sfx,
  ) {}

  // ------------------------------------------------------------ input ---

  inside(r: Rect, x = this.input.x, y = this.input.y): boolean {
    return x >= r.x && y >= r.y && x < r.x + r.w && y < r.y + r.h;
  }

  hover(r: Rect): boolean {
    return this.active && this.inside(r);
  }

  /** Mouse pressed and released inside `r`. */
  clicked(r: Rect): boolean {
    const i = this.input;
    return this.active && i.released && this.inside(r) && this.inside(r, i.pressX, i.pressY);
  }

  /** A click that started and ended outside `r` (e.g. to dismiss a dialog). */
  clickedOutside(r: Rect): boolean {
    const i = this.input;
    return this.active && i.released && !this.inside(r) && !this.inside(r, i.pressX, i.pressY);
  }

  key(k: string): boolean {
    return this.active && this.input.keys.has(k);
  }

  get shift(): boolean {
    return this.input.shift;
  }

  // ---------------------------------------------------------- drawing ---

  nine(name: PanelKind, r: Rect): void {
    const img = this.assets.get(`assets/ui/${name}.png`);
    if (!img) {
      this.ctx.fillStyle = name.includes('dark') ? C.plum : C.paper;
      this.ctx.fillRect(r.x, r.y, r.w, r.h);
      return;
    }
    const s = img.width;
    const m = s - CORNER * 2;
    const xs = [0, CORNER, s - CORNER];
    const ys = xs;
    const ws = [CORNER, m, CORNER];
    const dx = [r.x, r.x + CORNER, r.x + r.w - CORNER];
    const dy = [r.y, r.y + CORNER, r.y + r.h - CORNER];
    const dw = [CORNER, r.w - CORNER * 2, CORNER];
    const dh = [CORNER, r.h - CORNER * 2, CORNER];
    for (let j = 0; j < 3; j++)
      for (let i = 0; i < 3; i++)
        if (dw[i] > 0 && dh[j] > 0) this.ctx.drawImage(img, xs[i], ys[j], ws[i], ws[j], dx[i], dy[j], dw[i], dh[j]);
  }

  image(path: string, x: number, y: number): boolean {
    const img = this.assets.get(path);
    if (!img) return false;
    this.ctx.drawImage(img, Math.round(x), Math.round(y));
    return true;
  }

  text(s: string, x: number, y: number, color = C.ink, opts?: TextOpts): void {
    this.font.draw(this.ctx, s, x, y, color, opts);
  }

  /** Word-wrapped paragraph; returns the height used. */
  para(s: string, x: number, y: number, maxW: number, color = C.ink): number {
    const lines = this.font.wrap(s, maxW);
    lines.forEach((l, i) => this.text(l, x, y + i * this.font.lineHeight, color));
    return lines.length * this.font.lineHeight;
  }

  dim(alpha = 0.5, color = '20,14,32'): void {
    this.ctx.fillStyle = `rgba(${color},${alpha})`;
    this.ctx.fillRect(0, 0, this.ctx.canvas.width, this.ctx.canvas.height);
  }

  button(r: Rect, label: string, opts: { disabled?: boolean; scale?: number } = {}): boolean {
    const hot = !opts.disabled && this.hover(r);
    const down = hot && this.input.down && this.inside(r, this.input.pressX, this.input.pressY);
    const kind: PanelKind = opts.disabled ? 'btn_disabled' : down ? 'btn_down' : hot ? 'btn_hover' : 'btn';
    this.nine(kind, r);
    const scale = opts.scale ?? 1;
    const ty = r.y + Math.floor((r.h - 1 - 7 * scale) / 2) + (down ? 1 : 0);
    this.text(label, r.x + r.w / 2, ty, opts.disabled ? '#877a80' : C.ink, { align: 'center', scale });
    const hit = !opts.disabled && this.clicked(r);
    if (hit) this.sfx.play('click');
    return hit;
  }

  // ------------------------------------------------------ overlays ------

  /** Draw on top of everything at the end of the frame (tooltips). */
  overlay(fn: () => void): void {
    this.overlays.push(fn);
  }

  /** Dark tooltip box near the cursor, kept on-screen. `body` draws inside (x, y). */
  tooltip(w: number, h: number, body: (x: number, y: number) => void): void {
    const mx = this.input.x;
    const my = this.input.y;
    this.overlay(() => {
      let x = mx + 14;
      let y = my + 10;
      if (x + w > this.ctx.canvas.width - 4) x = mx - w - 8;
      if (y + h > this.ctx.canvas.height - 4) y = this.ctx.canvas.height - h - 4;
      this.nine('panel_dark', { x, y, w, h });
      body(x + 8, y + 7);
    });
  }

  floater(text: string, x: number, y: number, color: string): void {
    this.floaters.push({ text, x, y, color, age: 0 });
  }

  toast(text: string): void {
    this.toastText = text;
    this.toastAge = 0;
  }

  /** Big centre-screen text that pops in, wobbles, and fades out (e.g. "Last Day!"). */
  announce(text: string): void {
    this.announceText = text;
    this.announceAge = 0;
  }

  begin(dt: number): void {
    this.t += dt;
    for (const f of this.floaters) f.age += dt;
    this.floaters = this.floaters.filter((f) => f.age < 1.1);
    this.toastAge += dt;
    this.announceAge += dt;
  }

  end(): void {
    this.active = true;
    for (const f of this.floaters) {
      const y = f.y - f.age * 28;
      this.text(f.text, f.x, y, f.color, { align: 'center', shadow: C.shadow });
    }
    if (this.toastAge < 2.4) {
      const w = this.font.measure(this.toastText, 2) + 32;
      const slide = Math.min(1, this.toastAge * 6) * Math.min(1, (2.4 - this.toastAge) * 6);
      const y = Math.round(-40 + slide * 76);
      this.nine('panel_dark', { x: (W - w) / 2, y, w, h: 30 });
      this.text(this.toastText, W / 2, y + 8, C.gold, { align: 'center', scale: 2, shadow: C.shadow });
    }
    if (this.announceAge < ANNOUNCE_T) this.drawAnnounce();
    for (const fn of this.overlays) fn();
    this.overlays = [];
  }

  private drawAnnounce(): void {
    const { ctx } = this;
    const a = this.announceAge;
    const alpha = Math.min(1, a / 0.12, (ANNOUNCE_T - a) / 0.4);
    // dark band that opens from the middle
    const bandH = Math.round(76 * Math.min(1, a / 0.2));
    ctx.fillStyle = `rgba(20,14,32,${0.6 * alpha})`;
    ctx.fillRect(0, Math.round(H / 2 - bandH / 2), W, bandH);
    // pop in with an overshoot, then a wobble that settles
    const p = Math.min(1, a / 0.35) - 1;
    const pop = 1 + 2.70158 * p * p * p + 1.70158 * p * p;
    const rot = Math.sin(a * 14) * 0.07 * Math.max(0, 1 - a / 1.2);
    const scale = 5;
    const y = -Math.round((7 * scale) / 2);
    ctx.save();
    ctx.globalAlpha = Math.max(0, alpha);
    ctx.translate(W / 2, H / 2);
    ctx.rotate(rot);
    ctx.scale(pop, pop);
    for (const [dx, dy] of [[-2, 0], [2, 0], [0, -2], [0, 3], [2, 3], [-2, 3]])
      this.text(this.announceText, dx, y + dy, C.shadow, { align: 'center', scale });
    this.text(this.announceText, 0, y, C.gold, { align: 'center', scale });
    ctx.restore();
  }
}
