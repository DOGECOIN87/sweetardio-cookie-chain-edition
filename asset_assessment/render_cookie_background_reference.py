#!/usr/bin/env python3
"""Render a labelled, read-only reference sheet from Cookie Edition background sources."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets" / "backgroundz"
OUTPUT = ROOT / "catalog" / "backgroundz_authoritative_reference_sheet.png"
CELL = 296
LABEL_H = 44
COLUMNS = 5


def font(size: int, bold: bool = False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(Path("/usr/share/fonts/truetype/dejavu") / name, size)


def label(path: Path) -> str:
    return path.stem.replace("_", " ")


def main() -> None:
    plates = sorted(SOURCE.glob("*.png"))
    if not plates:
        raise SystemExit(f"no PNG backgrounds found in {SOURCE}")
    rows = (len(plates) + COLUMNS - 1) // COLUMNS
    sheet = Image.new("RGB", (COLUMNS * CELL, 42 + rows * (CELL + LABEL_H)), (16, 16, 20))
    draw = ImageDraw.Draw(sheet)
    draw.text((12, 12), "Cookie Chain Edition — Authoritative Background Sources · no post-processing", font=font(17, bold=True), fill=(246, 206, 86))
    caption = font(12, bold=True)

    for index, path in enumerate(plates):
        image = Image.open(path).convert("RGB")
        image.thumbnail((CELL, CELL), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (CELL, CELL), (5, 9, 26))
        tile.paste(image, ((CELL - image.width) // 2, (CELL - image.height) // 2))
        x = (index % COLUMNS) * CELL
        y = 42 + (index // COLUMNS) * (CELL + LABEL_H)
        sheet.paste(tile, (x, y))
        draw.text((x + 8, y + CELL + 12), label(path), font=caption, fill=(240, 240, 245))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUTPUT, optimize=True)
    print(f"{len(plates)} authoritative Cookie Edition backgrounds -> {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
