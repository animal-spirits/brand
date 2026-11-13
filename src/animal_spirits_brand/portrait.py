"""The Keynes woodcut and its two reductions. All three are paths in a 1254-unit square, ink only.

Cut 1 is the original drawing. Cuts 2 and 3 are traced from it at lower resolution with more blur, so the lines
thicken and the small gouges close up: cut 2 for 48 to 256 px, cut 3 below 48 px."""
import re
from functools import cache
from pathlib import Path

import numpy as np
import potrace
from PIL import Image, ImageFilter

DATA = Path(__file__).parent / "data"
SIZE = 1254
# (trace resolution, blur, threshold on the red channel, speckle limit)
REDUCTIONS = {2: (160, .9, 118, 6), 3: (96, 1.1, 122, 5)}


def _trace(res: int, blur: float, thresh: int, turd: int, src: Path = DATA / "keynes.png", tol: float = .4, nd: int = 1) -> str:
    im = Image.open(src).convert("RGB").split()[0].resize((res, res), Image.LANCZOS)
    paper = np.array(im.filter(ImageFilter.GaussianBlur(blur))) >= thresh  # the red ground is light in R; ink is dark
    s = SIZE / res
    out = []
    for curve in potrace.Bitmap(paper).trace(turdsize=turd, alphamax=1.0, opticurve=True, opttolerance=tol):
        f = lambda p: f"{p.x * s:.{nd}f} {p.y * s:.{nd}f}"
        d = [f"M{f(curve.start_point)}"]
        for seg in curve:
            if seg.is_corner:
                d.append(f"L{f(seg.c)}L{f(seg.end_point)}")
            else:
                d.append("C" + " ".join(f(p) for p in (seg.c1, seg.c2, seg.end_point)))
        out.append("".join(d) + "Z")
    return "".join(out)


@cache
def cut(n: int) -> str:
    if n == 1:
        return re.search(r' d="([^"]+)"', (DATA / "keynes.svg").read_text()).group(1)
    return _trace(*REDUCTIONS[n])


# Per-woodcut reductions where the defaults fill in the gouges. Black subjects (the swan) need a lower threshold.
# Scenes too dense to reduce exist only as cut 1, at 256 px and above.
LARGE_ONLY = {"the-floor", "the-city", "machine-hall", "the-assembly"}
LIGHT = {2: (240, .6, 92, 8), 3: (144, .9, 92, 8)}
CUT_REDUCTIONS = {"black-swan": LIGHT, "ship": LIGHT, "hawk": LIGHT}


def woodcut(src: Path, n: int) -> str:
    """Any generated woodcut (black on the red ground) in the portrait's three cuts. Cut 1 is traced at full size."""
    if n == 1:
        return _trace(1254, 0, 110, 6, src=src, tol=1.0, nd=0)  # integer units on a 1254 grid: invisible, half the bytes
    return _trace(*CUT_REDUCTIONS.get(src.stem, {}).get(n, REDUCTIONS[n]), src=src)


def engraving(src: Path) -> str:
    """A generated cabinet object traced at full size: a woodcut on the red ground, or an engraving on white."""
    r, g, _ = (np.median(np.asarray(c)) for c in Image.open(src).convert("RGB").split())
    return _trace(1254, 0, 110 if r - g > 60 else 150, 4, src=src, tol=1.0, nd=0)
