#!/usr/bin/env python3
"""오디오 에셋 검사: 길이·채널·샘플레이트·피크·라우드니스·루프 이음매를 측정해 acceptance 와 대조한다.

사용법
  audio_check.py f1.wav f2.wav --id sfx_door --acceptance '{"duration_s":[0.1,2.0],"peak_dbfs_max":-1.0}'
  audio_check.py amb_rain.wav --id amb_rain --acceptance-file acc.json --loop --out _workspace/x/03_assetqa_amb_rain.json
  audio_check.py f*.wav --id sfx_x --expect-count 5

측정 도구: ffprobe(형식), ffmpeg(디코딩·ebur128). 루프 검사는 numpy 로 한다.
루프 판정 기준(경험칙): 끝과 시작 50ms 의 RMS 차이 6dB 초과, 또는 경계 샘플 점프가
파일 내부 인접 샘플 차이의 99.9 백분위수의 4배와 0.05(선형) 를 모두 넘으면 실패.
"""
import argparse
import json
import math
import pathlib
import re
import subprocess
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from qa_common import Report, load_acceptance  # noqa: E402

SILENCE_DBFS = -60.0
SEAM_MS = 50


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
                          "stream=channels,sample_rate,codec_name:format=duration", "-of", "json", str(path)],
                         capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or "ffprobe 실패")
    d = json.loads(out.stdout or "{}")
    st = (d.get("streams") or [{}])[0]
    return {"channels": int(st.get("channels", 0) or 0), "sample_rate": int(st.get("sample_rate", 0) or 0),
            "codec": st.get("codec_name"), "duration_s": float((d.get("format") or {}).get("duration", 0) or 0)}


def decode(path, channels):
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", str(max(channels, 1)), "-"],
                         capture_output=True, timeout=300)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.decode(errors="ignore").strip() or "ffmpeg 디코딩 실패")
    x = np.frombuffer(out.stdout, dtype=np.float32)
    ch = max(channels, 1)
    return x[: len(x) // ch * ch].reshape(-1, ch)


def lufs(path):
    out = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", str(path), "-filter_complex", "ebur128",
                          "-f", "null", "-"], capture_output=True, text=True, timeout=300)
    m = re.findall(r"I:\s+(-?[\d.]+|-inf)\s+LUFS", out.stderr)
    if not m or m[-1] == "-inf":
        return None
    v = float(m[-1])
    return None if v <= -69.9 else v   # -70 은 게이트 아래(무음 또는 너무 짧음)라 측정값으로 쓰지 않는다


def dbfs(v):
    return -math.inf if v <= 0 else 20 * math.log10(v)


def seam(x, sr):
    n = max(1, int(sr * SEAM_MS / 1000))
    if len(x) < 4 * n:
        return None
    head, tail = x[:n], x[-n:]
    rms_h = float(np.sqrt(np.mean(head ** 2)))
    rms_t = float(np.sqrt(np.mean(tail ** 2)))
    rms_diff = abs(dbfs(rms_t + 1e-9) - dbfs(rms_h + 1e-9))
    jump = float(np.max(np.abs(x[-1] - x[0])))
    typical = float(np.percentile(np.abs(np.diff(x, axis=0)), 99.9))
    return {"rms_head_dbfs": round(dbfs(rms_h + 1e-12), 1), "rms_tail_dbfs": round(dbfs(rms_t + 1e-12), 1),
            "rms_diff_db": round(rms_diff, 2), "boundary_jump": round(jump, 4), "typical_step_p999": round(typical, 4),
            "ok": not (rms_diff > 6.0 or (jump > 4 * typical and jump > 0.05))}


