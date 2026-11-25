"""Generate assets/card-research.svg, the full-width card of the research section (same look as the project cards).

    python3 scripts/research.py

Edit the constants below to change the text, the pipeline steps or the project chips.
"""
from pathlib import Path
from xml.sax.saxutils import escape

from cards import ICON, M, icon_uri
from themes import NORD as T
from chrome import SB, TB, statusbar, tabs, titlebar

OUT = Path(__file__).resolve().parent.parent / "assets" / "card-research.svg"

W = 880
ACCENT = T["accent"]               # Nord green
TAG = "◆ RESEARCH · PUB/USP · CURRENT"
TITLE = "Data Generation for Software Testing & Debugging Experimentation"
GROUP = "Software Analysis & Experimentation Group (SAEG) · advised by Prof. Dr. Marcos Lordello Chaim"
ICONS = ["java", "maven", "linux", "git"]
# (label, title, detail): what happens to a bug on its way to the dataset
STEPS = [
    ("01 · bugs", "Bugs.jar", "real bugs, 8 Apache projects"),
    ("02 · run", "Run the tests", "every faulty version, Linux"),
    ("03 · measure", "Jaguar 2", "line & control-flow coverage"),
    ("04 · share", "Open dataset", "for fault localization"),
]
PROJECTS = ["Accumulo", "Camel", "Commons Math", "Flink", "Jackrabbit Oak", "Log4j 2", "Maven", "Wicket"]

BOX_W, BOX_H, GAP = 186, 64, 32      # 4 * 186 + 3 * 32 = 840 = card width - 2 * 20
PIPE_Y = 108
CHIP_Y = 194
H = 236 + TB + SB


def build():
    icons = "".join(
        f'<image x="{W - 20 - len(ICONS) * ICON - (len(ICONS) - 1) * 6 + i * (ICON + 6)}" y="14" width="{ICON}" height="{ICON}" href="{icon_uri(n)}"/>'
        for i, n in enumerate(ICONS))
    boxes = []
    for i, (label, title, detail) in enumerate(STEPS):
        x = 20 + i * (BOX_W + GAP)
        boxes.append(
            f'<rect x="{x}.5" y="{PIPE_Y}.5" width="{BOX_W - 1}" height="{BOX_H - 1}" rx="8" fill="#000" fill-opacity=".18" stroke="{ACCENT}" stroke-opacity=".35"/>'
            f'<text x="{x + 14}" y="{PIPE_Y + 19}" class="l">{escape(label)}</text>'
            f'<text x="{x + 14}" y="{PIPE_Y + 39}" class="b">{escape(title)}</text>'
            f'<text x="{x + 14}" y="{PIPE_Y + 55}" class="d s">{escape(detail)}</text>')
        if i < len(STEPS) - 1:
            x1, x2, y = x + BOX_W + 6, x + BOX_W + GAP - 6, PIPE_Y + BOX_H / 2
            boxes.append(
                f'<line x1="{x1}" y1="{y}" x2="{x2 - 5}" y2="{y}" stroke="{ACCENT}" stroke-width="2" stroke-dasharray="4 4" class="flow"/>'
                f'<path d="M{x2 - 6} {y - 5}L{x2} {y}L{x2 - 6} {y + 5}" fill="none" stroke="{ACCENT}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    chips, x = [], 20 + 74
    for name in PROJECTS:
        w = round(len(name) * 6.9 + 22)
        chips.append(
            f'<rect x="{x}.5" y="{CHIP_Y}.5" width="{w - 1}" height="21" rx="10.5" fill="{ACCENT}" fill-opacity=".08" stroke="{ACCENT}" stroke-opacity=".45"/>'
            f'<text x="{x + w / 2}" y="{CHIP_Y + 15}" class="p" text-anchor="middle">{escape(name)}</text>')
        x += w + 8
    steps = "; ".join(f"{t}: {d}" for _, t, d in STEPS)
    label = f"{TITLE}. {GROUP}. Pipeline: {steps}. Bugs from {', '.join(PROJECTS)}."
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="{M} 0 {W} {H + 2 * M}" width="{W}" height="{H + 2 * M}" role="img" aria-label="{escape(label)}">
<style>
text{{font-family:-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}}
.t{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11px;font-weight:600;letter-spacing:.08em;fill:{ACCENT}}}
.h{{font-size:21px;font-weight:700;fill:{T["fg"]}}}
.d{{font-size:13px;fill:{T["soft"]}}}
.s{{font-size:12px}}
.b{{font-size:14px;font-weight:700;fill:{T["fg"]}}}
.l{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:10.5px;letter-spacing:.06em;fill:{ACCENT}}}
.p{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11.5px;fill:{T["soft"]}}}
.k{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11px;fill:{T["dim"]}}}
.flow{{animation:flow 1s linear infinite}}@keyframes flow{{to{{stroke-dashoffset:-8}}}}
@media (prefers-reduced-motion:reduce){{.flow{{animation:none}}}}
</style>
<g transform="translate({M} {M})">
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{T["bg"]}" stroke="{T["border"]}"/>
{titlebar(W, ACCENT, T["border"], "", rx=12)}{tabs(W, ACCENT, T["border"], ["research", "pipeline", "dataset"], T["bg"], rx=12)}
{statusbar(W, H - SB, ACCENT, "⎇ main", f"{len(STEPS)} steps · {len(PROJECTS)} projects", "PUB/USP · SAEG", rx=12, border=T["border"], dark=T["surface"])}
<g transform="translate(0 {TB})">
<text x="20" y="32" class="t">{escape(TAG)}</text>{icons}
<text x="20" y="64" class="h">{escape(TITLE)}</text>
<text x="20" y="88" class="d">{escape(GROUP)}</text>
{"".join(boxes)}
<text x="20" y="{CHIP_Y + 15}" class="k">bugs from</text>{"".join(chips)}
</g>
</g>
</svg>
'''


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print("wrote", OUT)
