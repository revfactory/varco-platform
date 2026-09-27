import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        pg = await b.new_page(viewport={"width":1400,"height":1000})
        for slug in ["sound-conversion","voice-overview"]:
            await pg.goto(f"https://api.varco.ai/ko/docs/{slug}", wait_until="load", timeout=60000)
            await pg.wait_for_timeout(4000)
            t = await pg.evaluate("""() => { const m=document.querySelector('main'); const art=document.querySelector('[class*="markdown"]');
              const all=m.innerText; const a=art?art.innerText:''; const i=all.indexOf(a.slice(-80));
              return {tail: all.slice(i+80), artClass: art?art.className:null, artParentChildren: art?[...art.parentElement.children].map(c=>c.tagName+'.'+c.className).join(' | '):null}; }""")
            print('=====',slug); print(t)
        await b.close()
asyncio.run(main())
