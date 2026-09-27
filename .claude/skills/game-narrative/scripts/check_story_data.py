#!/usr/bin/env python3
"""캐릭터·대사·UI 문자열·용어집 CSV 가 산출물 계약서(4-2~4-5절)를 지키는지 검사한다.

사용법
  check_story_data.py --characters c.csv --dialogue d.csv --glossary g.csv --ui-strings u.csv
  check_story_data.py --game-dir games/{slug}        # data/ 아래 네 파일을 찾아 검사

결과는 JSON 으로 출력한다. errors 가 하나라도 있으면 종료 코드 1.
넘긴 파일만 검사한다. 대사의 speaker_id 대조는 --characters 를 함께 줄 때만 한다.
"""
import argparse
import csv
import json
import pathlib
import re
import sys

COLUMNS = {
    "characters": ["speaker_id", "name_ko", "role", "gender", "age_band", "personality", "voice_brief",
                   "voice_type", "face_anim"],
    "dialogue": ["line_id", "scene_id", "speaker_id", "text_ko", "emotion", "direction", "voice", "priority"],
    "ui_strings": ["string_id", "context", "text_ko", "max_len", "placeholders"],
    # 대상 언어 열(term_{lang})은 --langs 또는 run_meta.target_langs 로 정해진다(check_glossary_langs)
    "glossary": ["term_ko", "note", "do_not_translate"],
}
ENUMS = {
    ("characters", "gender"): {"male", "female", "none"},
    ("characters", "voice_type"): {"human", "creature", "none"},
    ("characters", "face_anim"): {"y", "n"},
    ("dialogue", "emotion"): {"neutral", "angry", "happy", "sad", "surprise"},
    ("dialogue", "voice"): {"tts", "acting", "creature", "none"},
    ("dialogue", "priority"): {"P0", "P1", "P2"},
    ("glossary", "do_not_translate"): {"y", "n", ""},
}
SNAKE = re.compile(r"^[a-z][a-z0-9_]*$")
LINE_ID = re.compile(r"^[a-z][a-z0-9_]*_\d{3}$")
STRING_ID = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$")
PLACEHOLDER = re.compile(r"\{([^{}]*)\}")
TTS_MAX_BYTES = 1200


def read_csv(path, kind, errors):
    p = pathlib.Path(path)
    if not p.is_file():
        errors.append(f"[{kind}] 파일이 없다: {path}")
        return None
    raw = p.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append(f"[{kind}] UTF-8 BOM 이 있다. BOM 없이 저장한다")
        raw = raw[3:]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        errors.append(f"[{kind}] UTF-8 이 아니다: {e}")
        return None
    reader = csv.DictReader(text.splitlines())
    header = reader.fieldnames or []
    expected = COLUMNS[kind]
    missing = [c for c in expected if c not in header]
    if missing:
        errors.append(f"[{kind}] 필수 열 누락: {missing}")
    if kind != "glossary":
        extra = [c for c in header if c not in expected]
        if extra:
            errors.append(f"[{kind}] 계약서에 없는 열: {extra}")
    elif not all(c in expected or re.match(r"^term_[a-z]{2}$", c) for c in header):
        errors.append(f"[{kind}] 계약서에 없는 열: {[c for c in header if c not in expected and not re.match(r'^term_[a-z]{2}$', c)]}")
    rows = list(reader)
    for i, r in enumerate(rows, 2):
        if None in r:
            errors.append(f"[{kind}] {i}행: 열 수가 머리글보다 많다(쉼표가 든 값을 큰따옴표로 감쌌는지 확인)")
    return rows


def check_enums(kind, rows, errors):
    for (k, col), allowed in ENUMS.items():
        if k != kind:
            continue
        for i, r in enumerate(rows, 2):
            v = (r.get(col) or "").strip()
            if v not in allowed:
                errors.append(f"[{kind}] {i}행 {col}={v!r}: 허용값 {sorted(a for a in allowed if a)}")


def placeholders(text):
    return PLACEHOLDER.findall(text or "")


def check_placeholder_format(kind, i, key, text, errors):
    for name in placeholders(text):
        if not SNAKE.match(name):
            errors.append(f"[{kind}] {i}행 {key}: 자리표시자 {{{name}}} 는 영문 snake_case 여야 한다")
    if text and (text.count("{") != text.count("}")):
        errors.append(f"[{kind}] {i}행 {key}: 중괄호 짝이 맞지 않는다")


def check_characters(rows, errors, warnings):
    ids = set()
    for i, r in enumerate(rows, 2):
        sid = (r.get("speaker_id") or "").strip()
        if not SNAKE.match(sid):
            errors.append(f"[characters] {i}행 speaker_id={sid!r}: 영문 snake_case 여야 한다")
        if sid in ids:
            errors.append(f"[characters] {i}행 speaker_id 중복: {sid}")
        ids.add(sid)
        if r.get("voice_type") in ("human", "creature") and len((r.get("voice_brief") or "").strip()) < 8:
            warnings.append(f"[characters] {sid}: voice_brief 가 너무 짧다. 성별·나이대·음높이·말 빠르기를 적는다")
    check_enums("characters", rows, errors)
    return {r.get("speaker_id", "").strip(): r for r in rows}


