"""The brand book: an A4 PDF built from the palette, the logo files and the drawing code.
Needs the `png` extra and the files from `uv run animal-spirits-brand` and scripts/export_png.py: uv run --extra png scripts/book.py
Layout follows zaofang/brand's book (MIT)."""
import asyncio
import base64
import os
import re
import tomllib
from pathlib import Path
from urllib.parse import quote

from playwright.async_api import async_playwright

from animal_spirits_brand import wordmark
from animal_spirits_brand.cabinet import CAPTIONS
from animal_spirits_brand.build import LETTER0, LETTER_STEP, SETTLE, STAMP
from animal_spirits_brand.logos import CAP, GAP, LEADING, TILE
from animal_spirits_brand.palette import ANSI, ANSI_NAMES, SYNTAX, TYPE_SCALE, UI, contrast

ROOT = Path(__file__).resolve().parents[1]
VERSION = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
D, L = 0, 1
BG, PAPER, INK, TEXT = UI["bg"][D], UI["bg"][L], UI["text"][L], UI["text"][D]
RED = UI["accent"][D]
GAMES = ["ceteris", "metropole", "strata", "hohmann", "foundry"]


def img(rel: str, style: str = "") -> str:
    p = ROOT / rel
    mime = "image/svg+xml" if p.suffix == ".svg" else "image/png"
    return f'<img src="data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}" style="display:block;{style}" alt="">'


