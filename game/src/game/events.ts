import type { AreaEvent, GameData, RunState, Weather } from './types';

/** The event on in an area on a day: the one that started most recently, if any. An event lasts
 *  until the run leaves the area. */
export function eventOn(data: GameData, areaId: string, day: number): AreaEvent | null {
  let on: AreaEvent | null = null;
  for (const e of data.areas[areaId]?.events ?? []) if (e.fromDay <= day && (!on || e.fromDay > on.fromDay)) on = e;
  return on;
}

/** Today's event in the run's area, if any. */
export function todayEvent(data: GameData, state: RunState): AreaEvent | null {
  return eventOn(data, state.area, state.day);
}

/** The weather in an area on a day: the event's, or the area's own. */
export function weatherOn(data: GameData, areaId: string, day: number): Weather | undefined {
  return eventOn(data, areaId, day)?.weather ?? data.areas[areaId]?.weather;
}
