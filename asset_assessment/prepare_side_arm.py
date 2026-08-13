#!/usr/bin/env python3
"""Prepare the Cookboy handheld game device as a side-only held-item trait."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (ROOT / "side_collection" / "assets" / "catalog_uploads" /
          "file_000000001e788230bece34d37c0840ab.png")
OUTPUT = ROOT / "side_collection" / "assets" / "armz" / "Cookboy_Handheld.png"
CANVAS = 1393
# Size and placement are matched to the production held-item arms, because the
# compositor gives an arm no per-character fitting: it drops the art onto the
# canvas at a fixed row (arms deliberately do not take CHAR_SCALE, so a weapon
# reads as the same object whoever holds it). Whatever is baked in here is what
# every token gets, so it has to land in the cohort's band on its own.
#
# Measured over the seven compact held-item arms in traits/armz (excluding the
# blade-down Katana and the three whole-figure arms):
#
#   top     median 707    bottom  median 1030    opaque coverage median 0.056
#
# At 650 tall the device carried 2.68x the median arm's opaque area and spanned
# 626-1273: it out-massed every body, reached up into the chin, and hung far
# below the figure's base. Area-matching the cohort gives scale ~0.6.
#
# The exact height is then pinned by ARMED_LIFT, which raises the WHOLE figure
# 70px when the arm overhangs the body's base. That made the old size worse
# than cosmetic: hanging to 1273 cleared every threshold in the cast, so all
# 27 were lifted -- including the ones CLAUDE.md documents as untouched
# because their arm already sits inside their own footprint (the ice creams,
# churro, the Nutty Bar, Twinkie) and og_gummy_bear. A rifle lifts 18 of 27.
#
# Two constraints therefore bracket the art, and 372 satisfies both exactly:
#
#   top    >= ~707   the cohort's median top; higher reaches into the mouth,
#                    since the skin ball's lower edge sits at ~747
#   bottom <= 1078   just under og_gummy_bear's 1078.5 and Twinkie's 1084.0
#                    lift thresholds, so the device lifts the same 18
#                    characters a rifle does
#
# 372 tall lands the art at 707-1077, opaque coverage against the cohort's
# 0.017-0.092 (median 0.056) -- i.e. the same visual mass as the AK15.
#
# CENTER_X is off the face column (~690) on purpose: the device is held in the
# character's LEFT hand, so it reads on the VIEWER'S RIGHT rather than centred
# on the chest. 810 keeps the casing's left edge inboard of the face column, so
# it still overlaps the torso instead of floating off the silhouette, while the
# right edge lands short of the AK15's 993. The narrowest body (Nutty_Bar) ends
# at x=887, so a little overhang there is expected -- the AK15 overhangs that
# same body by ~106px and that is the established look.
TARGET_HEIGHT = 372
CENTER_X = 810
BOTTOM_Y = 1078


def main():
    image = Image.open(SOURCE).convert("RGB")
    # The backdrop is a black-to-gray studio gradient and the device itself is
    # black, so colour-keying destroys the casing. Use a soft silhouette mask
    # around the known product and hand geometry instead.
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((140, 145, 872, 1325), radius=42, fill=255)
    # One hand only. The device is held in the character's LEFT hand, which is
    # the viewer's RIGHT, so the fingers that wrap the casing's right edge are
    # the grip and the source's opposite hand is dropped -- keeping both read
    # as a two-handed hold dead centre, which is not what this trait is.
    draw.ellipse((810, 405, 1008, 1015), fill=255)  # left hand (viewer right)
    mask = mask.filter(ImageFilter.GaussianBlur(2.0))
    cut = image.convert("RGBA")
    cut.putalpha(mask)
    bbox = cut.getchannel("A").getbbox()
    if bbox is None:
        raise SystemExit("game device extraction produced no artwork")
    cut = cut.crop(bbox)
    width = round(cut.width * TARGET_HEIGHT / cut.height)
    cut = cut.resize((width, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    canvas.alpha_composite(cut, (round(CENTER_X - width / 2), BOTTOM_Y - TARGET_HEIGHT))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT)
    print(f"{OUTPUT.relative_to(ROOT)}  bbox={canvas.getchannel('A').getbbox()}")


if __name__ == "__main__":
    main()
