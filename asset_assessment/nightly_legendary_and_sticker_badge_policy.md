# Nightly Legendary and Original-Style Sticker Policy

The supplied `file_0000000046f081fd962fe9210c620f09.png` file is installed unchanged as `assets/backgroundz/Legendary_Nightly.png`. Its public metadata value is **Nightly Legendary**. The `Legendary_` filename prefix is intentional: the compositor excludes it from normal random background selection, so it can only be introduced through the fixed allocator rule below.

| Rule | Final behavior |
| --- | --- |
| **Nightly allocation** | Exactly **one** token in the 444-token release uses the Nightly Legendary background. |
| **Rarity** | That token is explicitly assigned **Legendary Chase**, within the fixed 18-token Legendary Chase tier. |
| **Sticker pairing** | The Nightly Legendary token uses the official **Nightly Wallet** sticker, creating one deliberate, verifiable pairing. |
| **Image fidelity** | The supplied 1254×1254 source file is preserved unchanged in `assets/backgroundz`. During composition it is normalized to the collection’s 1393×1393 canvas through the same standard LANCZOS layer-resize rule applied to every non-native-size trait. |
| **General background pool** | Nightly Legendary never appears in Core, Uncommon, Rare, Mythic, or ordinary Legendary random draws. |

## Original-Style Sticker Overlays

All **26 active sticker traits** use the original Sweetardio Collection overlay treatment. The retained legacy sticker files preserve their authored transparent silhouettes and placement unchanged. Official Cookie Chain dapp logos retain their individual alpha silhouettes, fit within the original 200px lower-left footprint (center x=190, bottom y=1308), and are placed on a 1393×1393 transparent canvas without a border, square background, fill, or redrawn geometry.

The same source archive is used every time the overlay set is regenerated, preventing accidental style drift. The overlay builder excludes the retired **Bake Your Stake**, **Cookiebox Liquidity Hub**, **Hyperlane Bridge**, **Metaplex**, **Morsel Wallet**, **Sesamians**, and **Sweetardio** outputs before writing the active pool.
