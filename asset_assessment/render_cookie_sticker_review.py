#!/usr/bin/env python3
"""Render a two-token Cookie Edition review for the Morsel and Cookiebox stickers."""

import random
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import generator as g  # noqa: E402
from asset_assessment.apply_side_branding import prepare_overlay  # noqa: E402


STICKERS = ("Morsel.png", "Cookiebox.png")
OUT = ROOT / "catalog" / "cookie_sticker_trait_review.png"
TILES = ROOT / "catalog" / ".cookie_sticker_trait_tiles"
CANVAS = 1393
CELL = 520
LABEL_H = 52


def display(filename: str) -> str:
    return Path(filename).stem.replace("_", " ")


def main() -> None:
    g.BACKGROUNDZ = str((ROOT / "assets" / "backgroundz").resolve())
    g.ARMZ = str((ROOT / "assets" / "armz").resolve())
    g.STICKERZ = str((ROOT / "assets" / "stickerz").resolve())
    if TILES.exists():
        shutil.rmtree(TILES)
    TILES.mkdir(parents=True)

    random.seed(871003)
    overlay = prepare_overlay()
    entries = []
    for index, sticker in enumerate(STICKERS, 1):
        layers, character = g.generate_random_combination(force_sticker=sticker)
        path = TILES / f"{index:02d}.png"
        g.create_image(layers, str(path))
        token = Image.open(path).convert("RGBA")
        token.alpha_composite(overlay)
        token.save(path, compress_level=1)
        arm = next((Path(layer["path"]).stem.replace("_", " ") for layer in layers
                    if Path(layer["path"]).parent == g.ARMZ), "No arm")
        entries.append((path, g.trait_name(g.CHARACTERZ, character), display(sticker), arm))

    sheet = Image.new("RGB", (2 * CELL, 46 + CELL + LABEL_H), (16, 16, 20))
    draw = ImageDraw.Draw(sheet)
    headline = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    draw.text((12, 13), "Cookie Chain Edition — Sticker Trait Review", font=headline, fill=(246, 206, 86))
    for index, (path, character, sticker, arm) in enumerate(entries):
        image = Image.open(path).convert("RGB").resize((CELL, CELL), Image.Resampling.LANCZOS)
        x = index * CELL
        sheet.paste(image, (x, 46))
        draw.text((x + 10, 46 + CELL + 9), f"Sticker: {sticker}", font=label, fill=(240, 240, 245))
        draw.text((x + 10, 46 + CELL + 28), f"{character} · {arm}", font=label, fill=(160, 160, 174))
    sheet.save(OUT, optimize=True)
    print(f"{len(entries)} corrected sticker reviews -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
