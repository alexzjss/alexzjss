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

# (label, [(icon, name)])
ROWS = [
    ("languages", [("py", "Python"), ("java", "Java"), ("ts", "TypeScript"), ("js", "JavaScript"), ("cpp", "C++")]),
    ("frontend", [("react", "React"), ("nextjs", "Next.js"), ("vite", "Vite"), ("tailwind", "Tailwind"), ("html", "HTML"), ("css", "CSS")]),
    ("backend & data", [("nodejs", "Node.js"), ("fastapi", "FastAPI"), ("postgres", "PostgreSQL"), ("supabase", "Supabase"), ("sqlite", "SQLite")]),
    ("tools", [("docker", "Docker"), ("git", "Git"), ("linux", "Linux"), ("githubactions", "GitHub Actions"), ("maven", "Maven"), ("godot", "Godot"), ("vercel", "Vercel")]),
]


def build():
    w = max(len(r[1]) for r in ROWS) * (ICON + GAP) - GAP
    h = len(ROWS) * (LABEL_H + ICON + ROW_GAP) - ROW_GAP
    body, y = [], 0
    for label, icons in ROWS:
        body.append(f'<text x="0" y="{y + 11}">{escape(label)}</text>')
        for i, (n, _) in enumerate(icons):
            body.append(f'<image x="{i * (ICON + GAP)}" y="{y + LABEL_H}" width="{ICON}" height="{ICON}" href="{icon_uri(n)}"/>')
        y += LABEL_H + ICON + ROW_GAP
    alt = "; ".join(f"{l}: {', '.join(n for _, n in ic)}" for l, ic in ROWS)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Stack. {escape(alt)}">
<style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;fill:{LABEL}}}</style>
{"".join(body)}
</svg>
'''


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print("wrote", OUT)
