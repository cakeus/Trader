export const W = 640;
export const H = 480;

export interface Screen {
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  /** Client (CSS pixel) coords -> logical 640x480 coords. */
  toLogical(clientX: number, clientY: number): { x: number; y: number };
  /** Fill the window (keeping the aspect ratio) instead of scaling by whole numbers. */
  stretch: boolean;
}

/** A fixed 640x480 canvas, scaled up by the largest whole number that fits the window
 *  (or, stretched, by whatever fits). */
export function createScreen(canvas: HTMLCanvasElement): Screen {
  canvas.width = W;
  canvas.height = H;
  const ctx = canvas.getContext('2d')!;
  ctx.imageSmoothingEnabled = false;

  let stretch = false;
  const fit = () => {
    const fits = Math.min(innerWidth / W, innerHeight / H);
    const scale = stretch ? fits : Math.max(1, Math.floor(fits));
    canvas.style.width = `${W * scale}px`;
    canvas.style.height = `${H * scale}px`;
  };
  addEventListener('resize', fit);
  fit();

  return {
    canvas,
    ctx,
    toLogical(clientX, clientY) {
      const r = canvas.getBoundingClientRect();
      return {
        x: Math.floor(((clientX - r.left) / r.width) * W),
        y: Math.floor(((clientY - r.top) / r.height) * H),
      };
    },
    get stretch() {
      return stretch;
    },
    set stretch(s: boolean) {
      stretch = s;
      fit();
    },
  };
}
