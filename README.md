# Sweetardio Side Collection

A curated 444-token showcase built from the production Sweetardio compositor.
It uses only the newly supplied sticker artwork; the original `traits/stickerz`
pool is never sampled, and the side collection never reads the main
generator's `traits/backgroundz` directory.

> **Deploying the collection?** Start with [`DEPLOYMENT.md`](DEPLOYMENT.md). It
> covers the deterministic 444-piece recreation, Sugar-compatible asset
> staging, Cookie Chain Candy Machine v3 deployment, frontend configuration,
> and post-deploy safety checks.

This repo ships the **source assets** (prepared stickers, the held game-device
arm, background plates, the branding badge source, and the reviewed catalog
uploads), the **figure trait art** the compositor draws every token from, and
the **build scripts**, so the full 444-image set with metadata can be
regenerated on demand instead of shipping ~1.5GB of rendered PNGs.

## Requirements

- A checkout of the production compositor (**generator.py**), since
  `build_side_collection.py` composites tokens through it. Place this repo's
  contents at `side_collection/` inside that checkout — i.e. copy
  `asset_assessment/*.py` into its `asset_assessment/`, this repo's `assets/` +
  `catalog/` into its `side_collection/`, and this repo's `traits/` into its
  `traits/`.
- `pip install pillow numpy scipy`

The six figure trait pools the compositor needs are now checked in under
`traits/` (see below), so a checkout only has to supply `generator.py` itself.

## Generating the collection

The stickers, arm, and backgrounds under `assets/` are already prepared and
checked in, so the only step required to produce the full set is:

```bash
python3 asset_assessment/build_side_collection.py --count 444
```

This renders a larger candidate pool per sticker and selects the strongest
444 by subject/background separation, sticker readability, restrained
background detail, uniqueness, and collection-wide character/background
diversity. Every finished token receives the Cookie Chain Edition plaque in
its bottom-right corner automatically. Final images, OpenSea-style metadata,
a manifest, and a contact sheet are written under `side_collection/output/`
by default (override with `--out`).

To rebuild a prep step from scratch (not required — their outputs are already
in `assets/`):

```bash
python3 asset_assessment/prepare_side_stickers.py      # traits/stickerz -> assets/stickerz
python3 asset_assessment/prepare_side_backgrounds.py    # assets/catalog_uploads -> assets/backgroundz
python3 asset_assessment/prepare_side_arm.py            # assets/catalog_uploads -> assets/armz
```

To eyeball the pipeline without building the whole set:

```bash
python3 asset_assessment/render_side_sample_sheet.py --count 50 --seed 20260813
```

