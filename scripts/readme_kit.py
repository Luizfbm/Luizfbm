"""Shared pieces for the README SVGs: palette, fonts and text layout.

The SVGs are rendered by GitHub as <img>, so they can't load anything
external. Fonts are instanced from the portfolio's variable fonts, subset
to the glyphs each file uses and embedded as base64 woff2.
"""

from __future__ import annotations

import base64
import io
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

FONT_DIR = Path(__file__).parent / "fonts"

# Same tokens as the portfolio (portfolio.luizfbm.win), dark and light.
PALETTES = {
    "dark": {
        "sweep_top": "#171717",
        "sweep_bottom": "#050505",
        "plane": "#101010",
        "plane_lit": "#181818",
        "ink": "#f2f2f2",
        "ink2": "#bdbdbd",
        "ink3": "#8f8f8f",
        "rule": "rgba(242,242,242,.16)",
        "rule_strong": "rgba(242,242,242,.34)",
        "glass_tint": "rgba(255,255,255,.05)",
        "glass_edge": "rgba(255,255,255,.18)",
        "beam": "#ffffff",
        "beam_gain": 1.0,
        "shade": "#000000",
    },
    "light": {
        "sweep_top": "#f8f8f8",
        "sweep_bottom": "#d9d9d9",
        "plane": "#efefef",
        "plane_lit": "#f7f7f7",
        "ink": "#111111",
        "ink2": "#3d3d3d",
        "ink3": "#5e5e5e",
        "rule": "rgba(17,17,17,.18)",
        "rule_strong": "rgba(17,17,17,.38)",
        "glass_tint": "rgba(255,255,255,.42)",
        "glass_edge": "rgba(17,17,17,.14)",
        "beam": "#ffffff",
        "beam_gain": 1.6,
        "shade": "#000000",
    },
}

# name -> (file, axes, css family). Axes follow the portfolio's CSS.
FONTS = {
    "name": ("archivo", {"wght": 680, "wdth": 116}, "Archivo Name"),
    "title": ("archivo", {"wght": 640, "wdth": 110}, "Archivo Title"),
    "display": ("archivo", {"wght": 560, "wdth": 104}, "Archivo Display"),
    "body": ("instrument-sans", {"wght": 400}, "Instrument Sans"),
    "body_md": ("instrument-sans", {"wght": 560}, "Instrument Sans Md"),
    "mono": ("jetbrains-mono", {"wght": 400}, "JetBrains Mono"),
}

FALLBACK = {
    "mono": "ui-monospace, SFMono-Regular, Menlo, monospace",
}
DEFAULT_FALLBACK = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

# Glyphs the latin subsets don't have; drawn as paths instead.
ARROWS = {"→", "↗"}


@lru_cache(maxsize=None)
def _instance(key: str) -> TTFont:
    file, axes, _ = FONTS[key]
    font = TTFont(FONT_DIR / f"{file}.woff2")
    font = instancer.instantiateVariableFont(font, axes)
    font.flavor = None
    # Keep head.modified as is, so rebuilding doesn't change every SVG.
    font.recalcTimestamp = False
    return font


@lru_cache(maxsize=None)
def _metrics(key: str) -> tuple[dict[int, int], int]:
    font = _instance(key)
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    return {cp: hmtx[name][0] for cp, name in cmap.items()}, font["head"].unitsPerEm


def measure(text: str, key: str, size: float, tracking: float = 0.0) -> float:
    """Width in px, ignoring kerning. `tracking` is in em, like CSS letter-spacing."""
    widths, upm = _metrics(key)
    total = 0.0
    for ch in text:
        if ch in ARROWS:
            total += 0.9 * size
            continue
        if ord(ch) not in widths:
            raise ValueError(f"{FONTS[key][0]} has no glyph for {ch!r}")
        total += widths[ord(ch)] * size / upm + tracking * size
    return total


def wrap(text: str, key: str, size: float, width: float, tracking: float = 0.0) -> list[str]:
    lines: list[str] = []
    line = ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if line and measure(candidate, key, size, tracking) > width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def wrap_items(items: list[str], key: str, size: float, width: float, sep: str = "  ·  ") -> list[str]:
    """Like wrap(), but never breaks inside an item or leaves a separator dangling."""
    lines: list[str] = []
    line = ""
    for item in items:
        candidate = f"{line}{sep}{item}" if line else item
        if line and measure(candidate, key, size) > width:
            lines.append(line)
            line = item
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def _font_face(key: str, chars: set[str]) -> str:
    buf = io.BytesIO()
    _instance(key).save(buf)
    buf.seek(0)
    font = TTFont(buf, recalcTimestamp=False)
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = ["kern", "liga", "calt"]
    options.name_IDs = []
    options.notdef_outline = True
    subsetter = subset.Subsetter(options)
    subsetter.populate(text="".join(sorted(chars)) + " ")
    subsetter.subset(font)
    out = io.BytesIO()
    font.save(out)
    data = base64.b64encode(out.getvalue()).decode()
    family = FONTS[key][2]
    return f"@font-face{{font-family:'{family}';src:url(data:font/woff2;base64,{data}) format('woff2');}}"


def family(key: str) -> str:
    return f"'{FONTS[key][2]}', {FALLBACK.get(key, DEFAULT_FALLBACK)}"