def check_dialogue(rows, chars, errors, warnings):
    seen = set()
    stats = {"lines": len(rows), "by_voice": {}, "p0_voiced": 0}
    for i, r in enumerate(rows, 2):
        lid = (r.get("line_id") or "").strip()
        scene = (r.get("scene_id") or "").strip()
        text = r.get("text_ko") or ""
        voice = (r.get("voice") or "").strip()
        stats["by_voice"][voice] = stats["by_voice"].get(voice, 0) + 1
        if voice != "none" and r.get("priority") == "P0":
            stats["p0_voiced"] += 1
        if not LINE_ID.match(lid):
            errors.append(f"[dialogue] {i}행 line_id={lid!r}: '{{scene_id}}_{{세 자리 순번}}' 형식이어야 한다")
        elif scene and not lid.startswith(scene + "_"):
            errors.append(f"[dialogue] {i}행 line_id={lid!r} 가 scene_id={scene!r} 로 시작하지 않는다")
        if lid in seen:
            errors.append(f"[dialogue] {i}행 line_id 중복: {lid}")
        seen.add(lid)
        if not SNAKE.match(scene):
            errors.append(f"[dialogue] {i}행 scene_id={scene!r}: 영문 snake_case 여야 한다")
        if not text.strip():
            errors.append(f"[dialogue] {i}행 {lid}: text_ko 가 비어 있다")
        nbytes = len(text.encode("utf-8"))
        if nbytes > TTS_MAX_BYTES:
            errors.append(f"[dialogue] {i}행 {lid}: {nbytes}바이트 > TTS 한도 {TTS_MAX_BYTES}바이트")
        elif voice != "none" and len(text) > 120:
            warnings.append(f"[dialogue] {lid}: {len(text)}자 — 음성 대사는 한 호흡(80자 안팎)으로 끊는 편이 안정적이다")
        check_placeholder_format("dialogue", i, lid, text, errors)
        if voice != "none" and placeholders(text):
            errors.append(f"[dialogue] {i}행 {lid}: 음성 대사에 자리표시자가 있다. 음성에는 값이 들어가지 않는다(voice=none 으로 두거나 문장을 바꾼다)")
        if chars is not None:
            sid = (r.get("speaker_id") or "").strip()
            if sid not in chars:
                errors.append(f"[dialogue] {i}행 {lid}: characters.csv 에 없는 speaker_id {sid!r}")
            else:
                vt = chars[sid].get("voice_type")
                if vt == "creature" and voice in ("tts", "acting"):
                    errors.append(f"[dialogue] {i}행 {lid}: 크리처 화자 {sid} 의 대사가 voice={voice}. creature 로 둔다")
                if vt == "human" and voice == "creature":
                    warnings.append(f"[dialogue] {lid}: 사람 화자 {sid} 의 대사가 voice=creature 다. 의도했는지 확인한다")
                if vt == "none" and voice != "none":
                    errors.append(f"[dialogue] {i}행 {lid}: voice_type=none 화자 {sid} 의 대사에 음성 방식 {voice}")
    check_enums("dialogue", rows, errors)
    return stats


def check_ui(rows, errors, warnings):
    seen = set()
    for i, r in enumerate(rows, 2):
        sid = (r.get("string_id") or "").strip()
        text = r.get("text_ko") or ""
        if not STRING_ID.match(sid):
            errors.append(f"[ui_strings] {i}행 string_id={sid!r}: 점으로 구분한 영문 키여야 한다(예: ui.menu.start)")
        if sid in seen:
            errors.append(f"[ui_strings] {i}행 string_id 중복: {sid}")
        seen.add(sid)
        if not text.strip():
            errors.append(f"[ui_strings] {i}행 {sid}: text_ko 가 비어 있다")
        if not (r.get("context") or "").strip():
            warnings.append(f"[ui_strings] {sid}: context 가 비어 있다. 번역자가 쓰임새를 알 수 없다")
        check_placeholder_format("ui_strings", i, sid, text, errors)
        declared = set((r.get("placeholders") or "").split())
        used = set(placeholders(text))
        if declared != used:
            errors.append(f"[ui_strings] {i}행 {sid}: placeholders 열 {sorted(declared)} 와 문구의 자리표시자 {sorted(used)} 가 다르다")
        ml = (r.get("max_len") or "").strip()
        if ml:
            if not ml.isdigit():
                errors.append(f"[ui_strings] {i}행 {sid}: max_len={ml!r} 는 정수이거나 빈칸이어야 한다")
            else:
                # 자리표시자는 실제 값 길이를 알 수 없어 이름을 뺀 길이로 센다
                visible = PLACEHOLDER.sub("", text)
                if len(visible) > int(ml):
                    errors.append(f"[ui_strings] {i}행 {sid}: {len(visible)}자 > max_len {ml}")
                elif len(visible) > int(ml) * 0.7:
                    warnings.append(f"[ui_strings] {sid}: 원문이 max_len 의 70% 를 넘는다({len(visible)}/{ml}). 번역하면 넘칠 수 있다")


