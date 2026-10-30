"""Generate assets/achievements.svg, four trophy tiles for the README.

    python3 scripts/achievements.py

Edit ACHIEVEMENTS to add or change a tile (name lines are pre-wrapped).
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets" / "achievements.svg"

W, H, GAP, N = 880, 104, 20, 4
TW = (W - GAP * (N - 1)) / N
ACCENT, BG, BORDER = "#f778ba", "#1d0c15", "#8a3a68"

# 24x24 stroke glyphs
TROPHY = '<path d="M8 4h8v5a4 4 0 0 1-8 0zM8 6H5v1a3 3 0 0 0 3 3M16 6h3v1a3 3 0 0 1-3 3M12 13v4M9 20h6M10 17h4"/>'
BOT = '<rect x="4" y="8" width="16" height="11" rx="3"/><path d="M12 8V5M2 12v3M22 12v3"/><circle cx="12" cy="4" r="1"/><circle cx="9" cy="13" r="1.2"/><circle cx="15" cy="13" r="1.2"/>'
FLAG = '<path d="M6 21V4M6 5h11l-2 4 2 4H6"/>'
MEDAL = '<circle cx="12" cy="15" r="5"/><path d="M8.5 3L12 10l3.5-7M12 12.5v5"/>'

# (glyph, rank, name lines)
ACHIEVEMENTS = [
    (TROPHY, "CHAMPION", ["Hackfools 2026"]),
    (BOT, "1ST PLACE", ["AI Agent Building", "Hackathon"]),
    (FLAG, "CHAMPION", ["CTF"]),
    (MEDAL, "BRONZE MEDAL", ["OBMEP"]),
]


def build():
    tiles = []
    for i, (glyph, rank, name) in enumerate(ACHIEVEMENTS):
        x = i * (TW + GAP)
        lines = "".join(f'<text x="18" y="{66 + j * 19}" class="n">{escape(l)}</text>' for j, l in enumerate(name))
        tiles.append(
            f'<g transform="translate({x:.1f} 0)"><rect x="0.5" y="0.5" width="{TW - 1:.1f}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>'
            f'<g transform="translate(16 12) scale(1.25)" fill="none" stroke="{ACCENT}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">{glyph}</g>'
            f'<text x="56" y="32" class="t">{escape(rank)}</text>{lines}</g>')
    label = "Achievements: " + "; ".join(f"{r.title()}, {' '.join(n)}" for _, r, n in ACHIEVEMENTS)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{escape(label)}">
<style>.t{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11.5px;font-weight:600;letter-spacing:.08em;fill:{ACCENT}}}.n{{font-family:-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;font-size:15px;font-weight:600;fill:#e6edf3}}</style>
{"".join(tiles)}
</svg>
'''


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print("wrote", OUT)
