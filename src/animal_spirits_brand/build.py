"""Write every brand file from the drawing code and the palette. Run: uv run animal-spirits-brand

The token, terminal and editor theme writers follow zaofang/brand (MIT)."""
import json
from pathlib import Path

from . import logos, portrait, wordmark
from .logos import CAP, GAP, LEADING, MONO, TILE, version
from .palette import ANSI, ANSI_NAMES, FONTS, SYNTAX, TERMINAL, TYPE_SCALE, UI

ROOT = Path(__file__).resolve().parents[2]
DARK = version({k: v[0] for k, v in UI.items()})
LIGHT = version({k: v[1] for k, v in UI.items()})
NAME = "Animal Spirits Ledger"


def write(rel: str, text: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


# Logos -----------------------------------------------------------------------------------------------
def build_logos() -> None:
    for name, fn in {"lockup": logos.lockup, "bar": logos.bar, "wordmark": logos.word, "stacked": logos.stacked}.items():
        write(f"logo/{name}-on-dark.svg", fn(DARK))
        write(f"logo/{name}-on-light.svg", fn(LIGHT))
        write(f"logo/{name}-mono.svg", fn(MONO))
    for n in (1, 2, 3):
        write(f"logo/mark-cut-{n}.svg", logos.mark(DARK, n))
        write(f"logo/mark-cut-{n}-mono.svg", logos.mark(MONO, n))
    write("logo/avatar.svg", logos.avatar(DARK, UI["bg"][0]))
    write("logo/avatar-light.svg", logos.avatar(LIGHT, UI["bg"][1]))
    write("logo/favicon.svg", logos.favicon(DARK))


def ruling(fid: str, colour: str, step: int = 24, opacity: float = .10) -> tuple[str, str]:
    """Ledger ruling: one hairline every 24 px."""
    defs = (f'<pattern id="{fid}" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
            f'<rect y="{step - 1}" width="{step}" height="1" fill="{colour}" fill-opacity="{opacity}"/></pattern>')
    return defs, f'<rect width="100%" height="100%" fill="url(#{fid})"/>'


def _inner(svg: str) -> tuple[list[float], str]:
    vb = [float(v) for v in svg.split('viewBox="')[1].split('"')[0].split()]
    return vb, svg.split("</title>", 1)[1].rsplit("</svg>", 1)[0]


def banner(mode: int, w: int = 1280, h: int = 320, logo_w: float = 520) -> str:
    """README banner: the lockup centred on the ground, over ledger ruling."""
    vb, inner = _inner(logos.lockup(DARK if mode == 0 else LIGHT))
    s = logo_w / vb[2]
    tx, ty = (w - logo_w) / 2 - vb[0] * s, (h - vb[3] * s) / 2 - vb[1] * s
    defs, lines = ruling("r", UI["text"][mode])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Animal Spirits">'
            f'<title>Animal Spirits</title><defs>{defs}</defs><rect width="100%" height="100%" fill="{UI["bg"][mode]}"/>{lines}'
            f'<g transform="translate({tx:.2f} {ty:.2f}) scale({s:.4f})">{inner}</g></svg>\n')


def build_banners() -> None:
    write("social/readme-banner-dark.svg", banner(0))
    write("social/readme-banner-light.svg", banner(1))


# Motion ----------------------------------------------------------------------------------------------
STAMP = .30                       # the block lands, all at once, like a print block on paper
LETTER0, LETTER_STEP = .62, .055  # then the letters, left to right, top line first
SETTLE = 1.6                      # the whole composition holds from here; nothing loops


