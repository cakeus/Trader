# Trader

A cute, whimsical, lofi pixel-art trading roguelike. It is a 640×480 canvas game built with Vite and TypeScript, and its art is generated procedurally with Python and Pillow.

## How a run plays

- From the main menu you start a New Run or Continue the saved one. The game saves after every trade and at the end of every day.
- A run starts with $10 and a 4-slot bag. Each unit of a good takes one slot, and goods don't stack.
- Each day you pick one of 3 locations on the map. The map tooltips show which goods each location buys and sells today.
- At the location you click an actor to trade: click for 1 unit, shift-click for the max. Then you press End Day.
- Quota *n* is $25·`CONFIG.quotaGrowth`ⁿ (×1.6, rounded to $5: $25, $40, $65, $100, $165, …), due at the end of day 7·(*n*+1). A quota counts as met as soon as your cash reaches it, even if you spend below it afterwards. Missing a quota ends the run. Its stars are paid when it ends (see below).
- Meeting a quota earns **stars** (see below), which you spend on Stamps from the Dealer (Nox the Stamp Trader).
- On an unmet quota's due day, a big animated "Last Day!" (`ui.announce`, `lastDay` sfx) plays once, triggered from `drawHud` and keyed by seed and day on `app.announced`.
- At a location, when `canAct` (`run.ts`) says nothing can be bought or sold and no Stamp is affordable, the End Day button starts glowing 5s later (`NUDGE_AFTER` in `scenes/location.ts`).
- The pause menu (Menu button or Esc) has sound on/off, Save & Quit, Abandon Run, and the run's seed.

## Economy rules

- **Actors:** there are 4 goods (strawberry, seashell, old record, tools), each with 2 sellers and 2 buyers, for 16 actors in total. Every day `dealActors` (`src/game/deal.ts`) deals 9 of them out, 3 per location (2 where the Dealer is). No actor is in two places at once, and each good appears on at most one actor per location. No two locations buy and sell exactly the same goods: a location that matches an earlier one is rerolled. Any actor can appear anywhere. The deal is deterministic for (seed, day).
- **Due-day guarantee:** on a quota's due day, `guaranteedGood` (`src/game/run.ts`) makes sure at least one buyer for your most common bag good is dealt in. On a tie it picks the good with the higher Good-tier buyer price. An empty bag gets no guarantee.
- **Stuck-day guarantee:** on other days, `rescueGood` (`run.ts`) checks the normal deal. If you can't buy anything (bag full, or less cash than the cheapest price any seller could charge) and no dealt buyer takes anything in your bag, the day is re-dealt with a buyer for a random item from the bag. Otherwise the deal is left alone.
- **Deal tiers:**
  - Each actor good has a `prices` list with `bad`, `good`, `great` and `amazing` tiers.
  - Each day one tier is rolled per actor good: sellers use `CONFIG.dealWeights` (bad/good/great/amazing 0/50/30/20, so sellers never roll bad; their `bad` price is good + $1, unused), buyers use `CONFIG.buyerDealWeights` (20/40/25/15).
  - A buyer's `bad` price equals the good's great seller price: selling to one loses on a Good buy, breaks even on a Great buy and profits on an Amazing buy.
  - `buildData` only checks that the tiers improve for the player: sellers get cheaper and buyers pay more.
  - Good-to-Good routes break even, so all profit comes from catching Great or Amazing deals.
