#!/usr/bin/env python3
"""Repair approved public metadata labels in an already-rendered release."""

import argparse
import json
from collections import Counter
from pathlib import Path


REPLACEMENTS = {
    "Anime Detective": "L",
    "Armed Hero": "Real as a Doughnut",
    "Poptart Cat": "Nyancat",
}
RARITY_ORDER = ("Mythic Chase", "Legendary Chase", "Rare", "Uncommon", "Core")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", required=True)
    return parser.parse_args()


def normalize(token: dict) -> bool:
    changed = False
    for attribute in token.get("attributes", []):
        if attribute.get("trait_type") == "Sticker":
            old = attribute.get("value")
            if old in REPLACEMENTS:
                attribute["value"] = REPLACEMENTS[old]
                changed = True
    return changed


def write_rarity(release: Path, manifest: list[dict]) -> None:
    counts = {key: Counter() for key in ("Sticker", "Arms", "Background", "Character", "Rarity")}
    for token in manifest:
        for attribute in token.get("attributes", []):
            trait = attribute.get("trait_type")
            if trait in counts:
                counts[trait][attribute.get("value", "")] += 1
    lines = ["# Cookie Chain Edition — Rarity", "", f"Supply: **{len(manifest)}** · Seed: **871003** · all trait combinations unique.", "", "## Exact tiers", ""]
    for tier in RARITY_ORDER:
        n = counts["Rarity"][tier]
        lines.append(f"- {tier}: **{n}** ({100*n/len(manifest):.2f}%)")
    for group in ("Sticker", "Arms", "Background", "Character"):
        lines.extend(("", f"## {group}", ""))
        for name, n in sorted(counts[group].items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"- {name}: {n} ({100*n/len(manifest):.2f}%)")
    (release / "RARITY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    args = parse_args()
    release = Path(args.release).expanduser().resolve()
    metadata_dir = release / "metadata"
    changed = 0
    for path in sorted(metadata_dir.glob("*.json")):
        token = json.loads(path.read_text(encoding="utf-8"))
        if normalize(token):
            path.write_text(json.dumps(token, indent=2) + "\n", encoding="utf-8")
            changed += 1
    manifest_path = release / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for token in manifest:
        normalize(token)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_rarity(release, manifest)
    print(f"updated public sticker labels in {changed} metadata records")


if __name__ == "__main__":
    main()
