"""Generate assets/stack-v2.svg (renamed to bust the GitHub image cache), the tech-stack icon grid of the README (no external icon service).

    python3 scripts/stack.py

Icons come from assets/icons/<name>.svg (curl -o assets/icons/<name>.svg "https://skillicons.dev/icons?i=<name>").
Edit ROWS to change the stack.
"""
from pathlib import Path
from xml.sax.saxutils import escape

from cards import icon_uri
from chrome import frame_svg

OUT = Path(__file__).resolve().parent.parent / "assets" / "stack-v2.svg"

ICON, GAP, LABEL_H, ROW_GAP = 48, 8, 16, 14
LABEL = "#8b949e"

# (label, [(icon, name)], lines of tools without an icon). Four rows of six icons: the grid fills the column evenly.
ROWS = [
    ("languages", [("py", "Python"), ("java", "Java"), ("ts", "TypeScript"), ("js", "JavaScript"), ("cs", "C#"), ("cpp", "C++")], []),
    ("backend, data & ai", [("nodejs", "Node.js"), ("fastapi", "FastAPI"), ("postgres", "PostgreSQL"), ("supabase", "Supabase"), ("sqlite", "SQLite"), ("ollama", "Ollama")],
     ["REST · WebSocket · OAuth · Web Push · Discord", "igraph · H3 · OSMnx · spiking nets · local LLMs"]),
    ("frontend, mobile & tests", [("react", "React / React Native"), ("nextjs", "Next.js"), ("vite", "Vite"), ("tailwind", "Tailwind"), ("jest", "Jest"), ("vitest", "Vitest")],
     ["HTML · CSS · Expo · MapLibre · GUT"]),
    ("devops, build & research", [("docker", "Docker"), ("git", "Git"), ("linux", "Linux"), ("githubactions", "GitHub Actions"), ("vercel", "Vercel"), ("maven", "Maven")],
     ["Jaguar 2 · JaCoCo · fault localization"]),
]
CHIP_H = 16


def build():
    w = max(len(r[1]) for r in ROWS) * (ICON + GAP) - GAP
    heights = [LABEL_H + ICON + (len(r[2]) * CHIP_H + 2 if r[2] else 0) for r in ROWS]
    h = sum(heights) + ROW_GAP * (len(ROWS) - 1)
    body, y = [], 0
    for (label, icons, chips), rh in zip(ROWS, heights):
        body.append(f'<text x="0" y="{y + 11}">{escape(label)}</text>')
        for i, (n, _) in enumerate(icons):
            body.append(f'<image x="{i * (ICON + GAP)}" y="{y + LABEL_H}" width="{ICON}" height="{ICON}" href="{icon_uri(n)}"/>')
        for j, line in enumerate(chips):
            body.append(f'<text x="0" y="{y + LABEL_H + ICON + 13 + j * CHIP_H}" class="c">{escape(line)}</text>')
        y += rh + ROW_GAP
    alt = "; ".join(f"{l}: {', '.join([n for _, n in ic] + c)}" for l, ic, c in ROWS)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Stack. {escape(alt)}">
<style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;fill:{LABEL}}}.c{{font-size:11px;fill:#6e7681}}</style>
{"".join(body)}
</svg>
'''
    n = sum(len(r[1]) for r in ROWS)
    return frame_svg(svg, "tree --grow ~/stack", names=["stack", "tools", "notes"], status=("⎇ main", f"{n} tools · {len(ROWS)} groups", "always growing"), pad=(18, 14))


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print("wrote", OUT)
