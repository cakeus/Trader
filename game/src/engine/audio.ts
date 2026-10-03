import { isMobile } from './device';

export type SfxName = 'click' | 'open' | 'buy' | 'sell' | 'deny' | 'day' | 'quota' | 'fail' | 'lastDay' | 'tick' | 'star';

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
  tick: [{ f: 1320, t: 0, d: 0.025, type: 'square', v: 0.025 }],
  star: [
    { f: 1047, t: 0, d: 0.06, type: 'triangle', v: 0.08 },
    { f: 1568, t: 0.06, d: 0.16, type: 'triangle', v: 0.07 },
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
/** Mobile decodes the music at this sample rate, so a 3-minute track takes about 45MB instead of
 *  70MB (desktop decodes at the context's rate). */
const MOBILE_MUSIC_RATE = 32000;

interface Track {
  src: string;
  /** Fade level 0..1, times MUSIC_VOLUME. */
  level: number;
  /** Seconds this track's current fade (in or out) takes. */
  fade: number;
  /** The decoded track, once loaded. */
  buffer?: AudioBuffer;
  loading?: boolean;
  /** Loading or decoding it failed (it stays silent). */
  failed?: boolean;
  gain?: GainNode;
  /** The playing (looping) source; none while paused or loading. */
  node?: AudioBufferSourceNode;
  /** Seconds into the track: where a paused track picks up. */
  pos: number;
  /** Context time the track's start would have been, while it plays. */
  startedAt: number;
}

/** Tiny procedural chiptune blips via WebAudio, plus looping background music. The music is
 *  decoded and played through WebAudio too, not an `<audio>` element: iOS plays those as media
 *  at the phone's media volume and ignores their `volume`, so the music drowned out the effects. */
export class Sfx {
  private ctx: AudioContext | null = null;
  private _muted = false;
  private _musicMuted = false;
  /** The page is in the background (everything paused until it's back). */
  private _hidden = false;
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
      if (m) this.stop(t);
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
    this.track = back >= 0 ? this.fading.splice(back, 1)[0] : { src, level: 0, fade, pos: 0, startedAt: 0 };
    this.track.fade = fade;
    this.start(this.track);
  }

  /** Advance the music fades (call once a frame). */
  update(dt: number): void {
    const d = Math.max(0, dt); // the first frame's dt can be slightly negative
    // the new track fades in once it's actually playing (it may still be loading)
    if (this.track?.node) this.track.level = Math.min(1, this.track.level + d / this.track.fade);
    for (const t of this.fading) t.level = Math.max(0, t.level - d / t.fade);
    for (const t of this.fading.filter((f) => f.level <= 0)) this.drop(t);
    this.fading = this.fading.filter((f) => f.level > 0);
    for (const t of this.tracks()) if (t.gain) t.gain.gain.value = Math.min(1, Math.max(0, t.level * MUSIC_VOLUME));
  }

  /** Pause everything while the page is hidden (suspending the context pauses the music too),
   *  and pick it back up when it returns. */
  set hidden(h: boolean) {
    if (this._hidden === h) return;
    this._hidden = h;
    if (!this.ctx) return;
    if (h) void this.ctx.suspend();
    else {
      void this.ctx.resume();
      if (this.track) this.start(this.track);
    }
  }

  private tracks(): Track[] {
    return this.track ? [this.track, ...this.fading] : [...this.fading];
  }

  /** Fetch and decode a track (once there's a context), then start it. */
  private load(t: Track): void {
    const ctx = this.ctx;
    if (!ctx || t.buffer || t.loading || t.failed) return;
    t.loading = true;
    // mobile decodes at a lower rate to save memory; the context resamples it as it plays
    const decoder: BaseAudioContext = isMobile ? new OfflineAudioContext(2, 1, MOBILE_MUSIC_RATE) : ctx;
    fetch(encodeURI(t.src))
      .then((r) => {
        if (!r.ok) throw new Error(`${t.src}: ${r.status}`);
        return r.arrayBuffer();
      })
      .then((data) => new Promise<AudioBuffer>((ok, fail) => decoder.decodeAudioData(data, ok, fail)))
      .then((buffer) => {
        t.buffer = buffer;
        t.loading = false;
        // still wanted? (it may have faded out, or another track come in, while it loaded)
        if (this.tracks().includes(t)) this.start(t);
      })
      .catch(() => {
        t.loading = false;
        t.failed = true;
      });
  }

  /** Play a track (from where it paused) unless the music is off or the page hidden; before the
   *  first user gesture there's no context yet, so unlock retries. */
  private start(t: Track): void {
    const ctx = this.ctx;
    if (!ctx || this._musicMuted || this._hidden || t.node) return;
    if (!t.buffer) {
      this.load(t);
      return;
    }
    if (!t.gain) {
      t.gain = ctx.createGain();
      t.gain.gain.value = t.level * MUSIC_VOLUME;
      t.gain.connect(ctx.destination);
    }
    const node = ctx.createBufferSource();
    node.buffer = t.buffer;
    node.loop = true;
    node.connect(t.gain);
    const pos = t.pos % t.buffer.duration;
    node.start(0, pos);
    t.node = node;
    t.startedAt = ctx.currentTime - pos;
  }

  /** Pause a track, remembering where. */
  private stop(t: Track): void {
    if (!t.node || !this.ctx || !t.buffer) return;
    t.pos = (this.ctx.currentTime - t.startedAt) % t.buffer.duration;
    t.node.stop();
    t.node.disconnect();
    t.node = undefined;
  }

  /** A track that's faded out: stop it and let its buffer go. */
  private drop(t: Track): void {
    this.stop(t);
    t.gain?.disconnect();
    t.gain = undefined;
    t.buffer = undefined;
  }

  /** Browsers only allow audio after a user gesture (called on every tap, click and key). */
  unlock(): void {
    if (!this.ctx) {
      // iOS Safari plays WebAudio as "ambient" sound, which the silent switch mutes (the music's
      // <audio> isn't); a "playback" session plays the effects like the music (Safari 16.4+)
      const session = (navigator as Navigator & { audioSession?: { type: string } }).audioSession;
      if (session) {
        try {
          session.type = 'playback';
        } catch {
          // not allowed here; the effects just follow the silent switch
        }
      }
      try {
        this.ctx = new AudioContext();
      } catch {
        return;
      }
    }
    // iOS leaves the context 'interrupted' (not 'suspended') after a call, Siri or an app switch
    if (this.ctx.state !== 'running' && !this._hidden) void this.ctx.resume();
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
