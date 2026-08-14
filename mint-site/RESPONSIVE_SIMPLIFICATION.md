# Responsive Content Simplification Contract

The public mint page should answer only four questions: **What is this edition? What does the art look like? What does a mint cost? Can I mint safely now?** Everything else is either removed, condensed into the terminal, or retained only where it is necessary to explain a disabled state.

| Keep on the public page | Condense or remove |
| --- | --- |
| Canonical Cookie Chain Edition plaque and single collection statement | Repeated release strip, hero fact row, and descriptive trait list |
| One selected full-quality artwork with token number and rarity | Multiple featured-art traits and card-name copy outside the selected preview |
| Wallet entry point, price, quantity, and deploy-safe mint terminal | Separate supply/status summaries that repeat terminal information |
| Required deployment, treasury-mismatch, RPC, and receipt messages | Decorative instructions or labels that do not affect a mint decision |

## Breakpoint Rules

| Viewport | Composition |
| --- | --- |
| **≤ 599px** | Header, collection statement, single primary action, selected artwork, then mint terminal. The token deck is a horizontal, labeled selection strip below the artwork. |
| **600–899px** | A compact two-column hero keeps copy and selected artwork in the first screen where available, falling back to a balanced stack on portrait tablet. |
| **≥ 900px** | Editorial two-column hero and a two-column mint section. Line lengths, artwork width, and spacing are capped to avoid a sparse ultra-wide layout. |

The selected artwork is user-controlled only. Motion is limited to purposeful button hover/focus feedback and honors reduced-motion settings.

## Validation Notes

At 320×720, the top viewport presents only the brand, edition statement, primary mint action, and the beginning of the selected artwork; repeated supply and price facts have been removed. At 768×1024 portrait, the intentional stacked composition protects readable text width and artwork scale rather than forcing a compressed two-column layout.

At 1280×800 and 1600×1000, the hero remains bounded by the shared content width, with the collection copy and artwork balanced as two distinct columns. The removal of the fact row, release strip, secondary hero action, feature-trait sentence, and trait register gives the wide layouts a clearer, more professional conversion path without introducing excessive empty space.
