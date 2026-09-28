import type { AreaDef, GameData } from './types';

const views = new WeakMap<GameData, Map<string, GameData>>();
/** The full data each view was made from. */
const roots = new WeakMap<GameData, GameData>();

/** The game data as seen from one area: only its goods, locations and actors (each actor trades
 *  one good, so it belongs to that good's area). Memoized, and a view of a view is the same view. */
export function areaView(data: GameData, areaId: string): GameData {
  data = fullData(data);
  let byArea = views.get(data);
  if (!byArea) views.set(data, (byArea = new Map()));
  let view = byArea.get(areaId);
  if (!view) {
    const inArea = (good: string) => data.goods[good]?.area === areaId;
    view = {
      ...data,
      goods: Object.fromEntries(Object.entries(data.goods).filter(([id]) => inArea(id))),
      actors: Object.fromEntries(Object.entries(data.actors).filter(([, a]) => a.goods.some((g) => inArea(g.good)))),
      locations: Object.fromEntries(Object.entries(data.locations).filter(([, l]) => l.area === areaId)),
    };
    byArea.set(areaId, view);
    roots.set(view, data);
  }
  return view;
}

/** The areas in the order the run visits them. */
export function areasInOrder(data: GameData): AreaDef[] {
  return Object.values(data.areas).sort((a, b) => a.fromDay - b.fromDay);
}

/** The area the run is in on `day`: the last one whose `fromDay` has come. */
export function areaFor(data: GameData, day: number): string {
  const areas = areasInOrder(data);
  return (areas.filter((a) => a.fromDay <= day).pop() ?? areas[0]).id;
}

/** The full data behind a view (or the data itself). */
export function fullData(data: GameData): GameData {
  return roots.get(data) ?? data;
}

/** A good's category (from any area). */
export function categoryOf(data: GameData, good: string): string {
  return fullData(data).goods[good].category;
}

/** A category's good in an area. */
export function goodOf(data: GameData, category: string, areaId: string): string {
  const g = Object.values(fullData(data).goods).find((x) => x.category === category && x.area === areaId);
  if (!g) throw new Error(`no ${category} good in ${areaId}`);
  return g.id;
}
