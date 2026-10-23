"""Serves the site locally and screenshots each page at desktop and phone widths into _build/shots/."""
import asyncio, pathlib, subprocess, sys, time
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT/'_build/shots'; OUT.mkdir(exist_ok=True)
pages = sys.argv[1:] or ['/', '/books/', '/about/', '/contact/', '/privacy/', '/404.html']
srv = subprocess.Popen([sys.executable, '-m', 'http.server', '8765', '-d', str(ROOT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
        for w, h, tag in [(1280, 900, 'desk'), (390, 844, 'phone')]:
            pg = await b.new_page(viewport={'width': w, 'height': h})
            for path in pages:
                await pg.goto('http://localhost:8765' + path); await pg.wait_for_timeout(300)
                sw = await pg.evaluate('document.documentElement.scrollWidth')
                if sw > w: print('HORIZONTAL OVERFLOW', tag, path, sw)
                name = (path.strip('/').replace('/', '_').replace('.html','') or 'home') + f'_{tag}.png'
                await pg.screenshot(path=str(OUT/name), full_page=True)
        await b.close()
try: asyncio.run(main())
finally: srv.terminate()
print('shots in', OUT)
