#!/usr/bin/env python3
"""Prepare the Cookboy handheld game device as a side-only held-item trait."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (ROOT / "side_collection" / "assets" / "catalog_uploads" /
          "file_000000001e788230bece34d37c0840ab.png")
OUTPUT = ROOT / "side_collection" / "assets" / "armz" / "Cookboy_Handheld.png"
CANVAS = 1393
TARGET_HEIGHT = 650
CENTER_X = 695
BOTTOM_Y = 1275


def main():
    image = Image.open(SOURCE).convert("RGB")
    # The backdrop is a black-to-gray studio gradient and the device itself is
    # black, so colour-keying destroys the casing. Use a soft silhouette mask
    # around the known product and hand geometry instead.
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((140, 145, 872, 1325), radius=42, fill=255)
    draw.ellipse((8, 520, 178, 790), fill=255)       # left hand
    draw.ellipse((810, 405, 1008, 1015), fill=255)  # right fingers
    mask = mask.filter(ImageFilter.GaussianBlur(2.0))
    cut = image.convert("RGBA")
    cut.putalpha(mask)
    bbox = cut.getchannel("A").getbbox()
    if bbox is None:
        raise SystemExit("game device extraction produced no artwork")
    cut = cut.crop(bbox)
    width = round(cut.width * TARGET_HEIGHT / cut.height)
    cut = cut.resize((width, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    canvas.alpha_composite(cut, (round(CENTER_X - width / 2), BOTTOM_Y - TARGET_HEIGHT))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT)
    print(f"{OUTPUT.relative_to(ROOT)}  bbox={canvas.getchannel('A').getbbox()}")


if __name__ == "__main__":
    main()
