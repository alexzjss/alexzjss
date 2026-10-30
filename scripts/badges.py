"""Generate assets/badge-*.svg, the contact pills at the top of the README.

    python3 scripts/badges.py

Edit BADGES to change a label or link text.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

H, PAD, ICON = 34, 14, 18
BG, BORDER, AMBER, DIM = "#1a1408", "#6b4a00", "#ffb000", "#a87a1c"
CW = 7.8   # monospace advance at 13px, used only to size the pill; textLength keeps the text inside it

# 18x18 glyphs, stroke-only to match the terminal look
ICONS = {
    "linkedin": '<rect x="1" y="1" width="16" height="16" rx="3"/><path d="M5.5 8v5M5.5 5.2v.1M9 13V8m0 2.2c0-1.4 1-2.2 2.2-2.2s1.8.8 1.8 2.2V13"/>',
    "portfolio": '<path d="M9 2l8 14H1z"/>',
    "mail": '<rect x="1" y="3" width="16" height="12" rx="2"/><path d="M1.5 4.5L9 10l7.5-5.5"/>',
}

# slug: (key, value)
BADGES = {
    "linkedin": ("linkedin", "alex-jsz"),
    "portfolio": ("portfolio", "alexjsz.vercel.app"),
    "mail": ("mail", "benalex511@gmail.com"),
}


def build(slug, key, value):
    kw, vw = len(key) * CW, len(value) * CW
    w = round(PAD + ICON + 10 + kw + 8 + vw + PAD)
    tx = PAD + ICON + 10
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {H}" width="{w}" height="{H}" role="img" aria-label="{escape(key)}: {escape(value)}">
<style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13px;font-weight:600}}</style>
<rect x="0.5" y="0.5" width="{w - 1}" height="{H - 1}" rx="8" fill="{BG}" stroke="{BORDER}"/>
<g transform="translate({PAD} {(H - ICON) / 2})" fill="none" stroke="{AMBER}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">{ICONS[slug]}</g>
<text y="21.5"><tspan x="{tx}" fill="{DIM}" textLength="{kw:.1f}">{escape(key)}</tspan><tspan x="{tx + kw + 8:.1f}" fill="{AMBER}" textLength="{vw:.1f}">{escape(value)}</tspan></text>
</svg>
'''


if __name__ == "__main__":
    for slug, (key, value) in BADGES.items():
        path = OUT / f"badge-{slug}.svg"
        path.write_text(build(slug, key, value), encoding="utf-8")
        print("wrote", path)