def typeon_svg() -> str:
    """The block is pressed, then ANIMAL SPIRITS sets letter by letter. No loop, no blink."""
    x = TILE + GAP
    a, ra = wordmark.glyphs("ANIMAL", x, CAP)
    s, rs = wordmark.glyphs("SPIRITS", x, 2 * CAP + LEADING)
    parts = a + s
    times = [LETTER0 + i * LETTER_STEP for i in range(len(parts))]
    css = ("@keyframes show{from{opacity:0}to{opacity:1}}"
           f".b{{animation:show 0s {STAMP}s both}}.l{{opacity:0}}"
           + "".join(f".l{i}{{animation:show 0s {t:.3f}s both}}" for i, t in enumerate(times))
           + "@media (prefers-reduced-motion:reduce){.b,.l{animation:none;opacity:1}}")
    k = TILE / portrait.SIZE
    block = (f'<g class="b"><rect width="{TILE:g}" height="{TILE:g}" fill="{UI["accent"][0]}"/>'
             f'<path transform="scale({k:.5f})" fill="{UI["on-accent"][0]}" fill-rule="evenodd" d="{portrait.cut(1)}"/></g>')
    letters = "".join(f'<path class="l l{i}" fill="{UI["text"][0]}" d="{d}"/>' for i, d in enumerate(parts))
    m, W, H = 16, max(ra, rs), TILE
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-m} {-m} {W + 2 * m:.2f} {H + 2 * m:.2f}" width="{(W + 2 * m) * 2:.0f}" '
            f'height="{(H + 2 * m) * 2:.0f}" role="img" aria-label="Animal Spirits"><title>Animal Spirits</title><style>{css}</style>'
            f'<rect x="{-m}" y="{-m}" width="{W + 2 * m:.2f}" height="{H + 2 * m:.2f}" fill="{UI["bg"][0]}"/>{block}{letters}</svg>\n')


SPLASH = r"""#!/bin/sh
# Animal Spirits CLI splash: a red block, then the name set letter by letter. Shown on first launch or --version only.
# Truecolor escapes; terminals without truecolor show the nearest colour. Respects NO_COLOR.
if [ -n "$NO_COLOR" ]; then printf 'animal spirits\n'; exit 0; fi
ink='\033[38;2;236;230;216m'; red='\033[38;2;195;43;31m'; reset='\033[0m'
printf '\033[?25l'
printf "${red}\342\226\210\342\226\210${reset} "
sleep 0.3
for ch in a n i m a l ' ' s p i r i t s; do printf "${ink}%s${reset}" "$ch"; sleep 0.055; done
printf "\n\033[?25h"
"""


def build_motion() -> None:
    from . import ident
    write("motion/ident.html", ident.html())
    write("motion/ident-game.html", ident.html("ceteris"))
    write("motion/typeon.svg", typeon_svg())
    write("motion/splash.sh", SPLASH)
    (ROOT / "motion/splash.sh").chmod(0o755)


# Tokens ----------------------------------------------------------------------------------------------
def build_tokens() -> None:
    def block(i: int) -> str:
        rows = [f"  --as-{k}: {v[i]};" for k, v in UI.items()] + [f"  --as-code-{k}: {v[i]};" for k, v in SYNTAX.items()]
        return "\n".join(rows)
    fonts = "\n".join(f"  --as-font-{k}: {v};" for k, v in FONTS.items())
    scale = "\n".join(f"  --as-size-{k}: {v};" for k, v in TYPE_SCALE.items())
    css = f"""/* Animal Spirits Ledger tokens. Dark first: dark on :root, light under prefers-color-scheme and [data-theme="light"]. */
:root {{
{block(0)}
{fonts}
{scale}
  color-scheme: dark;
}}
@media (prefers-color-scheme: light) {{
  :root:not([data-theme="dark"]) {{
{block(1).replace("  --", "    --")}
    color-scheme: light;
  }}
}}
:root[data-theme="light"] {{
{block(1)}
  color-scheme: light;
}}
"""
    write("tokens/tokens.css", css)
    col = lambda v: {"$type": "color", "$value": v}  # noqa: E731
    tokens = {"color": {mode: {**{k: col(v[i]) for k, v in UI.items()}, "code": {k: col(v[i]) for k, v in SYNTAX.items()},
                               "ansi": {str(n): col(c) for n, c in enumerate(ANSI[mode])}}
                        for i, mode in enumerate(("dark", "light"))},
              "font": {k: {"$type": "fontFamily", "$value": [f.strip().strip("'") for f in v.split(",")]} for k, v in FONTS.items()},
              "size": {k: {"$type": "dimension", "$value": v} for k, v in TYPE_SCALE.items()}}
    write("tokens/tokens.json", json.dumps(tokens, indent=2, ensure_ascii=False) + "\n")


