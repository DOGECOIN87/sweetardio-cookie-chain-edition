#!/usr/bin/env python3
"""Build white-bordered square Cookie Chain Edition sticker badges from source art."""

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

from prepare_cookiechain_dapp_logo_stickers import OUTPUTS


CANVAS = 1393
BADGE = 200
BORDER = 8
INNER_ART = 160
BADGE_X = 90
BADGE_Y = 1108
OXFORD = (7, 15, 52, 255)
WHITE = (255, 255, 255, 255)

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


def make_badge(source: Path) -> Image.Image:
    art = visible_art(source)
    scale = min(INNER_ART / art.width, INNER_ART / art.height)
    art = art.resize(
        (max(1, round(art.width * scale)), max(1, round(art.height * scale))),
        Image.Resampling.LANCZOS,
    )
    badge = Image.new("RGBA", (BADGE, BADGE), WHITE)
    draw = ImageDraw.Draw(badge)
    draw.rectangle((BORDER, BORDER, BADGE - BORDER - 1, BADGE - BORDER - 1), fill=OXFORD)
    badge.alpha_composite(art, ((BADGE - art.width) // 2, (BADGE - art.height) // 2))
    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    canvas.alpha_composite(badge, (BADGE_X, BADGE_Y))
    return canvas


def entry_for(source: Path, output: str, origin: str) -> dict:
    return {
        "output": output,
        "source": str(source),
        "origin": origin,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "badge": {"width": BADGE, "height": BADGE, "border": BORDER, "x": BADGE_X, "y": BADGE_Y},
    }


def is_active_output(output: str) -> bool:
    """Return whether a generated badge belongs in the curated active pool."""
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
        make_badge(source).save(target, optimize=True)
        records.append(entry_for(source, target.name, "legacy Cookie Chain sticker overlay"))
        expected.add(target.name)
        print(f"badged legacy {target.name}")
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
        make_badge(source).save(target, optimize=True)
        records.append(entry_for(source, target.name, "official Cookie Chain Apps Registry logo"))
        expected.add(target.name)
        print(f"badged dapp {target.name}")
    actual = {path.name for path in out.glob("*.png")}
    for stale_name in sorted(actual & EXCLUDED_OUTPUTS):
        (out / stale_name).unlink()
    actual = {path.name for path in out.glob("*.png")}
    stale = actual - expected
    if stale:
        raise SystemExit(f"unexpected sticker PNG files after badge build: {sorted(stale)}")
    (out / "COOKIECHAIN_STICKER_BADGE_SOURCES.json").write_text(
        json.dumps(records, indent=2) + "\n", encoding="utf-8"
    )
    print(f"prepared {len(records)} curated white-bordered square sticker badges -> {out}")


if __name__ == "__main__":
    main()
