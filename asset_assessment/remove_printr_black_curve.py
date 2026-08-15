#!/usr/bin/env python3
"""Remove the isolated black curved arm from the owner-supplied PrintR PNG.

The image-edit model twice returned an opaque checkerboard canvas rather than
usable alpha. This fallback edits only the known isolated curved-arm region of
the original RGBA source and retains the source's genuine transparent canvas.
"""

from collections import deque
from pathlib import Path

from PIL import Image

SOURCE = Path("/home/ubuntu/upload/art_11(30).png")
DESTINATION = Path("/home/ubuntu/cookie-chain-pending-final-review/PrintR_smudges_removed.png")

# Exact disconnected visible-alpha fragments identified by
# analyze_printr_alpha_components.py. Unlike a rectangle mask, this removes
# only the observed detached pixels—including gray/white antialiasing that
# survived the prior dark-only cleanup—while preserving the connected trait.
SEARCH_REGION = (540, 860, 675, 1050)
SMUDGE_COMPONENT_BOUNDS = {
    (589, 922, 590, 923),
    (644, 1001, 645, 1002),
    (649, 999, 650, 1000),
    (623, 896, 631, 901),
    (580, 973, 595, 982),
    (590, 904, 622, 922),
    (592, 972, 652, 995),
}
ALPHA_THRESHOLD = 16


def visible_components(alpha):
    left, top, right, bottom = SEARCH_REGION
    pending = {(x, y) for y in range(top, bottom) for x in range(left, right)
               if alpha.getpixel((x, y)) >= ALPHA_THRESHOLD}
    components = []
    while pending:
        seed = pending.pop()
        queue = deque([seed])
        component = [seed]
        while queue:
            x, y = queue.popleft()
            for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if neighbor in pending:
                    pending.remove(neighbor)
                    queue.append(neighbor)
                    component.append(neighbor)
        xs, ys = zip(*component)
        yield component, (min(xs), min(ys), max(xs) + 1, max(ys) + 1)


def main() -> None:
    image = Image.open(SOURCE).convert("RGBA")
    if image.size != (1393, 1393):
        raise ValueError(f"expected 1393x1393 source, got {image.size}")
    alpha = image.getchannel("A")
    if alpha.getextrema()[0] != 0:
        raise ValueError("source must contain true transparency")

    rgba = image.copy()
    pixels = rgba.load()
    removed, matched = 0, set()
    for component, bounds in visible_components(alpha):
        if bounds not in SMUDGE_COMPONENT_BOUNDS:
            continue
        matched.add(bounds)
        for x, y in component:
            red, green, blue, opacity = pixels[x, y]
            pixels[x, y] = (red, green, blue, 0)
            removed += 1
    if matched != SMUDGE_COMPONENT_BOUNDS:
        raise ValueError(f"missing identified smudge components: {SMUDGE_COMPONENT_BOUNDS - matched}")

    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(DESTINATION)
    result_alpha = rgba.getchannel("A")
    if result_alpha.getextrema()[0] != 0:
        raise ValueError("output lost true transparency")
    print(f"{DESTINATION} ({removed} black smudge pixels removed)")


if __name__ == "__main__":
    main()
