#!/usr/bin/env python3
"""Render N random side-collection tokens as one labelled contact sheet.

This is a LOOK at the pipeline, not a mint. Tokens are drawn straight from
generator.generate_random_combination() with nothing but a uniqueness check --
no scoring, no diversity caps, no rarity tiers -- so the spread here is the
raw draw rather than what build_side_collection.py selects. Two consequences
are worth expecting before reading the sheet:

- Every armed token carries the same held item. The side collection points
  g.ARMZ at assets/armz, which holds only the Cookboy handheld, so roughly a
  third of a random sample shows it. The curated 444 rations it to 22 tokens
  (~5%) as a chase trait, so the real mint does not look like this.
- There is no Rarity attribute, because tiers are assigned during curation.

Pass --seed to reproduce a sheet exactly; the seed is printed onto it.
"""

import argparse
import math
import os
import random
import sys
from collections import Counter
from multiprocessing import get_context
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import generator as g  # noqa: E402
from asset_assessment.apply_side_branding import (  # noqa: E402
    OVERLAY as OVERLAY_PATH,
    prepare_overlay,
)

CELL = 260
COLUMNS = 10
LABEL_H = 34
HEADER_H = 34


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--count", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20260813)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--backgrounds", default="side_collection/assets/backgroundz_final")
    ap.add_argument("--out", default="side_collection/catalog/sample_sheet.png")
    return ap.parse_args()


def render(job):
    layers, path, branding = job
    g.create_image(layers, path)
    token = Image.open(path).convert("RGBA")
    token.alpha_composite(Image.open(branding).convert("RGBA"))
    token.save(path, compress_level=1)
    return path


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{name}", size)
    except OSError:
        return ImageFont.load_default()


def fit(draw, text, face, width):
    """Trim a label to the cell so neighbouring columns cannot overlap."""
    if draw.textlength(text, font=face) <= width:
        return text
    while text and draw.textlength(text + "...", font=face) > width:
        text = text[:-1]
    return text + "..."


def main():
    args = parse_args()
    if args.count < 1:
        raise SystemExit("count must be positive")

    background_dir = (ROOT / args.backgrounds).resolve()
    if background_dir == (ROOT / "traits" / "backgroundz").resolve():
        raise SystemExit("the side collection may not use traits/backgroundz")
    g.BACKGROUNDZ = str(background_dir)
    g.STICKERZ = str((ROOT / "side_collection" / "assets" / "stickerz").resolve())
    g.ARMZ = str((ROOT / "side_collection" / "assets" / "armz").resolve())

    out = (ROOT / args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    tiles = out.parent / "sample_tokens"
    tiles.mkdir(parents=True, exist_ok=True)

    random.seed(args.seed)
    prepare_overlay()
    branding = str(OVERLAY_PATH)

    picks, seen = [], set()
    while len(picks) < args.count:
        layers, character = g.generate_random_combination()
        signature = (character,) + tuple(os.path.basename(l["path"]) for l in layers)
        if signature in seen:
            continue
        seen.add(signature)
        meta = {item["trait_type"]: item["value"]
                for item in g.extract_metadata(layers, character)}
        picks.append((layers, meta))

    jobs = [(layers, str(tiles / f"{i:03d}.png"), branding)
            for i, (layers, _) in enumerate(picks, 1)]
    workers = max(1, args.workers)
    if workers == 1:
        for done, job in enumerate(jobs, 1):
            render(job)
            if done % 10 == 0 or done == len(jobs):
                print(f"rendered {done}/{len(jobs)}", flush=True)
    else:
        with get_context("fork").Pool(processes=workers) as pool:
            for done, _ in enumerate(pool.imap_unordered(render, jobs), 1):
                if done % 10 == 0 or done == len(jobs):
                    print(f"rendered {done}/{len(jobs)}", flush=True)

    columns = min(COLUMNS, args.count)
    rows = math.ceil(args.count / columns)
    sheet = Image.new("RGB", (columns * CELL, rows * (CELL + LABEL_H) + HEADER_H),
                      (16, 16, 20))
    draw = ImageDraw.Draw(sheet)
    title, small = font(17, bold=True), font(12)
    draw.text((10, 9), f"Sweetardio Cookie Chain Edition - {args.count} random "
                       f"draws (seed {args.seed})", font=title, fill=(245, 245, 250))
    for i, (_, meta) in enumerate(picks):
        image = Image.open(jobs[i][1]).convert("RGB").resize(
            (CELL, CELL), Image.Resampling.LANCZOS)
        x, y = (i % columns) * CELL, HEADER_H + (i // columns) * (CELL + LABEL_H)
        sheet.paste(image, (x, y))
        head = f"{i + 1:02d}  {meta.get('Character', '')}"
        rest = " · ".join(v for v in (meta.get("Eyes"), meta.get("Mouth"),
                                      meta.get("Arms"), meta.get("Footwear")) if v)
        draw.text((x + 5, y + CELL + 3), fit(draw, head, small, CELL - 10),
                  font=small, fill=(238, 238, 244))
        draw.text((x + 5, y + CELL + 17), fit(draw, rest, small, CELL - 10),
                  font=small, fill=(150, 150, 162))
    sheet.save(out, optimize=True)

    print(f"\n{args.count} random tokens -> {out}")
    for group in ("Character", "Eyes", "Mouth", "Arms", "Footwear", "Sticker"):
        counts = Counter(m.get(group) for _, m in picks if m.get(group))
        print(f"  {group:10} {len(counts):2} distinct on {sum(counts.values())}/{args.count}")


if __name__ == "__main__":
    main()
