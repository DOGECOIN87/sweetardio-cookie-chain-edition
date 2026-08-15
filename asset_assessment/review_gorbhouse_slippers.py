#!/usr/bin/env python3
"""Render every Gorbhouse Slippers-eligible character for owner placement review."""

import argparse
import random
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import generator as g  # noqa: E402

# Final collection renders use the legacy character/footwear source folders but
# the actively curated background pool. Keep the former relative to `traits`
# and point only the background category at the approved active assets.
g.BACKGROUNDZ = str(ROOT / "assets" / "backgroundz")


REVIEW_BACKGROUND = "Black_Cookie_Emboss.png"
CELL = 430
PAD = 26
HEADER = 98


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def display_name(value):
    return value.replace("_", " ").replace("-", " ").title()


def main():
    args = parse_args()
    out = Path(args.out).expanduser().resolve()
    render_dir = out / "gorbhouse_samples"
    if render_dir.exists():
        shutil.rmtree(render_dir)
    render_dir.mkdir(parents=True)

    characters = sorted({g.char_base_name(item) for item in g.get_files(g.CHARACTERZ)})
    eligible = [item for item in characters if g.gets_gorbhouse_overlay(item)]
    if not eligible:
        raise SystemExit("no Gorbhouse Slippers-eligible characters were found")
    rows, columns = (len(eligible) + 3) // 4, 4
    sheet = Image.new("RGBA", (columns * (CELL + PAD) + PAD, HEADER + rows * (CELL + 58)), "#070f34")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    draw.text((PAD, 24), "COOKIE CHAIN EDITION — GORBHOUSE SLIPPERS REVIEW", fill="#f715ab", font=font)
    draw.text((PAD, 50), f"{len(eligible)} eligible characters · normalized comparison background", fill="#34edf3", font=font)

    for index, character in enumerate(eligible):
        random.seed(871003 + index)
        layers, resolved = g.generate_random_combination(
            force_bg=(g.BACKGROUNDZ, REVIEW_BACKGROUND),
            force_char=character,
            force_wat="gorbhouse",
            force_arm=None,
            force_sticker=None,
        )
        if resolved != character or not any("gorbhouse" in layer["path"].lower() for layer in layers):
            raise SystemExit(f"failed to render Gorbhouse Slippers for {character}")
        sample = render_dir / f"{index + 1:02d}_{character}.png"
        g.create_image(layers, str(sample))
        image = Image.open(sample).convert("RGBA").resize((CELL, CELL), Image.Resampling.LANCZOS)
        col, row = index % columns, index // columns
        x, y = PAD + col * (CELL + PAD), HEADER + row * (CELL + 58)
        sheet.alpha_composite(image, (x, y))
        draw.text((x, y + CELL + 11), display_name(character), fill="#f6f7ff", font=font)
        draw.text((x, y + CELL + 29), "Gorbhouse Slippers", fill="#34edf3", font=font)

    target = out / "gorbhouse_slippers_all_eligible_review.png"
    sheet.convert("RGB").save(target, quality=95)
    print(f"rendered {len(eligible)} eligible Gorbhouse Slippers pairings -> {target}")


if __name__ == "__main__":
    main()
