import type { App } from '../app';
import type { Ui } from '../engine/ui';
import { dealGood, isUniversal } from '../game/dealer';
import type { DealerDeal } from '../game/types';

/** Width and height of the stamp background (assets/ui/stamp.png). */
export const STAMP_SIZE = 42;

/** 16x16 UI icon for deals that aren't about a specific good. */
const DEAL_ICON: Partial<Record<DealerDeal['kind'], string>> = {
  bag: 'assets/ui/icon_bag.png',
  dailyDiscount: 'assets/ui/icon_tag.png',
  tip: 'assets/ui/icon_tip.png',
  cantGetEnough: 'assets/ui/icon_more.png',
};

/** A deal drawn as a postage stamp (STAMP_SIZE square): the icon of its category's good in the
 *  run's area, a 2x2 grid of the area's goods (on a purple stamp) for all-goods deals, or a UI icon. */
export function drawStamp(app: App, ui: Ui, deal: DealerDeal, x: number, y: number): void {
  const all = isUniversal(deal);
  ui.image(all ? 'assets/ui/stamp_rare.png' : 'assets/ui/stamp.png', x, y);
  const ix = x + 5;
  const iy = y + 5;
  const good = dealGood(app.data, deal, app.area);
  if (good) ui.image(app.data.goods[good].icon, ix, iy);
  else if (all)
    Object.values(app.view.goods).slice(0, 4).forEach((g, j) => {
      ui.image(g.iconSmall, ix + 5 + (j % 2) * 13, iy + 5 + Math.floor(j / 2) * 13);
    });
  else ui.image(DEAL_ICON[deal.kind]!, ix + 8, iy + 8);
}