This renders N random tokens through the full compositor, plaque included, and
writes a labelled contact sheet to `side_collection/catalog/sample_sheet.png`
(the checked-in `catalog/sample_sheet.png` is that command's output). It is a
**look, not a mint** — tokens come straight from `generate_random_combination()`
with only a uniqueness check, so there is no scoring, no diversity cap and no
Rarity attribute, and every armed token shows the Cookboy because
`assets/armz/` holds just the one held item. The curated 444 rations that to
22 tokens (~5%), so the real mint is not distributed like the sheet. Reuse
`--seed` to reproduce a sheet exactly.

To brand an already-rendered image directory separately:

```bash
python3 asset_assessment/apply_side_branding.py --images path/to/images
```

To rebuild with another side-only background folder:

```bash
python3 asset_assessment/build_side_collection.py --count 444 --backgrounds path/to/backgrounds
```

## Assets in this repo

- `assets/stickerz/` — the 11 original Cookie Chain Edition stickers plus 22
  normalized public Cookie Chain dapp-logo stickers. Their canonical sources,
  public names, and normalization policy are recorded in
  `asset_assessment/cookiechain_dapp_logo_manifest.json` and
  `asset_assessment/cookiechain_dapp_sticker_policy.md`.
- `assets/armz/` — the Cookboy handheld game-device held item. It is sized and
  placed to match the production held-item arms, and is held in the character's
  **left** hand — the viewer's right. See `prepare_side_arm.py` for the
  measurements that fix its height and position.
- `assets/backgroundz/` — reviewed plate-style images normalized from the
  catalog upload.
- `assets/backgroundz_treated/` — those plates after the adaptive background
  pop grade (`catalog/BACKGROUND_TREATMENT_LOG.md` records the metrics).
- `assets/backgroundz_final/` — the background pool `build_side_collection.py`
  reads by default.
- `assets/branding/` — the derived Cookie Chain Edition plaque overlay
  (regenerated automatically from `assets/catalog_uploads/` on every build).
- `assets/catalog_uploads/` — the uploaded source pack, preserved intact.
- `catalog/` — the treatment log and the labeled background reference sheets
  (`backgroundz_reference_sheet.png` for the raw pool,
  `backgroundz_treated_reference_sheet.png` for the graded one), plus
  `sample_sheet.png`, a 50-token random draw through the full pipeline.

## Figure trait art (`traits/`)

`generator.py` resolves these pools as `traits/<name>/`, so they sit at the
repo root rather than under `assets/`. All 71 files are 1393×1393 RGBA, the
collection's canvas size.

The files are named for what they are — `Blue_Saber.png`, `Diamond_Grill.png`,
`zebra_cake.png` — and **this collection's copies are named independently of
the main collection's**, which still uses the original authoring names
(`Sweetardio_114 (4).png`, `layer-layer-layer-layer-AK15.png`).

These filenames are keys as well as labels, and the tables that read them live
in `generator.py`, which this repo does not ship. A rename there is silent —
nothing errors, the lookup just misses — so each name here was chosen to land
on the same value it had before:

| mechanism | how the new names keep it |
|---|---|
| metadata display name | `TRAIT_NAMES` misses, and `_fallback_display_name()` derives the identical string from the filename |
| character scale + placement | `CHAR_SCALE` / `CHAR_Y_ADJUST` match on `char_base_name()`, and the files are now named *exactly* that base name, so all 27 are byte-identical in scale, y-adjust, footwear exclusion and gorbhouse eligibility |
| footwear base↔overlay pairing | the `_Base` / `_Overlay` suffixes `wat_base_name()` parses are preserved, and `Shiba`→`Shiba_Slippers` etc. keeps the display name that `TRAIT_NAMES` used to supply |
| gorbhouse overlay | still `Gorbhouse_Overlay.png`, one of the two spellings the compositor looks for |

Two lookups could **not** be preserved from inside this repo, because they key
on the filename with no derivable fallback:

- **`MOUTH_PROP_FILES`** — it hardcodes `layer-Mouth_Smoke (1).png` and
  `layer-Mouth_Lollipop (1).png`, so `Smoke.png` and `Lollipop.png` no longer
  match and take the lighter `MOUTH_SHADOW` instead of the 3D prop shadow.
  Measured at up to 39 levels over ~4.6k pixels on the joint: the prop sits
  flatter against the ball. Fix, if wanted, is additive in `generator.py` —
  add `"Smoke.png"` and `"Lollipop.png"` to the set, keeping the old entries
  so the main collection is unaffected.
- **`ARM_SCALE` / `ARM_CHAR_ARM_DY`** — keyed on `Sweetardio_115 (11).png`
  (Dual Uzis at 0.8) and `Arms_Cash.png`. This collection never samples
  `traits/armz` at all — `build_side_collection.py` points `g.ARMZ` at
  `assets/armz` — so nothing here changes, but a main-collection render
  pointed at *this* `traits/armz` would lose those values.

The stickers under `assets/stickerz/` were renamed for the same reason: they
are this collection's own art, `TRAIT_NAMES` has no entry for them, so each
filename **is** its metadata value.

| folder | count | what it is |
|---|---|---|
| `traits/characterz/` | 27 | the character bodies |
| `traits/skinz/` | 3 | the lit skin balls (White, Black, Alien) |
| `traits/eyez/` | 10 | the registered, lens-lit eyes |
| `traits/mouthz/` | 9 | the mouths |
| `traits/what_are_thosez/` | 11 | footwear base + overlay pairs |
| `traits/armz/` | 11 | the production held-item arms |

Two notes on how the side build consumes them:

- **`traits/armz` is not sampled by this collection.** `build_side_collection.py`
  reassigns `g.ARMZ` to `assets/armz`, so the only held item a Cookie Chain
  token can draw is the Cookboy handheld. The production arms are checked in
  for completeness and for rendering through `generator.py` directly.
- The optional compat/weight maps (`char_compat.json`, `eyez_compat.json`,
  `wat_compat.json`, `skin_weights.json`, `rarity_weights.json`) are **not**
  shipped here — they are keyed to the main collection's plates, not these.
  `generator.py` treats each as optional and falls back to "no restrictions",
  which is the correct behaviour for this collection.
