"""PNG and ICO exports of the SVGs, plus the social cards. Needs the `png` extra: uv run --extra png scripts/export_png.py"""
import asyncio
import os
import base64
from io import BytesIO
from pathlib import Path

from PIL import Image
from playwright.async_api import async_playwright

from animal_spirits_brand.palette import UI

ROOT = Path(__file__).resolve().parents[1]
FONTS = "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap"

SQUARES = [("logo/avatar.svg", "avatar", (256, 512, 1024)), ("logo/avatar-light.svg", "avatar-light", (512,)),
           ("logo/favicon.svg", "favicon", (16, 32, 48, 180, 192, 512))]
WIDE = [("logo/lockup-on-dark.svg", "lockup-on-dark", 1200), ("logo/lockup-on-light.svg", "lockup-on-light", 1200),
        ("logo/bar-on-dark.svg", "bar-on-dark", 1200), ("logo/bar-on-light.svg", "bar-on-light", 1200),
        ("logo/wordmark-on-dark.svg", "wordmark-on-dark", 1200), ("logo/wordmark-on-light.svg", "wordmark-on-light", 1200)]
GAMES = ["ceteris", "metropole", "strata", "hohmann", "foundry"]


def card(w: int, h: int) -> str:
    lockup = base64.b64encode((ROOT / "logo/lockup-on-dark.svg").read_bytes()).decode()
    bg, text, muted = UI["bg"][0], UI["text"][0], UI["text-muted"][0]
    return f"""<!doctype html><html><head><link rel="stylesheet" href="{FONTS}"><style>
html,body{{margin:0}} body{{width:{w}px;height:{h}px;background:{bg};position:relative;overflow:hidden;
background-image:linear-gradient(transparent 23px,rgba(236,230,216,.10) 23px);background-size:100% 24px}}
img{{position:absolute;left:{w * .08:.0f}px;top:{h * .22:.0f}px;width:{w * .50:.0f}px}}
p{{position:absolute;left:{w * .08:.0f}px;bottom:{h * .11:.0f}px;margin:0;font:500 21px 'IBM Plex Mono',monospace;color:{muted};white-space:nowrap}}
p b{{color:{text};font-weight:500}}</style></head><body><img src="data:image/svg+xml;base64,{lockup}" alt="">
<p>{" · ".join(f"<b>{g}</b>" for g in GAMES)} &nbsp; github.com/animal-spirits</p></body></html>"""


async def main() -> None:
    out = ROOT / "logo/png"
    out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=os.environ.get("CHROMIUM"))  # CHROMIUM: use an installed browser
        page = await browser.new_page()

        async def shot(svg: str, w: int, h: int) -> bytes:
            data = base64.b64encode((ROOT / svg).read_bytes()).decode()
            await page.set_viewport_size({"width": w, "height": h})
            await page.set_content(f'<html><body style="margin:0"><img src="data:image/svg+xml;base64,{data}" width="{w}" height="{h}" style="display:block"></body></html>')
            return await page.screenshot(omit_background=True)

        for svg, name, sizes in SQUARES:
            for s in sizes:
                (out / f"{name}-{s}.png").write_bytes(await shot(svg, s, s))
        icons = [Image.open(BytesIO((out / f"favicon-{s}.png").read_bytes())) for s in (16, 32, 48)]
        icons[0].save(ROOT / "logo/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)], append_images=icons[1:])
        for svg, name, w in WIDE:
            vb = (ROOT / svg).read_text().split('viewBox="')[1].split('"')[0].split()
            (out / f"{name}.png").write_bytes(await shot(svg, w, round(w * float(vb[3]) / float(vb[2]))))
        for name, w, h in (("readme-banner-dark", 1280, 320), ("readme-banner-light", 1280, 320)):
            (ROOT / f"social/{name}.png").write_bytes(await shot(f"social/{name}.svg", w, h))
        for name, (w, h) in (("og-card", (1200, 630)), ("github-social-preview", (1280, 640))):
            await page.set_viewport_size({"width": w, "height": h})
            await page.set_content(card(w, h))
            await page.wait_for_timeout(1500)
            await page.screenshot(path=str(ROOT / f"social/{name}.png"))
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
