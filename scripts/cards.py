"""Generate assets/card-*.svg, the bento project cards of the README.

    python3 scripts/cards.py

Tech icons come from assets/icons/<name>.svg (downloaded from skillicons.dev, e.g.
`curl -o assets/icons/py.svg "https://skillicons.dev/icons?i=py"`) and are embedded as data URIs,
because an SVG loaded through <img> cannot reference external images.
Edit PROJECTS to add or remove a card and LAYOUT / MORE to place it; the look comes from themes.py (all cards share one theme).
"""
import base64
import json
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

from chrome import MONO, SB, TB, statusbar, tabs, titlebar
from refresh import REPOS
from themes import TOKYO_NIGHT as T

OUT = Path(__file__).resolve().parent.parent / "assets"

WIN = 22                   # title bar of the screenshot window
HALF, THIRD = 430, 280    # card width in a row of two / three: 2 * 430 + 20 gap = 3 * 280 + 2 * 20 = 880
ICON, GAP = 28, 6
M = 10                    # transparent margin baked into each SVG: the 20px gutter is exact, whatever the page width

# slug: (tag, title, description, icons, extra chips). Colors come from themes.py, widths from LAYOUT.
PROJECTS = {
    "dasiboard": (
        "★ FLAGSHIP · 700+ STUDENTS", "DaSIboard",
        "All-in-one academic workspace for USP Information Systems students: kanban, grades & attendance, "
        "calendar, study rooms and a curriculum flowchart. 500+ commits, built with a team.",
        ["ts", "react", "vite", "nodejs", "supabase", "postgres", "vercel", "vitest"],
        "Serverless API · Google OAuth · Web Push"),
    "sampanav": (
        "★ FLAGSHIP", "SampaNav",
        "São Paulo routes that trade travel time against recorded crime exposure (SSP-SP).",
        ["py", "fastapi", "js", "docker", "githubactions", "vercel"],
        "igraph · H3 · OSMnx · MapLibre"),
    "engrama": (
        "★ FLAGSHIP · LOCAL AI", "Engrama",
        "Offline tamagotchi-style companion: a deterministic body, a swappable mind (drives, spiking net, PAD affect, "
        "traits) and a lab for replayable simulations. Local memory and LLM chat, nothing leaves the machine.",
        ["py", "pygame", "sqlite", "ollama"],
        "SNN · PAD affect · pygame · Ollama"),
    "proxio": (
        "★ FLAGSHIP · EDTECH", "Próxio",
        "Web platform against high-school dropout in Brazilian public schools: students link what they study to the future they want, "
        "teachers get a map of where the class stalls. Deterministic rules, Gemini only writes text, RAG over BNCC.",
        ["ts", "nextjs", "react", "vitest", "vercel"],
        "Gemini 2.5 Flash · RAG · BNCC · MUI"),
    "jflp": (
        "◆ RESEARCH", "JFLP Studio",
        "Spectrum-Based Fault Localization on Defects4J and Bugs.jar, with a resumable run queue.",
        ["py", "fastapi", "java", "maven", "sqlite", "git"],
        "Jaguar 2 · JaCoCo · htmx"),
    "modaloop": (
        "▸ WEB", "ModaLoop",
        "Map of collection points for used clothing, with a disposal guide and environmental info.",
        ["react", "ts", "vite", "css"],
        "Geolocation · CSS Modules"),
    "vat": (
        "▸ GAME", "vat",
        "JRPG prototype with real-time ATB combat, elemental reactions, bosses and a bestiary.",
        ["godot"],
        "typed GDScript · GUT"),
    "icndy": (
        "▸ MOBILE", "ICNDY",
        "Offline-first Android app for timing the Cindy CrossFit workout, with PR pace and charts.",
        ["ts", "react", "sqlite", "vitest", "githubactions"],
        "Expo · React Native · EAS"),
    "clawdesk": (
        "★ FLAGSHIP · DESKTOP", "Clawdesk",
        "Pixel-art Clawd mascots on your Windows taskbar, one per Claude account, plus an office to watch every Claude "
        "Code session at work: live status, statistics, themes, skins and notifications. One-click installer.",
        ["cs", "ts", "js", "ps", "githubactions"],
        "Windows tray app · Claude Code mod · PT/EN"),
    "virtualjrpg": (
        "★ GAME · TABLETOP", "virtualJRPG",
        "Virtual tabletop with its own d100 rules: CTB combat, Aura/Sanity, a skill tree and crafting. GM panel, player sheets, live over WebSocket.",
        ["nodejs", "js", "html", "css"],
        "WebSocket · Three.js"),
    "constela": (
        "★ FLAGSHIP · MOBILE", "Constela",
        "Android investment companion that runs entirely on the phone: portfolio vs CDI and inflation, asset "
        "correlation (Ibovespa, S&P 500, USD) and allocation suggestions from a deterministic engine. No server, no accounts.",
        ["ts", "react", "sqlite", "jest", "githubactions"],
        "Expo · BCB & Yahoo data · optional BYO-key AI"),
    "acha-promocoes": (
        "▸ BOT", "acha-promocoes",
        "Discord bot that watches 6 Brazilian stores for tech deals, scores each offer and routes it to the right channel.",
        ["py", "discord"],
        "scoring · alerts · Render"),
    "website": (
        "▸ WEB", "website",
        "Bilingual (PT/EN) static portfolio: experience timeline, project filters, research and résumé, with light/dark design tokens.",
        ["react", "ts", "vite", "css", "vercel"],
        "PT/EN · SPA · design tokens"),
    "eco-fruta": (
        "▸ WEB", "eco-fruta",
        "Virtual organic market in PT-BR: fruit, vegetable and greens catalog, producer profiles, cart and Mercado Pago checkout.",
        ["nextjs", "react", "ts", "tailwind", "vercel"],
        "Zustand · Mercado Pago · Next.js 14"),
}

