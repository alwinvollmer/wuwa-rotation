# wuwa-rotation — CLAUDE.md

Wuthering Waves team builder (roster charges → three-slot teams). Static page, no build step,
published on GitHub Pages: https://alwinvollmer.github.io/wuwa-rotation/ (public repo — everything
committed here is public). `index.html` is the whole app; the `*.js` data files are generated.

## Where the data comes from

| File(s) | Source | Regenerate with |
|---|---|---|
| `chars.js`, `img/<id>.webp`, `img/roster/*.webp`, `img/live/<id>.webm`, `live.js` | shared asset hub **`~/projects/game-assets`** (local project, crawls arabwuwa.com + bakes the animated Spine portraits from ww.nanoka.cc) | `python3 tools/sync-assets.py` |
| `teams.js` | arabwuwa.com Team DPS projection | `python3 tools/update-teams.py` |
| `weapons.js` | arabwuwa per-character weapon comparison | `python3 tools/update-weapons.py` |
| `sequences.js` | arabwuwa sequence damage comparison | `python3 tools/update-sequences.py` |

**Never crawl character images or build loops in this repo.** Characters, portraits, roster art and
the animated loops all come from `~/projects/game-assets` (its CLAUDE.md documents sources, sizes and
the loop pipeline). `tools/sync-assets.py` only copies/resizes from its `dist/`: square art 192 px,
tall roster art 200 px wide, loops = the bundle's 176x220 `small` variant. A character that is
missing or misnamed is fixed in the hub (`./assets.py wuwa`, aliases in `data/aliases.json`),
then synced here. Only the team data (teams/weapons/sequences) is crawled by this repo's own scripts.

## New patch

```bash
cd ~/projects/game-assets && ./assets.py wuwa faces loops     # hub: new characters + their loops
cd ~/projects/wuwa-rotation && python3 tools/sync-assets.py
python3 tools/update-teams.py && python3 tools/update-weapons.py && python3 tools/update-sequences.py
git add -A chars.js live.js img teams.js weapons.js sequences.js && git commit -m "data: update for <version>" && git push
```

## Notes
- The four Rover forms share one roster card (`img/roster/rover.webp`) and stay static: the bundle
  has both a male and a female loop, the gender for the shared card is not decided yet.
- `index.html` has no `<meta charset>`: fine on GitHub Pages (sends utf-8), mojibake under
  `python -m http.server` or file://.
- Animated portraits: `<video muted loop playsinline>`, only on-screen ones play (IntersectionObserver).
