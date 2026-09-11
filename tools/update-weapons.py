#!/usr/bin/env python3
"""Regenerate weapons.js: per character, the weapon the Team DPS projection
assumes (their signature) and how much of that damage the best standard-banner
weapon is worth.

arabwuwa publishes weapon *stats* (/data/weapons.json) and the weapon each
projection team was calculated with, but its own weapon comparison lives inside
the auth-gated calculator, so the ratio here is modelled from the public stats
with the formula below. It is an estimate, and the app labels it as one.

    python3 tools/update-weapons.py
"""
import collections
import json
import pathlib
import re
import sys
import urllib.request

ORIGIN = "https://arabwuwa.com"
WEAPONS = ORIGIN + "/data/weapons.json"
TEAM_PAGE = ORIGIN + "/team-dps/"
ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = {"User-Agent": "Mozilla/5.0 (resonator-rotation updater)"}

# The two standard-banner 5-stars per weapon type.
STANDARD = [
    "laser-shearer", "radiance-cleaver", "phasic-homogenizer", "pulsation-bracer", "boson-astrolabe",
    "emerald-of-genesis", "lustrous-razor", "static-mist", "abyss-surges", "cosmic-ripples",
]

# A generic endgame carry, minus the weapon: flat ATK from character and echoes,
# and the bonuses a normal build already has. The weapon is then layered on top,
# so the ratio only reflects what the two weapons differ by.
BASE = {"atk": 1150, "atkPct": 0.30, "dmg": 0.55, "cr": 0.55, "cd": 1.90}

# Signature weapons lean on conditional buffs (stacks, after-skill windows) that
# a rotation only holds part of the time; standard weapons barely have any, so
# crediting them in full is what makes the ratio read far too harshly.
CONDITIONAL_UPTIME = 0.6

STAT_KEYS = {
    "atk%": "atkPct", "crit rate": "cr", "crit dmg": "cd",
    "hp%": None, "def%": None, "energy regen": None, "hp": None, "def": None,
}
PASSIVE_KEYS = {"dmgBonus": "dmg", "atkPct": "atkPct", "critRate": "cr", "critDmg": "cd",
                "defIgnore": "pen", "amplify": "pen", "resRed": "pen"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.loads(r.read())


def contribution(weapon):
    """Flat ATK plus the percentage terms a weapon brings, at refinement 1."""
    out = {"atk": 0.0, "atkPct": 0.0, "dmg": 0.0, "cr": 0.0, "cd": 0.0, "pen": 0.0}
    for name, raw in weapon.get("stats", {}).get("1", []):
        value = float(re.sub(r"[^0-9.]", "", raw) or 0)
        label = name.strip().lower()
        if label == "atk" and "%" not in raw:
            out["atk"] += value
            continue
        key = STAT_KEYS.get(label + ("%" if "%" in raw and label in ("atk", "hp", "def") else ""))
        if key:
            out[key] += value / 100.0
    for p in weapon.get("passiveBuffs", []):
        key = PASSIVE_KEYS.get(p.get("kind"))
        if not key:
            continue
        if "values" in p:
            value = float(p["values"].get("1", 0) or 0)
        elif "valuePerStack" in p:
            value = float(p["valuePerStack"].get("1", 0) or 0) * int(p.get("maxStacks", 1) or 1)
        else:
            continue
        if p.get("condition") != "unconditional":
            value *= CONDITIONAL_UPTIME
        out[key] += value / 100.0
    return out


def score(weapon):
    c = contribution(weapon)
    atk = (BASE["atk"] + c["atk"]) * (1 + BASE["atkPct"] + c["atkPct"])
    dmg = 1 + BASE["dmg"] + c["dmg"]
    crit = 1 + min(1.0, BASE["cr"] + c["cr"]) * (BASE["cd"] + c["cd"])
    pen = 1 + c["pen"]          # DEF ignore / amplify / RES shred multiply separately
    return atk * dmg * crit * pen


def main():
    weapons = {w["id"]: w for w in get(WEAPONS)}
    page = urllib.request.urlopen(urllib.request.Request(TEAM_PAGE, headers=UA), timeout=30).read().decode("utf-8", "replace")
    m = re.search(r"/data/team-dps-generated/([0-9a-f]{16,})/listing\.en\.json", page)
    if not m:
        print("could not find the Team DPS listing", file=sys.stderr)
        return 1
    listing = get(f"{ORIGIN}/data/team-dps-generated/{m.group(1)}/listing.en.json")
    ti = {k: i for i, k in enumerate(listing["tupleFields"]["team"])}
    bi = {k: i for i, k in enumerate(listing["tupleFields"]["firstRotationBuild"])}

    used = collections.defaultdict(collections.Counter)
    for team in listing["teams"]:
        for build in team[ti["firstRotationBuilds"]]:
            used[build[bi["characterId"]]][build[bi["weaponId"]]] += 1

    best_standard = {}
    for wid in STANDARD:
        w = weapons.get(wid)
        if not w:
            print(f"  ! standard weapon missing from weapons.json: {wid}", file=sys.stderr)
            continue
        kind = w["type"]
        if kind not in best_standard or score(w) > score(weapons[best_standard[kind]]):
            best_standard[kind] = wid

    out = {}
    for cid, counter in used.items():
        sig_id = counter.most_common(1)[0][0]
        sig = weapons.get(sig_id)
        if not sig:
            continue
        std_id = best_standard.get(sig["type"])
        if not std_id:
            continue
        ratio = 1.0 if sig_id in STANDARD else min(1.0, score(weapons[std_id]) / score(sig))
        out[cid] = {
            "s": sig["name"], "sid": sig_id,
            "b": weapons[std_id]["name"], "bid": std_id,
            "f": round(ratio, 4),
        }

    (ROOT / "weapons.js").write_text(
        "// Generated by tools/update-weapons.py.\n"
        "// s/sid: the weapon the Team DPS projection assumes (the character's signature).\n"
        "// b/bid: the strongest standard-banner weapon of that type.\n"
        "// f: modelled share of the signature's damage - an estimate, not arabwuwa's own number.\n"
        "const WEAPONS=" + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    ratios = sorted(v["f"] for v in out.values())
    print(f"wrote weapons.js: {len(out)} characters, factor {ratios[0]:.3f}–{ratios[-1]:.3f}, "
          f"median {ratios[len(ratios)//2]:.3f}")
    print("standard picks:", ", ".join(f"{k}={v}" for k, v in sorted(best_standard.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