def check_glossary(rows, errors, warnings, langs=None):
    seen = set()
    for i, r in enumerate(rows, 2):
        term = (r.get("term_ko") or "").strip()
        if not term:
            errors.append(f"[glossary] {i}행 term_ko 가 비어 있다")
        if term in seen:
            errors.append(f"[glossary] {i}행 term_ko 중복: {term}")
        seen.add(term)
        for col in r:
            if langs is not None and col and col[5:] not in langs:
                continue                  # 대상 언어가 아닌 열은 빈칸을 따지지 않는다
            if col and col.startswith("term_") and col != "term_ko" and not (r.get(col) or "").strip():
                warnings.append(f"[glossary] {term}: {col} 가 비어 있다")
    check_enums("glossary", rows, errors)


def target_langs(args):
    """대상 언어 목록: --langs → --run-meta → games/{slug} 옆 _workspace/{slug}/run_meta.json 순서로 찾는다."""
    if args.langs:
        return [x.strip() for x in args.langs.split(",") if x.strip()]
    candidates = []
    if args.run_meta:
        candidates.append(pathlib.Path(args.run_meta))
    if args.game_dir:
        g = pathlib.Path(args.game_dir).resolve()
        candidates.append(g.parent.parent / "_workspace" / g.name / "run_meta.json")
    for c in candidates:
        if c.is_file():
            try:
                return list(json.loads(c.read_text(encoding="utf-8")).get("target_langs", []))
            except (OSError, ValueError):
                pass
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--characters")
    ap.add_argument("--dialogue")
    ap.add_argument("--ui-strings")
    ap.add_argument("--glossary")
    ap.add_argument("--game-dir", help="games/{slug} — data/ 아래 네 파일을 찾아 검사")
    ap.add_argument("--langs", help="용어집에 있어야 할 대상 언어(쉼표 구분). 없으면 run_meta.target_langs 를 찾아 쓴다")
    ap.add_argument("--run-meta", help="run_meta.json 경로(대상 언어 확인용)")
    args = ap.parse_args()
    if args.game_dir:
        d = pathlib.Path(args.game_dir) / "data"
        args.characters = args.characters or str(d / "characters.csv")
        args.dialogue = args.dialogue or str(d / "dialogue.csv")
        args.ui_strings = args.ui_strings or str(d / "ui_strings.csv")
        args.glossary = args.glossary or str(d / "glossary.csv")
    if not any([args.characters, args.dialogue, args.ui_strings, args.glossary]):
        ap.error("검사할 파일을 하나 이상 넘긴다")

    errors, warnings, summary = [], [], {}
    chars = None
    if args.characters:
        rows = read_csv(args.characters, "characters", errors)
        if rows is not None:
            chars = check_characters(rows, errors, warnings)
            summary["characters"] = len(rows)
    if args.dialogue:
        rows = read_csv(args.dialogue, "dialogue", errors)
        if rows is not None:
            summary["dialogue"] = check_dialogue(rows, chars, errors, warnings)
            if chars is None:
                warnings.append("[dialogue] --characters 가 없어 speaker_id 대조를 건너뛰었다")
    if args.ui_strings:
        rows = read_csv(args.ui_strings, "ui_strings", errors)
        if rows is not None:
            check_ui(rows, errors, warnings)
            summary["ui_strings"] = len(rows)
    if args.glossary:
        rows = read_csv(args.glossary, "glossary", errors)
        langs = target_langs(args)
        if rows is not None and langs is not None:
            header = set(rows[0].keys()) if rows else set()
            for lang in langs:
                if header and f"term_{lang}" not in header:
                    errors.append(f"[glossary] 대상 언어 열 누락: term_{lang}")
            for col in sorted(c for c in header if c and c.startswith("term_") and c != "term_ko"):
                if col[5:] not in langs:
                    warnings.append(f"[glossary] {col} 는 대상 언어({langs})가 아니다. 쓰지 않을 열이면 지운다")
        elif langs is None:
            warnings.append("[glossary] 대상 언어를 알 수 없어 term_{lang} 열 대조를 건너뛰었다(--langs 또는 --run-meta)")
        if rows is not None:
            check_glossary(rows, errors, warnings, langs)
            summary["glossary"] = len(rows)

    print(json.dumps({"ok": not errors, "summary": summary, "errors": errors, "warnings": warnings},
                     ensure_ascii=False, indent=2))
    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()
