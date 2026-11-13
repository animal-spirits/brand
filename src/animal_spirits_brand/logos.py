"""Logo compositions. Each is drawn in one of three versions: on dark, on light, or single colour (currentColor)."""
from dataclasses import dataclass

from . import portrait, wordmark

CAP = wordmark.cap_height()          # 80 units
LEADING = 14.0                       # white between the two lines of the stacked wordmark
TILE = 2 * CAP + LEADING             # the block spans both lines, cap top to baseline
GAP = 26.0                           # block to wordmark
MARGIN = 10.0


@dataclass
class Version:
    ink: str | None      # letters; None = currentColor single-colour version
    block: str = ""      # the red block
    face: str = ""       # Keynes inside the block


def version(c: dict) -> Version:
    """c: one mode's UI colours. Letters take the text colour; the block is always red with Keynes in ink."""
    return Version(c["text"], c["accent"], c["on-accent"])


MONO = Version(None)


def _block(x: float, y: float, s: float, cut: int, v: Version) -> str:
    k = s / portrait.SIZE
    face = portrait.cut(cut)
    t = f'transform="translate({x:g} {y:g}) scale({k:.5f})"'
    if v.ink is None:  # single colour: Keynes alone in currentColor, no block (a knocked-out block prints him as a negative)
        return f'<path {t} fill="currentColor" fill-rule="evenodd" d="{face}"/>'
    return (f'<rect x="{x:g}" y="{y:g}" width="{s:g}" height="{s:g}" fill="{v.block}"/>'
            f'<path {t} fill="{v.face}" fill-rule="evenodd" d="{face}"/>')


def _letters(d: str, v: Version) -> str:
    return f'<path fill="{v.ink or "currentColor"}" d="{d}"/>'


def _svg(w: float, h: float, body: str, title: str, bg: str | None = None, pad: float = MARGIN) -> str:
    x0, y0, W, H = -pad, -pad, w + 2 * pad, h + 2 * pad
    rect = f'<rect x="{x0:g}" y="{y0:g}" width="{W:g}" height="{H:g}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:g} {y0:g} {W:.2f} {H:.2f}" width="{W:.0f}" height="{H:.0f}" '
            f'role="img" aria-label="{title}"><title>{title}</title>{rect}{body}</svg>\n')


def lockup(v: Version, bg: str | None = None) -> str:
    """The block on the left, ANIMAL over SPIRITS on the right. The block is as tall as the two lines."""
    x = TILE + GAP
    a, ra = wordmark.line("ANIMAL", x, CAP)
    s, rs = wordmark.line("SPIRITS", x, 2 * CAP + LEADING)
    return _svg(max(ra, rs), TILE, _block(0, 0, TILE, 1, v) + _letters(a + s, v), "Animal Spirits", bg)


def bar(v: Version, bg: str | None = None) -> str:
    """One line, for site headers and footers: a block the height of the caps, then ANIMAL SPIRITS."""
    d, r = wordmark.line("ANIMAL SPIRITS", CAP + 18, CAP)
    return _svg(r, CAP, _block(0, 0, CAP, 2, v) + _letters(d, v), "Animal Spirits", bg)


def word(v: Version, bg: str | None = None) -> str:
    """ANIMAL SPIRITS on one line, no block."""
    d, r = wordmark.line("ANIMAL SPIRITS", 0, CAP)
    return _svg(r, CAP, _letters(d, v), "Animal Spirits", bg)


def stacked(v: Version, bg: str | None = None) -> str:
    a, ra = wordmark.line("ANIMAL", 0, CAP)
    s, rs = wordmark.line("SPIRITS", 0, 2 * CAP + LEADING)
    return _svg(max(ra, rs), TILE, _letters(a + s, v), "Animal Spirits", bg)


def mark(v: Version, cut: int = 1) -> str:
    """The block alone, Keynes inside."""
    return _svg(100, 100, _block(0, 0, 100, cut, v), "Animal Spirits", pad=0)


def avatar(v: Version, bg: str) -> str:
    """The block inset on a square of ground, cut 2. 100-unit square."""
    return _svg(100, 100, f'<rect width="100" height="100" fill="{bg}"/>' + _block(10, 10, 80, 2, v), "Animal Spirits", pad=0)


def favicon(v: Version) -> str:
    """Full-bleed block, cut 3."""
    return _svg(100, 100, _block(0, 0, 100, 3, v), "Animal Spirits", pad=0)
