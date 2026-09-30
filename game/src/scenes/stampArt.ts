import type { App } from '../app';
import { C, type Ui } from '../engine/ui';
import { dealGood, isUniversal, rarityOf } from '../game/dealer';
import type { DealerDeal, Rarity } from '../game/types';

/** Width and height of the stamp background (assets/ui/stamp.png). */
export const STAMP_SIZE = 42;

/** 16x16 UI icon for deals that aren't about a specific good. */
const DEAL_ICON: Partial<Record<DealerDeal['kind'], string>> = {
  bag: 'icon_bag',
  dailyDiscount: 'icon_tag',
  tip: 'icon_tip',
  cantGetEnough: 'icon_more',
  collector: 'icon_collector',
  birdsEye: 'icon_eye',
  haggler: 'icon_haggle',
  fannyPack: 'icon_fannypack',
  packedHouse: 'icon_crowd',
  cramazing: 'icon_sparkle',
  mixedBag: 'icon_mixed',
  lastCall: 'icon_bell',
  bigTipper: 'icon_bigtip',
  fuzzyDice: 'icon_dice',
  sleepingBag: 'icon_sleepbag',
  campFire: 'icon_fire',
  monocle: 'icon_monocle',
  detour: 'icon_detour',
  vintage: 'icon_vintage',
  cleanSweep: 'icon_broom',
  flipper: 'icon_flip',
  perfectPlanner: 'icon_planner',
  dumpTruck: 'icon_truck',
};

/** Stamp backgrounds by rarity. */
const FRAME: Record<Rarity, string> = { common: 'stamp', rare: 'stamp_blue', epic: 'stamp_gold' };

/** Every image a stamp can draw (for preloading). */
export const STAMP_IMAGES = [...Object.values(DEAL_ICON), ...Object.values(FRAME)].map((n) => `assets/ui/${n}.png`);

/** How each rarity is labelled, in its color on light panels (`dark`) and dark tooltips (`light`).
 *  Common isn't labelled. */
export const RARITY_LABEL: Record<Rarity, { text: string; dark: string; light: string } | null> = {
  common: null,
  rare: { text: 'Rare', dark: '#3a6aa8', light: C.sky },
  epic: { text: 'Epic', dark: '#b8761c', light: '#ffb050' }, // STAR_INK (common.ts imports this file)
};

/** A deal drawn as a postage stamp (STAMP_SIZE square), framed by its rarity: the icon of its
 *  category's good in the run's area, a 2x2 grid of the area's goods for all-goods deals, or a
 *  UI icon. */
export function drawStamp(app: App, ui: Ui, deal: DealerDeal, x: number, y: number): void {
  const all = isUniversal(deal);
  ui.image(`assets/ui/${FRAME[rarityOf(deal)]}.png`, x, y);
  const ix = x + 5;
  const iy = y + 5;
  const good = dealGood(app.data, deal, app.area);
  if (good) ui.image(app.data.goods[good].icon, ix, iy);
  else if (all)
    Object.values(app.view.goods).slice(0, 4).forEach((g, j) => {
      ui.image(g.iconSmall, ix + 5 + (j % 2) * 13, iy + 5 + Math.floor(j / 2) * 13);
    });
  else ui.image(`assets/ui/${DEAL_ICON[deal.kind]!}.png`, ix + 8, iy + 8);
}
