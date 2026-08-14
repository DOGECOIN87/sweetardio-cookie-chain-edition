# Cookie Chain Edition — Final 444 Release Manifest

This directory records the validated **444-piece Cookie Chain Edition** metadata release generated with seed `871003` from the repository’s authoritative `assets/backgroundz` pool.

The emitted metadata uses the public token naming format `Cookie Chain Edition #001` through `Cookie Chain Edition #444`. The exact rarity allocation is **4 Mythic Chase**, **18 Legendary Chase**, **66 Rare**, **134 Uncommon**, and **222 Core**.

> **Trait correction:** `Cookie Hands` was deliberately removed before this final build. The only limited arm trait is **Cookboy Handheld**. **Morsel** and **Cookiebox** are emitted exclusively as **Sticker** attributes.

The full rendered image payload consists of 444 1393×1393 PNG files and is intentionally kept outside Git because it is approximately 1.5 GB. The committed build inputs, 444 token metadata files, manifest, rarity report, and validation summary allow the image set to be reproduced with:

```bash
python3 asset_assessment/build_side_collection.py \
  --count 444 --seed 871003 --candidates-per-sticker 120 --workers 4 \
  --out /path/to/cookie-chain-edition-444
```

The `VALIDATION.json` report confirms 444 images, 444 metadata files, 444 unique public trait signatures, the exact rarity allocation, the **Cookboy** background label, 22 **Cookboy Handheld** arm occurrences, 40 **Morsel** stickers, 41 **Cookiebox** stickers, and no Cookie Hands arm value.
