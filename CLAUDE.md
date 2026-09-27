# Trader

A cute, whimsical, lofi pixel-art trading roguelike. It is a 640×480 canvas game built with Vite and TypeScript, and its art is generated procedurally with Python and Pillow.

## How a run plays

- From the main menu you start a New Run or Continue the saved one. The game saves after every trade and at the end of every day.
- A run starts with $10 and a 4-slot bag. Each unit of a good takes one slot, and goods don't stack.
- Each day you pick one of 3 locations on the map. The map tooltips show which goods each location buys and sells today.
- At the location you click an actor to trade: click for 1 unit, shift-click for the max. Then you press End Day.
- Quota *n* is $25·2ⁿ, due at the end of day 7·(*n*+1). A quota counts as met as soon as your cash reaches it, even if you spend below it afterwards. Missing a quota ends the run.
- The pause menu (Menu button or Esc) has sound on/off, Save & Quit, Abandon Run, and the run's seed.

## Economy rules

- **Actors:** there are 4 goods (strawberry, seashell, old record, tools), each with 2 sellers and 2 buyers, for 16 actors in total. Every day `dealActors` (`src/game/deal.ts`) deals 9 of them out, 3 per location. No actor is in two places at once, and each good appears on at most one actor per location. Any actor can appear anywhere. The deal is deterministic for (seed, day).
- **Due-day guarantee:** on a quota's due day, `guaranteedGood` (`src/game/run.ts`) makes sure at least one buyer for your most common bag good is dealt in. On a tie it picks the good with the higher Good-tier buyer price. An empty bag gets no guarantee.
- **Deal tiers:**
  - Each actor good has a `prices` list with `good`, `great` and `amazing` tiers.
  - Each day one tier is rolled per actor good using `CONFIG.dealWeights` (50/30/20).
  - `buildData` only checks that the tiers improve for the player: sellers get cheaper and buyers pay more.
  - Good-to-Good routes break even, so all profit comes from catching Great or Amazing deals.
- **Stock and demand:** `qty` is the daily stock for sellers and the daily demand for buyers. It only applies when `CONFIG.limitStock` is on, which is the default.
- **Bag:** each bag item records what you paid and on which day. Selling removes the oldest unit first.
- **Hover tooltips:** hovering an actor shows the price, plus a "Great deal" (green) or "Amazing deal" (cyan) label when the tier isn't `good`. It also shows the stock or demand, and buyers show "Average paid" for units still in your bag.
- **Quick trade:** `CONFIG.quickTrade` (on) is the click-to-trade behaviour. Turning it off brings back the old trade dialog (`src/scenes/trade.ts`).

## Balance and the scaling wall (next phase: earnable player scaling)

- **First-quota sim** (`npm test`, `tests/sim.test.ts`): the best-possible player reaches it 100% of the time, the sensible player about 63% and the random player about 13%. That's accepted as "easier for now".
- **Long-run sim** (500 runs): the table shows the share of runs still alive after each quota.

  | Player | Day 7 | Day 14 | Day 21 | Day 28+ |
  |---|---|---|---|---|
  | Sensible | 62% | 41% | 4% | 0% |
  | Random | 15% | 2% | 0% | 0% |

- **Why:** income is roughly linear while quotas double every week. Four bag slots at about $1.40–$2.30 expected profit per unit, with one location a day, earn roughly $30–60 a week.
- **Scaling knobs:**
  - `CAPACITY`, `START_CASH`, `FIRST_QUOTA`, `QUOTA_DAYS` and `quotaFor()` in `src/game/run.ts`.
  - `CONFIG` in `src/game/config.ts`.
  - Price lists and `qty` in `public/data/actors.json`.
  - A placeholder for a rule-changing event every 3rd quota in `endDay()`.

## Layout

