"""Generate assets/contrib.svg: the last 12 months of contributions as twelve small calendars, sized for the
left cell of the stack table (about 307x530 on screen, so 328x566 here) and styled like assets/stack-v2.svg.

Each day is colored by the main language of that day's commits (the primary language of the repository that
got the most commits that day, using GitHub's own language colors); the shade says how busy the day was.
Days with contributions but no commits (reviews, issues...) stay neutral gray.

    python3 scripts/contrib.py --demo                      # random data, no token
    GITHUB_TOKEN=... python3 scripts/contrib.py alexzjss   # real data (GraphQL)
"""
import argparse
import calendar
import json
import os
import random
import urllib.request
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "contrib.svg"

W, H = 328, 566
CELL, GAP = 10, 2
PITCH = CELL + GAP
COLS = 3
BLOCK_W = 7 * PITCH - GAP          # 82
LABEL_H = 14
BLOCK_H = LABEL_H + 6 * PITCH      # 86
GX = (W - COLS * BLOCK_W) / (COLS - 1)
TOP, ROW_PITCH = 30, 98
LEGEND_Y, STATS_Y = 428, 494
LEGEND_MAX = 6

LABEL, DIM, EMPTY = "#bfbfbf", "#6272a4", "#21222c"
NEUTRAL = "#8b949e"                                  # contributions that are not commits
SHADE = [0.5, 0.68, 0.85, 1.0]                        # opacity for busy-ness level 1..4
FALLBACK = "#6e7681"                                  # repo without a detected language

QUERY = """query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){contributionsCollection(from:$from,to:$to){
contributionCalendar{weeks{contributionDays{date contributionCount}}}
commitContributionsByRepository(maxRepositories:100){repository{primaryLanguage{name color}}
contributions(first:100){nodes{occurredAt commitCount}}}}}}"""


