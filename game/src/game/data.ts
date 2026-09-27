import type { ActorDef, DealerDef, GameData, GoodDef, LocationDef } from './types';

function byId<T extends { id: string }>(list: T[]): Record<string, T> {
  return Object.fromEntries(list.map((x) => [x.id, x]));
}

/** Build lookup tables and check cross-references; throws on bad data. */
export function buildData(
  goods: GoodDef[],
  actors: ActorDef[],
  locations: LocationDef[],
  dealer: DealerDef,
): GameData {
  const data: GameData = { goods: byId(goods), actors: byId(actors), locations: byId(locations), dealer };
  const errors: string[] = [];
  for (const a of actors) {
    if (a.role !== 'supplier' && a.role !== 'buyer') errors.push(`actor ${a.id}: bad role ${a.role}`);
    for (const g of a.goods) {
      if (!data.goods[g.good]) errors.push(`actor ${a.id}: unknown good ${g.good}`);
      // Better deals are better for the player: sellers get cheaper, buyers pay more.
      const { bad, good, great, amazing } = g.prices;
      const ordered =
        a.role === 'supplier'
          ? bad > good && good > great && great > amazing
          : bad < good && good < great && great < amazing;
      if (!ordered) errors.push(`actor ${a.id}/${g.good}: prices must improve from bad -> good -> great -> amazing`);
      if (amazing < 1 || bad < 1) errors.push(`actor ${a.id}/${g.good}: prices must be >= 1`);
      if (g.qtyMin > g.qtyMax || g.qtyMin < 0) errors.push(`actor ${a.id}/${g.good}: bad qty range`);
    }
  }
  for (const g of goods) {
    const trades = (role: string) => actors.some((a) => a.role === role && a.goods.some((x) => x.good === g.id));
    if (!trades('supplier') || !trades('buyer')) errors.push(`good ${g.id}: needs at least one seller and one buyer`);
    if (!Number.isInteger(g.dealerDiscount) || g.dealerDiscount < 0) errors.push(`good ${g.id}: bad dealerDiscount`);
  }
  let slots = 0;
  for (const l of locations) {
    if (l.slots.length < l.actorSlots) errors.push(`location ${l.id}: fewer slots than actorSlots`);
    if (!l.dealerSlot) errors.push(`location ${l.id}: missing dealerSlot`);
    slots += l.actorSlots;
  }
  if (!dealer?.id || !dealer.portrait) errors.push('dealer: missing id or portrait');
  if (slots > actors.length) errors.push(`only ${actors.length} actors for ${slots} daily slots`);
  if (errors.length) throw new Error('Invalid game data:\n' + errors.join('\n'));
  return data;
}

export async function loadData(): Promise<GameData> {
  const get = async <T>(name: string): Promise<T> => {
    const res = await fetch(`data/${name}.json`);
    if (!res.ok) throw new Error(`failed to load data/${name}.json`);
    return (await res.json()) as T;
  };
  const [goods, actors, locations, dealer] = await Promise.all([
    get<GoodDef[]>('goods'),
    get<ActorDef[]>('actors'),
    get<LocationDef[]>('locations'),
    get<DealerDef>('dealer'),
  ]);
  return buildData(goods, actors, locations, dealer);
}
