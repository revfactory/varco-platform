#!/usr/bin/env python3
"""VARCO Sound 결과 후처리용 ffmpeg 래퍼.

Text to Sound 는 항상 10초 파일을 돌려준다. 짧은 효과음은 뒤쪽 무음을 잘라야 게임에서 바로 쓸 수 있다.
이 스크립트는 자르기·페이드·레벨 맞추기·모노 변환·측정·후보 비교를 같은 기준으로 처리한다.

사용법
  audio_post.py info a.wav [b.wav ...]                 # 길이·채널·샘플레이트·피크·유효 길이(JSON)
  audio_post.py trim in.wav out.wav [--threshold -50] [--keep-lead 0.005]
  audio_post.py fade in.wav out.wav [--in 0.005] [--out 0.05]
  audio_post.py normalize in.wav out.wav [--peak -1.0 | --lufs -18]
  audio_post.py mono in.wav out.wav
  audio_post.py sfx in.wav out.wav [--peak -1.0]       # trim → fade → normalize 를 한 번에(효과음 기본 처리)
  audio_post.py rank a.wav b.wav c.wav [--target-s 0.6] # 후보를 기준에 가깝고 클리핑 없는 순서로 정렬
  audio_post.py placeholder out.wav [--seconds 1.0] [--channels 1]   # 드라이런 체인용 무음 파일

모든 명령은 결과를 JSON 한 줄로 출력한다. ffmpeg/ffprobe 가 필요하다.
"""
import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import wave


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"명령 실패: {' '.join(cmd[:6])} … → {r.stderr.strip()[-400:]}")
    return r


def probe(path):
    r = run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
             "stream=channels,sample_rate:format=duration", "-of", "json", str(path)])
    d = json.loads(r.stdout)
    st = (d.get("streams") or [{}])[0]
    return {"duration_s": round(float(d.get("format", {}).get("duration", 0.0)), 3),
            "channels": int(st.get("channels", 0) or 0), "sample_rate": int(st.get("sample_rate", 0) or 0)}


