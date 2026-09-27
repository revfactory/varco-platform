"""쇼릴 렌더러: index.html 을 프레임 단위로 캡처한다.
사용:
  python3 render.py stills 4.2 9.5 ...          → preview/t004.20.jpg ...
  python3 render.py sheet 이름 4.2 9.5 ...      → preview/이름.jpg (3열 밀착 인화)
  python3 render.py video 출력.mp4 [fps] [오디오.wav] [시작] [끝]
"""
import asyncio, os, subprocess, sys
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
DUR = 60.0

async def open_page(p):
    b = await p.chromium.launch(channel="chrome", headless=True, args=["--allow-file-access-from-files"])
    pg = await b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.on("console", lambda m: errors.append("console: " + m.text) if m.type == "error" else None)
    await pg.goto(f"file://{HERE}/index.html?capture=1")
    await pg.wait_for_function("window.__ready === true", timeout=60000)
    return b, pg, errors

async def main():
    mode = sys.argv[1]
    os.makedirs(os.path.join(HERE, "preview"), exist_ok=True)
    async with async_playwright() as p:
        b, pg, errors = await open_page(p)
        if mode in ("stills", "sheet"):
            name = sys.argv[2] if mode == "sheet" else None
            times = [float(x) for x in sys.argv[3 if mode == "sheet" else 2:]]
            paths = []
            for t in times:
                await pg.evaluate(f"window.__seek({t})")
                path = os.path.join(HERE, "preview", f"t{t:06.2f}.jpg")
                await pg.screenshot(path=path, type="jpeg", quality=88)
                paths.append(path)
            if mode == "sheet":
                from PIL import Image, ImageDraw
                cols, tw_, th_ = 3, 640, 360
                rows = (len(paths) + cols - 1) // cols
                sheet = Image.new("RGB", (cols * tw_, rows * th_), "black")
                d = ImageDraw.Draw(sheet)
                for i, q in enumerate(paths):
                    im = Image.open(q).resize((tw_, th_), Image.LANCZOS)
                    x, y = (i % cols) * tw_, (i // cols) * th_
                    sheet.paste(im, (x, y))
                    d.rectangle([x, y, x + 74, y + 24], fill="black")
                    d.text((x + 6, y + 5), f"{times[i]:.2f}s", fill="white")
                sheet.save(os.path.join(HERE, "preview", f"{name}.jpg"), quality=88)
        else:
            out = sys.argv[2]
            fps = int(sys.argv[3]) if len(sys.argv) > 3 else 60
            audio = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != "-" else None
            t0 = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
            t1 = float(sys.argv[6]) if len(sys.argv) > 6 else DUR
            cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-"]
            if audio:
                cmd += ["-ss", str(t0), "-t", str(t1 - t0), "-i", audio, "-c:a", "aac", "-b:a", "320k", "-ar", "48000"]
            cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "15", "-preset", "slow", "-profile:v", "high",
                    "-tune", "animation", "-movflags", "+faststart", "-shortest" if audio else "-y", out]
            cmd = [c for c in cmd if c != "-y" or cmd.index(c) == 1] if not audio else cmd
            ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            n = int(round((t1 - t0) * fps))
            for i in range(n):
                await pg.evaluate(f"window.__seek({t0 + i / fps})")
                ff.stdin.write(await pg.screenshot(type="jpeg", quality=94))
                if i % (fps * 5) == 0:
                    print(f"frame {i}/{n}", flush=True)
            ff.stdin.close(); ff.wait()
        await b.close()
        if errors:
            print("PAGE ERRORS:", errors[:10]); sys.exit(1)

asyncio.run(main())
