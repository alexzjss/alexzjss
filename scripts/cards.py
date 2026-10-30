"""Generate assets/card-*.svg, the bento project cards of the README.

    python3 scripts/cards.py

Tech icons come from assets/icons/<name>.svg (downloaded from skillicons.dev, e.g.
`curl -o assets/icons/py.svg "https://skillicons.dev/icons?i=py"`) and are embedded as data URIs,
because an SVG loaded through <img> cannot reference external images.
Edit PROJECTS to add, remove or recolor a card.
"""
import base64
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

H = 220
NARROW, WIDE = 280, 580   # 2 * NARROW + 20 gap = WIDE, so rows of 3 and 1+1 line up
ICON, GAP = 28, 6
M = 10                    # transparent margin baked into each SVG: the 20px gutter is exact, whatever the page width

# slug: (tag, title, description, icons, extra chips, accent, width)
PROJECTS = {
    "dasiboard": (
        "★ FLAGSHIP · 700+ STUDENTS", "DaSIboard",
        "All-in-one academic workspace for USP Information Systems students: kanban, grades & attendance, "
        "calendar, study rooms and a curriculum flowchart. 500+ commits, built with a team.",
        ["ts", "react", "vite", "nodejs", "supabase", "postgres", "vercel", "vitest"],
        "Serverless API · Google OAuth · Web Push", "#39d0f0", WIDE),
    "sampanav": (
        "★ FLAGSHIP", "SampaNav",
        "São Paulo routes that trade travel time against recorded crime exposure (SSP-SP).",
        ["py", "fastapi", "js", "docker", "githubactions", "vercel"],
        "igraph · H3 · OSMnx · MapLibre", "#f2b530", NARROW),
    "jflp": (
        "◆ RESEARCH", "JFLP Studio",
        "Spectrum-Based Fault Localization on Defects4J and Bugs.jar, with a resumable run queue.",
        ["py", "fastapi", "java", "maven", "sqlite", "git"],
        "Jaguar 2 · JaCoCo · htmx", "#5fd38d", NARROW),
    "modaloop": (
        "▸ WEB", "ModaLoop",
        "Map of collection points for used clothing, with a disposal guide and environmental info.",
        ["react", "ts", "vite", "css"],
        "Geolocation · CSS Modules", "#b392f0", NARROW),
    "vat": (
        "▸ GAME", "vat",
        "JRPG prototype with real-time ATB combat, elemental reactions, bosses and a bestiary.",
        ["godot"],
        "typed GDScript · GUT", "#f778ba", NARROW),
    "icndy": (
        "▸ MOBILE", "ICNDY",
        "Offline-first Android app for timing the Cindy CrossFit workout, with PR pace and charts.",
        ["ts", "react", "sqlite", "vitest", "githubactions"],
        "Expo · React Native · EAS", "#ff7b72", NARROW),
    "website": (
        "▸ WEB", "website",
        "Bilingual (PT/EN) static portfolio: experience timeline, project filters, research and résumé, with light/dark design tokens.",
        ["react", "ts", "vite", "css", "vercel"],
        "PT/EN · SPA · design tokens", "#79c0ff", NARROW),
    "eco-fruta": (
        "▸ WEB", "eco-fruta",
        "Virtual organic market in PT-BR: fruit, vegetable and greens catalog, producer profiles, cart and Mercado Pago checkout.",
        ["nextjs", "react", "ts", "tailwind", "vercel"],
        "Zustand · Mercado Pago · Next.js 14", "#a5d86e", NARROW),
}

# README rows, left to right. The outer edge of each row has its margin cropped away so the
# grid lines up with the 880px section bars; widths below are printed as the <img> percentages.
LAYOUT = [["dasiboard", "sampanav"], ["jflp", "modaloop", "vat"], ["icndy", "website", "eco-fruta"]]

_cache = {}


def icon_uri(name):
    if name not in _cache:
        data = (OUT / "icons" / f"{name}.svg").read_bytes()
        _cache[name] = "data:image/svg+xml;base64," + base64.b64encode(data).decode()
    return _cache[name]


def tint(hex_color, k=0.10):
    """Dark card background: the accent mixed into the page background."""
    base = (13, 17, 23)
    rgb = [int(hex_color[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(b + (c - b) * k):02x}" for b, c in zip(base, rgb))


def build(tag, title, desc, icons, chips, accent, w, crop_l=False, crop_r=False):
    cols = 82 if w == WIDE else 38
    lines = textwrap.wrap(desc, cols)
    text = "".join(
        f'<text x="20" y="{86 + i * 18}" class="d">{escape(l)}</text>' for i, l in enumerate(lines))
    imgs = "".join(
        f'<image x="{20 + i * (ICON + GAP)}" y="148" width="{ICON}" height="{ICON}" href="{icon_uri(n)}"/>'
        for i, n in enumerate(icons))
    chip = f'<text x="20" y="206" class="c">{escape(chips)}</text>' if chips else ""
    x0 = M if crop_l else 0
    vw = w + 2 * M - x0 - (M if crop_r else 0)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="{x0} 0 {vw} {H + 2 * M}" width="{vw}" height="{H + 2 * M}" role="img" aria-label="{escape(title)}: {escape(desc)}">
<style>
text{{font-family:-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}}
.t{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11px;font-weight:600;letter-spacing:.08em;fill:{accent}}}
.h{{font-size:21px;font-weight:700;fill:#e6edf3}}
.d{{font-size:13px;fill:#b1bac4}}
.c{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11.5px;fill:{accent}}}
</style>
<g transform="translate({M} {M})">
<rect x="0.5" y="0.5" width="{w - 1}" height="{H - 1}" rx="12" fill="{tint(accent)}" stroke="{accent}" stroke-opacity=".7"/>
<text x="20" y="32" class="t">{escape(tag)}</text>
<text x="20" y="60" class="h">{escape(title)}</text>
{text}{imgs}{chip}
</g>
</svg>
'''


def legend():
    """One-line key for the tag symbols, placed above the grid."""
    items = [("★", "#ffb000", "flagship"), ("◆", "#5fd38d", "research"), ("▸", "#8b949e", "side builds")]
    x, parts = 0, []
    for sym, color, label in items:
        parts.append(f'<text x="{x}" y="17"><tspan fill="{color}">{sym}</tspan><tspan fill="#8b949e"> {label}</tspan></text>')
        x += 40 + len(label) * 7.8
    w = round(x - 22)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 24" width="{w}" height="24" role="img" aria-label="Legend: flagship, research, side builds">
<style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13px}}</style>
{"".join(parts)}
</svg>
'''


if __name__ == "__main__":
    (OUT / "legend-projects.svg").write_text(legend(), encoding="utf-8")
    for row in LAYOUT:
        for i, slug in enumerate(row):
            spec = PROJECTS[slug]
            path = OUT / f"card-{slug}.svg"
            path.write_text(build(*spec, crop_l=i == 0, crop_r=i == len(row) - 1), encoding="utf-8")
            total = sum(PROJECTS[x][-1] + 2 * M for x in row) - 2 * M
            vw = spec[-1] + 2 * M - (M if i == 0 else 0) - (M if i == len(row) - 1 else 0)
            print("wrote", path, f"width={vw / total * 100 - 0.1:.1f}%")
