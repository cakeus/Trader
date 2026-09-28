/** Player options, kept in localStorage apart from the run save. */
export interface Settings {
  sound: boolean;
  music: boolean;
  /** Scale the canvas to fill the window (keeping its aspect ratio) instead of by whole numbers. */
  stretch: boolean;
}

const SETTINGS_KEY = 'trader.settings';
const DEFAULTS: Settings = { sound: true, music: true, stretch: false };

export function loadSettings(): Settings {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    return { ...DEFAULTS, ...(raw ? (JSON.parse(raw) as Partial<Settings>) : {}) };
  } catch {
    return { ...DEFAULTS };
  }
}

export function saveSettings(s: Settings): void {
  try {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(s));
  } catch {
    // storage unavailable — the options just won't persist
  }
}
