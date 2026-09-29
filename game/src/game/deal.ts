import { rngFor } from '../engine/rng';
import type { GameData } from './types';

const MAX_ATTEMPTS = 50;
/** Rerolls of one location before the whole deal is retried. */
const LOCATION_REROLLS = 20;

/**
 * Deal today's actors out to the run's locations. Constraints:
 *  - each location gets exactly `actorSlots` actors (any mix of buyers and sellers), except
 *    `dealerAt`, which gets one fewer because the Dealer takes that spot, and `extraAt` (the
 *    Packed House stamp), which gets one more;
 *  - no actor is in two places at once;
 *  - each good appears on at most one actor per location (so a location never
 *    buys and sells the same good, and never has two buyers or two sellers of it);
 *  - no two locations buy and sell exactly the same goods (a location that matches an
 *    earlier one is rerolled from the actors still free);
 *  - with `needSeller` (the player's bag is empty), no location has only buyers: it would
 *    have nothing to offer, so it's rerolled the same way.
 * For each good in `requireBuyersOf`, a random buyer of it is placed first at a random location
 * (the next one with room, if that one is full), so at least one buyer of it is present today.
 * Deterministic for (seed, day, requireBuyersOf, dealerAt, needSeller, extraAt).
 */
export function dealActors(
  data: GameData,
  seed: number,
  day: number,
  locationIds: string[],
  requireBuyersOf: string[] = [],
  dealerAt?: string,
  needSeller = false,
  extraAt?: string | null,
): Record<string, string[]> {
  const all = Object.keys(data.actors).sort();
  const buyersOf = [...new Set(requireBuyersOf)].map((good) =>
    all.filter((id) => data.actors[id].role === 'buyer' && data.actors[id].goods.some((g) => g.good === good)),
  );
  const wants: Record<string, number> = Object.fromEntries(
    locationIds.map((id) => [id, data.locations[id].actorSlots - (id === dealerAt ? 1 : 0) + (id === extraAt ? 1 : 0)]),
  );
  for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
    const pool = rngFor(seed, 'deal', day, attempt).shuffle(all);
    const used = new Set<string>();
    const placed: Record<string, string[]> = Object.fromEntries(locationIds.map((id) => [id, []]));
    buyersOf.forEach((buyers, k) => {
      if (buyers.length === 0) return;
      // the first guarantee keeps the rolls it had when there could only be one
      const r = k === 0 ? rngFor(seed, 'deal', day, attempt, 'guarantee') : rngFor(seed, 'deal', day, attempt, 'guarantee', k);
      const buyer = buyers[r.int(0, buyers.length - 1)];
      const first = r.int(0, locationIds.length - 1);
      for (let i = 0; i < locationIds.length; i++) {
        const locId = locationIds[(first + i) % locationIds.length];
        if (placed[locId].length >= wants[locId] || conflicts(data, placed[locId], buyer)) continue;
        placed[locId].push(buyer);
        used.add(buyer);
        return;
      }
    });
    const result: Record<string, string[]> = {};
    let ok = true;
    const seen = new Set<string>();
    for (const locId of locationIds) {
      const want = wants[locId];
      const start = placed[locId];
      let here: string[] = [];
      const bad = () => seen.has(signature(data, here)) || (needSeller && buyersOnly(data, here));
      // the first try uses the deal's own order; a location matching an earlier one is rerolled
      for (let reroll = 0; reroll <= LOCATION_REROLLS; reroll++) {
        const order = reroll === 0 ? pool : rngFor(seed, 'deal', day, attempt, locId, reroll).shuffle(all);
        here = [...start];
        for (const id of order) {
          if (here.length >= want) break;
          if (used.has(id) || conflicts(data, here, id)) continue;
          here.push(id);
        }
        if (here.length < want || !bad()) break;
      }
      if (here.length < want || bad()) {
        ok = false;
        break;
      }
      for (const id of here) used.add(id);
      seen.add(signature(data, here));
      result[locId] = here;
    }
    if (ok) return result;
  }
  throw new Error(`could not deal actors for day ${day}`);
}

/** What a location trades, from the player's side: the goods its buyers take | its sellers' goods. */
function signature(data: GameData, ids: string[]): string {
  const goods = (role: string) =>
    ids.filter((id) => data.actors[id].role === role).flatMap((id) => data.actors[id].goods.map((g) => g.good)).sort();
  return `${goods('buyer').join(',')}|${goods('supplier').join(',')}`;
}

/** Does a location have no sellers (only buyers, or nobody)? */
function buyersOnly(data: GameData, ids: string[]): boolean {
  return !ids.some((id) => data.actors[id].role === 'supplier');
}

/** Would `candidate` share a good with someone already here? Each good may appear on
 *  only one actor per location: no buy+sell, no two buyers and no two sellers of it. */
function conflicts(data: GameData, here: string[], candidate: string): boolean {
  const c = data.actors[candidate];
  return here.some((id) => data.actors[id].goods.some((g) => c.goods.some((cg) => cg.good === g.good)));
}
