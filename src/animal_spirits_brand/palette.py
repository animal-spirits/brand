"""Ledger: press-black ground, ledger paper, one red block. Every colour Animal Spirits uses is defined here."""

# role -> (dark, light)
UI = {
    "bg": ("#161110", "#ECE8DE"),          # ground: press black / ledger paper
    "surface": ("#221C19", "#E1DCD0"),     # cards, code blocks
    "surface-2": ("#2E2724", "#D5CFC2"),   # hover, nested surfaces
    "border": ("#463D38", "#BDB5A6"),
    "text": ("#ECE6D8", "#161110"),
    "text-muted": ("#A39A8E", "#5A524C"),
    "accent": ("#C32B1F", "#C32B1F"),      # spirit red: the block behind Keynes, the primary button. Fills only.
    "on-accent": ("#161110", "#161110"),   # ink inside the block
    "accent-text": ("#F27A66", "#A8241A"), # red as text (errors); lifted on black, deepened on paper
    "selection": ("#3A2522", "#E6D2C6"),
    "link": ("#8FBACB", "#1F5F78"),        # slate
    "info": ("#8FBACB", "#1F5F78"),        # slate
    "success": ("#A9C48A", "#3C6E3A"),     # sage
    "warning": ("#D9B45E", "#7A5A08"),     # brass
    "error": ("#F27A66", "#A8241A"),       # red: errors are the one place red is text
    "chart": ("#A9B7E0", "#3F5E96"),       # periwinkle
}

# Syntax: red stays out of code text; it marks the cursor, search hits and errors.
SYNTAX = {
    "comment": ("#8C837A", "#6A625A"),
    "keyword": ("#8FBACB", "#1F5F78"),     # slate
    "function": ("#A9B7E0", "#3F5E96"),    # periwinkle
    "type": ("#D3A6B4", "#7D4058"),        # rose
    "string": ("#A9C48A", "#3C6E3A"),      # sage
    "number": ("#D9B45E", "#7A5A08"),      # brass
    "variable": ("#ECE6D8", "#161110"),
    "punctuation": ("#A39A8E", "#5A524C"),
    "invalid": ("#F27A66", "#A8241A"),
}

# 16-colour terminal palette: normal 0-7, bright 8-15.
ANSI = {
    "dark": ["#221C19", "#F27A66", "#A9C48A", "#D9B45E", "#A9B7E0", "#D3A6B4", "#8FBACB", "#C9C1B3",
             "#6A615A", "#FF9A88", "#C2DBA5", "#EBCB7E", "#C3CEF0", "#E6C2CD", "#B0D2DF", "#ECE6D8"],
    "light": ["#161110", "#A8241A", "#3C6E3A", "#7A5A08", "#3F5E96", "#7D4058", "#1F5F78", "#D5CFC2",
              "#5A524C", "#A8241A", "#3C6E3A", "#7A5A08", "#3F5E96", "#7D4058", "#1F5F78", "#E1DCD0"],
}
TERMINAL = {
    "dark": dict(bg="#161110", fg="#ECE6D8", cursor="#C32B1F", cursor_text="#ECE6D8", sel_bg="#3A2522", sel_fg="#ECE6D8"),
    "light": dict(bg="#ECE8DE", fg="#161110", cursor="#C32B1F", cursor_text="#ECE8DE", sel_bg="#E6D2C6", sel_fg="#161110"),
}
ANSI_NAMES = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]

FONTS = {
    "display": "'Source Serif 4', Georgia, serif",
    "text": "'IBM Plex Sans', system-ui, -apple-system, 'Segoe UI', sans-serif",
    "mono": "'IBM Plex Mono', ui-monospace, Menlo, Consolas, monospace",
}
# 16px base, ratio 1.25
TYPE_SCALE = {"xs": "0.8rem", "sm": "0.875rem", "base": "1rem", "lg": "1.25rem", "xl": "1.563rem", "2xl": "1.953rem",
              "3xl": "2.441rem", "4xl": "3.052rem"}


def _lin(c: float) -> float:
    return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4


def luminance(h: str) -> float:
    r, g, b = (_lin(int(h[i:i + 2], 16) / 255) for i in (1, 3, 5))
    return .2126 * r + .7152 * g + .0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + .05) / (lb + .05)