# README rows, left to right, most important first: flagships two to a row, then the rest three to a row.
# MORE is the collapsed block under the "ls -a ~/projects/more" button. Every row has one width per card, so the grid is uniform.
LAYOUT = [["dasiboard", "clawdesk"], ["proxio", "engrama"], ["constela", "sampanav"], ["virtualjrpg", "jflp"], ["acha-promocoes", "website"]]
MORE = [["modaloop", "vat"], ["icndy", "eco-fruta"]]
ROW_WIDTH = {2: HALF, 3: THIRD}
ROW_SHOT_H = {2: 160, 3: 130}      # strip heights, = TALL / SHORT of scripts/shots.py

# Commit counts and language bytes come from scripts/data.json (written by scripts/refresh.py).
DATA = json.loads((Path(__file__).resolve().parent / "data.json").read_text())
# GitHub linguist colors
LANG_COLORS = {"TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Python": "#3572a5", "Java": "#b07219",
               "GDScript": "#355570", "CSS": "#663399", "HTML": "#e34c26", "PLpgSQL": "#336790",
               "Shell": "#89e051", "Dockerfile": "#384d54", "PowerShell": "#012456", "Batchfile": "#c1f12e", "C#": "#178600"}
# tag glyph -> color, the legend of the grid
GLYPHS = {"★": (T["yellow"], "flagship"), "◆": (T["green"], "research"), "▸": (T["dim"], "side builds")}
COLS = {HALF: 58, THIRD: 38}       # description wrap width per card width
MIN_SHARE = 0.01                   # languages under 1% would be sub-pixel slivers

_cache = {}


def icon_uri(name):
    if name not in _cache:
        data = (OUT / "icons" / f"{name}.svg").read_bytes()
        _cache[name] = "data:image/svg+xml;base64," + base64.b64encode(data).decode()
    return _cache[name]


def shot_uri(slug):
    """assets/shots/<slug>.gif (animated) wins over <slug>.jpg."""
    gif = OUT / "shots" / f"{slug}.gif"
    if gif.exists():
        return "data:image/gif;base64," + base64.b64encode(gif.read_bytes()).decode()
    return "data:image/jpeg;base64," + base64.b64encode((OUT / "shots" / f"{slug}.jpg").read_bytes()).decode()


def wrap(desc, w):
    return textwrap.wrap(desc, COLS[w])


