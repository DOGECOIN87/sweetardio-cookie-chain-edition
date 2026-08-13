#!/usr/bin/env python3
"""Prepare the Cookboy handheld game device as a side-only held-item trait."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage


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
# CENTER_X is off the face column on purpose: the device is held in the
# character's LEFT hand, so it sits on the RIGHT SIDE of the character rather
# than centred on the chest.
#
# What matters is the casing's LEFT edge, not its centre. The character's
# centreline is the face column at ~690, so anything reaching left of that
# straddles the middle and still reads as a two-handed chest hold however far
# the centre is nudged -- at CENTER_X 810 the left edge was 672, still 18px
# across the centreline. 845 puts the left edge at ~708, wholly outboard of the
# centreline, so the device occupies the character's right half.
#
# The narrowest body (Nutty_Bar) ends at x=887, so some overhang is expected --
# the AK15 overhangs that same body by ~106px and that is the established look.
#
# Both values are then pushed as far up and right as the render allows. Swept
# together against the whole cast, three things fail at different points and
# they are what set the limit:
#
#   eyes    clean to dy -45; by -55 the casing starts clipping eye pixels,
#           because the device does overlap the ball horizontally
#   mouth   needs the rightward shift, not the height: at dx +30 the mouth
#           still clips, at +60 it is clear at every height tried
#   lift    bottom must stay above chocolate_frosted_poptart's 1008 threshold
#           or the ARMED_LIFT set drops from 18 to 17
#
# dy -45 / dx +60 is the furthest point where all three hold, giving 661-1032
# vertically and 768-1042 across. Past dx +60 on-body coverage falls away
# (56% median at +90) and the device starts to float off the narrow bodies.
TARGET_HEIGHT = 372
CENTER_X = 905
BOTTOM_Y = 1033


def luma(image):
    return (np.asarray(image, dtype=np.float32)
            @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32))


def hand_mask(image):
    """The gripping hand: three fingers wrapping the right edge, plus the thumb.

    It is ONE hand, not two. The sphere on the casing's left is the thumb of
    the same hand coming round the front while the fingers wrap the back, which
    is why it sits in front of the left bezel. Reading it as a second hand and
    dropping it costs the grip its thumb and leaves the fingers holding the
    device against nothing.

    Cut on EDGE DENSITY, not on brightness. Brightness looks like the obvious
    key -- the spheres are white -- but the studio backdrop immediately right
    of the casing is itself a bright grey ramp, so a luma threshold swallows it
    and lays a grey slab behind the fingers. The spheres do have a hard outline
    against that ramp, and the backdrop is smooth everywhere else, so gradient
    magnitude separates them cleanly where luminance cannot.
    """
    blurred = ndimage.gaussian_filter(luma(image), 1.2)
    gy, gx = np.gradient(blurred)
    magnitude = np.hypot(gx, gy)
    solid = magnitude > np.percentile(magnitude, 90)
    solid = ndimage.binary_fill_holes(
        ndimage.binary_closing(solid, structure=np.ones((13, 13))))
    solid = ndimage.binary_opening(solid, structure=np.ones((7, 7)))
    labels, count = ndimage.label(solid)
    if count == 0:
        raise SystemExit("no subject found in the source")
    sizes = ndimage.sum(solid, labels, range(1, count + 1))
    keep = labels == (int(np.argmax(sizes)) + 1)
    return Image.fromarray((keep * 255).astype(np.uint8), mode="L")


def main():
    image = Image.open(SOURCE).convert("RGB")
    # The backdrop is a black-to-gray studio gradient and the device itself is
    # black, so colour-keying destroys the casing. The casing is a hard-edged
    # rectangle, so mask it as one: it spans x 140-871 at every finger-free
    # height, and y 148-1322.
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((140, 145, 872, 1325), radius=42, fill=255)
    # Then the whole gripping hand -- three fingers round the right edge and
    # the thumb on the left. The device is held in the character's LEFT hand,
    # so it reads on the viewer's right.
    #
    # The fingers are NOT an ellipse and must not be masked with one. An
    # ellipse tapers towards its top and bottom, and the three spheres are
    # stacked down a column, so the outer two fell where the shape had almost
    # no width: the old (810,405,1008,1015) ellipse spanned only x 859-961 at
    # y=450 where the finger reaches 973, and was effectively zero-width at the
    # top sphere. Both end spheres came out sliced down the middle into flat
    # half-domes. hand_mask() cuts their real contour instead.
    mask.paste(255, (0, 0), hand_mask(image))
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
