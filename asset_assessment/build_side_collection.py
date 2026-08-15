#!/usr/bin/env python3
"""Build the curated 444-token Cookie Chain Edition collection.

Unlike the rarity-driven main mint, this renders a broad candidate set and
selects for visual separation, restrained background detail behind the figure,
clean sticker readability, uniqueness, and collection-level variety. Every
token carries exactly one sticker from the new side-collection sticker pool.
"""

import argparse
import json
import math
import os
import random
import shutil
import sys
import tempfile
from collections import Counter
from functools import lru_cache
from multiprocessing import get_context
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SIDE_ROOT = ROOT / "side_collection" if (ROOT / "side_collection").is_dir() else ROOT
sys.path.insert(0, str(ROOT))
import generator as g  # noqa: E402
from asset_assessment.apply_side_branding import (  # noqa: E402
    OVERLAY as OVERLAY_PATH,
    prepare_overlay,
)

RARITY_COUNTS = {
    "Mythic Chase": 4,
    "Legendary Chase": 18,
    "Rare": 66,
    "Uncommon": 134,
    "Core": 222,
}
CHASE_BACKGROUNDS = {
    "Emyr_Gallery.png", "Gold_Cookie_Emboss.png",
    "Short_The_Banks_Vault.png", "Golden_Bubbles.png", "Simplex_Arcade.png",
    "Cookie_Vault.png", "Cookboy_Paisley.png",
}
GAME_DEVICE = "Cookboy_Handheld.png"
LIMITED_ARM_COUNTS = {
    GAME_DEVICE: 22,
}

# Canonical public metadata labels. Asset filenames remain untouched because
# generator.py uses several of them as compositor keys.
DISPLAY_NAME_OVERRIDES = {
    "AK15": "AK-15", "AK15.png": "AK-15",
    "AR47": "AR-47", "AR47.png": "AR-47",
    "Out Of Order": "Out of Order",
    "Out_Of_Order": "Out of Order",
    "Short The Banks Vault": "Short the Banks Vault",
    "Short_The_Banks_Vault": "Short the Banks Vault",
    "Gold_Cookie_Emboss": "Cookboy",
    "Gold_Cookie_Emboss.png": "Cookboy",
    "Chocolate_Cookie_Emboss": "Cookboy Chocolate",
    "Chocolate_Cookie_Emboss.png": "Cookboy Chocolate",
    "Black_Cookie_Emboss": "Cookboy Black Enamel",
    "Black_Cookie_Emboss.png": "Cookboy Black Enamel",
    "Silver_Cookie_Emboss": "Cookboy Silver",
    "Silver_Cookie_Emboss.png": "Cookboy Silver",
    "Morsel": "Morsel",
    "Morsel.png": "Morsel",
    "Cookiebox": "Cookiebox",
    "Cookiebox.png": "Cookiebox",
    # Public Cookie Chain Apps Registry logo stickers.
    "CookieScan": "CookieScan",
    "Hyperlane_Bridge": "Hyperlane Bridge",
    "Nightly_Wallet": "Nightly Wallet",
    "DefiLlama": "DefiLlama",
    "Bake_Your_Stake": "Bake Your Stake",
    "CookieSwap": "CookieSwap",
    "Candy_Shop": "Candy Shop",
    "Metaplex": "Metaplex",
    "Cookie_Quads": "Cookie Quads",
    "Cookiebox_Liquidity_Hub": "Cookiebox Liquidity Hub",
    "CookieScan_DAS_API": "CookieScan DAS API",
    "MomoSwap": "MomoSwap",
    "Morsel_Wallet": "Morsel Wallet",
    "CookOven": "CookOven",
    "CookBook": "CookBook",
    "Cookie_Lock": "Cookie Lock",
    "Cookie_Chat": "Cookie Chat",
    "GORBOY": "GORBOY",
    "Sesamians": "Sesamians",
    "Baked_Bazaar": "Baked Bazaar",
    "GorWeld": "GorWeld",
    "Cookie_MCP": "Cookie MCP",
}


