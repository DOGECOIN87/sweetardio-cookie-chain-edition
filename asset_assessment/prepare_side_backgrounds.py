#!/usr/bin/env python3
"""Build the side collection's background pool from its isolated uploads.

This deliberately never reads traits/backgroundz. The upload archive contains
background plates as well as character pieces, overlays, a badge, and a review
sheet; BACKGROUNDS is the reviewed allowlist of images suitable as plates.
"""

from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "side_collection" / "assets" / "catalog_uploads"
OUTPUT = ROOT / "side_collection" / "assets" / "backgroundz"
CANVAS = 1393

# (uploaded source, clean production filename). Background-sheet positions
# 7, 17, 18 and 20 were rejected during art review and are deliberately absent.
BACKGROUNDS = (
    ("Legendary_Emyr (1).png", "Emyr_Gallery.png"),
    ("Legendary_Short_the_Banks (1).png", "Short_The_Banks_Gallery.png"),
    ("art_1 (16).png", "Chocolate_Cookie_Emboss.png"),
    ("art_1 (17).png", "Silver_Cookie_Emboss.png"),
    ("art_1 (18).png", "Gold_Cookie_Emboss.png"),
    ("art_1 (19).png", "Black_Cookie_Emboss.png"),
    ("art_mattrick_001-15-2.png", "Liberty_Cookie_Dime.png"),
    ("composite-export (20).png", "Yatrah_Arcade.png"),
    ("composite-export (24).png", "Welders_Equipment.png"),
    ("composite-export (27).png", "Short_The_Banks_Vault.png"),
    ("composite-export (29).png", "Marsel_Blue.png"),
    ("composite-export (31).png", "Gorbhouse_Treasures.png"),
    ("composite-export (32).png", "Fairdevs_Night.png"),
    ("composite-export (34).png", "Cookie_Vault.png"),
    ("file_000000003af871f8ad68fec5b355e42f.png", "Midnight_Bakery.png"),
    ("file_00000000640072309b0e0e191c3876b6.png", "Cosmic_Fog.png"),
    ("file_0000000077e871f8bad4686ac47fd73a.png", "Oxford_Blue_Fur.png"),
    ("file_00000000930c71f8a7c422cb37b6d90a.png", "Simplex_Arcade.png"),
    ("file_00000000c60071fdad4510cd962e8ec5.png", "Golden_Bubbles.png"),
    ("file_00000000d54c71f789a2ed3994519536.png", "Moon_Surface.png"),
    ("file_00000000f7f872308e55adf7dd7e96b1.png", "Picnic_Stage.png"),
    ("file_00000000fe8c71fd8c043c56e24782f0.png", "Digital_Future_Mural.png"),
    ("grok_image_1779942071264.jpg", "Cookboy_Paisley.png"),
)


def main() -> None:
    missing = [source for source, _ in BACKGROUNDS if not (SOURCE / source).exists()]
    if missing:
        raise SystemExit("missing isolated upload(s): " + ", ".join(missing))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    expected = {target for _, target in BACKGROUNDS}
    for stale in OUTPUT.glob("*.png"):
        if stale.name not in expected:
            stale.unlink()

    for source_name, target_name in BACKGROUNDS:
        source = SOURCE / source_name
        # Crop-to-fill avoids stretching portrait/landscape sources and makes
        # every plate canvas-native before the compositor sees it.
        image = Image.open(source).convert("RGB")
        image = ImageOps.fit(image, (CANVAS, CANVAS), Image.Resampling.LANCZOS,
                             centering=(0.5, 0.5))
        target = OUTPUT / target_name
        # Default PNG compression is intentionally used here. Pillow's global
        # optimizer is disproportionately slow for this large image pack.
        image.save(target)
        print(f"{target.relative_to(ROOT)}  RGB {CANVAS}x{CANVAS}")


if __name__ == "__main__":
    main()
