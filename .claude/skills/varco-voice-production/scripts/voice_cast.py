#!/usr/bin/env python3
"""캐릭터별 VARCO 화자를 정해 _workspace/{slug}/03_voice_casting.json 에 기록한다.

3단계 워크플로에서는 voice-director 여러 명이 장면별 에셋을 동시에 만든다. 각자 화자를 고르면 같은 캐릭터가
장면마다 다른 목소리가 된다. 그래서 캐스팅은 이 스크립트 하나로 하고, 결과 파일이 있으면 모두 그대로 쓴다.
파일 잠금으로 동시에 실행돼도 한 번만 기록하고, 같은 입력이면 항상 같은 화자를 고르도록 점수 규칙을 고정했다.

사용법
  voice_cast.py --run-meta _workspace/{slug}/run_meta.json [--model tts.standard] [--acting] [--force]
    --acting : voice=acting 대사가 있는 화자는 vc.acting 화자도 정한다
    --force  : 기존 캐스팅을 덮는다. 리더가 캐스팅 변경을 승인했을 때만 쓴다

드라이런이거나 키가 없어 화자 목록을 받을 수 없으면 uuid 자리에 "<speaker_uuid:{speaker_id}>" 를 넣고
placeholder=true 로 표시한다. 실제 호출 전에 --force 없이 다시 실행하면 자리표시만 실제 화자로 바꾼다.
"""
import argparse
import csv
import datetime as dt
import fcntl
import json
import pathlib
import re
import subprocess
import sys
import zlib

CLIENT = pathlib.Path(__file__).resolve().parents[2] / "varco-api" / "scripts" / "varco_client.py"
VOICE_LIST_API = {"tts.standard": "voices.tts_standard", "tts.lite": "voices.tts_lite", "vc.acting": "voices.vc_acting",
                  "vc.convert": "voices.vc"}
EMOTION_KO = {"중립": "neutral", "분노": "angry", "화남": "angry", "행복": "happy", "기쁨": "happy",
              "슬픔": "sad", "놀람": "surprise"}
GENDER_KO = {"male": "남성", "female": "여성"}
AGE_WORDS = {"child": ["아동", "어린이", "소년", "소녀"], "10s": ["소년", "소녀", "청소년", "아동"],
             "20s": ["청년", "20대"], "30s": ["청년", "30대", "중년"], "40s": ["중년", "40대"],
             "50s": ["중년", "장년", "50대"], "60s": ["노년", "60대"], "old": ["노년"]}
SYNONYM = {"낮은": "저음", "낮고": "저음", "낮게": "저음", "중저음": "저음", "굵은": "저음", "높은": "고음", "높고": "고음", "하이톤": "고음",
           "거친": "거침", "거칠고": "거침", "차분한": "차분", "차분하고": "차분", "밝은": "밝음", "밝고": "밝음",
           "부드러운": "부드러움", "건조한": "건조", "건조하고": "건조", "거만한": "거만", "냉소적인": "냉소"}


def read_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def tokens(text):
    out = set()
    for t in re.split(r"[\s,./·()]+", text or ""):
        if not t:
            continue
        out.add(SYNONYM.get(t, t))
        out.add(t)
    return out


def base_and_emotion(name):
    m = re.match(r"^(.*?)\s*\(([^)]+)\)\s*$", name or "")
    if m:
        return m.group(1).strip(), EMOTION_KO.get(m.group(2).strip(), m.group(2).strip())
    return (name or "").strip(), "neutral"


def gender_mismatch(char, voice):
    g = GENDER_KO.get((char.get("gender") or "").lower())
    desc = voice.get("description") or ""
    return bool(g) and g not in desc and ("남성" in desc or "여성" in desc)


def score(char, voice):
    desc = voice.get("description") or ""
    dtoks = tokens(desc)
    s = 0
    g = GENDER_KO.get((char.get("gender") or "").lower())
    if g:
        if g in desc:
            s += 3
        elif ("남성" in desc or "여성" in desc):
            s -= 5
    for w in AGE_WORDS.get((char.get("age_band") or "").lower(), []):
        if w in desc:
            s += 2
            break
    s += len(tokens(char.get("voice_brief", "")) & dtoks)
    s += len(tokens(char.get("personality", "")) & dtoks) * 0.5
    return s


def group_voices(voices):
    groups = {}
    for v in voices:
        uuid = v.get("speaker_uuid") or v.get("uuid") or v.get("id")
        if not uuid:
            continue
        base, emo = base_and_emotion(v.get("speaker_name", ""))
        g = groups.setdefault(base, {"speaker_name": base, "variants": {}, "description": v.get("description", "")})
        g["variants"].setdefault(emo, uuid)
        if emo == "neutral":
            g["description"] = v.get("description", g["description"])
    return groups


