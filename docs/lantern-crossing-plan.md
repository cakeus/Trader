# Plan: Lantern Crossing (third area)

A third area after Frostpine Peaks: a Japanese city market district at night, modeled on Tokyo. Lofi, dark, lit by warm paper lanterns. Read `CLAUDE.md` first; it explains how areas, categories, casts and the area move work. The Frostpine Peaks commit (`e1a3a2f`, "Add Frostpine Peaks with its own cast of 16 actors") is the best template: it touched the same data files, art scripts and code.

## Design (agreed with the user)

- **Area:** Lantern Crossing (id `crossing`). "Crossing" nods to Shibuya Crossing and to where the trains meet.
- **Blurb:** "A busy crossing in the big city, where the lanterns come on as the last trains roll in."
- **Setting:** a made-up district rooted in one real culture (Japan), the way the peaks are alpine. Lanterns should be everywhere in the art.

### Locations

| id | Name | Based on | Map landmark | Blurb |
|---|---|---|---|---|
| `midnight_station` | Midnight Station | Late-night Tokyo stations; the last train (shūden) | Platform and elevated tracks | "The last train is always about to leave, and nobody is in a hurry to catch it." |
| `emberglow_alley` | Emberglow Alley | Yokochō alleys like Omoide Yokochō; red lanterns (akachōchin) outside izakaya | A narrow lane of tiny bars strung with red lanterns | "Red lanterns, grill smoke, and eight-seat counters, all squeezed into one lane." |
| `stargazers_lookout` | Stargazer's Lookout | Rooftop gardens; moon viewing (tsukimi) | A rooftop garden or small observatory under the stars and moon | "A rooftop garden high above the city, where the lights below outshine the stars." |

### Goods

| Category | Bay | Peaks | Crossing (id) | Blurb |
|---|---|---|---|---|
| Food | Strawberry | Hot Cocoa | **Sushi Roll** (`sushi_roll`) | "Rice, fish, and a little seaweed jacket. Eat it before the conveyor belt takes it back." |
| Treasure | Seashell | Crystal | **Lucky Cat** (`lucky_cat`) | "Left paw up for customers, right paw up for money. This one's waving both." |
| Music | Old Record | Music Box | **Taiko Drum** (`taiko_drum`) | "Big, round, and loud enough to hear three stations away." |
| Tools | Hammer | Pickaxe | **Paper Lantern** (`paper_lantern`) | "Paper, bamboo, and a little flame. Hang one out and the night comes to you." |

The Lucky Cat is a gold maneki-neko (a calico is also traditional). The Paper Lantern is a chōchin: ribbed, round or cylindrical, red or cream, with dark top and bottom rings.

### Cast (16)

Same structure as the other casts: per good, 2 sellers and 2 buyers, and one stranger character per good. Each actor mirrors the bay actor in the same position (copy its `qtyMin`/`qtyMax`).

| id | Name | Role | Good | Mirrors | Who | Blurb |
|---|---|---|---|---|---|---|
| `mister_kaiten` | Mister Kaiten | supplier | sushi_roll | granny_puddingfoot | A conveyor-belt sushi robot | "A sushi conveyor belt that learned to talk. Everything he says comes back around eventually." |
| `chef_omakase` | Chef Omakase | supplier | sushi_roll | unit_b3rry | A stern old heron | "Has run the same eight-seat counter for forty years. He chooses your sushi. He also chooses your seat." |
| `kyu` | Kyu the Kappa | buyer | sushi_roll | sir_nibbleton | A kappa (river yokai) | "Only eats cucumber rolls. They're called kappa maki after him, and he will mention it." |
| `hachi` | Hachi | buyer | sushi_roll | baker_bun | A shiba | "Meets the last train at Midnight Station every night, with a sushi roll for whoever gets off." |
| `gacha_chan` | Gacha-chan | supplier | lucky_cat | captain_barnacle | A capsule-toy (gachapon) machine | "Turn his crank and out pops a lucky cat. Usually." |
| `mochi` | Mochi | supplier | lucky_cat | shelly | A calico cat | "Poses as a lucky cat in shop windows for a living. Sells the competition on the side." |
| `karasu` | Karasu | buyer | lucky_cat | madame_coquille | A salaryman crow | "Has missed the last train again. Collects lucky cats for his desk; it isn't working yet." |
| `kirara` | Kirara | buyer | lucky_cat | pip | A hamster pop idol | "Keeps a lucky cat for every concert. She has had a lot of concerts." |
| `goro` | Goro | supplier | taiko_drum | vinyl_vince | A little thunder imp (Kaminari-sama) | "Drums up the summer storms and sells last season's drums. Accepts belly buttons as a tip." |
| `kabuto` | Kabuto | supplier | taiko_drum | grandpa_gramophone | A rhinoceros beetle | "Carves every drum from a single log, mostly with his horn." |
| `kenji` | Kenji the Kaiju | buyer | taiko_drum | gloop | A kaiju | "In from the bay for the night. Keeps trying to play the drums gently. Keeps flattening them." |
| `ponpoko` | Ponpoko | buyer | taiko_drum | dj_mothball | A tanuki | "Has drummed on his own belly for years. Would like to try something that doesn't hurt." |
| `old_chochin` | Old Chochin | supplier | paper_lantern | walter | A lantern yokai (chōchin-obake) | "A paper lantern that came to life on its hundredth birthday. Swears the ones he sells are just lanterns." |
| `orika` | Orika | supplier | paper_lantern | mrs_tinkerbottom | An origami crane | "Folds lanterns between flights. The paper keeps trying to become more cranes." |
| `tsuki` | Tsuki | buyer | paper_lantern | bramble | The moon rabbit | "Comes down for moon viewing at Stargazer's Lookout. Needs a lantern to find the way back up." |
| `taisho` | Taisho | buyer | paper_lantern | gnorman | A boar who runs an izakaya | "A red lantern out front means 'we're open.' He is very, very open." |

