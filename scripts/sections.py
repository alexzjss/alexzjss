"""Generate assets/sec-*.svg, one terminal banner per README section, each with its own color.

    python3 scripts/sections.py

Edit SECTIONS to add or recolor a section.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

W, H = 880, 40

# slug: (command, background, border, foreground, dim)
SECTIONS = {
    "about":        ("cat about.md",           "#1a1408", "#6b4a00", "#ffb000", "#a87a1c"),
    "projects":     ("ls -l ~/projects",       "#08171b", "#0e5a6b", "#39d0f0", "#2a8aa0"),
    "research":     ("cat research.log",       "#08170e", "#1f6b3a", "#5fd38d", "#3d8f5f"),
    "roles":        ("history | grep -i role", "#120d1f", "#5a3fa0", "#b392f0", "#7b62b8"),
    "stack":        ("tree --grow ~/stack",    "#1f0d0c", "#8a3a35", "#ff7b72", "#b0524c"),
    "achievements": ("grep -c win ~/.achievements", "#1d0c15", "#8a3a68", "#f778ba", "#b0518a"),
    "gitlog":       ("git log --graph",        "#0a1220", "#1f4f8a", "#79c0ff", "#4f86c0"),
}


def build(cmd, bg, border, fg, dim):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="$ {escape(cmd)}">
<style>text{{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;font-size:16px;font-weight:600;white-space:pre}}</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="{bg}" stroke="{border}"/>
<text x="16" y="26"><tspan fill="{dim}">$ </tspan><tspan fill="{fg}">{escape(cmd)}</tspan></text>
<rect x="{W - 24}" y="14" width="9" height="14" fill="{fg}"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5001;1" dur="1.1s" repeatCount="indefinite"/></rect>
</svg>
'''


if __name__ == "__main__":
    for slug, spec in SECTIONS.items():
        path = OUT / f"sec-{slug}.svg"
        path.write_text(build(*spec), encoding="utf-8")
        print("wrote", path)
