import type { ActorDef, AreaDef, CategoryDef, DealerDef, GameData, GoodDef, LocationDef } from './types';

function byId<T extends { id: string }>(list: T[]): Record<string, T> {
  return Object.fromEntries(list.map((x) => [x.id, x]));
}

/** Build lookup tables and check cross-references; throws on bad data. */
export function buildData(
  goods: GoodDef[],
  actors: ActorDef[],
  locations: LocationDef[],
  dealer: DealerDef,
  categories: CategoryDef[],
  areas: AreaDef[],
): GameData {
  const data: GameData = {
    goods: byId(goods), actors: byId(actors), locations: byId(locations), dealer,
    categories: byId(categories), areas: byId(areas),
  };
  const errors: string[] = [];
  if (!areas.some((a) => a.fromDay === 1)) errors.push('no area starts on day 1');
  for (const area of areas) {
    // every category has exactly one good here
    for (const c of categories) {
      const n = goods.filter((g) => g.area === area.id && g.category === c.id).length;
      if (n !== 1) errors.push(`area ${area.id}: ${n} ${c.id} goods (want 1)`);
    }
    const cast = actors.filter((a) => a.goods.some((g) => data.goods[g.good]?.area === area.id)).length;
    const here = locations.filter((l) => l.area === area.id);
    const slots = here.reduce((sum, l) => sum + l.actorSlots, 0);
    if (here.length === 0) errors.push(`area ${area.id}: no locations`);
    if (slots > cast) errors.push(`area ${area.id}: only ${cast} actors for ${slots} daily slots`);
    // events start while the run is still here, after the area's first day
    const next = Math.min(Infinity, ...areas.filter((a) => a.fromDay > area.fromDay).map((a) => a.fromDay));
    for (const e of area.events ?? []) {
      if (e.fromDay < area.fromDay || e.fromDay >= next) errors.push(`event ${e.id}: day ${e.fromDay} is outside area ${area.id}`);
      if (e.buyerLimit !== undefined && !(Number.isInteger(e.buyerLimit) && e.buyerLimit >= 1))
        errors.push(`event ${e.id}: buyerLimit must be a whole number >= 1`);
      const b = e.bustling;
      if (b) {
        if (!(Number.isInteger(b.extraActors) && b.extraActors >= 0)) errors.push(`event ${e.id}: bustling.extraActors must be a whole number >= 0`);
        if (!(b.buyBonus >= 0)) errors.push(`event ${e.id}: bustling.buyBonus must be >= 0`);
        if (!(b.sellDiscount >= 0 && b.sellDiscount < 1)) errors.push(`event ${e.id}: bustling.sellDiscount must be in 0..1`);
        // each good appears on at most one actor per location
        const goodsHere = goods.filter((g) => g.area === area.id).length;
        for (const l of here)
          if (l.actorSlots + b.extraActors > goodsHere)
            errors.push(`event ${e.id}: ${l.id} can't hold ${l.actorSlots + b.extraActors} actors (${goodsHere} goods)`);
      }
    }
  }
  for (const g of goods) {
    if (!data.categories[g.category]) errors.push(`good ${g.id}: unknown category ${g.category}`);
    if (!data.areas[g.area]) errors.push(`good ${g.id}: unknown area ${g.area}`);
  }
  for (const a of actors) {
    if (a.role !== 'supplier' && a.role !== 'buyer') errors.push(`actor ${a.id}: bad role ${a.role}`);
    if (a.goods.length !== 1) errors.push(`actor ${a.id}: trades ${a.goods.length} goods (want 1)`);
    for (const g of a.goods) {
      if (!data.goods[g.good]) errors.push(`actor ${a.id}: unknown good ${g.good}`);
      // Better deals are better for the player: sellers get cheaper, buyers pay more.
      // Only buyers have a bad tier.
      const { bad, good, great, amazing } = g.prices;
      const ordered =
        a.role === 'supplier'
          ? bad === undefined && good > great && great > amazing
          : bad !== undefined && bad < good && good < great && great < amazing;
      if (!ordered) {
        const tiers = a.role === 'supplier' ? 'good -> great -> amazing (no bad)' : 'bad -> good -> great -> amazing';
        errors.push(`actor ${a.id}/${g.good}: prices must improve from ${tiers}`);
      }
      if (Math.min(bad ?? good, good, great, amazing) < 1) errors.push(`actor ${a.id}/${g.good}: prices must be >= 1`);
      if (g.qtyMin > g.qtyMax || g.qtyMin < 0) errors.push(`actor ${a.id}/${g.good}: bad qty range`);
    }
  }
  for (const g of goods) {
    const trades = (role: string) => actors.some((a) => a.role === role && a.goods.some((x) => x.good === g.id));
    if (!trades('supplier') || !trades('buyer')) errors.push(`good ${g.id}: needs at least one seller and one buyer`);
    if (!Number.isInteger(g.dealerDiscount) || g.dealerDiscount < 0) errors.push(`good ${g.id}: bad dealerDiscount`);
  }
  for (const l of locations) {
    if (l.slots.length < l.actorSlots) errors.push(`location ${l.id}: fewer slots than actorSlots`);
    if (!l.dealerSlot) errors.push(`location ${l.id}: missing dealerSlot`);
    if (!data.areas[l.area]) errors.push(`location ${l.id}: unknown area ${l.area}`);
  }
  if (!dealer?.id || !dealer.portrait) errors.push('dealer: missing id or portrait');
  if (errors.length) throw new Error('Invalid game data:\n' + errors.join('\n'));
  return data;
}

export async function loadData(): Promise<GameData> {
  const get = async <T>(name: string): Promise<T> => {
    const res = await fetch(`data/${name}.json`);
    if (!res.ok) throw new Error(`failed to load data/${name}.json`);
    return (await res.json()) as T;
  };
  const [goods, actors, locations, dealer, categories, areas] = await Promise.all([
    get<GoodDef[]>('goods'),
    get<ActorDef[]>('actors'),
    get<LocationDef[]>('locations'),
    get<DealerDef>('dealer'),
    get<CategoryDef[]>('categories'),
    get<AreaDef[]>('areas'),
  ]);
  // the stars baked into backgrounds, for the lantern weather's twinkle (a missing file just means none)
  await Promise.all(
    [...areas, ...locations].filter((x) => x.stars).map(async (x) => {
      const res = await fetch(x.stars!).catch(() => null);
      x.starPoints = res?.ok ? ((await res.json()) as [number, number][]) : [];
    }),
  );
  return buildData(goods, actors, locations, dealer, categories, areas);
}
