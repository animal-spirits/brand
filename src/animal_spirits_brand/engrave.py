"""Engraving for the cabinet: a small scene of solids is ray-marched, lit from the upper left, and the light is carved out
of black ink as lines that follow each part's form. Same rule as the portrait: one ink, tone made by line width."""
import numpy as np
from scipy import ndimage

from .trace import trace_ink


def nz(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def length(v):
    return np.linalg.norm(v, axis=-1)


def rot(ax: float = 0, ay: float = 0, az: float = 0) -> np.ndarray:
    cx, sx, cy, sy, cz, sz = np.cos(ax), np.sin(ax), np.cos(ay), np.sin(ay), np.cos(az), np.sin(az)
    X = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Y = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Z = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Z @ Y @ X


# primitives in local space
def sphere(r):
    return lambda p: length(p) - r


def rcyl(r, h, rr=0.0):
    def f(p):
        d = np.stack([np.hypot(p[:, 0], p[:, 2]) - r + rr, np.abs(p[:, 1]) - h + rr], -1)
        return np.minimum(d.max(-1), 0) + length(np.maximum(d, 0)) - rr
    return f


def rbox(b, rr):
    b = np.array(b)
    def f(p):
        q = np.abs(p) - b + rr
        return length(np.maximum(q, 0)) + np.minimum(q.max(-1), 0) - rr
    return f


def capsule(a, b, r):
    a, b = np.array(a, float), np.array(b, float)
    ba = b - a
    def f(p):
        pa = p - a
        h = np.clip(pa @ ba / (ba @ ba), 0, 1)
        return length(pa - h[:, None] * ba) - r
    return f


def torus(R, r):
    return lambda p: np.hypot(np.hypot(p[:, 0], p[:, 2]) - R, p[:, 1]) - r


def revolve(prof):
    """prof(rho, y) -> 2D signed distance."""
    return lambda p: prof(np.hypot(p[:, 0], p[:, 2]), p[:, 1])


class Part:
    def __init__(self, sdf, at=(0, 0, 0), R=np.eye(3), hatch=None, ink=None, pitch=0.045):
        self.sdf, self.t, self.R, self.hatch, self.ink, self.pitch = sdf, np.array(at, float), R, hatch, ink, pitch

    def local(self, p):
        return (p - self.t) @ self.R


class Scene:
    def __init__(self, parts, ground=None, light=(-0.55, 0.75, 0.45)):
        self.parts, self.ground, self.light = parts, ground, nz(np.array(light, float))

    def dist(self, p):
        ds = [pt.sdf(pt.local(p)) for pt in self.parts]
        if self.ground is not None:
            ds.append(p[:, 1] - self.ground)
        D = np.stack(ds, -1)
        return D.min(-1), D.argmin(-1)


def march(scene, o, d, steps=260, far=12.0):
    t = np.zeros(len(o))
    alive = np.ones(len(o), bool)
    hit = np.zeros(len(o), bool)
    for _ in range(steps):
        idx = np.nonzero(alive)[0]
        if not len(idx):
            break
        dd, _ = scene.dist(o[idx] + d[idx] * t[idx, None])
        t[idx] += dd * 0.9
        h = dd < 1e-3
        hit[idx[h]] = True
        alive[idx[h | (t[idx] > far)]] = False
    return t, hit


def shadow(scene, p, l, steps=60):
    t = np.full(len(p), 0.02)
    res = np.ones(len(p))
    for _ in range(steps):
        dd, _ = scene.dist(p + l * t[:, None])
        res = np.minimum(res, np.clip(10 * dd / t, 0, 1))
        t += np.clip(dd, 0.01, 0.2)
    return np.clip(res, 0, 1)


def render(scene, res=900, span=2.4, pitch_deg=24, yaw_deg=0, centre=(0, 0, 0), lines=1.0, ground_r=1.6):
    """Return the ink mask (True = ink) as res x res."""
    a, b = np.radians(pitch_deg), np.radians(yaw_deg)
    fwd = nz(np.array([np.sin(b) * np.cos(a), -np.sin(a), -np.cos(b) * np.cos(a)]))
    right = nz(np.cross(fwd, [0, 1, 0]))
    up = np.cross(right, fwd)
    xs = (np.arange(res) + .5) / res * span - span / 2
    X, Y = np.meshgrid(xs, -xs)
    o = np.array(centre) + X.reshape(-1, 1) * right + Y.reshape(-1, 1) * up - fwd * 6
    d = np.broadcast_to(fwd, o.shape).copy()
    t, hit = march(scene, o, d)
    p = o + d * t[:, None]
    ink = np.zeros(res * res, bool)
    carve = np.ones(res * res, bool)
    ids = np.full(res * res, -1)
    hp = p[hit]
    e = 1e-3
    n = nz(np.stack([scene.dist(hp + np.array(v) * e)[0] - scene.dist(hp - np.array(v) * e)[0] for v in np.eye(3)], -1))
    _, id_ = scene.dist(hp)
    ids[hit] = id_
    lam = np.clip(n @ scene.light, 0, 1)
    sh = shadow(scene, hp + n * 2e-3, scene.light)
    light = 0.04 + 0.8 * lam * (0.2 + 0.8 * sh)
    u = np.zeros(len(hp))
    pitch = np.zeros(len(hp))
    keep = np.zeros(len(hp), bool)
    for i, pt in enumerate(scene.parts):
        m = id_ == i
        if not m.any():
            continue
        q = pt.local(hp[m])
        nl = n[m] @ pt.R
        u[m] = pt.hatch(q, nl) if pt.hatch else q[:, 1]
        pitch[m] = pt.pitch
        if pt.ink:
            keep[m] = pt.ink(q, nl)
    g = id_ == len(scene.parts)
    if g.any():
        r = np.hypot(hp[g, 0] - centre[0], hp[g, 2] - centre[2])
        fade = np.clip((r - ground_r * 0.55) / (ground_r * 0.45), 0, 1)
        light[g] = np.maximum(0.62 * (0.35 + 0.65 * sh[g]), fade ** 0.7)
        fg = np.array([fwd[0], 0, fwd[2]]) / (np.hypot(fwd[0], fwd[2]) + 1e-9)
        u[g] = hp[g] @ fg
        pitch[g] = 0.05
    s = np.abs((u / (pitch * lines)) % 1 - 0.5) * 2
    cut = (s < light ** 1.25 * 1.1) | (light > 0.8)
    cut &= ~keep
    carve[hit] = cut
    ink[hit] = ~cut
    ink = ink.reshape(res, res)
    ids = ids.reshape(res, res)
    tt = np.where(hit, t, 99).reshape(res, res)
    # outline: silhouettes and creases between parts stay uncut
    edge = np.zeros_like(ink)
    for ax in (0, 1):
        for sft in (1, -1):
            edge |= (np.roll(ids, sft, ax) != ids) & (ids >= 0) & (ids != len(scene.parts))
            edge |= (np.abs(np.roll(tt, sft, ax) - tt) > 0.08) & (ids >= 0) & (ids != len(scene.parts))
    edge = ndimage.binary_dilation(edge, iterations=max(1, res // 450))
    ink |= edge
    ink = ndimage.binary_opening(ink, iterations=1)
    return ink


def svg_path(mask, size=100):
    return trace_ink(mask, size / mask.shape[0], turd=10)
