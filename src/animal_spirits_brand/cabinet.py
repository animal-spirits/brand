"""The cabinet: eight objects of the trade, each a scene for engrave.render."""
import numpy as np
from scipy import ndimage

from .engrave import capsule, Part, Scene, rot, sphere, rcyl, rbox, torus, revolve, render, svg_path, length

D = np.radians


def coins():
    th, r = 0.07, 0.17
    parts = []
    xs = [-0.84, -0.42, 0.0, 0.42, 0.84]
    for x, n in zip(xs, [3, 6, 5, 9, 13]):
        def f(q, n=n):
            k = np.clip(np.floor(q[:, 1] / th), 0, n - 1)
            qq = q.copy()
            qq[:, 1] = q[:, 1] - (k * th + th / 2)
            return rcyl(r, th / 2 * 0.94, 0.014)(qq)
        hatch = lambda q, nl: np.where(nl[:, 1] > 0.7, q[:, 0] * 0.8 + q[:, 2] * 0.6, q[:, 1] * 1.0)
        parts.append(Part(f, (x, 0, 0), hatch=hatch, pitch=0.0175))
    return Scene(parts, ground=0.0), dict(span=2.5, pitch_deg=20, centre=(0, 0.42, 0), ground_r=1.5)


def globe():
    tilt = rot(az=D(-23.4))
    c = np.array([0, 1.08, 0])
    def lat(q, nl):
        return q[:, 1]
    from .land import land_mask
    L = ndimage.binary_opening(land_mask(), structure=np.ones((5, 1)))
    def mer(q, nl):
        lon = np.arctan2(q[:, 0], q[:, 2]) + np.radians(-15)
        lat = np.arcsin(np.clip(q[:, 1] / 0.62, -1, 1))
        a = np.abs((lon / (np.pi / 6)) % 1 - 0.5)
        i = np.clip(((np.pi / 2 - lat) / np.pi * L.shape[0]).astype(int), 0, L.shape[0] - 1)
        j = ((lon / (2 * np.pi) + 0.5) % 1 * L.shape[1]).astype(int) % L.shape[1]
        land = L[i, j]
        return land | (a > 0.46) | (np.abs(q[:, 1]) < 0.008)
    parts = [Part(sphere(0.62), c, tilt, hatch=lat, ink=mer, pitch=0.03),
             Part(torus(0.71, 0.022), c, tilt @ rot(ax=D(90)), hatch=lambda q, nl: np.arctan2(q[:, 2], q[:, 0]) * 0.7, pitch=0.03),
             Part(rcyl(0.035, 0.17), (0, 0.2, 0), pitch=0.02, hatch=lambda q, nl: np.arctan2(q[:, 2], q[:, 0]) * 0.05),
             Part(rcyl(0.36, 0.035, 0.02), (0, 0.035, 0), hatch=lambda q, nl: np.where(nl[:, 1] > .7, np.hypot(q[:, 0], q[:, 2]), q[:, 1]), pitch=0.025)]
    return Scene(parts, ground=0.0), dict(span=2.3, pitch_deg=16, centre=(0, 0.88, 0), ground_r=1.1)


PIPS = {  # face normal -> pips (u, v) in units of .15
    (0, 1, 0): [(-1, -1), (1, 1), (0, 0), (-1, 1), (1, -1)],
    (1, 0, 0): [(-1, -1), (0, 0), (1, 1)],
    (0, 0, 1): [(-1, -1), (1, 1), (-1, 1), (1, -1), (-1, 0), (1, 0)],
    (-1, 0, 0): [(-1, -1), (1, 1), (-1, 1), (1, -1)],
    (0, 0, -1): [(0, 0)], (0, -1, 0): [(-1, -1), (1, 1)]}


def die_sdf(s=0.3):
    box = rbox([s, s, s], 0.07)
    centres = []
    for nrm, pips in PIPS.items():
        nrm = np.array(nrm, float)
        a = np.roll(nrm, 1) if nrm[1] == 0 else np.array([1., 0, 0])
        b = np.cross(nrm, a)
        for u, v in pips:
            centres.append(nrm * (s + 0.035) + (a * u + b * v) * 0.15)
    C = np.array(centres)
    def f(q):
        if q is None:
            return C
        dp = np.min(np.linalg.norm(q[:, None, :] - C[None], axis=-1), axis=1) - 0.085
        return np.maximum(box(q), -dp)
    return f