# Terminal themes -------------------------------------------------------------------------------------
def build_terminal() -> None:
    for mode, i in (("dark", 0), ("light", 1)):
        t, a, n = TERMINAL[mode], ANSI[mode], f"animal-spirits-ledger-{mode}"
        write(f"themes/ghostty/{n}", "".join(f"palette = {k}={c}\n" for k, c in enumerate(a))
              + f"background = {t['bg']}\nforeground = {t['fg']}\ncursor-color = {t['cursor']}\ncursor-text = {t['cursor_text']}\n"
                f"selection-background = {t['sel_bg']}\nselection-foreground = {t['sel_fg']}\n")
        write(f"themes/alacritty/{n}.toml",
              f"[colors.primary]\nbackground = \"{t['bg']}\"\nforeground = \"{t['fg']}\"\n\n"
              f"[colors.cursor]\ncursor = \"{t['cursor']}\"\ntext = \"{t['cursor_text']}\"\n\n"
              f"[colors.selection]\nbackground = \"{t['sel_bg']}\"\ntext = \"{t['sel_fg']}\"\n\n"
              + "[colors.normal]\n" + "".join(f"{nm} = \"{a[k]}\"\n" for k, nm in enumerate(ANSI_NAMES))
              + "\n[colors.bright]\n" + "".join(f"{nm} = \"{a[k + 8]}\"\n" for k, nm in enumerate(ANSI_NAMES)))
        write(f"themes/kitty/{n}.conf",
              f"background {t['bg']}\nforeground {t['fg']}\ncursor {t['cursor']}\ncursor_text_color {t['cursor_text']}\n"
              f"selection_background {t['sel_bg']}\nselection_foreground {t['sel_fg']}\n" + "".join(f"color{k} {c}\n" for k, c in enumerate(a)))
        q = lambda xs: ", ".join(f'"{x}"' for x in xs)  # noqa: E731
        write(f"themes/wezterm/{n}.toml",
              f"[colors]\nbackground = \"{t['bg']}\"\nforeground = \"{t['fg']}\"\ncursor_bg = \"{t['cursor']}\"\ncursor_fg = \"{t['cursor_text']}\"\n"
              f"cursor_border = \"{t['cursor']}\"\nselection_bg = \"{t['sel_bg']}\"\nselection_fg = \"{t['sel_fg']}\"\n"
              f"ansi = [{q(a[:8])}]\nbrights = [{q(a[8:])}]\n\n[metadata]\nname = \"{NAME} {mode.title()}\"\n")
    wt = []
    for mode in ("dark", "light"):
        t, a = TERMINAL[mode], ANSI[mode]
        names = ["black", "red", "green", "yellow", "blue", "purple", "cyan", "white"]
        s = {"name": f"{NAME} {mode.title()}", "background": t["bg"], "foreground": t["fg"], "cursorColor": t["cursor"],
             "selectionBackground": t["sel_bg"]}
        s |= {nm: a[k] for k, nm in enumerate(names)} | {"bright" + nm.title(): a[k + 8] for k, nm in enumerate(names)}
        wt.append(s)
    write("themes/windows-terminal/schemes.json", json.dumps({"schemes": wt}, indent=2) + "\n")


# Editor themes ---------------------------------------------------------------------------------------
def _alpha(h: str, a: float) -> str:
    return f"{h}{round(a * 255):02X}"