- `game/` is the web game.
  - `npm run dev` starts a dev server on http://localhost:5173. The Vite watcher uses polling because Windows file events were being missed.
  - `?timer` runs the game loop on setTimeout, so it keeps ticking in a hidden window during automated testing.
  - `npm test` runs vitest: `tests/economy.test.ts` for the rules and `tests/sim.test.ts` for balance. `npm run build` typechecks and bundles the game.
  - `src/engine/`: the platform layer. This covers screen scaling, input, the bitmap font, immediate-mode UI (`ui.ts`), WebAudio sfx and the seeded RNG (`rng.ts`, `rngFor(seed, ...keys)`).
  - `src/game/`: pure logic with no DOM.
    - `run.ts`: the run state, trading, quotas and `endDay`.
    - `deal.ts`: the daily actor deal.
    - `economy.ts`: the tier and qty rolls.
    - `config.ts`: rule switches and tier weights.
    - `data.ts`: loading and validation.
    - `save.ts`: the localStorage save.
    - `types.ts`: shared types.
  - `src/scenes/`: one file per screen or modal. The `App` in `src/app.ts` keeps a scene stack, and only the top scene receives input.
  - `public/data/*.json`: the content (goods, actors, locations). `public/assets/`: the generated PNGs. Don't hand-edit these.
- `art/`: the asset generators. Run `python make_<name>.py` from that folder, or `python build_all.py` to rebuild everything.
  - Shared helpers: `pixelkit.py`, `portraitkit.py` (for faces) and `bgkit.py` (for backgrounds).
  - Previews go to `art/previews/`. The `_*_sheet.png` files are contact sheets.

## Working notes

- When the saved `RunState` shape changes, bump `version` in `types.ts`, `run.ts` and `save.ts`. Old saves are then ignored.
- A save stores the already-dealt day (actors and prices). Rule changes only affect days dealt after the change.
- After editing `actors.json` or `goods.json`, rerun `npm test` and check the sim numbers.

## Environment

- Python 3.11 and Pillow 12.x are already installed. Node 24.

## Pixel-art style

`art/reference01.png` is the style guide (a sheet of pixel-art drinks and snacks). Look at it before designing a new sprite. Key traits to match:

- **Tinted outlines, never pure black.** Use a dark, desaturated version of the object's main hue. Each material gets its own outline color.
- **Light from the upper-left.** Light tones go on the left and top, with shading toward the lower-right.
- **3–4 value steps per material** (light / base / shade / deep shade), soft and fairly saturated.
- **A small white or cream specular glint** in the upper-left of shiny surfaces.
- **Small details as 1-pixel marks**, often with a 1-pixel shadow underneath (e.g. strawberry seeds).
- A chunky, readable silhouette, with no anti-aliasing against the transparent background.

## How to make a sprite

Write one script per sprite, `art/make_<name>.py`, built with `pixelkit.Sprite`:

1. **Palette:** use `hexc("#rrggbb")` colors or a char→RGBA dict.
2. **Shapes:**
   - For large rounded shapes, build a mask (`ellipse`, `rect`, `rounded_rect`, `rows_mask`), then call `Sprite.blob(mask, ramp, outline)`. It outlines the edge pixels and shades the interior for upper-left light.
   - Draw irregular overlays as text rows with `Sprite.rows`, with an outline outside their mask via `outline_around`.
   - Draw back to front.
3. **Save:** call `Sprite.center()` and then `Sprite.save(name, subdir)`. This writes `game/public/assets/<subdir>/<name>.png` and `art/previews/<name>_preview.png`, and prints the size, mode, bbox and corner pixel.
4. **Verify:** view the preview and iterate until it reads well.

## Asset sizes

- Goods: a 32×32 `icon` and an 8×8 `iconSmall` (`make_icons8.py`), in `assets/goods/`.
- Actor portraits: 64×64, in `assets/actors/<actor id>.png`.
- Backgrounds: 640×480, opaque, in `assets/bg/`. Keep them soft so the UI cards stand out.
- UI: 24×24 9-slice panels with 8px corners, 16×16 icons, and the cursor, in `assets/ui/`.
- Font: `assets/font/font.png` plus `font.json` (`make_font.py`). Add a glyph if a character renders as `?`.