def fetch_list(model, workspace, ledger, dry_run):
    key = VOICE_LIST_API[model]
    path = workspace / f"voices_{key.split('.', 1)[1]}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8")), str(path)
    if dry_run:
        return None, None
    r = subprocess.run([sys.executable, str(CLIENT), "call", key, "--out", str(path), "--ledger", str(ledger)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{key} 목록 조회 실패(종료 코드 {r.returncode}): {r.stdout.strip()[-300:]}")
    return json.loads(path.read_text(encoding="utf-8")), str(path)


def cast_model(model, speakers, chars, line_counts, existing, workspace, ledger, dry_run, force):
    table = {} if force else dict(existing.get(model, {}))
    voices, src = fetch_list(model, workspace, ledger, dry_run)
    groups = group_voices(voices) if voices else {}
    used = {v.get("speaker_name") for v in table.values() if not v.get("placeholder")}
    # 사람 화자를 대사가 많은 순서로 먼저 고른다(주인공이 가장 잘 맞는 화자를 가져가게).
    # 크리처는 Conversion 으로 음색을 바꿀 가이드 음성일 뿐이라 마지막에 고르고, 다른 캐릭터와 화자가 겹쳐도 된다.
    is_creature = lambda s: (chars[s].get("voice_type") or "").lower() == "creature"
    for sid in sorted(speakers, key=lambda s: (is_creature(s), -line_counts.get(s, 0), s)):
        cur = table.get(sid)
        if cur and not cur.get("placeholder"):
            continue
        if cur and cur.get("placeholder") and not groups:
            continue
        ch = chars[sid]
        seed = zlib.crc32(sid.encode()) % 100000
        if not groups:
            ph = f"<speaker_uuid:{sid}>"
            table[sid] = {"speaker_name": None, "default": ph, "by_emotion": {}, "description": None,
                          "seed": seed, "properties": {"speed": 1.0, "pitch": 1.0}, "placeholder": True,
                          "reason": "드라이런이거나 화자 목록이 없어 자리표시로 둔다"}
            continue
        ranked = sorted(groups.values(), key=lambda g: (-score(ch, g), g["speaker_name"]))
        creature = is_creature(sid)
        # 1순위: 아직 안 쓴 화자 중 성별이 맞는 화자 → 2순위: 성별이 맞는 화자 재사용 → 마지막: 최고점
        pick = next((g for g in ranked if (creature or g["speaker_name"] not in used) and not gender_mismatch(ch, g)),
                    None)
        reused = False
        if pick is None:
            pick = next((g for g in ranked if not gender_mismatch(ch, g)), ranked[0])
            reused = True
        if not creature:
            used.add(pick["speaker_name"])
        variants = pick["variants"]
        table[sid] = {"speaker_name": pick["speaker_name"],
                      "default": variants.get("neutral") or next(iter(variants.values())),
                      "by_emotion": variants, "description": pick["description"], "score": score(ch, pick),
                      "seed": seed, "properties": {"speed": 1.0, "pitch": 1.0}, "placeholder": False,
                      "reason": f"voice_brief '{ch.get('voice_brief', '')}' ↔ '{pick['description']}'"
                                + (" (다른 캐릭터와 화자 겹침 — 확인 필요)" if reused else "")
                                + (" (크리처 가이드 음성)" if creature else "")}
    return table, src


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-meta", required=True)
    ap.add_argument("--model", default="tts.standard", choices=["tts.standard", "tts.lite"])
    ap.add_argument("--acting", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="run_meta 와 관계없이 화자 목록을 조회하지 않는다")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    meta = json.loads(pathlib.Path(a.run_meta).read_text(encoding="utf-8"))
    slug = meta["slug"]
    workspace = pathlib.Path(a.run_meta).parent
    game_dir = workspace.parent.parent / "games" / slug
    ledger = workspace / "varco_ledger.jsonl"
    dry_run = a.dry_run or meta.get("varco_mode") != "live"
    chars = {c["speaker_id"]: c for c in read_csv(game_dir / "data" / "characters.csv")}
    dialogue = read_csv(game_dir / "data" / "dialogue.csv")
    need, acting, counts = set(), set(), {}
    for d in dialogue:
        v = (d.get("voice") or "none").strip()
        if v in ("tts", "acting", "creature") and d["speaker_id"] in chars:
            need.add(d["speaker_id"])
            counts[d["speaker_id"]] = counts.get(d["speaker_id"], 0) + 1
            if v == "acting":
                acting.add(d["speaker_id"])

    out = workspace / "03_voice_casting.json"
    lock = pathlib.Path(str(out) + ".lock")
    with lock.open("w") as lh:
        fcntl.flock(lh, fcntl.LOCK_EX)
        existing = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
        result = dict(existing)
        sources = {}
        try:
            result[a.model], sources[a.model] = cast_model(a.model, need, chars, counts, existing, workspace, ledger,
                                                            dry_run, a.force)
            if a.acting and acting:
                result["vc.acting"], sources["vc.acting"] = cast_model("vc.acting", acting, chars, counts, existing,
                                                                        workspace, ledger, dry_run, a.force)
        except RuntimeError as e:
            print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
            sys.exit(1)
        placeholders = sorted(f"{m}:{s}" for m, t in result.items() if not m.startswith("_")
                              for s, v in t.items() if v.get("placeholder"))
        result["_meta"] = {"updated": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
                           "method": "auto-score", "voice_lists": sources, "placeholders": placeholders,
                           "note": "이 파일이 있으면 모든 voice-director 가 그대로 쓴다. 바꾸려면 리더 승인 후 --force"}
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        fcntl.flock(lh, fcntl.LOCK_UN)
    print(json.dumps({"ok": True, "casting": str(out), "speakers": sorted(need), "acting_speakers": sorted(acting),
                      "placeholders": placeholders,
                      "picked": {s: v.get("speaker_name") for s, v in result[a.model].items()}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
