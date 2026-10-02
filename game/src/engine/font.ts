export interface FontMeta {
  height: number;
  /** Rows above the baseline, so also the capitals' height. */
  baseline: number;
  lineHeight: number;
  spacing: number;
  glyphs: Record<string, { x: number; w: number }>;
}

export type Align = 'left' | 'center' | 'right';

export interface TextOpts {
  scale?: number;
  align?: Align;
  /** Draw a 1px (x scale) drop shadow in this color first. */
  shadow?: string;
}

/** Bitmap font from a white glyph atlas; tinted copies are cached per color. */
export class Font {
  private tints = new Map<string, HTMLCanvasElement>();

  constructor(private atlas: HTMLImageElement, readonly meta: FontMeta) {}

  get lineHeight(): number {
    return this.meta.lineHeight;
  }

  /** How tall capitals are at `scale`. */
  cap(scale = 1): number {
    return this.meta.baseline * scale;
  }

  private tinted(color: string): HTMLCanvasElement {
    let c = this.tints.get(color);
    if (!c) {
      c = document.createElement('canvas');
      c.width = this.atlas.width;
      c.height = this.atlas.height;
      const g = c.getContext('2d')!;
      g.drawImage(this.atlas, 0, 0);
      g.globalCompositeOperation = 'source-in';
      g.fillStyle = color;
      g.fillRect(0, 0, c.width, c.height);
      this.tints.set(color, c);
    }
    return c;
  }

  private glyph(ch: string) {
    return this.meta.glyphs[ch] ?? this.meta.glyphs['?'];
  }

  measure(text: string, scale = 1): number {
    let w = 0;
    for (const ch of text) w += this.glyph(ch).w + this.meta.spacing;
    return Math.max(0, w - this.meta.spacing) * scale;
  }

  draw(ctx: CanvasRenderingContext2D, text: string, x: number, y: number, color: string, opts: TextOpts = {}): void {
    const scale = opts.scale ?? 1;
    const w = this.measure(text, scale);
    let cx = Math.round(opts.align === 'center' ? x - w / 2 : opts.align === 'right' ? x - w : x);
    const cy = Math.round(y);
    if (opts.shadow) this.draw(ctx, text, cx + scale, cy + scale, opts.shadow, { scale });
    const src = this.tinted(color);
    const h = this.meta.height;
    for (const ch of text) {
      const g = this.glyph(ch);
      ctx.drawImage(src, g.x, 0, g.w, h, cx, cy, g.w * scale, h * scale);
      cx += (g.w + this.meta.spacing) * scale;
    }
  }

  /** Greedy word wrap to `maxW` pixels. A `\n` starts a new line, and a word too long for a line
   *  of its own is broken wherever it has to be. */
  wrap(text: string, maxW: number, scale = 1): string[] {
    const lines: string[] = [];
    let line = '';
    // push the line, and keep the overflow of a word too long to fit one
    const flush = () => {
      while (line.length > 1 && this.measure(line, scale) > maxW) {
        let n = line.length - 1;
        while (n > 1 && this.measure(line.slice(0, n), scale) > maxW) n--;
        lines.push(line.slice(0, n));
        line = line.slice(n);
      }
    };
    text.split('\n').forEach((para, p) => {
      if (p > 0) {
        lines.push(line);
        line = '';
      }
      for (const word of para.split(' ')) {
        const next = line ? `${line} ${word}` : word;
        if (line && this.measure(next, scale) > maxW) {
          lines.push(line);
          line = word;
        } else {
          line = next;
        }
        flush();
      }
    });
    if (line) lines.push(line);
    return lines;
  }
}

/** The game's text: the small font, plus on mobile a bigger one for detail text (scale 1 and 2;
 *  scale 3 and up stay the small font scaled). Same calls as a `Font`; each picks by its scale. */
export class Fonts {
  constructor(readonly small: Font, readonly detail: Font = small) {}

  /** The font text at `scale` is drawn with. */
  at(scale = 1): Font {
    return scale <= 2 ? this.detail : this.small;
  }

  /** The detail font's line height (scale-1 text). */
  get lineHeight(): number {
    return this.detail.lineHeight;
  }

  cap(scale = 1): number {
    return this.at(scale).cap(scale);
  }

  measure(text: string, scale = 1): number {
    return this.at(scale).measure(text, scale);
  }

  draw(ctx: CanvasRenderingContext2D, text: string, x: number, y: number, color: string, opts: TextOpts = {}): void {
    this.at(opts.scale).draw(ctx, text, x, y, color, opts);
  }

  wrap(text: string, maxW: number, scale = 1): string[] {
    return this.at(scale).wrap(text, maxW, scale);
  }
}
