#!/usr/bin/env python3
"""Render original-style Cookie Chain Edition sticker overlays for review."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stickers", required=True, help="Prepared sticker directory")
    parser.add_argument("--out", required=True, help="PNG contact-sheet output")
    return parser.parse_args()


def font(size):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    args = parse_args()
    sticker_dir = Path(args.stickers).expanduser().resolve()
    files = sorted(sticker_dir.glob("*.png"))
    cols, cell, label = 4, 280, 54
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell, rows * (cell + label)), (7, 15, 52))
    draw = ImageDraw.Draw(sheet)
    label_face = font(15)
    for index, path in enumerate(files):
        x = (index % cols) * cell
        y = (index // cols) * (cell + label)
        sticker = Image.open(path).convert("RGBA")
        bbox = sticker.getchannel("A").getbbox()
        if bbox is None:
            raise SystemExit(f"{path.name}: empty overlay")
        silhouette = sticker.crop(bbox)
        silhouette.thumbnail((220, 205), Image.Resampling.LANCZOS)
        preview = Image.new("RGBA", (cell, cell), (22, 35, 68, 255))
        preview.alpha_composite(silhouette, ((cell - silhouette.width) // 2, (cell - silhouette.height) // 2))
        sheet.paste(preview.convert("RGB"), (x, y))
        draw.text((x + 10, y + cell + 10), path.stem.replace("_", " "), font=label_face, fill=(238, 240, 248))
    Path(args.out).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out, optimize=True)
    print(f"rendered {len(files)} original-style sticker overlays -> {args.out}")


if __name__ == "__main__":
    main()
