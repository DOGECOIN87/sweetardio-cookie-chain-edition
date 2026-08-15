# Cookie Chain Dapp Logo Sticker Policy

The Cookie Chain dapp-logo stickers are derived from the official public Apps Registry manifest, not redrawn or recreated. Each output preserves the source logo’s visual identity, retains alpha where supplied, and is resized with deterministic high-quality resampling into the existing **1393×1393** transparent sticker canvas.

## Placement and Rendering

| Property | Rule |
| --- | --- |
| Source | Official `cookiechain/apps` `apps.json` logo URL recorded in `cookiechain_dapp_logo_manifest.json`. |
| Output directory | `assets/stickerz/`, alongside the existing Cookie Chain sticker traits. |
| Canvas | 1393×1393 transparent RGBA, matching every existing sticker asset. |
| Footprint | Maximum 200px on the longest side. |
| Placement | Horizontal center `x=190`; lower edge `y=1308`, matching the existing Morsel/Cookiebox sticker anchor. |
| Visual treatment | No recoloring, redrawing, added text, or semantic editing. Fully transparent edges are retained; only simple transparent-margin cropping and resizing are applied. |
| Public trait type | `Sticker`. |

## Public Trait Names and Files

| Registry project | Output file | Public metadata value |
| --- | --- | --- |
| CookieScan | `CookieScan.png` | CookieScan |
| Hyperlane Bridge | `Hyperlane_Bridge.png` | Hyperlane Bridge |
| Nightly Wallet | `Nightly_Wallet.png` | Nightly Wallet |
| DefiLlama | `DefiLlama.png` | DefiLlama |
| Bake Your Stake | `Bake_Your_Stake.png` | Bake Your Stake |
| CookieSwap | `CookieSwap.png` | CookieSwap |
| Candy Shop | `Candy_Shop.png` | Candy Shop |
| Metaplex | `Metaplex.png` | Metaplex |
| Cookie Quads | `Cookie_Quads.png` | Cookie Quads |
| Cookiebox | `Cookiebox_Liquidity_Hub.png` | Cookiebox Liquidity Hub |
| CookieScan DAS API | `CookieScan_DAS_API.png` | CookieScan DAS API |
| MomoSwap | `MomoSwap.png` | MomoSwap |
| Morsel Wallet | `Morsel_Wallet.png` | Morsel Wallet |
| CookOven | `CookOven.png` | CookOven |
| CookBook | `CookBook.png` | CookBook |
| Cookie Lock | `Cookie_Lock.png` | Cookie Lock |
| Cookie Chat | `Cookie_Chat.png` | Cookie Chat |
| GORBOY | `GORBOY.png` | GORBOY |
| Sesamians | `Sesamians.png` | Sesamians |
| Baked Bazaar | `Baked_Bazaar.png` | Baked Bazaar |
| GorWeld | `GorWeld.png` | GorWeld |
| Cookie MCP | `Cookie_MCP.png` | Cookie MCP |

The existing **Morsel** and **Cookiebox** sticker traits remain in the pool; the dapp-logo traits are explicitly named **Morsel Wallet** and **Cookiebox Liquidity Hub** to avoid ambiguous public metadata.

## Source Review

The 22 public source assets were reviewed in `catalog/cookiechain_dapp_logo_sources.png` on a checkerboard. Several registry assets intentionally include an opaque square or colored brand plate; these are retained as part of the supplied public logo rather than removed or redrawn. Transparent source artwork remains transparent. This policy preserves official identity without reconstructing any logo.

The normalized review sheet at `catalog/cookiechain_dapp_logo_stickers.png` confirms that all 22 logos fit inside the intended lower-left 200px footprint without clipping. Wide project wordmarks such as CookOven, CookBook, and Cookie Lock remain in their official horizontal form rather than being redrawn into an invented icon.

The live mint preview also now uses regenerated final artwork in its Draw aisle. Token `#003` visibly renders the official GORBOY sticker within the collection composition and identifies it as `GORBOY sticker`; the selector additionally exposes examples carrying Cookie MCP, Nightly Wallet, CookieScan, and CookieSwap stickers.

## Rarity Integration

The collection builder distributes 444 selected tokens as evenly as possible across every file in `assets/stickerz`. After adding 22 dapp-logo files to the existing 11 sticker files, the 33-sticker pool assigns **13 or 14** tokens to each sticker, exactly 444 total. The established edition rarity tiers, 22-count Cookboy Handheld quota, and Sugar Doughnut/Gorbhouse guard remain unchanged.
