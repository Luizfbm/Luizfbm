"""Builds the static README SVGs into assets/, one dark and one light file each.

    python3 scripts/build_assets.py

Copy lives in this file. Change it here and run again.
"""

from __future__ import annotations

import math
import re
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
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
ICONS = Path(__file__).parent / "icons"
W = 880

PORTFOLIO = "portfolio.luizfbm.win"

INTRO_LEAD = (
    "I take messy operations in healthcare, education, ERP and customer support "
    "and get them live. AI only comes in when it cuts time or risk."
)
INTRO_REST = (
    "Right now I'm a full stack developer at PVT Software in Vitória, Brazil. "
    "My projects, with the code and the decisions behind each one, are on my portfolio."
)

# Only what I use day to day; the full list lives on the portfolio.
# (name, Simple Icons slug or None for a text tile)
STACK = [
    ("TypeScript", "typescript"), ("JavaScript", "javascript"), ("C#", None), ("React", "react"),
    ("Next.js", "nextdotjs"), ("React Native", "react"), ("Node.js", "nodedotjs"),
    ("NestJS", "nestjs"), ("PostgreSQL", "postgresql"), ("SQL Server", None), ("Prisma", "prisma"),
    ("Docker", "docker"), ("AWS", None), ("GitHub Actions", "githubactions"),
]
STACK_PER_ROW = 7
APPLIED_AI = ["RAG", "MCP", "Agentic workflows", "Streaming APIs", "Prompt engineering"]
TILE_TEXT = {"C#": "C#", "SQL Server": "MSSQL", "AWS": "AWS"}

CONTACT = [
    ("portfolio", PORTFOLIO),
    ("linkedin", "linkedin.com/in/luizfilipedev"),
    ("email", "contatoluizfbm@gmail.com"),
]

EASE_OUT = "cubic-bezier(.16,1,.3,1)"
EASE_LIGHT = "cubic-bezier(.33,0,.15,1)"


def background(doc: Doc) -> None:
    p = doc.p
    doc.defs.append(
        f'<linearGradient id="sweep" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{p["sweep_top"]}"/><stop offset="1" stop-color="{p["sweep_bottom"]}"/>'
        f"</linearGradient>"
    )
    doc.add(f'<rect width="100%" height="100%" rx="6" fill="url(#sweep)"/>')


def beams(doc: Doc, specs: list[tuple[float, float, float]], slope: float) -> None:
    """Defines diagonal light beams as #beams, plus a clip path with their shape.

    Each spec is (x at the top edge, width, strength). `slope` is how far a
    beam moves right per px down.
    """
    p = doc.p
    h = doc.height
    shift = slope * h
    skew = fmt(math.degrees(math.atan(slope)))
    polys = []
    for i, (x, w, s) in enumerate(specs):
        s *= p["beam_gain"]
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
            f'<linearGradient id="beam{i}" gradientUnits="userSpaceOnUse" x1="{fmt(x)}" y1="0" '
            f'x2="{fmt(x + w)}" y2="0" gradientTransform="skewX({skew})">{stop_xml}</linearGradient>'
        )
        polys.append(
            f'<path d="M{fmt(x)} 0H{fmt(x + w)}L{fmt(x + w + shift)} {fmt(h)}H{fmt(x + shift)}Z" fill="url(#beam{i})"/>'
        )
    doc.defs.append(
        '<radialGradient id="key" cx=".2" cy="0" r="1.1">'
        '<stop offset="0" stop-color="#fff"/><stop offset=".7" stop-color="#fff" stop-opacity=".5"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity=".2"/></radialGradient>'
        '<mask id="keymask"><rect width="100%" height="100%" fill="url(#key)"/></mask>'
        f'<g id="beams">{"".join(polys)}</g>'
        f'<clipPath id="beamclip">{"".join(polys)}</clipPath>'
    )


def sweep_light(doc: Doc, period: float = 8.0, delay: float = 1.2) -> None:
    """A soft highlight that travels across the beams now and then."""
    h = doc.height
    doc.defs.append(
        '<linearGradient id="glint" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="#fff" stop-opacity="{".22" if doc.theme == "dark" else ".7"}"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
    )
    doc.css.append(
        f".glint{{animation:glint {period}s {EASE_LIGHT} {delay}s infinite both}}"
        f"@keyframes glint{{from{{transform:translateX(-{fmt(h)}px)}}55%,to{{transform:translateX({fmt(doc.width + h)}px)}}}}"
    )
    doc.add(
        f'<g clip-path="url(#beamclip)"><rect class="glint" x="-240" y="0" width="240" '
        f'height="{fmt(h)}" fill="url(#glint)"/></g>'
    )


def banner(theme: str) -> Doc:
    h = 230
    doc = Doc(W, h, theme, "Luiz Filipe Miranda, full stack developer")
    p = doc.p
    doc.defs.append(f'<clipPath id="frame"><rect width="{W}" height="{h}" rx="6"/></clipPath>')
    doc.add('<g clip-path="url(#frame)">')
    background(doc)
    # Beams sit to the right so the name has a quiet area to the left.
    beams(doc, [(300, 120, 0.5), (430, 60, 0.6), (520, 190, 0.9), (720, 80, 0.45), (800, 170, 0.7)], slope=0.6)
    doc.add('<use href="#beams" mask="url(#keymask)"/>')
    sweep_light(doc)
    grain(doc, 0.06 if theme == "dark" else 0.05)
    doc.add("</g>")

    doc.css.append(
        f".rise{{animation:rise 1s {EASE_OUT} .15s both}}.fade{{animation:fade 1.2s {EASE_OUT} .5s both}}"
        "@keyframes rise{from{opacity:0;transform:translateY(10px)}}@keyframes fade{from{opacity:0}}"
        + REDUCED_MOTION
    )
    x = 40
    doc.text(x, 112, "Luiz Filipe Miranda", "name", 52, p["ink"], tracking=-0.038, attrs='class="rise"')
    doc.add('<g class="fade">')
    doc.text(x + 2, 146, "Full stack developer", "body", 17, p["ink2"])
    doc.add(f'<rect x="{x}" y="176" width="{W - 2 * x}" height="1" fill="{p["rule"]}"/>')
    doc.text(x, 200, "VITÓRIA, BRAZIL", "mono", 10.5, p["ink3"], tracking=0.08)
    doc.text(W - x, 200, f"{PORTFOLIO} ↗", "mono", 11, p["ink"], anchor="end")
    doc.add("</g>")
    return doc