def build(spec, w, nl, shot_h, crop_l=False, crop_r=False, commits=None, langs=None, shot=None):
    """A card is a terminal window: tabs in the title bar, a short shell session as the body
    (`$ cat README.md`, `$ ls stack/`), the screenshot in a mini window, and a status bar with commits and languages.
    `nl` is the longest description of the row in lines, so every card of a row has the same height."""
    tag, title, desc, icons, chips = spec
    accent, bg = T["accent"], T["bg"]
    lines = wrap(desc, w)
    text = "".join(f'<text x="20" y="{98 + i * 18}" class="d">{escape(l)}</text>' for i, l in enumerate(lines))
    p2 = 98 + 18 * (nl - 1) + 30                        # baseline of the `$ ls stack/` prompt
    icons_y = p2 + 8
    chip_y = icons_y + ICON + 20
    H = chip_y + 14                                     # end of the shell session, start of the screenshot window
    prompt = lambda y, cmd: f'<text x="20" y="{y}" class="pr"><tspan fill-opacity=".6">$ </tspan><tspan class="cm">{escape(cmd)}</tspan></text>'
    imgs = "".join(
        f'<image x="{20 + i * (ICON + GAP)}" y="{icons_y}" width="{ICON}" height="{ICON}" href="{icon_uri(n)}"/>'
        for i, n in enumerate(icons))
    chip = f'<text x="20" y="{chip_y}" class="c"># {escape(chips)}</text>' if chips else ""
    body_h, pic = H - 2, ""
    if shot:
        body_h = H + WIN + shot_h + 12
        pic = (f'<clipPath id="s"><rect x="20" y="{H}" width="{w - 40}" height="{WIN + shot_h}" rx="8"/></clipPath>'
               f'<rect x="20" y="{H}" width="{w - 40}" height="{WIN + shot_h}" rx="8" fill="{T["surface"]}" filter="url(#sh)"/>'
               f'<g clip-path="url(#s)"><image x="20" y="{H + WIN}" width="{w - 40}" height="{shot_h}" preserveAspectRatio="xMidYMid slice" href="{shot}"/></g>'
               f'<g transform="translate(20 {H})">{titlebar(w - 40, T["soft"], T["border"], "preview.png", rx=8, h=WIN, scale=.75)}</g>'
               f'<rect x="20.5" y="{H + .5}" width="{w - 41}" height="{WIN + shot_h - 1}" rx="8" fill="none" stroke="{T["border"]}"/>')
    h = TB + body_h + SB
    x0 = M if crop_l else 0
    vw = w + 2 * M - x0 - (M if crop_r else 0)
    glyph, rest = tag[0], tag[1:]
    gcolor = GLYPHS[glyph][0]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="{x0} 0 {vw} {h + 2 * M}" width="{vw}" height="{h + 2 * M}" role="img" aria-label="{escape(title)}: {escape(desc)}">
