"""Builds the static README SVGs into assets/, one dark and one light file each.

    python3 scripts/build_assets.py

Copy lives in this file. Change it here and run again.
"""

from __future__ import annotations

import base64
import math
from pathlib import Path

from readme_kit import (
    PALETTES,
    REDUCED_MOTION,
    Doc,
    fmt,
    grain,
    measure,
    section_head,
    wrap,
    wrap_items,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
W = 880

PORTFOLIO = "portfolio.luizfbm.win"

STATEMENT = (
    "I take messy operations in healthcare, education, ERP and customer support "
    "and get them live. AI only comes in when it cuts time or risk."
)
STATEMENT_ASIDE = "Portuguese native, English C1. Open to full stack, mobile and applied-AI roles."

IMPACT = [
    ("query time", "36s → 3s", "Portfolio query at PVT Software"),
    ("sql authoring", "15 → 5 min", "Anti-hallucination layer for agents that read the ERP"),
    ("build + deploy", "2d → <3h", "EAS and GitHub Actions on 30+ white-label apps"),
    ("reach", "3.5M", "Students on the internship flows I maintained"),
]

EXPERIENCE = [
    {
        "company": "PVT Software",
        "title": "Full Stack Developer",
        "period": "now",
        "summary": "Shipping and running internal systems, ERP integrations and AI agents wired into the database.",
        "bullets": [
            "Anti-hallucination layer for agents that write SQL and read the ERP: ~15-minute tasks now take 5, and the team adopted it.",
            "Portfolio query went from 36 seconds to 3.",
            "Blue/green deploys with PM2 and Nginx, with rollback when the new version doesn't hold up.",
            "TOTVS RM integration through DataServer and REST/SOAP TBC.",
        ],
        "stack": ["C#", "NestJS", "SQL", "Docker", "Next.js", "React", "TypeScript", "Tailwind"],
    },
    {
        "company": "S_line",
        "title": "Web and Mobile Developer",
        "period": "before",
        "summary": "Moved legacy apps onto a white-label base and cut the build cycle down.",
        "bullets": [
            "Migrated FlutterFlow apps to React Native, TypeScript, Node.js and REST APIs.",
            "Refactored 48+ screens and modules used by labs across Brazil.",
            "CI/CD with EAS and GitHub Actions: build and deploy went from 2 days to under 3 hours.",
        ],
        "stack": ["React Native", "TypeScript", "Node.js", "EAS", "GitHub Actions"],
    },
    {
        "company": "Super Estágios",
        "title": "Web Developer Intern",
        "period": "jul – oct 2025",
        "summary": "Maintained flows on Brazil's largest internship platform.",
        "bullets": [
            "Worked on flows used by 3.5 million students.",
            "Fixed queries, screens and integrations on MySQL and AWS, with an eye on performance and data consistency.",
        ],
        "stack": ["PHP", "JavaScript", "MySQL", "AWS"],
    },
]

CASES = [
    {
        "slug": "chrono-crash",
        "name": "Chrono Crash",
        "context": "Full-stack challenge",
        "headline": "Crash game with real money, realtime and observability.",
        "readings": [
            ("services", "2, Game and Wallet"),
            ("messaging", "RabbitMQ, outbox/inbox"),
            ("fairness", "HMAC SHA-256"),
            ("coverage", "84.58%"),
        ],
        "stack": ["NestJS", "React/Vite", "RabbitMQ", "Keycloak", "Kong", "Prisma", "Socket.IO", "OpenTelemetry"],
        "repo": "Luizfbm/fullstack-challenge",
    },
    {
        "slug": "iaejovem",
        "name": "IAeJovem",
        "context": "HackFaesa 2025",
        "headline": "Emotional support inside the school routine, without exposing what the student says.",
        "readings": [
            ("roles", "student, teacher, admin"),
            ("score", "0 to 10, chat stays closed"),
            ("ai", "Abacus.AI, streaming"),
            ("trail", "audit of sensitive actions"),
        ],
        "stack": ["Next.js 14", "TypeScript", "PostgreSQL", "Prisma", "NextAuth", "Abacus.AI"],
        "repo": "Luizfbm/IAeJovem-HackFaesa2025",
    },
    {
        "slug": "case-flow",
        "name": "Case Flow",
        "context": "InovaApp 2025",
        "headline": "Loose conversation goes in, an organized ticket comes out.",
        "readings": [
            ("input", "message → ticket"),
            ("status", "4 Kanban columns"),
            ("roles", "Admin, IT, Support, Finance"),
            ("history", "chat becomes context"),
        ],
        "stack": ["Next.js", "TypeScript", "PostgreSQL", "Prisma", "NextAuth", "NLP"],
        "repo": "Luizfbm/CaseFlow-EQPDEV",
    },
    {
        "slug": "dev-roast",
        "name": "Dev-roast",
        "context": "AI code review",
        "headline": "AI code review that ends in a page worth sharing.",
        "readings": [
            ("render", "server-first"),
            ("types", "Drizzle → tRPC → React"),
            ("highlight", "Shiki on the server"),
            ("output", "shareable page + OG"),
        ],
        "stack": ["Next.js 16", "React 19", "tRPC", "TanStack Query", "Drizzle", "Tailwind v4", "Gemini"],
        "repo": "Luizfbm/Dev-roast",
    },
]

STACK = [
    ("Languages", ["TypeScript", "JavaScript", "C#", "PHP", "Python", "Java", "SQL"]),
    ("Frameworks", ["React", "Next.js", "React Native", "Node.js", "NestJS", "Laravel", "Tailwind", "FastAPI"]),
    ("Data", ["PostgreSQL", "MySQL", "SQL Server", "Redis", "Prisma", "Drizzle", "SQLite"]),
    ("Operations", ["Docker", "Nginx", "PM2", "AWS", "GitHub Actions", "EAS", "CI/CD", "GitFlow"]),
    ("Applied AI", ["RAG", "Prompt Engineering", "NLP", "Streaming API", "MCP", "Agentic Workflows"]),
    ("Quality", ["TDD", "Automated tests", "RNTL", "SOLID", "REST APIs"]),
]

CONTACT = [
    ("email", "contatoluizfbm@gmail.com"),
    ("linkedin", "linkedin.com/in/luizfilipedev"),
    ("portfolio", PORTFOLIO),
]

CARD_GAP = 10

EASE_OUT = "cubic-bezier(.16,1,.3,1)"
EASE_LIGHT = "cubic-bezier(.33,0,.15,1)"


def background(doc: Doc) -> None:
    p = doc.p
    doc.defs.append(
        f'<linearGradient id="sweep" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{p["sweep_top"]}"/><stop offset="1" stop-color="{p["sweep_bottom"]}"/>'
        f"</linearGradient>"
    )
    doc.add('<rect width="100%" height="100%" fill="url(#sweep)"/>')


def beams(doc: Doc, specs: list[tuple[float, float, float]], slope: float, gid: str = "beams") -> None:
    """Defines the portfolio's diagonal light beams as #<gid> (drawn with <use>).

    Each spec is (x at the top edge, width, strength). `slope` is how far a
    beam moves right per px down.
    """
    p = doc.p
    gain = p["beam_gain"]
    h = doc.height
    shift = slope * h
    skew = fmt(math.degrees(math.atan(slope)))
    polys = []
    for i, (x, w, s) in enumerate(specs):
        s *= gain
        stops = [
            (0, p["shade"], 0.0),
            (0.3, p["shade"], 0.10 * s),
            (0.62, p["beam"], 0.06 * s),
            (0.86, p["beam"], 0.30 * s),
            (0.9, p["beam"], 0.62 * s),
            (0.94, p["beam"], 0.12 * s),
            (1, p["beam"], 0.0),
        ]
        stop_xml = "".join(
            f'<stop offset="{o}" stop-color="{c}" stop-opacity="{fmt(min(a, 1))}"/>' for o, c, a in stops
        )
        doc.defs.append(
            f'<linearGradient id="{gid}-g{i}" gradientUnits="userSpaceOnUse" x1="{fmt(x)}" y1="0" '
            f'x2="{fmt(x + w)}" y2="0" gradientTransform="skewX({skew})">{stop_xml}</linearGradient>'
        )
        polys.append(
            f'<path d="M{fmt(x)} 0H{fmt(x + w)}L{fmt(x + w + shift)} {fmt(h)}H{fmt(x + shift)}Z" fill="url(#{gid}-g{i})"/>'
        )
    doc.defs.append(
        f'<radialGradient id="{gid}-key" cx=".18" cy="0" r="1.1">'
        f'<stop offset="0" stop-color="#fff"/><stop offset=".7" stop-color="#fff" stop-opacity=".55"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity=".25"/></radialGradient>'
        f'<mask id="{gid}-mask"><rect width="100%" height="100%" fill="url(#{gid}-key)"/></mask>'
        f'<g id="{gid}">{"".join(polys)}</g>'
        f'<clipPath id="{gid}-clip">{"".join(polys)}</clipPath>'
    )


def sweep_light(doc: Doc, gid: str, period: float = 8.0, delay: float = 1.2) -> None:
    """A soft highlight that travels across the beams, like the light following the mouse."""
    h = doc.height
    doc.defs.append(
        f'<linearGradient id="{gid}-sweep" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="#fff" stop-opacity="{".22" if doc.theme == "dark" else ".7"}"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
    )
    doc.css.append(
        f".{gid}-sweep{{animation:{gid}-sweep {period}s {EASE_LIGHT} {delay}s infinite both}}"
        f"@keyframes {gid}-sweep{{from{{transform:translateX(-{fmt(h)}px)}}55%,to{{transform:translateX({fmt(doc.width + h)}px)}}}}"
    )
    doc.add(
        f'<g clip-path="url(#{gid}-clip)"><rect class="{gid}-sweep" x="-260" y="0" width="260" '
        f'height="{fmt(h)}" fill="url(#{gid}-sweep)"/></g>'
    )


def hero(theme: str) -> Doc:
    h = 400
    doc = Doc(W, h, theme, "Luiz Filipe Miranda, Full Stack developer in Vitória, ES")
    p = doc.p
    background(doc)
    beams(
        doc,
        [(-260, 210, 1.0), (-40, 70, 0.55), (60, 190, 0.85), (300, 80, 0.4), (430, 220, 0.6), (700, 110, 0.35)],
        slope=0.62,
    )
    doc.add('<use href="#beams" mask="url(#beams-mask)"/>')
    sweep_light(doc, "beams")

    # Portrait, faded into the beams on the left and bottom.
    portrait = base64.b64encode((Path(__file__).parent / "portrait.webp").read_bytes()).decode()
    px, size = W - 420, 440
    doc.defs.append(
        f'<linearGradient id="pfade-x" x1="{px}" y1="0" x2="{px + 140}" y2="0" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#fff"/></linearGradient>'
        f'<linearGradient id="pfade-y" x1="0" y1="{h - 90}" x2="0" y2="{h}" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
        f'<mask id="pmask"><rect width="100%" height="100%" fill="url(#pfade-x)"/></mask>'
        f'<mask id="pmask-y"><rect width="100%" height="100%" fill="url(#pfade-y)"/></mask>'
    )
    doc.css.append(f".portrait{{animation:fade 1.6s {EASE_OUT} .2s both}}@keyframes fade{{from{{opacity:0}}}}")
    doc.add(
        f'<g mask="url(#pmask-y)"><g mask="url(#pmask)"><image class="portrait" href="data:image/webp;base64,{portrait}" '
        f'x="{px}" y="-14" width="{size}" height="{size}"/></g></g>'
    )

    # Glass card: a blurred copy of the beams behind a tint, like backdrop-filter.
    cx, cy, cw, ch = 36, 62, 392, 268
    doc.defs.append(
        f'<clipPath id="card"><rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="4"/></clipPath>'
        '<filter id="frost" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="16"/></filter>'
    )
    doc.css.append(
        f".card{{animation:rise 1.1s {EASE_OUT} .1s both}}"
        f".l1{{animation:rise 1s {EASE_OUT} .25s both}}.l2{{animation:rise 1s {EASE_OUT} .35s both}}"
        f".l3{{animation:rise 1s {EASE_OUT} .45s both}}.meta{{animation:fade 1.2s {EASE_OUT} .7s both}}"
        "@keyframes rise{from{opacity:0;transform:translateY(12px)}}"
    )
    doc.add(
        f'<g class="card"><g clip-path="url(#card)"><rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" fill="{p["sweep_bottom"]}" opacity=".35"/>'
        f'<use href="#beams" filter="url(#frost)" opacity=".9"/>'
        f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" fill="{p["glass_tint"]}"/></g>'
        f'<rect x="{cx + 0.5}" y="{cy + 0.5}" width="{cw - 1}" height="{ch - 1}" rx="4" fill="none" stroke="{p["glass_edge"]}"/></g>'
    )
    tx, size_name = cx + 28, 56
    for i, word in enumerate(["Luiz", "Filipe", "Miranda"]):
        doc.text(tx, cy + 74 + i * 49, word, "name", size_name, p["ink"], tracking=-0.038, attrs=f'class="l{i + 1}"')
    doc.add('<g class="meta">')
    doc.text(tx + 2, cy + 210, "Full Stack · Vitória, ES", "body", 16, p["ink2"])
    doc.add(f'<rect x="{tx}" y="{cy + 228}" width="{cw - 56}" height="1" fill="{p["rule"]}"/>')
    doc.text(tx, cy + 250, "PVT SOFTWARE", "mono", 11, p["ink2"], tracking=0.08)
    doc.text(cx + cw - 28, cy + 250, f"{PORTFOLIO} ↗", "mono", 11, p["ink"], anchor="end")
    doc.add("</g>")
    doc.add('<g class="meta">')
    doc.text(cx, h - 26, "open to full stack · mobile · applied ai", "mono", 10.5, p["ink3"], tracking=0.02)
    doc.add("</g>")

    grain(doc, 0.06 if theme == "dark" else 0.05)
    doc.css.append(REDUCED_MOTION)
    return doc


def statement(theme: str) -> Doc:
    p = PALETTES[theme]
    size, lh, x0, width = 31, 35.5, 270, W - 270
    lines = wrap(STATEMENT, "display", size, width, -0.032)
    aside = wrap(STATEMENT_ASIDE, "body", 14, 210)
    h = 36 + len(lines) * lh + 20
    doc = Doc(W, h, theme, STATEMENT)
    doc.css.append(
        f".w{{animation:lit 1.1s {EASE_LIGHT} both}}@keyframes lit{{from{{opacity:.16}}}}" + REDUCED_MOTION
    )
    for i, line in enumerate(aside):
        doc.text(0, 46 + i * 20, line, "body", 14, p["ink2"])
    n = 0
    for i, line in enumerate(lines):
        x = x0
        for word in line.split():
            delay = 0.2 + n * 0.07
            w = doc.text(x, 36 + size * 0.72 + i * lh, word, "display", size, p["ink"], tracking=-0.032,
                         attrs=f'class="w" style="animation-delay:{delay:.2f}s"')
            x += w + measure(" ", "display", size, -0.032)
            n += 1
    return doc


def impact(theme: str) -> Doc:
    p = PALETTES[theme]
    gap, cols = 24, len(IMPACT)
    cw = (W - gap * (cols - 1)) / cols
    notes = [wrap(note, "body", 13, cw - 8) for _, _, note in IMPACT]
    h = 100 + max(len(n) for n in notes) * 18 + 8
    doc = Doc(W, h, theme, "Impact: " + "; ".join(f"{label} {value}" for label, value, _ in IMPACT))
    doc.css.append(f".c{{animation:rise .9s {EASE_OUT} both}}@keyframes rise{{from{{opacity:0;transform:translateY(8px)}}}}" + REDUCED_MOTION)
    for i, (label, value, _) in enumerate(IMPACT):
        x = i * (cw + gap)
        doc.add(f'<g class="c" style="animation-delay:{0.1 + i * 0.12:.2f}s">')
        doc.add(f'<rect x="{fmt(x)}" y="0" width="{fmt(cw)}" height="1" fill="{p["rule_strong"]}"/>')
        doc.text(x, 26, label.upper(), "mono", 10.5, p["ink3"], tracking=0.08)
        doc.text(x, 68, value, "title", 29, p["ink"], tracking=-0.03)
        for j, line in enumerate(notes[i]):
            doc.text(x, 96 + j * 18, line, "body", 13, p["ink2"])
        doc.add("</g>")
    return doc


def experience(theme: str) -> Doc:
    p = PALETTES[theme]
    left_w, rx = 250, 290
    rw = W - rx
    # Lay out first so the height is known.
    rows = []
    for role in EXPERIENCE:
        summary = wrap(role["summary"], "body_md", 16, rw)
        bullets = [wrap(b, "body", 14, rw - 20) for b in role["bullets"]]
        stack = wrap_items(role["stack"], "mono", 11, rw)
        right_h = len(summary) * 23 + 10 + sum(len(b) * 20 + 6 for b in bullets) + 10 + len(stack) * 17
        rows.append((role, summary, bullets, stack, max(right_h, 84) + 44))
    h = 84 + sum(r[-1] for r in rows)
    doc = Doc(W, h, theme, "Experience: " + ", ".join(f'{r["title"]} at {r["company"]}' for r in EXPERIENCE))
    y = section_head(doc, 0, "Experience", "Operations, ERP and AI that has to justify itself.")
    for k, (role, summary, bullets, stack, row_h) in enumerate(rows):
        if k:
            doc.add(f'<rect x="0" y="{fmt(y)}" width="{W}" height="1" fill="{p["rule"]}"/>')
        top = y + 30
        doc.text(0, top + 8, role["company"], "title", 22, p["ink"], tracking=-0.03)
        doc.text(0, top + 32, role["title"], "body", 14, p["ink2"])
        period = role["period"].upper()
        doc.text(0, top + 54, period, "mono", 10.5, p["ink3"], tracking=0.08)
        if role["period"] == "now":
            pw = measure(period, "mono", 10.5, 0.08)
            doc.css.append("@keyframes pulse{50%{opacity:.25}}.live{animation:pulse 2.4s ease-in-out infinite}")
            doc.add(f'<circle class="live" cx="{fmt(pw + 9)}" cy="{fmt(top + 50.5)}" r="3" fill="{p["ink"]}"/>')
        yy = top + 8
        for line in summary:
            doc.text(rx, yy, line, "body_md", 16, p["ink"])
            yy += 23
        yy += 10
        for bullet in bullets:
            doc.add(f'<rect x="{rx}" y="{fmt(yy - 5)}" width="9" height="1" fill="{p["ink3"]}"/>')
            for line in bullet:
                doc.text(rx + 20, yy, line, "body", 14, p["ink2"])
                yy += 20
            yy += 6
        yy += 10
        for line in stack:
            doc.text(rx, yy, line, "mono", 11, p["ink3"])
            yy += 17
        y += row_h
    doc.css.append(REDUCED_MOTION)
    return doc


def heading(theme: str, title: str, aside: str) -> Doc:
    doc = Doc(W, 84, theme, title)
    section_head(doc, 0, title, aside)
    return doc


def case_card(theme: str, i: int, case: dict, height: float | None = None) -> Doc:
    cw, pad = 432, 26
    inner = cw - pad * 2
    headline = wrap(case["headline"], "display", 18, inner, -0.02)
    cell_w = (inner - 20) / 2
    readings = [(label, wrap(value, "body", 13.5, cell_w)) for label, value in case["readings"]]
    reading_rows = [readings[0:2], readings[2:4]]
    row_heights = [30 + max(len(v) for _, v in row) * 18 for row in reading_rows]

    # Stack chips, wrapped.
    chips, cx, cy = [], 0.0, 0.0
    for item in case["stack"]:
        w = measure(item, "mono", 10.5) + 18
        if cx and cx + w > inner:
            cx, cy = 0.0, cy + 30
        chips.append((cx, cy, w, item))
        cx += w + 6
    chips_h = cy + 22

    natural = 104 + len(headline) * 23 + 18 + sum(row_heights) + 14 + chips_h + 64
    h = height or natural
    doc = Doc(cw, h + CARD_GAP, theme, f'{case["name"]}: {case["headline"]}')
    doc.natural = natural  # type: ignore[attr-defined]
    p = doc.p

    doc.defs.append(f'<clipPath id="frame"><rect width="{cw}" height="{fmt(h)}" rx="6"/></clipPath>')
    doc.add('<g clip-path="url(#frame)">')
    doc.add(f'<rect width="{cw}" height="{fmt(h)}" fill="{p["plane"]}"/>')
    # Faint beams in the top-right corner, so the cards share the hero's light.
    beams(doc, [(cw - 150 + i * 14, 70, 0.45), (cw - 40 + i * 9, 120, 0.3)], slope=0.55, gid="cb")
    doc.defs.append(
        '<linearGradient id="cb-fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/>'
        '<stop offset=".55" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        '<mask id="cb-m"><rect width="100%" height="100%" fill="url(#cb-fade)"/></mask>'
    )
    doc.add('<use href="#cb" mask="url(#cb-m)"/>')
    sweep_light(doc, "cb", period=9.0, delay=1.6 + i * 0.5)
    grain(doc, 0.05)
    doc.add("</g>")
    doc.add(f'<rect x=".5" y=".5" width="{cw - 1}" height="{fmt(h - 1)}" rx="6" fill="none" stroke="{p["rule"]}"/>')

    x = pad
    doc.text(x, 38, f'{i + 1:02d} / {case["context"].upper()}', "mono", 10.5, p["ink3"], tracking=0.08)
    doc.text(x, 84, case["name"], "title", 34, p["ink"], tracking=-0.034)
    y = 114
    for line in headline:
        doc.text(x, y, line, "display", 18, p["ink2"], tracking=-0.02)
        y += 23
    y += 8
    for row, row_h in zip(reading_rows, row_heights):
        for j, (label, value) in enumerate(row):
            rx = x + j * (cell_w + 20)
            doc.add(f'<rect x="{fmt(rx)}" y="{fmt(y)}" width="{fmt(cell_w)}" height="1" fill="{p["rule"]}"/>')
            doc.text(rx, y + 19, label.upper(), "mono", 9.5, p["ink3"], tracking=0.08)
            for k, line in enumerate(value):
                doc.text(rx, y + 38 + k * 18, line, "body", 13.5, p["ink"])
        y += row_h
    y += 14
    for chx, chy, w, item in chips:
        doc.add(
            f'<rect x="{fmt(x + chx + 0.5)}" y="{fmt(y + chy + 0.5)}" width="{fmt(w - 1)}" height="21" rx="10.5" '
            f'fill="none" stroke="{p["rule_strong"]}"/>'
        )
        doc.text(x + chx + 9, y + chy + 14.5, item, "mono", 10.5, p["ink2"])

    fy = h - 46
    doc.add(f'<rect x="{x}" y="{fmt(fy)}" width="{inner}" height="1" fill="{p["rule"]}"/>')
    doc.text(x, fy + 26, "Read the case ↗", "mono", 11, p["ink"])
    doc.text(cw - pad, fy + 26, case["repo"], "mono", 10.5, p["ink3"], anchor="end")
    doc.css.append(REDUCED_MOTION)
    return doc


def stack(theme: str) -> Doc:
    p = PALETTES[theme]
    cols, gap = 3, 28
    cw = (W - gap * (cols - 1)) / cols
    groups = [(label, wrap_items(items, "body", 15, cw)) for label, items in STACK]
    rows = [groups[0:3], groups[3:6]]
    row_heights = [40 + max(len(lines) for _, lines in row) * 22 + 22 for row in rows]
    marquee_h = 64
    h = 84 + marquee_h + sum(row_heights)
    doc = Doc(W, h, theme, "Stack: " + "; ".join(f"{label}: {', '.join(items)}" for label, items in STACK))
    y = section_head(doc, 0, "Stack", "What I use day to day.")

    # Marquee, like the portfolio's logo loop.
    loop_items = ["TypeScript", "Next.js", "NestJS", "PostgreSQL", "React Native", "Docker", "C#", "Prisma", "AWS", "RAG", "MCP"]
    sep = 34
    widths = [measure(t, "display", 24, -0.03) for t in loop_items]
    loop_w = sum(widths) + sep * len(loop_items)
    doc.defs.append(
        f'<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000"/>'
        f'<stop offset=".1" stop-color="#fff"/><stop offset=".9" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
        f'<mask id="edges"><rect width="{W}" height="{h}" fill="url(#edge)"/></mask>'
    )
    doc.css.append(f".loop{{animation:loop 38s linear infinite}}@keyframes loop{{to{{transform:translateX(-{fmt(loop_w)}px)}}}}")
    doc.add('<g mask="url(#edges)"><g class="loop">')
    x = 0.0
    for _ in range(3):
        for t, w in zip(loop_items, widths):
            doc.text(x, y + 30, t, "display", 24, p["ink3"], tracking=-0.03)
            x += w + sep / 2
            doc.add(f'<circle cx="{fmt(x - 1.5)}" cy="{fmt(y + 22)}" r="2" fill="{p["rule_strong"]}"/>')
            x += sep / 2
    doc.add("</g></g>")
    y += marquee_h

    for row, row_h in zip(rows, row_heights):
        for j, (label, lines) in enumerate(row):
            x = j * (cw + gap)
            doc.add(f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(cw)}" height="1" fill="{p["rule"]}"/>')
            doc.text(x, y + 24, label.upper(), "mono", 10.5, p["ink3"], tracking=0.08)
            for k, line in enumerate(lines):
                doc.text(x, y + 50 + k * 22, line, "body", 15, p["ink"])
        y += row_h
    doc.css.append(REDUCED_MOTION)
    return doc


def contact_link(theme: str, label: str, value: str) -> Doc:
    p = PALETTES[theme]
    doc = Doc(W, 62, theme, f"{label}: {value}")
    doc.text(0, 20, label.upper(), "mono", 10.5, p["ink3"], tracking=0.08)
    w = doc.text(150, 44, value, "display", 30, p["ink"], tracking=-0.03)
    doc.text(150 + w + 10, 44, "↗", "display", 26, p["ink2"])
    doc.add(f'<rect x="0" y="61" width="{W}" height="1" fill="{p["rule"]}"/>')
    return doc


def write(name: str, doc: Doc) -> None:
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(doc.render(), encoding="utf-8")
    print(f"{path.relative_to(ROOT)}  {path.stat().st_size / 1024:.1f} KB")


def main() -> None:
    for theme in PALETTES:
        write(f"hero-{theme}.svg", hero(theme))
        write(f"statement-{theme}.svg", statement(theme))
        write(f"impact-{theme}.svg", impact(theme))
        write(f"experience-{theme}.svg", experience(theme))
        write(f"head-cases-{theme}.svg", heading(theme, "Cases", "Four projects with architecture, decisions and code in the open."))
        card_h = max(case_card(theme, i, c).natural for i, c in enumerate(CASES))  # type: ignore[attr-defined]
        for i, case in enumerate(CASES):
            write(f"cases/{case['slug']}-{theme}.svg", case_card(theme, i, case, card_h))
        write(f"stack-{theme}.svg", stack(theme))
        write(f"head-contact-{theme}.svg", heading(theme, "Contact", "Email is usually the fastest way to reach me."))
        for label, value in CONTACT:
            write(f"contact/{label}-{theme}.svg", contact_link(theme, label, value))


if __name__ == "__main__":
    main()
