#!/usr/bin/env python3
"""Write refreshed catalog and managed mint preview records from upload output."""

import argparse
import json
import re
from pathlib import Path


UPLOAD = re.compile(r"\[SUCCESS\].*?/token-(\d{3})\.png -> (/manus-storage/\S+)")
SPECIAL = {"Nightly Legendary", "Mattrick Legendary", "Shubbi Legendary", "Tenders Legendary"}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", required=True)
    parser.add_argument("--uploads", required=True)
    parser.add_argument("--catalog-out", required=True)
    parser.add_argument("--managed-out", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    selected = json.loads(Path(args.selection).read_text(encoding="utf-8"))["selection"]
    paths = {match.group(1): match.group(2) for match in UPLOAD.finditer(Path(args.uploads).read_text(encoding="utf-8"))}
    tokens = []
    for row in selected:
        token_id = f"{int(row['id']):03d}"
        image = paths.get(token_id)
        if not image:
            raise SystemExit(f"missing managed upload for token {token_id}")
        note = row["background"] if row["background"] in SPECIAL else "Curated draw"
        tokens.append({
            "id": token_id,
            "name": row["name"],
            "image": image,
            "rarity": row["rarity"],
            "sticker": f"{row['sticker']} sticker",
            "note": note,
            "background": row["background"],
            "arms": row["arms"],
        })
    if len(tokens) != 50 or tokens[0]["background"] != "Nightly Legendary":
        raise SystemExit("preview selection must contain 50 records with Nightly Legendary first")
    catalog = Path(args.catalog_out).expanduser().resolve()
    catalog.parent.mkdir(parents=True, exist_ok=True)
    catalog.write_text(json.dumps({"count": len(tokens), "selection": tokens}, indent=2) + "\n", encoding="utf-8")
    managed = Path(args.managed_out).expanduser().resolve()
    managed.parent.mkdir(parents=True, exist_ok=True)
    public_tokens = [{key: value for key, value in token.items() if key not in {"background", "arms"}}
                     for token in tokens]
    managed.write_text(
        "// Generated from the validated Cookie Chain Edition final release; do not hand-edit.\n"
        "export type PreviewToken = { id: string; name: string; image: string; rarity: string; sticker: string; note: string };\n\n"
        f"export const previewTokens: PreviewToken[] = {json.dumps(public_tokens, indent=2)};\n",
        encoding="utf-8",
    )
    print(f"wrote {len(tokens)} refreshed preview records")


if __name__ == "__main__":
    main()
