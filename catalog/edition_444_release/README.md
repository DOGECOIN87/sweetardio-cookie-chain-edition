# Cookie Chain Edition — Approved 444-Token Release

This catalog records the finalized Cookie Chain Edition release, deterministically generated from seed `871003`. It contains the committed metadata, manifest, rarity report, and validation output for the synchronized 444-token set. The rendered PNGs are maintained outside Git to keep the repository practical to clone and deploy.

| Release rule | Final behavior |
| --- | --- |
| Token count | **444** unique `1393×1393` RGBA token images and metadata records |
| Rarity tiers | **4** Mythic Chase, **18** Legendary Chase, **66** Rare, **134** Uncommon, and **222** Core |
| Sticker pool | **22** curated transparent overlays with 6px white silhouette contours; each appears **20–21** times |
| Sticker adjustments | L, Real as a Doughnut, Cookboy, and Nyancat naming updates; approved round-logo and size treatments are embedded in the asset builder |
| Arms | Cookboy Handheld and **Printer** each appear exactly **22** times; Printer is excluded from gummy-bear characters |
| Background pool | Cosmic Fog, Oxford Blue Fur, and Golden Bubbles are excluded; the approved name changes and new Cookie Dough/Mattrick/Shubbi/Tenders artwork are reflected in metadata |
| Legendary handling | Nightly Legendary is exactly one Legendary Chase token paired with Nightly Wallet; Mattrick, Shubbi, and Tenders are each reserved as a single Legendary Chase background |

The finalized rendered image set is held at `/home/ubuntu/cookie-chain-edition-444-final-approved`. The zero-indexed Sugar/Candy Machine deployment staging set is held at `/home/ubuntu/cookie-chain-candy-machine/assets`.

## Reproduce and validate

```bash
python3 asset_assessment/prepare_cookiechain_sticker_overlays.py \
  --legacy-dir assets/catalog_uploads/cookie_chain_legacy_sticker_overlays \
  --dapp-source-dir assets/catalog_uploads/cookiechain_dapp_logos \
  --dapp-manifest asset_assessment/cookiechain_dapp_logo_manifest.json \
  --out assets/stickerz

python3 asset_assessment/build_side_collection.py \
  --count 444 --seed 871003 --candidates-per-sticker 120 --workers 4 \
  --out /path/to/cookie-chain-edition-444

python3 asset_assessment/validate_cookie_chain_release.py \
  --release /path/to/cookie-chain-edition-444 --count 444 --sticker-dir assets/stickerz
```

Run release validation before metadata upload or Candy Machine deployment. Then build zero-indexed deployment files with `asset_assessment/build_candy_machine_staging.py`.
