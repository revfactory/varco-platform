"""2분 제작 과정 영상 렌더러: index.html 을 프레임 단위로 캡처한다.
사용:
  python3 render.py stills 4.2 9.5 ...              → preview/t004.20.jpg ...
  python3 render.py sheet 이름 4.2 9.5 ...          → preview/이름.jpg (3열 밀착 인화)
  python3 render.py video 출력.mp4 [fps] [오디오.wav] [작업자 수]
    구간을 작업자 수만큼 나눠 브라우저를 여러 개 띄워 동시에 렌더링하고, 이어 붙인 뒤 오디오를 얹는다.
  python3 render.py chunk 출력.mp4 fps 시작프레임 끝프레임   (video 가 내부에서 부른다)
  python3 render.py concat 출력.mp4 [오디오.wav]           (out/chunks 의 조각만 다시 잇기)
"""
import asyncio, os, subprocess, sys, json, time
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
DUR = json.load(open(os.path.join(HERE, "timeline.json"), encoding="utf-8"))["duration"]
CRF = os.environ.get("CRF", "18")


async def open_page(p):
    b = await p.chromium.launch(channel="chrome", headless=True, args=["--allow-file-access-from-files"])
    pg = await b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.on("console", lambda m: errors.append("console: " + m.text) if m.type == "error" else None)
    await pg.goto(f"file://{HERE}/index.html?capture=1")
    await pg.wait_for_function("window.__ready === true", timeout=60000)
    return b, pg, errors


async def stills(mode, args):
    os.makedirs(os.path.join(HERE, "preview"), exist_ok=True)
    async with async_playwright() as p:
        b, pg, errors = await open_page(p)
        name = args[0] if mode == "sheet" else None
        times = [float(x) for x in (args[1:] if mode == "sheet" else args)]
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
                d.rectangle([x, y, x + 84, y + 24], fill="black")
                d.text((x + 6, y + 5), f"{times[i]:.2f}s", fill="white")
            sheet.save(os.path.join(HERE, "preview", f"{name}.jpg"), quality=88)
        await b.close()
        if errors:
            print("PAGE ERRORS:", errors[:10]); sys.exit(1)


async def chunk(out, fps, f0, f1):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", CRF, "-preset", "slow", "-profile:v", "high",
           "-tune", "animation", "-g", str(fps * 2), out]
    async with async_playwright() as p:
        b, pg, errors = await open_page(p)
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(f0, f1):
            await pg.evaluate(f"window.__seek({i / fps})")
            ff.stdin.write(await pg.screenshot(type="jpeg", quality=94))
            if (i - f0) % (fps * 5) == 0:
                print(f"[{f0}-{f1}] frame {i - f0}/{f1 - f0}", flush=True)
        ff.stdin.close(); ff.wait()
        if errors:
            print("PAGE ERRORS:", errors[:10], flush=True)
        # 브라우저 종료가 가끔 멈춰서 작업자가 끝나지 않는다. 파일은 이미 다 썼으므로 바로 끝낸다
        try:
            await asyncio.wait_for(b.close(), 10)
        except Exception:
            pass
        os._exit(1 if errors else 0)


def concat(out, audio, parts):
    lst = os.path.join(HERE, "out", "chunks", "list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst]
    if audio:
        cmd += ["-i", audio, "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "320k", "-ar", "48000"]
    cmd += ["-c:v", "copy", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)


def video(out, fps=60, audio=None, workers=8):
    n = int(round(DUR * fps))
    tmp = os.path.join(HERE, "out", "chunks")
    os.makedirs(tmp, exist_ok=True)
    bounds = [round(n * k / workers) for k in range(workers + 1)]
    t0 = time.time()
    procs, parts = [], []
    for k in range(workers):
        part = os.path.join(tmp, f"part{k:02d}.mp4")
        parts.append(part)
        procs.append(subprocess.Popen([sys.executable, __file__, "chunk", part, str(fps), str(bounds[k]), str(bounds[k + 1])]))
    codes = [p.wait() for p in procs]
    if any(codes):
        sys.exit(f"chunk failed: {codes}")
    concat(out, audio, parts)
    print(f"done {out} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode in ("stills", "sheet"):
        asyncio.run(stills(mode, sys.argv[2:]))
    elif mode == "concat":   # python3 render.py concat 출력.mp4 오디오.wav  (이미 렌더링한 조각만 잇기)
        parts = sorted(os.path.join(HERE, "out", "chunks", f) for f in os.listdir(os.path.join(HERE, "out", "chunks")) if f.startswith("part"))
        concat(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None, parts)
    elif mode == "chunk":
        asyncio.run(chunk(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])))
    else:
        a = sys.argv
        video(a[2], int(a[3]) if len(a) > 3 else 60, a[4] if len(a) > 4 and a[4] != "-" else None, int(a[5]) if len(a) > 5 else 8)
