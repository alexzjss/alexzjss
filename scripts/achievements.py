"""Generate assets/achievement-*.svg, one trophy tile each for the README (each is linked to its proof).

    python3 scripts/achievements.py

Edit ACHIEVEMENTS to add or change a tile (name lines are pre-wrapped).
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

TW, H, M = 205, 104, 10   # M: transparent margin, so four tiles side by side leave a 20px gutter
ACCENT, BG, BORDER = "#f778ba", "#1d0c15", "#8a3a68"

# 24x24 stroke glyphs
TROPHY = '<path d="M8 4h8v5a4 4 0 0 1-8 0zM8 6H5v1a3 3 0 0 0 3 3M16 6h3v1a3 3 0 0 1-3 3M12 13v4M9 20h6M10 17h4"/>'
BOT = '<rect x="4" y="8" width="16" height="11" rx="3"/><path d="M12 8V5M2 12v3M22 12v3"/><circle cx="12" cy="4" r="1"/><circle cx="9" cy="13" r="1.2"/><circle cx="15" cy="13" r="1.2"/>'
FLAG = '<path d="M6 21V4M6 5h11l-2 4 2 4H6"/>'
MEDAL = '<circle cx="12" cy="15" r="5"/><path d="M8.5 3L12 10l3.5-7M12 12.5v5"/>'

# slug: (glyph, rank, name lines, linked)
ACHIEVEMENTS = {
    "hackfools": (TROPHY, "1ST PLACE", ["Hackfools 2026", "USPCodeLab"], True),
    "agents": (BOT, "1ST PLACE", ["AI Agent Building", "Hackathon"], True),
    "ctf": (FLAG, "CHAMPION", ["Capture the Flag"], True),
    "obmep": (MEDAL, "BRONZE MEDAL", ["OBMEP 2025", "State award · BA"], True),
}


def build(glyph, rank, name, linked, crop_l=False, crop_r=False):
    x0 = M if crop_l else 0
    vw = TW + 2 * M - x0 - (M if crop_r else 0)
    lines = "".join(f'<text x="18" y="{66 + j * 19}" class="n">{escape(l)}</text>' for j, l in enumerate(name))
    arrow = f'<text x="{TW - 18}" y="32" class="t" text-anchor="end">↗</text>' if linked else ""
    label = f"{rank.title()}, {' '.join(name)}"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} 0 {vw} {H + 2 * M}" width="{vw}" height="{H + 2 * M}" role="img" aria-label="{escape(label)}">
<style>.t{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11.5px;font-weight:600;letter-spacing:.08em;fill:{ACCENT}}}.n{{font-family:-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;font-size:15px;font-weight:600;fill:#e6edf3}}</style>
<g transform="translate({M} {M})"><rect x="0.5" y="0.5" width="{TW - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<g transform="translate(16 12) scale(1.25)" fill="none" stroke="{ACCENT}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">{glyph}</g>
<text x="56" y="32" class="t">{escape(rank)}</text>{arrow}{lines}</g>
</svg>
'''


if __name__ == "__main__":
    n = len(ACHIEVEMENTS)
    for i, (slug, spec) in enumerate(ACHIEVEMENTS.items()):
        path = OUT / f"achievement-{slug}.svg"
        path.write_text(build(*spec, crop_l=i == 0, crop_r=i == n - 1), encoding="utf-8")
        vw = TW + 2 * M - (M if i == 0 else 0) - (M if i == n - 1 else 0)
        print("wrote", path, f"width={vw / (n * TW + (n - 1) * 2 * M) * 100 - 0.1:.1f}%")
