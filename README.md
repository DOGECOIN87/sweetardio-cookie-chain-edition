# Cookie Chain Edition — 444 Tokens

This repository holds the finished collection: 444 images and their 444 matching
metadata files. Nothing else.

| Folder | Contents |
| --- | --- |
| `images/` | `001.png` … `444.png` — 1393×1393 PNG, ~1.4 GB total |
| `metadata/` | `001.json` … `444.json` — one per image, ~1.8 MB total |

The numbers pair up: `metadata/007.json` describes `images/007.png`.

## How to download

### Option 1 — Download everything as a ZIP (no tools needed)

1. Click the green **Code** button at the top of this page.
2. Choose **Download ZIP**.
3. Unzip the file. You'll get the `images` and `metadata` folders inside.

The download is about 1.4 GB, so give it a few minutes on a normal connection.

### Option 2 — Clone with git (faster, skips old history)

```bash
git clone --depth 1 https://github.com/DOGECOIN87/sweetardio-cookie-chain-edition.git
```

The `--depth 1` part downloads only the current files, not the project's past
versions. Leave it off if you want the full history.

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
    { "trait_type": "Character", "value": "Oatmeal Cream Pie" },
    { "trait_type": "Background", "value": "Picnic Stage" },
    { "trait_type": "Skin", "value": "Black" },
    { "trait_type": "Eyes", "value": "Blue" },
    { "trait_type": "Mouth", "value": "Awkward Smile" },
    { "trait_type": "Footwear", "value": "Bunny Slippers" },
    { "trait_type": "Sticker", "value": "Emyr" },
    { "trait_type": "Edition", "value": "Cookie Chain Edition" },
    { "trait_type": "Rarity", "value": "Core" }
  ]
}
```

The `image` path is relative, so it resolves correctly as long as `images/` and
`metadata/` sit side by side — keep them in the same parent folder.

`Footwear` and `Arms` are optional and appear only on the tokens that have them.
The other trait types are on every token.

## What's in the collection

27 characters, 23 backgrounds, 22 stickers, 3 skins, 10 eyes, 9 mouths,
5 footwear traits and 2 arm traits. Every one of the 444 tokens is a unique
combination.

**Rarity tiers**

| Tier | Count | Share |
| --- | --- | --- |
| Mythic Chase | 4 | 0.90% |
| Legendary Chase | 18 | 4.05% |
| Rare | 66 | 14.86% |
| Uncommon | 134 | 30.18% |
| Core | 222 | 50.00% |

`Rarity` is a curated tier — tokens were ranked on how well the artwork reads,
not purely on how rare their traits are. A trait-frequency ranking will order
the collection differently, which is expected. The scarcest traits to pull are:

- **Four one-of-one backgrounds**, all tiered Legendary Chase:
  Mattrick Legendary (#079), Nightly Legendary (#176),
  Tenders Legendary (#268), Shubbi Legendary (#434)
- **Two arm traits**, 22 tokens each: Cookboy Handheld and Printer
- **Pepe Slippers**, 6 tokens — the thinnest footwear
- **Alien skin**, 37 tokens
