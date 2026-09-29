import type { Assets } from './engine/assets';
import { MUSIC_FADE, type Sfx } from './engine/audio';
import type { Input } from './engine/input';
import { isMobile } from './engine/device';
import { H, W, type Screen } from './engine/screen';
import { saveSettings, type Settings } from './engine/settings';
import type { Ui } from './engine/ui';
import { areaFor, areasInOrder, areaView } from './game/area';
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
  /** During the move: plays this area's music instead of the run's (null for silence), and
   *  changes track over `musicFade` seconds. Undefined follows the run. */
  musicArea: string | null | undefined = undefined;
  /** The saved run's area, shown and played on the title screen while there's no run loaded. */
  titleArea: string | null = null;
  musicFade = MUSIC_FADE;
  private fade = 0;
  readonly ctx: CanvasRenderingContext2D;

  constructor(
    readonly screen: Screen,
    readonly ui: Ui,
    readonly data: GameData,
    readonly assets: Assets,
    readonly input: Input,
    readonly sfx: Sfx,
    readonly settings: Settings,
  ) {
    this.ctx = screen.ctx;
    this.applySettings();
  }

  /** Push `settings` out to the sound and screen, and remember them. */
  applySettings(): void {
    const s = this.settings;
    this.sfx.muted = !s.sound;
    this.sfx.musicMuted = !s.music;
    // whole-number scaling breaks on phones, so they always stretch
    this.screen.stretch = s.stretch || isMobile;
    saveSettings(s);
  }

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

  /** The run's area (the first area when there's no run). */
  get area(): string {
    return this.run?.area ?? areaFor(this.data, 1);
  }

  /** The game data as seen from the run's area: its goods and locations, actors trading its goods. */
  get view(): GameData {
    return areaView(this.data, this.area);
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
    // the run's area music, or on the title screen the saved run's (else the first area's)
    const area = this.musicArea === undefined ? (this.run?.area ?? this.titleArea ?? undefined) : this.musicArea;
    const music = area === null ? null : (area ? this.data.areas[area] : areasInOrder(this.data)[0]).music;
    this.sfx.music(music, this.musicFade);
    this.sfx.update(dt);
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
    // touch screens have no pointer to show
    if (this.input.x >= 0 && !isMobile) ui.image('assets/ui/cursor.png', this.input.x, this.input.y);
    this.input.endFrame();
  }
}
