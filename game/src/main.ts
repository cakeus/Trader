import { App } from './app';
import { Assets, loadJSON } from './engine/assets';
import { Sfx } from './engine/audio';
import { Font, type FontMeta } from './engine/font';
import { Input } from './engine/input';
import { createScreen } from './engine/screen';
import { loadSettings } from './engine/settings';
import { Ui } from './engine/ui';
import { loadData } from './game/data';
import { MainMenu } from './scenes/mainMenu';

const UI_IMAGES = [
  'panel', 'panel_dark', 'btn', 'btn_hover', 'btn_down', 'btn_disabled', 'row', 'row_hover', 'cursor',
  'icon_coin', 'icon_bag', 'icon_calendar', 'icon_check', 'icon_pin', 'icon_star', 'icon_flag', 'stamp', 'stamp_rare',
].map((n) => `assets/ui/${n}.png`);

async function boot(): Promise<void> {
  const screen = createScreen(document.getElementById('screen') as HTMLCanvasElement);
  const [data, fontMeta] = await Promise.all([loadData(), loadJSON<FontMeta>('assets/font/font.json')]);

  const assets = new Assets();
  await assets.load([
    ...UI_IMAGES,
    'assets/font/font.png',
    ...Object.values(data.areas).map((a) => a.map),
    ...Object.values(data.goods).flatMap((g) => [g.icon, g.iconSmall, g.iconMedium]),
    ...Object.values(data.actors).map((a) => a.portrait),
    data.dealer.portrait,
    ...Object.values(data.locations).map((l) => l.background),
  ]);

  const font = new Font(assets.get('assets/font/font.png')!, fontMeta);
  const input = new Input();
  const sfx = new Sfx();
  input.attach(screen, () => sfx.unlock());
  const syncHidden = () => (sfx.hidden = document.hidden);
  document.addEventListener('visibilitychange', syncHidden);
  window.addEventListener('pagehide', () => (sfx.hidden = true));
  window.addEventListener('pageshow', syncHidden);
  syncHidden();
  const ui = new Ui(screen.ctx, font, assets, input, sfx);
  const app = new App(screen, ui, data, assets, input, sfx, loadSettings());
  app.goto(new MainMenu(app));

  // `?timer` drives frames with setTimeout so the game keeps ticking in a hidden
  // window (handy for automated browser testing); normally we use rAF.
  const schedule: (cb: (now: number) => void) => void = new URLSearchParams(location.search).has('timer')
    ? (cb) => setTimeout(() => cb(performance.now()), 16)
    : (cb) => requestAnimationFrame(cb);
  let last = performance.now();
  const loop = (now: number) => {
    const dt = Math.min(0.1, (now - last) / 1000);
    last = now;
    app.frame(dt);
    schedule(loop);
  };
  schedule(loop);
}

boot().catch((e) => {
  console.error(e);
  document.body.innerHTML = `<pre style="color:#fbf1dc;padding:16px">${String(e)}</pre>`;
});
