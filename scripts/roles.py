"""Generate assets/roles.svg, the `history` timeline of the README, and refresh the block around it in README.md.

    python3 scripts/roles.py

Edit scripts/roles.json ("roles", newest first, and "also") to add a role: the SVG, its alt text and the
"also:" line all come from there. README.md is rewritten between the <!-- roles:start --> and <!-- roles:end --> markers.
"""
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "roles.svg"
README = ROOT / "README.md"
DATA = json.loads((Path(__file__).resolve().parent / "roles.json").read_text(encoding="utf-8"))

W, ROW, TOP = 880, 46, 22
BG, BORDER, FG, DIM, SOFT = "#120d1f", "#5a3fa0", "#b392f0", "#7b62b8", "#a99bd6"
NODE_X = 150

ROLES = [(r["since"], r["role"], r["where"]) for r in DATA["roles"]]


def build():
    h = TOP * 2 + ROW * (len(ROLES) - 1) + 4
    ys = [TOP + 2 + i * ROW for i in range(len(ROLES))]
    label = "; ".join(f"{s} {r} at {w}" for s, r, w in ROLES)
    rows = []
    for i, ((since, role, where), y) in enumerate(zip(ROLES, ys)):
        now = i == 0
        node = (f'<circle cx="{NODE_X}" cy="{y}" r="5" fill="{FG}"/>'
                f'<circle cx="{NODE_X}" cy="{y}" r="5" fill="none" stroke="{FG}"><animate attributeName="r" values="5;12" dur="2s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values=".8;0" dur="2s" repeatCount="indefinite"/></circle>') if now else \
               f'<circle cx="{NODE_X}" cy="{y}" r="4.5" fill="{BG}" stroke="{FG}" stroke-width="1.5"/>'
        rows.append(
            f'<text x="28" y="{y + 4.5}" class="m" fill="{DIM}">since <tspan fill="{FG}">{since}</tspan></text>{node}'
            f'<text x="{NODE_X + 28}" y="{y + 5.5}" class="r" fill="#e6edf3">{escape(role)}</text>'
            f'<text x="{W - 28}" y="{y + 4.5}" class="m" text-anchor="end" fill="{SOFT if not now else FG}">{escape(where)}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-label="Roles, newest first: {escape(label)}">
<style>.m{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13px}}.r{{font-family:-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;font-size:16px;font-weight:600}}</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<line x1="{NODE_X}" y1="{ys[0]}" x2="{NODE_X}" y2="{ys[-1]}" stroke="{BORDER}" stroke-width="2"/>
{"".join(rows)}
</svg>
'''


def readme_block():
    short = lambda w: w.split(" (")[0]            # "Síntese Jr. (IT consulting ...)" -> "Síntese Jr."
    alt = "Roles, newest first: " + "; ".join(f"{s} {r} at {short(w)}" for s, r, w in ROLES)
    return (f'<!-- roles:start -->\n<img src="assets/roles.svg" width="100%" alt={quoteattr(alt)}>\n\n'
            f'<sub>also: {" · ".join(DATA["also"])}</sub>\n<!-- roles:end -->')


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print("wrote", OUT)
    text = README.read_text(encoding="utf-8")
    new, n = re.subn(r"<!-- roles:start -->.*?<!-- roles:end -->", lambda _: readme_block(), text, flags=re.S)
    if n:
        README.write_text(new, encoding="utf-8")
        print("updated the roles block in", README)
    else:
        print("no <!-- roles:start --> / <!-- roles:end --> markers in README.md: add them around the roles image to keep it in sync")
