#!/usr/bin/env python3
"""Select 50 visually varied finalized tokens for the Cookie Chain mint carousel."""

import argparse
import json
from pathlib import Path


SPECIAL_IDS = (176, 79, 434, 268)  # Nightly, Mattrick, Shubbi, Tenders
PRINTER_TARGET = 8
RARITY_BONUS = {"Mythic Chase": 10.0, "Legendary Chase": 7.0, "Rare": 2.0, "Uncommon": 1.0, "Core": 0.0}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", required=True)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def attrs(token):
    return {entry["trait_type"]: entry["value"] for entry in token["attributes"]}


def main():
    args = parse_args()
    release = Path(args.release).expanduser().resolve()
    manifest = json.loads((release / "manifest.json").read_text(encoding="utf-8"))
    rows = []
    for number, token in enumerate(manifest, 1):
        values = attrs(token)
        rows.append({
            "id": number,
            "name": values.get("Character", ""),
            "rarity": values.get("Rarity", ""),
            "sticker": values.get("Sticker", ""),
            "background": values.get("Background", ""),
            "arms": values.get("Arms", ""),
            "selection_score": token.get("selection_score", 0.0),
        })
    by_id = {row["id"]: row for row in rows}
    chosen = [by_id[item] for item in SPECIAL_IDS]
    seen = {item["id"] for item in chosen}
    printer = [row for row in rows if row["arms"] == "Printer" and row["id"] not in seen]
    for row in sorted(printer, key=lambda item: (-item["selection_score"], item["id"]))[:PRINTER_TARGET]:
        chosen.append(row)
        seen.add(row["id"])
    used_characters = {item["name"] for item in chosen}
    used_backgrounds = {item["background"] for item in chosen}
    used_stickers = {item["sticker"] for item in chosen}
    while len(chosen) < 50:
        candidates = [row for row in rows if row["id"] not in seen]
        def rank(row):
            diversity = (4.0 if row["name"] not in used_characters else 0.0)
            diversity += 3.0 if row["background"] not in used_backgrounds else 0.0
            diversity += 2.0 if row["sticker"] not in used_stickers else 0.0
            return RARITY_BONUS.get(row["rarity"], 0.0) + diversity + row["selection_score"]
        winner = max(candidates, key=lambda item: (rank(item), -item["id"]))
        chosen.append(winner)
        seen.add(winner["id"])
        used_characters.add(winner["name"])
        used_backgrounds.add(winner["background"])
        used_stickers.add(winner["sticker"])
    result = {"count": len(chosen), "selection": chosen}
    target = Path(args.out).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"curated {len(chosen)} tokens -> {target}")


if __name__ == "__main__":
    main()
