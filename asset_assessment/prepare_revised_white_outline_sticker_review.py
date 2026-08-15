#!/usr/bin/env python3
"""Render a review-only, curated white-outline sticker proposal.

This utility reads the active native overlays but never writes to assets/stickerz.
It creates copies for approval with the requested removals, label rename, selective
scale adjustments, and circular treatment of non-Nightly square logo sources.
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
REMOVE = frozenset({"GorWeld.png", "DefiLlama.png", "Crying_Tomato.png", "CookieScan_DAS_API.png"})
SCALE_OVERRIDES = {"CookBook.png": 1.18, "CookOven.png": 1.18}
CIRCULARIZE = frozenset({
    "Baked_Bazaar.png",
    "CookieScan.png",
    "CookieScan_DAS_API.png",
    "CookieSwap.png",
    "Cookie_Quads.png",
    "GORBOY.png",
})
RENAME = {
    "Anime_Detective.png": "L",
    "Armed_Hero.png": "Real as a Doughnut",
    "GORBOY.png": "Cookboy",
    "Poptart_Cat.png": "Nyancat",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stickers", required=True, help="Current active native-overlay directory")
    parser.add_argument("--out-dir", required=True, help="Review-only transformed overlay directory")
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


def visible_bounds(image: Image.Image) -> tuple[int, int, int, int]:
    bbox = image.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("sticker has no visible pixels")
    return bbox


def scale_overlay(image: Image.Image, factor: float) -> Image.Image:
    """Scale visible art from its anchored lower-left position without altering the canvas."""
    bbox = visible_bounds(image)
    art = image.crop(bbox)
    art = art.resize((round(art.width * factor), round(art.height * factor)), Image.Resampling.LANCZOS)
    result = Image.new("RGBA", image.size, (0, 0, 0, 0))
    result.alpha_composite(art, (round((bbox[0] + bbox[2] - art.width) / 2), bbox[3] - art.height))
    return result


def circularize_overlay(image: Image.Image) -> Image.Image:
    """Crop a square-logo source to a circular native logo treatment, preserving its center and location."""
    bbox = visible_bounds(image)
    art = image.crop(bbox)
    side = max(art.width, art.height)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.alpha_composite(art, ((side - art.width) // 2, (side - art.height) // 2))
    mask = Image.new("L", (side, side), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, side - 1, side - 1), fill=255)
    clipped = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    clipped.paste(square, (0, 0), Image.composite(mask, Image.new("L", (side, side), 0), square.getchannel("A")))
    result = Image.new("RGBA", image.size, (0, 0, 0, 0))
    result.alpha_composite(clipped, (round((bbox[0] + bbox[2] - side) / 2), bbox[3] - side))
    return result


def add_white_outline(image: Image.Image) -> Image.Image:
    alpha = image.getchannel("A")
    expanded = alpha.filter(ImageFilter.MaxFilter(OUTLINE_FILTER_SIZE))
    outline = Image.new("RGBA", image.size, (255, 255, 255, 0))
    outline.putalpha(expanded)
    outline.alpha_composite(image)
    return outline


def display_name(path: Path) -> str:
    if path.name in RENAME:
        return RENAME[path.name]
    return path.stem.replace("_", " ")


def main() -> None:
    args = parse_args()
    sticker_dir = Path(args.stickers).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    sheet_path = Path(args.sheet).expanduser().resolve()
    files = [path for path in sorted(sticker_dir.glob("*.png")) if path.name not in REMOVE]
    if len(files) != 22:
        raise SystemExit(f"expected 22 proposed active stickers after removals, got {len(files)}")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    rendered: list[tuple[str, Image.Image, str]] = []
    for source_path in files:
        image = Image.open(source_path).convert("RGBA")
        treatment = "native silhouette"
        if source_path.name in CIRCULARIZE:
            image = circularize_overlay(image)
            treatment = "round logo"
        if source_path.name in SCALE_OVERRIDES:
            image = scale_overlay(image, SCALE_OVERRIDES[source_path.name])
            treatment = f"{treatment} • +18%"
        image = add_white_outline(image)
        image.save(out_dir / source_path.name, optimize=True)
        rendered.append((display_name(source_path), image, treatment))

    rows = (len(rendered) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * CELL, rows * (CELL + LABEL) + 92), (7, 15, 52))
    draw = ImageDraw.Draw(sheet)
    draw.text((18, 14), "REVISED WHITE-OUTLINE STICKER PROPOSAL", font=font(25), fill=(255, 255, 255))
    draw.text((18, 46), "22 active after requested removals • white contour follows each silhouette • review only", font=font(13), fill=(52, 237, 243))
    draw.text((18, 66), "CookBook & CookOven +18% • non-Nightly square logos circularized • no collection assets changed", font=font(12), fill=(247, 21, 171))
    label_face = font(15)
    note_face = font(10)
    for index, (name, sticker, treatment) in enumerate(rendered):
        x = (index % COLS) * CELL
        y = 92 + (index // COLS) * (CELL + LABEL)
        bbox = visible_bounds(sticker)
        silhouette = sticker.crop(bbox)
        silhouette.thumbnail((220, 195), Image.Resampling.LANCZOS)
        preview = Image.new("RGBA", (CELL, CELL), (22, 35, 68, 255))
        preview.alpha_composite(silhouette, ((CELL - silhouette.width) // 2, (CELL - silhouette.height) // 2))
        sheet.paste(preview.convert("RGB"), (x, y))
        draw.text((x + 10, y + CELL + 7), name, font=label_face, fill=(238, 240, 248))
        draw.text((x + 10, y + CELL + 29), treatment, font=note_face, fill=(52, 237, 243))

    sheet_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(sheet_path, optimize=True)
    print(f"review-only revised overlays: {len(rendered)} -> {out_dir}")
    print(f"review sheet -> {sheet_path}")


if __name__ == "__main__":
    main()
