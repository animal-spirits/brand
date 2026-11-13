"""ANIMAL SPIRITS, outlined from Big Shoulders Display Black and spaced by hand. The wordmark is a drawing: never typed."""
from functools import cache
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT = Path(__file__).parent / "data" / "BigShouldersDisplay-Black.woff2"
SIZE = 100.0       # em, in logo units
TRACK = 1.5        # units added after every letter
WORD_GAP = 14.0    # the space between ANIMAL and SPIRITS on one line, in units
KERN = {"LS": -1.0, "AN": .5}


@cache
def _font() -> TTFont:
    return TTFont(FONT)


def cap_height() -> float:
    f = _font()
    gs = f.getGlyphSet()
    pen = BoundsPen(gs)
    gs[f.getBestCmap()[ord("H")]].draw(pen)
    return pen.bounds[3] * SIZE / f["head"].unitsPerEm


def glyphs(text: str, x: float = 0, y: float = 0) -> tuple[list[str], float]:
    """One path per letter, baseline at y; returns (paths, right edge)."""
    f = _font()
    s = SIZE / f["head"].unitsPerEm
    cmap, hmtx, gs = f.getBestCmap(), f["hmtx"], f.getGlyphSet()
    out, prev = [], ""
    for ch in text:
        if ch == " ":
            x += WORD_GAP
            prev = ""
            continue
        x += KERN.get(prev + ch, 0)
        g = cmap[ord(ch)]
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
        out.append(pen.getCommands())
        x += hmtx[g][0] * s + TRACK
        prev = ch
    return out, x - TRACK


def line(text: str, x: float = 0, y: float = 0) -> tuple[str, float]:
    """Path data for one line with its baseline at y; returns (d, right edge)."""
    parts, r = glyphs(text, x, y)
    return "".join(parts), r


def width(text: str) -> float:
    return line(text)[1]
