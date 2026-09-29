# Trader

A cute, whimsical, lofi pixel-art trading roguelike. It is a 640×480 canvas game built with Vite and TypeScript, and its art is generated procedurally with Python and Pillow.

## How a run plays

- From the main menu you start a New Run or Continue the saved one. The game saves after every trade and at the end of every day.
- A run starts with $10 and a 4-slot bag. Each unit of a good takes one slot, and goods don't stack.
- Each day you pick one of 3 locations on the map. The map tooltips show which goods each location buys and sells today.
- At the location you click an actor to trade: click for 1 unit, shift-click for the max. Then you press End Day.
- Quota *n* is $20·`CONFIG.quotaGrowth`ⁿ (×1.75, rounded to $5: $20, $35, $60, $105, $190, …), due at the end of day 7·(*n*+1). A quota counts as met as soon as your cash reaches it, even if you spend below it afterwards. Missing a quota ends the run. Its stars are paid when it ends (see below).
- Meeting a quota earns **stars** (see below), which you spend on Stamps from the Dealer (Nox the Stamp Trader).
- **Last-chance buyout:** pressing End Day on an unmet quota's due day, short of the quota and with goods in the bag, opens `BuyoutDialog` (`src/scenes/buyout.ts`) instead of the plain "Last day!" confirm. It offers to buy the whole bag at Bad-deal prices (`buyoutPrice`: each good's lowest `bad` buyer price) and says whether that covers the quota. Back, End Day (without selling) or Sell (`takeBuyout` in `run.ts`, then the day ends). The sims always take it (it's a no-op unless offered).
- On an unmet quota's due day, a big animated "Last Day!" (`ui.announce`, `lastDay` sfx) plays once, triggered from `drawHud` and keyed by seed and day on `app.announced`.
- At a location, when `canAct` (`run.ts`) says nothing can be bought or sold and no Stamp is affordable, the End Day button starts glowing 5s later (`NUDGE_AFTER` in `scenes/location.ts`).
- The pause menu (Menu button or Esc, `scenes/pause.ts`) has Resume, Options, Save & Quit, Abandon Run, and the run's seed. Submenus (`SubMenu`) are drawn in the pause panel's place.
  - **Options** (`OptionsMenu`): Sound (effects), Music, and Stretch to Fit (scales the canvas to fill the window, keeping the aspect ratio, instead of by whole numbers; `screen.stretch`). They live in `app.settings`, saved to localStorage (`trader.settings`, `engine/settings.ts`) apart from the run; `app.applySettings()` pushes them to `Sfx` and the screen. On mobile (`isMobile`, `engine/device.ts`) Stretch to Fit is forced on (`applySettings`; the option is hidden) and the pixel cursor isn't drawn; `index.html` has the fullscreen/no-zoom mobile CSS and the strawberry favicon. `?mobile` forces mobile mode on a desktop browser.
  - **Touch UI:** mobile can't hover, so tapping an item picks it (`ui.focus(key, rect)`, which is plain hover on desktop) and shows its tooltip next to it, with action buttons along the bottom (the `actions` argument of `ui.tooltip`): Go on a map location, Buy 1 or Sell 1 on an actor (grayed out when that trade is blocked; there's no max on touch), Open on Nox. Bag slots and stamps just show their tooltip. A tap elsewhere, or a second tap on the item, puts it away, and taps on the tooltip don't reach what's under it. Direct click-to-act uses `ui.activated(rect)`, which is desktop only.
  - **Debug** (dev builds only, `import.meta.env.DEV`; `DebugMenu`): Mark Quota Complete / Incomplete (`debugSetQuotaMet` in `run.ts`: latches it met with its stars pending as if met today, or unmet again), Advance to Day *X* (`debugAdvance`: ends days without trading until the current quota's due day, or the next quota's when it's due and met; disabled on an unmet due day; the quota result and area move play through `showDayEnd` in `scenes/location.ts`), Go to *next area* (`debugGotoNextArea`: moves there today without touching the day or quota, silently buying the bag back at what you paid, then re-deals today and goes to the map; disabled in the last area), Cash +5 / +20 / Reset (to $0; adding can meet the quota), Stars +1 / +5 / Reset, and Give *stamp* (< / > pick one of `eligibleDeals`; `grantDeal` in `dealer.ts`, the same effect code buying uses).
- **Music:** each area has a looping `music` track (`areas.json`, files in `public/assets/audio/`). The peaks have Winter Village Loop. The title screen (`MainMenu`) shows the saved run's area (its map, weather and music, via `app.titleArea`), or the bay's when there's no save. `App.frame` asks for the right track each frame through `sfx.music()`. `Sfx` (`engine/audio.ts`) plays it at `MUSIC_VOLUME` (10%) and crossfades between tracks over `MUSIC_FADE` (1.5s), or a given fade time (`app.musicFade`; the area move fades the old track out over 0.9s and the new one in over 0.8s). Music off (`sfx.musicMuted`) pauses it; Sound off (`sfx.muted`) only silences the effects. Browsers block audio until the first click, so `unlock` starts it then. While the page is hidden (`visibilitychange`/`pagehide`, wired in `main.ts`), `sfx.hidden` pauses the music and suspends the effects context, so it doesn't keep playing in the background on mobile.

## Areas and categories

- **Areas** (`public/data/areas.json`): Blossom Bay (`bay`, the seaside town, from day 1) and Frostpine Peaks (`peaks`, a snowy mountain town, from day 22). Each area has its own map (`map`), 3 locations (`area` in `locations.json`) and 4 goods (`area` in `goods.json`). Each area has its own cast of 16 actors: every actor trades exactly one good (`actors.json`), so it belongs to that good's area. The peaks cast mirrors the bay's roles and prices (each bay actor has a peaks counterpart at 2× its prices).
- **Weather:** an area can set `"weather": "snow"` in `areas.json` (the peaks do). `MapScene` then draws `drawSnow` (`scenes/common.ts`) over the map, under the pins: stateless 1–2px white flakes in three depth layers (the 2px near ones with a faint 1px shadow), positioned from `ui.t`. The count (`SNOW_FLAKES`, 540) gusts ±`SNOW_GUST` (29%) on two slow out-of-step waves, and flakes at the edge of the count fade rather than pop. The peaks map is tinted a little dimmer and bluer (end of `make_bg_map_peaks.py`) so the flakes show. Scenes draw weather with `drawWeather(ui, weatherOn(data, area, day))`, which covers events too; it goes under the pins on the map and under the cards at locations (`LocationScene`), and `AreaTransition` shows the old area's weather from its last day. `drawRain` is the rain version: a soft stormy tint (`ui.dim`), about `RAIN_DROPS` (300, gusting ±25%) slanted 1px streaks in three depth layers (1–3 segments of 3px, each stepping 1px across), and `RAIN_SPLASHES` (36) little splashes flicking up on the lower part of the screen.
- **Area events** (`events` on an area in `areas.json`, `src/game/events.ts`): an event starts on its `fromDay` and lasts until the run leaves the area (`eventOn(data, area, day)` picks the latest one started, `todayEvent(data, state)`). An event can set `weather` (replacing the area's, `weatherOn`) and `buyerLimit`. `buildData` checks that its day falls inside the area.
  - **Rainstorm** (bay, days 15–21, the last quota there): rain everywhere, and every buyer takes at most `buyerLimit` (2) of its good a day. `rollMarket` then sets a buyer's `left` to the limit and marks the offer `capped`. `demandApplies(o)` (`run.ts`, `CONFIG.limitDemand || o.capped`) is what `sellBlock`, `maxSell` and `sell` check, so shift-click stops at 2, a third sale gets the "Wants no more" deny, and `canAct` and the sims follow. The last-chance buyout isn't capped.
  - The first morning an event is on, once the map has been the top scene for `EVENT_NOTICE_DELAY` (1.5s; so after the QuotaResult is closed, and after the rain's been seen), `MapScene` pushes `EventNotice` (`scenes/event.ts`): the event's name, blurb and rule. Its id goes into `run.eventsSeen` (optional, so older saves load), so it only shows once per run.
  - A capped buyer's tooltip shows its demand as "Raining (buys 2)" in cyan, or "Raining (can't buy more)" in light red once it's used up (an event without rain uses its name instead of "Raining").
- **Categories** (`categories.json`): Food, Treasure, Music and Tools. Every good has a `category`, and each area has exactly one good per category:

  | Category | Blossom Bay | Frostpine Peaks |
  |---|---|---|
  | Food | Strawberry | Hot Cocoa |
  | Treasure | Seashell | Crystal |
  | Music | Old Record | Music Box |
  | Tools | Hammer | Pickaxe |

  Stamps are per category, so they carry over.
- **Mountain prices** are exactly 2× the bay counterpart's on every tier, for both sides (tested).
- **`areaView(data, areaId)`** (`src/game/area.ts`) is the game data as seen from one area: only its goods, locations and actors. It's memoized, and a view of a view resolves back to the full data (`fullData`). Anything that loops over actors' goods starts with `areaView(data, state.area)`: `startDay`, `rollMarket`, `deckCards`, the guarantees, `canAct`, `buyDealerDeal` and the sims. Scenes use `app.view`. `areaFor(data, day)`, `categoryOf` and `goodOf(data, category, area)` are also in `area.ts`.
- **The move:** `endDay` calls `moveArea` (`run.ts`) when `areaFor(day + 1)` comes after the current area (never backwards, so a debug jump sticks). You only get there by meeting the day-21 quota. `moveArea`:
  - buys the bag back at what you paid for it;
  - picks the new area's locations (seeded by area);
  - resets the tier deck and clears the Dealer;
  - sets `state.moved`.

  `LocationScene` then goes to `AreaTransition` (`scenes/arrival.ts`) instead of the map. It shows the quota result over the old area's map (with the old area's music, via `app.musicArea`), fades to dark (the music fades to silence with it), then fades up the new map under the area's name in big letters (a click skips it). Then the map comes in with the `AreaArrival` popup, which lists each category's old and new goods and the buyback. Dismissing it clears `moved`. A save continued mid-move plays the transition from the title.

## Economy rules

- **Actors:** each area has 4 goods (bay: strawberry, seashell, old record, hammer), each with 2 sellers and 2 buyers, for 16 actors per area. Every day `dealActors` (`src/game/deal.ts`) deals 9 of them out, 3 per location (2 where the Dealer is). No actor is in two places at once, and each good appears on at most one actor per location. No two locations buy and sell exactly the same goods: a location that matches an earlier one is rerolled. When your bag is empty at the start of the day, a location with only buyers (counting a buyers-and-Nox location) is rerolled the same way (`needSeller`). Any actor can appear anywhere. The deal is deterministic for (seed, day).
- **Due-day guarantee:** on a quota's due day, `guaranteedGood` (`src/game/run.ts`) makes sure at least one buyer for your most common bag good is dealt in. On a tie it picks the good with the higher Good-tier buyer price. An empty bag gets no guarantee.
- **Stuck-day guarantee:** on other days, `rescueGood` (`run.ts`) checks the normal deal. If you can't buy anything (bag full, or less cash than the cheapest price any seller could charge) and no dealt buyer takes anything in your bag, the day is re-dealt with a buyer for a random item from the bag. Otherwise the deal is left alone.
- **Deal tiers:**
  - Each actor good has a `prices` list with `good`, `great` and `amazing` tiers; buyers also have `bad` (`tierPrice` in `economy.ts` reads one).
  - Each day one tier is dealt per actor good: sellers use `CONFIG.dealWeights` (good/great/amazing 50/30/20), buyers use `CONFIG.buyerDealWeights` (bad/good/great/amazing 20/40/25/15). During the first quota (days 1–7), buyers use `CONFIG.firstQuotaBuyerDealWeights` (10/50/25/15) instead (`tierWeights` in `economy.ts`).
  - **Tier deck** (`CONFIG.tierDeck`, on): tiers come from a shuffled deck per role (seller / buyer) instead of independent rolls. Each cycle of `CONFIG.deckSize` (10) cards holds one random point in each tenth of 0..1 (`deckCard`), and `tierAt` maps it through that good's weights. So whole-card weights are exact per cycle (1 bad buyer in 10 in week 1, 2 after; sellers exactly 5 / 3 / 2), and a 25% / 15% pair comes out 2–3 / 1–2. Every location reads the same next cards at the start of the day (`rollMarket`), but only the one you `visit` uses them up (`deckCards`, `state.deck`), so every card dealt is one you see; it's the same as rolling on arrival. Each quota starts a fresh deck (`endDay` resets `state.deck`, and the quota index is part of the deck's seed). A 20-card deck that carried across quotas made week-1 survivors (who'd drawn the good cards) pay it back in week 2. Stock rolls don't depend on the switch.
  - A buyer's `bad` price is $1 under the good's great seller price (strawberry: equal to it), and its `amazing` price is $1 over `great` (hammer $13, record $10, seashell $6, strawberry $5). Mountain goods double all of this. Selling to a bad buyer loses unless you bought at Amazing (or a strawberry at Great, which breaks even).
  - Buyer prices (bad / good / great / amazing): strawberry 2 / 3 / 4 / 5, seashell 2 / 4 / 5 / 6, old record 5 / 7 / 9 / 10, hammer 8 / 10 / 12 / 13. Seller prices (good / great / amazing): 3 / 2 / 1, 4 / 3 / 2, 7 / 6 / 5, 10 / 9 / 7. Hot cocoa, crystal, music box and pickaxe cost 2× these.
  - `buildData` only checks that the tiers improve for the player: sellers get cheaper and buyers pay more.
  - Good-to-Good routes break even, so all profit comes from catching Great or Amazing deals.
- **Stock and demand:** a seller's daily stock is rolled evenly from its good's category range in `CONFIG.stockRange` (`rollStock` in `economy.ts`): Food 3, Treasure 2–3, Music 1–3, Tools 1. Stock stamps are added on top; sellers' `qty` ranges in `actors.json` are unused. A buyer's `qty` is its daily demand. Seller stock applies when `CONFIG.limitStock` is on (the default). Buyer demand applies only when `CONFIG.limitDemand` is on; it's off, so buyers take everything you bring (their `qty` is still rolled, just ignored), except when an event caps it (the Rainstorm, see above).
- **Bag:** each bag item records what you paid and on which day. Selling removes the oldest unit first.
- **Hover tooltips:** hovering an actor shows the price, plus a "Bad deal" (light red), "Great deal" (green) or "Amazing deal" (cyan) label when the tier isn't `good`. It also shows a seller's stock (and a buyer's demand when `limitDemand` is on or an event caps it), and buyers show "Average paid" for units still in your bag.
- **Quick trade:** `CONFIG.quickTrade` (on) is the click-to-trade behaviour. Turning it off brings back the old trade dialog (`src/scenes/trade.ts`).

## Stars and the Dealer

- **Stars:** `updateQuota` works them out the moment a quota is met (`starsPending`), but `endDay` only pays them (`payStars`) at the end of the due day, and the QuotaResult screen the next morning announces them. This keeps early stars from snowballing. The amount is the quota's base `stars` (`BASE_STARS`, 5 for every quota, in `run.ts`) plus `EARLY_STAR` (1) per day before the due day. `starsAwarded`/`earlyBonus` are recorded on the quota for the QuotaResult screen. The "Quota reached!" toast at the moment it's met doesn't mention stars. Saves from before this have no `starsPending` and aren't paid twice.
- **Dealer** ("Nox the Stamp Trader"; his deals are called **Stamps** in the UI; `src/game/dealer.ts`, content in `public/data/dealer.json`): not one of the 16 actors, so `dealActors` ignores him. `rollDealer` runs in `startDay`: nothing until stars have been paid, a guaranteed first visit the next morning (so no earlier than day 8) (`dealerSeen`), then `CONFIG.dealer.chance` (50%) per day, at one random run location. His first visit after each quota's stars are paid (`dealerCheapOwed`, set in `payStars`) always includes a stamp costing at most `CONFIG.dealer.cheapAfterQuota` (5★): the first offer is the first such card in the deck (reshuffling if none is left), skipping pricier ones. He takes the place of one of the location's actors: `startDay` rolls him first, then `dealActors` (`dealerAt`) deals his location one actor fewer, and his card stands in the freed slot. `dealerSlot` is only a fallback for days saved before this. Deterministic for (seed, day).
- **Deals:** each visit brings up to `CONFIG.dealer.offers` (3; 4 with the Stamp Collector) distinct deals, bought separately. They come from one shuffled **stamp deck per rarity** (`state.stampDecks`): one card per enabled deal not yet bought, where a ranked deal has a card per unowned rank and each of its cards stands for whichever rank is next (`cardDeal`). Each visit `rollDealer` draws 3 cards (`drawStamps`): each rolls a rarity (`rollRarity`) and takes the next card of that rarity's deck, falling back to the next lower rarity when it has none, then to the higher ones (`rarityFallback`: epic → rare → common). Unbought cards are used up until a deck runs out, and then everything of that rarity not yet bought, not left in its deck and not on his table is shuffled in under the cards that are left. A card that can't be offered right now (a second card of a ranked kind already on the table, or a pricey card while looking for the cheap one) is skipped but stays in place. Cards bought or switched off since they were shuffled in are dropped. The "per-good" kinds below are really **per category** (`{kind, category}`, keys like `stock:food`, perks keyed by category id). They are titled by category ("Food Surplus", "Tools Dealer"), and the description and stamp icon show the current area's good. **Rarity** (`CONFIG.dealer.rarity`, common unless listed; `rarityOf`): Common, Rare or Epic. Each stamp drawn is epic with `rarityOdds.epic` (4% in week 2, +2% a week) and rare with `rarityOdds.rare` (8% in week 2, +4% a week), otherwise common (`rarityOdds(week)`, week = quota index + 1, clamped to at least 2). There are no epics yet. Rares: Daily Discount, Can't Get Enough, Stamp Collector and the 18 stamps below, all 8★. Rare stamps have a blue frame (`stamp_blue`), epics a gold one (`stamp_gold`), and the Nox dialog and Stamps tooltip label them (`RARITY_LABEL` in `stampArt.ts`). Within a rarity every card is equally likely, so per-category kinds (4 cards each) and bags (4) come up more than the one-off commons. Kinds in `CONFIG.dealer.disabled` are never offered: currently `discount` and `discountAll` (they gave too much cash) and `buyerStock` and `buyerStockAll` (pointless without demand limits). Stamps already owned keep working, and the Stamps dialog only counts disabled ones you own. **Every deal can be bought only once per run** (`perks.owned`, keyed by `dealKey`). Once nothing is left, he stops coming.
  - **Ranked kinds** (`RankedKind`, `CONFIG.dealer.ranks`): `bag` has 4 ranks, `buyerStockAll` and `luckAll` 3 each (titles end in I / II / III / IV), and `stockAll` 1 (no numeral). Only the next rank is offered, so each needs the one before. Ranks stack.
  - `bag` I / II / III / IV: +2 capacity each (`bagSlots`, 8 in all; was +1 each, then +1 / +2 / +3, then +3 ×3 at 3 / 4 / 5★), costing `bagCosts` (3 / 5 / 7 / 9★). Bigger bags barely move the sims: going from +1 each to +3 each raised day 35 by only 1–4 points (Impulse 36% → 38%, Specialist 11% → 16%, Tip focus 47% → 51%, CGE focus 79% → 80%). Many runs never buy one (54% of Impulse runs), and the rest mostly get them late, by which point seller stock limits what a bigger bag can hold.
  - `discount` (per category, 3★, disabled, "<Category> Sale"): each good's own `dealerDiscount` from `goods.json` off every seller of that category's goods, floor $1, applied immediately.
  - `stock` (per category, 3★, "<Category> Surplus"): +`stockStep[category]` daily stock for every seller of that good (Food +3, Treasure +2, Music +2, Tools +1), applied immediately.
  - `buyerStock` (per category, 3★, "<Category> Demand"): +`buyerStockStep` (2) daily demand for every buyer of that good, applied immediately (`extraDemand` in `economy.ts`).
  - `luck` (per category, 3★, "<Category> Dealer"): +`luckStep` (5%) to the great and amazing weights of that good's sellers and buyers, taken from bad first, then good (sellers have no bad, so good pays) (`tierWeights(state, good, role)` in `economy.ts`). Applies from the next day's roll.
  - `dailyDiscount` ("Daily Discount", 8★ Rare, one-time, `icon_tag`): the first unit you buy each day costs half, rounded up, min $1 (`buyPrice` in `run.ts`, used by `buyBlock`, `maxBuy`, `buy`, the rescue check and the tooltips; `state.boughtToday`, optional, reset in `endDay`).
  - `tip` ("Tip Jar", 5★, one-time, `icon_tip`): a buyer pays an extra $`CONFIG.dealer.tip` (5) once you've sold it `tipAfter` (2) units in a day, once per buyer per day (`sold`/`tipped` on its `Offer`, in `sell`). The buyer tooltip shows the progress, and the sale shows a "+$5 tip!" floater.
  - `cantGetEnough` ("Can't Get Enough", 8★ Rare, one-time, `icon_more`): a buyer's price goes up $`CONFIG.dealer.cantGetEnoughStep` (1; it was 2 for a while) after every unit you sell it, for the rest of the day (`sellUnits` raises the offer's `price`, so the tooltip shows it; the tooltip adds "+$1 after each sale").
  - `collector` ("Stamp Collector", 8★ Rare, one-time, `icon_collector`): Nox brings `CONFIG.dealer.collectorOffers` (1) more stamp every visit (`dealerOfferCount`). Buying it draws the extra card onto his table right away (`drawStamps` in `dealer.ts`, which `rollDealer` also uses). The sims value it at 2 (`DEAL_VALUE`).
  - These kinds (`SingleKind`, with `discountAll` and `collector`) have a 16×16 icon from `make_ui.py`. In the long-run sim (at 5★) they lifted day-35 survival a lot (Impulse 14% → 31%, Patient 20% → 43%, Dealer chaser 27% → 56%); Packrat and Specialist don't buy them.
  - **The rare stamps** (all `SingleKind`, 8★, icons from `make_stamp_icons.py`; tunables in `CONFIG.dealer`). Prices: `Offer.price` stays the offer's base (the tier price after Cramazing and seller discounts, plus Can't Get Enough raises). `buyPrice`/`fullBuyPrice` and `sellPrice`/`nextSellPrice` in `run.ts` work out what's actually paid, and the tooltips, trade dialog, map and sims use them. A sale is `round(round(price × (1 + Monocle + Vintage + Flipper)) × Haggler)`, per unit.
    - `birdsEye` ("Bird's Eye"): the map tooltip shows each good's price under its icon, colored by tier.
    - `haggler`: a final sell multiplier `1 + hagglerStart − hagglerStep × units sold today` (150%, 125%, 100%, … down to 0 after 6 sales; `state.soldToday`; `hagglerMultiplier`).
    - `fannyPack`, `sleepingBag`, `cleanSweep`: end-of-day payouts (`endOfDayPayouts`), paid in `endDay` **before** the quota check, so they can meet it (the buyout and "Last day!" confirm count them too). They pay $1 per different good in the bag; 5% of what the bag cost (rounded) if nothing was bought or sold today (`tradedToday`); and $1 per bag slot with an empty bag. The End Day button's hover tooltip lists them.
    - `packedHouse`: one location a day (`state.packedAt`, seeded) gets an extra actor (`extraAt` in `dealActors`). It stands in the old `dealerSlot` spot, as does Nox when he's at the packed location. The map tooltip says "Packed house!".
    - `cramazing`: an Amazing deal's gap from the Good price is ×`cramazing` (2), for both roles (sellers min $1) (`dealPrice` in `economy.ts`). Buying it re-prices today's Amazing offers.
    - `mixedBag`: a $3 tip for the first sale of each good a day (`state.soldGoodsToday`). `bigTipper`: every tip ×3 (`payTip`). Sales return a `Sale` (`sellUnits`) with the tips for the floater.
    - `lastCall`: the buyout pays each good's lowest Amazing buyer price, with Cramazing (`buyoutPrice(data, good, state)`).
    - `fuzzyDice`: after each unit sold, a 1-in-6 roll (seeded per buyer and unit) makes that buyer Amazing for the day, keeping CGE raises ("Lucky dice!" floater).
    - `campFire`: the day's first unit bought comes with a free copy at the same `paid`, if there's room. It doesn't use up stock (`buyUnits` returns `{n, free}`).
    - `monocle`: +25% on every buy and sell price (so margins ×1.25, but goods cost more).
    - `detour`: until you've bought or sold something (`canDetour`), the End Day button says Detour. It sends you back to the map (`detour`, `state.detoured`), where that location is grayed out, once a day.
    - `vintage` (+10% per day in the bag) and `flipper` (+25% for units bought yesterday): per unit (`sellBonus`).
    - `perfectPlanner` / `dumpTruck`: every day, a buyer of the bag good with the highest Good-tier buyer price (`plannerGood`) / the most common bag good (`guaranteedGood`) is dealt in. `dealActors` takes a list of required goods.
  - All-goods deals (`isUniversal`, 6★ per rank, `luckAll` 8★; purple stamps): `discountAll` ("Clearance Sale", $`discountAll` off every seller, one rank), `stockAll` ("Overflowing Supply", one rank: every seller's stock ×`stockAll` (2), applied after the per-category Surplus is added, so food gains the most; `sellerStock`/`stockMultiplier` in `economy.ts`; bought mid-day, it doubles what today's sellers have left), `buyerStockAll` ("Universal Demand", +`buyerStockAll` demand per rank) and `luckAll` ("Deals, Deals, Everywhere", +`luckAll` (5%) great and amazing per rank, for every seller and buyer). They stack with the per-good deals (`sellerPrice`, `extraStock`, `extraDemand`, `tierWeights`). Bad buyers go from 20% to 10% at rank I and 0% at rank II. With all 3 `luckAll` ranks plus a good's `luck`, buyers are at 0 / 20 / 45 / 35% and sellers at 10 / 50 / 40%.
