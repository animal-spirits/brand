"""The studio site: one self-contained page built from the tokens, the woodcuts, the cabinet and the lexicon, opened by
the ident. Run after build and cabinet: uv run scripts/site.py. Writes site/index.html (whole document) and
site/body.html (the same page without the document shell, for hosts that supply one), and the Ceteris Paribus page
site/ceteris.html, which wears the game's identity (logo kit tokens, carved wordmark in site/ceteris/) under the studio
header. Its "to come" sections are filled as the game nears release."""
import json
import re
import tomllib
from pathlib import Path

from animal_spirits_brand import ident, logos
from animal_spirits_brand.cabinet import CAPTIONS
from animal_spirits_brand.palette import UI

ROOT = Path(__file__).resolve().parents[1]
LEXICON = tomllib.loads((ROOT / "src/animal_spirits_brand/data/lexicon.toml").read_text())["entry"]
FONTS = ("https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400"
         "&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400;500&display=swap")

GAMES = [  # name, subject, span, status; Ceteris has its own page
    ("Ceteris Paribus", "The world economy and its trade, agent by agent, from published data.", "2000 onward", "in development"),
    ("Metropole", "A serious city builder.", "present day", "planned"),
    ("Strata", "An emergent civilisation, from the first fields to the first mills.", "Neolithic to c. 1800", "working title"),
    ("Hohmann", "Hard-science colonisation of the solar system.", "near future", "working title"),
    ("Foundry", "A factory inside a living economy.", "industrial", "planned"),
]
WOODCUTS = [  # group, layout, [(woodcut, label, gloss)]; the first of a 3-column group spans two by two
    ("The market", 3, [
        ("bull", "the bull", "a buyer who expects prices to rise"),
        ("bear", "the bear", "a seller who expects them to fall"),
        ("hawk", "the hawk", "a central banker for higher rates"),
        ("dove", "the dove", "a central banker for lower rates"),
        ("black-swan", "the black swan", "the event outside the model"),
        ("lame-duck", "the lame duck", "a broker who cannot settle his debts"),
    ]),
    ("The state", 2, [
        ("the-assembly", "the assembly", "power that is counted"),
        ("the-city", "the City", "the Royal Exchange under St Paul's"),
        ("the-seal", "the seal", "power that is decreed"),
        ("hand", "the invisible hand", "the market setting a price"),
    ]),
    ("Production and trade", 3, [
        ("steelworks", "the steelworks", "capital, coal and iron"),
        ("anvil", "the anvil", "work on material"),
        ("steam-engine", "the engine", "a governor keeps it steady"),
        ("machine-hall", "the machine hall", "the division of labour"),
        ("beehive", "the hive", "private vices, public benefits"),
        ("ship", "the ship", "comparative advantage at sea"),
    ]),
]


def svg(rel: str, cls: str = "", label: str | None = None) -> str:
    s = (ROOT / rel).read_text().strip()
    s = re.sub(r'^<svg xmlns="http://www.w3.org/2000/svg"', "<svg", s)
    s = re.sub(r' width="\d+" height="\d+"', "", s, count=1)
    if cls:
        s = s.replace("<svg", f'<svg class="{cls}"', 1)
    if label is not None:
        s = re.sub(r' aria-label="[^"]*"', f' aria-label="{label}"', s, count=1)
    return s


def lexicon_card(e: dict, n: int) -> str:
    return (f'<article class="lex"><div class="lex-top mono"><span>lexicon {n:02}</span><span>{e["pos"]}</span></div>'
            f'<div class="lex-obj">{svg(f"cabinet/{e["object"]}.svg", label="")}</div>'
            f'<h3>{e["term"]}</h3><p>{e["text"]}</p><div class="lex-src mono">{e["source"]}</div></article>')


