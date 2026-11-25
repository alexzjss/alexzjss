"""Shared macOS-style window chrome (traffic lights + title bar) for every terminal block of the README.

    from chrome import titlebar, TB

`titlebar()` returns an SVG fragment drawn at the top of a block of width `w`; the block's own content is
expected to start at y = TB (wrap it in `<g transform="translate(0 TB)">`).
"""
from xml.sax.saxutils import escape

LIGHTS = ("#ff5f57", "#febc2e", "#28c840")
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
TB = 28   # default title bar height


def titlebar(w, color, border, title="", right="", rx=10, h=TB, align="middle", scale=1.0):
    """Title bar with rounded top corners, three traffic lights, a title and an optional right-aligned note.

    color: text color of the title; border: color of the divider line. Text carries an inline style, so the
    host SVG's own `text{...}` rules cannot override the monospace font.
    """
    r = 5.5 * scale
    pitch = 18 * scale
    cy = h / 2
    bar = (f'<path d="M.5 {h}V{rx + .5}A{rx} {rx} 0 0 1 {rx + .5} .5H{w - rx - .5}A{rx} {rx} 0 0 1 {w - .5} {rx + .5}V{h}Z" '
           f'fill="#fff" fill-opacity=".045"/>'
           f'<line x1=".5" y1="{h}" x2="{w - .5}" y2="{h}" stroke="{border}" stroke-opacity=".7"/>')
    dots = "".join(f'<circle cx="{16 * scale + i * pitch:.1f}" cy="{cy}" r="{r:.1f}" fill="{c}"/>' for i, c in enumerate(LIGHTS))
    style = f'font-family:{MONO};font-size:{11.5 * scale:.1f}px;font-weight:500;white-space:pre'
    out = [bar, dots]
    if title:
        x, anchor = (w / 2, "middle") if align == "middle" else (16 * scale + 3 * pitch + 2, "start")
        out.append(f'<text x="{x:.1f}" y="{cy + 4 * scale:.1f}" text-anchor="{anchor}" fill="{color}" style="{style}">{escape(title)}</text>')
    if right:
        out.append(f'<text x="{w - 14}" y="{cy + 4 * scale:.1f}" text-anchor="end" fill="{color}" fill-opacity=".7" style="{style}">{escape(right)}</text>')
    return "".join(out)
