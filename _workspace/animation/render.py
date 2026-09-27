"""index.html 애니메이션을 프레임 단위로 캡처한다.
사용: python3 render.py stills t1 t2 ...   → preview/ 에 정지 화면
      python3 render.py video 출력.mp4 [fps] → ffmpeg 로 H.264 MP4
"""
import asyncio
import os
import subprocess
import sys

from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
DUR = 47.0


async def main():
    mode = sys.argv[1]
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        pg = await b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        await pg.goto(f"file://{HERE}/index.html?capture=1")
        await pg.wait_for_function("window.__ready === true", timeout=60000)
        if mode == "stills":
            os.makedirs(os.path.join(HERE, "preview"), exist_ok=True)
            for t in [float(x) for x in sys.argv[2:]]:
                await pg.evaluate(f"window.__seek({t})")
                await pg.screenshot(path=os.path.join(HERE, "preview", f"t{t:05.2f}.jpg"), type="jpeg", quality=85)
        else:
            out, fps = sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 30
            ff = subprocess.Popen(
                ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
                 "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "slow", "-movflags", "+faststart", out],
                stdin=subprocess.PIPE)
            n = int(DUR * fps)
            for i in range(n):
                await pg.evaluate(f"window.__seek({i / fps})")
                ff.stdin.write(await pg.screenshot(type="jpeg", quality=95))
                if i % (fps * 5) == 0:
                    print(f"frame {i}/{n}", flush=True)
            ff.stdin.close()
            ff.wait()
        await b.close()
        if errors:
            print("PAGE ERRORS:", errors)
            sys.exit(1)


asyncio.run(main())
