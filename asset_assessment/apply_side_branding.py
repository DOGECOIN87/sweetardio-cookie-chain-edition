#!/usr/bin/env python3
"""Prepare and apply the Cookie Chain Edition badge to side-edition tokens."""

import argparse
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent.parent
SIDE_ROOT = ROOT / "side_collection" if (ROOT / "side_collection").is_dir() else ROOT
SOURCE = (SIDE_ROOT / "assets" / "catalog_uploads" /
          "file_00000000ff0c82309ed8c5681a61919d.png")
OVERLAY = SIDE_ROOT / "assets" / "branding" / "cookie_chain_edition.png"
CANVAS = 1393
BADGE_WIDTH = 390
MARGIN_X = 30
MARGIN_Y = 28


def prepare_overlay() -> Image.Image:
    source = Image.open(SOURCE).convert("RGB")
    # The uploaded image presents the plaque on a dark 1536x1024 field. This
    # crop isolates the actual gold nameplate without baking that field into
    # every token.
    plaque = source.crop((31, 354, 1505, 650))
    height = round(plaque.height * BADGE_WIDTH / plaque.width)
    plaque = plaque.resize((BADGE_WIDTH, height), Image.Resampling.LANCZOS).convert("RGBA")

    # A rounded mask follows the plaque's silhouette and discards the remaining
    # rectangular presentation backdrop while retaining its soft gold edge.
    mask = Image.new("L", plaque.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, plaque.width - 1, plaque.height - 1),
        radius=max(1, round(plaque.height * 0.42)), fill=255,
    )
    plaque.putalpha(mask)

    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    x = CANVAS - MARGIN_X - plaque.width
    y = CANVAS - MARGIN_Y - plaque.height
    canvas.alpha_composite(plaque, (x, y))
    OVERLAY.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OVERLAY)
    return canvas


def apply_one(path: Path, overlay: Image.Image) -> None:
    token = Image.open(path).convert("RGBA")
    if token.size != (CANVAS, CANVAS):
        raise ValueError(f"{path}: expected {CANVAS}x{CANVAS}, got {token.size}")
    token.alpha_composite(overlay)
    temporary = path.with_name(f".{path.name}.branding.tmp.png")
    token.save(temporary, compress_level=1)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", default="output/images")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--start", type=int, default=1,
                        help="first numeric token to brand (for resumable batches)")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    overlay = prepare_overlay()
    print(f"prepared {OVERLAY.relative_to(ROOT)}")
    if args.prepare_only:
        return
    image_dir = (SIDE_ROOT / args.images).resolve()
    paths = [path for path in sorted(image_dir.glob("*.png"))
             if path.stem.isdigit() and int(path.stem) >= args.start]
    if not paths:
        raise SystemExit(f"no PNG tokens in {image_dir}")
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
      for index, _ in enumerate(pool.map(lambda path: apply_one(path, overlay), paths), 1):
        if index % 25 == 0 or index == len(paths):
            print(f"branded {index}/{len(paths)}", flush=True)


if __name__ == "__main__":
    main()
