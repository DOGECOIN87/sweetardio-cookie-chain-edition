# Cookie Chain Edition — 444 Tokens

## Start here: which files are the collection

| Folder / file | What it is | Upload for the mint? |
| --- | --- | --- |
| **`images/`** | `001.png` … `444.png`, 1393×1393 PNG | **YES** |
| **`metadata/`** | `001.json` … `444.json`, one per image | **YES** |
| `plan.json` | the build record: exactly how each token was made | no |
| `BUILD.md`, `scripts/`, `assets/`, `compositor/` | the tools that build the collection from the Rarity Board | no |

**Only `images/` and `metadata/` are the collection.**
Everything else is the build kit and must not be uploaded. Always take the
files from the `main` branch; other branches are work in progress.
This build is stills only: no animations.

The numbers pair up: `metadata/007.json` describes `images/007.png`.

Everything needed to rebuild it is in this repository too — see
[Rebuilding the collection](#rebuilding-the-collection). `plan.json` records
the exact layer stack of every token.

## How to download

### Option 1 — Download everything as a ZIP (no tools needed)

1. Click the green **Code** button at the top of this page.
2. Choose **Download ZIP**.
3. Unzip the file. You'll get the `images` and `metadata` folders inside.

### Option 2 — Clone with git (skips old history)

```bash
git clone --depth 1 https://github.com/iamabotama/sweetardio-cookie-chain-edition.git
```

### Option 3 — Grab a single token

Open `images/` or `metadata/` above, click the file you want, then use the
download button on the file page.

## What a metadata file looks like

```json
{
  "name": "Cookie Chain Edition #001",
  "description": "One of 444 Cookie Chain Edition collectibles.",
  "image": "../images/001.png",
  "attributes": [
    {
      "trait_type": "Character",
      "value": "Brownie Bite"
    },
    {
      "trait_type": "Background",
      "value": "Cookie Dough"
    },
    {
      "trait_type": "Skin",
      "value": "White"
    },
    {
      "trait_type": "Eyes",
      "value": "Clueless"
    },
    {
      "trait_type": "Mouth",
      "value": "Diamond Grill"
    },
    {
      "trait_type": "Footwear",
      "value": "Cookie Monster Slippers"
    },
    {
      "trait_type": "Arms",
      "value": "Nerf Blaster"
    },
    {
      "trait_type": "Sticker",
      "value": "Nyancat"
    },
    {
      "trait_type": "Edition",
      "value": "Cookie Chain Edition"
    },
    {
      "trait_type": "Rarity",
      "value": "Common"
    }
  ]
}
```

The `image` path is relative, so it resolves as long as `images/` and
`metadata/` sit side by side.

`Footwear` and `Arms` are optional and appear only on the tokens that have them
(74 and 121 tokens). Every other trait type is on every composited
token. Token #338 is the animated 1/1: finished artwork rather than a
composited character, so it carries `1/1`, `Edition` and `Rarity` only, plus an
`animation_url` pointing at `animations/338.mp4`.

## What's in the collection

27 characters, 25 backgrounds,
22 stickers, 3 skins, 10 eyes,
9 mouths, 5 footwear traits and
12 arm traits. Every token is a unique combination.

**Rarity tiers**

| Tier | Count |
| --- | --- |
| 1/1 | 1 |
| Legendary | 12 |
| Rare | 66 |
| Uncommon | 132 |
| Common | 233 |

**1/1** is exactly the 1 one-of-one tokens:
Cookboy Blue Raspberry (animated) (#338). Every other tier is
labelled by its background's tier, the same tier the background holds on the Rarity Board.

**Weather** (69 tokens) — a still showing the weather, plus a loop

| Weather | Tokens |
| --- | --- |
| Fog | 15 |
| Blizzard | 12 |
| Rain | 11 |
| Flooded | 10 |
| Snow | 9 |
| Storm | 8 |
| Tornado | 4 |

**Arms** (121 tokens)

| Arm | Tokens |
| --- | --- |
| Nerf Blaster | 27 |
| Printer | 24 |
| Cookboy Handheld | 14 |
| Cash | 13 |
| Katana | 12 |
| Military Brat | 10 |
| AR-47 | 9 |
| AK-15 | 5 |
| Dual Uzis | 3 |
| Cyan Saber | 2 |
| Blue Saber | 1 |
| Pink Saber | 1 |

**Footwear** (74 tokens)

| Footwear | Tokens |
| --- | --- |
| Shiba Slippers | 24 |
| Bunny Slippers | 19 |
| Gorbhouse Slippers | 13 |
| Cookie Monster Slippers | 10 |
| Pepe Slippers | 8 |

**Backgrounds**

| Background | Tokens |
| --- | --- |
| Cookie Dough | 59 |
| Cookboy Silver | 58 |
| Liberty Cookie Dime | 58 |
| Moon Surface | 58 |
| Cookboy Black Enamel | 22 |
| Cookboy Chocolate | 22 |
| NFTs Aren't Dead | 22 |
| Picnic Stage | 22 |
| Shubbi | 22 |
| Tenders | 22 |
| Closedgotchi | 6 |
| Cookboy Arcade | 6 |
| Cookboy Gold | 6 |
| Emyr | 6 |
| Fairdevs | 6 |
| GorWeld | 6 |
| Gorbhouse Treasures | 6 |
| M Power | 6 |
| Mattrick | 6 |
| Opengotchi | 6 |
| Yatrah Arcade | 6 |
| Momo Swap Legendary | 3 |
| Nightly Legendary | 3 |
| Short The Banks Legendary | 3 |
| Starfield Legendary | 3 |

**Characters**

| Character | Tokens |
| --- | --- |
| Chocolate Chip Cookie | 34 |
| OG Gummy Bear | 32 |
| Twinkie | 31 |
| S'mores | 25 |
| Rice Crispy Treat | 22 |
| Vanilla Ice Cream | 21 |
| Marshmallow | 20 |
| Sugar Doughnut | 20 |
| Zebra Cake | 19 |
| Glazed Doughnut | 18 |
| Waffle | 18 |
| OG Pop Tart | 15 |
| Sugar Cube | 15 |
| Brownie Bite | 14 |
| Cyan Sherbert Ice Cream | 14 |
| Chocolate Sandwich Cookie | 13 |
| Oatmeal Cream Pie | 13 |
| Ding Dong | 12 |
| Nutty Bar | 12 |
| Chocolate Ice Cream | 11 |
| Churro | 10 |
| Gold Waffle | 10 |
| Neapolitan Ice Cream | 10 |
| Chocolate Doughnut | 9 |
| Cyan Frosted Pop Tart | 9 |
| Chocolate Frosted Pop Tart | 8 |
| Pink Sherbert Ice Cream | 8 |

**Stickers** — one on every token

| Sticker | Tokens |
| --- | --- |
| Real as a Doughnut | 28 |
| Nightly Wallet | 26 |
| CookieScan | 24 |
| Candy Shop | 23 |
| Cookboy | 23 |
| Morsel | 23 |
| Shorts Doggo | 23 |
| Emyr | 22 |
| Baked Bazaar | 21 |
| Cookie Chat | 21 |
| Cookie MCP | 21 |
| L | 21 |
| CookOven | 20 |
| Cookie Quads | 20 |
| CookieSwap | 19 |
| CookBook | 18 |
| Cookiebox | 17 |
| Nyancat | 17 |
| Cookie Lock | 16 |
| MomoSwap | 16 |
| Out of Order | 15 |
| Chibi Monster | 9 |

## Rebuilding the collection

Everything the build needs is in this repository:

| Path | What it is |
| --- | --- |
| `scripts/` | the build scripts |
| `assets/` | the edition's plates, stickers (+ sources), re-cut footwear, two held items and plaque |
| `compositor/` | the Sweetardio compositor and figure art it draws from (vendored; see its README) |
| `plan.json` | the curated 444: every token's exact layer stack, traits and rarity |

Requirements: Python 3.10+ and `pip install -r requirements.txt` (Pillow,
NumPy, SciPy). About 2 GB of free disk for the output.

```bash
python3 scripts/build_cookie_chain.py render   --out output   # writes output/images + output/metadata (~6 min on 4 cores)
python3 scripts/build_cookie_chain.py validate --out output   # checks pairing, counts, uniqueness, name bytes
```

`render` reads only `plan.json`, so it reproduces this exact collection. It
goes to `output/`, which git ignores, so a rebuild can never overwrite the
collection at the top level by accident. Add `--no-animations` for a
stills-only build, as this one is.
`--workers N` sets the number of parallel renders (default 4).

Optional steps:

```bash
python3 scripts/build_cookie_chain.py sheet            # the 50-token preview sheet -> work/approval_sheet_50.jpg
python3 scripts/prepare_assets.py --sheet work/s.png   # rebuild the 22 stickers + plaque from assets/sticker_sources
python3 scripts/prepare_footwear.py --sheet work/f.jpg # re-cut the footwear outlines from compositor/traits
python3 scripts/build_cookie_chain.py plan             # re-curate from scratch: new pool, scores, selection (~1.5 h)
python3 scripts/build_cookie_chain.py plan --extend 1100   # add candidates aimed at the best pairings, re-select
```

Re-running `plan` writes a NEW `plan.json` — a different 444. Commit it only
if that is the intent.
