export type SfxName = 'click' | 'open' | 'buy' | 'sell' | 'deny' | 'day' | 'quota' | 'fail' | 'lastDay';

interface Note {
  f: number;
  /** Optional slide target frequency. */
  to?: number;
  t: number;
  d: number;
  type?: OscillatorType;
  v?: number;
}

const SFX: Record<SfxName, Note[]> = {
  click: [{ f: 660, t: 0, d: 0.04, type: 'square', v: 0.05 }],
  open: [
    { f: 520, t: 0, d: 0.05, type: 'triangle' },
    { f: 780, t: 0.05, d: 0.07, type: 'triangle' },
  ],
  buy: [
    { f: 440, t: 0, d: 0.05, type: 'square', v: 0.05 },
    { f: 330, t: 0.05, d: 0.08, type: 'square', v: 0.05 },
  ],
  sell: [
    { f: 988, t: 0, d: 0.05, type: 'square', v: 0.05 },
    { f: 1319, t: 0.05, d: 0.12, type: 'square', v: 0.05 },
  ],
  deny: [{ f: 180, to: 120, t: 0, d: 0.12, type: 'sawtooth', v: 0.04 }],
  day: [
    { f: 392, t: 0, d: 0.1, type: 'triangle' },
    { f: 523, t: 0.1, d: 0.1, type: 'triangle' },
    { f: 659, t: 0.2, d: 0.18, type: 'triangle' },
  ],
  quota: [
    { f: 523, t: 0, d: 0.08, type: 'square', v: 0.05 },
    { f: 659, t: 0.08, d: 0.08, type: 'square', v: 0.05 },
    { f: 784, t: 0.16, d: 0.08, type: 'square', v: 0.05 },
    { f: 1047, t: 0.24, d: 0.25, type: 'square', v: 0.05 },
  ],
  lastDay: [
    { f: 659, t: 0, d: 0.07, type: 'square', v: 0.05 },
    { f: 784, t: 0.08, d: 0.07, type: 'square', v: 0.05 },
    { f: 988, t: 0.16, d: 0.07, type: 'square', v: 0.05 },
    { f: 1319, t: 0.26, d: 0.12, type: 'square', v: 0.045 },
    { f: 1319, t: 0.26, d: 0.6, type: 'triangle', v: 0.07 },
    { f: 988, t: 0.5, d: 0.08, type: 'square', v: 0.035 },
    { f: 1319, t: 0.6, d: 0.35, type: 'square', v: 0.035 },
  ],
  fail: [
    { f: 392, t: 0, d: 0.18, type: 'triangle' },
    { f: 330, t: 0.18, d: 0.18, type: 'triangle' },
    { f: 262, to: 196, t: 0.36, d: 0.4, type: 'triangle' },
  ],
};

/** Music volume (0..1), kept under the sfx so they mix well. */
const MUSIC_VOLUME = 0.1;
/** Seconds to fade one track out and the next in. */
export const MUSIC_FADE = 1.5;

interface Track {
  src: string;
  el: HTMLAudioElement;
  /** Fade level 0..1, times MUSIC_VOLUME. */
  level: number;
  /** Seconds this track's current fade (in or out) takes. */
  fade: number;
}

/** Tiny procedural chiptune blips via WebAudio, plus looping background music. */
export class Sfx {
  private ctx: AudioContext | null = null;
  private _muted = false;
  private _musicMuted = false;
  /** The track that should be playing, and any still fading out. */
  private track: Track | null = null;
  private fading: Track[] = [];

  /** Sound effects off. */
  get muted(): boolean {
    return this._muted;
  }

  set muted(m: boolean) {
    this._muted = m;
  }

  /** Music off (pauses it). */
  get musicMuted(): boolean {
    return this._musicMuted;
  }

  set musicMuted(m: boolean) {
    this._musicMuted = m;
    for (const t of this.tracks()) {
      if (m) t.el.pause();
      else this.start(t);
    }
  }

  /** Loop `src` as the background music, crossfading from whatever was playing over `fade`
   *  seconds (null fades to silence). Cheap to call every frame: nothing happens while it's
   *  already the current track. */
  music(src: string | null, fade = MUSIC_FADE): void {
    if ((this.track?.src ?? null) === src) return;
    if (this.track) {
      this.track.fade = fade;
      this.fading.push(this.track);
      this.track = null;
    }
    if (src === null) return;
    const back = this.fading.findIndex((t) => t.src === src);
    if (back >= 0) {
      this.track = this.fading.splice(back, 1)[0];
    } else {
      const el = new Audio(encodeURI(src));
      el.loop = true;
      el.volume = 0;
      this.track = { src, el, level: 0, fade };
    }
    this.track.fade = fade;
    this.start(this.track);
  }

  /** Advance the music fades (call once a frame). */
  update(dt: number): void {
    const d = Math.max(0, dt); // the first frame's dt can be slightly negative
    if (this.track) this.track.level = Math.min(1, this.track.level + d / this.track.fade);
    for (const t of this.fading) t.level = Math.max(0, t.level - d / t.fade);
    for (const t of this.fading.filter((f) => f.level <= 0)) t.el.pause();
    this.fading = this.fading.filter((f) => f.level > 0);
    for (const t of this.tracks()) t.el.volume = Math.min(1, Math.max(0, t.level * MUSIC_VOLUME));
  }

  private tracks(): Track[] {
    return this.track ? [this.track, ...this.fading] : [...this.fading];
  }

  /** Play a track unless the music is off; browsers refuse before the first user gesture, so unlock retries. */
  private start(t: Track): void {
    if (this._musicMuted || !t.el.paused) return;
    t.el.play().catch(() => {});
  }

  /** Browsers only allow audio after a user gesture. */
  unlock(): void {
    if (!this.ctx) {
      try {
        this.ctx = new AudioContext();
      } catch {
        return;
      }
    }
    if (this.ctx.state === 'suspended') void this.ctx.resume();
    if (this.track) this.start(this.track);
  }

  play(name: SfxName): void {
    const ctx = this.ctx;
    if (!ctx || this.muted) return;
    const now = ctx.currentTime;
    for (const n of SFX[name]) {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = n.type ?? 'square';
      osc.frequency.setValueAtTime(n.f, now + n.t);
      if (n.to) osc.frequency.linearRampToValueAtTime(n.to, now + n.t + n.d);
      const v = n.v ?? 0.08;
      gain.gain.setValueAtTime(0, now + n.t);
      gain.gain.linearRampToValueAtTime(v, now + n.t + 0.005);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + n.t + n.d);
      osc.connect(gain).connect(ctx.destination);
      osc.start(now + n.t);
      osc.stop(now + n.t + n.d + 0.02);
    }
  }
}
