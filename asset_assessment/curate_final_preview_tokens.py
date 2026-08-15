#!/usr/bin/env python3
"""Select 50 visually varied finalized tokens for the Cookie Chain mint carousel."""

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps


SPECIAL_IDS = (176, 79, 434, 268)  # Nightly, Mattrick, Shubbi, Tenders
PRINTER_TARGET = 8
RARITY_BONUS = {"Mythic Chase": 10.0, "Legendary Chase": 7.0, "Rare": 2.0, "Uncommon": 1.0, "Core": 0.0}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--max-perceptual-distance",
        type=int,
        default=6,
        help="Maximum combined 128-bit hash distance accepted as visually distinct (default: 6).",
    )
    return parser.parse_args()


def attrs(token):
    return {entry["trait_type"]: entry["value"] for entry in token["attributes"]}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bit_hash(image: Image.Image, *, mode: str) -> int:
    normalized = ImageOps.grayscale(image.convert("RGBA").convert("RGB"))
    if mode == "dhash":
        pixels = list(normalized.resize((9, 8), Image.Resampling.LANCZOS).getdata())
        bits = 0
        for row in range(8):
            for col in range(8):
                bits = (bits << 1) | int(pixels[row * 9 + col] > pixels[row * 9 + col + 1])
        return bits
    pixels = list(normalized.resize((8, 8), Image.Resampling.LANCZOS).getdata())
    average = sum(pixels) / len(pixels)
    bits = 0
    for pixel in pixels:
        bits = (bits << 1) | int(pixel >= average)
    return bits


def hamming_distance(left: int, right: int) -> int:
    return (left ^ right).bit_count()


def visually_distinct(candidate, chosen, *, max_distance: int) -> bool:
    return all(
        candidate["sha256"] != item["sha256"]
        and hamming_distance(candidate["dhash"], item["dhash"]) + hamming_distance(candidate["ahash"], item["ahash"]) > max_distance
        for item in chosen
    )


def main():
    args = parse_args()
    release = Path(args.release).expanduser().resolve()
    manifest = json.loads((release / "manifest.json").read_text(encoding="utf-8"))
    rows = []
    for number, token in enumerate(manifest, 1):
        values = attrs(token)
        image_path = release / "images" / f"{number:03d}.png"
        with Image.open(image_path) as image:
            dhash = bit_hash(image, mode="dhash")
            ahash = bit_hash(image, mode="ahash")
        rows.append({
            "id": number,
            "name": values.get("Character", ""),
            "rarity": values.get("Rarity", ""),
            "sticker": values.get("Sticker", ""),
            "background": values.get("Background", ""),
            "arms": values.get("Arms", ""),
            "selection_score": token.get("selection_score", 0.0),
            "sha256": sha256(image_path),
            "dhash": dhash,
            "ahash": ahash,
        })
    by_id = {row["id"]: row for row in rows}
    chosen = []
    for item in SPECIAL_IDS:
        candidate = by_id[item]
        if not visually_distinct(candidate, chosen, max_distance=args.max_perceptual_distance):
            raise RuntimeError(f"Required special token #{item:03d} conflicts with the visual uniqueness rule")
        chosen.append(candidate)
    seen = {item["id"] for item in chosen}
    printer = [row for row in rows if row["arms"] == "Printer" and row["id"] not in seen]
    for row in sorted(printer, key=lambda item: (-item["selection_score"], item["id"])):
        if len([item for item in chosen if item["arms"] == "Printer"]) >= PRINTER_TARGET:
            break
        if visually_distinct(row, chosen, max_distance=args.max_perceptual_distance):
            chosen.append(row)
            seen.add(row["id"])
    used_characters = {item["name"] for item in chosen}
    used_backgrounds = {item["background"] for item in chosen}
    used_stickers = {item["sticker"] for item in chosen}
    while len(chosen) < 50:
        candidates = [
            row
            for row in rows
            if row["id"] not in seen and visually_distinct(row, chosen, max_distance=args.max_perceptual_distance)
        ]
        if not candidates:
            raise RuntimeError("Unable to curate 50 visually unique carousel renders from the release")
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
