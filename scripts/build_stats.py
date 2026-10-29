"""Builds the activity card from the GitHub API, in the same style as the rest.

    GITHUB_TOKEN=... python3 scripts/build_stats.py Luizfbm dist

Runs daily in .github/workflows/profile.yml, which publishes dist/ to the
`output` branch. Locally, `gh auth token` works as the token.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from collections import Counter
from pathlib import Path

from readme_kit import PALETTES, REDUCED_MOTION, Doc, fmt, measure, section_head

W = 880

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100) {
      totalCount
      nodes {
        isFork
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      contributionCalendar { totalContributions }
    }
  }
}
"""


def fetch(login: str, token: str) -> dict:
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        payload = json.load(res)
    if payload.get("errors"):
        raise SystemExit(f"GitHub API error: {payload['errors']}")
    return payload["data"]["user"]


def summarize(user: dict) -> tuple[list[tuple[str, str]], list[tuple[str, float]]]:
    c = user["contributionsCollection"]
    repos = user["repositories"]
    numbers = [
        ("contributions, 12 mo", f'{c["contributionCalendar"]["totalContributions"]:,}'),
        ("public commits", f'{c["totalCommitContributions"]:,}'),
        ("pull requests", f'{c["totalPullRequestContributions"]:,}'),
        ("public repos", f'{repos["totalCount"]}'),
    ]

    sizes: Counter[str] = Counter()
    for repo in repos["nodes"]:
        if repo["isFork"]:
            continue
        for edge in repo["languages"]["edges"]:
            sizes[edge["node"]["name"]] += edge["size"]
    total = sum(sizes.values()) or 1
    top = sizes.most_common(5)
    langs = [(name, size / total) for name, size in top]
    rest = 1 - sum(share for _, share in langs)
    if rest > 0.005:
        langs.append(("Other", rest))
    return numbers, langs


def card(theme: str, numbers: list[tuple[str, str]], langs: list[tuple[str, float]]) -> Doc:
    p = PALETTES[theme]
    h = 84 + 96 + 96
    doc = Doc(W, h, theme, "GitHub activity: " + "; ".join(f"{label} {value}" for label, value in numbers))
    y = section_head(doc, 0, "Activity", "Last 12 months on GitHub, private work included. Refreshed daily.")

    gap = 24
    cw = (W - gap * (len(numbers) - 1)) / len(numbers)
    doc.css.append(
        ".c{animation:rise .9s cubic-bezier(.16,1,.3,1) both}"
        "@keyframes rise{from{opacity:0;transform:translateY(8px)}}"
        ".bar{animation:grow 1.4s cubic-bezier(.16,1,.3,1) .5s both;transform-origin:0 0}"
        "@keyframes grow{from{transform:scaleX(0)}}"
    )
    for i, (label, value) in enumerate(numbers):
        x = i * (cw + gap)
        doc.add(f'<g class="c" style="animation-delay:{0.1 + i * 0.1:.2f}s">')
        doc.add(f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(cw)}" height="1" fill="{p["rule"]}"/>')
        doc.text(x, y + 24, label.upper(), "mono", 10.5, p["ink3"], tracking=0.08)
        doc.text(x, y + 66, value, "title", 32, p["ink"], tracking=-0.03)
        doc.add("</g>")
    y += 96

    # Language share as one monochrome bar, strongest first.
    doc.add(f'<rect x="0" y="{fmt(y)}" width="{W}" height="1" fill="{p["rule"]}"/>')
    doc.text(0, y + 24, "LANGUAGES, BY BYTES IN PUBLIC REPOS", "mono", 10.5, p["ink3"], tracking=0.08)
    shades = [1, 0.7, 0.5, 0.34, 0.22, 0.12]
    bar_y, x = y + 40, 0.0
    doc.defs.append(f'<clipPath id="bar"><rect x="0" y="{fmt(bar_y)}" width="{W}" height="8" rx="4"/></clipPath>')
    doc.add('<g clip-path="url(#bar)"><g class="bar">')
    for (name, share), shade in zip(langs, shades):
        w = share * W
        doc.add(f'<rect x="{fmt(x)}" y="{fmt(bar_y)}" width="{fmt(max(w - 2, 1))}" height="8" fill="{p["ink"]}" opacity="{shade}"/>')
        x += w
    doc.add("</g></g>")
    x = 0.0
    for (name, share), shade in zip(langs, shades):
        doc.add(f'<rect x="{fmt(x)}" y="{fmt(bar_y + 25)}" width="8" height="8" rx="2" fill="{p["ink"]}" opacity="{shade}"/>')
        text = f"{name} {share * 100:.1f}%"
        doc.text(x + 14, bar_y + 33, text, "mono", 11, p["ink2"])
        x += 14 + measure(text, "mono", 11) + 22
    doc.css.append(REDUCED_MOTION)
    return doc


def main() -> None:
    login = sys.argv[1] if len(sys.argv) > 1 else "Luizfbm"
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "dist")
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is not set")
    numbers, langs = summarize(fetch(login, token))
    out.mkdir(parents=True, exist_ok=True)
    for theme in PALETTES:
        path = out / f"activity-{theme}.svg"
        path.write_text(card(theme, numbers, langs).render(), encoding="utf-8")
        print(path)


if __name__ == "__main__":
    main()
