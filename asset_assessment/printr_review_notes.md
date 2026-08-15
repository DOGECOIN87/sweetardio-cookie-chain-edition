# PrintR Arms Trait Review Notes

The first generated revision successfully removed the requested black curved arm in the visible prop area. However, its exported checkerboard was baked into the canvas rather than preserved as usable alpha when composited in the review sheet. This output is rejected and will not be used in the collection. A second image-edit pass is required with an explicit true-alpha PNG requirement before the review can continue.

The second generated revision also returned an opaque checkerboard, so it was likewise rejected. The first deterministic true-alpha fallback retained a lower-left remnant of the targeted curved arm. It must be re-masked more tightly before being used in the review sheet.