def intro(theme: str) -> Doc:
    p = PALETTES[theme]
    size, lh = 27, 32
    lead = wrap(INTRO_LEAD, "display", size, W, -0.03)
    rest = wrap(INTRO_REST, "body", 16, 640)
    h = 12 + len(lead) * lh + 18 + len(rest) * 24 + 8
    doc = Doc(W, h, theme, f"{INTRO_LEAD} {INTRO_REST}")
    doc.css.append(
        f".w{{animation:lit 1.1s {EASE_LIGHT} both}}@keyframes lit{{from{{opacity:.16}}}}"
        f".rest{{animation:fade 1s {EASE_OUT} both}}@keyframes fade{{from{{opacity:0}}}}" + REDUCED_MOTION
    )
    n = 0
    y = 12 + size * 0.75
    for line in lead:
        x = 0.0
        for word in line.split():
            w = doc.text(x, y, word, "display", size, p["ink"], tracking=-0.03,
                         attrs=f'class="w" style="animation-delay:{0.2 + n * 0.06:.2f}s"')
            x += w + measure(" ", "display", size, -0.03)
            n += 1
        y += lh
    y += 18
    doc.add(f'<g class="rest" style="animation-delay:{0.4 + n * 0.06:.2f}s">')
    for line in rest:
        doc.text(0, y, line, "body", 16, p["ink2"])
        y += 24
    doc.add("</g>")
    return doc


def icon_path(slug: str) -> str:
    svg = (ICONS / f"{slug}.svg").read_text()
    match = re.search(r'<path d="([^"]+)"', svg)
    if not match:
        raise ValueError(f"no path in {slug}.svg")
    return match.group(1)


def stack(theme: str) -> Doc:
    p = PALETTES[theme]
    tile_w, icon = W / STACK_PER_ROW, 28
    row_h = 18 + icon + 34
    rows = [STACK[i:i + STACK_PER_ROW] for i in range(0, len(STACK), STACK_PER_ROW)]
    h = 84 + len(rows) * row_h + 52
    doc = Doc(W, h, theme, "Stack: " + ", ".join(name for name, _ in STACK)
              + ". Applied AI: " + ", ".join(APPLIED_AI) + ".")
    y = section_head(doc, 0, "Stack", "What I use day to day.")
    doc.css.append(
        f".t{{animation:rise .8s {EASE_OUT} both}}@keyframes rise{{from{{opacity:0;transform:translateY(6px)}}}}"
        + REDUCED_MOTION
    )

    n = 0
    for items in rows:
        for i, (name, slug) in enumerate(items):
            cx = i * tile_w + tile_w / 2
            ix, iy = cx - icon / 2, y + 18
            doc.add(f'<g class="t" style="animation-delay:{0.05 + n * 0.03:.3f}s">')
            if slug:
                doc.add(
                    f'<svg x="{fmt(ix)}" y="{fmt(iy)}" width="{icon}" height="{icon}" viewBox="0 0 24 24">'
                    f'<path d="{icon_path(slug)}" fill="{p["ink"]}"/></svg>'
                )
            else:
                doc.add(
                    f'<rect x="{fmt(ix + 0.5)}" y="{fmt(iy + 0.5)}" width="{icon - 1}" height="{icon - 1}" rx="6" '
                    f'fill="none" stroke="{p["ink2"]}"/>'
                )
                tag = TILE_TEXT[name]
                doc.text(cx, iy + icon / 2 + 3.5, tag, "mono", 9.5 if len(tag) < 4 else 7.5, p["ink"], anchor="middle")
            doc.text(cx, iy + icon + 20, name, "body", 12.5, p["ink2"], anchor="middle")
            doc.add("</g>")
            n += 1
        y += row_h

    # Applied AI has no logos worth showing, so it gets one line of text.
    doc.add(f'<rect x="0" y="{fmt(y + 8)}" width="{W}" height="1" fill="{p["rule"]}"/>')
    doc.text(0, y + 38, "APPLIED AI", "mono", 10.5, p["ink3"], tracking=0.08)
    doc.text(112, y + 38, "  ·  ".join(APPLIED_AI), "body", 15, p["ink"])
    return doc


def heading(theme: str, title: str, aside: str) -> Doc:
    doc = Doc(W, 84, theme, title)
    section_head(doc, 0, title, aside)
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
        write(f"banner-{theme}.svg", banner(theme))
        write(f"intro-{theme}.svg", intro(theme))
        write(f"stack-{theme}.svg", stack(theme))
        write(f"head-contact-{theme}.svg", heading(
            theme, "Contact", "The projects live on the portfolio. Email is the fastest way to reach me."
        ))
        for label, value in CONTACT:
            write(f"contact/{label}-{theme}.svg", contact_link(theme, label, value))


if __name__ == "__main__":
    main()
