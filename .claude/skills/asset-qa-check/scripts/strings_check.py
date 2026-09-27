#!/usr/bin/env python3
"""현지화 문자열 검사: data/strings/{lang}.json 을 원문 ko.json 과 대조한다(계약서 4-4~4-6절).

사용법
  strings_check.py --game-dir games/x --langs en ja --id l10n_en_ja
  strings_check.py --game-dir games/x --langs en --allow-dryrun      # 드라이런: 미번역 자리표시를 실패로 세지 않음

검사
  lang_coverage   원문 키가 대상 언어 파일에 모두 있는가(빈 문자열도 누락)
  placeholders    {name} 자리표시자가 원문과 같은 집합인가
  max_len_ok      ui_strings.csv 의 max_len 을 넘지 않는가(글자 수 기준)
  translated      한국어 원문이 그대로 남거나 드라이런·TODO 표시가 남지 않았는가
  glossary        용어집에 대상 언어 표기가 있는 용어가 원문에 나오면 번역에도 그 표기가 있는가
  source_sync     ko.json 이 dialogue.csv·ui_strings.csv 의 키를 모두 담는가
"""
import argparse
import csv
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from qa_common import Report  # noqa: E402

PH = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")
HANGUL = re.compile(r"[가-힣]")
RESIDUE = re.compile(r"dry-?run|\bTODO\b|\[untranslated\]|<translate|^\[[a-z]{2}\] ", re.I)  # "[en] 원문" 은 translate_table.py 의 드라이런 표시


def read_csv(p):
    if not p.exists():
        return None
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_json(p):
    d = json.loads(p.read_text(encoding="utf-8"))
    return {k: v for k, v in d.items() if not k.startswith("_")}, d.get("_meta", {})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game-dir", required=True)
    ap.add_argument("--langs", nargs="+", required=True)
    ap.add_argument("--source", default="ko")
    ap.add_argument("--id", default="l10n")
    ap.add_argument("--allow-dryrun", action="store_true")
    ap.add_argument("--out")
    args = ap.parse_args()

    g = pathlib.Path(args.game_dir)
    sdir = g / "data" / "strings"
    rep = Report(args.id, mode="dry-run" if args.allow_dryrun else "live")
    src_path = sdir / f"{args.source}.json"
    if not src_path.exists():
        rep.add("source_exists", False, str(src_path), f"원문 파일 없음: {src_path}", "원문 ko.json 을 먼저 만든다")
        sys.exit(rep.emit(args.out))
    src, _ = load_json(src_path)

    ui = read_csv(g / "data" / "ui_strings.csv") or []
    dia = read_csv(g / "data" / "dialogue.csv") or []
    max_len = {r["string_id"]: int(r["max_len"]) for r in ui if (r.get("max_len") or "").strip().isdigit()}
    expected = {r["string_id"] for r in ui} | {r["line_id"] for r in dia}
    if expected:
        lack = sorted(expected - set(src))
        rep.add("source_sync", not lack, f"원문 키 {len(src)} / 데이터 키 {len(expected)}",
                f"ko.json 에 없는 키 {len(lack)}개: {lack[:10]}", "dialogue.csv·ui_strings.csv 로 ko.json 을 다시 만든다")
    else:
        rep.add("source_sync", None, "dialogue.csv·ui_strings.csv 없음")

    voiced_ph = [r["line_id"] for r in dia if r.get("voice", "none") not in ("none", "") and PH.search(r.get("text_ko", ""))]
    if voiced_ph:   # 기획 규칙: 음성이 있는 대사에는 자리표시자를 쓰지 않는다(녹음본과 자막이 달라진다)
        rep.issues.append(f"정보: 음성이 있는 대사에 자리표시자가 있다(game-narrative 규칙 위반): {voiced_ph[:10]}")

    gloss = read_csv(g / "data" / "glossary.csv") or []
    stats = {}
    for lang in args.langs:
        p = sdir / f"{lang}.json"
        if not p.exists():
            rep.add(f"{lang}:exists", False, str(p), f"{lang}.json 없음", "해당 언어를 번역한다")
            continue
        try:
            tgt, meta = load_json(p)
        except json.JSONDecodeError as e:
            rep.add(f"{lang}:json", False, str(e), f"{lang}.json 형식 오류", "JSON 을 다시 쓴다")
            continue
        missing = [k for k in src if not str(tgt.get(k, "")).strip()]
        extra = [k for k in tgt if k not in src]
        rep.add(f"{lang}:lang_coverage", not missing, f"{len(src) - len(missing)}/{len(src)}",
                f"{lang} 누락 {len(missing)}개: {missing[:10]}", "누락 키만 다시 번역한다")
        ph_bad = [k for k in src if k in tgt and set(PH.findall(src[k])) != set(PH.findall(str(tgt[k])))]
        rep.add(f"{lang}:placeholders", not ph_bad, f"불일치 {len(ph_bad)}",
                f"{lang} 자리표시자 불일치: {ph_bad[:10]}", "자리표시자를 보호한 뒤 다시 번역한다")
        untrans = {k for k in src if k in tgt and HANGUL.search(str(tgt[k]))} if lang != args.source else set()
        residue = {k for k in tgt if RESIDUE.search(str(tgt[k]))}
        # 드라이런이면 미번역 키는 번역 품질 검사(글자 수·용어집)에서 뺀다. 원문을 그대로 재는 것은 의미가 없다.
        skip = (untrans | residue) if args.allow_dryrun else set()
        too_long = [f"{k}({len(str(tgt[k]))}>{n})" for k, n in max_len.items()
                    if k in tgt and k not in skip and len(str(tgt[k])) > n]
        rep.add(f"{lang}:max_len_ok", not too_long, f"초과 {len(too_long)}",
                f"{lang} UI 글자 수 초과: {too_long[:10]}", "짧은 표현으로 다시 번역하고 ux-designer 에 알린다")
        if lang != args.source:
            bad = sorted(untrans | residue)
            if args.allow_dryrun:
                rep.add(f"{lang}:translated", None, f"드라이런 — 미번역 {len(untrans)}, 자리표시 {len(residue)}")
            else:
                rep.add(f"{lang}:translated", not bad, f"미번역 {len(untrans)}, 자리표시 {len(residue)}",
                        f"{lang} 미번역·자리표시 잔존: {bad[:10]}", "해당 키를 실제로 번역한다")
        col = f"term_{lang}"
        if gloss and col in gloss[0]:
            gl_bad = []
            for row in gloss:
                ko_t, tg_t = (row.get("term_ko") or "").strip(), (row.get(col) or "").strip()
                if not ko_t or not tg_t:
                    continue
                for k, v in src.items():
                    if k in skip:
                        continue
                    if ko_t in v and k in tgt and tg_t.lower() not in str(tgt[k]).lower():
                        gl_bad.append(f"{k}:{ko_t}→{tg_t}")
            rep.add(f"{lang}:glossary", not gl_bad, f"불일치 {len(gl_bad)}", f"{lang} 용어집 불일치: {gl_bad[:10]}",
                    "용어집 표기로 고친다")
        stats[lang] = {"keys": len(tgt), "missing": len(missing), "extra": len(extra), "meta": meta}
    rep.extra["stats"] = stats
    sys.exit(rep.emit(args.out))


if __name__ == "__main__":
    main()
