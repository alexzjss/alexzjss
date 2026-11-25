"""Prepare assets/shots/<slug>.jpg: project screenshots cut to the exact slot of the card they go in.

    python3 scripts/shots.py

Each card shows its screenshot in a strip of (card width - 40) x ROW_SHOT_H (see cards.py), so every image is
cropped here to that aspect ratio and saved at 2x, instead of letting the SVG slice-crop an arbitrary picture.
The sources live in the project repos (docs/screenshots...) or are fresh captures of the running app;
set SHOT_SRC to the folder where you cloned them. Edit SHOTS to change a crop: (source, (left, top, right, bottom)).
"""
import os
import sys
from pathlib import Path

from PIL import Image, ImageEnhance

ASSETS = Path(__file__).resolve().parent.parent / "assets" / "shots"
SRC = Path(os.environ.get("SHOT_SRC", Path(__file__).resolve().parents[2]))   # folder holding the cloned project repos
BRIGHTEN = {"virtualjrpg": 1.45}
WIDE, NARROW = 540, 240           # strip widths, = card width - 40 (see cards.py)

# slug: (source image, crop box in source pixels, strip width, strip height)
SHOTS = {
    # constellation view of the curriculum: dark like the card, a lot of color
    "dasiboard": (SRC / "dasiboard-omg/docs/screenshots/disciplinas.png", (200, 300, 1440, 598), WIDE, 130),
    # four times of day of the same meadow
    "engrama": (SRC / "engrama/docs/images/ui-daynight.png", (98, 0, 2302, 450), WIDE, 110),
    # a battle in the running app (GM panel, 3/4 camera): the party, the command menu and an enemy group, 1440x660 capture
    "virtualjrpg": (SRC / "scratch/vj-combat.png", (100, 100, 1200, 605), NARROW, 110),
}

# slug: (list of (phone screenshot, top offset in source px), strip width, strip height, background): phone screens
# side by side, each showing the top of the screen. Constela's are the app running on the web with made-up positions.
PHONES = {
    "constela": ([(SRC / "scratch/constela-1.png", 0), (SRC / "scratch/constela-2.png", 170), (SRC / "scratch/constela-3.png", 0)],
                 WIDE, 130, (13, 28, 22)),
}


def make(slug, src, box, w, h):
    im = Image.open(src).convert("RGB")
    if box:
        im = im.crop(box)
    else:                                           # no box: cover-fit, centered
        k = max(w * 2 / im.width, h * 2 / im.height)
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        l, t = (im.width - w * 2) // 2, (im.height - h * 2) // 2
        im = im.crop((l, t, l + w * 2, t + h * 2))
    im = im.resize((w * 2, h * 2), Image.LANCZOS)
    if slug in BRIGHTEN:                            # dark 3D scenes read better at thumbnail size
        im = ImageEnhance.Brightness(im).enhance(BRIGHTEN[slug])
    out = ASSETS / f"{slug}.jpg"
    im.save(out, quality=82, optimize=True, progressive=True)
    print("wrote", out, f"{out.stat().st_size / 1024:.0f} KB")


def make_phones(slug, screens, w, h, bg, gap=18, radius=10):
    from PIL import ImageDraw
    n = len(screens)
    pw = (w - gap * (n - 1)) // n                                 # each phone is pw x h on screen, drawn at 2x
    canvas = Image.new("RGB", (w * 2, h * 2), bg)
    for i, (path, top) in enumerate(screens):
        im = Image.open(path).convert("RGB")
        k = pw * 2 / im.width
        im = im.resize((pw * 2, round(im.height * k)), Image.LANCZOS).crop((0, round(top * k), pw * 2, round(top * k) + h * 2))
        mask = Image.new("L", im.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius * 2, fill=255)
        canvas.paste(im, (i * (pw + gap) * 2 + (w - n * pw - gap * (n - 1)), 0), mask)
    out = ASSETS / f"{slug}.jpg"
    canvas.save(out, quality=84, optimize=True, progressive=True)
    print("wrote", out, f"{out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    only = sys.argv[1:] or [*SHOTS, *PHONES]
    for slug in only:
        make_phones(slug, *PHONES[slug]) if slug in PHONES else make(slug, *SHOTS[slug])
