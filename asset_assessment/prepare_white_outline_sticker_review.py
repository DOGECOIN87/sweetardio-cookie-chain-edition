#!/usr/bin/env python3
"""Create review-only white-outline copies of native Cookie Chain sticker overlays.

This script never writes to assets/stickerz. It preserves each overlay's 1393px
canvas, current placement, and source pixels, adding only a 6px white alpha
expansion beneath the native silhouette for approval review.
"""

import argparse
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


OUTLINE_RADIUS = 6
OUTLINE_FILTER_SIZE = OUTLINE_RADIUS * 2 + 1
COLS = 4
CELL = 280
LABEL = 64


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stickers", required=True, help="Current active native-overlay directory")
    parser.add_argument("--out-dir", required=True, help="Review-only outlined overlay directory")
    parser.add_argument("--sheet", required=True, help="Labeled review-sheet PNG output")
    return parser.parse_args()


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def outlined_copy(source: Image.Image) -> Image.Image:
    """Add a white native-silhouette outline while preserving all source art."""
    source = source.convert("RGBA")
    alpha = source.getchannel("A")
    expanded = alpha.filter(ImageFilter.MaxFilter(OUTLINE_FILTER_SIZE))
    outline = Image.new("RGBA", source.size, (255, 255, 255, 0))
    outline.putalpha(expanded)
    outline.alpha_composite(source)
    return outline


def main() -> None:
    args = parse_args()
    sticker_dir = Path(args.stickers).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    sheet_path = Path(args.sheet).expanduser().resolve()
    files = sorted(sticker_dir.glob("*.png"))
    if not files:
        raise SystemExit(f"no sticker PNG files found in {sticker_dir}")

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    rendered: list[tuple[str, Image.Image]] = []
    for source_path in files:
        prepared = outlined_copy(Image.open(source_path))
        prepared.save(out_dir / source_path.name, optimize=True)
        rendered.append((source_path.stem.replace("_", " "), prepared))

    rows = (len(rendered) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * CELL, rows * (CELL + LABEL) + 74), (7, 15, 52))
    draw = ImageDraw.Draw(sheet)
    draw.text((18, 14), "PROPOSED ORIGINAL-STYLE WHITE OUTLINE", font=font(26), fill=(255, 255, 255))
    draw.text((18, 47), "26 active native silhouettes • 6px white contour • review only • no collection assets changed", font=font(13), fill=(52, 237, 243))
    label_face = font(15)
    for index, (name, sticker) in enumerate(rendered):
        x = (index % COLS) * CELL
        y = 74 + (index // COLS) * (CELL + LABEL)
        bbox = sticker.getchannel("A").getbbox()
        if bbox is None:
            raise SystemExit(f"{name}: empty overlay")
        silhouette = sticker.crop(bbox)
        silhouette.thumbnail((220, 205), Image.Resampling.LANCZOS)
        preview = Image.new("RGBA", (CELL, CELL), (22, 35, 68, 255))
        preview.alpha_composite(silhouette, ((CELL - silhouette.width) // 2, (CELL - silhouette.height) // 2))
        sheet.paste(preview.convert("RGB"), (x, y))
        draw.text((x + 10, y + CELL + 10), name, font=label_face, fill=(238, 240, 248))

    sheet_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(sheet_path, optimize=True)
    print(f"review-only outlined overlays: {len(rendered)} -> {out_dir}")
    print(f"review sheet -> {sheet_path}")


if __name__ == "__main__":
    main()
