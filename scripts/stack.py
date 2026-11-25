"""Generate assets/stack.svg, the tech-stack icon grid of the README (no external icon service).

    python3 scripts/stack.py

Icons come from assets/icons/<name>.svg (curl -o assets/icons/<name>.svg "https://skillicons.dev/icons?i=<name>").
Edit ROWS to change the stack.
"""
from pathlib import Path
from xml.sax.saxutils import escape

from cards import icon_uri

OUT = Path(__file__).resolve().parent.parent / "assets" / "stack.svg"

ICON, GAP, LABEL_H, ROW_GAP = 48, 8, 16, 14
LABEL = "#8b949e"

# (label, [(icon, name)], optional line of tools without an icon)
ROWS = [
    ("languages", [("py", "Python"), ("java", "Java"), ("ts", "TypeScript"), ("js", "JavaScript"), ("cs", "C#"), ("cpp", "C++"), ("ps", "PowerShell"), ("bash", "Bash")], ""),
    ("backend & data", [("nodejs", "Node.js"), ("fastapi", "FastAPI"), ("postgres", "PostgreSQL"), ("supabase", "Supabase"), ("sqlite", "SQLite"), ("discord", "Discord API")], "REST · WebSocket · OAuth · Web Push"),
    ("frontend & mobile", [("react", "React / React Native"), ("nextjs", "Next.js"), ("vite", "Vite"), ("tailwind", "Tailwind"), ("html", "HTML"), ("css", "CSS")], "Expo · MapLibre · design tokens"),
    ("testing & analysis", [("maven", "Maven"), ("jest", "Jest"), ("vitest", "Vitest")], "Jaguar 2 · JaCoCo · GUT · fault localization"),
    ("geospatial & ML/AI", [("ollama", "Ollama")], "igraph · H3 · OSMnx · spiking nets · local LLMs"),
    ("devops & cloud", [("docker", "Docker"), ("git", "Git"), ("linux", "Linux"), ("githubactions", "GitHub Actions"), ("vercel", "Vercel")], ""),
    ("games & graphics", [("godot", "Godot"), ("pygame", "pygame"), ("threejs", "Three.js")], ""),
]
CHIP_H = 18


def build():
    w = max(len(r[1]) for r in ROWS) * (ICON + GAP) - GAP
    heights = [LABEL_H + ICON + (CHIP_H if r[2] else 0) for r in ROWS]
    h = sum(heights) + ROW_GAP * (len(ROWS) - 1)
    body, y = [], 0
    for (label, icons, chips), rh in zip(ROWS, heights):
        body.append(f'<text x="0" y="{y + 11}">{escape(label)}</text>')
        for i, (n, _) in enumerate(icons):
            body.append(f'<image x="{i * (ICON + GAP)}" y="{y + LABEL_H}" width="{ICON}" height="{ICON}" href="{icon_uri(n)}"/>')
        if chips:
            body.append(f'<text x="0" y="{y + LABEL_H + ICON + 13}" class="c">{escape(chips)}</text>')
        y += rh + ROW_GAP
    alt = "; ".join(f"{l}: {', '.join([n for _, n in ic] + ([c] if c else []))}" for l, ic, c in ROWS)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Stack. {escape(alt)}">
<style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;fill:{LABEL}}}.c{{font-size:11px;fill:#6e7681}}</style>
{"".join(body)}
</svg>
'''


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print("wrote", OUT)
