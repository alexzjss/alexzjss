"""Generate assets/sec-*.svg, one terminal window banner per README section, each in its own editor theme.

    python3 scripts/sections.py

Edit SECTIONS to add a section or move it to another theme (themes.py). `sec-more.svg` is the button of the collapsed
"more projects" block: a window whose prompt is the command, plus a pill with the number of hidden cards.
"""
from pathlib import Path
from xml.sax.saxutils import escape

from cards import MORE
from chrome import MONO, TB, titlebar
from themes import CATPPUCCIN, DRACULA, NORD, ROSE_PINE, SOLARIZED, TOKYO_NIGHT

OUT = Path(__file__).resolve().parent.parent / "assets"

W, H = 880, TB + 38

# slug: (command, theme, window title)
SECTIONS = {
    "projects":      ("ls -l ~/projects",            TOKYO_NIGHT, "zsh — ~/projects"),
    "research":      ("cat research.log",            NORD,        "zsh — ~/research"),
    "roles":         ("history | grep -i role",      CATPPUCCIN,  "zsh — ~"),
    "stack":         ("tree --grow ~/stack",         DRACULA,     "zsh — ~/stack"),
    "achievements":  ("grep -c win ~/.achievements", ROSE_PINE,   "zsh — ~"),
    "contributions": ("pacman ./contributions",      SOLARIZED,   "zsh — ~/contributions"),
}
CHAR_W = 9.6          # advance of the 16px monospace prompt


def frame(cmd, T, title, extra, label):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{escape(label)}">
<style>text{{font-family:{MONO};font-size:16px;font-weight:600;white-space:pre}}@media (prefers-reduced-motion:reduce){{.cur{{display:none}}}}</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="{T["surface"]}" stroke="{T["border"]}"/>
{titlebar(W, T["dim"], T["border"], title, rx=8)}
<text x="16" y="{TB + 25}"><tspan fill="{T["dim"]}">$ </tspan><tspan fill="{T["accent"]}">{escape(cmd)}</tspan></text>
{extra}
</svg>
'''


def cursor(T, x):
    return (f'<rect class="cur" x="{x:.1f}" y="{TB + 12}" width="9" height="14" fill="{T["accent"]}">'
            f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5001;1" dur="1.1s" repeatCount="indefinite"/></rect>')


def build(cmd, T, title):
    done = (f'<text x="{W - 40}" y="{TB + 25}" text-anchor="end" fill="{T["dim"]}" fill-opacity=".7" '
            f'style="font-size:12px;font-weight:500">✓ 0.03s</text>')
    return frame(cmd, T, title, done + cursor(T, W - 24), f"$ {cmd}")


def build_more():
    """The open/close button of the collapsed block: the command, a hint and a pill with the hidden card count."""
    T, cmd = TOKYO_NIGHT, "ls -a ~/projects/more"
    n = sum(len(r) for r in MORE)
    pill_w, pill_h = 112, 24
    px, py = W - 16 - pill_w, TB + 7
    hint = f'<text x="{px - 14}" y="{TB + 24}" text-anchor="end" fill="{T["dim"]}" style="font-size:12px;font-weight:500">click to toggle</text>'
    pill = (f'<rect x="{px}" y="{py}" width="{pill_w}" height="{pill_h}" rx="{pill_h / 2}" fill="{T["accent"]}"/>'
            f'<text x="{px + pill_w / 2}" y="{py + 16.5}" text-anchor="middle" fill="{T["surface"]}" style="font-size:13px;font-weight:700;fill:{T["surface"]}">+{n} more  ▾</text>')
    return frame(cmd, T, "zsh — ~/projects/more", hint + pill + cursor(T, 16 + (len(cmd) + 2) * CHAR_W + 2),
                 f"$ ls -a ~/projects/more [+{n}]: click to show or hide {n} more projects")


if __name__ == "__main__":
    for slug, (cmd, T, title) in SECTIONS.items():
        path = OUT / f"sec-{slug}.svg"
        path.write_text(build(cmd, T, title), encoding="utf-8")
        print("wrote", path)
    path = OUT / "sec-more.svg"
    path.write_text(build_more(), encoding="utf-8")
    print("wrote", path)