def dice():
    def hatch(q, nl):
        ax = np.abs(nl).argmax(-1)
        return np.choose(ax, [q[:, 1] + 0.3 * q[:, 2], q[:, 0] * 0.7 + q[:, 2] * 0.7, q[:, 1] - 0.3 * q[:, 0]])
    f = die_sdf()
    C = f(None)
    pip = lambda q, nl: np.min(np.linalg.norm(q[:, None, :] - C[None], axis=-1), axis=1) < 0.1
    parts = [Part(f, (-0.36, 0.3, 0.05), rot(ay=D(28)), hatch=hatch, ink=pip, pitch=0.03),
             Part(f, (0.42, 0.3, -0.12), rot(ay=D(-22)), hatch=hatch, ink=pip, pitch=0.03)]
    return Scene(parts, ground=0.0), dict(span=2.1, pitch_deg=30, centre=(0, 0.3, 0), ground_r=1.2)


def hourglass():
    def bulb(rho, y):
        z = np.clip(np.abs(y - 0.7) / 0.6, 0, 1)
        r = 0.045 + 0.25 * np.sin(np.pi * z) ** 0.75
        return np.maximum((rho - r) * 0.55, np.abs(y - 0.7) - 0.62)
    posts = [Part(rcyl(0.028, 0.66), (0.37 * np.cos(D(a)), 0.7, 0.37 * np.sin(D(a))), pitch=0.02,
                  hatch=lambda q, nl: np.arctan2(q[:, 2], q[:, 0]) * 0.03) for a in (100, 220, 340)]
    plate = lambda y: Part(rcyl(0.44, 0.04, 0.02), (0, y, 0), hatch=lambda q, nl: np.where(np.abs(nl[:, 1]) > .7, np.hypot(q[:, 0], q[:, 2]), q[:, 1]), pitch=0.022)
    parts = [Part(revolve(bulb), (0, 0, 0), hatch=lambda q, nl: q[:, 1], pitch=0.026,
                  ink=lambda q, nl: (q[:, 1] < 0.36) & (q[:, 1] > 0.1) & ((q[:, 1] * 80) % 1 < 0.35))] + posts + [plate(0.04), plate(1.36)]
    return Scene(parts, ground=0.0), dict(span=2.0, pitch_deg=14, centre=(0, 0.7, 0), ground_r=1.0)


def bowler():
    parts = [Part(rcyl(0.3, 0.22, 0.2), (0, 0.3, 0), hatch=lambda q, nl: np.where(nl[:, 1] > 0.6, q[:, 0] * 0.7 + q[:, 2] * 0.7, q[:, 1]), pitch=0.024),
             Part(rcyl(0.306, 0.035, 0.005), (0, 0.13, 0), ink=lambda q, nl: np.ones(len(q), bool), pitch=0.02),
             Part(rcyl(0.5, 0.012, 0.01), (0, 0.075, 0), hatch=lambda q, nl: np.hypot(q[:, 0], q[:, 2]), pitch=0.022),
             Part(torus(0.49, 0.03), (0, 0.095, 0), hatch=lambda q, nl: q[:, 1] * 2, pitch=0.02)]
    return Scene(parts, ground=0.0), dict(span=1.55, pitch_deg=22, centre=(0, 0.25, 0), ground_r=0.85)


def hat():
    sc, kw = bowler()
    sc.ground = None
    return sc, dict(kw, span=1.1, centre=(0, 0.2, 0))


def balance():
    vert = lambda q, nl: np.arctan2(q[:, 2], q[:, 0]) * 0.04
    flat = lambda q, nl: np.where(np.abs(nl[:, 1]) > .7, np.hypot(q[:, 0], q[:, 2]), q[:, 1])
    tilt = D(7)
    parts = [Part(rcyl(0.36, 0.04, 0.02), (0, 0.04, 0), hatch=flat, pitch=0.022),
             Part(rcyl(0.15, 0.05, 0.02), (0, 0.12, 0), hatch=flat, pitch=0.022),
             Part(rcyl(0.035, 0.62), (0, 0.78, 0), hatch=vert, pitch=0.02),
             Part(sphere(0.065), (0, 1.42, 0), pitch=0.02),
             Part(rbox([0.82, 0.028, 0.028], 0.01), (0, 1.34, 0), rot(az=tilt), pitch=0.02, hatch=lambda q, nl: q[:, 0] * 0.3 + q[:, 1])]
    for sx in (-1, 1):
        ex, ey = 0.8 * np.cos(tilt) * sx, 1.34 + 0.8 * np.sin(tilt) * sx
        py = ey - 0.62
        for dz in (-0.2, 0.2):
            for dx in (-0.2, 0.2):
                if dz < 0 and dx < 0:
                    continue
                parts.append(Part(capsule((ex, ey, 0), (ex + dx, py + 0.02, dz), 0.006), (0, 0, 0), pitch=0.02))
        parts.append(Part(revolve(lambda rho, yy: np.maximum(np.abs(np.hypot(rho, yy - 0.34) - 0.34) - 0.014, yy - 0.06)), (ex, py - 0.06, 0),
                          hatch=lambda q, nl: q[:, 1] * 1.4, pitch=0.02))
    return Scene(parts, ground=0.0), dict(span=2.3, pitch_deg=14, centre=(0, 0.72, 0), ground_r=1.2)