def vscode_theme(i: int) -> dict:
    u = {k: v[i] for k, v in UI.items()}
    s = {k: v[i] for k, v in SYNTAX.items()}
    a = ANSI["dark" if i == 0 else "light"]
    term = {f"terminal.ansi{'Bright' if k >= 8 else ''}{['Black', 'Red', 'Green', 'Yellow', 'Blue', 'Magenta', 'Cyan', 'White'][k % 8]}": c
            for k, c in enumerate(a)}
    colors = {
        "editor.background": u["bg"], "editor.foreground": u["text"], "editorCursor.foreground": TERMINAL["dark" if i == 0 else "light"]["cursor"],
        "editorCursor.background": u["on-accent"], "editor.selectionBackground": u["selection"],
        "editor.lineHighlightBackground": _alpha(u["surface"], .6), "editorLineNumber.foreground": u["border"] if i == 0 else u["text-muted"],
        "editorLineNumber.activeForeground": u["text"], "editorBracketMatch.border": u["accent"], "editorBracketMatch.background": "#00000000",
        "editor.findMatchBackground": _alpha(u["accent"], .55), "editor.findMatchHighlightBackground": _alpha(u["accent"], .22),
        "editorWhitespace.foreground": u["border"], "editorIndentGuide.background1": u["surface-2"], "editorIndentGuide.activeBackground1": u["border"],
        "editorGutter.background": u["bg"], "editorError.foreground": u["error"], "editorWarning.foreground": u["warning"],
        "editorInfo.foreground": u["info"], "focusBorder": u["link"], "foreground": u["text"], "descriptionForeground": u["text-muted"],
        "textLink.foreground": u["link"], "textLink.activeForeground": u["link"], "errorForeground": u["error"],
        "sideBar.background": u["bg"], "sideBar.foreground": u["text-muted"], "sideBar.border": u["surface"],
        "sideBarSectionHeader.background": u["bg"], "sideBarTitle.foreground": u["text"],
        "activityBar.background": u["bg"], "activityBar.foreground": u["text"], "activityBar.inactiveForeground": u["text-muted"],
        "activityBarBadge.background": u["accent"], "activityBarBadge.foreground": u["on-accent"], "activityBar.border": u["surface"],
        "statusBar.background": u["surface"], "statusBar.foreground": u["text-muted"], "statusBar.border": u["surface"],
        "statusBarItem.remoteBackground": u["accent"], "statusBarItem.remoteForeground": u["on-accent"],
        "titleBar.activeBackground": u["bg"], "titleBar.activeForeground": u["text"], "titleBar.inactiveBackground": u["bg"],
        "tab.activeBackground": u["bg"], "tab.inactiveBackground": u["surface"], "tab.activeForeground": u["text"],
        "tab.inactiveForeground": u["text-muted"], "tab.activeBorderTop": u["accent"], "tab.border": u["surface"],
        "editorGroupHeader.tabsBackground": u["surface"], "panel.background": u["bg"], "panel.border": u["surface-2"],
        "terminal.background": u["bg"], "terminal.foreground": u["text"], "terminalCursor.foreground": TERMINAL["dark" if i == 0 else "light"]["cursor"],
        "button.background": u["accent"], "button.foreground": u["on-accent"], "button.hoverBackground": u["accent"],
        "input.background": u["surface"], "input.border": u["border"], "input.foreground": u["text"], "input.placeholderForeground": u["text-muted"],
        "dropdown.background": u["surface"], "dropdown.border": u["border"], "badge.background": u["surface-2"], "badge.foreground": u["text"],
        "list.activeSelectionBackground": u["selection"], "list.activeSelectionForeground": u["text"], "list.hoverBackground": u["surface"],
        "list.inactiveSelectionBackground": u["surface"], "list.highlightForeground": u["link"],
        "gitDecoration.addedResourceForeground": u["success"], "gitDecoration.modifiedResourceForeground": u["chart"],
        "gitDecoration.deletedResourceForeground": u["error"], "gitDecoration.untrackedResourceForeground": u["success"],
        "editorWidget.background": u["surface"], "editorWidget.border": u["border"], "scrollbarSlider.background": _alpha(u["border"], .5),
        **term,
    }

    def rule(scope, key, style=None):
        r = {"scope": scope, "settings": {"foreground": s[key]}}
        if style:
            r["settings"]["fontStyle"] = style
        return r
    tokens = [
        rule(["comment", "punctuation.definition.comment"], "comment", "italic"),
        rule(["keyword", "storage.type", "storage.modifier", "keyword.control", "keyword.other"], "keyword"),
        rule(["entity.name.function", "support.function", "meta.function-call.generic"], "function"),
        rule(["entity.name.type", "entity.name.class", "support.type", "support.class", "storage.type.primitive", "entity.other.inherited-class"], "type"),
        rule(["string", "string.quoted", "punctuation.definition.string"], "string"),
        rule(["constant.numeric", "constant.language", "constant.character", "constant.other"], "number"),
        rule(["variable", "variable.parameter", "variable.other"], "variable"),
        rule(["punctuation", "keyword.operator", "meta.brace"], "punctuation"),
        rule(["invalid", "invalid.illegal"], "invalid", "underline"),
        rule(["markup.heading", "entity.name.section"], "keyword", "bold"),
        rule(["markup.inline.raw", "markup.fenced_code"], "string"),
        rule(["markup.underline.link", "markup.link"], "keyword", "underline"),
        {"scope": "markup.italic", "settings": {"fontStyle": "italic"}},
        {"scope": "markup.bold", "settings": {"fontStyle": "bold"}},
    ]
    semantic = {"function": s["function"], "method": s["function"], "type": s["type"], "class": s["type"], "interface": s["type"],
                "enum": s["type"], "keyword": s["keyword"], "string": s["string"], "number": s["number"], "variable": s["variable"],
                "parameter": s["variable"], "property": s["variable"], "comment": {"foreground": s["comment"], "italic": True}}
    return {"name": f"{NAME} {'Dark' if i == 0 else 'Light'}", "type": "dark" if i == 0 else "light", "semanticHighlighting": True,
            "colors": colors, "tokenColors": tokens, "semanticTokenColors": semantic}