def clean_display(value):
    """Return one stable, human-readable metadata value without renaming art."""
    stem = Path(value).stem
    if stem in DISPLAY_NAME_OVERRIDES:
        return DISPLAY_NAME_OVERRIDES[stem]
    return stem.replace("_", " ")


def canonicalize_metadata(metadata):
    """Normalize all emitted values through the same public naming policy."""
    return [{"trait_type": item["trait_type"],
             "value": clean_display(str(item["value"]))}
            for item in metadata]


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--count", type=int, default=100)
    ap.add_argument("--candidates-per-sticker", type=int, default=120)
    ap.add_argument("--workers", type=int, default=4,
                    help="parallel full-quality render processes")
    ap.add_argument("--seed", type=int, default=871003)
    ap.add_argument("--dry-run", action="store_true",
                    help="select and validate the full allocation without rendering")
    ap.add_argument("--backgrounds", default="assets/backgroundz",
                    help="authoritative Cookie Edition background directory (never traits/backgroundz)")
    ap.add_argument("--out", default="output")
    return ap.parse_args()


def layer_signature(layers, character):
    return (character,) + tuple(os.path.basename(layer["path"]) for layer in layers)


def layer_kind(layer, sticker_dir):
    path = os.path.normpath(layer["path"])
    if path.startswith(os.path.normpath(sticker_dir) + os.sep):
        return "sticker"
    if path.startswith(os.path.normpath(os.path.join(g.TRAITS_DIR, g.CHARACTERZ)) + os.sep):
        return "character"
    return "other"


def render_mask(layers, sticker_dir):
    mask = Image.new("L", (g.CANVAS_SIZE, g.CANVAS_SIZE), 0)
    for layer in layers[1:]:
        if layer_kind(layer, sticker_dir) == "sticker":
            continue
        rendered = g._render_layer(layer)
        if rendered is not None:
            mask = ImageChops.lighter(mask, rendered.getchannel("A"))
    return mask


def visual_score(path, layers, sticker_dir):
    # Score at review resolution. Full-canvas float arrays exceed 100 MB per
    # candidate and add no useful accuracy for these broad composition metrics.
    review = (256, 256)
    final = np.asarray(Image.open(path).convert("RGB").resize(review, Image.Resampling.BILINEAR), dtype=np.float32)
    background = np.asarray(g._render_layer(layers[0]).convert("RGB").resize(review, Image.Resampling.BILINEAR), dtype=np.float32)
    mask_image = render_mask(layers, sticker_dir).resize(review, Image.Resampling.BILINEAR)
    mask = np.asarray(mask_image) >= 128
    if mask.sum() < 1000:
        return -1e9

    # Colour/luma separation between the figure and the exact plate region it covers.
    fg = final[mask]
    bg_under = background[mask]
    fg_mean, bg_mean = fg.mean(axis=0), bg_under.mean(axis=0)
    colour_sep = float(np.linalg.norm(fg_mean - bg_mean) / 441.7)
    fg_luma = fg @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    bg_luma = bg_under @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    luma_sep = abs(float(fg_luma.mean() - bg_luma.mean())) / 255.0

    # Moderate detail reads as intentional; very busy plates compete with the character.
    gray = background @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    gy, gx = np.gradient(gray)
    busy = float(np.hypot(gx, gy)[mask].mean())
    busy_score = math.exp(-((busy - 10.0) / 11.0) ** 2)

    # The new sticker must remain distinct from its lower-left plate region.
    sticker_mask_image = Image.new("L", (g.CANVAS_SIZE, g.CANVAS_SIZE), 0)
    for layer in layers:
        if layer_kind(layer, sticker_dir) == "sticker":
            rendered = g._render_layer(layer)
            sticker_mask_image = ImageChops.lighter(sticker_mask_image, rendered.getchannel("A"))
    sticker_mask = np.asarray(sticker_mask_image.resize(review, Image.Resampling.BILINEAR)) >= 128
    sticker_sep = 0.0
    if sticker_mask.any():
        sfg = final[sticker_mask].mean(axis=0)
        sbg = background[sticker_mask].mean(axis=0)
        sticker_sep = float(np.linalg.norm(sfg - sbg) / 441.7)

    # Strong weighting on subject readability, then sticker clarity and plate restraint.
    return 4.0 * colour_sep + 2.5 * luma_sep + 1.8 * sticker_sep + 1.2 * busy_score


