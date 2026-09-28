import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { buildData } from '../src/game/data';
import type { GameData } from '../src/game/types';

const dir = join(__dirname, '..', 'public', 'data');
const read = (name: string) => JSON.parse(readFileSync(join(dir, `${name}.json`), 'utf8'));

export function loadTestData(): GameData {
  return buildData(read('goods'), read('actors'), read('locations'), read('dealer'), read('categories'), read('areas'));
}
