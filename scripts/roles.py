"""Generate assets/roles.svg, the `history` timeline of the README.

    python3 scripts/roles.py

Edit ROLES (newest first) to add a role.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets" / "roles.svg"

W, ROW, TOP = 880, 46, 22
BG, BORDER, FG, DIM, SOFT = "#120d1f", "#5a3fa0", "#b392f0", "#7b62b8", "#a99bd6"
NODE_X = 150

# (since, role, where)
ROLES = [
    ("2026-10", "Claude Campus Ambassador", "THE·TEAM"),
    ("2026-09", "Backend Development Trainee", "Síntese Jr. (IT consulting junior enterprise)"),
    ("2026-07", "Undergraduate Researcher", "SAEG · USP"),
    ("2026-05", "Data & AI Researcher", "Hype — Data & AI"),
    ("2026-03", "IT Project Coordinator", "DASI USP"),
]


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


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print("wrote", OUT)
