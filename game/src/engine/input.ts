import type { Screen } from './screen';

/** Per-frame mouse/keyboard snapshot for immediate-mode UI. */
export class Input {
  x = -1;
  y = -1;
  down = false;
  /** Mouse went down this frame. */
  pressed = false;
  /** Mouse went up this frame. */
  released = false;
  pressX = -1;
  pressY = -1;
  shift = false;
  /** Keys pressed this frame (KeyboardEvent.key). */
  keys = new Set<string>();

  attach(screen: Screen, onFirstGesture: () => void): void {
    const c = screen.canvas;
    const move = (e: MouseEvent) => {
      const p = screen.toLogical(e.clientX, e.clientY);
      this.x = p.x;
      this.y = p.y;
      this.shift = e.shiftKey;
    };
    c.addEventListener('mousemove', move);
    c.addEventListener('mouseleave', () => {
      this.x = -1;
      this.y = -1;
    });
    c.addEventListener('mousedown', (e) => {
      if (e.button !== 0) return;
      move(e);
      onFirstGesture();
      this.down = true;
      this.pressed = true;
      this.pressX = this.x;
      this.pressY = this.y;
    });
    addEventListener('mouseup', (e) => {
      if (e.button !== 0 || !this.down) return;
      move(e);
      this.down = false;
      this.released = true;
    });
    // iOS only counts some events as a gesture that may start audio: touchend is the surest
    c.addEventListener('touchend', () => onFirstGesture(), { passive: true });
    c.addEventListener('contextmenu', (e) => e.preventDefault());
    addEventListener('keydown', (e) => {
      onFirstGesture();
      this.shift = e.shiftKey;
      this.keys.add(e.key);
    });
    addEventListener('keyup', (e) => {
      this.shift = e.shiftKey;
    });
  }

  endFrame(): void {
    this.pressed = false;
    this.released = false;
    this.keys.clear();
  }
}