def metadata_dict(metadata):
    return {item["trait_type"]: item["value"] for item in metadata}


@lru_cache(maxsize=None)
def asset_descriptor(path):
    """Compact colour/detail descriptor used before expensive final renders."""
    image = Image.open(path).convert("RGBA")
    image.thumbnail((160, 160), Image.Resampling.BILINEAR)
    rgba = np.asarray(image, dtype=np.float32)
    alpha = rgba[:, :, 3] / 255.0
    visible = alpha > 0.2
    if not visible.any():
        return np.zeros(3), 0.0, 0.0
    rgb = rgba[:, :, :3]
    weights = alpha[visible]
    mean = np.average(rgb[visible], axis=0, weights=weights)
    luma = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    gy, gx = np.gradient(luma)
    busy = float(np.average(np.hypot(gx, gy)[visible], weights=weights))
    return mean, float(np.average(luma[visible], weights=weights)), busy


def proxy_visual_score(layers, sticker_dir):
    """Rank combinations using their actual component art, before rendering.

    The score rewards foreground/plate and sticker/plate separation while
    preferring moderately detailed plates. It lets us inspect thousands of
    combinations and reserve the expensive production compositor for winners.
    """
    bg_path = layers[0]["path"]
    bg_rgb, bg_luma, busy = asset_descriptor(bg_path)
    foreground = []
    sticker = None
    for layer in layers[1:]:
        path = layer["path"]
        if layer_kind(layer, sticker_dir) == "sticker":
            sticker = asset_descriptor(path)
        elif not os.path.basename(path).endswith("_Overlay.png"):
            foreground.append(asset_descriptor(path))
    if not foreground:
        return -1e9
    fg_rgb = np.mean([item[0] for item in foreground], axis=0)
    fg_luma = float(np.mean([item[1] for item in foreground]))
    colour_sep = float(np.linalg.norm(fg_rgb - bg_rgb) / 441.7)
    luma_sep = abs(fg_luma - bg_luma) / 255.0
    sticker_sep = 0.0
    if sticker is not None:
        sticker_sep = float(np.linalg.norm(sticker[0] - bg_rgb) / 441.7)
    busy_score = math.exp(-((busy - 18.0) / 18.0) ** 2)
    return 4.2 * colour_sep + 2.8 * luma_sep + 1.7 * sticker_sep + busy_score


def arm_filename(candidate):
    """Return the selected arm filename, if this candidate has one."""
    for layer in candidate["layers"]:
        filename = os.path.basename(layer["path"])
        if filename in LIMITED_ARM_COUNTS:
            return filename
    return None