def page() -> tuple[str, str]:
    ident_css, ident_html = ident.parts()
    v = logos.Version("currentColor", UI["accent"][0], UI["on-accent"][0])
    bar = re.sub(r' width="\d+" height="\d+"', "", logos.bar(v).replace('xmlns="http://www.w3.org/2000/svg" ', ""), count=1)
    stamp_mark = svg("logo/favicon.svg", "stampmark", "")
    tape = svg("devices/tape-dark.svg", "tape-svg", "").replace('fill="#A39A8E"', 'fill="currentColor"')

    games = "".join(
        f'<article class="game"><div class="g-top mono"><span>{p}</span><span class="st-{st.split()[0]}">{st}</span></div><h3>{n}</h3><p>{s}</p>'
        + ('<a class="g-more mono" href="ceteris.html">read more</a>' if n.startswith("Ceteris") else '<span class="g-more mono">later</span>')
        + "</article>" for n, s, p, st in GAMES)
    beasts = "".join(f'<h3 class="wc-h">{h}</h3><div class="bestiary c{n}">' + "".join(
        f'<figure class="beast">{svg(f"woodcuts/{w}-cut-1-block.svg", label=l)}<figcaption><b>{l}</b> {g}</figcaption></figure>'
        for w, l, g in items) + "</div>" for h, n, items in WOODCUTS)
    cabinet = "".join(f'<figure>{svg(f"cabinet/{k}.svg", label=c)}<figcaption class="mono">{k}<span>{c}</span></figcaption></figure>'
                      for k, c in CAPTIONS.items())
    lex = "".join(lexicon_card(e, i + 1) for i, e in enumerate(LEXICON[:3]))

    css = (ROOT / "tokens/tokens.css").read_text() + (ROOT / "tokens/devices.css").read_text().split(".as-utility")[0] + ident_css + """
/* Layout: a ledger page. A narrow account column of mono labels on the left, the entries on the right, ruled across. */
body{background:var(--as-bg);color:var(--as-text);font:400 1rem/1.6 var(--as-font-text);margin:0}
.wrap{max-width:1180px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.mono{font-family:var(--as-font-mono)}
a{color:var(--as-link)} a:focus-visible,button:focus-visible{outline:2px solid var(--as-accent-text);outline-offset:3px}
::selection{background:var(--as-selection)}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--as-bg)}
header.top{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--as-bg);border-bottom:1px solid var(--as-border)}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;padding-block:14px}
header.top svg{height:26px;width:auto;display:block;color:var(--as-text)}
header.top nav{display:flex;gap:20px;font:500 .8rem var(--as-font-mono);letter-spacing:.04em}
header.top nav a{color:var(--as-text-muted);text-decoration:none} header.top nav a:hover{color:var(--as-text)}
.hero .wrap{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);gap:56px;align-items:center;padding-block:64px 56px}
.hero h1{font:600 clamp(2.2rem,4.6vw,3.6rem)/1.05 var(--as-font-display);letter-spacing:-.015em;margin:0;text-wrap:balance}
.hero p.lede{font:400 1.2rem/1.55 var(--as-font-display);margin:24px 0 0;max-width:34ch;color:var(--as-text)}
.hero blockquote{margin:36px 0 0;padding:16px 0 0;border-top:2px solid var(--as-text);max-width:46ch;font:italic 400 1.05rem/1.55 var(--as-font-display);color:var(--as-text-muted)}
.hero blockquote cite{display:block;margin-top:10px;font:400 .75rem/1.4 var(--as-font-mono);font-style:normal}
.hero .cut{margin:0;max-width:100%}
.hero .cut svg{display:block;width:100%;height:auto}
.hero .cut figcaption,.beast figcaption,.cab figcaption{font:400 .75rem/1.45 var(--as-font-mono);color:var(--as-text-muted);margin-top:10px}
.tape{border-block:1px solid var(--as-border);color:var(--as-text-muted);overflow:hidden;height:32px}
.tape-run{display:flex;width:max-content;animation:tape 60s linear infinite}
.tape-svg{height:32px;width:auto;display:block;flex:none}
@keyframes tape{to{transform:translateX(-50%)}}
section.acct .wrap{display:grid;grid-template-columns:160px minmax(0,1fr);gap:40px;padding-block:72px;border-bottom:1px solid var(--as-border)}
section.acct .label{font:500 .75rem/1.4 var(--as-font-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--as-text-muted);padding-top:.5rem}
section.acct .label b{display:block;color:var(--as-accent-text);font-weight:500;margin-bottom:4px}
h2{font:600 var(--as-size-3xl)/1.1 var(--as-font-display);letter-spacing:-.01em;margin:0 0 12px;text-wrap:balance}
.intro{max-width:60ch;color:var(--as-text-muted);margin:0 0 36px}
.tbl{overflow-x:auto}
table.as-ledger{font-size:.875rem}
table.as-ledger td{vertical-align:top}
table.as-ledger.txt td:not(:first-child){text-align:left}
.games{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:20px}
@media (max-width:900px){.games{grid-template-columns:repeat(2,minmax(0,1fr))}}
.game{border-top:2px solid var(--as-text);padding-top:12px;display:flex;flex-direction:column;min-width:0}
.g-top{display:flex;flex-direction:column;font-size:.72rem;line-height:1.5;color:var(--as-text-muted)} .st-in{color:var(--as-accent-text)}
.game h3{font:600 1.35rem/1.15 var(--as-font-display);margin:10px 0 6px} .game p{margin:0 0 14px;color:var(--as-text-muted);font-size:.92rem}
.g-more{margin-top:auto;font-size:.75rem;color:var(--as-text-muted)} a.g-more{color:var(--as-link)}
.bestiary{display:grid;gap:28px 24px} .c3{grid-template-columns:repeat(3,minmax(0,1fr))} .c2{grid-template-columns:repeat(2,minmax(0,1fr))}
.wc-h{font:500 .75rem/1 var(--as-font-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--as-text-muted);margin:44px 0 16px;padding-top:12px;border-top:1px solid var(--as-border)}
.wc-h:first-of-type{margin-top:0}
.beast{margin:0} .beast svg{display:block;width:100%;height:auto}
.c3 .beast:first-child{grid-column:span 2;grid-row:span 2}
.beast figcaption b{font-weight:500;color:var(--as-text)}
.cab{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px 24px;color:var(--as-text)}
.cab figure{margin:0;border-top:1px solid var(--as-border);padding-top:12px}
.cab svg{display:block;width:100%;height:auto;aspect-ratio:1}
.cab figcaption{display:flex;justify-content:space-between;gap:8px}
.cab figcaption span{color:var(--as-text)}
.lexgrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}
.lex{background:var(--as-surface);padding:22px 22px 20px;display:flex;flex-direction:column;min-width:0}
.lex-top{display:flex;justify-content:space-between;font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--as-text-muted)}
.lex-obj{width:56%;margin:18px auto 8px;color:var(--as-text)} .lex-obj svg{display:block;width:100%;height:auto}
.lex h3{font:600 1.6rem/1.1 var(--as-font-display);margin:auto 0 0;letter-spacing:-.01em}
.lex p{font:400 1.05rem/1.45 var(--as-font-display);margin:10px 0 0}
.lex-src{margin-top:18px;padding-top:10px;border-top:2px solid var(--as-text);font-size:.72rem;line-height:1.45;color:var(--as-text-muted)}
.lexbar{display:flex;align-items:center;gap:16px;margin-top:20px;font:.8rem var(--as-font-mono);color:var(--as-text-muted)}
button.more{font:500 .8rem var(--as-font-mono);letter-spacing:.04em;color:var(--as-on-accent);background:var(--as-accent);border:0;padding:10px 14px;cursor:pointer}
button.more:hover{filter:brightness(1.1)}
.note{display:grid;grid-template-columns:minmax(0,1fr) 260px;gap:40px;align-items:start}
.note-head{display:flex;gap:20px;align-items:flex-start}
.note-head svg.thumb{width:96px;height:96px;flex:none}
.note h3{font:600 var(--as-size-2xl)/1.15 var(--as-font-display);margin:4px 0 0;text-wrap:balance}
.note .meta{font:400 .75rem var(--as-font-mono);color:var(--as-text-muted)}
.note-body{max-width:64ch} .note-body p{margin:16px 0}
.stamps{display:flex;flex-direction:column;gap:8px}
.stamps svg{width:200px;height:auto;display:block}
.example{display:inline-block;font:500 .7rem var(--as-font-mono);letter-spacing:.06em;text-transform:uppercase;border:1px solid var(--as-border);color:var(--as-text-muted);padding:2px 6px;margin-bottom:14px}
footer .wrap{display:flex;flex-wrap:wrap;justify-content:space-between;gap:24px;padding-block:40px 56px;font:400 .8rem var(--as-font-mono);color:var(--as-text-muted)}
footer .line{display:flex;align-items:center;gap:10px;color:var(--as-text)}
.stampmark{width:20px;height:20px}
#ident{position:fixed;inset:0;z-index:20;background:var(--as-bg);cursor:pointer;transition:opacity .2s}
#ident.gone{opacity:0;pointer-events:none}
#ident .skip{position:absolute;right:max(20px,env(safe-area-inset-right,0px));bottom:calc(20px + env(safe-area-inset-bottom,0px));font:500 .75rem var(--as-font-mono);
  letter-spacing:.06em;color:var(--as-text-muted);background:none;border:1px solid var(--as-border);padding:8px 12px;cursor:pointer;z-index:1}
/* the ident is dark in both themes */
#ident{background:#161110} #ident .skip{color:#A39A8E;border-color:#463D38}
@media (max-width:860px){
 .hero .wrap{grid-template-columns:minmax(0,1fr);gap:36px;padding-block:40px}
 section.acct .wrap{grid-template-columns:minmax(0,1fr);gap:16px;padding-block:52px}
 .lexgrid{grid-template-columns:minmax(0,1fr)} .note{grid-template-columns:minmax(0,1fr)} .cab{grid-template-columns:repeat(2,minmax(0,1fr))}
 .stamps{flex-direction:row;flex-wrap:wrap} .stamps svg{width:150px}
 header.top nav{display:none}
}
@media (max-width:560px){ .c3,.c2{grid-template-columns:repeat(2,minmax(0,1fr))} .c3 .beast:first-child{grid-row:auto} }
@media (prefers-reduced-motion:reduce){ .tape-run{animation:none} #ident{display:none} }
"""
    body = f"""
<div id="ident" aria-hidden="true">{ident_html}<button class="skip" type="button">skip</button></div>
<header class="top"><div class="wrap"><a href="#top" aria-label="Animal Spirits, top">{bar}</a>
<nav aria-label="Sections"><a href="#games">games</a><a href="#bestiary">woodcuts</a><a href="#cabinet">cabinet</a><a href="#lexicon">lexicon</a><a href="#notes">lab notes</a></nav></div></header>
<main id="top">
<section class="hero"><div class="wrap">
<div><h1>Simulation games built from published data and cited models.</h1>
<p class="lede">Animal Spirits is one person making open-source games that take economics too seriously. Every number has a source. Every run can be repeated.</p>
<blockquote>Most, probably, of our decisions to do something positive, the full consequences of which will be drawn out over many days to come, can only be taken as the result of animal spirits.<sup class="as-fn">1</sup>
<cite>1. J. M. Keynes, The General Theory of Employment, Interest and Money, 1936, chapter 12</cite></blockquote></div>
<figure class="cut">{svg("woodcuts/the-floor-cut-1-block.svg", label="Woodcut: a trading floor")}<figcaption>the floor, woodcut, cut 1</figcaption></figure>
</div></section>
<div class="tape" aria-hidden="true"><div class="tape-run">{tape}{tape}</div></div>

<section class="acct" id="games"><div class="wrap"><div class="label"><b>01</b>games</div><div>
<h2>Five games, one studio</h2><p class="intro">Economies, cities, civilisations, colonies and factories, each with its own name and look. Animal Spirits appears on them only as a stamp. All open source.</p>
<div class="games">{games}</div></div></div></section>

<section class="acct" id="bestiary"><div class="wrap"><div class="label"><b>02</b>woodcuts</div><div>
<h2>The woodcuts</h2><p class="intro">Cut in one ink on spirit red, in the hand of the Keynes block. Animals and objects come in three cuts, from full detail down to a favicon; scenes are drawn large only.</p>
<div class="bestiary">{beasts}</div></div></div></section>

<section class="acct" id="cabinet"><div class="wrap"><div class="label"><b>03</b>cabinet</div><div>
<h2>The cabinet</h2><p class="intro">Eight objects from an economist's desk, cut in one ink like the woodcuts. They head lab notes, posts and lexicon cards.</p>
<div class="cab">{cabinet}</div></div></div></section>

<section class="acct" id="lexicon"><div class="wrap"><div class="label"><b>04</b>lexicon</div><div>
<h2>The lexicon</h2><p class="intro">Thirty terms, one a week. Plain definitions; the source is where the idea was first stated or named.</p>
<div class="lexgrid" id="lexgrid">{lex}</div>
<div class="lexbar"><button class="more" type="button" id="more">next three</button><span id="lexpos">1 to 3 of {len(LEXICON)}</span></div></div></div></section>

<section class="acct" id="notes"><div class="wrap"><div class="label"><b>05</b>lab notes</div><div>
<span class="example">example layout</span>
<article class="note"><div><div class="note-head">{svg("cabinet/ledger-block.svg", "thumb", "")}<div>
<div class="meta">lab note · studio</div><h3>Every number has a source</h3></div></div>
<div class="note-body"><p>Each game starts from published data: national accounts, trade statistics, censuses, survey maps. Every constant in the code points to the table or paper it came from, and the source list ships with the game.<sup class="as-fn">1</sup></p>
<p>The same seed and the same sources give the same world, bit for bit. Change one thing and run it again: that is the whole method.<sup class="as-fn">2</sup></p>
<div class="tbl"><table class="as-ledger txt"><thead><tr><th>rule</th><th>checked by</th><th>when</th></tr></thead><tbody>
<tr><td>every input is cited</td><td>source manifest</td><td>every build</td></tr>
<tr><td>same seed, same world</td><td>state hash</td><td>every test run</td></tr></tbody>
<tfoot><tr><td>rules</td><td></td><td>2</td></tr></tfoot></table></div>
<aside class="as-note" style="margin-top:20px">1. Licences are checked per source; anything not redistributable stays out. 2. Hashes are compared across runs and thread counts.</aside></div></div>
<div class="stamps">{svg("devices/stamp-ceteris-paribus.svg", label="ceteris paribus")}{svg("devices/stamp-seed.svg", label="seed")}{svg("devices/stamp-sourced.svg", label="sourced")}</div></article>
</div></div></section>
</main>
<footer><div class="wrap"><span class="line">{stamp_mark}Animal Spirits</span><span>github.com/animal-spirits</span><span>code MIT · name, marks and woodcuts are trademarks</span></div></footer>
<script>
(() => {{
  const ov = document.getElementById('ident');
  const fit = () => ov.style.setProperty('--k', Math.min(innerWidth / 1920, innerHeight / 1080));
  const done = () => {{ ov.classList.add('gone'); setTimeout(() => ov.remove(), 250); }};
  let seen = false;
  try {{ seen = sessionStorage.getItem('as-ident') === '1'; sessionStorage.setItem('as-ident', '1'); }} catch (e) {{}}
  if (seen || matchMedia('(prefers-reduced-motion: reduce)').matches) ov.remove();
  else {{
    fit(); addEventListener('resize', fit);
    for (const ev of ['click', 'keydown', 'wheel', 'touchstart']) addEventListener(ev, done, {{once: true, passive: true}});
    setTimeout(done, {ident.END * 1000:.0f});
  }}
  const L = {json.dumps(LEXICON, ensure_ascii=False)};
  const OBJ = {json.dumps({k: svg(f"cabinet/{k}.svg", label="") for k in CAPTIONS})};
  let at = 0;
  const card = (e, n) => `<article class="lex"><div class="lex-top mono"><span>lexicon ${{String(n).padStart(2, '0')}}</span><span>${{e.pos}}</span></div>`
    + `<div class="lex-obj">${{OBJ[e.object]}}</div><h3>${{e.term}}</h3><p>${{e.text}}</p><div class="lex-src mono">${{e.source}}</div></article>`;
  document.getElementById('more').addEventListener('click', () => {{
    at = (at + 3) % L.length;
    document.getElementById('lexgrid').innerHTML = L.slice(at, at + 3).map((e, i) => card(e, at + i + 1)).join('');
    document.getElementById('lexpos').textContent = `${{at + 1}} to ${{at + 3}} of ${{L.length}}`;
  }});
}})();
</script>"""
    head = f'<title>Animal Spirits</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<link rel="stylesheet" href="{FONTS}">\n<style>{css}</style>\n'
    return head, body


