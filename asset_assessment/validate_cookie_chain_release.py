#!/usr/bin/env python3
"""Validate a rendered 444-piece Cookie Chain Edition release directory."""

import argparse
import json
from collections import Counter
from pathlib import Path

from PIL import Image


EXPECTED_RARITY = {
    "Mythic Chase": 4,
    "Legendary Chase": 18,
    "Rare": 66,
    "Uncommon": 134,
    "Core": 222,
}
EXPECTED_STICKERS = {"Morsel": 40, "Cookiebox": 41}
CANVAS = (1393, 1393)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", required=True, help="Rendered release directory")
    parser.add_argument("--count", type=int, default=444, help="Expected token count")
    return parser.parse_args()


def load_token(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main():
    args = parse_args()
    release = Path(args.release).expanduser().resolve()
    image_dir = release / "images"
    metadata_dir = release / "metadata"
    image_paths = sorted(image_dir.glob("*.png"))
    metadata_paths = sorted(metadata_dir.glob("*.json"))

    report = {
        "release": str(release),
        "expected_count": args.count,
        "images": len(image_paths),
        "metadata": len(metadata_paths),
        "manifest": 0,
        "image_dimensions": {},
        "rarity": {},
        "arms": {},
        "stickers": {},
        "backgrounds": {},
        "public_trait_signatures": 0,
        "issues": [],
    }

    manifest_path = release / "manifest.json"
    if manifest_path.is_file():
        manifest = load_token(manifest_path)
        report["manifest"] = len(manifest) if isinstance(manifest, list) else 0
    else:
        report["issues"].append("missing manifest.json")

    if len(image_paths) != args.count:
        report["issues"].append(f"expected {args.count} images, found {len(image_paths)}")
    if len(metadata_paths) != args.count:
        report["issues"].append(f"expected {args.count} metadata files, found {len(metadata_paths)}")
    if report["manifest"] != args.count:
        report["issues"].append(
            f"expected manifest with {args.count} tokens, found {report['manifest']}")

    dimensions = Counter()
    for image_path in image_paths:
        with Image.open(image_path) as image:
            dimensions[f"{image.width}x{image.height} {image.mode}"] += 1
            if image.size != CANVAS or image.mode != "RGBA":
                report["issues"].append(
                    f"{image_path.name} must be {CANVAS[0]}x{CANVAS[1]} RGBA, "
                    f"found {image.width}x{image.height} {image.mode}")
    report["image_dimensions"] = dict(dimensions)

    rarity = Counter()
    arms = Counter()
    stickers = Counter()
    backgrounds = Counter()
    signatures = set()
    expected_names = {f"Cookie Chain Edition #{number:03d}" for number in range(1, args.count + 1)}
    actual_names = set()
    for index, metadata_path in enumerate(metadata_paths, 1):
        token = load_token(metadata_path)
        actual_names.add(token.get("name"))
        attrs = token.get("attributes")
        if not isinstance(attrs, list):
            report["issues"].append(f"{metadata_path.name} is missing attributes")
            continue
        values = {}
        for attribute in attrs:
            trait_type = attribute.get("trait_type")
            value = attribute.get("value")
            if not isinstance(trait_type, str) or not isinstance(value, str):
                report["issues"].append(f"{metadata_path.name} has an invalid attribute")
                continue
            if trait_type in values:
                report["issues"].append(f"{metadata_path.name} repeats {trait_type}")
            values[trait_type] = value
        signatures.add(tuple(sorted(values.items())))
        rarity[values.get("Rarity", "<missing>")] += 1
        if "Arms" in values:
            arms[values["Arms"]] += 1
        if "Sticker" in values:
            stickers[values["Sticker"]] += 1
        if "Background" in values:
            backgrounds[values["Background"]] += 1
        if values.get("Edition") != "Cookie Chain Edition":
            report["issues"].append(f"{metadata_path.name} has invalid Edition metadata")
        if values.get("Arms") == "Cookie Hands":
            report["issues"].append(f"{metadata_path.name} contains removed Cookie Hands trait")
        if values.get("Character") == "Sugar Doughnut" and values.get("Footwear") == "Gorbhouse Slippers":
            report["issues"].append(
                f"{metadata_path.name} contains blocked Sugar Doughnut + Gorbhouse pairing")

    if actual_names != expected_names:
        report["issues"].append("token names are not the exact #001–#444 public sequence")
    if rarity != Counter(EXPECTED_RARITY):
        report["issues"].append(f"rarity mismatch: {dict(rarity)}")
    if arms != Counter({"Cookboy Handheld": 22}):
        report["issues"].append(f"arms mismatch: {dict(arms)}")
    for sticker, expected in EXPECTED_STICKERS.items():
        if stickers.get(sticker) != expected:
            report["issues"].append(
                f"{sticker} sticker count is {stickers.get(sticker, 0)}, expected {expected}")
    if len(signatures) != args.count:
        report["issues"].append(
            f"expected {args.count} unique public trait signatures, found {len(signatures)}")

    report["rarity"] = dict(rarity)
    report["arms"] = dict(arms)
    report["stickers"] = dict(stickers)
    report["backgrounds"] = dict(backgrounds)
    report["public_trait_signatures"] = len(signatures)
    report_path = release / "VALIDATION.json"
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")

    if report["issues"]:
        raise SystemExit(f"validation failed; see {report_path}")
    print(f"validation passed: {args.count} tokens -> {report_path}")


if __name__ == "__main__":
    main()
