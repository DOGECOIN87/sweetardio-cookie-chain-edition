#!/usr/bin/env python3
"""Download the official public Cookie Chain dapp logos listed in a manifest."""

import argparse
import hashlib
import json
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="Registry-derived JSON manifest")
    parser.add_argument("--out", required=True, help="Directory for unmodified source images")
    return parser.parse_args()


def main():
    args = parse_args()
    manifest_path = Path(args.manifest).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        raise SystemExit("manifest must contain a non-empty entries array")
    out.mkdir(parents=True, exist_ok=True)
    receipts = []
    for entry in entries:
        slug = entry.get("slug")
        url = entry.get("logo")
        if not isinstance(slug, str) or not isinstance(url, str):
            raise SystemExit("manifest entry is missing slug or logo")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        payload = response.content
        try:
            image = Image.open(BytesIO(payload))
            image.verify()
            image = Image.open(BytesIO(payload))
            width, height = image.size
            mode = image.mode
        except Exception as error:
            raise SystemExit(f"{slug}: downloaded asset is not a readable image: {error}")
        suffix = ".png" if "png" in response.headers.get("content-type", "").lower() else ".img"
        target = out / f"{slug}{suffix}"
        target.write_bytes(payload)
        receipts.append({
            "slug": slug,
            "title": entry.get("title", slug),
            "url": url,
            "file": target.name,
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
            "width": width,
            "height": height,
            "mode": mode,
        })
        print(f"downloaded {slug}: {width}x{height} {mode}")
    (out / "SOURCES.json").write_text(json.dumps(receipts, indent=2) + "\n", encoding="utf-8")
    print(f"saved {len(receipts)} official source logos to {out}")


if __name__ == "__main__":
    main()