def months_back(today, n=12):
    y, m = today.year, today.month
    out = []
    for _ in range(n):
        out.append((y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return out[::-1]


def gql(token, variables):
    body = json.dumps({"query": QUERY, "variables": variables}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", body, {
        "Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "contrib-svg"})
    data = json.load(urllib.request.urlopen(req))
    if "errors" in data:
        raise SystemExit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]["contributionsCollection"]


def parse_month(col):
    """One contributionsCollection -> (counts {date: n}, langs {date: {(name, color): commits}})."""
    counts = {d["date"]: d["contributionCount"]
              for w in col["contributionCalendar"]["weeks"] for d in w["contributionDays"]}
    langs = defaultdict(Counter)
    for repo in col["commitContributionsByRepository"]:
        pl = repo["repository"]["primaryLanguage"]
        key = (pl["name"], pl["color"] or FALLBACK) if pl else ("other", FALLBACK)
        for node in repo["contributions"]["nodes"]:
            langs[node["occurredAt"][:10]][key] += node["commitCount"]
    return counts, langs


def fetch(login, token, today):
    """One query per month, so no repository ever has more than ~31 contribution days to page through."""
    counts, langs = {}, defaultdict(Counter)
    for y, m in months_back(today):
        last = min(date(y, m, calendar.monthrange(y, m)[1]), today)
        c, l = parse_month(gql(token, {"login": login, "from": f"{y}-{m:02d}-01T00:00:00Z",
                                       "to": f"{last}T23:59:59Z"}))
        counts.update({k: v for k, v in c.items() if k.startswith(f"{y}-{m:02d}-")})
        for k, v in l.items():
            if k.startswith(f"{y}-{m:02d}-"):
                langs[k].update(v)
    return counts, langs


def demo(today):
    rnd = random.Random(7)
    pool = [(("Python", "#3572A5"), 5), (("TypeScript", "#3178c6"), 5), (("Java", "#b07219"), 3),
            (("JavaScript", "#f1e05a"), 3), (("C#", "#178600"), 1), (("C++", "#f34b7d"), 1)]
    names, weights = zip(*pool)
    counts, langs = {}, defaultdict(Counter)
    d = date(*months_back(today)[0], 1)
    cur = rnd.choice(names)                      # languages come in streaks, like real project work
    while d <= today:
        if rnd.random() < 0.25:
            cur = rnd.choices(names, weights)[0]
        busy = 0.35 + 0.25 * ((d.month % 5) / 4)
        n = 0 if rnd.random() > busy else int(rnd.expovariate(1 / 4)) + 1
        counts[d.isoformat()] = n
        if n and rnd.random() > 0.08:            # a few days with no commits at all
            langs[d.isoformat()][cur] += n
        d += timedelta(days=1)
    return counts, langs


def levels(counts):
    nz = sorted(c for c in counts.values() if c > 0)
    if not nz:
        return lambda c: 0
    q = [nz[int(len(nz) * f)] for f in (0.25, 0.5, 0.75)]
    return lambda c: 0 if c <= 0 else 1 + sum(c > t for t in q)


def streaks(counts, today):
    best = run = 0
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


def build(counts, langs, today):
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
            iso = d.isoformat()
            pos = first_wd + day - 1
            x, yy = bx + (pos % 7) * PITCH, by + LABEL_H + (pos // 7) * PITCH
            lv = lvl(counts.get(iso, 0))
            if lv == 0:
                fill, op = EMPTY, 1
            else:
                top = langs[iso].most_common(1) if iso in langs else []
                fill, op = (top[0][0][1] if top else NEUTRAL), SHADE[lv - 1]
            parts.append(f'<rect x="{x:.1f}" y="{yy:.1f}" width="{CELL}" height="{CELL}" rx="2" fill="{fill}" '
                         f'fill-opacity="{op}" class="d" style="animation-delay:{idx * 0.012:.2f}s"/>')
            idx += 1
    # legend: the languages with the most commits in the period, in two columns of three
    by_lang = Counter()
    for c in langs.values():
        by_lang.update(c)
    top = by_lang.most_common(LEGEND_MAX)
    legend = []
    for i, ((name, color), n) in enumerate(top):
        lx, ly = (i % 2) * (W / 2), LEGEND_Y + (i // 2) * 18
        legend.append(f'<rect x="{lx:.1f}" y="{ly - 9}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>'
                      f'<text x="{lx + 16:.1f}" y="{ly}">{name.lower()}</text>')
    cur, best = streaks(counts, today)
    active = sum(1 for v in counts.values() if v > 0)
    rows = [("total", f"{total}"), ("active days", f"{active}"), ("best day", f"{max(counts.values())}"),
            ("streak", f"{cur}d now · {best}d best")]
    stats = "".join(f'<text x="0" y="{STATS_Y + i * 20}">{k}<tspan class="v" x="{W}" text-anchor="end">{v}</tspan></text>'
                    for i, (k, v) in enumerate(rows))
    sx = W - 34 - 5 * PITCH                      # five squares (empty + 4 shades), "less" left, "more" right
    shades = f'<rect x="{sx}" y="2" width="{CELL}" height="{CELL}" rx="2" fill="{EMPTY}"/>' + "".join(
        f'<rect x="{sx + (i + 1) * PITCH}" y="2" width="{CELL}" height="{CELL}" rx="2" fill="{NEUTRAL}" '
        f'fill-opacity="{o}"/>' for i, o in enumerate(SHADE))
    head = (f'<text x="0" y="11">contributions</text><text x="{sx - 5}" y="11" class="c" text-anchor="end">less</text>'
            f'{shades}<text x="{W}" y="11" class="c" text-anchor="end">more</text>')
    names = ", ".join(n for (n, _), _ in top)
    alt = (f"Contributions over the last 12 months: {total} in total, shown as twelve small calendars, "
           f"each day colored by its main commit language ({names}).")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{alt}">
<style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;fill:{LABEL}}}.c{{font-size:11px;fill:{DIM}}}.v{{fill:#c9d1d9}}
.d{{opacity:0;animation:in .5s ease-out forwards;transform-box:fill-box;transform-origin:center}}
@keyframes in{{from{{opacity:0;transform:scale(.4)}}to{{opacity:1;transform:scale(1)}}}}
@media (prefers-reduced-motion:reduce){{.d{{animation:none;opacity:1}}}}</style>
{head}
{chr(10).join(parts)}
{"".join(legend)}
{stats}
</svg>
'''
    from chrome import frame_svg
    from themes import DRACULA as T
    return frame_svg(svg, "git log --since=12.months", names=["commits", "calendar"], status=("⎇ main", f"{total} contributions", "12 months"), color=T["accent"], border=T["border"], bg=T["bg"], dark=T["surface"], pad=(14, 12))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("login", nargs="?")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    today = date.today()
    if a.demo:
        counts, langs = demo(today)
    else:
        token = os.environ.get("GITHUB_TOKEN")
        if not (a.login and token):
            raise SystemExit("need a login and GITHUB_TOKEN (or use --demo)")
        counts, langs = fetch(a.login, token, today)
    Path(a.out).write_text(build(counts, langs, today), encoding="utf-8")
    print("wrote", a.out, f"({sum(counts.values())} contributions)")
