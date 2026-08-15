# Nightly Legendary and Sticker Badge Policy

The supplied `file_0000000046f081fd962fe9210c620f09.png` file is installed unchanged as `assets/backgroundz/Legendary_Nightly.png`. Its public metadata value is **Nightly Legendary**. The `Legendary_` filename prefix is intentional: the compositor excludes it from normal random background selection, so it can only be introduced through the fixed allocator rule below.

| Rule | Final behavior |
| --- | --- |
| **Nightly allocation** | Exactly **one** token in the 444-token release uses the Nightly Legendary background. |
| **Rarity** | That token is explicitly assigned **Legendary Chase**, within the fixed 18-token Legendary Chase tier. |
| **Sticker pairing** | The Nightly Legendary token uses the official **Nightly Wallet** sticker, creating one deliberate, verifiable pairing. |
| **Image fidelity** | The supplied 1254×1254 source file is preserved unchanged in `assets/backgroundz`. During composition it is normalized to the collection’s 1393×1393 canvas through the same standard LANCZOS layer-resize rule applied to every non-native-size trait. |
| **General background pool** | Nightly Legendary never appears in Core, Uncommon, Rare, Mythic, or ordinary Legendary random draws. |

## White-Bordered Square Sticker Badges

All **26 active sticker traits** use the same deterministic badge treatment. Each badge is a **200×200px square** with a **8px solid white border**, a dark Oxford Blue reading surface, and centered source artwork fitted inside a 160px inner area. The square badge is placed in the existing lower-left anchor at x=90, y=1108 on the 1393×1393 transparent sticker canvas.

This treatment adds a consistent border and square silhouette without redrawing, recoloring, or otherwise altering the original logo/sticker artwork. The same source archive is used every time the badge set is regenerated, preventing compound framing on repeated builds. The badge builder excludes the retired **Bake Your Stake**, **Cookiebox Liquidity Hub**, **Hyperlane Bridge**, **Metaplex**, **Morsel Wallet**, **Sesamians**, and **Sweetardio** outputs before writing the active pool.
