"""README 용 GIF 를 만든다. 쇼릴·소개 영상에서 구간을 잘라 팔레트 최적화 GIF 로 바꾼다.
크기 한도를 넘으면 fps → 가로 크기 순으로 낮춰 다시 만든다."""
import os, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "media"
REEL = ROOT / "VARCO-Game-Studio-Showreel.mp4"
INTRO = ROOT / "VARCO-Platform-Intro.mp4"
TMP = pathlib.Path(__file__).resolve().parent

# (이름, 원본, [(시작, 끝), ...], 가로, fps, 한도 MB)
CLIPS = [
    ("showreel-hero", REEL, [(4.0, 7.55), (8.0, 9.8), (26.0, 27.3), (29.6, 31.4), (50.35, 51.5), (55.6, 57.4)], 960, 15, 9.5),
    ("varco-apis", INTRO, [(8.8, 12.6)], 800, 12, 4.0),
    ("phase-team", REEL, [(8.0, 11.6)], 800, 12, 4.0),
    ("phase-plan", REEL, [(17.8, 21.7)], 800, 12, 4.0),
    ("phase-spec", REEL, [(23.4, 25.7)], 800, 12, 4.0),
    ("phase-make", REEL, [(28.0, 32.9)], 800, 12, 4.0),
    ("phase-build", REEL, [(36.4, 42.4)], 800, 12, 4.0),
    ("phase-ship", REEL, [(47.9, 51.7)], 800, 12, 4.0),
]

def cut(src, segs, dst):
    if len(segs) == 1:
        s, e = segs[0]
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(s), "-t", str(e - s), "-i", str(src), "-an", "-c:v", "libx264", "-crf", "12", str(dst)], check=True)
        return
    parts = "".join(f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}];" for i, (s, e) in enumerate(segs))
    parts += "".join(f"[v{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=0[out]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-filter_complex", parts, "-map", "[out]", "-an", "-c:v", "libx264", "-crf", "12", str(dst)], check=True)

def gif(src, dst, width, fps, colors=160):
    vf = (f"fps={fps},scale={width}:-1:flags=lanczos,split[a][b];"
          f"[a]palettegen=max_colors={colors}:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", vf, "-loop", "0", str(dst)], check=True)

OUT.mkdir(parents=True, exist_ok=True)
for name, src, segs, width, fps, limit in CLIPS:
    mid = TMP / f"{name}.mp4"; dst = OUT / f"{name}.gif"
    cut(src, segs, mid)
    attempts = [(width, fps, 160), (width, fps - 2, 128), (int(width * 0.85), fps - 2, 128), (int(width * 0.75), fps - 4, 96), (int(width * 0.66), 8, 96)]
    for w, f, c in attempts:
        gif(mid, dst, w, f, c)
        mb = dst.stat().st_size / 1e6
        if mb <= limit:
            break
    dur = sum(e - s for s, e in segs)
    print(f"{name:15s} {dur:4.1f}s  {w}px {f}fps {c}색  {mb:.2f}MB {'OK' if mb <= limit else '한도 초과'}")
