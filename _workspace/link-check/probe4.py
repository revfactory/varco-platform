import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        pg = await b.new_page(viewport={"width":1400,"height":1000})
        await pg.goto("https://api.varco.ai/ko/docs/pricing", wait_until="load", timeout=60000)
        await pg.wait_for_timeout(4000)
        cells = await pg.evaluate("""() => [...document.querySelectorAll('td')].filter(td => td.innerHTML.includes('br') || td.textContent.includes('br')).map(td => td.innerHTML)""")
        print(cells)
        await b.close()
asyncio.run(main())
