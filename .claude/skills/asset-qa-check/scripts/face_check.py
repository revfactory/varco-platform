#!/usr/bin/env python3
"""얼굴 애니메이션(Voice-to-Face 응답 JSON) 검사: 구조가 맞는지, 짝이 되는 음성과 길이가 맞는지 확인한다.

사용법
  face_check.py games/x/assets/anim/face/ch1_intro_001.json --audio games/x/assets/audio/voice/korean/ch1_intro_001.wav
  face_check.py --face-dir games/x/assets/anim/face --audio-dir games/x/assets/audio/voice/korean --lines ch1_intro_001 ch1_intro_002 --id vo_ch1_intro

검사: success=true, numFrames == weightMat 행 수, numPoses == faceNames 수 == 각 행 길이, 가중치가 0~1 근처(-0.05~1.05),
      음성 길이와 애니메이션 길이(numFrames/exportFps) 차이가 0.25초 이하, 표정이 실제로 움직이는가(가중치 분산 > 0).
"""
import argparse
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from qa_common import Report  # noqa: E402

TOL_S = 0.25


def audio_seconds(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1",
                          str(path)], capture_output=True, text=True, timeout=60)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return None


def check_one(rep, face_path, audio_path):
    name = pathlib.Path(face_path).stem
    try:
        d = json.loads(pathlib.Path(face_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        rep.add(f"{name}:json", False, str(e), f"{name} 얼굴 JSON 을 읽을 수 없다", "face.blendshape 를 다시 호출한다")
        return
    b = d.get("blendshape") or {}
    rep.add(f"{name}:success", d.get("success") is True, f"success={d.get('success')}",
            f"{name} 응답 success 가 true 가 아니다", "음성 입력을 확인해 다시 호출한다")
    W, names = b.get("weightMat") or [], b.get("faceNames") or []
    frames, poses, fps = b.get("numFrames"), b.get("numPoses"), b.get("exportFps") or 30
    shape_ok = (frames == len(W) and poses == len(names) and all(len(r) == len(names) for r in W) and len(W) > 0)
    rep.add(f"{name}:shape", shape_ok, f"frames {frames}/{len(W)}, poses {poses}/{len(names)}",
            f"{name} weightMat 크기가 numFrames×numPoses 와 다르다", "다시 호출한다")
    if W:
        flat = [v for r in W for v in r]
        lo, hi = min(flat), max(flat)
        rep.add(f"{name}:range", -0.05 <= lo and hi <= 1.05, f"{lo:.3f}~{hi:.3f}", f"{name} 가중치 범위 이상",
                "다시 호출한다")
        mean = sum(flat) / len(flat)
        var = sum((v - mean) ** 2 for v in flat) / len(flat)
        rep.add(f"{name}:moves", var > 1e-6, f"분산 {var:.2e}", f"{name} 표정이 움직이지 않는다",
                "face_style·lip_style 을 바꾸거나 음성을 확인한다")
    if audio_path:
        secs = audio_seconds(audio_path) if pathlib.Path(audio_path).exists() else None
        if secs is None:
            rep.add(f"{name}:sync", None, "짝 음성을 찾지 못함")
        else:
            anim = (frames or len(W)) / fps
            rep.add(f"{name}:sync", abs(anim - secs) <= TOL_S, f"애니 {anim:.2f}s / 음성 {secs:.2f}s",
                    f"{name} 음성과 애니메이션 길이 차이 {abs(anim - secs):.2f}s", "최종 음성 파일로 다시 호출한다")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--audio")
    ap.add_argument("--face-dir")
    ap.add_argument("--audio-dir")
    ap.add_argument("--audio-ext", default="wav")
    ap.add_argument("--lines", nargs="*")
    ap.add_argument("--id", default="face")
    ap.add_argument("--out")
    args = ap.parse_args()
    rep = Report(args.id)
    pairs = [(f, args.audio) for f in args.files]
    if args.lines and args.face_dir:
        for lid in args.lines:
            pairs.append((str(pathlib.Path(args.face_dir) / f"{lid}.json"),
                          str(pathlib.Path(args.audio_dir) / f"{lid}.{args.audio_ext}") if args.audio_dir else None))
    missing = [f for f, _ in pairs if not pathlib.Path(f).exists()]
    if missing:
        rep.add("file_count", False, f"{len(pairs) - len(missing)}/{len(pairs)}", f"얼굴 JSON 없음: {missing[:5]}",
                "빠진 줄의 face.blendshape 를 호출한다")
    present = [(f, a) for f, a in pairs if pathlib.Path(f).exists()]
    if not present:
        rep.cannot_verify("검사할 얼굴 JSON 이 없다")
    for f, a in present:
        check_one(rep, f, a)
    sys.exit(rep.emit(args.out))


if __name__ == "__main__":
    main()
