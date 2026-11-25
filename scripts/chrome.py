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
        out.append(f'<text x="{x:.1f}" y="{cy + 4 * scale:.1f}" text-anchor="{anchor}" fill="{color}" style="{style};fill:{color}">{escape(title)}</text>')
    if right:
        out.append(f'<text x="{w - 14}" y="{cy + 4 * scale:.1f}" text-anchor="end" fill="{color}" fill-opacity=".7" style="{style};fill:{color}">{escape(right)}</text>')
    return "".join(out)


SB = 24   # default status bar height


def tabs(w, color, border, names, bg, rx=10, h=TB, scale=1.0):
    """Tab strip drawn in a title bar after the traffic lights: the first tab is the active one and merges
    with the body below (filled with `bg`, no divider underneath)."""
    x = 16 * scale + 3 * 18 * scale + 6
    out, style = [], f'font-family:{MONO};font-size:{11 * scale:.1f}px;white-space:pre'
    for i, name in enumerate(names):
        tw = round(len(name) * 6.6 * scale + 22)
        if x + tw > w - 8:
            break
        if i == 0:
            out.append(f'<path d="M{x:.1f} {h + .5}V{7 + 5}a5 5 0 0 1 5 -5H{x + tw - 5:.1f}a5 5 0 0 1 5 5V{h + .5}Z" fill="{bg}" stroke="{border}" stroke-opacity=".7"/>'
                       f'<rect x="{x + .5:.1f}" y="{h - .5}" width="{tw - 1}" height="2" fill="{bg}"/>'
                       f'<rect x="{x + 5:.1f}" y="6.5" width="{tw - 10}" height="1.5" rx=".75" fill="{color}"/>')
        out.append(f'<text x="{x + tw / 2:.1f}" y="{h / 2 + 4 * scale + 1:.1f}" text-anchor="middle" fill="{color}" '
                   f'fill-opacity="{1 if i == 0 else .55}" style="{style};fill:{color}">{escape(name)}</text>')
        x += tw + 2
    return "".join(out)


def statusbar(w, y, color, left="", mid="", right="", rx=10, h=SB, border=None, dark="#0d1117"):
    """vim/tmux-style status bar with rounded bottom corners: a filled `left` segment, a dim `mid` note and a
    right-aligned `right` note."""
    border = border or color
    cy = y + h / 2 + 4
    style = f"font-family:{MONO};font-size:11px;font-weight:600;white-space:pre"
    out = [f'<path d="M.5 {y}H{w - .5}V{y + h - rx - .5}A{rx} {rx} 0 0 1 {w - rx - .5} {y + h - .5}H{rx + .5}A{rx} {rx} 0 0 1 .5 {y + h - rx - .5}Z" fill="#000" fill-opacity=".28"/>'
           f'<line x1=".5" y1="{y}" x2="{w - .5}" y2="{y}" stroke="{border}" stroke-opacity=".5"/>']
    x = 14
    if left:
        lw = round(len(left) * 6.6 + 22)
        out.append(f'<path d="M.5 {y + 1}H{lw}V{y + h - .5}H{rx + .5}A{rx} {rx} 0 0 1 .5 {y + h - rx - .5}Z" fill="{color}"/>'
                   f'<text x="{lw / 2 + .5:.1f}" y="{cy}" text-anchor="middle" fill="{dark}" style="{style};fill:{dark}">{escape(left)}</text>')
        x = lw + 12
    if mid:
        out.append(f'<text x="{x}" y="{cy}" fill="{color}" fill-opacity=".75" style="{style};font-weight:500;fill:{color}">{escape(mid)}</text>')
    if right:
        out.append(f'<text x="{w - 14}" y="{cy}" text-anchor="end" fill="{color}" fill-opacity=".75" style="{style};font-weight:500;fill:{color}">{escape(right)}</text>')
    return "".join(out)


def frame_svg(svg, title, color="#8b949e", border="#8b949e", names=None, status=None, bg="none", rx=10, pad=(14, 10), dark="#0d1117"):
    """Wrap a finished standalone SVG in a window: title bar (or tabs), the original drawing as a nested <svg>,
    and an optional status bar `(left, mid, right)`. Idempotent: an already framed SVG is returned unchanged.
    The frame is neutral by default, so charts that adapt to the page's light/dark theme keep working."""
    import re
    if "data-framed" in svg[:400]:
        return svg
    m = re.match(r"\s*<svg\b([^>]*)>(.*)</svg>\s*$", svg, re.S)
    head, body = m.group(1), m.group(2)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', head).group(1).split()]
    iw, ih = vb[2], vb[3]
    px, py = pad
    w, h = iw + 2 * px, TB + py + ih + py + (SB if status else 0)
    label = re.search(r'aria-label="([^"]*)"', head)
    label = f' role="img" aria-label="{label.group(1)}"' if label else ""
    fmt = lambda v: f"{v:g}"
    bar = titlebar(w, color, border, "" if names else title, rx=rx) + (tabs(w, color, border, names, bg if bg != "none" else "#0d1117", rx=rx) if names else "")
    sb = statusbar(w, h - SB, color, *status, rx=rx, border=border, dark=dark) if status else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" data-framed="1" viewBox="0 0 {fmt(w)} {fmt(h)}" width="{fmt(w)}" height="{fmt(h)}"{label}>\n'
            f'<rect x=".5" y=".5" width="{fmt(w - 1)}" height="{fmt(h - 1)}" rx="{rx}" fill="{bg}" stroke="{border}" stroke-opacity=".5"/>\n'
            f'{bar}\n<svg x="{px}" y="{TB + py}" width="{fmt(iw)}" height="{fmt(ih)}" viewBox="{fmt(vb[0])} {fmt(vb[1])} {fmt(iw)} {fmt(ih)}">{body}</svg>\n{sb}\n</svg>\n')


if __name__ == "__main__":
    # python3 scripts/chrome.py <file.svg> <THEME> <title> [status-left status-mid status-right]: frame a generated SVG in place
    # with a palette of themes.py (e.g. SOLARIZED).
    import sys
    from pathlib import Path
    import themes
    path, theme, title, *st = sys.argv[1:]
    T = getattr(themes, theme.upper())
    p = Path(path)
    p.write_text(frame_svg(p.read_text(encoding="utf-8"), title, color=T["accent"], border=T["border"], bg=T["bg"], dark=T["surface"],
                           status=tuple(st) if st else None), encoding="utf-8")
    print("framed", p)