def build_vscode() -> None:
    files = []
    for i, mode in enumerate(("dark", "light")):
        fn = f"themes/animal-spirits-ledger-{mode}-color-theme.json"
        write(f"themes/vscode/{fn}", json.dumps(vscode_theme(i), indent=2) + "\n")
        files.append({"label": f"{NAME} {mode.title()}", "uiTheme": "vs-dark" if i == 0 else "vs", "path": f"./{fn}"})
    pkg = {"name": "animal-spirits-ledger", "displayName": NAME, "description": "Animal Spirits' Ledger colours: press black, ledger paper, one red block.",
           "version": "1.0.0", "publisher": "animal-spirits", "engines": {"vscode": "^1.80.0"}, "categories": ["Themes"],
           "contributes": {"themes": files}}
    write("themes/vscode/package.json", json.dumps(pkg, indent=2) + "\n")


def nvim_lua() -> str:
    def table(i: int) -> str:
        vals = {k.replace("-", "_"): v[i] for k, v in UI.items()} | {"c_" + k: v[i] for k, v in SYNTAX.items()}
        vals["cursor"] = TERMINAL["dark" if i == 0 else "light"]["cursor"]
        return "{ " + ", ".join(f'{k} = "{v}"' for k, v in vals.items()) + " }"
    ansi = lambda m: "{ " + ", ".join(f'"{c}"' for c in ANSI[m]) + " }"  # noqa: E731
    return f'''-- Animal Spirits Ledger for Neovim. Follows 'background': dark by default, light when set to light.
local palettes = {{
  dark = {table(0)},
  light = {table(1)},
}}
local ansi = {{ dark = {ansi("dark")}, light = {ansi("light")} }}

vim.cmd("highlight clear")
if vim.fn.exists("syntax_on") == 1 then vim.cmd("syntax reset") end
vim.g.colors_name = "animal-spirits"
local mode = vim.o.background == "light" and "light" or "dark"
local c = palettes[mode]
for i, col in ipairs(ansi[mode]) do vim.g["terminal_color_" .. (i - 1)] = col end

local function hl(group, opts) vim.api.nvim_set_hl(0, group, opts) end
hl("Normal", {{ fg = c.text, bg = c.bg }})
hl("NormalFloat", {{ fg = c.text, bg = c.surface }})
hl("FloatBorder", {{ fg = c.border, bg = c.surface }})
hl("Cursor", {{ fg = c.on_accent, bg = c.cursor }})
hl("CursorLine", {{ bg = c.surface }})
hl("CursorLineNr", {{ fg = c.text }})
hl("LineNr", {{ fg = c.text_muted }})
hl("SignColumn", {{ bg = c.bg }})
hl("Visual", {{ bg = c.selection }})
hl("Search", {{ fg = c.on_accent, bg = c.accent }})
hl("IncSearch", {{ fg = c.on_accent, bg = c.accent, bold = true }})
hl("CurSearch", {{ link = "IncSearch" }})
hl("MatchParen", {{ fg = c.accent_text, bold = true, underline = true }})
hl("Todo", {{ fg = c.on_accent, bg = c.accent, bold = true }})
hl("StatusLine", {{ fg = c.text_muted, bg = c.surface }})
hl("StatusLineNC", {{ fg = c.text_muted, bg = c.bg }})
hl("WinSeparator", {{ fg = c.surface_2 }})
hl("Pmenu", {{ fg = c.text, bg = c.surface }})
hl("PmenuSel", {{ fg = c.text, bg = c.selection }})
hl("TabLine", {{ fg = c.text_muted, bg = c.surface }})
hl("TabLineSel", {{ fg = c.text, bg = c.bg }})
hl("TabLineFill", {{ bg = c.surface }})
hl("Title", {{ fg = c.text, bold = true }})
hl("Directory", {{ fg = c.link }})
hl("NonText", {{ fg = c.border }})
hl("Whitespace", {{ fg = c.border }})
hl("Comment", {{ fg = c.c_comment, italic = true }})
hl("Constant", {{ fg = c.c_number }})
hl("String", {{ fg = c.c_string }})
hl("Character", {{ fg = c.c_string }})
hl("Identifier", {{ fg = c.c_variable }})
hl("Function", {{ fg = c.c_function }})
hl("Statement", {{ fg = c.c_keyword }})
hl("Keyword", {{ fg = c.c_keyword }})
hl("PreProc", {{ fg = c.c_keyword }})
hl("Type", {{ fg = c.c_type }})
hl("Special", {{ fg = c.link }})
hl("Operator", {{ fg = c.c_punctuation }})
hl("Delimiter", {{ fg = c.c_punctuation }})
hl("Underlined", {{ fg = c.link, underline = true }})
hl("Error", {{ fg = c.error }})
hl("ErrorMsg", {{ fg = c.error }})
hl("WarningMsg", {{ fg = c.warning }})
hl("DiagnosticError", {{ fg = c.error }})
hl("DiagnosticWarn", {{ fg = c.warning }})
hl("DiagnosticInfo", {{ fg = c.info }})
hl("DiagnosticHint", {{ fg = c.text_muted }})
hl("DiagnosticOk", {{ fg = c.success }})
hl("DiagnosticUnderlineError", {{ undercurl = true, sp = c.error }})
hl("DiagnosticUnderlineWarn", {{ undercurl = true, sp = c.warning }})
hl("DiffAdd", {{ fg = c.success }})
hl("DiffChange", {{ fg = c.chart }})
hl("DiffDelete", {{ fg = c.error }})
hl("@comment", {{ link = "Comment" }})
hl("@keyword", {{ link = "Keyword" }})
hl("@function", {{ link = "Function" }})
hl("@function.call", {{ link = "Function" }})
hl("@type", {{ link = "Type" }})
hl("@string", {{ link = "String" }})
hl("@number", {{ link = "Constant" }})
hl("@boolean", {{ link = "Constant" }})
hl("@constant", {{ link = "Constant" }})
hl("@variable", {{ link = "Identifier" }})
hl("@punctuation", {{ link = "Delimiter" }})
hl("@operator", {{ link = "Operator" }})
'''


