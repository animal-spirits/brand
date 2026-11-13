"""The slow drawings: the cabinet objects (ray-marched, a few minutes each), the Crowd pattern built from the hat,
and generated woodcuts from data/cuts/*.png traced into three cuts. Run after any change to cabinet.py or a new cut:
uv run scripts/cabinet.py [name ... | --cuts]"""
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from animal_spirits_brand import patterns
from animal_spirits_brand.cabinet import OBJECTS
from animal_spirits_brand.engrave import render, svg_path
from animal_spirits_brand.palette import UI
from animal_spirits_brand.portrait import DATA, LARGE_ONLY, SIZE, engraving, woodcut

ROOT = Path(__file__).resolve().parents[1]
RED, INK, PAPER, TEXT = UI["accent"][0], UI["bg"][0], UI["bg"][1], UI["text"][0]


def write(rel: str, text: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def ink_svg(d: str, vb: float, label: str, fill: str = "currentColor") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb:g} {vb:g}" width="512" height="512" role="img" aria-label="{label}">'
            f'<path fill="{fill}" fill-rule="evenodd" d="{d}"/></svg>')


def block_svg(d: str, vb: float, label: str, inset: float) -> str:
    """The red block holding a subject in ink; objects sit inside with a margin, portraits fill it."""
    k = 1 - 2 * inset
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb:g} {vb:g}" width="512" height="512" role="img" aria-label="{label}">'
            f'<rect width="{vb:g}" height="{vb:g}" fill="{RED}"/><path transform="translate({vb * inset:g} {vb * inset:g}) scale({k:g})" '
            f'fill="{INK}" fill-rule="evenodd" d="{d}"/></svg>')


def draw(name: str) -> tuple[str, str]:
    """A generated engraving in data/cabinet/<name>.png replaces the ray-marched drawing."""
    png = DATA / "cabinet" / f"{name}.png"
    if png.exists():
        return name, engraving(png)
    scene, view = OBJECTS[name]()
    return name, svg_path(render(scene, res=900, **view))


def main(names: list[str]) -> None:
    if names == ["--cuts"]:
        names = []
    else:
        names = names or list(OBJECTS)
    with ProcessPoolExecutor() as ex:
        for name, d in ex.map(draw, names):
            vb = SIZE if (DATA / "cabinet" / f"{name}.png").exists() else 100
            write(f"cabinet/{name}.svg", ink_svg(d, vb, name))
            if name != "hat":
                write(f"cabinet/{name}-block.svg", block_svg(d, vb, name, .06))
            print(name)
    if names:
        _crowd()
    _cuts()


def _crowd() -> None:
    hat = (ROOT / "cabinet/hat.svg").read_text().split(' d="')[1].split('"')[0]
    write("patterns/crowd-tile-light.svg", patterns.crowd_tile(hat, INK, .9))
    write("patterns/crowd-tile-dark.svg", patterns.crowd_tile(hat, TEXT, .3))
    write("patterns/crowd-light.svg", patterns.svg(patterns.crowd(hat, INK, .9), PAPER))
    write("patterns/crowd-dark.svg", patterns.svg(patterns.crowd(hat, TEXT, .3), INK))


def _cuts() -> None:
    for png in sorted((DATA / "cuts").glob("*.png")):
        for n in (1,) if png.stem in LARGE_ONLY else (1, 2, 3):
            d = woodcut(png, n)
            write(f"woodcuts/{png.stem}-cut-{n}.svg", ink_svg(d, SIZE, png.stem))
            write(f"woodcuts/{png.stem}-cut-{n}-block.svg", block_svg(d, SIZE, png.stem, 0))
        print(png.stem)


if __name__ == "__main__":
    main(sys.argv[1:])