def ledger_book():
    def page(side):
        return rbox([0.66, 0.025, 0.5], 0.01)
    rules = lambda q, nl: (nl[:, 1] > 0.6) & ((((q[:, 2] + 0.5) / 0.07) % 1 < 0.2) & (np.abs(q[:, 2]) < 0.44) & (np.abs(q[:, 0]) > 0.06)
                           | ((np.abs(np.abs(q[:, 0]) - 0.5) < 0.008) & (np.abs(q[:, 2]) < 0.45)))
    hatch = lambda q, nl: np.where(nl[:, 1] > 0.6, q[:, 2] * 0.3 + q[:, 0], q[:, 1])
    parts = [Part(page(-1), (-0.68, 0.26, 0), rot(az=D(-7)), hatch=hatch, ink=rules, pitch=0.03),
             Part(page(1), (0.68, 0.26, 0), rot(az=D(7)), hatch=hatch, ink=rules, pitch=0.03),
             Part(rbox([1.42, 0.1, 0.54], 0.03), (0, 0.08, 0), hatch=lambda q, nl: q[:, 1] + 0.2 * q[:, 0], pitch=0.018)]
    return Scene(parts, ground=0.0), dict(span=3.3, pitch_deg=58, yaw_deg=0, centre=(0, 0.2, 0), ground_r=1.8)


def ship():
    box = rbox([1.2, 0.16, 0.2], 0.015)
    n1, n2 = np.array([0.45, 0, 1]) / np.hypot(0.45, 1), np.array([0.45, 0, -1]) / np.hypot(0.45, 1)
    def hull(q):
        bow = np.maximum((q - [0.85, 0, 0]) @ n1, (q - [0.85, 0, 0]) @ n2)
        keel = (q - [0, -0.16, 0]) @ (np.array([0.5, -1, 0]) / np.hypot(0.5, 1)) - 0.25
        return np.maximum(np.maximum(box(q), bow), keel)
    side = lambda q, nl: q[:, 1]
    parts = [Part(hull, (0, 0.16, 0), hatch=side, pitch=0.018, ink=lambda q, nl: (q[:, 1] < -0.02) & (q[:, 1] > -0.06))]
    hs = [2, 3, 2, 3, 3, 2]
    for i, x in enumerate(np.arange(-0.55, 0.75, 0.24)):
        h = 0.085 * hs[i]
        corr = lambda q, nl: (np.abs(nl[:, 2]) > .6) & ((q[:, 0] * 16) % 1 < 0.3) | (np.abs(nl[:, 2]) > .6) & ((((q[:, 1] + 0.3) / 0.085) % 1) < 0.1)
        parts.append(Part(rbox([0.105, h / 2, 0.17], 0.004), (x, 0.32 + h / 2, 0), hatch=lambda q, nl: q[:, 1] + q[:, 0] * 0.3,
                          ink=corr, pitch=0.022))
    win = lambda q, nl: (np.abs(nl[:, 2]) > .6) & (np.abs(q[:, 1] - 0.1) < 0.025) & ((q[:, 0] * 25) % 1 < 0.5)
    parts += [Part(rbox([0.14, 0.2, 0.18], 0.01), (-0.92, 0.52, 0), hatch=side, pitch=0.02, ink=win),
              Part(rbox([0.18, 0.012, 0.2], 0.005), (-0.92, 0.73, 0), hatch=side, pitch=0.02),
              Part(rcyl(0.065, 0.15, 0.01), (-0.98, 0.9, 0), hatch=side, pitch=0.02, ink=lambda q, nl: np.abs(q[:, 1] - 0.08) < 0.035)]
    sc = Scene(parts, ground=0.06)
    return sc, dict(span=2.75, pitch_deg=6, yaw_deg=-14, centre=(0, 0.45, 0), ground_r=1.5)


OBJECTS = dict(globe=globe, coins=coins, dice=dice, hourglass=hourglass, bowler=bowler, balance=balance, ledger=ledger_book, ship=ship, hat=hat)
CAPTIONS = dict(globe="the open economy", coins="accumulation", dice="quantitative probabilities", hourglass="the long run",
                bowler="the City", balance="equilibrium", ledger="the accounts", ship="trade")

