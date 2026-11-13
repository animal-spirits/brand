"""The studio ident, 1.6 s at 1920 x 1080. The block is pressed, a roller inks Keynes left to right, the name is set
letter by letter, then everything holds and fades. The game version adds the stamp line. Reduced motion shows the final
frame. parts() gives the stage alone (classes prefixed id-) so the site can play it as its opening."""
from . import portrait, wordmark
from .logos import CAP, GAP, LEADING, TILE
from .palette import UI
from .patterns import svg as pattern_svg, utility

GROUND, BLOCK = .0, .08      # utility ground fades in; the block lands at once
ROLL0, ROLL = .14, .30       # the roller crosses the block
LETTER0, STEP = .44, .026    # then the letters, top line first
LINE = .86                   # game version: the stamp line
FADE0, END = 1.30, 1.60


def parts(game: str | None = None) -> tuple[str, str]:
    """(css, html) for a 1920 x 1080 stage, scaled to its container by --k."""
    bg, text, muted, red, ink = UI["bg"][0], UI["text"][0], UI["text-muted"][0], UI["accent"][0], UI["on-accent"][0]
    x = TILE + GAP
    a, ra = wordmark.glyphs("ANIMAL", x, CAP)
    s, rs = wordmark.glyphs("SPIRITS", x, 2 * CAP + LEADING)
    W = max(ra, rs)
    k = TILE / portrait.SIZE
    letters = "".join(f'<path class="id-l" style="animation-delay:{LETTER0 + i * STEP:.3f}s" d="{d}"/>' for i, d in enumerate(a + s))
    line = f'<div class="id-line">{game} · an animal spirits game</div>' if game else ""
    ground = pattern_svg(utility(text, .07), bg).replace("<svg ", '<svg class="id-ground" ', 1)
    ease = "cubic-bezier(.45,.05,.4,1)"
    css = f"""
.id-stage{{position:absolute;left:50%;top:50%;width:1920px;height:1080px;transform:translate(-50%,-50%) scale(var(--k,1));background:{bg}}}
.id-ground{{position:absolute;inset:0;width:100%;height:100%;opacity:0;animation:id-in .4s {GROUND}s ease-out forwards}}
.id-all{{position:absolute;inset:0;animation:id-out {END - FADE0:.2f}s {FADE0}s ease-in forwards}}
.id-lock{{position:absolute;left:50%;top:50%;width:1040px;transform:translate(-50%,-56%);overflow:visible}}
.id-block{{opacity:0;transform-box:fill-box;transform-origin:center;animation:id-press .08s {BLOCK}s ease-out forwards}}
.id-face{{clip-path:inset(0 100% 0 0);animation:id-roll {ROLL}s {ROLL0}s {ease} forwards}}
.id-roller{{opacity:0;animation:id-roller {ROLL}s {ROLL0}s {ease} forwards}}
.id-l{{fill:{text};opacity:0;animation:id-in 0s linear forwards}}
.id-line{{position:absolute;left:0;right:0;top:calc(50% + 190px);text-align:center;font:500 30px 'IBM Plex Mono',monospace;color:{muted};
  letter-spacing:.04em;opacity:0;animation:id-in .2s {LINE}s ease-out forwards}}
@keyframes id-in{{to{{opacity:1}}}} @keyframes id-out{{to{{opacity:0}}}}
@keyframes id-press{{from{{opacity:1;transform:scale(1.025)}}to{{opacity:1;transform:scale(1)}}}}
@keyframes id-roll{{to{{clip-path:inset(0 0 0 0)}}}}
@keyframes id-roller{{0%{{opacity:1;transform:translateX(0)}}92%{{opacity:1}}100%{{opacity:0;transform:translateX({TILE:g}px)}}}}
@media (prefers-reduced-motion:reduce){{.id-stage *{{animation-duration:0s!important;animation-delay:0s!important}} .id-all{{animation:none}}}}
"""
    html = f"""<div class="id-stage"><div class="id-all">{ground}
<svg class="id-lock" viewBox="0 0 {W:.1f} {TILE:g}" role="img" aria-label="Animal Spirits">
<g class="id-block"><rect width="{TILE:g}" height="{TILE:g}" fill="{red}"/>
<g class="id-face"><path transform="scale({k:.5f})" fill="{ink}" fill-rule="evenodd" d="{portrait.cut(1)}"/></g>
<rect class="id-roller" x="-4" y="-4" width="8" height="{TILE + 8:g}" fill="{ink}"/></g>{letters}</svg>{line}</div></div>"""
    return css, html


def html(game: str | None = None) -> str:
    css, body = parts(game)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Animal Spirits ident</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500&display=swap">
<style>html,body{{margin:0;height:100%;background:{UI["bg"][0]};overflow:hidden}}{css}</style></head><body>{body}
<script>
const fit = () => document.documentElement.style.setProperty('--k', Math.min(innerWidth / 1920, innerHeight / 1080));
addEventListener('resize', fit); fit();
</script></body></html>
"""
