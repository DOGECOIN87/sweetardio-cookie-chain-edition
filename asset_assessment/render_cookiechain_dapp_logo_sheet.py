#!/usr/bin/env python3
"""Render a labeled contact sheet for official Cookie Chain dapp logo sources."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", required=True, help="Downloaded source-logo directory")
    parser.add_argument("--out", required=True, help="PNG contact-sheet output")
    return parser.parse_args()


def font(size):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def checkerboard(size, step=18):
    image = Image.new("RGB", size, (25, 30, 49))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], step):
        for x in range(0, size[0], step):
            if (x // step + y // step) % 2:
                draw.rectangle((x, y, x + step - 1, y + step - 1), fill=(39, 47, 71))
    return image


def main():
    args = parse_args()
    source_dir = Path(args.sources).expanduser().resolve()
    receipts = json.loads((source_dir / "SOURCES.json").read_text(encoding="utf-8"))
    cols, cell, label = 4, 280, 58
    rows = (len(receipts) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell, rows * (cell + label)), (7, 15, 52))
    draw = ImageDraw.Draw(sheet)
    title_font = font(17)
    sub_font = font(12)
    for index, receipt in enumerate(receipts):
        x = (index % cols) * cell
        y = (index // cols) * (cell + label)
        plate = checkerboard((cell, cell)).convert("RGBA")
        source = Image.open(source_dir / receipt["file"]).convert("RGBA")
        source.thumbnail((cell - 44, cell - 44), Image.Resampling.LANCZOS)
        plate.alpha_composite(source, ((cell - source.width) // 2, (cell - source.height) // 2))
        sheet.paste(plate.convert("RGB"), (x, y))
        draw.text((x + 12, y + cell + 9), receipt["title"], font=title_font, fill=(238, 240, 248))
        draw.text((x + 12, y + cell + 33), f"{receipt['width']}×{receipt['height']} · {receipt['mode']}", font=sub_font, fill=(151, 166, 202))
    Path(args.out).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out, optimize=True)
    print(f"rendered {len(receipts)} source logos -> {args.out}")


if __name__ == "__main__":
    main()
