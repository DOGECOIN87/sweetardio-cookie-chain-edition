#!/usr/bin/env python3
"""Audit a curated Cookie Chain carousel for repeated or visually duplicate renders."""

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path

from PIL import Image, ImageOps


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", required=True, help="Release directory containing images/.")
    parser.add_argument("--selection", required=True, help="Preview-selection JSON file.")
    parser.add_argument("--out", required=True, help="Audit JSON output path.")
    parser.add_argument(
        "--max-perceptual-distance",
        type=int,
        default=6,
        help="Maximum combined 128-bit hash distance considered visually duplicated (default: 6).",
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bit_hash(image: Image.Image, *, mode: str) -> int:
    """Return a stable 64-bit dHash or average-hash of a normalized render."""
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


def main():
    args = parse_args()
    release = Path(args.release).expanduser().resolve()
    selection_path = Path(args.selection).expanduser().resolve()
    output_path = Path(args.out).expanduser().resolve()
    selection = json.loads(selection_path.read_text(encoding="utf-8"))["selection"]

    entries = []
    for item in selection:
        token_id = int(item["id"])
        image_path = release / "images" / f"{token_id:03d}.png"
        if not image_path.is_file():
            raise FileNotFoundError(f"Missing render for carousel token #{token_id}: {image_path}")
        with Image.open(image_path) as image:
            entries.append(
                {
                    "id": f"{token_id:03d}",
                    "sha256": sha256(image_path),
                    "dhash": bit_hash(image, mode="dhash"),
                    "ahash": bit_hash(image, mode="ahash"),
                }
            )

    def groups_by(key: str):
        grouped = {}
        for entry in entries:
            grouped.setdefault(entry[key], []).append(entry["id"])
        return [ids for ids in grouped.values() if len(ids) > 1]

    exact_duplicates = groups_by("sha256")
    id_duplicates = groups_by("id")
    perceptual_matches = []
    for left, right in combinations(entries, 2):
        distance = hamming_distance(left["dhash"], right["dhash"]) + hamming_distance(left["ahash"], right["ahash"])
        if distance <= args.max_perceptual_distance:
            perceptual_matches.append({"ids": [left["id"], right["id"]], "distance": distance})

    report = {
        "selection_count": len(entries),
        "unique_ids": len({entry["id"] for entry in entries}),
        "unique_sha256": len({entry["sha256"] for entry in entries}),
        "perceptual_distance_limit": args.max_perceptual_distance,
        "id_duplicate_groups": id_duplicates,
        "exact_duplicate_groups": exact_duplicates,
        "perceptual_duplicate_pairs": perceptual_matches,
        "passed": not id_duplicates and not exact_duplicates and not perceptual_matches,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
