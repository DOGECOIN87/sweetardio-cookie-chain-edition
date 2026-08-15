#!/usr/bin/env python3
"""Stage the supplied Cookie Chain review assets and render non-release arm tests.

This intentionally does not touch ``assets/backgroundz`` or ``assets/armz``.
It preserves the pending review state until the owner explicitly authorizes the
final collection regeneration.
"""

import json
import random
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import generator as g  # noqa: E402

UPLOADS = Path("/home/ubuntu/upload")
STAGE_ROOT = Path("/home/ubuntu/cookie-chain-pending-final-review")
BACKGROUND_DIR = STAGE_ROOT / "backgroundz"
ARM_DIR = STAGE_ROOT / "armz"
PREVIEW_DIR = STAGE_ROOT / "printr_arms_positioning_preview"

ASSETS = {
    "Emyr_Gallery.png": UPLOADS / "art_matt(13).png",
    "Cookie_Dough.png": UPLOADS / "art_mattrick_001(27).png",
    "PrintR.png": Path("/home/ubuntu/cookie-chain-pending-final-review/PrintR_smudges_removed.png"),
    "Legendary_Mattrick.png": UPLOADS / "Legendary_Just_Aliens(2).png",
    "Legendary_Shubbi.png": UPLOADS / "layer-Legendary_Shubbi.png",
    "Legendary_Tenders.png": UPLOADS / "composite-export(25).png",
}

TEST_BACKGROUND = "Cookie_Dough.png"
# The owner supplied a compact, pre-positioned 1393px PrintR canvas. Preserve
# it exactly for review rather than applying another runtime scale or offset.
PRINT_R_EXCLUDED_CHARACTER_PATTERNS = ("gummy_bear",)
# Owner-requested final review refinement: raise the complete compact PrintR
# canvas just enough to improve its relationship to the character, with no
# source crop, rescale, or component-level edit.
REVIEW_PRINTR_DY = -18


def font(size: int):
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def stage_sources() -> dict:
    BACKGROUND_DIR.mkdir(parents=True, exist_ok=True)
    ARM_DIR.mkdir(parents=True, exist_ok=True)
    for name, source in ASSETS.items():
        if not source.is_file():
            raise FileNotFoundError(f"Missing supplied source: {source}")
        destination = (ARM_DIR if name == "PrintR.png" else BACKGROUND_DIR) / name
        shutil.copy2(source, destination)

    inventory = {}
    for name, source in ASSETS.items():
        image = Image.open(source).convert("RGBA")
        alpha = image.getchannel("A")
        inventory[name] = {
            "source": str(source),
            "staged": str((ARM_DIR if name == "PrintR.png" else BACKGROUND_DIR) / name),
            "dimensions": list(image.size),
            "alpha_range": list(alpha.getextrema()),
            "opaque_bounds": list(alpha.getbbox()) if alpha.getbbox() else None,
        }
    return inventory


def inspect_native_printr() -> dict:
    """Validate the owner-supplied compact PrintR canvas without transforming it."""
    image = Image.open(ARM_DIR / "PrintR.png").convert("RGBA")
    alpha = image.getchannel("A")
    bounds = alpha.getbbox()
    if not bounds:
        raise ValueError("PrintR source contains no visible pixels")
    if alpha.getextrema()[0] > 0:
        raise ValueError("PrintR edit has an opaque baked background instead of true transparency")
    source_size = image.size
    if source_size != (g.CANVAS_SIZE, g.CANVAS_SIZE):
        # The image edit model returned a 1920px square canvas. Resize the
        # complete canvas only—never crop or shift it—so the approved compact
        # composition keeps its exact relative placement in the collection.
        image = image.resize((g.CANVAS_SIZE, g.CANVAS_SIZE), Image.Resampling.LANCZOS)
        image.save(ARM_DIR / "PrintR.png")
        bounds = image.getchannel("A").getbbox()
    return {
        "native_opaque_bounds": list(bounds),
        "source_canvas": list(source_size),
        "native_canvas": list(image.size),
        "excluded_character_patterns": list(PRINT_R_EXCLUDED_CHARACTER_PATTERNS),
    }


