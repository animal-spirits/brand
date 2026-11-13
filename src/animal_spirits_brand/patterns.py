"""Patterns: Utility (indifference curves, the quiet ground) and Crowd (bowler hats, the loud one)."""
import numpy as np

W, H = 600, 400


def pl(pts, w, c, op=1.0):
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-opacity="{op}" stroke-linecap="round"/>'


def utility(c, op=1.0):
    """Indifference curves x*y = k from an origin off the bottom-left corner; every fifth curve heavier."""
    out = []
    ox, oy = -60, H + 60
    for i in range(1, 80):
        k = (i * 15.0) ** 2
        xs = np.geomspace(k / (W + 200), W + 200, 160)
        pts = [(ox + x, oy - k / x) for x in xs]
        out.append(pl(pts, 2.0 if i % 5 == 0 else 0.9, c, op))
    return "".join(out)


def svg(inner, bg, w=W, h=H):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice"><rect width="{w}" height="{h}" fill="{bg}"/>{inner}</svg>'


def crowd(hat_d, c, op=1.0, s=34, gap=10):
    """Bowler hats in half-drop rows."""
    uses = []
    for j in range(-1, int(H / (s * 0.62)) + 2):
        for i in range(-1, int(W / (s + gap)) + 2):
            x = i * (s + gap) + (j % 2) * (s + gap) / 2
            y = j * s * 0.62
            uses.append(f'<use href="#hat" transform="translate({x:.1f} {y:.1f}) scale({s / 100:.3f})"/>')
    return f'<defs><path id="hat" d="{hat_d}" fill-rule="evenodd"/></defs><g fill="{c}" fill-opacity="{op}">{"".join(uses)}</g>'


def crowd_tile(hat_d, c, op=1.0, s=34, gap=10):
    """One repeatable tile of the crowd, for CSS background-repeat."""
    w, r = s + gap, s * 0.62
    pos = [(x, y) for x in (-w, 0, w) for y in (-2 * r, 0, 2 * r)] + [(x, y) for x in (-w / 2, w / 2, 1.5 * w) for y in (-r, r, 3 * r)]
    uses = "".join(f'<use href="#hat" transform="translate({x:.1f} {y:.1f}) scale({s / 100:.3f})"/>' for x, y in pos)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {2 * r:.1f}" width="{w:.1f}" height="{2 * r:.1f}">'
            f'<defs><path id="hat" d="{hat_d}" fill-rule="evenodd"/></defs><g fill="{c}" fill-opacity="{op}">{uses}</g></svg>')
