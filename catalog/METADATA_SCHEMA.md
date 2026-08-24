# Cookie Chain Edition — Public Metadata Vocabulary

Every generated token uses the public name format `Cookie Chain Edition #001` through `Cookie Chain Edition #444`. Metadata attributes use a stable display order: **Character**, **Background**, **Skin**, **Eyes**, **Mouth**, **Footwear**, **Arms**, **Sticker**, **Edition**, and **Rarity**.

| Trait type | Public values or policy |
| --- | --- |
| Background | `Gold_Cookie_Emboss.png` is displayed as **Cookboy Gold**. Its colour-family companions are displayed as **Cookboy Chocolate**, **Cookboy Black Enamel**, and **Cookboy Silver**. Other backgrounds use their readable asset names. |
| Footwear | Optional; present on 107 of 444 tokens. Absent tokens omit the attribute rather than emitting a placeholder value. |
| Arms | Optional, and limited: **Cookboy Handheld** and **Printer** appear 22 times each and nowhere else. Printer never lands on a gummy-bear character. |
| Sticker | Exactly one of the 22 curated stickers per token. Values come from the sticker filename, with **L**, **Real as a Doughnut**, **Nyancat**, **Cookboy**, and **Out of Order** supplied by the display-name overrides. |
| Edition | Always **Cookie Chain Edition**. |
| Rarity | Exactly **Mythic Chase**, **Legendary Chase**, **Rare**, **Uncommon**, or **Core**. This is a curated tier rather than a trait-frequency score; `edition_444_release/RARITY.md` explains how it is assigned and publishes the counts needed to compute frequency rarity. |

Asset filenames are retained for compositor stability; these public labels are applied only to emitted metadata.
