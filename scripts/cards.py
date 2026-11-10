"""Generate assets/card-*.svg, the bento project cards of the README.

    python3 scripts/cards.py

Tech icons come from assets/icons/<name>.svg (downloaded from skillicons.dev, e.g.
`curl -o assets/icons/py.svg "https://skillicons.dev/icons?i=py"`) and are embedded as data URIs,
because an SVG loaded through <img> cannot reference external images.
Edit PROJECTS to add, remove or recolor a card.
"""
import base64
import json
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
    "engrama": (
        "★ FLAGSHIP · LOCAL AI", "Engrama",
        "Offline tamagotchi-style companion: a deterministic body, a swappable mind (drives, spiking net, PAD affect, "
        "traits) and a lab for replayable simulations. Local memory and LLM chat, nothing leaves the machine.",
        ["py", "pygame", "sqlite", "ollama"],
        "SNN · PAD affect · pygame · Ollama", "#ff9f6b", WIDE),
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
    "money": (
        "★ FLAGSHIP · MOBILE", "Paralelo",
        "Android investment companion that runs entirely on the phone: portfolio vs CDI and inflation, asset "
        "correlation (Ibovespa, S&P 500, USD) and allocation suggestions from a deterministic engine. No server, no accounts.",
        ["ts", "react", "sqlite", "jest", "githubactions"],
        "Expo · BCB & Yahoo data · optional BYO-key AI", "#3ddc97", WIDE),
    "acha-promocoes": (
        "▸ BOT", "acha-promocoes",
        "Discord bot that watches 6 Brazilian stores for tech deals, scores each offer and routes it to the right channel.",
        ["py", "discord"],
        "scoring · alerts · affiliate links · Render", "#7289ff", NARROW),
    "website": (
        "▸ WEB", "website",
        "Bilingual (PT/EN) static portfolio: experience timeline, project filters, research and résumé, with light/dark design tokens.",
        ["react", "ts", "vite", "css", "vercel"],
        "PT/EN · SPA · design tokens", "#79c0ff", WIDE),
    "eco-fruta": (
        "▸ WEB", "eco-fruta",
        "Virtual organic market in PT-BR: fruit, vegetable and greens catalog, producer profiles, cart and Mercado Pago checkout.",
        ["nextjs", "react", "ts", "tailwind", "vercel"],
        "Zustand · Mercado Pago · Next.js 14", "#a5d86e", NARROW),
}

# README rows, left to right. The outer edge of each row has its margin cropped away so the
# grid lines up with the 880px section bars; widths below are printed as the <img> percentages.
LAYOUT = [["dasiboard", "sampanav"], ["engrama", "jflp"], ["money", "acha-promocoes"], ["modaloop", "vat", "icndy"], ["website", "eco-fruta"]]

# Commit counts and language bytes come from scripts/data.json (written by scripts/refresh.py).
DATA = json.loads((Path(__file__).resolve().parent / "data.json").read_text())
# GitHub linguist colors
LANG_COLORS = {"TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Python": "#3572a5", "Java": "#b07219",
               "GDScript": "#355570", "CSS": "#663399", "HTML": "#e34c26", "PLpgSQL": "#336790",
               "Shell": "#89e051", "Dockerfile": "#384d54", "PowerShell": "#012456", "Batchfile": "#c1f12e"}
SHOT_H = 110              # screenshot strip under the chips; cards with one grow by SHOT_H + 10
SHOTS = {"dasiboard", "sampanav"}   # slugs with assets/shots/<slug>.jpg (real screenshots of the live apps)
MIN_SHARE = 0.01          # languages under 1% would be sub-pixel slivers

_cache = {}


def icon_uri(name):
    if name not in _cache:
        data = (OUT / "icons" / f"{name}.svg").read_bytes()
        _cache[name] = "data:image/svg+xml;base64," + base64.b64encode(data).decode()
    return _cache[name]


def shot_uri(slug):
    return "data:image/jpeg;base64," + base64.b64encode((OUT / "shots" / f"{slug}.jpg").read_bytes()).decode()


