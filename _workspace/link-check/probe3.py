import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        pg = await b.new_page(viewport={"width":1400,"height":1000})
        await pg.goto("https://api.varco.ai/ko/reference/sound-conversion", wait_until="load", timeout=60000)
        await pg.wait_for_timeout(4000)
        await pg.screenshot(path="shots/ref-sound-conversion.png")
        t = await pg.evaluate("""() => { const art=document.querySelector('[class*="markdown"]');
          return {artParentChildren: art?[...art.parentElement.children].map(c=>c.tagName+'.'+c.className).join(' | '):null,
                  outside: art ? [...art.parentElement.children].filter(c=>c!==art).map(c=>c.innerText.slice(0,300)).join(' || ') : null}; }""")
        print(t)
        await b.close()
asyncio.run(main())
