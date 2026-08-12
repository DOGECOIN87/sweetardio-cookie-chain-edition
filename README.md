# Sweetardio Side Collection

A curated 444-token showcase built from the production Sweetardio compositor.
It uses only the newly supplied sticker artwork; the original `traits/stickerz`
pool is never sampled, and the side collection never reads the main
generator's `traits/backgroundz` directory.

This repo ships the **source assets** (prepared stickers, the held game-device
arm, background plates, the branding badge source, and the reviewed catalog
uploads) plus the **build scripts**, so the full 444-image set with metadata
can be regenerated on demand instead of shipping ~1.5GB of rendered PNGs.

## Requirements

- A checkout of the production compositor (**generator.py** + **traits/**),
  since `build_side_collection.py` composites tokens through it. Place this
  repo's contents at `side_collection/` inside that checkout — i.e. copy
  `asset_assessment/*.py` into its `asset_assessment/` and this repo's
  `assets/` + `catalog/` into its `side_collection/`.
- `pip install pillow numpy scipy`

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
- `assets/armz/` — the Cookboy handheld game-device held item.
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
