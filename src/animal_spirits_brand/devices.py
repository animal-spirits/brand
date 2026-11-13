"""Office devices: rubber stamps and the ticker tape, with lettering outlined from IBM Plex Mono Medium."""
from functools import cache
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT = Path(__file__).parent / "data" / "IBMPlexMono-Medium.woff2"
STAMPS = [  # (file, text, small line); status marks, never decoration
    ("ceteris-paribus", "CETERIS PARIBUS", "ALL ELSE HELD EQUAL"),
    ("ex-ante", "EX ANTE", "BEFORE THE FACT"),
    ("ex-post", "EX POST", "AFTER THE FACT"),
    ("seed", "SEED 64", "SAME SEED · SAME WORLD"),
    ("re-run", "RE-RUN", "CHANGE ONE THING"),
    ("sourced", "SOURCED", "DATA CITED IN FULL"),
]


@cache
def _font() -> TTFont:
    return TTFont(FONT)


def text(s: str, size: float, x: float, y: float, track: float = 0, anchor: str = "start") -> str:
    """Outlined monospaced text, baseline at y."""
    f = _font()
    k = size / f["head"].unitsPerEm
    cmap, gs = f.getBestCmap(), f.getGlyphSet()
    adv = f["hmtx"][cmap[ord("M")]][0] * k + track
    if anchor == "middle":
        x -= (adv * len(s) - track) / 2
    out = []
    for ch in s:
        g = cmap.get(ord(ch))
        if g and ch != " ":
            pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
            gs[g].draw(TransformPen(pen, (k, 0, 0, -k, x, y)))
            out.append(pen.getCommands())
        x += adv
    return "".join(out)


ROUGH = ('<filter id="rough" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".9" '
         'numOctaves="2" seed="4" result="n"/><feColorMatrix in="n" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -1.5 1.4" '
         'result="m"/><feComposite in="SourceGraphic" in2="m" operator="in"/></filter>')


def stamp(big: str, small: str, colour: str = "currentColor", w: int = 260) -> str:
    fs = min(25, ((w - 44) / len(big) - 2) / 0.6)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 92" width="{w}" height="92"><defs>{ROUGH}</defs>'
            f'<g filter="url(#rough)" fill="{colour}"><path fill="none" stroke="{colour}" stroke-width="4" d="M4 4H{w - 4}V88H4Z"/>'
            f'<path fill="none" stroke="{colour}" stroke-width="1.5" d="M11 11H{w - 11}V81H11Z"/>'
            f'<path d="{text(big, fs, w / 2, 50, 2, "middle")}"/><path d="{text(small, 11, w / 2, 70, 1.5, "middle")}"/></g></svg>')


TAPE = ["GDP.DEU +0.9", "CPI.FRA 1.7", "UNEMP.ESP 14.2", "GDP.JPN +0.5", "SEED 64", "TICK 0000412", "MARKETS 41,388", "CLEARED 41,301",
        "RATIONED 87", "CPI.ITA 2.3", "GDP.USA +1.0", "M2.EZ +5.6"]


def tape(colour: str, w: int = 1600) -> str:
    """One line of tape, codes separated by dots. The figures are illustrative; real tape is fed from a run's journal."""
    s = " · ".join(TAPE * 3) + " ·"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 32" width="{w}" height="32">'
            f'<path fill="{colour}" d="{text(s, 13, 0, 21, .3)}"/></svg>')
