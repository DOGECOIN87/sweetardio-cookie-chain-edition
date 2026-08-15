#!/usr/bin/env python3
"""Build a labelled, non-destructive Cookie Chain background review sheet."""

from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ACTIVE = ROOT / "assets" / "backgroundz"
STAGED = Path("/home/ubuntu/cookie-chain-pending-final-review/backgroundz")
OUT = Path("/home/ubuntu/cookie-chain-pending-final-review/current_background_curation_review.png")

# The sequence represents the proposed post-approval collection pool. Labels
# use the requested metadata names; source filenames remain visible only in the
# code so compositor references remain stable until approval.
CURATED = [
    (ACTIVE, "Black_Cookie_Emboss.png", "Cookboy Black Enamel"),
    (ACTIVE, "Chocolate_Cookie_Emboss.png", "Cookboy Chocolate"),
    (ACTIVE, "Gold_Cookie_Emboss.png", "Cookboy Gold"),
    (ACTIVE, "Cookboy_Paisley.png", "Sarv Legendary"),
    (ACTIVE, "Cookie_Vault.png", "M Power Legendary"),
    (STAGED, "Cookie_Dough.png", "Cookie Dough — New"),
    (ACTIVE, "Digital_Future_Mural.png", "NFTs Aren’t Dead"),
    (STAGED, "Emyr_Gallery.png", "Emyr Legendary — Replacement"),
    (ACTIVE, "Fairdevs_Night.png", "Fairdevs Legendary"),
    (ACTIVE, "Gorbhouse_Treasures.png", "Gorbhouse Treasures"),
    (STAGED, "Legendary_Mattrick.png", "Mattrick Legendary — New"),
    (ACTIVE, "Legendary_Nightly.png", "Nightly Legendary — Reserved 1/1"),
    (STAGED, "Legendary_Shubbi.png", "Shubbi Legendary — New"),
    (STAGED, "Legendary_Tenders.png", "Tenders Legendary — New"),
    (ACTIVE, "Liberty_Cookie_Dime.png", "Liberty Cookie Dime"),
    (ACTIVE, "Marsel_Blue.png", "Morsel Legendary"),
    (ACTIVE, "Moon_Surface.png", "Moon Surface"),
    (ACTIVE, "Picnic_Stage.png", "Picnic Stage"),
    (ACTIVE, "Short_The_Banks_Vault.png", "Short The Banks Legendary"),
    (ACTIVE, "Silver_Cookie_Emboss.png", "Cookboy Silver"),
    (ACTIVE, "Simplex_Arcade.png", "Cookboy Legendary"),
    (ACTIVE, "Welders_Equipment.png", "GorWeld Legendary"),
    (ACTIVE, "Yatrah_Arcade.png", "Yatrah Arcade"),
]

REMOVED = [
    (ACTIVE, "Cosmic_Fog.png", "Cosmic Fog — Remove"),
    (ACTIVE, "Oxford_Blue_Fur.png", "Oxford Blue Fur — Remove"),
    (ACTIVE, "Golden_Bubbles.png", "Golden Bubbles — Remove"),
    (ACTIVE, "Midnight_Bakery.png", "Midnight Bakery — Remove"),
]


def font(size: int):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def place_tile(sheet, draw, item, index, cols, start_y, title_font, label_font, accent):
    source_dir, filename, label = item
    cell, label_h, gutter = 250, 48, 12
    x = gutter + (index % cols) * (cell + gutter)
    y = start_y + (index // cols) * (cell + label_h + gutter)
    path = source_dir / filename
    if not path.is_file():
        raise FileNotFoundError(path)
    tile = Image.open(path).convert("RGB").resize((cell, cell), Image.Resampling.LANCZOS)
    sheet.paste(tile, (x, y))
    draw.rectangle((x, y + cell, x + cell, y + cell + label_h), fill=(6, 15, 52))
    draw.rectangle((x, y + cell, x + cell, y + cell + 4), fill=accent)
    # Center within the fixed label band, truncating only at a natural length.
    shown = label if len(label) <= 30 else label[:27].rstrip() + "…"
    bbox = draw.textbbox((0, 0), shown, font=label_font)
    draw.text((x + (cell - (bbox[2] - bbox[0])) / 2, y + cell + 14), shown,
              font=label_font, fill=(255, 255, 255))


def main() -> None:
    cols, cell, label_h, gutter = 4, 250, 48, 12
    title_h, section_h = 116, 44
    curated_rows = math.ceil(len(CURATED) / cols)
    removed_rows = math.ceil(len(REMOVED) / cols)
    curated_h = curated_rows * (cell + label_h + gutter)
    removed_h = removed_rows * (cell + label_h + gutter)
    height = title_h + section_h + curated_h + section_h + removed_h + gutter
    width = cols * cell + (cols + 1) * gutter
    sheet = Image.new("RGB", (width, height), (6, 15, 52))
    draw = ImageDraw.Draw(sheet)
    title_font, body_font, label_font = font(34), font(16), font(15)
    draw.text((gutter, 22), "COOKIE CHAIN EDITION — CURRENT BACKGROUND REVIEW",
              font=title_font, fill=(247, 21, 171))
    draw.text((gutter, 70), "Proposed collection pool: requested renames and pending new artwork are reflected below.",
              font=body_font, fill=(52, 237, 243))
    draw.text((gutter, title_h), "CURATED POOL — PENDING FINAL APPROVAL",
              font=body_font, fill=(52, 237, 243))
    curated_y = title_h + section_h
    for index, item in enumerate(CURATED):
        place_tile(sheet, draw, item, index, cols, curated_y, title_font, label_font, (52, 237, 243))
    removed_y = curated_y + curated_h + 6
    draw.text((gutter, removed_y), "EXCLUDED FROM POOL — ARTWORK RETAINED UNTIL APPROVAL",
              font=body_font, fill=(247, 21, 171))
    removed_tiles_y = removed_y + section_h
    for index, item in enumerate(REMOVED):
        place_tile(sheet, draw, item, index, cols, removed_tiles_y, title_font, label_font, (247, 21, 171))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT, optimize=True)
    print(OUT)


if __name__ == "__main__":
    main()
