import type { Assets } from './assets';
import { isMobile } from './device';
import type { Sfx } from './audio';
import type { Fonts, TextOpts } from './font';
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
  /** Festive lantern orange (Fireworks Night). */
  festive: '#ffac5e',
};

export type PanelKind = 'panel' | 'panel_dark' | 'row' | 'row_hover' | 'btn' | 'btn_hover' | 'btn_down' | 'btn_disabled';

interface Floater {
  text: string;
  x: number;
  y: number;
  color: string;
  age: number;
}

/** A button under a tapped item's tooltip (touch screens only). */
export interface TipAction {
  label: string;
  onClick: () => void;
  /** Grayed out and not clickable. */
  disabled?: boolean;
}

/** A corner of the screen a touch tooltip can dock in (`ui.tooltip`'s `dock`). */
export type TipCorner = 'topLeft' | 'topRight' | 'bottomLeft' | 'bottomRight';

const CORNER = 8;
const TIP_BTN_H = isMobile ? 30 : 22;
/** Mobile tooltips are a sheet across the screen, docked at the bottom, or at this y (under the
 *  HUD) when the item tapped is low on the screen (its middle below `SHEET_FLIP` of the height). */
const SHEET_TOP = 44;
const SHEET_FLIP = 0.6;
/** A docked tooltip is half the screen wide, between the HUD and `DOCK_BOTTOM` (clear of the bag
 *  and the Day box along the bottom). */
