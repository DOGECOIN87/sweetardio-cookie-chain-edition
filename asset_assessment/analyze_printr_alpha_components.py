#!/usr/bin/env python3
"""List detached visible-alpha components near the left side of PrintR."""

import json
from collections import deque
from pathlib import Path

from PIL import Image

SOURCE = Path("/home/ubuntu/upload/art_11(30).png")
REGION = (540, 860, 675, 1050)
ALPHA_THRESHOLD = 16


def main() -> None:
    image = Image.open(SOURCE).convert("RGBA")
    alpha = image.getchannel("A")
    left, top, right, bottom = REGION
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
        components.append({"area": len(component),
                           "bbox": [min(xs), min(ys), max(xs) + 1, max(ys) + 1]})
    components.sort(key=lambda item: (item["area"], item["bbox"]))
    report = {"source": str(SOURCE), "region": list(REGION),
              "alpha_threshold": ALPHA_THRESHOLD, "components": components}
    path = Path("/home/ubuntu/cookie-chain-pending-final-review/printr_alpha_component_report.json")
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