def build_world() -> None:
    from . import devices, patterns
    write("patterns/utility-dark.svg", patterns.svg(patterns.utility(UI["text"][0], .12), UI["bg"][0]))
    write("patterns/utility-light.svg", patterns.svg(patterns.utility(UI["text"][1], .14), UI["bg"][1]))
    for name, big, small in devices.STAMPS:
        write(f"devices/stamp-{name}.svg", devices.stamp(big, small))
    write("devices/tape-dark.svg", devices.tape(UI["text-muted"][0]))
    write("devices/tape-light.svg", devices.tape(UI["text-muted"][1]))
    write("tokens/devices.css", DEVICES_CSS)


DEVICES_CSS = """/* Devices: load after tokens.css. Footnotes are numbered in red squares; ledgers end on a double rule. */
sup.as-fn { font: 500 .7em/1 var(--as-font-mono); background: var(--as-accent); color: var(--as-on-accent);
  padding: .15em .35em; margin-left: .1em; vertical-align: .45em; }
aside.as-note { border-left: 2px solid var(--as-text); padding-left: 1em; font: 400 .875rem/1.55 var(--as-font-text);
  color: var(--as-text-muted); }
table.as-ledger { border-collapse: collapse; width: 100%; font: .8125rem var(--as-font-mono); font-variant-numeric: tabular-nums; }
table.as-ledger th { text-align: left; font-weight: 400; color: var(--as-text-muted); }
table.as-ledger td, table.as-ledger th { padding: .45em .6em; border-bottom: 1px solid var(--as-border); }
table.as-ledger td:not(:first-child) { text-align: right; }
table.as-ledger tbody tr:first-child td { border-top: 2px solid var(--as-text); }
table.as-ledger tfoot td { border-top: 1px solid var(--as-text); border-bottom: 3px double var(--as-text); }
.as-utility { background: var(--as-bg) url(../patterns/utility-dark.svg) center / cover; }
:root[data-theme="light"] .as-utility { background-image: url(../patterns/utility-light.svg); }
@media (prefers-color-scheme: light) { :root:not([data-theme="dark"]) .as-utility { background-image: url(../patterns/utility-light.svg); } }
"""


def main() -> None:
    build_logos()
    build_banners()
    build_motion()
    build_tokens()
    build_terminal()
    build_vscode()
    build_world()
    write("themes/nvim/colors/animal-spirits.lua", nvim_lua())
    print("wrote", ROOT)


if __name__ == "__main__":
    main()
