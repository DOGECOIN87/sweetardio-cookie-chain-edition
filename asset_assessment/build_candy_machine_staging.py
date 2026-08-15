#!/usr/bin/env python3
"""Create zero-indexed Sugar/Candy Machine assets from a validated release."""

import argparse
import json
import shutil
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--count", type=int, default=444)
    return parser.parse_args()


def main():
    args = parse_args()
    release = Path(args.release).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    image_dir, metadata_dir = release / "images", release / "metadata"
    if not (release / "VALIDATION.json").is_file():
        raise SystemExit("release must be validated before staging deployment assets")
    report = json.loads((release / "VALIDATION.json").read_text(encoding="utf-8"))
    if report.get("issues"):
        raise SystemExit("release validation contains issues")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for index in range(args.count):
        token_number = index + 1
        source_image = image_dir / f"{token_number:03d}.png"
        source_metadata = metadata_dir / f"{token_number:03d}.json"
        if not source_image.is_file() or not source_metadata.is_file():
            raise SystemExit(f"missing source pair for token {token_number:03d}")
        shutil.copy2(source_image, out / f"{index}.png")
        token = json.loads(source_metadata.read_text(encoding="utf-8"))
        token.pop("selection_score", None)
        token.pop("seed", None)
        token["image"] = f"{index}.png"
        token["properties"] = {
            "files": [{"uri": f"{index}.png", "type": "image/png"}],
            "category": "image",
        }
        (out / f"{index}.json").write_text(json.dumps(token, indent=2) + "\n", encoding="utf-8")
    print(f"staged {args.count} zero-indexed Candy Machine pairs -> {out}")


if __name__ == "__main__":
    main()
