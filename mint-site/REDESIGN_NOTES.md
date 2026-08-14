# Cookie Chain Mint: Critical Redesign Direction

## Audit Findings

The current page uses the correct colors and assets, but it treats nearly every element as a focal point. Multiple glow treatments, animated bulbs, a moving marquee, decorative scanlines, dense all-caps labels, and a permanently cycling featured draw compete with the actual mint decision. The result is visual noise rather than the deliberate arcade-shop atmosphere used by the original Sweetardio.fun landing page.

The composition also relies too heavily on centered panels. It provides little directional flow from collection context to mint action, and several interface elements mimic terminal controls without adding useful information. On mobile, these effects consume valuable space before the primary decision is clear.

## Redesign System

The corrected page will be built as a **curated arcade counter**. It will use one clear hero message, one dominant mint action, and one static featured draw. The original shop-scene background and gold Cookie Chain plaque remain prominent, but their surrounding effects will be restrained.

| Principle | Implementation rule |
| --- | --- |
| **Hierarchy before decoration** | The headline, availability, mint cost, and wallet action are the only hero priorities. Decorative treatment supports them rather than repeating them. |
| **Intentional asymmetry** | A left-aligned editorial hero copy block is paired with a framed token preview and release facts, giving users a clear reading and action path. |
| **One interaction per control** | The featured draw does not auto-rotate. Users select a token deliberately; the mint quantity and wallet controls retain clear, conventional behavior. |
| **Readable arcade language** | Pusia is reserved for display titles, while DM Mono labels are sparing and high contrast. Body copy stays at readable size and line length. |
| **Responsive clarity** | The desktop two-column counter becomes a single ordered story on mobile: availability, plaque, collection message, featured draw, then mint action. |
| **Reduced effects** | No moving ticker, bulb rail, or nonessential panel shine. Motion is limited to direct hover and focus feedback, and it honors reduced-motion settings. |

The technical mint path remains unchanged: wallet connection, Candy Machine retrieval, Candy Guard validation, treasury matching, mint transaction construction, price, maximum transaction quantity, and configuration safety locks are preserved.

## Validation Notes

The corrected desktop composition establishes a deliberate left-to-right reading path: collection identity, price and availability, primary mint action, then the featured finalized draw. The mobile capture preserves the same order and keeps the gold plaque, primary action, and 444-token facts visible before the selected artwork.
