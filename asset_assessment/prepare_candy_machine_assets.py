#!/usr/bin/env python3
"""Create zero-indexed Sugar assets from a rendered Cookie Chain release.

Input:  a build_side_collection.py output directory containing images/001.png
        through images/444.png and matching metadata/001.json through 444.json.
Output: an assets directory containing collection.{png,json} and 0.{png,json}
        through 443.{png,json}, ready for the legacy Candy Machine v3 Sugar flow.
"""

import argparse
import json
import shutil
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Rendered release output directory")
    parser.add_argument("--out", required=True, help="Target Sugar assets directory")
    parser.add_argument("--count", type=int, default=444, help="Expected release size")
    parser.add_argument(
        "--collection-name",
        default="Sweetardio — Cookie Chain Edition",
        help="Collection metadata name",
    )
    parser.add_argument(
        "--collection-description",
        default="A 444-piece Sweetardio side edition for the Cookie Chain.",
        help="Collection metadata description",
    )
    return parser.parse_args()


def load_token(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        token = json.load(handle)
    if not isinstance(token.get("name"), str) or not token["name"].strip():
        raise ValueError(f"{path} is missing a token name")
    if not isinstance(token.get("attributes"), list):
        raise ValueError(f"{path} is missing its attributes array")
    return token


def sugar_metadata(token: dict, image_name: str) -> dict:
    """Retain public metadata while changing only local image references."""
    output = {
        "name": token["name"],
        "description": token.get("description", ""),
        "image": image_name,
        "attributes": token["attributes"],
        "properties": {
            "files": [{"uri": image_name, "type": "image/png"}],
            "category": "image",
        },
    }
    if token.get("external_url"):
        output["external_url"] = token["external_url"]
    return output


def main():
    args = parse_args()
    source = Path(args.source).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    image_source = source / "images"
    metadata_source = source / "metadata"
    if not image_source.is_dir() or not metadata_source.is_dir():
        raise SystemExit("source must contain images/ and metadata/ directories")
    if args.count < 1:
        raise SystemExit("count must be positive")

    out.mkdir(parents=True, exist_ok=True)
    expected = []
    for token_number in range(1, args.count + 1):
        stem = f"{token_number:03d}"
        image_path = image_source / f"{stem}.png"
        metadata_path = metadata_source / f"{stem}.json"
        if not image_path.is_file() or not metadata_path.is_file():
            raise SystemExit(f"missing rendered pair for token #{stem}")
        expected.extend([f"{token_number - 1}.png", f"{token_number - 1}.json"])

    # Refuse to leave stale numbered pairs from a different collection in place.
    for child in out.iterdir():
        if child.name in {"collection.png", "collection.json"} or child.name in expected:
            child.unlink()

    for token_number in range(1, args.count + 1):
        source_stem = f"{token_number:03d}"
        target_stem = str(token_number - 1)
        token = load_token(metadata_source / f"{source_stem}.json")
        shutil.copy2(image_source / f"{source_stem}.png", out / f"{target_stem}.png")
        with (out / f"{target_stem}.json").open("w", encoding="utf-8") as handle:
            json.dump(sugar_metadata(token, f"{target_stem}.png"), handle, indent=2)
            handle.write("\n")

    # Use a final rendered token as the collection artwork. The deployer may
    # replace this pair with a separately approved collection image before launch.
    shutil.copy2(image_source / "001.png", out / "collection.png")
    collection = {
        "name": args.collection_name,
        "description": args.collection_description,
        "image": "collection.png",
        "properties": {
            "files": [{"uri": "collection.png", "type": "image/png"}],
            "category": "image",
        },
    }
    with (out / "collection.json").open("w", encoding="utf-8") as handle:
        json.dump(collection, handle, indent=2)
        handle.write("\n")

    print(f"prepared {args.count} indexed Sugar asset pairs in {out}")
    print("review collection.png and collection.json before upload")


if __name__ == "__main__":
    main()
