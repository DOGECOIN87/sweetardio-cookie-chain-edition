# Cookie Chain Edition — Final 444-Token Release

This catalog is the deterministic final release for the Cookie Chain Edition. It is rendered from seed `871003` and contains the committed metadata, manifest, rarity report, and validation output for the synchronized 444-token set.

| Release rule | Final behavior |
| --- | --- |
| Token count | 444 unique 1393×1393 RGBA images and metadata records |
| Rarity tiers | 4 Mythic Chase, 18 Legendary Chase, 66 Rare, 134 Uncommon, and 222 Core |
| Background metadata | The embossed background is named **Cookboy** |
| Arms | **Cookboy Handheld** appears exactly 22 times; Cookie Hands is absent |
| Sticker pool | 26 curated original-style transparent overlays, balanced at 17–18 uses each |
| Nightly Legendary | Exactly one Legendary Chase token, paired with Nightly Wallet |

The full rendered image set is intentionally held outside Git at `/home/ubuntu/cookie-chain-edition-444-original-stickers`. The zero-indexed Sugar deployment staging set is held at `/home/ubuntu/cookie-chain-candy-machine/assets`.

To reproduce the release:

```bash
python3 asset_assessment/prepare_cookiechain_sticker_overlays.py \
  --legacy-dir assets/catalog_uploads/cookie_chain_legacy_sticker_overlays \
  --dapp-source-dir assets/catalog_uploads/cookiechain_dapp_logos \
  --dapp-manifest asset_assessment/cookiechain_dapp_logo_manifest.json \
  --out assets/stickerz

python3 asset_assessment/build_side_collection.py \
  --count 444 --seed 871003 --candidates-per-sticker 120 --workers 4 \
  --out /path/to/cookie-chain-edition-444
```

Run `asset_assessment/validate_cookie_chain_release.py` against the rendered output before any metadata upload or Candy Machine deployment.