**The font has no macrons** (only ASCII), so in-game names are "Old Chochin" and "Taisho". Don't add a glyph just for this.

### Background on the references (for flavor and portraits)

- Kaiten-zushi: conveyor-belt sushi. Omakase: "I'll leave it to you," the chef's choice.
- Kappa love cucumbers (kyūri); cucumber rolls are called kappa maki.
- Hachi: a gentle nod to Hachikō, the loyal dog of Shibuya Station. Keep it warm, not sad.
- Gachapon: capsule-toy machines. Kira-kira: sparkly. Karasu: crow (Tokyo is known for its crows).
- Kaminari-sama, the thunder spirit, drums up storms and is said to steal children's belly buttons. Gorogoro is the sound of thunder.
- Tanuki drum on their bellies in folklore; "ponpoko" is the sound.
- Chōchin-obake is a lantern yokai. Tsukumogami are objects that come alive at 100.
- The moon rabbit pounds mochi on the moon. Taishō is what regulars call the izakaya boss.

## Authenticity guidelines (apply to all art and text)

- One culture: Japan. Don't borrow from other Asian cultures.
- **No Godzilla.** It's Toho's trademark, and they act against knock-offs, including "-zilla" names. Kenji must look original: round and chubby, glowing lantern-orange back plates, clearly not Godzilla's silhouette.
- No gong, and no Orientalist shortcuts in sound or art.
- No fake writing. Don't draw squiggles meant to look like Japanese characters on signs or lanterns. Use tassels, ribs, rings, stripes and simple shapes.
- Portraits: no slanted-eye caricatures, no costume shorthand, not everyone in a kimono.
- Leave out sacred and funerary items (Obon floating lanterns, shrine amulets). A torii may appear in the background of the city but isn't a landmark.
- Names are plain words used for their meaning. No jokes on how Japanese sounds.
- Before the art is final, the user plans to have someone with Japanese roots review the portraits and names.

## Art direction

- **Night palette:** deep indigo, navy and plum, with warm lantern light (red, orange, cream) as the main accents. Keep backgrounds soft so the UI cards still stand out (see "Backgrounds" in `CLAUDE.md`). Check that the HUD and card text read against the dark map.
- Follow the pixel-art style in `CLAUDE.md` and `art/reference01.png`: tinted outlines, upper-left light, 3–4 value steps. On a night map the "light" can come from lanterns instead, but stay consistent within a sprite.
- Lanterns appear in the map, all three location backgrounds, and several portraits.

## Work

### 1. Goods art

- `art/make_sushi_roll.py`, `make_lucky_cat.py`, `make_taiko_drum.py`, `make_paper_lantern.py`: 32×32 icons in `assets/goods/`.
- Add each to `make_icons16.py` (16×16) and `make_icons8.py` (8×8). Each needs a clear silhouette at 8px: a round roll with a dark nori ring and a light center, the cat with its raised paw, a barrel drum (sticks optional), a ribbed lantern with dark rings.
- Check the contact sheets (`art/previews/_icons16_sheet.png`, `_icons8_sheet.png`).

### 2. Portraits

