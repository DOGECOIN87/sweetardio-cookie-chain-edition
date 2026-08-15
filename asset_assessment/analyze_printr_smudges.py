#!/usr/bin/env python3
"""List disconnected dark-alpha components in the left-lower PrintR area."""

import json
from collections import deque
from pathlib import Path

from PIL import Image

SOURCE = Path("/home/ubuntu/upload/art_11(30).png")
# Restrict analysis to the reported left-side artifact zone. The printer body
# and gloves extend beyond this box, allowing small detached marks to be
# identified without manipulating any connected artwork.
REGION = (540, 860, 675, 1050)


def is_dark(pixel) -> bool:
    red, green, blue, opacity = pixel
    return opacity >= 96 and red <= 95 and green <= 95 and blue <= 95


def main() -> None:
    image = Image.open(SOURCE).convert("RGBA")
    pixels = image.load()
    left, top, right, bottom = REGION
    dark = {(x, y) for y in range(top, bottom) for x in range(left, right)
            if is_dark(pixels[x, y])}
    components = []
    while dark:
        seed = dark.pop()
        queue = deque([seed])
        component = [seed]
        while queue:
            x, y = queue.popleft()
            for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if neighbor in dark:
                    dark.remove(neighbor)
                    queue.append(neighbor)
                    component.append(neighbor)
        xs, ys = zip(*component)
        components.append({
            "area": len(component),
            "bbox": [min(xs), min(ys), max(xs) + 1, max(ys) + 1],
        })
    components.sort(key=lambda item: (item["area"], item["bbox"]))
    report = {"source": str(SOURCE), "region": list(REGION), "components": components}
    path = Path("/home/ubuntu/cookie-chain-pending-final-review/printr_dark_component_report.json")
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
