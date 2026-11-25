"""Generate assets/contrib.svg: the last 12 months of contributions as twelve small calendars, sized for the
left cell of the stack table (about 307x530 on screen, so 328x566 here) and styled like assets/stack-v2.svg.

    python3 scripts/contrib.py --demo                      # random data, no token
    GITHUB_TOKEN=... python3 scripts/contrib.py alexzjss   # real data (GraphQL contributionCalendar)

Colors are the coral ramp of the stack banner. Edit RAMP / geometry below to restyle.
"""
import argparse
import calendar
import json
import os
import random
import urllib.request
from datetime import date, timedelta
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "contrib.svg"

W, H = 328, 566
CELL, GAP = 10, 2
PITCH = CELL + GAP
COLS, ROWS = 3, 4
BLOCK_W = 7 * PITCH - GAP          # 82
LABEL_H = 14
BLOCK_H = LABEL_H + 6 * PITCH      # 86
GX = (W - COLS * BLOCK_W) / (COLS - 1)
TOP, ROW_PITCH = 30, 112

LABEL, DIM = "#8b949e", "#6e7681"
RAMP = ["#161b22", "#4a1f1c", "#8a3a35", "#c9524a", "#ff7b72"]   # empty .. busiest

QUERY = """query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){contributionsCollection(from:$from,to:$to){
contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"""


def months_back(today, n=12):
    y, m = today.year, today.month
    out = []
    for _ in range(n):
        out.append((y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return out[::-1]


def fetch(login, token, today):
    start = months_back(today)[0]
    frm = date(start[0], start[1], 1)
    body = json.dumps({"query": QUERY, "variables": {
        "login": login, "from": f"{frm}T00:00:00Z", "to": f"{today}T23:59:59Z"}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", body, {
        "Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "contrib-svg"})
    data = json.load(urllib.request.urlopen(req))
    if "errors" in data:
        raise SystemExit(f"GraphQL error: {data['errors']}")
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return {d["date"]: d["contributionCount"] for w in weeks for d in w["contributionDays"]}


def demo(today):
    rnd = random.Random(7)
    out, d = {}, months_back(today)[0]
    d = date(d[0], d[1], 1)
    while d <= today:
        busy = 0.35 + 0.25 * ((d.month % 5) / 4)
        out[d.isoformat()] = 0 if rnd.random() > busy else int(rnd.expovariate(1 / 4)) + 1
        d += timedelta(days=1)
    return out


def levels(counts):
    nz = sorted(c for c in counts.values() if c > 0)
    if not nz:
        return lambda c: 0
    q = [nz[int(len(nz) * f)] for f in (0.25, 0.5, 0.75)]
    return lambda c: 0 if c <= 0 else 1 + sum(c > t for t in q)


def streaks(counts, today):
    best = cur = run = 0
    d = date.fromisoformat(min(counts))
    while d <= today:
        run = run + 1 if counts.get(d.isoformat(), 0) > 0 else 0
        best = max(best, run)
        d += timedelta(days=1)
    d, cur = today, 0
    if counts.get(d.isoformat(), 0) == 0:
        d -= timedelta(days=1)          # today may simply not have happened yet
    while counts.get(d.isoformat(), 0) > 0:
        cur += 1
        d -= timedelta(days=1)
    return cur, best


def build(counts, today):
    lvl = levels(counts)
    parts, idx = [], 0
    total = sum(counts.values())
    for i, (y, m) in enumerate(months_back(today)):
        bx = (i % COLS) * (BLOCK_W + GX)
        by = TOP + (i // COLS) * ROW_PITCH
        n_month = sum(v for k, v in counts.items() if k.startswith(f"{y}-{m:02d}-"))
        parts.append(f'<text x="{bx:.1f}" y="{by + 10:.1f}">{calendar.month_abbr[m].lower()}'
                     f'<tspan class="c" dx="5">{n_month}</tspan></text>')
        first_wd = (date(y, m, 1).weekday() + 1) % 7          # Sunday = 0
        for day in range(1, calendar.monthrange(y, m)[1] + 1):
            d = date(y, m, day)
            if d > today:
                continue
            pos = first_wd + day - 1
            col, row = pos % 7, pos // 7
            lv = lvl(counts.get(d.isoformat(), 0))
            x, yy = bx + col * PITCH, by + LABEL_H + row * PITCH
            delay = idx * 0.012
            idx += 1
            parts.append(f'<rect x="{x:.1f}" y="{yy:.1f}" width="{CELL}" height="{CELL}" rx="2" fill="{RAMP[lv]}" '
                         f'class="d" style="animation-delay:{delay:.2f}s"/>')
    cur, best = streaks(counts, today)
    busiest = max(counts.values())
    active = sum(1 for v in counts.values() if v > 0)
    y0 = TOP + 3 * ROW_PITCH + BLOCK_H + 30
    rows = [("total", f"{total}"), ("active days", f"{active}"), ("best day", f"{busiest}"),
            ("streak", f"{cur}d now · {best}d best")]
    stats = "".join(f'<text x="0" y="{y0 + i * 20}">{k}<tspan class="v" x="{W - 0}" text-anchor="end">{v}</tspan></text>'
                    for i, (k, v) in enumerate(rows))
    lx = W - 5 * PITCH - 26
    legend = (f'<text x="{lx - 6}" y="11" class="c" text-anchor="end">less</text>'
              + "".join(f'<rect x="{lx + i * PITCH}" y="2" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>'
                        for i, c in enumerate(RAMP))
              + f'<text x="{lx + 5 * PITCH + 4}" y="11" class="c">more</text>')
    parts.insert(0, '<text x="0" y="11">contributions</text>')
    parts += [stats, legend]
    alt = f"Contributions over the last 12 months: {total} in total, shown as twelve small calendars."
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{alt}">
<style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;fill:{LABEL}}}.c{{font-size:11px;fill:{DIM}}}.v{{fill:#c9d1d9}}
.d{{opacity:0;animation:in .5s ease-out forwards}}@keyframes in{{from{{opacity:0;transform:scale(.4)}}to{{opacity:1;transform:scale(1)}}}}
.d{{transform-box:fill-box;transform-origin:center}}
@media (prefers-reduced-motion:reduce){{.d{{animation:none;opacity:1}}}}</style>
{chr(10).join(parts)}
</svg>
'''


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("login", nargs="?")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    today = date.today()
    if a.demo:
        counts = demo(today)
    else:
        token = os.environ.get("GITHUB_TOKEN")
        if not (a.login and token):
            raise SystemExit("need a login and GITHUB_TOKEN (or use --demo)")
        counts = fetch(a.login, token, today)
    Path(a.out).write_text(build(counts, today), encoding="utf-8")
    print("wrote", a.out, f"({sum(counts.values())} contributions)")
