#!/usr/bin/env python3
"""Regenerate chars.js and img/ from arabwuwa.com.

The characters page is client-rendered; the data behind it is a plain static
JSON file, which is what we read here. Run from anywhere:

    python3 tools/update-characters.py
"""
import json
import pathlib
import sys
import urllib.request

SOURCE = "https://arabwuwa.com/data/characters.json"
ORIGIN = "https://arabwuwa.com"
ROSTER = "/images/characters-filter/roster/340w/{name}.webp"
SIZE = 192          # square art (detail modal)
ROSTER_SIZE = 200   # tall art (roster grid, team slots, bench)
ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = {"User-Agent": "Mozilla/5.0 (resonator-rotation updater)"}


def get(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read()


def main() -> int:
    try:
        from PIL import Image
    except ImportError:
        print("Pillow is required: pip install --user pillow", file=sys.stderr)
        return 1

    records = json.loads(get(SOURCE))
    chars = [c for c in records if not c.get("__meta")]
    print(f"{len(chars)} characters in {SOURCE}")

    img_dir = ROOT / "img"
    img_dir.mkdir(exist_ok=True)
    kept, added = set(), 0

    for c in chars:
        cid = c["id"]
        kept.add(cid + ".webp")
        out = img_dir / f"{cid}.webp"
        if out.exists():
            continue
        # Take the path from the record: the Rovers sit in a different folder
        # than everyone else, so a constructed URL 404s for them.
        path = c["images"]["small"].split("?")[0]
        raw = get(ORIGIN + path)
        tmp = out.with_suffix(".tmp")
        tmp.write_bytes(raw)
        im = Image.open(tmp)
        im.thumbnail((SIZE, SIZE))
        im.save(out, "WEBP", quality=80)
        tmp.unlink()
        added += 1
        print(f"  + {cid} ({out.stat().st_size // 1024} KB)")

    # Tall roster art. The four Rover forms share one image upstream, which is
    # also how this app treats them: one resonator, one charge pool.
    roster_dir = img_dir / "roster"
    roster_dir.mkdir(exist_ok=True)
    roster_kept, roster_added = set(), 0
    for name in sorted({("rover" if c["id"].startswith("rover-") else c["id"]) for c in chars}):
        roster_kept.add(name + ".webp")
        out = roster_dir / f"{name}.webp"
        if out.exists():
            continue
        try:
            raw = get(ORIGIN + ROSTER.format(name=name))
        except Exception as exc:
            print(f"  ! no roster art for {name}: {exc}", file=sys.stderr)
            continue
        tmp = out.with_suffix(".tmp")
        tmp.write_bytes(raw)
        im = Image.open(tmp)
        im.thumbnail((ROSTER_SIZE, ROSTER_SIZE * 2))
        im.save(out, "WEBP", quality=82)
        tmp.unlink()
        roster_added += 1
        print(f"  + roster/{name} ({out.stat().st_size // 1024} KB)")

    stale = [p for p in img_dir.glob("*.webp") if p.name not in kept]
    stale += [p for p in roster_dir.glob("*.webp") if p.name not in roster_kept]
    for p in stale:
        print(f"  - {p.name} (no longer listed)")

    # Keep the source order: newest release first, as the upstream file states.
    data = [{"i": c["id"], "n": c["name"], "e": c["element"], "w": c["weapon"], "s": c["stars"]} for c in chars]
    (ROOT / "chars.js").write_text(
        "const CHARS=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"wrote chars.js ({len(data)} entries), {added} new square + "
          f"{roster_added} new roster portrait(s), {len(stale)} stale")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
