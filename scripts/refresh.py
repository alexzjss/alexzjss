"""Fetch commit counts and language bytes of the project repos into scripts/data.json.

    GITHUB_TOKEN=... python3 scripts/refresh.py     # token optional locally, raises the rate limit

scripts/cards.py reads that file, so the numbers on the cards are never typed by hand.
"""
import json
import os
import re
import urllib.request
from pathlib import Path

OWNER = "alexzjss"
# card slug: repo name
REPOS = {
    "dasiboard": "dasiboard-omg", "sampanav": "SampaNav", "engrama": "engrama", "jflp": "jflp",
    "money": "money", "acha-promocoes": "acha-promocoes", "modaloop": "modaloop", "vat": "vat",
    "icndy": "ICNDY", "website": "website", "eco-fruta": "eco-fruta",
}
OUT = Path(__file__).resolve().parent / "data.json"


def get(path):
    req = urllib.request.Request(f"https://api.github.com/{path}", headers={"Accept": "application/vnd.github+json"})
    if token := os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {token}")
    return urllib.request.urlopen(req)


def commits(repo):
    """With per_page=1 the last page number of the Link header is the commit count."""
    r = get(f"repos/{OWNER}/{repo}/commits?per_page=1")
    m = re.search(r'[?&]page=(\d+)>; rel="last"', r.headers.get("Link", ""))
    return int(m.group(1)) if m else len(json.load(r))


if __name__ == "__main__":
    data = {}
    for slug, repo in REPOS.items():
        data[slug] = {"commits": commits(repo), "languages": json.load(get(f"repos/{OWNER}/{repo}/languages"))}
        print(slug, data[slug]["commits"], list(data[slug]["languages"])[:3])
    OUT.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