def fmt(n: float) -> str:
    return f"{n:.2f}".rstrip("0").rstrip(".")


@dataclass
class Doc:
    """An SVG under construction. Records which glyphs each font needs."""

    width: float
    height: float
    theme: str
    title: str
    body: list[str] = field(default_factory=list)
    defs: list[str] = field(default_factory=list)
    css: list[str] = field(default_factory=list)
    used: dict[str, set[str]] = field(default_factory=dict)

    @property
    def p(self) -> dict:
        return PALETTES[self.theme]

    def add(self, *parts: str) -> None:
        self.body.extend(parts)

    def text(
        self,
        x: float,
        y: float,
        content: str,
        key: str,
        size: float,
        fill: str,
        tracking: float = 0.0,
        anchor: str = "start",
        attrs: str = "",
    ) -> float:
        """Draws one line of text and returns its width.

        Arrows split the line into runs; each run is placed at a measured x,
        so kerning is turned off there to keep the measurement honest.
        """
        width = measure(content, key, size, tracking)
        if anchor == "end":
            x -= width
        elif anchor == "middle":
            x -= width / 2

        runs: list[tuple[str, str]] = []
        for ch in content:
            kind = "arrow" if ch in ARROWS else "text"
            if runs and runs[-1][0] == "text" and kind == "text":
                runs[-1] = ("text", runs[-1][1] + ch)
            else:
                runs.append((kind, ch))

        split = len(runs) > 1
        style = f"font-family:{family(key)};font-size:{fmt(size)}px"
        if tracking:
            style += f";letter-spacing:{fmt(tracking * size)}px"
        if split:
            style += ";font-kerning:none"

        parts = []
        cursor = x
        for kind, chunk in runs:
            if kind == "arrow":
                parts.append(arrow(cursor, y, size, fill, diagonal=chunk == "↗"))
                cursor += 0.9 * size
                continue
            self.used.setdefault(key, set()).update(chunk)
            parts.append(
                f'<text x="{fmt(cursor)}" y="{fmt(y)}" fill="{fill}" style="{style}" xml:space="preserve">'
                f"{escape(chunk)}</text>"
            )
            cursor += measure(chunk, key, size, tracking)

        if split or attrs:
            self.add(f"<g {attrs}>" + "".join(parts) + "</g>")
        else:
            self.add(parts[0])
        return width

    def render(self) -> str:
        faces = "".join(_font_face(key, chars) for key, chars in sorted(self.used.items()))
        css = faces + "".join(self.css)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(self.width)}" height="{fmt(self.height)}" '
            f'viewBox="0 0 {fmt(self.width)} {fmt(self.height)}" role="img" aria-label="{escape(self.title)}">'
            f"<title>{escape(self.title)}</title>"
            f"<style>{css}</style>"
            f"<defs>{''.join(self.defs)}</defs>"
            f"{''.join(self.body)}</svg>"
        )


def arrow(x: float, y: float, size: float, color: str, diagonal: bool = False) -> str:
    """A stroked arrow sitting on the text baseline, 0.9em wide."""
    s = size
    stroke = max(1.2, s * 0.075)
    if diagonal:
        x0, y0, x1, y1 = x + s * 0.18, y - s * 0.08, x + s * 0.68, y - s * 0.58
        head = f"M{fmt(x1 - s * 0.36)} {fmt(y1)}H{fmt(x1)}V{fmt(y1 + s * 0.36)}"
    else:
        mid = y - s * 0.33
        x0, y0, x1, y1 = x + s * 0.12, mid, x + s * 0.76, mid
        head = f"M{fmt(x1 - s * 0.24)} {fmt(mid - s * 0.24)}L{fmt(x1)} {fmt(mid)}L{fmt(x1 - s * 0.24)} {fmt(mid + s * 0.24)}"
    return (
        f'<path d="M{fmt(x0)} {fmt(y0)}L{fmt(x1)} {fmt(y1)}{head}" fill="none" stroke="{color}" '
        f'stroke-width="{fmt(stroke)}" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def grain(doc: Doc, opacity: float = 0.07) -> None:
    """Film grain, like the portfolio's --grain overlay."""
    doc.defs.append(
        '<filter id="grain" x="0" y="0" width="100%" height="100%">'
        '<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" stitchTiles="stitch"/>'
        '<feColorMatrix values="0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 1.2 -.35"/>'
        "</filter>"
    )
    doc.add(f'<rect width="100%" height="100%" filter="url(#grain)" opacity="{opacity}"/>')


def section_head(doc: Doc, y: float, title: str, aside: str) -> float:
    """Rule, big title on the left, quiet aside on the right. Returns the y below it."""
    p = doc.p
    doc.add(f'<rect x="0" y="{fmt(y)}" width="{fmt(doc.width)}" height="1" fill="{p["rule_strong"]}"/>')
    doc.text(0, y + 52, title, "title", 34, p["ink"], tracking=-0.032)
    aside_lines = wrap(aside, "body", 14, 300)
    for i, line in enumerate(aside_lines):
        doc.text(doc.width, y + 30 + i * 20, line, "body", 14, p["ink3"], anchor="end")
    return y + 84


REDUCED_MOTION = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
