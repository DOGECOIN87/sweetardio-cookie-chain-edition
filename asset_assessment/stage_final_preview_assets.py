#!/usr/bin/env python3
"""Copy selected final-release previews into the managed static-asset staging area."""

import argparse
import json
import shutil
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", required=True)
    parser.add_argument("--release", required=True)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    selection = json.loads(Path(args.selection).read_text(encoding="utf-8"))["selection"]
    release = Path(args.release).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for row in selection:
        number = int(row["id"])
        source = release / "images" / f"{number:03d}.png"
        target = out / f"token-{number:03d}.png"
        if not source.is_file():
            raise SystemExit(f"missing selected token image: {source}")
        shutil.copy2(source, target)
    (out / "selection.json").write_text(json.dumps({"count": len(selection), "selection": selection}, indent=2) + "\n")
    print(f"staged {len(selection)} final preview images -> {out}")


if __name__ == "__main__":
    main()
