#!/usr/bin/env python3
"""dialogue.csv + characters.csv 에서 음성 에셋 초안을 만든다(계약서 5절 '대사 음성은 장면 단위로 묶는다').

대사 한 줄마다 에셋을 만들면 3단계 워크플로의 에이전트 호출이 대사 수만큼 늘어난다.
그래서 같은 장면(scene_id)·같은 제작 방식의 대사를 한 에셋으로 묶고, 20줄을 넘으면 나눈다.

규칙
  voice=tts      → voice_line 에셋 vo_{scene}        : tts.standard (+ face.blendshape)
  voice=acting   → voice_line 에셋 vo_{scene}_acting : tts.standard → vc.acting (+ face.blendshape)
  voice=creature → creature_voice 에셋 crv_{scene}   : tts.standard(가이드) + sound.text2sound(참조음) → sound.conversion
  voice=none     → 만들지 않는다
  face.blendshape 는 화자의 characters.face_anim=y 인 줄에만 적용한다(step 의 "when": "speaker_face_anim").

사용법
  draft_voice_assets.py --game-dir games/{slug} [--voice-lang korean] [--model tts.standard] [--out drafts.json]

출력은 매니페스트 assets 배열에 그대로 붙일 수 있는 JSON 배열이다. 화자 uuid(voice, speaker_uuid)는 비워 둔다.
voice-director 가 캐스팅하며 채운다. 요약은 표준 오류로 출력한다.
"""
import argparse
import csv
import json
import pathlib
import re
import sys

MAX_LINES = 20
LANG_CODE = {"korean": "ko", "english": "en", "japanese": "ja", "taiwanese": "tw"}
PRIO = {"P0": 0, "P1": 1, "P2": 2}
FACE_EMOTIONS = {"neutral", "angry", "happy", "sad", "surprise"}


def read_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def snake(s):
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9_]", "_", s.lower())).strip("_")


def speech_seconds(text):
    # 한국어 대사 기준 대략 초당 7자 + 앞뒤 여백. 음성 변환 견적(10초 단위)에만 쓴다.
    return round(len(text) / 7.0 + 0.6, 1)


