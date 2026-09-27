export const W = 640;
export const H = 480;

export interface Screen {
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  /** Client (CSS pixel) coords -> logical 640x480 coords. */
  toLogical(clientX: number, clientY: number): { x: number; y: number };
}

/** A fixed 640x480 canvas, scaled up by the largest whole number that fits the window. */
export function createScreen(canvas: HTMLCanvasElement): Screen {
  canvas.width = W;
  canvas.height = H;
  const ctx = canvas.getContext('2d')!;
  ctx.imageSmoothingEnabled = false;

  const fit = () => {
    const scale = Math.max(1, Math.floor(Math.min(innerWidth / W, innerHeight / H)));
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
  };
}
