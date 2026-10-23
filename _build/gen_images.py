"""Renders og-card.png, favicon-32.png and apple-touch-icon.png with headless Chromium (Literata + owl)."""
import pathlib, asyncio, base64
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
font = base64.b64encode((ROOT/'assets/fonts/Literata-VF.woff2').read_bytes()).decode()
owl = base64.b64encode((ROOT/'assets/img/owl-ink.svg').read_bytes()).decode()
fav = base64.b64encode((ROOT/'favicon.svg').read_bytes()).decode()
OG = f"""<html><head><style>
@font-face{{font-family:Literata;src:url(data:font/woff2;base64,{font}) format('woff2');font-weight:200 900}}
body{{margin:0;width:1200px;height:630px;background:#FFFFFA;color:#181716;font-family:Literata;font-optical-sizing:auto;overflow:hidden}}
.c{{position:absolute;inset:0;padding:84px 96px;display:flex;flex-direction:column;justify-content:space-between}}
.lab{{display:flex;align-items:center;gap:18px;font-size:22px;font-weight:600;letter-spacing:.16em;text-transform:uppercase}}
.sq{{width:14px;height:14px;background:#FF3700}}
h1{{font-size:76px;line-height:1.02;font-weight:500;letter-spacing:-.015em;margin:0;max-width:820px}}
.foot{{display:flex;align-items:center;gap:20px}}
.foot img{{height:58px}}
.wm{{font-size:26px;font-weight:500;letter-spacing:.26em;text-transform:uppercase}}
.rule{{width:96px;height:5px;background:#FF3700}}
.owl{{position:absolute;right:110px;top:110px;height:410px}}
</style></head><body><div class="c">
<div class="lab"><span class="sq"></span>Western Philosophy Series</div>
<h1>The great questions, and the minds that asked them.</h1>
<div class="foot"><div class="rule"></div><span class="wm">Alex Omberg</span></div>
</div><img class="owl" src="data:image/svg+xml;base64,{owl}"></body></html>"""
ICON = lambda n: f'<html><body style="margin:0;width:{n}px;height:{n}px"><img src="data:image/svg+xml;base64,{fav}" style="width:{n}px;height:{n}px;display:block"></body></html>'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
        for html, w, h, out in [(OG,1200,630,'assets/img/og-card.png'),(ICON(32),32,32,'favicon-32.png'),(ICON(180),180,180,'apple-touch-icon.png')]:
            pg = await b.new_page(viewport={'width':w,'height':h})
            await pg.set_content(html); await pg.wait_for_timeout(400)
            await pg.screenshot(path=str(ROOT/out)); await pg.close()
        await b.close()
asyncio.run(main()); print('ok')
