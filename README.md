# Sweetardio Side Collection

This is a curated 100-token showcase built from the production Sweetardio
compositor. It uses only the newly supplied sticker artwork; the original
`traits/stickerz` pool is never sampled.

```bash
python3 asset_assessment/prepare_side_stickers.py
python3 asset_assessment/prepare_side_backgrounds.py
python3 asset_assessment/build_side_collection.py
```

Every finished token receives the Cookie Chain Edition plaque in its
bottom-right corner. To brand an already-rendered image directory, run
`python3 asset_assessment/apply_side_branding.py`.

The builder renders a larger candidate pool and selects the strongest 100 by
subject/background separation, sticker readability, restrained background
detail, uniqueness, and collection-wide character/background diversity.

The side collection never reads the main generator's `traits/backgroundz`
directory. The newly uploaded catalog pack is preserved intact under
`assets/catalog_uploads/`; reviewed plate-style images are normalized into the
separate `assets/backgroundz/` pool, then the established adaptive background
pop grade writes production plates to `assets/backgroundz_treated/`. Character
pieces, transparent overlays,
the Cookie Chain badge, and the uploaded review sheet stay archived but are
not misclassified as backgrounds.

Treatment metrics for every plate are recorded in
`catalog/BACKGROUND_TREATMENT_LOG.md`. The curated builder uses only the
treated directory by default.

To rebuild with another side-only background folder:

```bash
python3 asset_assessment/build_side_collection.py --backgrounds path/to/backgrounds
```

Final images, OpenSea-style metadata, a manifest, and a 10x10 review sheet are
written under `side_collection/output/`.

The labeled 27-background catalog is `catalog/backgroundz_reference_sheet.png`.
