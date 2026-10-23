"""Generate assets/header.svg, the amber terminal header of the profile README.

    python3 scripts/header.py

Edit SCRIPT below to change what gets typed.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets" / "header.svg"

W, H = 780, 300
FS, LH = 17, 30
CW = FS * 0.62        # approx monospace advance; overestimate so the typing clip never cuts text
X0, Y0 = 32, 78
STEP, PAUSE = 0.055, 0.45

BG, BORDER = "#120d05", "#3a2a0c"
AMBER, HI, DIM = "#ffb000", "#ffd98a", "#a87a1c"

# (command, [output line as (text, color) segments])
SCRIPT = [
    ("whoami", [[("Alex Santana", HI), ("  // software & data engineer", DIM)]]),
    ("cat ./now", [[("Information Systems @ USP", AMBER), ("  ·  São Paulo, BR", DIM)]]),
    ("ls ./interests", [[("backend/  data-eng/  ml-ai/  testing-debugging/  security/", AMBER)]]),
]

PROMPT = [("alex@usp", AMBER), (":", DIM), ("~", HI), ("$ ", DIM)]


def prompt(y):
    spans = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in PROMPT)
    return f'<text x="{X0}" y="{y}">{spans}</text>'


def build():
    px = X0 + sum(len(s) for s, _ in PROMPT) * CW
    clips, body = [], []
    t, y = 0.6, Y0
    for i, (cmd, outputs) in enumerate(SCRIPT):
        n = len(cmd)
        widths = ";".join(f"{k * CW:.1f}" for k in range(n + 1))
        keys = ";".join(f"{k / (n + 1):.4f}" for k in range(n + 1))
        clips.append(
            f'<clipPath id="c{i}"><rect x="{px:.1f}" y="{y - FS}" width="0" height="{FS + 8}">'
            f'<animate attributeName="width" begin="{t:.2f}s" dur="{(n + 1) * STEP:.2f}s" calcMode="discrete" '
            f'values="{widths}" keyTimes="{keys}" fill="freeze"/></rect></clipPath>')
        body.append(
            f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t - 0.25:.2f}s" fill="freeze"/>'
            f'{prompt(y)}<text x="{px:.1f}" y="{y}" fill="{HI}" clip-path="url(#c{i})">{escape(cmd)}</text></g>')
        t += (n + 1) * STEP + 0.2
        y += LH
        for line in outputs:
            spans = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in line)
            body.append(f'<text x="{X0}" y="{y}" opacity="0">{spans}'
                        f'<set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/></text>')
            y += LH
        t += PAUSE
        y += 6
    body.append(
        f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>{prompt(y)}'
        f'<rect x="{px:.1f}" y="{y - FS + 2}" width="{CW:.1f}" height="{FS + 2}" fill="{AMBER}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5001;1" dur="1.1s" '
        f'begin="{t:.2f}s" repeatCount="indefinite"/></rect></g>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Terminal: whoami — Alex Santana, software and data engineer, Information Systems at USP">
<defs>
<filter id="glow" x="-5%" y="-30%" width="110%" height="160%">
  <feGaussianBlur stdDeviation="0.9" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
{"".join(clips)}
</defs>
<style>text{{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;font-size:{FS}px;white-space:pre}}</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{BG}" stroke="{BORDER}"/>
<text x="{W - 24}" y="30" text-anchor="end" fill="{DIM}" style="font-size:12px">alex@usp: ~ — fish</text>
<g filter="url(#glow)">{"".join(body)}</g>
</svg>
'''


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print("wrote", OUT)