const DOCK_W = W / 2 - 8;
const DOCK_BOTTOM = H - 60;
const TOAST_H = isMobile ? 38 : 30;
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
  /** Touch screens can't hover: tapping an item picks it, which shows its tooltip (anchored to
   *  it, with action buttons) until the next tap elsewhere. */
  readonly touch = isMobile;
  /** The pitch of stacked lines of detail text (tooltips, tables): 12px, or 17 with mobile's big font. */
  readonly lh = isMobile ? 17 : 12;
  private picked: string | null = null;
  private pickedRect: Rect | null = null;
  private pickedSeen = false;
  /** The picked item's tooltip as drawn last frame; taps inside it only reach its buttons. */
  private popup: Rect | null = null;
  private inPopup = false;
  /** This frame's tap landed on a pickable item or the popup (so it doesn't unpick). */
  private tapUsed = false;

  constructor(
    readonly ctx: CanvasRenderingContext2D,
    readonly font: Fonts,
    readonly assets: Assets,
    readonly input: Input,
    readonly sfx: Sfx,
  ) {}

  // ------------------------------------------------------------ input ---

  inside(r: Rect, x = this.input.x, y = this.input.y): boolean {
    return x >= r.x && y >= r.y && x < r.x + r.w && y < r.y + r.h;
  }

  /** The pointer is over `r` (on touch screens, only while a finger is down on it). */
  hover(r: Rect): boolean {
    return this.active && this.inside(r) && (!this.touch || this.input.down) && !this.underPopup();
  }

  /** Mouse pressed and released inside `r`. */
  clicked(r: Rect): boolean {
    const i = this.input;
    return this.active && i.released && this.inside(r) && this.inside(r, i.pressX, i.pressY) && !this.underPopup();
  }

  /** The press is on the picked item's tooltip, and this isn't the tooltip asking. */
  private underPopup(): boolean {
    const i = this.input;
    return this.touch && !this.inPopup && this.popup !== null && this.inside(this.popup, i.pressX, i.pressY);
  }

  /** Whether an item with a tooltip should show it: hovered with a mouse, or on touch screens
   *  picked by a tap (a second tap on it, or a tap anywhere else, puts it away). `key` names
   *  the item and must be unique among what's on screen. */
  focus(key: string, r: Rect): boolean {
    if (!this.touch) return this.hover(r);
    if (!this.active) return false;
    if (this.clicked(r)) {
      this.tapUsed = true;
      this.picked = this.picked === key ? null : key;
      if (this.picked === null) this.popup = null;
    }
    if (this.picked !== key) return false;
    this.pickedRect = r;
    this.pickedSeen = true;
    return true;
  }

  /** A click that acts on an item directly (desktop only: on touch screens a tap picks it and
   *  its tooltip's buttons act). */
  activated(r: Rect): boolean {
    return !this.touch && this.clicked(r);
  }

  /** A click that started and ended outside `r` (e.g. to dismiss a dialog). */
  clickedOutside(r: Rect): boolean {
    const i = this.input;
    return this.active && i.released && !this.inside(r) && !this.inside(r, i.pressX, i.pressY) && !this.underPopup();
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

  /** How wide a tooltip asked to be `w` wide has inside for its body (the mobile sheet is wider,
   *  a docked one half the screen). */
  tipWidth(w: number, dock?: TipCorner): number {
    if (!this.touch) return w - 16;
    return dock ? DOCK_W - 20 : W - 36;
  }

  /** The y to draw text at `scale` so its capitals sit centred in a box at `y`, `h` tall. */
  vcenter(y: number, h: number, scale = 1): number {
    return y + Math.floor((h - 1 - this.font.cap(scale)) / 2);
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
    const ty = this.vcenter(r.y, r.h, scale) + (down ? 1 : 0);
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

  /** Dark tooltip box near the cursor, kept on-screen. `body` draws inside (x, y), `w` wide. On
   *  touch screens it's a sheet across the screen, away from the picked item, with `actions` as
   *  buttons along its bottom (`w` is then the sheet's width; `h` is still the caller's). With a
   *  `dock`, the touch tooltip is half the screen wide, always in that corner. */
  tooltip(w: number, h: number, body: (x: number, y: number, w: number) => void, actions: TipAction[] = [], dock?: TipCorner): void {
    if (this.touch && this.pickedRect) {
      this.pickedTooltip(this.pickedRect, h, body, actions, dock);
      return;
    }
    const mx = this.input.x;
    const my = this.input.y;
    this.overlay(() => {
      let x = mx + 14;
      let y = my + 10;
      if (x + w > this.ctx.canvas.width - 4) x = mx - w - 8;
      if (y + h > this.ctx.canvas.height - 4) y = this.ctx.canvas.height - h - 4;
      this.nine('panel_dark', { x, y, w, h });
      body(x + 8, y + 7, w - 16);
    });
  }

  private pickedTooltip(at: Rect, h: number, body: (x: number, y: number, w: number) => void, actions: TipAction[], dock?: TipCorner): void {
    const w = dock ? DOCK_W : W - 16;
    if (actions.length > 0) h += TIP_BTN_H + 8;
    // in its corner; or across the bottom, or the top when the item is in the bottom half
    const x = dock === 'topRight' || dock === 'bottomRight' ? W - 8 - w : 8;
    const y = dock
      ? dock.startsWith('top') ? SHEET_TOP : DOCK_BOTTOM - h
      : at.y + at.h / 2 < H * SHEET_FLIP ? H - h - 8 : SHEET_TOP;
    const r: Rect = { x, y, w, h };
    this.overlay(() => {
      this.nine('panel_dark', r);
      body(x + 10, y + 8, w - 20);
      this.inPopup = true;
      const i = this.input;
      if (i.released && this.inside(r, i.pressX, i.pressY)) this.tapUsed = true;
      // the buttons share the bottom, each at most 160 wide, centred
      const gap = 8;
      const n = Math.max(1, actions.length);
      const bw = Math.min(160, (w - 20 - gap * (n - 1)) / n);
      const total = actions.length * bw + gap * (actions.length - 1);
      actions.forEach((a, j) => {
        const br: Rect = { x: Math.round(x + (w - total) / 2 + j * (bw + gap)), y: y + h - TIP_BTN_H - 8, w: Math.round(bw), h: TIP_BTN_H };
        if (this.button(br, a.label, { disabled: a.disabled })) a.onClick();
      });
      this.inPopup = false;
      this.popup = this.picked ? r : null;
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
      this.nine('panel_dark', { x: (W - w) / 2, y, w, h: TOAST_H });
      const ty = y + Math.floor((TOAST_H - this.font.cap(2)) / 2);
      this.text(this.toastText, W / 2, ty, C.gold, { align: 'center', scale: 2, shadow: C.shadow });
    }
    if (this.announceAge < ANNOUNCE_T) this.drawAnnounce();
    for (const fn of this.overlays) fn();
    this.overlays = [];
    if (this.touch) {
      // put the tooltip away on a tap elsewhere, or when its item is gone (a new screen or modal)
      if (!this.pickedSeen || (this.input.released && !this.tapUsed)) this.unpick();
      this.pickedSeen = false;
      this.tapUsed = false;
    }
  }

  /** Put away the picked item's tooltip (touch screens). */
  unpick(): void {
    this.picked = null;
    this.pickedRect = null;
    this.popup = null;
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
    const y = -Math.round(this.font.cap(scale) / 2);
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