CETERIS_FACTS = [  # label, value
    ("starts", "1 January 2000"),
    ("world", "every country, its firms, households and governments as agents"),
    ("data", "BACI bilateral trade (CEPII), OECD input-output tables, national accounts"),
    ("runs", "deterministic: same seed and sources, same world, bit for bit"),
    ("forks", "change one thing at any date and run both worlds side by side"),
    ("platform", "desktop app"),
    ("licence", "open source"),
    ("status", "in development"),
]
CETERIS_LATER = [  # heading, what goes there
    ("Screenshots", "The map, the ledger views and a forked run, once the interface is settled."),
    ("Devlog", "Lab notes from the build: what each model does and the paper it comes from."),
    ("System requirements", "Measured on the release build, not estimated."),
    ("Release", "Date, price and where to get it."),
]


def ceteris_page() -> str:
    """The game's own page: Ceteris tokens (logo kit, day and night), carved wordmark at 400 px and up, flat below."""
    v = logos.Version("currentColor", UI["accent"][0], UI["on-accent"][0])
    bar = re.sub(r' width="\d+" height="\d+"', "", logos.bar(v).replace('xmlns="http://www.w3.org/2000/svg" ', ""), count=1)
    flat = (ROOT / "site/ceteris/wordmark.svg").read_text().replace("<svg ", '<svg class="flat" role="img" aria-label="Ceteris Paribus" ', 1)
    facts = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in CETERIS_FACTS)
    later = "".join(f'<section class="later"><div class="mono tag">to come</div><h2>{h}</h2><p>{t}</p></section>' for h, t in CETERIS_LATER)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Ceteris Paribus</title><link rel="stylesheet" href="{FONTS}">