def tint(hex_color, k=0.10):
    """Dark card background: the accent mixed into the page background."""
    base = (13, 17, 23)
    rgb = [int(hex_color[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(b + (c - b) * k):02x}" for b, c in zip(base, rgb))


def build(tag, title, desc, icons, chips, accent, w, crop_l=False, crop_r=False, commits=None, langs=None, shot=None):
    cols = 82 if w == WIDE else 38
    lines = textwrap.wrap(desc, cols)
    text = "".join(
        f'<text x="20" y="{86 + i * 18}" class="d">{escape(l)}</text>' for i, l in enumerate(lines))
    imgs = "".join(
        f'<image x="{20 + i * (ICON + GAP)}" y="148" width="{ICON}" height="{ICON}" href="{icon_uri(n)}"/>'
        for i, n in enumerate(icons))
    chip = f'<text x="20" y="206" class="c">{escape(chips)}</text>' if chips else ""
    meta = f'<text x="{w - 20}" y="32" class="m" text-anchor="end">{commits} commits</text>' if commits else ""
    h = H + (SHOT_H + 10 if shot else 0)
    pic = (f'<clipPath id="s"><rect x="20" y="{H}" width="{w - 40}" height="{SHOT_H}" rx="8"/></clipPath>'
           f'<image x="20" y="{H}" width="{w - 40}" height="{SHOT_H}" preserveAspectRatio="xMidYMid slice" clip-path="url(#s)" href="{shot}"/>'
           f'<rect x="20.5" y="{H + .5}" width="{w - 41}" height="{SHOT_H - 1}" rx="8" fill="none" stroke="{accent}" stroke-opacity=".35"/>') if shot else ""
    bar = lang_bar(langs, w) if langs else ""
    x0 = M if crop_l else 0
    vw = w + 2 * M - x0 - (M if crop_r else 0)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="{x0} 0 {vw} {h + 2 * M}" width="{vw}" height="{h + 2 * M}" role="img" aria-label="{escape(title)}: {escape(desc)}">
<style>
text{{font-family:-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}}
.t{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11px;font-weight:600;letter-spacing:.08em;fill:{accent}}}
.m{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11px;fill:#6e7681}}
.h{{font-size:21px;font-weight:700;fill:#e6edf3}}
.d{{font-size:13px;fill:#b1bac4}}
.c{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11.5px;fill:{accent}}}
</style>
<g transform="translate({M} {M})">
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12" fill="{tint(accent)}" stroke="{accent}" stroke-opacity=".7"/>
<text x="20" y="32" class="t">{escape(tag)}</text>{meta}
<text x="20" y="60" class="h">{escape(title)}</text>
{text}{imgs}{chip}{bar}{pic}
</g>
</svg>
'''


def lang_bar(langs, w):
    """Thin GitHub-style language strip along the card's bottom edge."""
    total = sum(langs.values())
    segs, x, span = [], 20, w - 40
    for name, n in sorted(langs.items(), key=lambda kv: -kv[1]):
        if n / total < MIN_SHARE:
            continue
        sw = n / total * span
        segs.append(f'<rect x="{x:.1f}" y="0" width="{sw:.1f}" height="3" fill="{LANG_COLORS.get(name, "#8b949e")}"><title>{escape(name)} {n / total:.0%}</title></rect>')
        x += sw
    return f'<g transform="translate(0 211)"><clipPath id="r"><rect x="20" y="0" width="{span}" height="3" rx="1.5"/></clipPath><g clip-path="url(#r)">{"".join(segs)}</g></g>'


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
            path.write_text(build(*spec, crop_l=i == 0, crop_r=i == len(row) - 1, commits=DATA[slug]['commits'], langs=DATA[slug]['languages'],
                                   shot=shot_uri(slug) if slug in SHOTS else None), encoding="utf-8")
            total = sum(PROJECTS[x][-1] + 2 * M for x in row) - 2 * M
            vw = spec[-1] + 2 * M - (M if i == 0 else 0) - (M if i == len(row) - 1 else 0)
            print("wrote", path, f"width={vw / total * 100 - 0.1:.1f}%")