- **Stock and demand:** a seller's daily stock is rolled per good from `CONFIG.stockWeights` (1 / 2 / 3 at 50 / 30 / 20%, `rollStock` in `economy.ts`), with stock stamps added on top; sellers' `qty` ranges in `actors.json` are unused. A buyer's `qty` is its daily demand. Seller stock applies when `CONFIG.limitStock` is on (the default). Buyer demand applies only when `CONFIG.limitDemand` is on; it's off, so buyers take everything you bring (their `qty` is still rolled, just ignored).
- **Bag:** each bag item records what you paid and on which day. Selling removes the oldest unit first.
- **Hover tooltips:** hovering an actor shows the price, plus a "Bad deal" (light red), "Great deal" (green) or "Amazing deal" (cyan) label when the tier isn't `good`. It also shows a seller's stock (and a buyer's demand when `limitDemand` is on), and buyers show "Average paid" for units still in your bag.
- **Quick trade:** `CONFIG.quickTrade` (on) is the click-to-trade behaviour. Turning it off brings back the old trade dialog (`src/scenes/trade.ts`).

## Stars and the Dealer

- **Stars:** `updateQuota` works them out the moment a quota is met (`starsPending`), but `endDay` only pays them (`payStars`) at the end of the due day, and the QuotaResult screen the next morning announces them. This keeps early stars from snowballing. The amount is the quota's base `stars` (`BASE_STARS`, 5 for every quota, in `run.ts`) plus `EARLY_STAR` (1) per day before the due day. `starsAwarded`/`earlyBonus` are recorded on the quota for the QuotaResult screen. The "Quota reached!" toast at the moment it's met doesn't mention stars. Saves from before this have no `starsPending` and aren't paid twice.
- **Dealer** ("Nox the Stamp Trader"; his deals are called **Stamps** in the UI; `src/game/dealer.ts`, content in `public/data/dealer.json`): not one of the 16 actors, so `dealActors` ignores him. `rollDealer` runs in `startDay`: nothing until stars have been paid, a guaranteed first visit the next morning (so no earlier than day 8) (`dealerSeen`), then `CONFIG.dealer.chance` (50%) per day, at one random run location. His first visit after each quota's stars are paid (`dealerCheapOwed`, set in `payStars`) always includes a stamp costing at most `CONFIG.dealer.cheapAfterQuota` (5★): the first offer is drawn from those only. He takes the place of one of the location's actors: `startDay` rolls him first, then `dealActors` (`dealerAt`) deals his location one actor fewer, and his card stands in the freed slot. `dealerSlot` is only a fallback for days saved before this. Deterministic for (seed, day).
- **Deals:** each visit brings up to `CONFIG.dealer.offers` (3) distinct deals from `eligibleDeals`, bought separately. For each offer slot, `rollDealer` first picks a deal **kind** evenly among the kinds still available (`CONFIG.dealer.weight` can skew this, default 1 each), then a deal of that kind: which good for per-good kinds, or the next rank. So `stock` (any good) is as likely as `stockAll`. There is no rarity. Kinds in `CONFIG.dealer.disabled` are never offered: currently `discount` and `discountAll` (they gave too much cash) and `buyerStock` and `buyerStockAll` (pointless without demand limits). Stamps already owned keep working, and the Stamps dialog only counts disabled ones you own. **Every deal can be bought only once per run** (`perks.owned`, keyed by `dealKey`). Once nothing is left, he stops coming.
  - **Ranked kinds** (`RankedKind`, `CONFIG.dealer.ranks`): `bag`, `stockAll`, `buyerStockAll` and `sellChanceAll` have 3 ranks each (titles end in I / II / III). Only the next rank is offered, so each needs the one before. Ranks stack.
  - `bag` I / II / III: +1 capacity each, costing `bagCosts` (3 / 4 / 5★).
  - `discount` (per good, 3★, disabled, "<Good> Sale"): `dealerDiscount` from `goods.json` off every seller of that good, floor $1, applied immediately.
  - `stock` (per good, 3★, "<Good> Surplus"): +`stockStep` (2) daily stock for every seller of that good, applied immediately.
  - `buyerStock` (per good, 3★, "<Good> Demand"): +`buyerStockStep` (2) daily demand for every buyer of that good, applied immediately (`extraDemand` in `economy.ts`).
  - `sellChance` (per good, 3★): +`sellChanceStep` (10%) to that good's buyers' great and amazing weights, taken from bad first, then good (`buyerWeights(state, good)` in `economy.ts`). Applies from the next day's roll.
  - All-goods deals (`isUniversal`, 6★ per rank; purple stamps): `discountAll` ("Clearance Sale", $`discountAll` off every seller, one rank), `stockAll` ("Overflowing Supply", +`stockAll` stock per rank), `buyerStockAll` ("Universal Demand", +`buyerStockAll` demand per rank) and `sellChanceAll` ("Deals, Deals, Everywhere", +`sellChanceAll` (10%) great and amazing per rank). They stack with the per-good deals (`sellerPrice`, `extraStock`, `extraDemand`, `buyerWeights`). With all 3 `sellChanceAll` ranks plus a good's `sellChance`, that good's buyers' good-tier weight hits the 0 floor.
- UI: HUD star counter (quota uses `icon_flag`), map tooltip line, card (tag "Stamps") + tooltip, and `DealerDialog` (`src/scenes/dealer.ts`), laid out like the old trade dialog with one clickable row per deal. Each deal is drawn as a postage stamp by `drawStamp` (`src/scenes/stampArt.ts`, 42×42 `stamp`/`stamp_rare` backgrounds from `make_stamp.py`). All-goods deals get the purple stamp and a 2×2 grid of the goods' small icons.
- **Stamps button** in the HUD opens `StampsDialog` (`src/scenes/stamps.ts`): every owned stamp (`allDeals` filtered by `owns`, keys decoded with `dealFromKey`), with hover tooltips.

## Balance and the scaling wall (next phase: earnable player scaling)

- **First-quota sim** (`npm test`, `tests/sim.test.ts`): the best-possible player reaches it 99% of the time, the sensible player about 48%, a no-loss player (the Patient profile) also 48%, and the random player 15%. Its "random under 15%" check fails (random is right at 15%).
- **Long-run sim** (`npm run sim`, `tests/longrun.test.ts`, log only; also runs under `npm test`): 500 runs to day 35 for every strategy profile in `tests/players.ts`, plus a random player. It prints the share of runs still alive after each quota, the average cash on hand after each day's trading (over every day played, so long-surviving profiles skew higher), star and deal stats, and a histogram of the day the first quota was met (identical profiles share one). Env overrides: `RUNS`, `DAYS`, `GROWTH=2,1.6,1.5` to compare quota growth factors, `DEALER=0.5` for the Dealer chance, and `DISABLED=discount,discountAll` for the stamp kinds switched off (`DISABLED=` turns them all on). All profiles value goods at perk-adjusted prices.
  - **Frugal:** plays the market well and ignores the Dealer.
  - **Impulse:** buys every affordable deal, bag upgrades first, then in the order shown (also the first-quota sim's player).
  - **Packrat:** only buys bag upgrades, then all-goods deals.
  - **Specialist:** commits to one good (its first per-good deal) and buys bag upgrades first, then that good's deals and all-goods deals. It values that good ×3 when trading (so buys it first whenever it turns a profit), picks locations where it can restock it into its free slots, and heads for the Dealer (+10, with 3+ stars) when his location also lets it buy the focus good or sell focus units it holds. About 44% of its trades after its first stamp are its focus good.
  - **Patient:** Impulse, but never sells a unit below what it paid (sales take the oldest unit first, so it stops at the first unit bought for more), except on an unmet quota's due day.
  - **Dealer chaser:** adds +10 to the Dealer's location whenever it has 3+ stars, and buys by value: bag > all-goods discount/buyers > all-goods stock/demand > discount > buyers > stock/demand.

  Current tuning (buyer tiers bad/good/great/amazing 20/40/25/15, seller stock 1 / 2 / 3 at 50 / 30 / 20%, quotas ×1.6, 5 base stars per quota, Dealer 50%, 3 one-time deals per visit, kinds drawn evenly, a ≤5★ deal on his first visit after each quota, discount stamps off, stars paid when a quota ends, per-good stamps 3★ and +2 / +2 / 10%, Nox takes an actor's spot, unlimited buyer demand, demand stamps off). Survival is the share of runs still alive after that day:

  | Profile | Day 14 | Day 21 | Day 28 | Day 35 | Avg cash | Stars got / spent | Bags bought |
  |---|---|---|---|---|---|---|---|
  | Frugal | 38% | 26% | 8% | 0% | $34 | 8.6 / 0 | 0 |
  | Impulse | 39% | 30% | 19% | 6% | $41 | 10.4 / 6.0 | 0.4 |
  | Packrat | 38% | 28% | 17% | 4% | $39 | 9.9 / 4.5 | 0.4 |
  | Specialist | 39% | 30% | 22% | 10% | $42 | 11.0 / 7.0 | 0.7 |
  | Patient | 39% | 30% | 20% | 7% | $41 | 10.5 / 6.3 | 0.4 |
  | Dealer chaser | 37% | 30% | 25% | 13% | $45 | 11.5 / 9.6 | 0.7 |
  | Random | 6% | 3% | 0% | 0% | $11 | 1.5 / 1.1 | 0.1 |

  Adding bad buyer deals (20/40/25/15, was 0/50/30/20) cut day 7 from 67% to 45% and day-35 survival from 25 / 18 / 32 / 38% to 6 / 4 / 10 / 13% (Impulse / Packrat / Specialist / Dealer chaser). Refusing to sell at a loss (Patient) barely matters: only about 8% of Impulse's sales before day 7 lose money, always by $1, and holding those units costs about as much as it saves.

  Rolling seller stock as 1 / 2 / 3 (50 / 30 / 20%, instead of each seller's 2–4ish `qty` range) made it harder: day 7 dropped from 81% to 67%, and day-35 survival from 47 / 40 / 54 / 63% to 25 / 18 / 32 / 38% (Impulse / Packrat / Specialist / Dealer chaser). Stock stamps are worth more now.

  Removing buyer demand limits made the game much easier: every profile is at 81% on day 7 (was 64%), and day-35 survival went from 5 / 4 / 10 / 12% to 47 / 40 / 54 / 63% (Impulse / Packrat / Specialist / Dealer chaser). Even Frugal now reaches day 35 in 10% of runs.

  Nox taking an actor's spot (instead of standing as a 4th card) cut day-35 survival from 12 / 13 / 16 / 20% to 5 / 4 / 10 / 12% (Impulse / Packrat / Specialist / Dealer chaser). His location looks worse to a market-minded player, so the profiles that don't chase him stop running into him and buy far fewer stamps. The Dealer chaser loses the most in absolute terms, but it still leads.

  Boosting the Specialist so far: per-good stamps doubled in strength (11% → 14% on day 35), a more focused AI that also buys bags first and visits the Dealer when it can trade its good there (→ 16%). Stamps for its one good are still rarely offered, so it owns only about one per run. Impulse buying bags first didn't change its survival (bags 0.6 → 0.8 per run).

  Paying stars immediately (before they were delayed) gave day-35 survival 13% / 18% / 17% / 22% (Impulse / Packrat / Specialist / Dealer chaser). With the discount stamps also on, average cash was $60 / $59 / $59 / $68 (Impulse / Packrat / Specialist / Dealer chaser) and day-35 survival 26% / 27% / 27% / 39%.

  Every profile is at 64% on day 7 (the stuck-day guarantee added about 2 points across the board). Chasing the Dealer still wins. Drawing kinds evenly helped the picky profiles a lot (Packrat went from 3% to 24% on day 35): bags and the all-goods deals now come up far more often than when they were 1 deal among many or rares at a quarter weight.

- **Why:** income is roughly linear while quotas grow geometrically (they used to double every week; now ×1.6). Four bag slots at about $1.40–$2.30 expected profit per unit, with one location a day, earn roughly $30–60 a week.
- **Scaling knobs:**
  - `CAPACITY`, `START_CASH`, `FIRST_QUOTA`, `QUOTA_DAYS` and `quotaFor()` in `src/game/run.ts`, and `CONFIG.quotaGrowth`.
  - `BASE_STARS`, `EARLY_STAR` in `run.ts`.
  - `CONFIG` in `src/game/config.ts` (including `CONFIG.dealer`).
  - Price lists and `qty` in `public/data/actors.json`.
  - A placeholder for a rule-changing event every 3rd quota in `endDay()`.

## Layout

- `game/` is the web game.
  - `npm run dev` starts a dev server on http://localhost:5173. The Vite watcher uses polling because Windows file events were being missed.
  - `?timer` runs the game loop on setTimeout, so it keeps ticking in a hidden window during automated testing.
  - `npm test` runs vitest: `tests/economy.test.ts` for the rules and `tests/sim.test.ts` (first quota) and `tests/longrun.test.ts` (long run, log only) for balance; `npm run sim` shows the long-run table. `npm run build` typechecks and bundles the game.
  - `src/engine/`: the platform layer. This covers screen scaling, input, the bitmap font, immediate-mode UI (`ui.ts`), WebAudio sfx and the seeded RNG (`rng.ts`, `rngFor(seed, ...keys)`).
  - `src/game/`: pure logic with no DOM.
    - `run.ts`: the run state, trading, quotas and `endDay`.
    - `deal.ts`: the daily actor deal.
    - `dealer.ts`: the star Dealer's visits and upgrades.
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

- Goods: a 32×32 `icon`, a 16×16 `iconMedium` (`make_icons16.py`, for the map tooltip) and an 8×8 `iconSmall` (`make_icons8.py`), in `assets/goods/`.
- Actor portraits: 64×64, in `assets/actors/<actor id>.png`.
- Backgrounds: 640×480, opaque, in `assets/bg/`. Keep them soft so the UI cards stand out.
- UI: 24×24 9-slice panels with 8px corners, 16×16 icons, and the cursor, in `assets/ui/`.
- Font: `assets/font/font.png` plus `font.json` (`make_font.py`). Add a glyph if a character renders as `?`.
