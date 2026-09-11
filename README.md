# Resonator Rotation

A small single-page web app for the Wuthering Waves game modes that ask for **many distinct teams**, where each resonator can only be used a limited number of times per season — and where that limit changes from season to season.

Mark which resonators you own, set how many **charges** (uses) each one has this season, then drag them into three-slot teams. Everything is stored in your browser.

**Live:** https://alwin-vollmer.gitlab.io/wuwa-rotation/

## What it does

- **Roster** — all resonators, portraits included. Click a portrait to own it (starts at 1 charge); the `−` / `+` stepper sets charges from 0 to 12. Dropping to 0 removes the resonator and clears it from every team.
- **Teams** — three slots each. Drag a portrait from the roster into a slot, drag a slot onto another slot to swap, or click a portrait and then click a slot (works on touch). A resonator cannot appear twice in one team, and cannot be placed with no charges left.
- **Reorder teams** — drag a team by its header, or use the `‹` `›` buttons.
- **Charges left** — everything owned but not yet placed, so you can see what is still spendable.
- **Filters** — search, element, rarity, owned only, has charges.
- **Export / Import** — a JSON payload you can copy to another browser.

State lives in `localStorage` under `wuwa.rotation.v1`:

```json
{ "owned": { "camellya": 2 }, "teams": [["camellya", null, null]] }
```

The first visit loads an example roster so the board is not empty; **Start empty** wipes it.

## Files

| Path | Purpose |
| --- | --- |
| `index.html` | The whole app — markup, styles and logic, no build step |
| `chars.js` | Generated character list (`id`, `name`, `element`, `weapon`, `stars`) |
| `img/<id>.webp` | Generated portraits, 192 px |
| `tools/update-characters.py` | Regenerates `chars.js` and `img/` |
| `.gitlab-ci.yml` | GitLab Pages deploy |

## Updating for a new patch

Character data and portraits come from [arabwuwa.com](https://arabwuwa.com/characters/), which serves them as a static JSON file:

```bash
python3 tools/update-characters.py
git add chars.js img && git commit -m "chars: update for <version>" && git push
```

Two things the script handles that are easy to get wrong by hand:

- The image path must be taken from each record's `images.small`. Most portraits live under `/images/characters-filter/`, but the four Rovers live under `/images/characters-profile/` — a constructed path 404s for them.
- The JSON's first entry is a `__meta` reference object, not a character.

Pushing to `main` redeploys Pages automatically.

## License

MIT — see `LICENSE`.
