"""potrace a boolean mask (True = ink) into SVG path data."""
import numpy as np
import potrace


def trace_ink(ink: np.ndarray, scale: float, turd: int = 6) -> str:
    out = []
    for c in potrace.Bitmap(~ink).trace(turdsize=turd, alphamax=1.0, opticurve=True, opttolerance=.4):
        d = [f"M{c.start_point.x * scale:.1f} {c.start_point.y * scale:.1f}"]
        for g in c:
            if g.is_corner:
                d.append(f"L{g.c.x * scale:.1f} {g.c.y * scale:.1f}L{g.end_point.x * scale:.1f} {g.end_point.y * scale:.1f}")
            else:
                d.append("C" + " ".join(f"{p.x * scale:.1f} {p.y * scale:.1f}" for p in (g.c1, g.c2, g.end_point)))
        out.append("".join(d) + "Z")
    return "".join(out)