- 16 × `art/make_actor_<id>.py`, 64×64, in `assets/actors/<id>.png`. Use `portraitkit.py`. Check `_actors_sheet.png` alongside the existing casts for consistency.

### 3. Backgrounds and map

- `art/make_bg_map_crossing.py`: 640×480 night map with the three landmarks at the locations' `mapPos`.
- `art/make_bg_midnight_station.py`, `make_bg_emberglow_alley.py`, `make_bg_stargazers_lookout.py`: 640×480 location scenes with room for 3 actor slots plus the dealer slot, like the existing ones. Each shows some night sky with dim stars, and exports the star positions for the twinkle (see step 6). Stargazer's Lookout has the most sky, plus plants for the fireflies.
- Make mockups with pins and cards like the peaks' `_mock_*.png` previews.

### 4. Data

- `areas.json`: add `crossing` with `map`, `fromDay`, `music` and `blurb`.
- `locations.json`: the three locations with `area: "crossing"`, `mapPos`, `slots`, `dealerSlot` and `actorSlots: 3`.
- `goods.json`: the four goods with their category, `area`, icons, blurb and `dealerDiscount` (follow the peaks pattern).
- `actors.json`: the 16 actors above, appended after the peaks cast.
- `categories.json`: whatever per-area fields the peaks added there.

**Timing (decided):** `fromDay: 43`. Each area lasts 21 days: the bay is days 1–21, the peaks 22–42, and Lantern Crossing 43–63. You get there by meeting the day-42 quota.

**Prices (starting point, to confirm with the user and the sim):** **4× the bay prices** on every tier. The peaks are 2×, and `CLAUDE.md` says a third area needs richer prices again to keep up with the quotas. For example, Sushi Roll sellers 12 / 8 / 4, buyers 8 / 12 / 16 / 20; Paper Lantern sellers 40 / 36 / 28, buyers 32 / 40 / 48 / 52.

### 5. Code

The peaks were the first second area, so most of the code should already handle more areas. Check rather than assume:

- `areaFor`, `moveArea` and `endDay` move from peaks to crossing on day 43 (only after meeting the day-42 quota).
- `AreaTransition` and `AreaArrival` (`scenes/arrival.ts`) work from peaks to crossing: the old and new goods per category, and the buyback.
- The title screen, weather and music follow the saved area.
- Tests or sims that assume exactly two areas.
- `buildData` validation passes: one good per category per area, and the tiers improve for the player.

### 6. Weather and event

