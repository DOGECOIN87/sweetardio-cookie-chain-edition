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
CANVAS = (1393, 1393)
DEFAULT_STICKER_DIR = Path(__file__).resolve().parent.parent / "assets" / "stickerz"
NIGHTLY_LEGENDARY_BACKGROUND = "Nightly Legendary"
NIGHTLY_LEGENDARY_STICKER = "Nightly Wallet"


def sticker_display_name(path: Path) -> str:
    """Mirror the public sticker names emitted by the Cookie Chain builder."""
    overrides = {
        "Out_Of_Order": "Out of Order",
        "Anime_Detective": "L",
        "Armed_Hero": "Real as a Doughnut",
        "GORBOY": "Cookboy",
        "Poptart_Cat": "Nyancat",
    }
    return overrides.get(path.stem, path.stem.replace("_", " "))


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", required=True, help="Rendered release directory")
    parser.add_argument("--count", type=int, default=444, help="Expected token count")
    parser.add_argument(
        "--sticker-dir",
        default=str(DEFAULT_STICKER_DIR),
        help="Directory containing the sticker files expected in the release",
    )
    return parser.parse_args()


def load_token(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def expected_rarity_counts(count: int) -> Counter:
    """Match build_side_collection.py tier behavior for production and previews."""
    if count == sum(EXPECTED_RARITY.values()):
        return Counter(EXPECTED_RARITY)
    weights = [(name, amount / 444) for name, amount in EXPECTED_RARITY.items()]
    counts, used = {}, 0
    for name, share in weights[:-1]:
        counts[name] = round(count * share)
        used += counts[name]
    counts[weights[-1][0]] = count - used
    return Counter(counts)


def main():
    args = parse_args()
    release = Path(args.release).expanduser().resolve()
    image_dir = release / "images"
    metadata_dir = release / "metadata"
    sticker_dir = Path(args.sticker_dir).expanduser().resolve()
    image_paths = sorted(image_dir.glob("*.png"))
    metadata_paths = sorted(metadata_dir.glob("*.json"))
    expected_stickers = {sticker_display_name(path) for path in sticker_dir.glob("*.png")}

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
        "expected_stickers": sorted(expected_stickers),
        "backgrounds": {},
        "nightly_legendary_count": 0,
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
    if not expected_stickers:
        report["issues"].append(f"no PNG sticker files in {sticker_dir}")

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
    nightly_tokens = []
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
        if values.get("Arms") == "Printer" and "gummy bear" in values.get("Character", "").lower():
            report["issues"].append(f"{metadata_path.name} assigns Printer to a gummy-bear character")
        if values.get("Character") == "Sugar Doughnut" and values.get("Footwear") == "Gorbhouse Slippers":
            report["issues"].append(
                f"{metadata_path.name} contains blocked Sugar Doughnut + Gorbhouse pairing")
        if values.get("Background") == NIGHTLY_LEGENDARY_BACKGROUND:
            nightly_tokens.append((metadata_path.name, values))

    if actual_names != expected_names:
        report["issues"].append("token names are not the exact #001–#444 public sequence")
    expected_rarity = expected_rarity_counts(args.count)
    if rarity != expected_rarity:
        report["issues"].append(f"rarity mismatch: {dict(rarity)}")
    expected_arms = Counter({"Cookboy Handheld": 22, "Printer": 22}) if args.count == 444 else Counter()
    if arms != expected_arms:
        report["issues"].append(f"arms mismatch: {dict(arms)}")
    if set(stickers) != expected_stickers:
        missing = sorted(expected_stickers - set(stickers))
        unexpected = sorted(set(stickers) - expected_stickers)
        report["issues"].append(
            f"sticker pool mismatch; missing={missing}, unexpected={unexpected}")
    if expected_stickers:
        floor, remainder = divmod(args.count, len(expected_stickers))
        permitted = {floor, floor + 1} if remainder else {floor}
        invalid_counts = {
            name: stickers.get(name, 0) for name in sorted(expected_stickers)
            if stickers.get(name, 0) not in permitted
        }
        if invalid_counts:
            report["issues"].append(
                f"sticker distribution must be {sorted(permitted)} per asset: {invalid_counts}")
    if len(signatures) != args.count:
        report["issues"].append(
            f"expected {args.count} unique public trait signatures, found {len(signatures)}")
    if args.count == 444:
        if len(nightly_tokens) != 1:
            report["issues"].append(
                f"expected exactly one {NIGHTLY_LEGENDARY_BACKGROUND} background, found {len(nightly_tokens)}")
        elif nightly_tokens[0][1].get("Rarity") != "Legendary Chase":
            report["issues"].append("Nightly Legendary token must be Legendary Chase")
        elif nightly_tokens[0][1].get("Sticker") != NIGHTLY_LEGENDARY_STICKER:
            report["issues"].append("Nightly Legendary token must carry the Nightly Wallet sticker")

    report["rarity"] = dict(rarity)
    report["arms"] = dict(arms)
    report["stickers"] = dict(stickers)
    report["backgrounds"] = dict(backgrounds)
    report["nightly_legendary_count"] = len(nightly_tokens)
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
