export interface FontMeta {
  height: number;
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

  /** Greedy word wrap to `maxW` pixels. */
  wrap(text: string, maxW: number, scale = 1): string[] {
    const lines: string[] = [];
    let line = '';
    for (const word of text.split(' ')) {
      const next = line ? `${line} ${word}` : word;
      if (line && this.measure(next, scale) > maxW) {
        lines.push(line);
        line = word;
      } else {
        line = next;
      }
    }
    if (line) lines.push(line);
    return lines;
  }
}
