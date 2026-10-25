# Building the 444 from the Rarity Board

The Rarity Board's **Save configuration** button gives you a script to paste
into a terminal. It clones this branch, writes the board's settings to
`scripts/board.json`, and then:

1. `scripts/build_cookie_chain.py plan --reuse --board scripts/board.json --free sticker,arm,mouth`
   picks the best-looking 444 for those settings from the 2,800 scored
   candidates in `scripts/pool.json` (seconds). Backgrounds, characters,
   footwear, eyes and skins hit the board's counts exactly; stickers, arms and
   mouths follow the best picks.
2. `render --out output` writes `output/images`, `output/metadata` and
   `output/animations` (about 30-40 minutes on 4 cores).
3. `validate --out output` checks the result.

Needs git, Python 3.10+ and about 3 GB free. Paths given to the scripts must
be absolute: they change directory into `compositor/` at startup.

| Path | What it is |
| --- | --- |
| `scripts/` | the build scripts, board defaults and the scored candidate pool |
| `assets/` | the edition's plates, stickers, re-cut footwear and held items |
| `compositor/` | the Sweetardio compositor and figure art, vendored from DOGECOIN87/Sweetardio_Collection |
| `plan.json` | the last selection made (re-written by step 1) |

`images/` and `metadata/` at the top level are the earlier release and are not
touched by the build.