def measure(path):
    p = probe(path)
    x = decode(path, p["channels"])
    peak = float(np.max(np.abs(x))) if x.size else 0.0
    m = dict(p)
    m["peak_dbfs"] = round(dbfs(peak), 2) if peak > 0 else None
    m["lufs"] = lufs(path)
    m["_samples"] = x
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--id", default="audio")
    ap.add_argument("--acceptance")
    ap.add_argument("--acceptance-file")
    ap.add_argument("--loop", action="store_true", help="acceptance.loop 와 같다")
    ap.add_argument("--expect-count", type=int)
    ap.add_argument("--out")
    args = ap.parse_args()

    acc = load_acceptance(args.acceptance, args.acceptance_file)
    loop = args.loop or bool(acc.get("loop"))
    rep = Report(args.id)
    existing = [f for f in args.files if pathlib.Path(f).is_file()]
    missing = [f for f in args.files if not pathlib.Path(f).is_file()]

    if args.expect_count is not None:
        rep.add("file_count", len(existing) == args.expect_count, f"{len(existing)}/{args.expect_count}",
                f"결과 파일 {len(existing)}개(기대 {args.expect_count}개). 없음: {missing[:5]}",
                "빠진 결과 파일을 다시 생성한다")
    elif missing:
        rep.add("file_count", False, f"없음 {len(missing)}개", f"파일 없음: {missing[:5]}", "빠진 결과 파일을 다시 생성한다")
    if not existing:
        rep.cannot_verify("검사할 오디오 파일이 없다")
        sys.exit(rep.emit(args.out))

    measures, decode_fail = {}, []
    for f in existing:
        try:
            measures[f] = measure(f)
        except Exception as e:  # 손상 파일
            decode_fail.append(f"{pathlib.Path(f).name}: {e}")
    rep.add("decodable", not decode_fail, f"{len(measures)}/{len(existing)}",
            f"디코딩 실패: {decode_fail}", "손상된 파일을 다시 생성한다")
    if not measures:
        sys.exit(rep.emit(args.out))

    def over_all(name, pred, fmt, issue, hint):
        bad = [f"{pathlib.Path(f).name}={fmt(m)}" for f, m in measures.items() if not pred(m)]
        vals = sorted((fmt(m) for m in measures.values()), key=lambda v: -math.inf if v is None else v)
        rep.add(name, not bad, f"{vals[0]}~{vals[-1]}" if len(vals) > 1 else str(vals[0]),
                f"{issue}: {bad[:5]}" if bad else None, hint)

    over_all("not_silent", lambda m: m["peak_dbfs"] is not None and m["peak_dbfs"] > SILENCE_DBFS,
             lambda m: m["peak_dbfs"], "무음에 가까움", "프롬프트나 입력을 바꿔 다시 생성한다")

    if "duration_s" in acc:
        lo, hi = acc["duration_s"]
        over_all("duration_s", lambda m: lo <= m["duration_s"] <= hi, lambda m: round(m["duration_s"], 2),
                 f"길이가 [{lo}, {hi}]초 밖", "뒤쪽 무음을 자르거나(ffmpeg silenceremove) 길이 파라미터를 조정한다")
    else:
        rep.add("duration_s", None, "기준 없음")
    for key in ("channels", "sample_rate"):
        if key in acc:
            over_all(key, lambda m, k=key: m[k] == acc[k], lambda m, k=key: m[k], f"{key} 가 {acc[key]} 아님",
                     "mono2stereo 로 확장하거나 ffmpeg 로 변환한다" if key == "channels" else "ffmpeg -ar 로 변환한다")
    if "peak_dbfs_max" in acc:
        lim = acc["peak_dbfs_max"]
        over_all("peak_dbfs", lambda m: m["peak_dbfs"] is None or m["peak_dbfs"] <= lim,
                 lambda m: m["peak_dbfs"], f"피크가 {lim}dBFS 초과", "게인을 낮추거나 variation strength 를 낮춘다")
    if "lufs_range" in acc:
        lo, hi = acc["lufs_range"]
        bad = [f for f, m in measures.items() if m["lufs"] is None or not (lo <= m["lufs"] <= hi)]
        vals = [m["lufs"] for m in measures.values()]
        if all(v is None for v in vals):
            rep.add("lufs_range", None, "라우드니스 측정 불가(파일이 너무 짧음)")
        else:
            rep.add("lufs_range", not bad, f"{vals}", f"LUFS 범위 [{lo},{hi}] 밖: {[pathlib.Path(b).name for b in bad]}",
                    "ffmpeg loudnorm 으로 라우드니스를 맞춘다")
    if loop:
        seams = {}
        for f, m in measures.items():
            seams[pathlib.Path(f).name] = seam(m["_samples"], m["sample_rate"])
        bad = [k for k, v in seams.items() if v is None or not v["ok"]]
        rep.add("loop", not bad, json.dumps(seams, ensure_ascii=False),
                f"루프 이음매 문제: {bad}", "sound.looping 을 다시 호출하거나 preserve 구간을 조정한다")
        rep.extra["seams"] = seams

    rep.extra["measurements"] = {pathlib.Path(f).name: {k: v for k, v in m.items() if not k.startswith("_")}
                                 for f, m in measures.items()}
    sys.exit(rep.emit(args.out))


if __name__ == "__main__":
    main()
