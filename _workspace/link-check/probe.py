import json, asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        pg = await b.new_page(viewport={"width":1400,"height":1000})
        gql = []
        async def on_resp(r):
            if '/graphql' in r.url:
                try: gql.append({"req": r.request.post_data, "body": await r.text()})
                except Exception as e: gql.append({"err": str(e)})
        pg.on("response", on_resp)
        for slug in ["pricing", "sound-conversion", "voice-overview", "voice-text-to-speech-lite"]:
            await pg.goto(f"https://api.varco.ai/ko/docs/{slug}", wait_until="load", timeout=60000)
            await pg.wait_for_timeout(4000)
            await pg.screenshot(path=f"shots/{slug}.png", full_page=True)
        json.dump(gql, open("gql_capture.json","w"), ensure_ascii=False, indent=1)
        await b.close()
asyncio.run(main())