<style>
:root{{--bg:#11171B;--panel:#182026;--line:#36424A;--ink:#E2E7E3;--ink2:#A2B0AE;--accent:#D48A8D;
--sans:"IBM Plex Sans",system-ui,sans-serif;--mono:"IBM Plex Mono",ui-monospace,monospace;--serif:"Source Serif 4",Georgia,serif;color-scheme:dark}}
@media (prefers-color-scheme:light){{:root:not([data-theme="dark"]){{--bg:#EEF1EC;--panel:#F7F8F5;--line:#C9D0CB;--ink:#1C292F;--ink2:#4E5E64;--accent:#C2306B;color-scheme:light}}}}
:root[data-theme="light"]{{--bg:#EEF1EC;--panel:#F7F8F5;--line:#C9D0CB;--ink:#1C292F;--ink2:#4E5E64;--accent:#C2306B;color-scheme:light}}
body{{margin:0;background:var(--bg);color:var(--ink);font:400 1rem/1.6 var(--sans)}}
.wrap{{max-width:1040px;margin:0 auto;padding-inline:max(16px,env(safe-area-inset-left,0px)) max(16px,env(safe-area-inset-right,0px))}}
.mono{{font-family:var(--mono)}} a{{color:var(--ink)}} a:focus-visible{{outline:2px solid var(--accent);outline-offset:3px}}
header{{border-bottom:1px solid var(--line)}} header .wrap{{display:flex;align-items:center;justify-content:space-between;gap:16px;padding-block:12px}}
header svg{{height:22px;width:auto;display:block;color:var(--ink)}} header a.back{{font:500 .78rem var(--mono);color:var(--ink2);text-decoration:none}}
.slab{{margin:48px 0 0;border:1px solid var(--line);border-radius:4px;overflow:hidden;background:var(--panel)}}
.slab img{{display:block;width:100%;height:auto}} .slab .night{{display:none}} .slab .flat{{display:none;width:100%;height:auto;color:var(--ink);padding:28px 18px;box-sizing:border-box}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]) .slab .day{{display:none}} :root:not([data-theme="light"]) .slab .night{{display:block}}}}
:root[data-theme="dark"] .slab .day{{display:none}} :root[data-theme="dark"] .slab .night{{display:block}}
@media (max-width:440px){{.slab img{{display:none!important}} .slab .flat{{display:block}} .facts th{{width:5.5rem}}}}
.lede{{font:400 clamp(1.25rem,2.4vw,1.6rem)/1.4 var(--serif);max-width:38em;margin:36px 0 8px;text-wrap:pretty}}
.sub{{color:var(--ink2);max-width:40em;margin:0}}
h2{{font:600 1.05rem var(--sans);margin:0 0 8px}}
.facts{{margin-top:48px;border-top:2px solid var(--ink)}}
.facts table{{width:100%;border-collapse:collapse}} .facts th,.facts td{{text-align:left;vertical-align:top;padding:10px 0;border-bottom:1px solid var(--line)}}
.facts th{{font:500 .75rem/1.9 var(--mono);color:var(--ink2);width:8.5rem;padding-right:16px;letter-spacing:.04em}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px;margin:48px 0 64px}}
.later{{border:1px dashed var(--line);border-radius:4px;padding:16px 18px;background:var(--panel)}}
.later .tag{{font-size:.7rem;color:var(--accent);letter-spacing:.06em;margin-bottom:6px}} .later p{{margin:0;color:var(--ink2);font-size:.92rem}}
footer{{border-top:1px solid var(--line)}} footer .wrap{{display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px 24px;padding-block:20px;font:400 .75rem var(--mono);color:var(--ink2)}}
</style></head><body>
<header><div class="wrap"><a href="index.html" aria-label="Animal Spirits, studio home">{bar}</a><a class="back" href="index.html#games">all games</a></div></header>
<main class="wrap">
<div class="slab"><img class="day" src="ceteris/carved-day.webp" width="1600" height="260" alt="Ceteris Paribus">
<img class="night" src="ceteris/carved-night.webp" width="1600" height="260" alt="Ceteris Paribus">{flat}</div>
<p class="lede">A world economy simulator. Every country, firm and household from 1 January 2000, built from published trade and national accounts, run forward one day at a time.</p>
<p class="sub">Fork the world at any date, change one thing, and watch both worlds diverge. Other things equal, until they are not.</p>
<div class="facts"><table>{facts}</table></div>
<div class="grid">{later}</div>
</main>
<footer><div class="wrap"><span>an Animal Spirits game</span><span>github.com/animal-spirits</span></div></footer>
</body></html>
"""


def main() -> None:
    head, body = page()
    out = ROOT / "site"
    out.mkdir(exist_ok=True)
    (out / "body.html").write_text(head + body)
    (out / "index.html").write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
                                    f'<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">{head}</head><body>{body}</body></html>\n')
    (out / "ceteris.html").write_text(ceteris_page())
    print(f"wrote site/index.html ({(out / 'index.html').stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