def chunks(rows):
    if len(rows) <= MAX_LINES:
        return [("", rows)]
    out = []
    for i in range(0, len(rows), MAX_LINES):
        out.append(("_" + "abcdefghijklmnopqrstuvwxyz"[i // MAX_LINES], rows[i:i + MAX_LINES]))
    return out


def best_priority(rows):
    return min((r.get("priority") or "P1" for r in rows), key=lambda p: PRIO.get(p, 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game-dir", required=True)
    ap.add_argument("--voice-lang", default="korean", choices=sorted(LANG_CODE))
    ap.add_argument("--model", default="tts.standard", choices=["tts.standard", "tts.lite"])
    ap.add_argument("--out")
    args = ap.parse_args()

    gd = pathlib.Path(args.game_dir)
    dialogue = read_csv(gd / "data" / "dialogue.csv")
    chars = {c["speaker_id"]: c for c in read_csv(gd / "data" / "characters.csv")}
    lang = args.voice_lang
    source_lang = lang == "korean"
    problems = []

    groups = {}
    order = []
    for r in dialogue:
        mode = (r.get("voice") or "none").strip()
        if mode == "none":
            continue
        if mode not in ("tts", "acting", "creature"):
            problems.append(f"{r['line_id']}: voice 값 '{mode}' 은 허용값이 아니다")
            continue
        if r["speaker_id"] not in chars:
            problems.append(f"{r['line_id']}: characters.csv 에 없는 speaker_id '{r['speaker_id']}'")
            continue
        if mode != "creature" and chars[r["speaker_id"]].get("voice_type") == "creature":
            mode = "creature"          # 화자가 크리처면 제작 방식도 크리처로 본다
        key = (r["scene_id"], mode)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(r)
        if r.get("emotion") not in FACE_EMOTIONS:
            problems.append(f"{r['line_id']}: emotion '{r.get('emotion')}' 은 Voice-to-Face 허용값이 아니다")
        if len(r["text_ko"].encode("utf-8")) > 1200:
            problems.append(f"{r['line_id']}: 1,200바이트를 넘어 TTS 한 번에 합성할 수 없다")
        if "{" in r["text_ko"]:
            problems.append(f"{r['line_id']}: 음성 대사에 자리표시자가 있다(규칙 위반). narrative 에 문장 수정을 요청한다 — 고치기 전에는 이 줄을 합성하지 않는다")

    assets = []
    for scene, mode in order:
        rows = groups[(scene, mode)]
        for suffix, part in chunks(rows):
            ids = [r["line_id"] for r in part]
            chars_per = [len(r["text_ko"]) for r in part]
            speakers = sorted({r["speaker_id"] for r in part})
            face_lines = [r["line_id"] for r in part if chars[r["speaker_id"]].get("face_anim", "n").lower() == "y"]
            tts_params = {"language": lang}
            tts_step = {"api": args.model, "params": tts_params, "calls": len(part), "per_call_chars": chars_per}
            if not source_lang:
                tts_step["text_source"] = f"data/strings/{LANG_CODE[lang]}.json"
            lang_dir = lang

            if mode == "creature":
                brief_voice = "; ".join(f"{s}: {chars[s].get('voice_brief', '')}" for s in speakers)
                asset = {
                    "id": f"crv_{snake(scene)}{suffix}",
                    "category": "creature_voice",
                    "owner": "sound-designer",
                    "phase": "production",
                    "priority": best_priority(part),
                    "source_ref": f"data/dialogue.csv:scene={scene}",
                    "brief": (f"장면 {scene} 크리처 음성 {len(part)}줄({', '.join(speakers)}). 가이드 음성을 TTS 로 만들고 "
                              f"크리처 참조음을 text2sound 로 한 번 만든 뒤 줄마다 Conversion 한다. 음색: {brief_voice}. "
                              f"사람이 녹음한 가이드가 있으면 inputs 에 넣고 step1 을 건너뛴다."),
                    "lines": ids,
                    "inputs": [],
                    "steps": [
                        tts_step,
                        {"api": "sound.text2sound", "params": {"prompt": f"creature vocal reference: {brief_voice}"[:200],
                                                                 "num_sample": 1, "version": "v2"}},
                        {"api": "sound.conversion", "input_from": {"source": "step1", "reference": "step2"},
                         "params": {"ratio": 1.0, "enhance": False}, "calls": len(part)},
                    ],
                    "output": {"dir": "assets/audio/creature", "basename": "{line_id}", "format": "wav", "count": len(part)},
                    "acceptance": {"duration_s": [0.2, 15.0], "peak_dbfs_max": -1.0},
                    "status": "planned",
                }
                assets.append(asset)
                continue

            steps = [tts_step]
            if mode == "acting":
                steps.append({"api": "vc.acting", "input_from": "previous", "params": {}, "calls": len(part),
                              "est_audio_seconds": max(speech_seconds(r["text_ko"]) for r in part)})
            output = {"dir": f"assets/audio/voice/{lang_dir}", "basename": "{line_id}", "format": "wav", "count": len(part)}
            if face_lines:
                steps.append({"api": "face.blendshape", "input_from": "previous", "when": "speaker_face_anim",
                              "params": {"fps": 30, "lip_style": "balanced", "face_style": "natural"},
                              "calls": len(face_lines)})
                face_dir = "assets/anim/face" if source_lang else f"assets/anim/face/{lang_dir}"
                output["extra"] = [{"dir": face_dir, "basename": "{line_id}", "format": "json", "count": len(face_lines),
                                    "lines": face_lines}]
            asset = {
                "id": f"vo_{snake(scene)}{'_acting' if mode == 'acting' else ''}{suffix}"
                      + ("" if source_lang else f"_{LANG_CODE[lang]}"),
                "category": "voice_line",
                "owner": "voice-director",
                "phase": "production",
                "priority": best_priority(part),
                "source_ref": f"data/dialogue.csv:scene={scene}",
                "brief": (f"장면 {scene} 대사 {len(part)}줄, 화자 {', '.join(speakers)}"
                          + (" — 연기 톤을 살리려고 VC Acting 을 거친다" if mode == "acting" else "")
                          + (f". 얼굴 애니메이션 {len(face_lines)}줄" if face_lines else "")
                          + ("" if source_lang else f". 원문이 아니라 번역 문자열({LANG_CODE[lang]}.json)을 읽으므로 현지화가 끝난 뒤 만든다")),
                "lines": ids,
                "inputs": [],
                "steps": steps,
                "output": output,
                "acceptance": {"duration_s": [0.3, 20.0], "peak_dbfs_max": -1.0},
                "status": "planned",
            }
            if not source_lang:
                asset["blocked_by"] = f"l10n_{LANG_CODE[lang]}"
            assets.append(asset)

    text = json.dumps(assets, ensure_ascii=False, indent=2)
    if args.out:
        pathlib.Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    lines_total = sum(len(a["lines"]) for a in assets)
    print(json.dumps({"assets": len(assets), "lines": lines_total,
                      "by_category": {c: sum(1 for a in assets if a["category"] == c) for c in {a["category"] for a in assets}},
                      "problems": problems}, ensure_ascii=False), file=sys.stderr)


if __name__ == "__main__":
    main()