def levels(path):
    """피크(dBFS)와 평균 음량(dB)을 volumedetect 로 잰다."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True)
    peak = re.search(r"max_volume:\s*(-?[\d.]+|-inf) dB", r.stderr)
    mean = re.search(r"mean_volume:\s*(-?[\d.]+|-inf) dB", r.stderr)
    to_f = lambda m: (float("-inf") if m.group(1) == "-inf" else float(m.group(1))) if m else None
    return to_f(peak), to_f(mean)


def active_duration(path, threshold_db=-50.0):
    """앞뒤 무음을 뺀 실제 소리 길이(초)."""
    with tempfile.TemporaryDirectory() as td:
        out = pathlib.Path(td) / "t.wav"
        trim_file(path, out, threshold_db, 0.0)
        return probe(out)["duration_s"]


def trim_file(src, dst, threshold_db=-50.0, keep_lead=0.005):
    # 앞 무음 제거 → 뒤집어서 다시 앞 무음 제거(=뒤 무음 제거) → 원래 방향
    f = (f"silenceremove=start_periods=1:start_threshold={threshold_db}dB:start_silence={keep_lead},"
         f"areverse,silenceremove=start_periods=1:start_threshold={threshold_db}dB:start_silence=0.02,areverse")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-af", f, str(dst)])


def cmd_info(a):
    rows = []
    for p in a.files:
        info = probe(p)
        peak, mean = levels(p)
        info.update(file=p, peak_dbfs=peak, mean_db=mean, active_s=active_duration(p, a.threshold))
        rows.append(info)
    print(json.dumps(rows if len(rows) > 1 else rows[0], ensure_ascii=False))


def cmd_trim(a):
    trim_file(a.src, a.dst, a.threshold, a.keep_lead)
    print(json.dumps({"ok": True, "out": a.dst, **probe(a.dst)}, ensure_ascii=False))


def fade_file(src, dst, fin, fout):
    dur = probe(src)["duration_s"]
    st = max(0.0, dur - fout)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
         "-af", f"afade=t=in:st=0:d={fin},afade=t=out:st={st:.3f}:d={fout}", str(dst)])


def cmd_fade(a):
    fade_file(a.src, a.dst, getattr(a, "in"), a.out)
    print(json.dumps({"ok": True, "out": a.dst, **probe(a.dst)}, ensure_ascii=False))


def normalize_file(src, dst, peak=None, lufs=None):
    if lufs is not None:
        # 환경음처럼 긴 소리는 체감 음량(LUFS)으로 맞춘다
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
             "-af", f"loudnorm=I={lufs}:TP=-1.5:LRA=11", "-ar", str(probe(src)["sample_rate"] or 44100), str(dst)])
        return {"mode": "lufs", "target": lufs}
    cur, _ = levels(src)
    if cur is None or cur == float("-inf"):
        shutil.copyfile(src, dst)
        return {"mode": "peak", "gain_db": 0.0, "note": "무음 파일"}
    gain = round(peak - cur, 2)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-af", f"volume={gain}dB", str(dst)])
    return {"mode": "peak", "gain_db": gain, "target": peak}


def cmd_normalize(a):
    info = normalize_file(a.src, a.dst, a.peak, a.lufs)
    peak, _ = levels(a.dst)
    print(json.dumps({"ok": True, "out": a.dst, "peak_dbfs": peak, **info}, ensure_ascii=False))


def cmd_mono(a):
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", a.src, "-ac", "1", a.dst])
    print(json.dumps({"ok": True, "out": a.dst, **probe(a.dst)}, ensure_ascii=False))


def cmd_sfx(a):
    with tempfile.TemporaryDirectory() as td:
        t1, t2 = pathlib.Path(td) / "1.wav", pathlib.Path(td) / "2.wav"
        trim_file(a.src, t1, a.threshold, 0.005)
        fade_file(t1, t2, 0.003, min(0.05, max(0.01, probe(t1)["duration_s"] * 0.1)))
        pathlib.Path(a.dst).parent.mkdir(parents=True, exist_ok=True)
        info = normalize_file(t2, a.dst, a.peak, None)
    peak, _ = levels(a.dst)
    print(json.dumps({"ok": True, "out": a.dst, "peak_dbfs": peak, **probe(a.dst), **info}, ensure_ascii=False))


def cmd_rank(a):
    rows = []
    for p in a.files:
        peak, _ = levels(p)
        act = active_duration(p, a.threshold)
        clip = peak is not None and peak > -0.1
        dist = abs(act - a.target_s) if a.target_s else 0.0
        rows.append({"file": p, "active_s": act, "peak_dbfs": peak, "clipping": clip, "distance": round(dist, 3)})
    rows.sort(key=lambda r: (r["clipping"], r["distance"], r["file"]))
    print(json.dumps({"ranked": rows, "best": rows[0]["file"] if rows else None}, ensure_ascii=False))


def cmd_placeholder(a):
    p = pathlib.Path(a.dst)
    p.parent.mkdir(parents=True, exist_ok=True)
    rate = 44100
    with wave.open(str(p), "wb") as w:
        w.setnchannels(a.channels)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x00\x00" * a.channels * int(rate * a.seconds))
    print(json.dumps({"ok": True, "out": str(p), "placeholder": True, "seconds": a.seconds}, ensure_ascii=False))


def main():
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print(json.dumps({"ok": False, "error": "ffmpeg/ffprobe 가 없다"}, ensure_ascii=False))
        sys.exit(2)
    ap = argparse.ArgumentParser(description="VARCO 사운드 후처리")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("info"); p.add_argument("files", nargs="+"); p.add_argument("--threshold", type=float, default=-50.0)
    p.set_defaults(f=cmd_info)
    p = sub.add_parser("trim"); p.add_argument("src"); p.add_argument("dst")
    p.add_argument("--threshold", type=float, default=-50.0); p.add_argument("--keep-lead", type=float, default=0.005)
    p.set_defaults(f=cmd_trim)
    p = sub.add_parser("fade"); p.add_argument("src"); p.add_argument("dst")
    p.add_argument("--in", type=float, default=0.005); p.add_argument("--out", type=float, default=0.05)
    p.set_defaults(f=cmd_fade)
    p = sub.add_parser("normalize"); p.add_argument("src"); p.add_argument("dst")
    g = p.add_mutually_exclusive_group(); g.add_argument("--peak", type=float, default=-1.0); g.add_argument("--lufs", type=float)
    p.set_defaults(f=cmd_normalize)
    p = sub.add_parser("mono"); p.add_argument("src"); p.add_argument("dst"); p.set_defaults(f=cmd_mono)
    p = sub.add_parser("sfx"); p.add_argument("src"); p.add_argument("dst")
    p.add_argument("--peak", type=float, default=-1.0); p.add_argument("--threshold", type=float, default=-50.0)
    p.set_defaults(f=cmd_sfx)
    p = sub.add_parser("rank"); p.add_argument("files", nargs="+"); p.add_argument("--target-s", type=float, default=0.0)
    p.add_argument("--threshold", type=float, default=-50.0); p.set_defaults(f=cmd_rank)
    p = sub.add_parser("placeholder"); p.add_argument("dst"); p.add_argument("--seconds", type=float, default=1.0)
    p.add_argument("--channels", type=int, default=1); p.set_defaults(f=cmd_placeholder)

    a = ap.parse_args()
    try:
        a.f(a)
    except (RuntimeError, OSError, ValueError) as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
