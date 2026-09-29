import { type Rng, rngFor } from '../engine/rng';
import { areaView, categoryOf, fullData } from './area';
import { CONFIG } from './config';
import { todayEvent } from './events';
import { type ActorGood, type GameData, type Offer, type Role, type RunState, type Tier, TIERS } from './types';

export function offerKey(actorId: string, goodId: string): string {
  return `${actorId}:${goodId}`;
}

/** Weighted pick of a deal tier (CONFIG.dealWeights by default). */
export function rollTier(r: Rng, weights: Partial<Record<Tier, number>> = CONFIG.dealWeights): Tier {
  return tierAt(r.next(), weights);
}

/** The tier at `u` (0..1) along the weights, laid end to end in TIERS order. */
export function tierAt(u: number, weights: Partial<Record<Tier, number>>): Tier {
  const total = TIERS.reduce((sum, t) => sum + (weights[t] ?? 0), 0);
  let x = u * total;
  for (const t of TIERS) {
    x -= weights[t] ?? 0;
    if (x < 0) return t;
  }
  return TIERS[TIERS.length - 1];
}

/** Card `index` of a role's tier deck for a quota: each cycle of CONFIG.deckSize cards is a
 *  shuffle of one random point in each of deckSize equal slices of 0..1, which `tierAt` turns into
 *  tiers for that actor good's weights. So a weight that's a whole number of slices comes out
 *  exactly over a cycle, and the rest are right on average. */
export function deckCard(seed: number, role: Role, quota: number, index: number): number {
  const n = CONFIG.deckSize;
  const r = rngFor(seed, 'deck', role, quota, Math.floor(index / n));
  const cards = r.shuffle([...Array(n).keys()]).map((k) => (k + r.next()) / n);
  return cards[index % n];
}

/** How many deck cards a location's offers use, per role (one per actor good). */
export function deckCards(data: GameData, state: RunState, locationId: string): Record<Role, number> {
  data = areaView(data, state.area);
  const used: Record<Role, number> = { supplier: 0, buyer: 0 };
  for (const id of state.locations.find((l) => l.id === locationId)?.actorIds ?? []) {
    used[data.actors[id].role] += data.actors[id].goods.length;
  }
  return used;
}

/** An actor good's price at a tier (sellers have no bad price and never roll one). */
export function tierPrice(prices: ActorGood['prices'], tier: Tier): number {
  const p = prices[tier];
  if (p === undefined) throw new Error(`no ${tier} price`);
  return p;
}

/** An actor good's price at a tier, with the Cramazing stamp: an Amazing deal's difference from
 *  the Good price is multiplied by CONFIG.dealer.cramazing (never below $1). */
export function dealPrice(state: RunState, prices: ActorGood['prices'], tier: Tier): number {
  const p = tierPrice(prices, tier);
  if (tier !== 'amazing' || !state.perks.owned.includes('cramazing')) return p;
  return Math.max(1, prices.good + CONFIG.dealer.cramazing * (p - prices.good));
}

/** A seller's base daily stock for a good of `category`, picked evenly from CONFIG.stockRange. */
export function rollStock(r: Rng, category: string): number {
  const range = CONFIG.stockRange[category];
  if (!range) throw new Error(`no stock range for ${category}`);
  return r.int(range[0], range[1]);
}

/** A seller's or buyer's tier weights for a good after the Dealer's luck perks (its category's, plus
 *  the all-goods one): great and amazing gain, and bad pays for both, then good once bad is gone
 *  (sellers have no bad, so good pays). */
export function tierWeights(data: GameData, state: RunState, good: string, role: Role): Partial<Record<Tier, number>> {
  const buyer = state.quota.index === 0 ? CONFIG.firstQuotaBuyerDealWeights : CONFIG.buyerDealWeights;
  const w = role === 'supplier' ? CONFIG.dealWeights : buyer;
  const s = (state.perks.luck[categoryOf(data, good)] ?? 0) + state.perks.luckAll;
  const bad = Math.max(0, (w.bad ?? 0) - 2 * s);
  const fromGood = 2 * s - ((w.bad ?? 0) - bad);
  const out = { good: Math.max(0, (w.good ?? 0) - fromGood), great: (w.great ?? 0) + s, amazing: (w.amazing ?? 0) + s };
  return w.bad === undefined ? out : { bad, ...out };
}

/** A seller's price after the Dealer's discounts on its category (the good's own `dealerDiscount`)
 *  and on everything (never below $1). */
export function sellerPrice(data: GameData, state: RunState, good: string, base: number): number {
  const off = state.perks.discounts[categoryOf(data, good)] ? fullData(data).goods[good].dealerDiscount : 0;
  return Math.max(1, base - off - state.perks.discountAll);
}

/** How much the all-goods stock deal (Overflowing Supply) multiplies every seller's stock by. */
export function stockMultiplier(state: RunState): number {
  return CONFIG.dealer.stockAll ** state.perks.stockAll;
}

/** A seller's daily stock of `good` from its rolled `base`: the category's stock deal is added,
 *  then Overflowing Supply multiplies it. */
export function sellerStock(data: GameData, state: RunState, good: string, base: number): number {
  return (base + (state.perks.stock[categoryOf(data, good)] ?? 0)) * stockMultiplier(state);
}

/** Extra daily demand a buyer of `good` has from the Dealer's demand deals. */
export function extraDemand(data: GameData, state: RunState, good: string): number {
  return (state.perks.buyerStock[categoryOf(data, good)] ?? 0) + state.perks.buyerStockAll;
}

/** Today's deal tier, price and stock/demand for every actor present in the run.
 *  With CONFIG.tierDeck, every location reads the same next cards off the decks; only the
 *  visited one uses them up (see `visit`), so it gets exactly what rolling on arrival would.
 *  A pure function of (seed, day, quota, deck position, actor, good), so it is reproducible. */
export function rollMarket(data: GameData, state: RunState): Record<string, Offer> {
  data = areaView(data, state.area);
  const market: Record<string, Offer> = {};
  // today's event can cap every buyer's demand, even when demand is otherwise unlimited
  const limit = todayEvent(data, state)?.buyerLimit;
  for (const loc of state.locations) {
    const next = { ...state.deck };
    for (const actorId of loc.actorIds) {
      const role = data.actors[actorId].role;
      const seller = role === 'supplier';
      for (const ag of data.actors[actorId].goods) {
        const r = rngFor(state.seed, 'market', state.day, actorId, ag.good);
        const roll = r.next(); // drawn either way, so stock rolls don't depend on the deck switch
        const u = CONFIG.tierDeck ? deckCard(state.seed, role, state.quota.index, next[role]++) : roll;
        const tier = tierAt(u, tierWeights(data, state, ag.good, role));
        const base = dealPrice(state, ag.prices, tier);
        const price = seller ? sellerPrice(data, state, ag.good, base) : base;
        if (seller) {
          market[offerKey(actorId, ag.good)] = { tier, price, left: sellerStock(data, state, ag.good, rollStock(r, categoryOf(data, ag.good))) };
          continue;
        }
        const demand = r.int(ag.qtyMin, ag.qtyMax) + extraDemand(data, state, ag.good);
        market[offerKey(actorId, ag.good)] =
          limit === undefined
            ? { tier, price, left: demand }
            : { tier, price, left: CONFIG.limitDemand ? Math.min(demand, limit) : limit, capped: true };
      }
    }
  }
  return market;
}
