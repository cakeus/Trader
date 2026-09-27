export type SfxName = 'click' | 'open' | 'buy' | 'sell' | 'deny' | 'day' | 'quota' | 'fail';

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
  fail: [
    { f: 392, t: 0, d: 0.18, type: 'triangle' },
    { f: 330, t: 0.18, d: 0.18, type: 'triangle' },
    { f: 262, to: 196, t: 0.36, d: 0.4, type: 'triangle' },
  ],
};

/** Tiny procedural chiptune blips via WebAudio. */
export class Sfx {
  private ctx: AudioContext | null = null;
  muted = false;

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