- UI: HUD star counter (quota uses `icon_flag`), map tooltip line, card (tag "Stamps") + tooltip, and `DealerDialog` (`src/scenes/dealer.ts`), laid out like the old trade dialog with one clickable row per deal. Each deal is drawn as a postage stamp by `drawStamp` (`src/scenes/stampArt.ts`, 42×42 `stamp` / `stamp_blue` / `stamp_gold` backgrounds by rarity, and `stamp_all`, from `make_stamp.py`). All-goods deals get the purple stamp and a 2×2 grid of the goods' small icons. Only preloaded images draw, so `main.ts` preloads `STAMP_IMAGES`.
- **Stamps button** in the HUD opens `StampsDialog` (`src/scenes/stamps.ts`): every owned stamp (`allDeals` filtered by `owns`, keys decoded with `dealFromKey`), with hover tooltips.

## Balance and the scaling wall (next phase: earnable player scaling)

- **First-quota sim** (`npm test`, `tests/sim.test.ts`): the best-possible player reaches it 100% of the time, the sensible player about 83%, a no-loss player (the Patient profile) 87%, and the random player 48% (the check allows up to 40%, so it currently fails).
- **Long-run sim** (`npm run sim`, `tests/longrun.test.ts`, log only; also runs under `npm test`): 500 runs to day 35 for every strategy profile in `tests/players.ts`, plus a random player. It prints the share of runs still alive after each quota, the average cash on hand after each day's trading (over every day played, so long-surviving profiles skew higher), star and deal stats, and a histogram of the day the first quota was met (identical profiles share one). Env overrides: `RUNS`, `DAYS`, `GROWTH=2,1.6,1.5` to compare quota growth factors, `DEALER=0.5` for the Dealer chance, and `DISABLED=discount,discountAll` for the stamp kinds switched off (`DISABLED=` turns them all on). `DECK=0` rolls tiers independently, and `WEEK1BAD=0.2` sets the first quota's bad buyer weight (the rest goes to good). It also prints the spread of cash after day 7's trading (p10 / p25 / p50 / p75 / p90 and the standard deviation). And, per week, the units in the bag and what was paid for them after each day's trading (before `endDay`, so the day-21 move doesn't empty it first): avg (min–max) over the run-days played. All profiles value goods at perk-adjusted prices.
  - **Frugal:** plays the market well and ignores the Dealer.
  - **Impulse:** buys every affordable deal, bag upgrades first, then in the order shown (also the first-quota sim's player).
  - **Packrat:** only buys bag upgrades, then all-goods deals.
  - **Specialist:** commits to one category (its first per-category deal), i.e. its good in the current area, and buys bag upgrades first, then that good's deals and all-goods deals. It values that good ×3 when trading (so buys it first whenever it turns a profit), picks locations where it can restock it into its free slots, and heads for the Dealer (+10, with 3+ stars) when his location also lets it buy the focus good or sell focus units it holds. About 44% of its trades after its first stamp are its focus good.
  - **Patient:** Impulse, but never sells a unit below what it paid (sales take the oldest unit first, so it stops at the first unit bought for more), except on an unmet quota's due day.
  - **Focus profiles** (Discount focus, Tip focus, CGE focus; `focus()` in `tests/players.ts`): each is built around one of the three new stamps. `forceStamp` swaps it into Nox's offers until it's bought (so on his first visit, day 8), the profile always goes there for it, and it never buys the other two. Otherwise it buys deals and chases the Dealer like the Dealer chaser. Discount focus spends the day's first buy on the priciest profitable unit and counts the best saving when picking a location. Tip focus and CGE focus value holding more of one good (`stackValue`: the $5 tip at 2+, or n(n−1)/2 for n units) when buying and picking buyers, once they own the stamp. Day 35 (at 5★): Discount 82%, Tip 53%, CGE 81% (Dealer chaser, which buys all three when offered, 45%). With Daily Discount and Can't Get Enough at 8★ Rare they can't be bought on day 8 any more: Discount 48%, CGE 34%, while Tip (still 5★ common) is at 82%. At a $1 step, CGE focus was at 55–57%. CGE focus also restocks the good it holds most of first (×3) and ranks the stock stamps right after bags; neither changed its survival. Holding a good until it can sell a stack of `HOLD` to one buyer (never when the buyer is capped, the bag is full, cash is short or the quota is due within a day) doesn't help. At a $1 step it made CGE focus worse (day 35: 55% off, 48% at 3, 41% at 4): stacks only grow from 2.5 to 2.6 units per sale, because seller stock and bag size limit them, so holding just delays cash. At a $2 step it's about even (79% off, 78% at 3). It's off by default (`HOLD=3 npm run sim` turns it on).
  - **Rainstorm buying:** every profile except Random (`ignoresRain`) buys differently when buyers will be capped the next day: it ranks goods by profit per unit instead of per dollar, and holds at most the cap (2) of any good. It changed survival by only about ±2 points either way (Dealer chaser on day 35: 62% without it, 60% with it). `RAIN=0 npm run sim` turns it off. Daily Discount is by far the strongest: half off a tools unit is $5 a day in the bay and $10 in the peaks.
  - **Dealer chaser:** adds +10 to the Dealer's location whenever it has 3+ stars, and buys by value: bag > all-goods discount/buyers > all-goods stock/demand > discount > buyers > stock/demand.

  The sims value the new rares by `DEAL_VALUE` (Monocle and Camp Fire highest; Bird's Eye, Detour and Sleeping Bag low, since the players don't use the information or skip days). Adding rarity and the 18 rares moved day 35 (against commit `e8e4922`) from 28 / 8 / 16 / 36 / 46% to 21 / 9 / 17 / 30 / 38% (Impulse / Packrat / Specialist / Patient / Dealer chaser). The sims make little use of the new stamps, and fewer cheap deals come up.

  Current tuning (Frostpine Peaks from day 22 at 2× prices, first quota $20 growing ×1.75, tier deck of 10, first-quota bad buyers 10%, luck stamps +5% / +5% on both sides, `luckAll` 8★, buyer tiers bad/good/great/amazing 20/40/25/15 with bad $1 under the great seller price and amazing $1 over great, seller stock by category (Food 3, Treasure 2–3, Music 1–3, Tools 1), 5 base stars per quota, Dealer 50%, 3 one-time deals per visit from shuffled stamp decks per rarity (rare 8% +4% a week from week 2, epic 4% +2%, none yet), bags +2 ×4 at 3 / 5 / 7 / 9★, a ≤5★ deal on his first visit after each quota, discount stamps off, stars paid when a quota ends, per-good stamps 3★ and stock +3 / +2 / +2 / +1 (Food / Treasure / Music / Tools), demand +2, luck 10%, Nox takes an actor's spot, unlimited buyer demand except the Rainstorm's 2 a day on days 15–21, demand stamps off, last-chance buyout taken). Survival is the share of runs still alive after that day:

  | Profile | Day 14 | Day 21 | Day 28 | Day 35 | Avg cash | Stars got / spent | Bags bought |
  |---|---|---|---|---|---|---|---|
  | Frugal | 74% | 32% | 10% | 0% | $31 | 14.6 / 0 | 0 |
  | Impulse | 75% | 44% | 33% | 21% | $44 | 19.1 / 11.2 | 0.8 |
  | Packrat | 74% | 38% | 23% | 9% | $36 | 16.5 / 6.6 | 0.8 |
  | Specialist | 73% | 39% | 29% | 17% | $39 | 17.9 / 10.5 | 1.1 |
  | Patient | 84% | 57% | 46% | 30% | $49 | 22.7 / 13.2 | 0.9 |
  | Dealer chaser | 76% | 53% | 49% | 38% | $54 | 23.3 / 18.6 | 1.4 |
  | Random | 19% | 5% | 2% | 0% | $14 | 4.5 / 3.1 | 0.3 |

  Dealing stamps from a shuffled deck (instead of picking a kind evenly each slot) lifted day 35 a lot: with the old bags (+3 ×3 at 3 / 4 / 5★) it went from 14 / 12 / 14 / 20 / 27% to 28 / 13 / 20 / 37 / 51% (Impulse / Packrat / Specialist / Patient / Dealer chaser); the focus profiles moved little (Discount 80%, Tip 57%, CGE 81%). Bags at +2 ×4 for 3 / 5 / 7 / 9★ then took it to 25 / 13 / 15 / 34 / 45% (focus profiles 82 / 53 / 81%).

  Rolling seller stock by category (Food 3, Treasure 2–3, Music 1–3, Tools 1, was 1 / 2 / 3 at 50 / 30 / 20% for every good; average 2.1, was 1.7) with Surplus stamps at +3 / +2 / +2 / +1 made the game easier: day 7 went from 74% to 84% for the market profiles (Patient 90%, Random 43%), day 14 from 54% to 74%, and day 35 from 5 / 4 / 7 / 11% to 14 / 12 / 14 / 27% (Impulse / Packrat / Specialist / Dealer chaser).

  The Rainstorm (buyers take 2 a day on days 15–21) took day 21 from 23 / 32 / 28 / 30 / 47 / 36% to 18 / 25 / 23 / 22 / 38 / 30% (Frugal / Impulse / Packrat / Specialist / Patient / Dealer chaser), and day 35 from 0 / 6 / 5 / 10 / 13 / 16% to 0 / 5 / 4 / 7 / 10 / 11%. Patient loses the most (it holds more units waiting for a good price, and now can't unload them at once).

  Moving to Frostpine Peaks on day 22 with 2× prices (profit per slot doubles) took day 28 from 0 / 6 / 4 / 8 / 9 / 11% to 5 / 19 / 15 / 20 / 37 / 25% (Frugal / Impulse / Packrat / Specialist / Patient / Dealer chaser), and day 35 from 0% everywhere to 0 / 6 / 4 / 9 / 15 / 15%. With `DAYS=49`, day 42 is 0–5% and nobody reaches day 49 ($330 then $580): a third area would need higher prices again.

  Squeezing buyer prices (bad +$1, amazing −$1; mean-neutral, about 20–25% less spread per sale) took the day-7 cash spread from sd $6.6 to $5.5 (p10 $14 → $16, p90 $32 → $30). Day 7 went from 71% to 74–75% for the market profiles and day 14 from 48–51% to 54–56%. The cost: selling patiently pays less, so Patient's lead roughly halved (day 7 +11 → +5 points, day 14 +23 → +12), and Patient itself fell (day 21 54% → 45%, day 28 18% → 9%). Also tried in 1000-run sims: only trimming amazing by $1 (plus the tools amazing seller $7 → $8) cut day 7 to 63% for a smaller gain in spread (sd $5.8), and the squeeze plus the tools seller change tightened it slightly more (sd $5.3) but cost about 4 points on day 7 and 6 on day 14.

  Raising quota growth from ×1.6 to ×1.75 ($20, $35, $60, $105, $190) left day 7 alone (71% for the market profiles, 82% Patient) and made day 35 all but impossible (0–1% for every profile) on purpose: the plan is to add more ways for the player to scale. Day 21 went from 42–50% to 20–32% for the market profiles (Patient 75% → 54%), and day 28 from 14–39% to 1–13% (Patient 63% → 18%).

  Lowering the first quota from $25 to $20 (so every quota after it too: $20, $30, $50, $80, $130) took day 7 from 39% to 71% for the market profiles (Patient 47% → 82%, Random 8% → 28%), and day-35 survival from 1 / 0 / 1 / 2% to 14 / 10 / 15 / 26% (Impulse / Packrat / Specialist / Dealer chaser). Patient reaches day 35 in 33% of runs.

  Before that, at $25, day 7 was 39% for the market profiles and 47% for Patient. Comparing 1000 runs each (market profiles; sd is the standard deviation of cash after day 7's trading):

  | Setup | Day 7 | Day 14 | Day 21 | Day-7 cash p10 / p50 / p90 | sd |
  |---|---|---|---|---|---|
  | Independent rolls, week-1 bad 20% (before) | 30% | 20% | 12% | $9 / $19 / $32 | $8.7 |
  | Deck, week-1 bad 20% | 28% | 19% | 9% | $11 / $19 / $30 | $7.0 |
  | Independent rolls, week-1 bad 10% | 40% | 27% | 16% | $12 / $22 / $34 | $8.4 |
  | Deck, week-1 bad 10% (current) | 38% | 26% | 12% | $14 / $22 / $32 | $6.5 |

  (Day 14 / 21 are Impulse.) The deck cuts the day-7 spread by about a quarter, but it slightly *lowers* survival: every quota sits above the median player's cash, so passing depends on luck, and less variance means fewer lucky passes. With lower variance, a quota target sets the pass rate more directly, so the next step is lowering targets (or raising income) until the median sensible player clears them. Halving week-1 bad buyers is worth about +10 points on day 7.

  The last-chance buyout (all profiles take it) lifted day 7 from 29% to 30% (Patient 38% → 40%) and later quotas by about 1–3 points.

  Adding bad buyer deals (20/40/25/15, was 0/50/30/20) at the great seller price cut day 7 from 67% to 45% and day-35 survival from 25 / 18 / 32 / 38% to 6 / 4 / 10 / 13% (Impulse / Packrat / Specialist / Dealer chaser). At that price, refusing to sell at a loss (Patient) barely mattered (45% vs 45% on day 7): only about 8% of sales lost money, always by $1. Lowering bad by another $1 (to great seller price − 1) cut the sell-anything profiles to 40% on day 7, while Patient reached 48%, the best of any profile, and led through day 21. Raising old record prices by $1 and tools by $2 on both sides (same margins, more cash tied up per unit) cut day 7 to 32% (Patient 37%) and day 35 to 3 / 3 / 5 / 6% (Impulse / Packrat / Specialist / Dealer chaser). Lowering bad buyers by another $1 (strawberry held at the $1 floor) cut the sell-anything profiles to 29% on day 7, while Patient held at 38% and now clearly leads every quota. Making luck +5% / +5% on both sides (was +10% / +10% on buyers only) with `luckAll` at 8★ trimmed day-35 survival from 3 / 2 / 3 / 4% to 2 / 1 / 1 / 3% (Impulse / Packrat / Specialist / Dealer chaser).

  Rolling seller stock as 1 / 2 / 3 (50 / 30 / 20%, instead of each seller's 2–4ish `qty` range) made it harder: day 7 dropped from 81% to 67%, and day-35 survival from 47 / 40 / 54 / 63% to 25 / 18 / 32 / 38% (Impulse / Packrat / Specialist / Dealer chaser). Stock stamps are worth more now.

  Removing buyer demand limits made the game much easier: every profile is at 81% on day 7 (was 64%), and day-35 survival went from 5 / 4 / 10 / 12% to 47 / 40 / 54 / 63% (Impulse / Packrat / Specialist / Dealer chaser). Even Frugal now reaches day 35 in 10% of runs.

  Nox taking an actor's spot (instead of standing as a 4th card) cut day-35 survival from 12 / 13 / 16 / 20% to 5 / 4 / 10 / 12% (Impulse / Packrat / Specialist / Dealer chaser). His location looks worse to a market-minded player, so the profiles that don't chase him stop running into him and buy far fewer stamps. The Dealer chaser loses the most in absolute terms, but it still leads.

  Boosting the Specialist so far: per-good stamps doubled in strength (11% → 14% on day 35), a more focused AI that also buys bags first and visits the Dealer when it can trade its good there (→ 16%). Stamps for its one good are still rarely offered, so it owns only about one per run. Impulse buying bags first didn't change its survival (bags 0.6 → 0.8 per run).

  Paying stars immediately (before they were delayed) gave day-35 survival 13% / 18% / 17% / 22% (Impulse / Packrat / Specialist / Dealer chaser). With the discount stamps also on, average cash was $60 / $59 / $59 / $68 (Impulse / Packrat / Specialist / Dealer chaser) and day-35 survival 26% / 27% / 27% / 39%.

  Every profile is at 64% on day 7 (the stuck-day guarantee added about 2 points across the board). Chasing the Dealer still wins. Drawing kinds evenly helped the picky profiles a lot (Packrat went from 3% to 24% on day 35): bags and the all-goods deals now come up far more often than when they were 1 deal among many or rares at a quarter weight.

- **Why:** income is roughly linear while quotas grow geometrically (they used to double every week; now ×1.75). Four bag slots at about $1.40–$2.30 expected profit per unit, with one location a day, earn roughly $30–60 a week.
- **Scaling knobs:**
  - `CAPACITY`, `START_CASH`, `FIRST_QUOTA`, `QUOTA_DAYS` and `quotaFor()` in `src/game/run.ts`, and `CONFIG.quotaGrowth`.
  - `BASE_STARS`, `EARLY_STAR` in `run.ts`.
  - `CONFIG` in `src/game/config.ts` (including `CONFIG.dealer`).
  - Price lists and `qty` in `public/data/actors.json` (the last 16 actors are the peaks cast).
  - An area's `fromDay` in `areas.json`.

## Layout

- `game/` is the web game.
  - `npm run dev` starts a dev server on http://localhost:5173. The Vite watcher uses polling because Windows file events were being missed.
  - `?timer` runs the game loop on setTimeout, so it keeps ticking in a hidden window during automated testing.
  - `npm test` runs vitest: `tests/economy.test.ts` for the rules and `tests/sim.test.ts` (first quota) and `tests/longrun.test.ts` (long run, log only) for balance; `npm run sim` shows the long-run table. `npm run build` typechecks and bundles the game.
  - `src/engine/`: the platform layer. This covers screen scaling, input, the bitmap font, immediate-mode UI (`ui.ts`), WebAudio sfx and the seeded RNG (`rng.ts`, `rngFor(seed, ...keys)`).
  - `src/game/`: pure logic with no DOM.
    - `run.ts`: the run state, trading, quotas, `endDay` and `moveArea`.
    - `area.ts`: areas, categories and `areaView`.
    - `deal.ts`: the daily actor deal.
    - `dealer.ts`: the star Dealer's visits and upgrades.
    - `economy.ts`: the tier and qty rolls.
    - `config.ts`: rule switches and tier weights.
    - `data.ts`: loading and validation.
    - `save.ts`: the localStorage save.
    - `types.ts`: shared types.
  - `src/scenes/`: one file per screen or modal. The `App` in `src/app.ts` keeps a scene stack, and only the top scene receives input.
  - `public/data/*.json`: the content (goods, actors, locations, areas, categories). `public/assets/`: the generated PNGs. Don't hand-edit these.
- `art/`: the asset generators (`make_stamp_icons.py` draws the rare stamps' 16×16 icons). Run `python make_<name>.py` from that folder, or `python build_all.py` to rebuild everything.
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

- Goods: one `make_<good>.py` per good (`make_hammer.py`, `make_hot_cocoa.py`, …) for the 32×32 `icon`, a 16×16 `iconMedium` (`make_icons16.py`, for the map tooltip) and an 8×8 `iconSmall` (`make_icons8.py`), in `assets/goods/`.
- Actor portraits: 64×64, in `assets/actors/<actor id>.png`.
- Backgrounds: 640×480, opaque, in `assets/bg/`. Keep them soft so the UI cards stand out. Each area has a map (`make_bg_map.py`, `make_bg_map_peaks.py`) whose landmarks sit at its locations' `mapPos`.
- UI: 24×24 9-slice panels with 8px corners, 16×16 icons, and the cursor, in `assets/ui/`.
- Font: `assets/font/font.png` plus `font.json` (`make_font.py`). Add a glyph if a character renders as `?`.
