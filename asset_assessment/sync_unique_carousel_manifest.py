#!/usr/bin/env python3
"""Sync an audited unique preview selection into the catalog and managed mint carousel."""

import argparse
import json
from pathlib import Path


SPECIAL_BACKGROUNDS = {
    "Nightly Legendary",
    "Mattrick Legendary",
    "Shubbi Legendary",
    "Tenders Legendary",
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", required=True, help="Audited unique preview-selection JSON.")
    parser.add_argument("--existing-catalog", required=True, help="Current catalog selection JSON with managed URLs.")
    parser.add_argument("--catalog-out", required=True, help="Catalog JSON output path.")
    parser.add_argument("--managed-out", required=True, help="Managed TypeScript carousel-data output path.")
    parser.add_argument(
        "--new-asset",
        action="append",
        default=[],
        metavar="TOKEN_ID=URL",
        help="Managed asset URL for an inserted token; repeat as needed.",
    )
    return parser.parse_args()


def parse_asset_overrides(entries):
    overrides = {}
    for entry in entries:
        token_id, separator, url = entry.partition("=")
        if not separator or not token_id.isdigit() or not url.startswith("/manus-storage/"):
            raise ValueError(f"Invalid --new-asset value: {entry!r}")
        overrides[int(token_id)] = url
    return overrides


def main():
    args = parse_args()
    selection = json.loads(Path(args.selection).read_text(encoding="utf-8"))["selection"]
    existing = json.loads(Path(args.existing_catalog).read_text(encoding="utf-8"))["selection"]
    existing_assets = {int(token["id"]): token["image"] for token in existing}
    assets = {**existing_assets, **parse_asset_overrides(args.new_asset)}

    tokens = []
    for item in selection:
        token_id = int(item["id"])
        image = assets.get(token_id)
        if not image:
            raise ValueError(f"No managed image URL is available for token #{token_id:03d}")
        background = item["background"]
        tokens.append(
            {
                "id": f"{token_id:03d}",
                "name": item["name"],
                "image": image,
                "rarity": item["rarity"],
                "sticker": f"{item['sticker']} sticker",
                "note": background if background in SPECIAL_BACKGROUNDS else "Curated draw",
                "background": background,
                "arms": item["arms"],
            }
        )

    if len(tokens) != 50 or len({token["id"] for token in tokens}) != 50:
        raise ValueError("Expected exactly 50 unique carousel token IDs")

    catalog_path = Path(args.catalog_out)
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_path.write_text(json.dumps({"count": len(tokens), "selection": tokens}, indent=2) + "\n", encoding="utf-8")

    managed_path = Path(args.managed_out)
    managed_path.parent.mkdir(parents=True, exist_ok=True)
    managed_tokens = [{key: token[key] for key in ("id", "name", "image", "rarity", "sticker", "note")} for token in tokens]
    managed_path.write_text(
        "// Generated from the audited unique Cookie Chain Edition release; do not hand-edit.\n"
        "export type PreviewToken = { id: string; name: string; image: string; rarity: string; sticker: string; note: string };\n\n"
        f"export const previewTokens: PreviewToken[] = {json.dumps(managed_tokens, indent=2)};\n",
        encoding="utf-8",
    )
    print(f"synced {len(tokens)} unique carousel previews")


if __name__ == "__main__":
    main()
