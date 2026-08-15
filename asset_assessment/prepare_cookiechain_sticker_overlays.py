#!/usr/bin/env python3
"""Build original-style Cookie Chain Edition sticker overlays from source art."""

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

from prepare_cookiechain_dapp_logo_stickers import OUTPUTS


CANVAS = 1393
STICKER_CENTER_X = 190
STICKER_BOTTOM_Y = 1308
STICKER_MAX_FOOTPRINT = 200

# This is the curated, active Cookie Chain Edition pool. Source art stays in
# the archive for provenance, but these outputs must never be reintroduced to
# assets/stickerz during a badge rebuild. Cookiebox and Morsel are the approved
# legacy representatives of their duplicate-brand pairs.
EXCLUDED_OUTPUTS = frozenset({
    "Bake_Your_Stake.png",
    "Cookiebox_Liquidity_Hub.png",
    "Hyperlane_Bridge.png",
    "Metaplex.png",
    "Morsel_Wallet.png",
    "Sesamians.png",
    "Sweetardio.png",
})


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy-dir", required=True, help="Archived original 11 sticker overlays")
    parser.add_argument("--dapp-source-dir", required=True, help="Official downloaded dapp-logo source directory")
    parser.add_argument("--dapp-manifest", required=True, help="Official dapp-logo registry manifest")
    parser.add_argument("--out", required=True, help="Sticker output directory")
    return parser.parse_args()


def visible_art(source: Path) -> Image.Image:
    image = Image.open(source).convert("RGBA")
    bbox = image.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError(f"{source.name}: no visible artwork")
    return image.crop(bbox)


def place_corner_sticker(source: Path) -> Image.Image:
    """Return a transparent full-canvas overlay with the native logo silhouette.

    This is the original Sweetardio Collection treatment: crop only unused
    transparent canvas, preserve the supplied art's own silhouette, fit it
    within the established 200px lower-left footprint, and add no frame,
    fill, outline, or new geometry.
    """
    art = visible_art(source)
    scale = min(STICKER_MAX_FOOTPRINT / art.width, STICKER_MAX_FOOTPRINT / art.height)
    art = art.resize(
        (max(1, round(art.width * scale)), max(1, round(art.height * scale))),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    position = (round(STICKER_CENTER_X - art.width / 2), STICKER_BOTTOM_Y - art.height)
    canvas.alpha_composite(art, position)
    return canvas


def preserve_native_overlay(source: Path) -> Image.Image:
    """Keep an already-authored 1393px legacy overlay byte-for-byte in spirit."""
    image = Image.open(source).convert("RGBA")
    if image.getchannel("A").getbbox() is None:
        raise ValueError(f"{source.name}: no visible artwork")
    return image if image.size == (CANVAS, CANVAS) else place_corner_sticker(source)


def entry_for(source: Path, output: str, origin: str, rendered: Image.Image, mode: str) -> dict:
    bbox = rendered.getchannel("A").getbbox()
    return {
        "output": output,
        "source": str(source),
        "origin": origin,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "treatment": {
            "mode": mode,
            "canvas": {"width": CANVAS, "height": CANVAS},
            "visible_bounds": {"left": bbox[0], "top": bbox[1], "right": bbox[2], "bottom": bbox[3]},
        },
    }


def is_active_output(output: str) -> bool:
    """Return whether a generated original-style overlay belongs in the active pool."""
    return output not in EXCLUDED_OUTPUTS


def main():
    args = parse_args()
    legacy_dir = Path(args.legacy_dir).expanduser().resolve()
    dapp_dir = Path(args.dapp_source_dir).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    dapp_manifest = json.loads(Path(args.dapp_manifest).expanduser().read_text(encoding="utf-8"))
    source_receipts = {
        item["slug"]: item for item in json.loads((dapp_dir / "SOURCES.json").read_text(encoding="utf-8"))
    }
    out.mkdir(parents=True, exist_ok=True)
    records = []
    expected = set()
    for source in sorted(legacy_dir.glob("*.png")):
        target = out / source.name
        if not is_active_output(target.name):
            continue
        overlay = preserve_native_overlay(source)
        overlay.save(target, optimize=True)
        records.append(entry_for(source, target.name, "legacy Cookie Chain sticker overlay", overlay, "preserved native canvas"))
        expected.add(target.name)
        print(f"restored legacy overlay {target.name}")
    for entry in dapp_manifest.get("entries", []):
        slug = entry["slug"]
        receipt = source_receipts.get(slug)
        if receipt is None:
            raise SystemExit(f"missing downloaded source receipt for {slug}")
        source = dapp_dir / receipt["file"]
        output = OUTPUTS[slug]
        target = out / output
        if not is_active_output(target.name):
            continue
        overlay = place_corner_sticker(source)
        overlay.save(target, optimize=True)
        records.append(entry_for(source, target.name, "official Cookie Chain Apps Registry logo", overlay, "native silhouette corner overlay"))
        expected.add(target.name)
        print(f"prepared dapp overlay {target.name}")
    actual = {path.name for path in out.glob("*.png")}
    for stale_name in sorted(actual & EXCLUDED_OUTPUTS):
        (out / stale_name).unlink()
    actual = {path.name for path in out.glob("*.png")}
    stale = actual - expected
    if stale:
        raise SystemExit(f"unexpected sticker PNG files after badge build: {sorted(stale)}")
    stale_manifest = out / "COOKIECHAIN_STICKER_BADGE_SOURCES.json"
    if stale_manifest.exists():
        stale_manifest.unlink()
    (out / "COOKIECHAIN_STICKER_SOURCES.json").write_text(
        json.dumps(records, indent=2) + "\n", encoding="utf-8"
    )
    print(f"prepared {len(records)} curated original-style sticker overlays -> {out}")


if __name__ == "__main__":
    main()