def choose(candidates, count, stickers):
    base, extra = divmod(count, len(stickers))
    quotas = {name: base + (i < extra) for i, name in enumerate(stickers)}
    chosen = []
    char_counts, bg_counts = Counter(), Counter()
    unique_chars = {c["metadata_map"].get("Character", "") for c in candidates}
    unique_bgs = {c["metadata_map"].get("Background", "") for c in candidates}
    char_cap = math.ceil(count / max(1, len(unique_chars))) + 3
    bg_cap = math.ceil(count / max(1, len(unique_bgs))) + 3

    limited_quotas = {}
    for arm, target in LIMITED_ARM_COUNTS.items():
        exact_target = target if count == 444 else 0
        base, extra = divmod(exact_target, len(stickers))
        limited_quotas[arm] = {
            sticker: base + (i < extra) for i, sticker in enumerate(stickers)
        }

    for sticker in stickers:
        pool = sorted((c for c in candidates if c["sticker_file"] == sticker),
                      key=lambda c: c["score"], reverse=True)
        sticker_chosen = 0
        for arm, per_sticker in limited_quotas.items():
            arm_quota = per_sticker[sticker]
            arm_pool = [candidate for candidate in pool if arm_filename(candidate) == arm]
            for candidate in arm_pool[:arm_quota]:
                md = candidate["metadata_map"]
                char, bg = md.get("Character", ""), md.get("Background", "")
                chosen.append(candidate)
                char_counts[char] += 1
                bg_counts[bg] += 1
                sticker_chosen += 1
            if sum(arm_filename(candidate) == arm for candidate in chosen
                   if candidate["sticker_file"] == sticker) != arm_quota:
                raise RuntimeError(f"not enough compatible {arm} candidates for {sticker}")
        regular_pool = [candidate for candidate in pool if arm_filename(candidate) is None]
        for candidate in regular_pool:
            md = candidate["metadata_map"]
            char, bg = md.get("Character", ""), md.get("Background", "")
            if char_counts[char] >= char_cap or bg_counts[bg] >= bg_cap:
                continue
            chosen.append(candidate)
            char_counts[char] += 1
            bg_counts[bg] += 1
            sticker_chosen += 1
            if sticker_chosen >= quotas[sticker]:
                break
        if sticker_chosen != quotas[sticker]:
            raise RuntimeError(f"not enough unique candidates for {sticker}")

    # Relax diversity caps only if a small candidate pool could not satisfy them.
    if len(chosen) < count:
        used = {c["signature"] for c in chosen}
        for candidate in sorted(candidates, key=lambda c: c["score"], reverse=True):
            if candidate["signature"] in used:
                continue
            if arm_filename(candidate) is not None:
                continue
            if sum(c["sticker_file"] == candidate["sticker_file"] for c in chosen) >= quotas[candidate["sticker_file"]]:
                continue
            chosen.append(candidate)
            used.add(candidate["signature"])
            if len(chosen) == count:
                break
    if len(chosen) != count:
        raise RuntimeError(f"could select only {len(chosen)} of {count} requested tokens")
    return chosen


def assign_rarity(chosen, count):
    """Assign exact tiers, reserving the strongest chase-background tokens."""
    if count != sum(RARITY_COUNTS.values()):
        # Smoke tests and alternate counts use proportional tiers.
        weights = [(name, n / 444) for name, n in RARITY_COUNTS.items()]
        counts, used = {}, 0
        for name, share in weights[:-1]:
            counts[name] = round(count * share)
            used += counts[name]
        counts[weights[-1][0]] = count - used
    else:
        counts = RARITY_COUNTS
    if sum(counts.values()) != count:
        raise RuntimeError(f"rarity tiers total {sum(counts.values())}, expected {count}")
    ordered = list(counts.values())
    if ordered != sorted(ordered):
        raise RuntimeError("rarity tiers must increase from Mythic Chase through Core")

    def chase_key(item):
        bg = os.path.basename(item["layers"][0]["path"])
        bonus = 2.0 if bg in CHASE_BACKGROUNDS else 0.0
        arms = 0.45 if "Arms" in item["metadata_map"] else 0.0
        footwear = 0.25 if "Footwear" in item["metadata_map"] else 0.0
        return bonus + arms + footwear + item["score"]

    ranked = sorted(chosen, key=chase_key, reverse=True)
    # Both limited arm traits land before the Rare/Core tiers while still
    # allowing the four strongest combinations to become Mythics.
    ranked.sort(key=lambda item: (
        arm_filename(item) is None,
        -chase_key(item),
    ))
    cursor = 0
    for tier, amount in counts.items():
        for item in ranked[cursor:cursor + amount]:
            item["rarity"] = tier
        cursor += amount
    # Mint numbering is shuffled so chase tokens cannot be guessed by number.
    random.shuffle(chosen)
    return counts


def validate_selection(chosen, count, rarity_counts):
    """Fail before expensive rendering if supply or rarity invariants drift."""
    if len(chosen) != count:
        raise RuntimeError(f"selected {len(chosen)} tokens, expected {count}")
    signatures = [item["signature"] for item in chosen]
    if len(set(signatures)) != count:
        raise RuntimeError("selected trait combinations are not unique")
    actual_rarities = Counter(item.get("rarity") for item in chosen)
    if actual_rarities != Counter(rarity_counts):
        raise RuntimeError(
            f"rarity assignment mismatch: {dict(actual_rarities)} != {rarity_counts}")
    if count == 444:
        for arm, expected in LIMITED_ARM_COUNTS.items():
            actual = sum(arm_filename(item) == arm for item in chosen)
            if actual != expected:
                raise RuntimeError(f"{arm} count is {actual}, expected {expected}")


