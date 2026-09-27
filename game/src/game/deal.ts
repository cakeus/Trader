import { rngFor } from '../engine/rng';
import type { GameData } from './types';

const MAX_ATTEMPTS = 50;

/**
 * Deal today's actors out to the run's locations. Constraints:
 *  - each location gets exactly `actorSlots` actors (any mix of buyers and sellers);
 *  - no actor is in two places at once;
 *  - each good appears on at most one actor per location (so a location never
 *    buys and sells the same good, and never has two buyers or two sellers of it).
 * If `requireBuyerOf` is given, a random buyer of that good is placed first at a
 * random location, so at least one buyer of it is present today.
 * Deterministic for (seed, day, requireBuyerOf).
 */
export function dealActors(
  data: GameData,
  seed: number,
  day: number,
  locationIds: string[],
  requireBuyerOf?: string,
): Record<string, string[]> {
  const all = Object.keys(data.actors).sort();
  const buyersOf = requireBuyerOf
    ? all.filter((id) => data.actors[id].role === 'buyer' && data.actors[id].goods.some((g) => g.good === requireBuyerOf))
    : [];
  for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
    const pool = rngFor(seed, 'deal', day, attempt).shuffle(all);
    const used = new Set<string>();
    const placed: Record<string, string[]> = Object.fromEntries(locationIds.map((id) => [id, []]));
    if (buyersOf.length > 0) {
      const r = rngFor(seed, 'deal', day, attempt, 'guarantee');
      const buyer = buyersOf[r.int(0, buyersOf.length - 1)];
      placed[locationIds[r.int(0, locationIds.length - 1)]].push(buyer);
      used.add(buyer);
    }
    const result: Record<string, string[]> = {};
    let ok = true;
    for (const locId of locationIds) {
      const want = data.locations[locId].actorSlots;
      const here = placed[locId];
      for (const id of pool) {
        if (here.length >= want) break;
        if (used.has(id) || conflicts(data, here, id)) continue;
        here.push(id);
        used.add(id);
      }
      if (here.length < want) {
        ok = false;
        break;
      }
      result[locId] = here;
    }
    if (ok) return result;
  }
  throw new Error(`could not deal actors for day ${day}`);
}

/** Would `candidate` share a good with someone already here? Each good may appear on
 *  only one actor per location: no buy+sell, no two buyers and no two sellers of it. */
function conflicts(data: GameData, here: string[], candidate: string): boolean {
  const c = data.actors[candidate];
  return here.some((id) => data.actors[id].goods.some((g) => c.goods.some((cg) => cg.good === g.good)));
}
