import type { Assets } from './engine/assets';
import type { Sfx } from './engine/audio';
import type { Input } from './engine/input';
import { H, W } from './engine/screen';
import type { Ui } from './engine/ui';
import { clearRun, saveRun } from './game/save';
import type { GameData, RunState } from './game/types';

export interface Scene {
  frame(ui: Ui, dt: number): void;
}

/** Owns the scene stack, the current run, and the frame loop. */
export class App {
  scenes: Scene[] = [];
  run: RunState | null = null;
  /** "seed:day" the "Last Day!" announcement last played for (not saved, so it replays after Continue). */
  announced = '';
  private fade = 0;

  constructor(
    readonly ctx: CanvasRenderingContext2D,
    readonly ui: Ui,
    readonly data: GameData,
    readonly assets: Assets,
    readonly input: Input,
    readonly sfx: Sfx,
  ) {}

  /** Replace the whole stack (a full screen change) with a short fade-in. */
  goto(scene: Scene): void {
    this.scenes = [scene];
    this.fade = 1;
  }

  /** Open a modal on top of the current scene. */
  push(scene: Scene): void {
    this.scenes.push(scene);
  }

  pop(scene?: Scene): void {
    if (!scene) this.scenes.pop();
    else this.scenes = this.scenes.filter((s) => s !== scene);
  }

  save(): void {
    if (this.run) saveRun(this.run);
  }

  endRun(): void {
    this.run = null;
    clearRun();
  }

  frame(dt: number): void {
    const { ctx, ui } = this;
    ui.begin(dt);
    ctx.fillStyle = '#1a1426';
    ctx.fillRect(0, 0, W, H);
    const stack = this.scenes.slice();
    stack.forEach((s, i) => {
      ui.active = i === stack.length - 1;
      s.frame(ui, dt);
    });
    ui.end();
    if (this.fade > 0) {
      ctx.fillStyle = `rgba(26,20,38,${this.fade})`;
      ctx.fillRect(0, 0, W, H);
      this.fade = Math.max(0, this.fade - dt * 4);
    }
    if (this.input.x >= 0) ui.image('assets/ui/cursor.png', this.input.x, this.input.y);
    this.input.endFrame();
  }
}