def make_position_tests() -> list[dict]:
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    g.BACKGROUNDZ = str(BACKGROUND_DIR)
    g.ARMZ = str(ARM_DIR)
    # Render every available character except gummy-bear variants, as requested.
    review_characters = sorted({g.char_base_name(name)
                                for name in g.get_files(g.CHARACTERZ)})
    review_characters = [character for character in review_characters
                         if not any(pattern in character.lower()
                                    for pattern in PRINT_R_EXCLUDED_CHARACTER_PATTERNS)]
    results = []
    for index, character in enumerate(review_characters, 1):
        random.seed(871003 + index)
        layers, resolved_character = g.generate_random_combination(
            force_bg=(str(BACKGROUND_DIR), TEST_BACKGROUND),
            force_arm="PrintR.png",
            force_wat=None,
            force_sticker=None,
            force_char=character,
        )
        for layer in layers:
            if Path(layer["path"]).name == "PrintR.png":
                layer["dy"] = layer.get("dy", 0) + REVIEW_PRINTR_DY
        destination = PREVIEW_DIR / f"{index:02d}_{character}.png"
        g.create_image(layers, str(destination))
        results.append({
            "character": resolved_character,
            "image": str(destination),
            "attributes": g.extract_metadata(layers, resolved_character),
        })
    return results


def make_contact_sheet(tests: list[dict]) -> Path:
    cell, title_h, gutter, cols = 250, 30, 10, 5
    rows = (len(tests) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell + (cols + 1) * gutter,
                               rows * (cell + title_h) + (rows + 1) * gutter),
                      (7, 15, 52))
    draw = ImageDraw.Draw(sheet)
    label_font = font(15)
    for index, test in enumerate(tests):
        tile = Image.open(test["image"]).convert("RGB").resize((cell, cell), Image.Resampling.LANCZOS)
        x = gutter + (index % cols) * (cell + gutter)
        y = gutter + (index // cols) * (cell + title_h + gutter)
        sheet.paste(tile, (x, y))
        label = f"{test['character'].replace('_', ' ').title()} + PrintR"
        draw.text((x, y + cell + 9), label, fill=(255, 255, 255), font=label_font)
    destination = STAGE_ROOT / "printr_arms_positioning_review.png"
    sheet.save(destination, optimize=True)
    return destination


def main() -> None:
    inventory = stage_sources()
    printr_geometry = inspect_native_printr()
    tests = make_position_tests()
    sheet = make_contact_sheet(tests)
    manifest = {
        "status": "pending_owner_approval_no_release_assets_modified",
        "background_replacement": {
            "asset": "Emyr_Gallery.png",
            "display_name": "Emyr Legendary",
        },
        "background_addition": {
            "asset": "Cookie_Dough.png",
            "display_name": "Cookie Dough",
        },
        "legendary_background_additions": [
            {"asset": "Legendary_Mattrick.png", "display_name": "Mattrick Legendary"},
            {"asset": "Legendary_Shubbi.png", "display_name": "Shubbi Legendary"},
            {"asset": "Legendary_Tenders.png", "display_name": "Tenders Legendary"},
        ],
        "arms_addition": {
            "asset": "PrintR.png",
            "display_name": "PrintR",
            "review_treatment": "exact owner-supplied compact pre-positioned canvas",
            "review_vertical_offset_px": REVIEW_PRINTR_DY,
            "geometry": printr_geometry,
        },
        "inventory": inventory,
        "placement_tests": tests,
        "contact_sheet": str(sheet),
    }
    path = STAGE_ROOT / "pending_trait_manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(path), "contact_sheet": str(sheet)}, indent=2))


if __name__ == "__main__":
    main()
