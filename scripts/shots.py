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
HALF, THIRD = 390, 240             # strip widths, = card width - 40 (see cards.py): two cards a row (430) or three (280)
TALL, SHORT = 160, 130             # strip heights of the two-card rows and of the three-card row

# slug: (source, crop box in source pixels or None for a centered cover fit, strip width, strip height)
SHOTS = {
    # curriculum constellation, cut on the semester borders (seven full columns)
    "dasiboard": (SRC / "dasiboard.webp", (272, 334, 1327, 607), HALF, TALL),
    # the four times of day of the same meadow
    "engrama": (SRC / "engrama.webp", (98, 0, 2302, 450), HALF, TALL),
    # a battle in the GM panel (3/4 camera) without the nav bar: the party, the command menu, an enemy group
    "virtualjrpg": (SRC / "virtualjrpg.webp", (170, 45, 1128, 660), HALF, TALL),
    # coverage panel of the studio, dark theme
    "jflp": (SRC / "jflp.webp", (0, 0, 1280, 587), THIRD, SHORT),
    # an offer as the bot posts it (an embed with the same fields as services/discord_sender.py; fictional offer)
    "acha-promocoes": (SRC / "acha-promocoes.webp", None, THIRD, SHORT),
    "modaloop": (SRC / "modaloop.webp", (0, 0, 1609, 872), HALF, TALL),
    "vat": (SRC / "vat.webp", (0, 27, 1280, 720), HALF, TALL),
    # the Projetos page of the live site (heading, filters, first case study)
    "website": (SRC / "website.webp", (0, 100, 1440, 473), THIRD, SHORT),
    # hero of the live site: headline and the basket illustration
    "eco-fruta": (SRC / "ecofruta.webp", (100, 150, 1310, 646), HALF, TALL),
}

# slug: (list of (phone screenshot, top offset in source px), strip width, strip height, background): phone screens
# side by side, each showing the top of the screen. Captured from the apps running on the web (made-up demo data).
PHONES = {
    "constela": ([(SRC / "constela-1.webp", 0), (SRC / "constela-2.webp", 170), (SRC / "constela-3.webp", 0)],
                 HALF, TALL, (13, 28, 22)),
    "icndy": ([(SRC / "icndy-setup.webp", 0), (SRC / "icndy-home.webp", 190)], HALF, TALL, (24, 18, 22)),
}

# slug: (frames, crop box, seconds per frame): animated gif cut from the project's own docs images, at their native
# resolution (pixel art: no resampling), re-fitted to the strip's aspect ratio.
GIFS = {
    "clawdesk": ([SRC / f"clawdesk-{n}.webp" for n in
                  ("trabalhando", "esperando", "feito-erro", "bola", "cavalinho", "filhotes", "descansando", "testes-web")],
                 (78, 20, 761, 300), 1.8, (HALF, TALL)),
}


def fit_box(box, w, h, size):
    """Re-shape a crop box to the aspect ratio w:h, keeping its centre and as much of it as the source allows."""
    l, t, r, b = box
    bw, bh, r_ = r - l, b - t, w / h
    nw, nh = (bw, bw / r_) if bw / bh > r_ else (bh * r_, bh)
    k = min(1, size[0] / nw, size[1] / nh)                      # shrink when the grown box would leave the source
    nw, nh = nw * k, nh * k
    cx, cy = (l + r) / 2, (t + b) / 2
    x0 = min(max(cx - nw / 2, 0), size[0] - nw)
    y0 = min(max(cy - nh / 2, 0), size[1] - nh)
    return (round(x0), round(y0), round(x0 + nw), round(y0 + nh))


def make(slug, src, box, w, h):
    im = Image.open(src).convert("RGB")
    if box:
        im = im.crop(fit_box(box, w, h, im.size))
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


def make_gif(slug, frames, box, seconds, strip):
    box = fit_box(box, *strip, Image.open(frames[0]).size)
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