def uri(rel: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode((ROOT / rel).read_bytes()).decode()


def inline(rel: str, style: str) -> str:
    s = re.sub(r' width="[^"]*" height="[^"]*"', "", (ROOT / rel).read_text(), count=1)
    return s.replace("<svg ", f'<svg style="display:block;{style}" ', 1)


def ruling(colour: str, opacity: float = .10) -> str:
    return f"background-image:linear-gradient(transparent 23px,{colour}{round(opacity * 255):02X} 23px);background-size:100% 24px"


GRAIN = ("background-image:url('data:image/svg+xml," + quote(
    '<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240"><filter id="n"><feTurbulence type="fractalNoise" '
    'baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 .09 0 0 0 0 .07 0 0 0 0 .06 0 0 0 .05 0"/>'
    '</filter><rect width="240" height="240" filter="url(#n)"/></svg>') + "')")

HATCH = ("background-image:url('data:image/svg+xml," + quote(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><rect width="200" height="200" fill="{BG}"/>'
    + "".join(f'<path d="M0 {y} C50 {y - 6} 150 {y + 6} 200 {y}" stroke="{RED}" stroke-width="{1.2 + 2.6 * abs((y - 100) / 100):.1f}" fill="none"/>'
              for y in range(5, 200, 10)) + '</svg>') + "')")

STRIPES = ("background-image:url('data:image/svg+xml," + quote(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12"><path d="M0 12L12 0M-3 3L3 -3M9 15L15 9" stroke="{UI["text-muted"][L]}" stroke-width="4"/></svg>') + "')")


def frame(t: float) -> str:
    """motion/typeon.svg as it stands at t seconds."""
    x = TILE + GAP
    a, ra = wordmark.glyphs("ANIMAL", x, CAP)
    s, rs = wordmark.glyphs("SPIRITS", x, 2 * CAP + LEADING)
    shown = [d for i, d in enumerate(a + s) if t >= LETTER0 + i * LETTER_STEP]
    block = re.search(r'<g class="b">(.*?)</g>', (ROOT / "motion/typeon.svg").read_text()).group(1) if t >= STAMP else ""
    W = max(ra, rs)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-12 -12 {W + 24:.1f} {TILE + 24:.1f}" style="display:block;width:100%">'
            f'{block}{"".join(f"<path fill=\"{TEXT}\" d=\"{d}\"/>" for d in shown)}</svg>')


CSS = f"""@page{{size:210mm 297mm;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
body{{font:400 15px/1.6 'IBM Plex Sans',sans-serif;color:{INK}}}
.pg{{width:794px;height:1123px;position:relative;overflow:hidden;break-after:page;background:{PAPER}}}
.paper{{{GRAIN};padding:150px 76px 0}}
.lab,code,.mono{{font-family:'IBM Plex Mono',monospace}} code{{white-space:nowrap;font-size:.92em}}
.lab{{font-size:11px;color:{UI["text-muted"][L]};letter-spacing:.02em}}
.hd{{position:absolute;left:76px;right:76px;top:56px;display:flex;justify-content:space-between;border-top:2px solid {INK};padding-top:10px}}
.ft{{position:absolute;left:76px;right:76px;bottom:48px;display:flex;justify-content:space-between}}
h1{{font:600 60px/1.05 'Source Serif 4',serif;letter-spacing:-.01em}}
h2{{font:600 30px/1.15 'Source Serif 4',serif;margin:44px 0 14px}}
p,li{{font:400 17px/1.6 'Source Serif 4',serif;max-width:540px}}
p+p{{margin-top:10px}} ul{{list-style:none}} li{{padding-left:18px;position:relative}}
li::before{{content:"";position:absolute;left:0;top:.6em;width:7px;height:7px;background:{RED}}}
.num{{font:600 120px/1 'Source Serif 4',serif;color:{UI["border"][L]}}}
.rule{{border-top:1px solid {UI["border"][L]}}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:12px}} .grid3{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}}
.panel{{display:grid;place-items:center;padding:28px}}
.cap{{margin-top:6px}}
table{{border-collapse:collapse;width:100%}} td,th{{text-align:left;padding:7px 8px 7px 0;vertical-align:middle;font-weight:400}}
table.led{{font:13px 'IBM Plex Mono',monospace;font-variant-numeric:tabular-nums}} table.led th{{color:{UI["text-muted"][L]};font-size:12px}}
table.led td:not(:first-child),table.led th:not(:first-child){{text-align:right}} table.led tr.tot td{{border-top:1px solid {INK};border-bottom:3px double {INK}}}
sup.fn{{font:500 10px 'IBM Plex Mono',monospace;background:{RED};color:{INK};padding:1px 4px;vertical-align:5px}}
.paper tr{{border-top:1px solid {UI["border"][L]}}} .paper td{{font-size:15px}}
.man{{background:{BG};color:{TEXT};font:13px/1.6 'IBM Plex Mono',monospace;padding:118px 64px 0;{ruling(TEXT, .06)}}}
.man .mh,.man .mf{{position:absolute;left:64px;right:64px;display:flex;justify-content:space-between;color:{UI["text-muted"][D]}}}
.man .mh{{top:48px}} .man .mf{{bottom:40px}}
.man .s{{font-weight:500;margin:22px 0 6px}} .man .i{{padding-left:48px;color:#C9C1B3}}
.man .m{{color:{UI["text-muted"][D]}}} .man tr{{border-top:1px solid {UI["border"][D]}}} .man td{{padding:4px 8px 4px 0}}
.chip{{display:inline-block;width:40px;height:22px;vertical-align:middle;outline:1px solid rgba(128,128,128,.35);outline-offset:-1px}}
blockquote{{font:italic 400 22px/1.45 'Source Serif 4',serif;max-width:600px;border-left:3px solid {RED};padding-left:20px}}
"""


class Book:
    def __init__(self, title: str) -> None:
        self.title = title
        self.pages: list[str] = []
        self.starts: list[int] = []

    def chapter(self) -> None:
        self.starts.append(self.n)

    @property
    def n(self) -> int:
        return len(self.pages) + 1

    def paper(self, chapter: str, body: str, at: int | None = None) -> None:
        page = (f'<section class="pg paper"><div class="hd"><span class="lab">{self.title}</span>'
                f'<span class="lab">{chapter}</span></div>{body}<div class="ft"><span class="lab">{chapter}</span>'
                f'<span class="lab">{(at or self.n):02}</span></div></section>')
        if at:
            self.pages[at - 1] = page
        else:
            self.pages.append(page)

    def man(self, section: str, body: str) -> None:
        self.pages.append(f'<section class="pg man"><div class="mh"><span>ANIMAL-SPIRITS(7)</span><span>{section}</span><span>ANIMAL-SPIRITS(7)</span></div>'
                          f'{body}<div class="mf"><span>animal-spirits/brand {VERSION}</span><span>{self.n:02}</span></div></section>')

    def raw(self, html: str) -> None:
        self.pages.append(html)


def opener(num: str, title: str, intro: str) -> str:
    return f'<div class="num">{num}</div><h1 style="margin-top:20px">{title}</h1><p style="margin-top:22px">{intro}</p>'


def panel(content: str, bg: str, cap: str, style: str = "") -> str:
    return f'<div><div class="panel" style="background:{bg};{style}">{content}</div><div class="lab cap">{cap}</div></div>'


def rows2(pairs, w: int = 240) -> str:
    return "".join(f'<tr><td style="width:{w}px">{k}</td><td>{v}</td></tr>' for k, v in pairs)


def build() -> str:
    chapters = ["Name", "Story and voice", "Logo", "Woodcuts and cabinet", "Colour", "Type", "Motion", "Patterns and devices", "Lexicon", "Games", "Applications"]
    label = lambda i: f"{i + 1:02} {chapters[i].lower()}"  # noqa: E731
    b = Book("animal spirits · brand identity")

    # Cover and contents
    b.raw(f'<section class="pg" style="background:{BG};color:{TEXT};{ruling(TEXT, .07)}">'
          f'<div style="position:absolute;left:76px;top:76px;color:{UI["text-muted"][D]}" class="lab">animal spirits · brand identity · {VERSION}</div>'
          f'<div style="position:absolute;left:76px;width:560px;top:400px">{img("logo/lockup-on-dark.svg", "width:100%")}</div>'
          f'<div style="position:absolute;left:76px;bottom:64px;right:76px;display:flex;justify-content:space-between;color:{UI["text-muted"][D]}" class="lab">'
          f'<span>{" · ".join(GAMES)}</span><span>github.com/animal-spirits</span></div></section>')
    b.raw("")

    # 01 Name
    b.chapter()
    b.paper(label(0), opener("01", chapters[0], "Animal spirits is Keynes's name for the urge to act that no calculation accounts for. "
                             "The studio builds the calculations anyway.") +
            '<blockquote style="margin-top:40px">Most, probably, of our decisions to do something positive, the full consequences of which '
            'will be drawn out over many days to come, can only be taken as a result of animal spirits: of a spontaneous urge to action '
            'rather than inaction, and not as the outcome of a weighted average of quantitative benefits multiplied by quantitative '
            'probabilities.</blockquote><div class="lab" style="margin:10px 0 0 23px">J. M. Keynes, The General Theory of Employment, '
            'Interest and Money, 1936, chapter 12</div>'
            '<h2>Writing the name</h2><table>' + rows2([
                ("Prose", "Animal Spirits"),
                ("Handles, URLs, code", "<code>animal-spirits</code>"),
                ("Logo", "ANIMAL SPIRITS, drawn, in capitals"),
                ("Never", "AS, AnimalSpirits, Animal Spirits Studio, Animal Spirits Games")]) +
            '</table><p style="margin-top:22px">There is no tagline. The quote explains the name: cite it in full or not at all, '
            'never paraphrase it.</p>')

    # 02 Story and voice
    b.chapter()
    b.paper(label(1), opener("02", chapters[1],
                             "A study after the market closes. A ledger, a model on the desk, and a man on the wall who does not believe it. "
                             "Games built from published data and cited models, by one person who takes them too seriously.") +
            "<p>Show the working, not the size of the studio. One bright thing on the page: the red block behind Keynes.</p>"
            '<h2>Voice</h2><p>Margin notes in a ledger: plain, exact, a little dry.</p><ul style="margin-top:12px">' + "".join(f"<li>{x}</li>" for x in [
                "Address the reader as you, and the game by its name.",
                "Avoid we: it implies a team. I only in devlogs, lab notes and release notes.",
                "Specific over impressive: numbers, units, sources, dates.",
                "Short sentences. No exclamation marks, no emoji. State limits early.",
                "Dry humour at most once, never at the player's expense."]) + '</ul>'
            f'<div class="grid2" style="margin-top:36px"><div class="rule" style="padding-top:12px"><div class="lab">not</div>'
            f'<p style="color:{UI["text-muted"][L]};margin-top:6px">Rewrite history in the ultimate grand strategy experience.</p></div>'
            f'<div class="rule" style="padding-top:12px"><div class="lab">but</div><p style="margin-top:6px">'
            'Ceteris starts on 1 January 2000 with OECD and BACI trade data. Change one thing and run it again.</p></div></div>')

    # 03 Logo
    b.chapter()
    b.paper(label(2), opener("03", chapters[2],
                             "Every mark follows the Woodcut rule: one ink, solid, cut by hand-width lines. No tone, no outline, no gradient. "
                             "Keynes faces right and is never flipped. One red block per composition.") +
            f'<div style="margin-top:40px;width:480px">{img("logo/lockup-on-light.svg", "width:100%")}</div>'
            '<div class="lab cap" style="margin-top:14px">Primary lockup · logo/lockup-on-light.svg</div>'
            f'<div class="panel" style="background:{BG};margin-top:28px;padding:36px">{img("logo/lockup-on-dark.svg", "width:400px")}</div>'
            '<div class="lab cap">On dark · logo/lockup-on-dark.svg</div>')
    b.paper(label(2), '<h2 style="margin-top:0">Lockup</h2><p>' +
            f"The block on the left, ANIMAL over SPIRITS on the right. The block is exactly as tall as the two lines, from the top of the "
            f"capitals to the last baseline ({TILE:.0f} units), and sits {GAP:.0f} units from the letters.</p>"
            f'<div style="margin-top:28px;width:420px">{img("logo/bar-on-light.svg", "width:100%")}</div>'
            '<div class="lab cap" style="margin-top:10px">Bar · logo/bar-on-light.svg</div>'
            "<p style=\"margin-top:20px\">The bar is the one-line version for site headers, footers and title bars. Its block is the "
            "height of the capitals and uses cut 2.</p>"
            '<h2>Clear space and size</h2><p>Keep half the block clear on every side. Below the minimum width, use the avatar or favicon.</p>'
            f'<div style="display:inline-block;padding:40px;outline:1px dashed {UI["text-muted"][L]};outline-offset:-1px;margin-top:20px">'
            f'<div style="outline:1px solid {UI["border"][L]}">{img("logo/lockup-on-light.svg", "width:300px")}</div></div>'
            '<table style="margin-top:20px">' + rows2([("Lockup", '<span class="mono">120 px · 30 mm</span>'),
                                                       ("Bar", '<span class="mono">160 px · 40 mm</span>'),
                                                       ("Block alone", '<span class="mono">16 px · 5 mm</span>')]) + '</table>')
    b.paper(label(2), '<h2 style="margin-top:0">Wordmark</h2><p>ANIMAL SPIRITS is drawn, never typed: outlined from Big Shoulders Display '
            "Black, capitals only, spaced by hand. Big Shoulders appears nowhere else in the brand.</p>"
            f'<div style="margin-top:32px;width:520px">{img("logo/wordmark-on-light.svg", "width:100%")}</div>'
            '<div class="lab cap">logo/wordmark-on-light.svg</div>'
            f'<div style="margin-top:28px;width:260px">{img("logo/stacked-on-light.svg", "width:100%")}</div>'
            '<div class="lab cap">logo/stacked-on-light.svg</div>'
            '<table style="margin-top:28px">' + rows2([
                ("Cap height", f'<span class="mono">{CAP:.0f} units</span>'),
                ("Letter spacing", f'<span class="mono">+{wordmark.TRACK} units</span>'),
                ("Word space", f'<span class="mono">{wordmark.WORD_GAP:.0f} units</span>'),
                ("Line gap, stacked", f'<span class="mono">{LEADING:.0f} units</span>')]) + '</table>')
    favs = "".join(f'<div style="display:flex;flex-direction:column;align-items:center;gap:8px">{img("logo/favicon.svg", f"width:{s}px")}'
                   f'<span class="lab">{s}</span></div>' for s in (96, 48, 32, 16))
    cuts = "".join(f'<div>{img(f"logo/mark-cut-{n}.svg", "width:100%")}<div class="lab cap">Cut {n} · {r}</div></div>'
                   for n, r in ((1, "above 256 px"), (2, "48 to 256 px"), (3, "below 48 px")))
    b.paper(label(2), '<h2 style="margin-top:0">The block and its three cuts</h2><p>The block is a plain red square with Keynes in ink. '
            "It is the only red in a logo. The portrait comes in three cuts: the original, and two reductions with thicker lines "
            "and fewer gouges, so the face still reads when small.</p>"
            f'<div class="grid3" style="margin-top:28px">{cuts}</div>'
            f'<div class="grid2" style="margin-top:32px">{panel(img("logo/avatar.svg", "width:170px"), BG, "Avatar · logo/avatar.svg")}'
            f'{panel(img("logo/avatar-light.svg", "width:170px"), UI["surface"][L], "Avatar on paper · logo/avatar-light.svg")}</div>'
            f'<div style="display:flex;gap:40px;align-items:end;margin-top:32px">{favs}</div>'
            '<div class="lab cap">Favicon, full-bleed block, cut 3 · logo/favicon.svg, favicon.ico, png/favicon-180.png</div>')
    b.paper(label(2), '<h2 style="margin-top:0">Versions</h2><p>Three, and only three: on dark with paper letters, on light with ink '
            "letters, and single colour. The single-colour version drops the block and prints Keynes in the one ink; a knocked-out "
            "block would print him as a negative.</p>"
            f'<div style="display:grid;gap:12px;margin-top:28px">'
            f'{panel(img("logo/lockup-on-dark.svg", "width:400px"), BG, "On dark")}'
            f'{panel(img("logo/lockup-on-light.svg", "width:400px"), UI["surface"][L], "On light")}'
            f'{panel(inline("logo/lockup-mono.svg", f"width:400px;color:{INK}"), PAPER, "Single colour · currentColor", f"outline:1px solid {UI["border"][L]};outline-offset:-1px")}</div>')
    b.paper(label(2), '<h2 style="margin-top:0">Never</h2><p>Use the files as they are. Anything below needs a new drawing, and the '
            "drawings come from <code>src/</code>.</p>" + misuse() +
            '<ul style="margin-top:28px">' + "".join(f"<li>{x}</li>" for x in [
                "Do not redraw, stretch, rotate, outline or add effects.",
                "Do not flip Keynes, crop his face, or show two blocks.",
                "Do not recolour beyond the three versions.",
                "Do not set ANIMAL SPIRITS in a font, including Big Shoulders.",
                "Do not place the logo on photos or busy patterns."]) + '</ul>')

    # 04 Cabinet
    b.chapter()
    objs = "".join(f'<div><div style="background:{UI["surface"][L]}">{inline(f"cabinet/{n}.svg", f"width:100%;color:{INK}")}</div>'
                   f'<div class="lab cap">{n} · {c}</div></div>' for n, c in CAPTIONS.items())
    b.paper(label(3), opener("04", chapters[3], "Eight objects from an economist's desk, cut in one ink in the hand of the Keynes block. "
                             "They head lab notes, posts and lexicon cards, and print in any single colour.") +
            f'<div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:40px">{objs}</div>')
    tenants = "".join(f'<div>{img(f, "width:100%")}<div class="lab cap">{c}</div></div>' for f, c in [
        ("logo/mark-cut-1.svg", "Keynes: signature"), ("cabinet/globe-block.svg", "lab notes"), ("cabinet/dice-block.svg", "releases"),
        ("cabinet/coins-block.svg", "economy posts"), ("cabinet/hourglass-block.svg", "roadmap"), ("cabinet/bowler-block.svg", "community")])
    b.paper(label(3), '<h2 style="margin-top:0">The block holds a subject</h2><p>Keynes in the block is the signature: logo, avatar, favicon, '
            "sign-off. Everywhere else the same square may hold an object from the cabinet. Still one block per composition, and the "
            "subject is always in ink.</p>"
            f'<div class="grid3" style="margin-top:24px">{tenants}</div>'
            "<h2>Generated woodcuts</h2><p>Animals, objects and scenes come the way Keynes did: generated as a PNG in the portrait's hand, saved to "
            "<code>data/cuts/</code> (woodcuts) or <code>data/cabinet/</code> (objects), and traced by <code>scripts/cabinet.py</code>. "
            "Animals and objects get three cuts; dense scenes only cut 1, at 256 px and above.</p>")
    groups = [("The market", ["bull", "bear", "hawk", "dove", "black-swan", "lame-duck"]),
              ("The state", ["the-assembly", "the-city", "the-seal", "hand"]),
              ("Production and trade", ["steelworks", "anvil", "steam-engine", "machine-hall", "beehive", "ship"])]
    gal = "".join(f'<h2 style="margin-top:{0 if i == 0 else 22}px">{h}</h2><div style="display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px;margin-top:10px">'
                  + "".join(f'<div>{img(f"woodcuts/{w}-cut-1-block.svg", "width:100%")}<div class="lab cap">{w.replace("-", " ")}</div></div>' for w in ws)
                  + "</div>" for i, (h, ws) in enumerate(groups))
    b.paper(label(3), gal + '<div class="grid2" style="margin-top:26px"><div><h2 style="margin-top:0">Prompt rules</h2><ul>' + "".join(f"<li>{x}</li>" for x in [
        "Black ink on flat spirit red #C32B1F, no other colour, no gradient.",
        "Carved gouge lines that follow the form; red shows through.",
        "No solid black larger than an eye; ink about 40 percent of the block.",
        "Same hand as the bull. Square, no text, no frame."]) + '</ul></div><div><h2 style="margin-top:0">Accepting a cut</h2><ul>' + "".join(f"<li>{x}</li>" for x in [
        "Trace all three cuts and look at them at 300, 120 and 48 px.",
        "Cut 3 must still name the subject, or the woodcut is large only.",
        "Too dark in the small cuts: use the LIGHT reductions.",
        "Reject stencils: a woodcut is carved, not filled."]) + "</ul></div></div>")

    # 05 Colour
    b.chapter()

    def ui_row(k: str) -> str:
        cells = ""
        for m in (D, L):
            v = UI[k][m]
            cr = f'{contrast(v, UI["bg"][m]):.1f}' if k not in ("bg", "surface", "surface-2", "selection", "accent", "on-accent") else ""
            cells += f'<td><span class="chip" style="background:{v}"></span></td><td>{v}</td><td class="m">{cr}</td>'
        return f"<tr><td>{k}</td>{cells}</tr>"
    head = '<tr class="m"><td></td><td colspan="3">dark</td><td colspan="3">light</td></tr>'
    prop = (f'<div style="display:flex;height:40px;margin:10px 0 0 48px;outline:1px solid {UI["border"][D]}">'
            f'<div style="flex:70;background:{BG}"></div><div style="flex:25;background:{PAPER}"></div><div style="flex:5;background:{RED}"></div></div>'
            '<div class="i m" style="display:flex;padding-top:4px"><span style="flex:70">70 ground</span>'
            '<span style="flex:25">25 paper or ink</span><span style="flex:5">5</span></div>')
    b.man(chapters[4], '<div class="s" style="margin-top:0">NAME</div><div class="i">Ledger: press-black ground, ledger paper, one red '
          "block. Dark first; paper is a full light mode. Neutrals are warm in both.</div>"
          f'<div class="s">PROPORTION</div>{prop}'
          '<div class="s">TOKENS</div><div class="i m">tokens/tokens.css as --as-*. Third column: contrast on the ground. Every text '
          'colour passes WCAG AA, 4.5:1.</div>'
          f'<table style="margin:10px 0 0 48px;width:calc(100% - 48px)">{head}{"".join(ui_row(k) for k in UI)}</table>'
          '<div class="s">RULES</div><div class="i">Red fills the block, the primary button and the terminal cursor, and is the colour '
          "of errors. Never a large background, never body text, never decoration.</div>")
    ansi = "".join(f'<div style="height:54px;padding:5px 7px;font-size:10.5px;background:{c};color:{BG if i not in (0, 8) else TEXT}">'
                   f'{i} {ANSI_NAMES[i % 8]}<br>{c}</div>' for i, c in enumerate(ANSI["dark"]))
    syn = "".join(f'<tr><td>{k}</td><td><span class="chip" style="background:{d}"></span></td><td>{d}</td>'
                  f'<td><span class="chip" style="background:{l}"></span></td><td>{l}</td></tr>' for k, (d, l) in SYNTAX.items())
    s = {k: v[D] for k, v in SYNTAX.items()}
    code = (f'<span style="color:{s["comment"]}">// clear the province market; shortfall is rationed by queue</span><br>'
            f'<span style="color:{s["keyword"]}">pub fn</span> <span style="color:{s["function"]}">clear</span>(m: &amp;<span style="color:{s["keyword"]}">mut</span> '
            f'<span style="color:{s["type"]}">Market</span>, tol: <span style="color:{s["type"]}">f64</span>) -&gt; <span style="color:{s["type"]}">Price</span> {{<br>'
            f'&nbsp;&nbsp;&nbsp;&nbsp;m.<span style="color:{s["function"]}">tatonnement</span>(<span style="color:{s["number"]}">64</span>, tol, '
            f'<span style="color:{s["string"]}">"province"</span>)<br>}}')
    b.man(chapters[4], f'<div class="s" style="margin-top:0">ANSI 0-15</div><div class="i m">ANSI red is the error red, lifted for black ground.</div>'
          f'<div style="margin:10px 0 0 48px;display:grid;grid-template-columns:repeat(8,1fr);gap:3px">{ansi}</div>'
          f'<div class="s">SYNTAX</div><table style="margin:4px 0 0 48px;width:calc(100% - 48px)">{syn}</table>'
          f'<div class="s">EXAMPLE</div><div style="margin-left:48px;background:{UI["surface"][D]};padding:14px 20px">{code}</div>'
          '<div class="s">CLI</div><div class="i">Errors red, warnings brass, success sage, info slate, secondary text bright black. '
          "Respect NO_COLOR. In code, red stays out of text: cursor, search hits and errors only.</div>"
          f'<div class="s">FILES</div><div class="i" style="color:{UI["link"][D]}">themes/ghostty  themes/alacritty  themes/kitty  themes/wezterm<br>'
          'themes/windows-terminal  themes/vscode  themes/nvim</div>')

    # 06 Type
    b.chapter()
    spec = lambda font, size, text: f'<div style="font:{font};font-size:{size};line-height:1.15;color:{TEXT}">{text}</div>'  # noqa: E731
    b.man(chapters[5], '<div class="s" style="margin-top:0">FACES</div><div class="i m">All SIL Open Font License. Big Shoulders Display '
          "is inside the logo drawing and nowhere else.</div>"
          '<div class="s">Source Serif 4</div><div class="i">Display and long reading: headings, lab notes, the quote. 600 headings, 400 text.'
          f'<div style="margin-top:12px">{spec("600 1px \'Source Serif 4\'", "47px", "The shortfall is rationed by queue")}</div></div>'
          '<div class="s">IBM Plex Sans</div><div class="i">Interface: navigation, buttons, labels, short text. 400 and 500.'
          f'<div style="margin-top:12px">{spec("500 1px \'IBM Plex Sans\'", "37px", "Fork this run")}</div></div>'
          '<div class="s">IBM Plex Mono</div><div class="i">Code, terminal, data, seeds, hashes, versions. 400 and 500.'
          f'<div style="margin-top:12px">{spec("400 1px \'IBM Plex Mono\'", "27px", "seed 64 · 2000-01-01 → 2060-12-31")}</div></div>')
    scale = "".join(f'<tr><td style="width:60px">{k}</td><td style="width:90px" class="m">{float(v[:-3]) * 16:.1f} px</td>'
                    f'<td style="font:600 {v} \'Source Serif 4\';line-height:1.15;color:{TEXT}">Liquidity trap</td></tr>' for k, v in reversed(TYPE_SCALE.items()))
    b.man(chapters[5], f'<div class="s" style="margin-top:0">SCALE</div><div class="i m">16 px base, ratio 1.25. --as-size-*</div>'
          f'<table style="margin:10px 0 0 48px;width:calc(100% - 48px)">{scale}</table>'
          '<div class="s">SETTINGS</div><div class="i">Headings 1.15 line height. Interface 16/1.6. Lab notes may use Source Serif 18/1.6. Code 14 px.</div>'
          '<div class="s">RULES</div><div class="i">Sentence case. Numbers with their units. Seeds, versions, commands and paths always in '
          "Plex Mono. The logo is a drawing: never set ANIMAL SPIRITS in a font.</div>")

    # 07 Motion
    b.chapter()
    marks = [(STAMP, f"{STAMP} s, block"), (LETTER0 + 2 * LETTER_STEP, f"{LETTER0 + 2 * LETTER_STEP:.2f} s"),
             (LETTER0 + 8 * LETTER_STEP, f"{LETTER0 + 8 * LETTER_STEP:.2f} s"), (SETTLE, f"{SETTLE} s, set")]
    strip = "".join(f'<div><div style="background:{BG};padding:8px">{frame(t)}</div><div class="lab cap">{c}</div></div>' for t, c in marks)
    total = SETTLE
    ticks = "".join(f'<div style="position:absolute;left:{(LETTER0 + i * LETTER_STEP) / total * 100:.2f}%;top:24px;width:2px;height:16px;background:{INK}"></div>'
                    for i in range(13))
    stamp = f'<div style="position:absolute;left:{STAMP / total * 100:.2f}%;top:0;width:16px;height:16px;background:{RED}"></div>'
    b.paper(label(6), opener("07", chapters[6],
                             "The block is pressed first, all at once, like a print block on paper. Then ANIMAL SPIRITS is set letter by letter, "
                             "top line first. It plays once and holds. Nothing loops, nothing blinks.") +
            f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:40px">{strip}</div>'
            f'<h2>Timing</h2><div style="position:relative;height:44px;margin-top:8px">{stamp}{ticks}</div>'
            f'<div class="lab" style="display:flex;justify-content:space-between"><span>0 s</span><span>{total} s</span></div>'
            f'<p style="margin-top:16px">Block at {STAMP} s. Letters from {LETTER0} s, {LETTER_STEP * 1000:.0f} ms apart, all set by '
            f'{LETTER0 + 12 * LETTER_STEP:.2f} s. With reduced motion, the finished lockup appears at once.</p>'
            "<p>Interface motion: 150 to 200 ms, ease-out, no bounce, no parallax. CLI splash: a red block, then the name at 55 ms per "
            "letter, on first launch or <code>--version</code> only.</p>")

    # 08 Patterns and devices
    b.chapter()
    bd = f"outline:1px solid {UI['border'][L]};outline-offset:-1px"
    b.paper(label(7), opener("08", chapters[7], "Two grounds and a drawer of office devices. Patterns come from an economist's drawing or "
                             "from the market itself; devices mark status and never decorate.") +
            '<div class="grid2" style="margin-top:44px">'
            + panel("", BG, "Utility, quiet · patterns/utility-dark.svg", f"height:150px;background:url({uri('patterns/utility-dark.svg')}) center/cover")
            + panel("", PAPER, "Utility on paper · patterns/utility-light.svg", f"height:150px;background:url({uri('patterns/utility-light.svg')}) center/cover;{bd}")
            + '</div><div style="margin-top:12px">'
            + panel("", PAPER, "Crowd, loud: bowler hats in half-drop rows · patterns/crowd-tile-light.svg, repeated",
                    f"height:120px;background:url({uri('patterns/crowd-tile-light.svg')});background-size:66px auto;{bd}")
            + '</div><ul style="margin-top:24px">' + "".join(f"<li>{x}</li>" for x in [
                "Utility behind site sections, slides and the book, at 12 to 14 percent. Never behind body text.",
                "Crowd for merch, stickers, community posts and the 404 page. Never behind the logo.",
                "The ledger ruling stays for documents."]) + '</ul>')
    stamps = "".join(f'<div style="color:{RED if n in ("ex-post", "sourced") else INK}">{inline(f"devices/stamp-{n}.svg", "width:100%")}</div>'
                     for n in ("ceteris-paribus", "ex-ante", "ex-post", "seed", "re-run", "sourced"))
    b.paper(label(7), '<h2 style="margin-top:0">Devices</h2><p>Stamps are rectangular, in black, or in red when no block is on the page. '
            "They say what a figure is: assumed, measured, re-run, sourced.</p>"
            f'<div class="grid3" style="margin-top:20px;gap:18px 24px">{stamps}</div>'
            '<p style="margin-top:28px">Rationing by queue is the default when a market fails to clear.<sup class="fn">1</sup> '
            "Footnotes are numbered in red squares and carry sources, not argument.</p>"
            '<table class="led" style="margin-top:16px"><tr><th>Province</th><th>Demand</th><th>Supplied</th><th>Queued</th></tr>'
            '<tr><td>Lombardia</td><td>1,204</td><td>1,180</td><td>24</td></tr><tr><td>Bayern</td><td>1,410</td><td>1,347</td><td>63</td></tr>'
            '<tr class="tot"><td>Total</td><td>2,614</td><td>2,527</td><td>87</td></tr></table>'
            '<div class="lab cap">Ledger table, table.as-ledger in tokens/devices.css: tabular figures, a double rule under the total. Figures illustrative.</div>'
            f'<div style="background:{BG};padding:12px 14px;margin-top:22px;overflow:hidden">{img("devices/tape-dark.svg", "height:24px;width:auto;max-width:none")}</div>'
            '<div class="lab cap">Tape · devices/tape-dark.svg. In a game it is fed from the run journal; elsewhere its figures are labelled illustrative.</div>')

    # 09 Lexicon
    b.chapter()
    cards = sorted((ROOT / "social/lexicon").glob("*.png"))[:4]
    thumbs = "".join(img(str(c.relative_to(ROOT)), f"width:100%;{bd}") for c in cards)
    b.paper(label(8), opener("09", chapters[8], "A recurring series: one term, defined plainly, sourced, with an object from the cabinet. "
                             "Something to say between releases, in the studio's voice.") +
            f'<div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:36px">{thumbs}</div>'
            '<ul style="margin-top:24px">' + "".join(f"<li>{x}</li>" for x in [
                "Thirty entries in LEXICON.md, posted in order. Cards in social/lexicon/, 1080 by 1350.",
                "Each source is the first statement of the idea or the work that named it. Check one before adding an entry.",
                "Quotations only when exact; otherwise a plain paraphrase. Dry at most once per card."]) + '</ul>')

    # 10 Games
    b.chapter()
    stampline = (f'<div style="display:flex;align-items:center;gap:10px">{img("logo/favicon.svg", "width:22px")}'
                 '<span style="font:14px \'IBM Plex Mono\'">an animal spirits game</span></div>')
    b.paper(label(9), opener("10", chapters[9], "Ceteris, Metropole, Strata, Hohmann and Foundry each get their own name, colour and mark. "
                             "Animal Spirits appears on them only as a stamp.") +
            f'<div class="grid2" style="margin-top:44px">{panel(stampline, UI["surface"][L], "README, site and docs footers", "height:90px")}'
            f'{panel(img("logo/png/bar-on-dark.png", "width:200px"), BG, "Store pages and credits: the bar", "height:90px")}</div>'
            f'<div style="margin-top:24px;background:{BG};color:{TEXT};padding:20px 24px" class="mono">$ ceteris --version<br>ceteris 0.1.0 · an animal spirits game</div>'
            '<div class="lab cap">The --version line (version shown is an example)</div>'
            '<ul style="margin-top:28px">' + "".join(f"<li>{x}</li>" for x in [
                'Stamp: the favicon at 16 to 24 px, then "an animal spirits game" in Plex Mono, lowercase.',
                "On Steam, Animal Spirits is the developer and publisher. Capsules carry the game's own logo; the studio is in the credits and on its developer page.",
                "Games may share IBM Plex Mono and nothing else.",
                "Never spirit red, the block, Keynes, Big Shoulders or the ledger ruling as a game's identity."]) + '</ul>')

    # 11 Applications
    b.chapter()
    rows = "".join(f'<tr><td style="width:220px">{k}</td><td class="mono" style="font-size:13px">{v}</td></tr>' for k, v in [
        ("Site header", "logo/bar-on-dark.svg, 28 to 32 px tall"),
        ("Site hero, first visit", "motion/typeon.svg"),
        ("Lab notes, docs", "tokens/tokens.css, tokens/devices.css; code via Shiki with themes/vscode"),
        ("Lab note, post or release header", "cabinet/&lt;object&gt;-block.svg"),
        ("Lexicon posts", "social/lexicon/NN-term.png"),
        ("Merch, stickers, 404", "patterns/crowd-*.svg, cabinet/*.svg, devices/stamp-*.svg"),
        ("GitHub org avatar", "logo/png/avatar-512.png"),
        ("Org README", "social/readme-banner-dark.svg, -light.svg"),
        ("Repo social preview", "social/github-social-preview.png"),
        ("Link previews", "social/og-card.png"),
        ("Steam developer page", "logo/png/avatar-512.png, logo/png/lockup-on-dark.png"),
        ("Favicon", "logo/favicon.svg, favicon.ico, png/favicon-180.png"),
        ("Terminals, editors", "themes/")])
    b.paper(label(10), opener("11", chapters[10], "Each surface has its file. Use the file; do not rebuild the logo.") +
            f'<table style="margin-top:36px">{rows}</table>')
    b.paper(label(10), '<h2 style="margin-top:0">Surfaces</h2>'
            f'<div class="grid2" style="margin-top:20px;align-items:end"><div>{img("social/og-card.png", "width:100%")}<div class="lab cap">Link preview · social/og-card.png</div></div>'
            f'<div>{img("social/readme-banner-light.svg", "width:100%")}<div class="lab cap">Org README · social/readme-banner-light.svg</div></div></div>'
            f'<div class="grid3" style="margin-top:28px;align-items:stretch">{img("cabinet/globe-block.svg", "width:100%")}{img("social/lexicon/03-the-long-run.png", "width:100%")}'
            f'<div style="background:url({uri("patterns/crowd-tile-light.svg")});background-size:50px auto;display:grid;place-items:center">'
            f'<div style="background:{PAPER};padding:12px;width:74%">{inline("devices/stamp-ceteris-paribus.svg", f"width:100%;color:{RED}")}</div></div></div>'
            '<div class="lab cap">Lab note header · lexicon post · sticker on the Crowd</div>')

    # Back cover
    b.raw(f'<section class="pg" style="background:{BG};color:{TEXT}">'
          f'<div style="position:absolute;left:76px;top:76px">{img("logo/favicon.svg", "width:64px")}</div>'
          f'<div style="position:absolute;left:76px;right:76px;bottom:64px;font:12px/1.7 \'IBM Plex Mono\';color:{UI["text-muted"][D]}">'
          f"Generated by scripts/book.py from animal-spirits/brand {VERSION}.<br>Code, tokens and themes: MIT. Logos and the name Animal "
          "Spirits are trademarks; see TRADEMARK.md.<br>Set in Source Serif 4, IBM Plex Sans and IBM Plex Mono; logo drawn from Big Shoulders "
          "Display. SIL Open Font License.</div></section>")
    toc = "".join(f'<tr><td class="lab" style="width:48px">{i + 1:02}</td><td style="font:600 22px \'Source Serif 4\'">{c}</td>'
                  f'<td class="lab" style="text-align:right">{p:02}</td></tr>' for i, (c, p) in enumerate(zip(chapters, b.starts)))
    b.paper("contents", '<h1>Contents</h1><p style="margin-top:22px">Animal Spirits is an open-source studio for simulation games: '
            "Ceteris, Metropole, Strata, Hohmann and Foundry. This book sets out how the studio looks and sounds. Every logo, colour and "
            "theme in it is generated by <code>animal-spirits/brand</code>; if this book and the repository disagree, the repository is right.</p>"
            f'<table style="margin-top:56px">{toc}</table>', at=2)
    return "".join(b.pages)


def misuse() -> str:
    logo = img("logo/lockup-on-light.svg", "width:150px")
    cases = [("No: stretch", f'<div style="transform:scaleX(1.35)">{logo}</div>'),
             ("No: flip", f'<div style="transform:scaleX(-1)">{logo}</div>'),
             ("No: recolour", f'<div style="filter:hue-rotate(160deg)">{logo}</div>'),
             ("No: add effects", f'<div style="filter:drop-shadow(4px 4px 0 {UI["border"][L]})">{logo}</div>'),
             ("No: set in a font", '<div style="font:600 30px \'Source Serif 4\'">Animal Spirits</div>'),
             ("No: busy ground", f'<div style="padding:10px;{STRIPES}">{logo}</div>')]
    return '<div class="grid3">' + "".join(panel(c, UI["surface"][L], n, "height:130px;overflow:hidden;padding:12px") for n, c in cases) + "</div>"


FONTS = ("https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400"
         "&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400;500&display=swap")


async def main() -> None:
    (ROOT / "book").mkdir(exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=os.environ.get("CHROMIUM"))
        page = await browser.new_page()
        html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Animal Spirits brand identity</title>'
                f'<link rel="stylesheet" href="{FONTS}"><style>{CSS}</style></head><body>{build()}</body></html>')
        await page.set_content(html, wait_until="networkidle")
        await page.evaluate("document.fonts.ready")
        await page.pdf(path=str(ROOT / "book/animal-spirits-brand-book.pdf"), width="210mm", height="297mm", print_background=True,
                       prefer_css_page_size=True)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