<defs><filter id="sh" x="-5%" y="-5%" width="110%" height="120%"><feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#000" flood-opacity=".5"/></filter></defs>
<style>
text{{font-family:-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}}
.t{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11px;font-weight:600;letter-spacing:.08em;fill:{T["violet"]}}}
.pr{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;font-weight:600;fill:{accent}}}
.cm{{fill:{T["fg"]};font-weight:500}}
.h{{font-size:21px;font-weight:700;fill:{T["fg"]}}}
.d{{font-size:13px;fill:{T["soft"]}}}
.c{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11.5px;fill:{T["cyan"]};fill-opacity:.85}}
</style>
<g transform="translate({M} {M})">
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12" fill="{bg}" stroke="{T["border"]}"/>
{titlebar(w, accent, T["border"], "", rx=12)}{tabs(w, accent, T["border"], ["readme", "stack", "shot"], bg, rx=12)}
<g transform="translate(0 {TB})">
{prompt(24, "cat README.md")}
<text x="20" y="48" class="t"><tspan fill="{gcolor}">{glyph}</tspan>{escape(rest)}</text>
<text x="20" y="76" class="h">{escape(title)}</text>
{text}{prompt(p2, "ls stack/")}{imgs}{chip}{pic}
</g>
{status(w, h, commits, langs)}
</g>
</svg>
'''


def status(w, h, commits, langs):
    """Bottom status bar: branch pill, commit count, and the top language with a GitHub-style strip."""
    accent = T["accent"]
    right_w, y = 70, h - SB
    bar = statusbar(w, y, accent, "⎇ main", f"{commits} commits" if commits else "", rx=12, border=T["border"], dark=T["surface"])
    if not langs:
        return bar
    total = sum(langs.values())
    top = max(langs, key=langs.get)
    segs, x = [], w - 14 - right_w
    for name, n in sorted(langs.items(), key=lambda kv: -kv[1]):
        if n / total < MIN_SHARE:
            continue
        sw = n / total * right_w
        segs.append(f'<rect x="{x:.1f}" y="{y + 9}" width="{sw:.1f}" height="6" fill="{LANG_COLORS.get(name, "#8b949e")}"><title>{escape(name)} {n / total:.0%}</title></rect>')
        x += sw
    label = f'<text x="{w - 14 - right_w - 8}" y="{y + SB / 2 + 4}" text-anchor="end" fill="{accent}" fill-opacity=".75" style="font-family:{MONO};font-size:11px;fill:{accent}">{escape(top) + " " if w == HALF else ""}{langs[top] / total:.0%}</text>'
    return f'{bar}{label}<clipPath id="r"><rect x="{w - 14 - right_w}" y="{y + 9}" width="{right_w}" height="6" rx="3"/></clipPath><g clip-path="url(#r)">{"".join(segs)}</g>'


def legend():
    """One-line key for the tag glyphs, placed above the grid."""
    x, parts = 0, []
    for sym, (color, label) in GLYPHS.items():
        parts.append(f'<text x="{x}" y="17"><tspan fill="{color}">{sym}</tspan><tspan fill="{T["dim"]}"> {label}</tspan></text>')
        x += 40 + len(label) * 7.8
    w = round(x - 22)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 24" width="{w}" height="24" role="img" aria-label="Legend: flagship, research, side builds">
<style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13px}}</style>
{"".join(parts)}
</svg>
'''


def card_rows(rows):
    """Write the cards of `rows` and return the README <p> rows that show them (widths in percent)."""
    html = []
    for row in rows:
        w = ROW_WIDTH[len(row)]
        nl = max(len(wrap(PROJECTS[s][2], w)) for s in row)
        total = len(row) * (w + 2 * M) - 2 * M
        imgs = []
        for i, slug in enumerate(row):
            first, last = i == 0, i == len(row) - 1
            (OUT / f"card-{slug}.svg").write_text(
                build(PROJECTS[slug], w, nl, ROW_SHOT_H[len(row)], crop_l=first, crop_r=last, commits=DATA[slug]["commits"],
                      langs=DATA[slug]["languages"], shot=shot_uri(slug)), encoding="utf-8")
            vw = w + 2 * M - (M if first else 0) - (M if last else 0)
            pct = f"{vw / total * 100 - 0.1:.1f}%"
            imgs.append(f'<a href="https://github.com/alexzjss/{REPOS[slug]}"><img src="assets/card-{slug}.svg" width="{pct}" alt="{slug}"></a>')
            print("wrote", f"card-{slug}.svg", pct)
        html.append('<p align="center">' + "".join(imgs) + "</p>")
    return html


def readme_block():
    """The cards of the README: the visible grid and the collapsed `more` block. Replaced between the cards markers."""
    n = sum(len(r) for r in MORE)
    grid = "\n\n".join(card_rows(LAYOUT))
    more = "\n\n".join(card_rows(MORE))
    return (f'<!-- cards:start -->\n<p align="center"><img src="assets/legend-projects.svg" alt="Legend: flagship, research, side builds"></p>\n\n{grid}\n\n'
            f'<details>\n<summary><img src="assets/sec-more.svg" width="100%" alt="$ ls -a ~/projects/more [+{n}]"></summary>\n<br>\n\n{more}\n\n</details>\n<!-- cards:end -->')


if __name__ == "__main__":
    import re
    (OUT / "legend-projects.svg").write_text(legend(), encoding="utf-8")
    block = readme_block()
    readme = OUT.parent / "README.md"
    text = readme.read_text(encoding="utf-8")
    new, n = re.subn(r"<!-- cards:start -->.*?<!-- cards:end -->", lambda _: block, text, flags=re.S)
    if n:
        readme.write_text(new, encoding="utf-8")
        print("updated the cards block in", readme)
    else:
        print("no <!-- cards:start --> / <!-- cards:end --> markers in README.md: add them around the cards to keep the grid in sync")
