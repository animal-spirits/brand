"""Land mask from world-atlas land-110m (Natural Earth, public domain; packaging ISC), equirectangular."""
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw


def land_mask(w=1440, h=720, src=None):
    t = json.load(open(src or Path(__file__).parent / "data" / "land-110m.json"))
    sx, sy = t["transform"]["scale"]
    tx, ty = t["transform"]["translate"]
    arcs = []
    for a in t["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in a:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)

    def ring(idx):
        out = []
        for i in idx:
            pts = arcs[i] if i >= 0 else arcs[~i][::-1]
            out += pts[1:] if out else pts
        return out

    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    for g in t["objects"]["land"]["geometries"]:
        polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
        for poly in polys:
            for k, r in enumerate(poly):
                pts = [((lon + 180) / 360 * w, (90 - lat) / 180 * h) for lon, lat in ring(r)]
                d.polygon(pts, fill=0 if k else 255)
    return np.array(im) > 127