- **Ambient weather (decided): lantern glow, with fireflies where there's greenery, and twinkling stars in location skies.** Set `"weather": "lanterns"` on the area and add the drawing in `scenes/common.ts`, in the style of `drawSnow` and `drawRain`: stateless, positioned from `ui.t`, drawn through `drawWeather` so it sits under the pins on the map and under the cards at locations.
  - **Lantern glow (everywhere):** soft warm motes (cream, orange, a little red) drifting slowly upward and swaying, each gently pulsing in brightness, a few with a faint 1px halo. Keep it sparse and calm; it's ambience, not a storm. Somewhere around 60–120 motes, to tune by eye.
  - **Fireflies (only where there's greenery):** small yellow-green blinkers that wander slowly and blink on and off (fade in, hold, fade out, dark for a while). On the map, cluster them around Stargazer's Lookout's rooftop garden. At locations, only in the Stargazer's Lookout scene, around its plants. Fireflies aren't believable over city streets, so none at Midnight Station or Emberglow Alley.
  - **Twinkling stars (location scenes, and the map's sky if it shows one):** the location backgrounds should all include a night sky. Bake dim stars into the PNG, and have the art script also write their positions (for example `assets/bg/<location>_stars.json`, or a `stars` list on the location in `locations.json`). The game then draws a twinkle over them: each star brightens now and then on its own slow cycle, and a few get a 1px cross flare at their peak. This keeps stars off buildings without the code needing to know where the sky is.
  - Because weather is per area, the drawing function needs to know which scene it's in (the map, a location, and which location) to place the fireflies and stars. Pass that in rather than hard-coding location ids in the drawing code, for example from a per-location field in `locations.json` like `"fireflies": { "x", "y", "w", "h" }`.
  - Show the result in the game and look at it at both 1× and stretched scale before calling it done.
- **Event, Fireworks Night (decided):** build it after the area itself works.
  - **When:** `fromDay: 57`, running to the end of the area (days 57–63, its last week). This matches the bay's Rainstorm (days 15–21) and the peaks' coming event (days 36–42). Tell the user the start day when you report, since they agreed to the event but not explicitly to day 57.
  - **The rule:** each day, one of the three locations is **Bustling**, picked at random, seeded by (seed, day) like Packed House's `state.packedAt`. At the bustling location:
    - It has **4 actors** instead of 3. Deal one extra actor there the way Packed House does (`extraAt` in `dealActors`); it stands in the `dealerSlot` spot.
    - **Buyers pay 25% more** and **sellers charge 25% less.** Round to whole dollars, sellers at least $1.
  - **Suggested data:** new optional event fields in `areas.json`, for example `"bustling": { "extraActors": 1, "buyBonus": 0.25, "sellDiscount": 0.25 }`, with `buildData` checking them. Keep the numbers in data, not in code, so they're easy to tune.
  - **Prices:** decide where the ±25% goes in the price pipeline and write it down in `CLAUDE.md`. The simplest option is baking it into the `Offer.price` when `rollMarket` rolls the bustling location, like Cramazing does, so the tooltips, trade dialog, map, sims and stamp bonuses all pick it up with no extra work. Stamp multipliers (Monocle, Haggler and the rest) then apply on top. Mark those offers (for example `bustling: true`) so the tooltip can label them.
  - **Clashes to settle:**
    - **Packed House on the bustling location:** cap it at 4 cards by picking a different location for Packed House that day (both effects still happen, just at different places). Only if both would have to share a location (for example a 1-location edge case) does Packed House do nothing.
    - **Nox never appears at the bustling location.** When he visits, he goes to one of the other two locations. Pick the bustling location first, then have `rollDealer` choose among the rest. This doesn't change his chance to visit, only where he goes, and he takes an actor's spot there as usual. So the bustling location always has 4 actors.
    - **Nox and Packed House** can then both land on the same non-bustling location. That already works today: the extra actor and Nox share the location as they do now.
    - **The last-chance buyout** isn't affected (like the Rainstorm's cap).
    - **The due-day and stuck-day guarantees and Perfect Planner / Dump Truck** still work, with the required goods counted among the 4 actors.
  - **UI:**
    - Map tooltip: a "Bustling!" line on that location, like "Packed house!", in a festive color.
    - Actor tooltips there: a "Bustling" label with the price change (for example "Bustling (+25%)" on buyers and "Bustling (−25%)" on sellers). Check that the font has "−", or use "-".
    - `EventNotice` on its first morning with the name, a blurb and the rule. Suggested blurb: "The summer fireworks are on and the whole city is out. Each night one spot is bustling: more traders, and better prices both ways."
    - Optional: a small burst over the bustling pin on the map.
  - **Weather:** the event sets `"weather": "fireworks"`. Since event weather replaces the area's (`weatherOn`), the fireworks drawing should also draw the lantern glow, fireflies and stars underneath, not replace them. Fireworks: occasional bursts of colored 1px sparks high in the sky, spreading out, falling a little and fading. Keep them off the UI and not too frequent; it's lofi.
  - **Save:** the bustling location goes in the run state (like `packedAt`). Follow the "Working notes" in `CLAUDE.md` on bumping `version`, or make the field optional so older saves load, as `eventsSeen` did.
  - **Tests and sims:** test that exactly one location is bustling each event day, that it has 4 actors, the ±25% prices and rounding, the Packed House clash, that Nox is never at the bustling location (while his visit chance is unchanged), and that nothing changes before day 57. The sim profiles should favor the bustling location on their own, since they rank locations by price; check that they do, and report the day-63 survival with and without the event.

### 7. Tests and balance

- Add a price test like the peaks' ("exactly 2× the bay counterpart") for the multiplier chosen.
- Run `npm test` and `DAYS=63 npm run sim` (the full run through the crossing's last quota). Report survival after every quota from day 35 on, against the current table, and tune the price multiplier with the user. The quotas grow ×1.75 a week (see `quotaFor` in `run.ts`), so by day 63 they're far above today's numbers; expect to tune.
- Run `npm run build`.

### 8. Docs

- Update `CLAUDE.md`: the areas list, the categories table (add a Lantern Crossing column), the music, weather and event, and the new sim numbers.

## Out of scope

- **The peaks' special event** (days 36–42, the peaks' last week, like the bay's Rainstorm). The user will add it separately. Moving the crossing to day 43 leaves room for it; don't build it here, but don't block it either (the peaks' `events` list stays free for it).

## Still needs the user

- **The music track** for `public/assets/audio/`.
- Confirming Fireworks Night's start day (57).
- Confirming the price multiplier after the sim.
- The cultural review of portraits and names.
