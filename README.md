# Sweetardio Side Collection

A curated 444-token showcase built from the production Sweetardio compositor.
It uses only the newly supplied sticker artwork; the original `traits/stickerz`
pool is never sampled, and the side collection never reads the main
generator's `traits/backgroundz` directory.

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

To brand an already-rendered image directory separately:

```bash
python3 asset_assessment/apply_side_branding.py --images path/to/images
```

To rebuild with another side-only background folder:

```bash
python3 asset_assessment/build_side_collection.py --count 444 --backgrounds path/to/backgrounds
```

## Assets in this repo

- `assets/stickerz/` — the 9 prepared side-collection stickers.
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
- `catalog/` — the treatment log and labeled background reference sheets
  (`backgroundz_reference_sheet.png` for the raw pool,
  `backgroundz_treated_reference_sheet.png` for the graded one).

## Figure trait art (`traits/`)

`generator.py` resolves these pools as `traits/<name>/`, so they sit at the
repo root rather than under `assets/`. All 71 files are 1393×1393 RGBA, the
collection's canvas size.

**Do not rename anything in `traits/`.** The filenames look untidy —
`Sweetardio_114 (4).png`, `layer-layer-layer-layer-AK15.png` — but they are
keys, not labels, and the tables that consume them live in `generator.py`,
which this repo does not ship. A rename here is silent: nothing errors, the
lookup just misses and the behaviour it carried disappears.

| what a rename breaks | keyed by |
|---|---|
| the display name in the token metadata | `TRAIT_NAMES[<category>]` |
| Dual Uzis' 0.8 scale | `ARM_SCALE["Sweetardio_115 (11).png"]` |
| ding_dong's per-arm nudges | `ARM_CHAR_ARM_DY[(char, arm_file)]` |
| the lollipop's and joint's 3D prop shadow | `MOUTH_PROP_FILES` |
| every character's scale and placement | `CHAR_SCALE` / `CHAR_Y_ADJUST`, matched by **substring** of `char_base_name()` |
| footwear base↔overlay pairing | the `_Base` / `_Overlay` filename suffixes, parsed by `wat_base_name()` |

The metadata already comes out clean through `TRAIT_NAMES` — `Sweetardio_114
(4).png` renders as "Blue Saber" — so a rename buys nothing and costs the
above. Renaming them properly means editing `generator.py`'s tables and the
main collection's art in the same change, then rebuilding `char_compat.json`
and re-running `calibrate_rarity.py`.

The stickers under `assets/stickerz/` are the opposite case and were renamed:
they are this collection's own art, `TRAIT_NAMES` has no entry for them, so
each filename **is** its metadata value.

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
