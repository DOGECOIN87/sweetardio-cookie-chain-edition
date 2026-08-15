#!/usr/bin/env python3
"""Normalize official Cookie Chain dapp logos as collection sticker overlays."""

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


CANVAS = 1393
STICKER_CENTER_X = 190
STICKER_BOTTOM_Y = 1308
STICKER_MAX_FOOTPRINT = 200
OUTPUTS = {
    "cookie_scan": "CookieScan.png",
    "hyperlane_bridge": "Hyperlane_Bridge.png",
    "nightly_wallet": "Nightly_Wallet.png",
    "defi_llama": "DefiLlama.png",
    "bake_your_stake": "Bake_Your_Stake.png",
    "cookie_swap": "CookieSwap.png",
    "candy_shop": "Candy_Shop.png",
    "metaplex": "Metaplex.png",
    "cookie_quads": "Cookie_Quads.png",
    "cookiebox_liquidity_hub": "Cookiebox_Liquidity_Hub.png",
    "cookiescan_das_api": "CookieScan_DAS_API.png",
    "momo_swap": "MomoSwap.png",
    "morsel_wallet": "Morsel_Wallet.png",
    "cook_oven": "CookOven.png",
    "cook_book": "CookBook.png",
    "cookie_lock": "Cookie_Lock.png",
    "cookie_chat": "Cookie_Chat.png",
    "gorboy": "GORBOY.png",
    "sesamians": "Sesamians.png",
    "baked_bazaar": "Baked_Bazaar.png",
    "gorweld": "GorWeld.png",
    "cookie_mcp": "Cookie_MCP.png",
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", required=True, help="Downloaded source-logo directory")
    parser.add_argument("--manifest", required=True, help="Registry-derived JSON manifest")
    parser.add_argument("--out", required=True, help="Sticker output directory")
    return parser.parse_args()


def prepare(source: Path):
    image = Image.open(source).convert("RGBA")
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        raise ValueError(f"{source.name}: no visible artwork")
    art = image.crop(bbox)
    scale = min(STICKER_MAX_FOOTPRINT / art.width, STICKER_MAX_FOOTPRINT / art.height)
    art = art.resize(
        (max(1, round(art.width * scale)), max(1, round(art.height * scale))),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    position = (round(STICKER_CENTER_X - art.width / 2), STICKER_BOTTOM_Y - art.height)
    canvas.alpha_composite(art, position)
    return canvas, art.size, position


def main():
    args = parse_args()
    source_dir = Path(args.sources).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    manifest = json.loads(Path(args.manifest).expanduser().read_text(encoding="utf-8"))
    receipts = {item["slug"]: item for item in json.loads((source_dir / "SOURCES.json").read_text(encoding="utf-8"))}
    entries = manifest.get("entries", [])
    if {item.get("slug") for item in entries} != set(OUTPUTS):
        raise SystemExit("registry manifest and output mapping must contain the same dapp slugs")
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for entry in entries:
        slug = entry["slug"]
        receipt = receipts.get(slug)
        if receipt is None:
            raise SystemExit(f"missing downloaded source for {slug}")
        source = source_dir / receipt["file"]
        sticker, art_size, position = prepare(source)
        target = out / OUTPUTS[slug]
        sticker.save(target, optimize=True)
        results.append({
            "slug": slug,
            "title": entry["title"],
            "source_url": entry["logo"],
            "source_sha256": receipt["sha256"],
            "output": target.name,
            "art_size": {"width": art_size[0], "height": art_size[1]},
            "position": {"x": position[0], "y": position[1]},
            "canvas": {"width": CANVAS, "height": CANVAS},
        })
        print(f"prepared {target.name} art={art_size[0]}x{art_size[1]} pos={position}")
    manifest_path = out / "COOKIECHAIN_DAPP_LOGO_SOURCES.json"
    manifest_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"prepared {len(results)} dapp-logo stickers -> {out}")


if __name__ == "__main__":
    main()
