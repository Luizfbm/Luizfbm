"""Builds the activity card from the GitHub API, in the same style as the rest.

    GITHUB_TOKEN=... python3 scripts/build_stats.py Luizfbm dist

Runs daily in .github/workflows/profile.yml, which publishes dist/ to the
`output` branch. Locally, `gh auth token` works as the token.

The card is written for someone who doesn't read code: plain sentences
about how often and how recently I ship, plus the contribution map.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

from readme_kit import PALETTES, REDUCED_MOTION, Doc, fmt, section_head

W = 880
# Past this, "last code pushed" would read as a gap, so the card leaves it out.
RECENT_DAYS = 7

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100) {
      nodes {
        isFork
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}
"""

LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
LEVEL_OPACITY = [0.08, 0.3, 0.52, 0.76, 1.0]


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


def relative_day(day: date, today: date) -> str | None:
    gap = (today - day).days
    if gap > RECENT_DAYS:
        return None
    if gap <= 0:
        return "today"
    if gap == 1:
        return "yesterday"
    return f"{gap} days ago"


def summarize(user: dict, today: date) -> dict:
    calendar = user["contributionsCollection"]["contributionCalendar"]
    weeks = calendar["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    active_weeks = sum(1 for w in weeks if any(d["contributionCount"] for d in w["contributionDays"]))
    last = max((date.fromisoformat(d["date"]) for d in days if d["contributionCount"]), default=None)

    sizes: Counter[str] = Counter()
    for repo in user["repositories"]["nodes"]:
        if repo["isFork"]:
            continue
        for edge in repo["languages"]["edges"]:
            sizes[edge["node"]["name"]] += edge["size"]
    top = [name for name, _ in sizes.most_common(2)]

    return {
        "weeks": weeks,
        "active_weeks": active_weeks,
        "total_weeks": len(weeks),
        "contributions": calendar["totalContributions"],
        "last": relative_day(last, today) if last else None,
        "languages": " and ".join(top),
    }


def card(theme: str, s: dict) -> Doc:
    p = PALETTES[theme]
    cell, gap = 13, 3.4
    map_h = 7 * (cell + gap)
    h = 84 + 112 + 22 + map_h + 60
    numbers = [
        (f'{s["active_weeks"]} of {s["total_weeks"]}', "weeks with code shipped"),
        (f'{s["contributions"]:,}', "contributions, private work included"),
    ]
    if s["last"]:
        numbers.append((s["last"], "last time I pushed code"))
    doc = Doc(W, h, theme, "GitHub activity: " + "; ".join(f"{v} {label}" for v, label in numbers)
              + f'. Mostly {s["languages"]}.')
    y = section_head(doc, 0, "Activity", "Last 12 months on GitHub. Updated every day.")
    doc.css.append(
        ".c{animation:rise .9s cubic-bezier(.16,1,.3,1) both}"
        "@keyframes rise{from{opacity:0;transform:translateY(8px)}}"
        ".d{animation:pop .5s ease-out both}@keyframes pop{from{opacity:0}}" + REDUCED_MOTION
    )

    col_w = W / 3
    for i, (value, label) in enumerate(numbers):
        x = i * col_w
        doc.add(f'<g class="c" style="animation-delay:{0.1 + i * 0.12:.2f}s">')
        doc.add(f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(col_w - 24)}" height="1" fill="{p["rule"]}"/>')
        doc.text(x, y + 50, value, "title", 34, p["ink"], tracking=-0.03)
        doc.text(x, y + 78, label, "body", 14, p["ink2"])
        doc.add("</g>")
    y += 112

    # Contribution map: one column per week, oldest on the left.
    weeks = s["weeks"]
    step = cell + gap
    x0 = W - len(weeks) * step + gap
    last_month = None
    for wi, week in enumerate(weeks):
        first = date.fromisoformat(week["contributionDays"][0]["date"])
        if first.month != last_month and first.day <= 7 and wi < len(weeks) - 2:
            doc.text(x0 + wi * step, y + 8, first.strftime("%b").upper(), "mono", 9.5, p["ink3"], tracking=0.06)
            last_month = first.month
        for day in week["contributionDays"]:
            dow = (date.fromisoformat(day["date"]).weekday() + 1) % 7  # Sunday first, like GitHub
            level = LEVELS[day["contributionLevel"]]
            doc.add(
                f'<rect class="d" style="animation-delay:{0.3 + wi * 0.012:.3f}s" x="{fmt(x0 + wi * step)}" '
                f'y="{fmt(y + 22 + dow * step)}" width="{cell}" height="{cell}" rx="2.5" '
                f'fill="{p["ink"]}" opacity="{LEVEL_OPACITY[level]}"/>'
            )
    y += 22 + map_h + 20

    doc.text(0, y + 14, f'Mostly {s["languages"]}.', "body", 14, p["ink2"])
    # Legend, right aligned: less ▢▢▢▢▢ more
    lx = W - 5 * 13 - 34
    doc.text(lx - 8, y + 14, "LESS", "mono", 9.5, p["ink3"], tracking=0.06, anchor="end")
    for k, op in enumerate(LEVEL_OPACITY):
        doc.add(f'<rect x="{fmt(lx + k * 13)}" y="{fmt(y + 4)}" width="10" height="10" rx="2" fill="{p["ink"]}" opacity="{op}"/>')
    doc.text(lx + 5 * 13 + 4, y + 14, "MORE", "mono", 9.5, p["ink3"], tracking=0.06)
    return doc


def main() -> None:
    login = sys.argv[1] if len(sys.argv) > 1 else "Luizfbm"
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "dist")
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is not set")
    stats = summarize(fetch(login, token), datetime.now(timezone.utc).date())
    out.mkdir(parents=True, exist_ok=True)
    for theme in PALETTES:
        path = out / f"activity-{theme}.svg"
        path.write_text(card(theme, stats).render(), encoding="utf-8")
        print(path)


if __name__ == "__main__":
    main()
