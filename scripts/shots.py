"""Prepare assets/shots/<slug>.(jpg|gif): project screenshots cut to the exact strip of the card they go in.

    python3 scripts/shots.py            # every card
    python3 scripts/shots.py engrama    # just one

Each card shows its picture in a strip of (card width - 40) x ROW_SHOT_H (see cards.py), so every image is cropped here to
that aspect ratio and saved at 2x, instead of letting the SVG slice-crop an arbitrary picture. All sources live in
assets/shots/src/, so this runs anywhere with Pillow; scripts/capture/ has the scripts that took the captures
(running apps, live sites) and says where the rest came from (docs/ of the project repos). Edit SHOTS / PHONES / GIFS
to change a crop: (source, (left, top, right, bottom), strip width, strip height).
sampanav.jpg is the one picture here with no source: it is used as is.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance

ASSETS = Path(__file__).resolve().parent.parent / "assets" / "shots"
SRC = ASSETS / "src"
BRIGHTEN = {"virtualjrpg": 1.45}   # dark 3D scenes read better at thumbnail size
WIDE, NARROW = 540, 240            # strip widths, = card width - 40 (see cards.py)

# slug: (source, crop box in source pixels or None for a centered cover fit, strip width, strip height)
SHOTS = {
    # curriculum constellation, cut on the semester borders (seven full columns)
    "dasiboard": (SRC / "dasiboard.webp", (272, 334, 1327, 607), WIDE, 140),
    # the four times of day of the same meadow
    "engrama": (SRC / "engrama.webp", (98, 0, 2302, 450), WIDE, 110),
    # a battle in the GM panel (3/4 camera) without the nav bar: the party, the command menu, an enemy group
    "virtualjrpg": (SRC / "virtualjrpg.webp", (170, 45, 1128, 660), NARROW, 154),
    # coverage panel of the studio, dark theme
    "jflp": (SRC / "jflp.webp", (0, 0, 1280, 587), NARROW, 110),
    # an offer as the bot posts it (an embed with the same fields as services/discord_sender.py; fictional offer)
    "acha-promocoes": (SRC / "acha-promocoes.webp", None, NARROW, 130),
    "modaloop": (SRC / "modaloop.webp", (0, 0, 1609, 872), NARROW, 130),
    "vat": (SRC / "vat.webp", (0, 27, 1280, 720), NARROW, 130),
    # the Projetos page of the live site (heading, filters, first case study)
    "website": (SRC / "website.webp", (0, 100, 1440, 473), WIDE, 140),
    # hero of the live site: headline and the basket illustration
    "eco-fruta": (SRC / "ecofruta.webp", (700, 90, 1440, 522), NARROW, 140),
}

# slug: (list of (phone screenshot, top offset in source px), strip width, strip height, background): phone screens
# side by side, each showing the top of the screen. Captured from the apps running on the web (made-up demo data).
PHONES = {
    "constela": ([(SRC / "constela-1.webp", 0), (SRC / "constela-2.webp", 170), (SRC / "constela-3.webp", 0)],
                 WIDE, 130, (13, 28, 22)),
    "icndy": ([(SRC / "icndy-setup.webp", 0), (SRC / "icndy-home.webp", 190)], NARROW, 130, (24, 18, 22)),
}

# slug: (frames, crop box, seconds per frame): animated gif cut from the project's own docs images, at their native
# resolution (pixel art: no resampling). 840x240 is the 540x154 strip of the card at 1.55x.
GIFS = {
    "clawdesk": ([SRC / f"clawdesk-{n}.webp" for n in
                  ("trabalhando", "esperando", "feito-erro", "bola", "cavalinho", "filhotes", "descansando", "testes-web")],
                 (0, 62, 840, 302), 1.8),
}


def make(slug, src, box, w, h):
    im = Image.open(src).convert("RGB")
    if box:
        im = im.crop(box)
    else:
        k = max(w * 2 / im.width, h * 2 / im.height)
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        l, t = (im.width - w * 2) // 2, (im.height - h * 2) // 2
        im = im.crop((l, t, l + w * 2, t + h * 2))
    im = im.resize((w * 2, h * 2), Image.LANCZOS)
    if slug in BRIGHTEN:
        im = ImageEnhance.Brightness(im).enhance(BRIGHTEN[slug])
    save(slug, im)


def make_phones(slug, screens, w, h, bg, gap=18, radius=10):
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
    save(slug, canvas)


def make_gif(slug, frames, box, seconds):
    ims = [Image.open(f).convert("RGB").crop(box) for f in frames]
    out = ASSETS / f"{slug}.gif"
    ims[0].save(out, save_all=True, append_images=ims[1:], duration=int(seconds * 1000), loop=0, optimize=True)
    print("wrote", out, f"{out.stat().st_size / 1024:.0f} KB")


def save(slug, im):
    out = ASSETS / f"{slug}.jpg"
    im.save(out, quality=84, optimize=True, progressive=True)
    print("wrote", out, f"{out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    for slug in sys.argv[1:] or [*SHOTS, *PHONES, *GIFS]:
        if slug in GIFS:
            make_gif(slug, *GIFS[slug])
        elif slug in PHONES:
            make_phones(slug, *PHONES[slug])
        else:
            make(slug, *SHOTS[slug])
