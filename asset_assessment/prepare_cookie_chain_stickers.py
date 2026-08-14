#!/usr/bin/env python3
"""Prepare the supplied Morsel and Cookiebox assets as Cookie Edition stickers."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "assets" / "catalog_uploads"
OUTPUT = ROOT / "assets" / "stickerz"
CANVAS = 1393
STICKER_CENTER_X = 190
STICKER_BOTTOM_Y = 1308
STICKER_MAX_FOOTPRINT = 200
SOURCES = (("Morsel.png", "Morsel.png"), ("Cookiebox.png", "Cookiebox.png"))


def prepare_sticker(source: Path) -> Image.Image:
    image = Image.open(source).convert("RGBA")
    bbox = image.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError(f"{source.name}: no visible artwork")
    art = image.crop(bbox)
    scale = min(STICKER_MAX_FOOTPRINT / art.width, STICKER_MAX_FOOTPRINT / art.height)
    art = art.resize(
        (max(1, round(art.width * scale)), max(1, round(art.height * scale))),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    canvas.alpha_composite(
        art,
        (round(STICKER_CENTER_X - art.width / 2), STICKER_BOTTOM_Y - art.height),
    )
    return canvas


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for source_name, output_name in SOURCES:
        source = CATALOG / source_name
        if not source.exists():
            raise SystemExit(f"missing supplied sticker source: {source_name}")
        sticker = prepare_sticker(source)
        target = OUTPUT / output_name
        sticker.save(target, optimize=True)
        print(f"{target.relative_to(ROOT)} bbox={sticker.getchannel('A').getbbox()}")


if __name__ == "__main__":
    main()
