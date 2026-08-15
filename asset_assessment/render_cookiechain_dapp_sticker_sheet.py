#!/usr/bin/env python3
"""Render a labeled contact sheet of normalized Cookie Chain dapp sticker overlays."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stickers", required=True, help="Sticker output directory")
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
    manifest = json.loads((sticker_dir / "COOKIECHAIN_DAPP_LOGO_SOURCES.json").read_text(encoding="utf-8"))
    cols, cell, label = 4, 300, 54
    rows = (len(manifest) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell, rows * (cell + label)), (7, 15, 52))
    draw = ImageDraw.Draw(sheet)
    title = font(16)
    info = font(11)
    for index, item in enumerate(manifest):
        x = (index % cols) * cell
        y = (index // cols) * (cell + label)
        preview = Image.new("RGBA", (300, 300), (23, 37, 70, 255))
        sticker = Image.open(sticker_dir / item["output"]).convert("RGBA")
        # Crop the only region where the normalized overlay can contain artwork.
        crop = sticker.crop((0, 1000, 400, 1393))
        preview.alpha_composite(crop, (0, 0))
        sheet.paste(preview.convert("RGB"), (x, y))
        draw.text((x + 10, y + cell + 8), item["title"], font=title, fill=(238, 240, 248))
        size = item["art_size"]
        draw.text((x + 10, y + cell + 30), f"{size['width']}×{size['height']}px artwork", font=info, fill=(151, 166, 202))
    Path(args.out).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out, optimize=True)
    print(f"rendered {len(manifest)} normalized sticker previews -> {args.out}")


if __name__ == "__main__":
    main()
