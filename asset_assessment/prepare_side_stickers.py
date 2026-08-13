#!/usr/bin/env python3
"""Prepare only the newly supplied stickers for the 100-piece side collection.

The production compositor requires every overlay to be a 1393x1393 RGBA PNG.
This script leaves the uploaded source files untouched, removes border-connected
black mattes from the flattened uploads, fits their artwork to the established
corner-sticker footprint, and writes a clean, uniquely named pool.
"""

from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "traits" / "stickerz"
OUTPUT = ROOT / "side_collection" / "assets" / "stickerz"
CANVAS = 1393
ANCHOR_CENTER_X = 190
ANCHOR_BOTTOM = 1308
MAX_FOOTPRINT = 200

# The first five are already transparent corner overlays. The remaining four
# are flattened sticker art. 30_poptart_cat.png is used for Nyan Cat;
# photo_2026-05-09_10-53-17.jpg is the same artwork and is intentionally omitted.
# Target names carry NO ordering prefix. The compositor has no TRAIT_NAMES
# entry for the side collection's stickers, so each one's metadata value is
# derived from its filename -- and a leading "01_" came out in the token as
# "01 Crying Tomato". Here the filename IS the display name, so it has to read
# as one.
SOURCES = (
    ("08_Crying_Tomato.png", "Crying_Tomato.png", "canvas"),
    ("09_Chibi_Monster.png", "Chibi_Monster.png", "canvas"),
    ("14_Shorts_doggo.png", "Shorts_Doggo.png", "canvas"),
    ("19_Emyr.png", "Emyr.png", "canvas"),
    ("27_sweetardio.png", "Sweetardio.png", "canvas"),
    ("30_poptart_cat.png", "Poptart_Cat.png", "matte"),
    ("photo_2026-05-09_10-53-28.jpg", "Armed_Hero.png", "matte"),
    ("photo_2026-05-09_11-07-01.jpg", "Anime_Detective.png", "matte"),
    ("photo_2026-05-09_11-07-20.jpg", "Out_Of_Order.png", "matte"),
)


def remove_border_black(image: Image.Image, tolerance: int = 42) -> Image.Image:
    """Make only near-black pixels connected to the image border transparent."""
    rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
    candidate = rgb.max(axis=2) <= tolerance
    h, w = candidate.shape
    seeds = np.zeros_like(candidate)
    seeds[0, :] = seeds[-1, :] = True
    seeds[:, 0] = seeds[:, -1] = True
    outside = ndimage.binary_propagation(seeds & candidate, mask=candidate)

    rgba = np.empty((h, w, 4), dtype=np.uint8)
    rgba[:, :, :3] = rgb
    rgba[:, :, 3] = np.where(outside, 0, 255).astype(np.uint8)
    # Fully clear pixels should carry no hidden black RGB, preventing resize halos.
    rgba[outside, :3] = 0
    return Image.fromarray(rgba, "RGBA")


def place_corner_sticker(image: Image.Image) -> Image.Image:
    bbox = image.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("sticker became empty after matte removal")
    art = image.crop(bbox)
    scale = min(MAX_FOOTPRINT / art.width, MAX_FOOTPRINT / art.height)
    size = (max(1, round(art.width * scale)), max(1, round(art.height * scale)))
    art = art.resize(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    x = round(ANCHOR_CENTER_X - art.width / 2)
    y = ANCHOR_BOTTOM - art.height
    canvas.alpha_composite(art, (x, y))
    return canvas


def prepare(source: Path, mode: str) -> Image.Image:
    image = Image.open(source).convert("RGBA")
    if mode == "canvas":
        if image.getchannel("A").getbbox() is None:
            raise ValueError(f"{source.name}: no visible artwork")
        return image.resize((CANVAS, CANVAS), Image.Resampling.LANCZOS)
    return place_corner_sticker(remove_border_black(image))


def main() -> None:
    missing = [name for name, _, _ in SOURCES if not (SOURCE / name).exists()]
    if missing:
        raise SystemExit("missing new sticker upload(s): " + ", ".join(missing))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    expected = {target for _, target, _ in SOURCES}
    for stale in OUTPUT.glob("*.png"):
        if stale.name not in expected:
            stale.unlink()

    for source_name, target_name, mode in SOURCES:
        result = prepare(SOURCE / source_name, mode)
        target = OUTPUT / target_name
        result.save(target, optimize=True)
        bbox = result.getchannel("A").point(lambda a: 255 if a >= 128 else 0).getbbox()
        print(f"{target.relative_to(ROOT)}  {result.mode} {result.size[0]}x{result.size[1]}  bbox={bbox}")


if __name__ == "__main__":
    main()