def render_job(job):
    layers, path, branding_path = job
    g.create_image(layers, path)
    token = Image.open(path).convert("RGBA")
    token.alpha_composite(Image.open(branding_path).convert("RGBA"))
    token.save(path, compress_level=1)
    return path


def font(size):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def contact_sheet(chosen, out_path):
    cell, label_h, cols = 300, 30, 10
    rows = math.ceil(len(chosen) / cols)
    sheet = Image.new("RGB", (cols * cell, rows * (cell + label_h)), (15, 15, 18))
    draw = ImageDraw.Draw(sheet)
    face = font(15)
    for i, item in enumerate(chosen):
        image = Image.open(item["final_path"]).convert("RGB").resize((cell, cell), Image.Resampling.LANCZOS)
        x, y = (i % cols) * cell, (i // cols) * (cell + label_h)
        sheet.paste(image, (x, y))
        label = f"#{i + 1:03d}  {item['metadata_map'].get('Character', '')}"
        draw.text((x + 6, y + cell + 6), label, font=face, fill=(238, 238, 242))
    sheet.save(out_path, optimize=True)


def main():
    args = parse_args()
    if args.count < 1 or args.candidates_per_sticker < 1:
        raise SystemExit("count and candidates-per-sticker must be positive")
    random.seed(args.seed)

    sticker_dir = (SIDE_ROOT / "assets" / "stickerz").resolve()
    arm_dir = (SIDE_ROOT / "assets" / "armz").resolve()
    stickers = sorted(path.name for path in sticker_dir.glob("*.png"))
    if not stickers:
        raise SystemExit("no prepared stickers; run prepare_side_stickers.py first")
    # Small smoke runs need not render unused sticker groups. Production's
    # default count (100) still activates and balances the complete pool.
    stickers = stickers[:min(args.count, len(stickers))]
    g.STICKERZ = str(sticker_dir)
    if not (arm_dir / GAME_DEVICE).exists():
        raise SystemExit("missing side arm; run prepare_side_arm.py first")
    g.ARMZ = str(arm_dir)
    background_dir = (SIDE_ROOT / args.backgrounds).resolve()
    production_backgrounds = (ROOT / "traits" / "backgroundz").resolve()
    if background_dir == production_backgrounds:
        raise SystemExit("the side collection may not use traits/backgroundz")
    if not list(background_dir.glob("*.png")):
        raise SystemExit("no side backgrounds; run prepare_side_backgrounds.py first")
    g.BACKGROUNDZ = str(background_dir)

    out = (SIDE_ROOT / args.out).resolve()
    images_dir, metadata_dir = out / "images", out / "metadata"
    images_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    candidates = []
    seen = set()
    total = len(stickers) * args.candidates_per_sticker
    made = 0
    for sticker in stickers:
        accepted = 0
        attempts = 0
        while accepted < args.candidates_per_sticker and attempts < args.candidates_per_sticker * 20:
            attempts += 1
            # Seed every sticker pool with both limited arm traits so the final
            # allocation can hit exact counts without sacrificing sticker balance.
            per_arm_seed = max(6, math.ceil(max(LIMITED_ARM_COUNTS.values()) / len(stickers)) * 3)
            limited_arms = tuple(LIMITED_ARM_COUNTS)
            forced_arm = (limited_arms[accepted % len(limited_arms)]
                          if accepted < len(limited_arms) * per_arm_seed else None)
            layers, character = g.generate_random_combination(
                force_sticker=sticker,
                force_arm=forced_arm,
            )
            signature = layer_signature(layers, character)
            if signature in seen:
                continue
            seen.add(signature)
            metadata = g.extract_metadata(layers, character)
            score = proxy_visual_score(layers, str(sticker_dir))
            candidates.append({
                "layers": layers, "character": character,
                "signature": signature, "sticker_file": sticker,
                "metadata": metadata, "metadata_map": metadata_dict(metadata),
                "score": score,
            })
            accepted += 1
            made += 1
            if made % 100 == 0 or made == total:
                print(f"ranked {made}/{total} candidate combinations", flush=True)

    chosen = choose(candidates, args.count, stickers)
    rarity_counts = assign_rarity(chosen, args.count)
    validate_selection(chosen, args.count, rarity_counts)
    if args.dry_run:
        print(f"validated {len(chosen)} unique allocations (seed {args.seed})")
        print("rarity: " + ", ".join(
            f"{tier}={rarity_counts[tier]}" for tier in RARITY_COUNTS))
        print("stickers: " + ", ".join(
            f"{clean_display(sticker)}={sum(c['sticker_file'] == sticker for c in chosen)}"
            for sticker in stickers))
        print(", ".join(
            f"{clean_display(arm)}={sum(arm_filename(item) == arm for item in chosen)}"
            for arm in LIMITED_ARM_COUNTS))
        return
    jobs = []
    prepare_overlay()
    branding_path = str(OVERLAY_PATH)
    for i, item in enumerate(chosen, 1):
        image_path = images_dir / f"{i:03d}.png"
        item["final_path"] = str(image_path)
        jobs.append((item["layers"], str(image_path), branding_path))

    workers = max(1, args.workers)
    print(f"rendering {len(jobs)} winners at full quality with {workers} workers", flush=True)
    if workers == 1:
        for done, job in enumerate(jobs, 1):
            render_job(job)
            if done % 10 == 0 or done == len(jobs):
                print(f"rendered {done}/{len(jobs)}", flush=True)
    else:
        with get_context("fork").Pool(processes=workers) as pool:
            for done, _ in enumerate(pool.imap_unordered(render_job, jobs), 1):
                if done % 10 == 0 or done == len(jobs):
                    print(f"rendered {done}/{len(jobs)}", flush=True)

    manifest = []
    for i, item in enumerate(chosen, 1):
        attrs = canonicalize_metadata(item["metadata"])
        # The layer filename is authoritative for side-collection backgrounds.
        for attr in attrs:
            if attr["trait_type"] == "Background":
                attr["value"] = clean_display(os.path.basename(item["layers"][0]["path"]))
        attrs.append({"trait_type": "Edition", "value": "Cookie Chain Edition"})
        attrs.append({"trait_type": "Rarity", "value": item["rarity"]})
        token = {
            "name": f"Cookie Chain Edition #{i:03d}",
            "description": "One of 444 Cookie Chain Edition collectibles.",
            "image": f"../images/{i:03d}.png",
            "attributes": attrs,
            "selection_score": round(item["score"], 6),
            "seed": args.seed,
        }
        with open(metadata_dir / f"{i:03d}.json", "w", encoding="utf-8") as handle:
            json.dump(token, handle, indent=2)
            handle.write("\n")
        manifest.append(token)

    with open(out / "manifest.json", "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")
    contact_sheet(chosen, out / "contact_sheet.png")

    trait_counts = {key: Counter() for key in
                    ("Character", "Background", "Sticker", "Arms", "Rarity")}
    for token in manifest:
        for attr in token["attributes"]:
            if attr["trait_type"] in trait_counts:
                trait_counts[attr["trait_type"]][attr["value"]] += 1
    with open(out / "RARITY.md", "w", encoding="utf-8") as handle:
        handle.write("# Cookie Chain Edition — Rarity\n\n")
        handle.write(f"Supply: **{args.count}** · Seed: **{args.seed}** · "
                     "all trait combinations unique.\n\n")
        handle.write("## Exact tiers\n\n")
        for tier in RARITY_COUNTS:
            n = rarity_counts.get(tier, 0)
            handle.write(f"- {tier}: **{n}** ({100*n/args.count:.2f}%)\n")
        for group in ("Sticker", "Arms", "Background", "Character"):
            handle.write(f"\n## {group}\n\n")
            for name, n in sorted(trait_counts[group].items(), key=lambda x: (-x[1], x[0])):
                handle.write(f"- {name}: {n} ({100*n/args.count:.2f}%)\n")

    print(f"selected {len(chosen)} curated tokens -> {out}")
    print("stickers: " + ", ".join(f"{s}={sum(c['sticker_file'] == s for c in chosen)}" for s in stickers))


if __name__ == "__main__":
    main()
