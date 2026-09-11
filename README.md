# Resonator Rotation

A small single-page web app for the Wuthering Waves game modes that ask for **many distinct teams**, where each resonator can only be used a limited number of times per season — and where that limit changes from season to season.

Mark which resonators you own, set how many **charges** (uses) each one has this season, then drag them into three-slot teams. Everything is stored in your browser.

**Live:** https://alwinvollmer.github.io/wuwa-rotation/

## What it does

- **Roster** — all resonators, portraits included. Click a portrait to own it (starts at 1 charge); the `−` / `+` stepper sets charges from 0 to 12. Dropping to 0 removes the resonator and clears it from every team.
- **Teams** — three slots each. Drag a portrait from the roster into a slot, drag a slot onto another slot to swap, or click a portrait and then click a slot (works on touch). A resonator cannot appear twice in one team, and cannot be placed with no charges left.
- **Rover counts once** — the four Rover forms share a single charge pool, and only one form can sit in a team. Own or step any of them and all four follow.
- **Team DPS on the board** — a full team whose trio matches the projection gets a strip under its slots with the projection rank, three-rotation DPS and difficulty. Matching ignores slot order and folds the Rover forms together, and where the projection lists the same trio more than once the strongest variant is credited.
- **Estimated DPS** — with no exact match, a team whose first two slots match a projection team still gets a figure, prefixed `~` and marked **estimate** in amber: the last of the matching teams, i.e. the lowest-ranked, so it reads as a floor rather than a promise. It appears as soon as slots 1 and 2 are filled.
- **Signature weapons** — every resonator is assumed to hold the weapon the projection calculates with. The crossed-swords badge on an owned portrait (and the weapon line in the detail modal) flags that you *don't* have it; teams they lead are then scaled to what the best standard-banner weapon of that type is worth, the figure turning red with a `⚔ 76%` tag. Only the lead slot is scaled, since that is where the damage sits.
- **Premium teams** — the crest in a team header flags it as one of your heavy-lifting teams: gold frame, filed corner, `premium` micro-label, gold slot borders and one slow pass of light across the header (suppressed under `prefers-reduced-motion`). A **Premium** tile in the stats row counts them. The flag rides with the team when you reorder, and survives export/import.
- **Reorder teams** — drag a team by its header, or use the `‹` `›` buttons.
- **Recommended teams** — the `i` button on any portrait, in the roster *or* in a team slot, opens that resonator's teams from the arabwuwa.com Team DPS projection: rank, three-rotation DPS and difficulty. Every team lands in one of three groups, filterable by chips that carry their counts:
  - **On the board** — that exact trio is already placed; the row names which team it is.
  - **Ready now** — you own all three with a charge to spare; one click on **Add team** places it and spends the charges.
  - **Needs a charge** — you own the whole team, but its charges are committed to teams already on the board; free one and it moves up.
  - **Missing units** — you do not have these resonators, named individually on the member chips.
- **Charges left** — everything owned but not yet placed, so you can see what is still spendable.
- **Filters** — search, element, rarity, owned only, has charges.
- **Export / Import** — a JSON payload you can copy to another browser.

State lives in `localStorage` under `wuwa.rotation.v1`:

```json
{ "owned": { "camellya": 2 }, "teams": [{ "c": ["camellya", null, null], "p": false }] }
```

`p` is the premium flag. Saves written before it existed stored each team as a bare
`["camellya", null, null]`; those are upgraded on load.

The first visit loads an example roster so the board is not empty; **Start empty** wipes it.

## Files

| Path | Purpose |
| --- | --- |
| `index.html` | The whole app — markup, styles and logic, no build step |
| `chars.js` | Generated character list (`id`, `name`, `element`, `weapon`, `stars`) |
| `img/<id>.webp` | Generated square art, 192 px — used in the detail modal |
| `img/roster/<id>.webp` | Generated tall art, 200 px wide — used in the roster, team slots and bench (all four Rover forms share `rover.webp`, as upstream does) |
| `teams.js` | Generated team recommendations (152 teams) |
| `tools/update-characters.py` | Regenerates `chars.js` and `img/` |
| `weapons.js` | Generated signature/standard weapon factors |
| `tools/update-teams.py` | Regenerates `teams.js` |
| `tools/update-weapons.py` | Regenerates `weapons.js` |

## Updating for a new patch

Character data and portraits come from [arabwuwa.com](https://arabwuwa.com/characters/), which serves them as a static JSON file:

```bash
python3 tools/update-characters.py
python3 tools/update-teams.py
python3 tools/update-weapons.py
git add chars.js teams.js weapons.js img && git commit -m "data: update for <version>" && git push
```

Two things the script handles that are easy to get wrong by hand:

- The image path must be taken from each record's `images.small`. Most portraits live under `/images/characters-filter/`, but the four Rovers live under `/images/characters-profile/` — a constructed path 404s for them.
- The JSON's first entry is a `__meta` reference object, not a character.
- Team recommendations come from a second dataset, `/data/team-dps-generated/<revision>/listing.en.json`, whose records are tuple-encoded against a `tupleFields` map and whose `<revision>` hash changes on every rebuild — `update-teams.py` reads the current one off the `/team-dps/` page instead of hard-coding it.

### Where the weapon factor comes from

Each character page on arabwuwa carries a **Weapon comparison / Relative damage**
section: weapons at various refinements, scored against that character's signature at
R1 (= 100%). `tools/update-weapons.py` scrapes those cards from all 60 character pages,
takes the 100% entry as the signature and the best standard-banner weapon listed as the
fallback, preferring the R1 row — where only a higher refinement is published (Qingxiao,
Chisa) the app says so in the tooltip.

37 characters publish a comparison; factors run 0.713–1.000 with a median of 0.825. The
other 20 — Verina, Shorekeeper, Baizhi, Mortefi and friends — publish none and simply get
no toggle, which costs nothing because only the lead slot is scaled.

Pushing to `main` redeploys GitHub Pages automatically.

## License

MIT — see `LICENSE`.
