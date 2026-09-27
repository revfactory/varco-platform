#!/usr/bin/env python3
"""게임 문자열을 VARCO Translate(mt.translate)로 번역해 data/strings/{lang}.json 을 만든다(계약서 4-6).

문자열마다 varco_client.py 를 subprocess 로 불러 장부·예산·드라이런 규칙을 지킨다.
번역 전에 자리표시자({player_name})와 용어집 용어를 토큰(⟦P0⟧, ⟦G1⟧)으로 바꾸고, 번역 뒤 되돌린다.
용어집: do_not_translate=y 면 원문 그대로 보호하고, 아니면 term_{lang} 열 값을 강제 번역어로 쓴다(열이 없으면 경고).
번역기가 자리표시자를 옮기거나 용어를 제멋대로 바꾸면 게임에서 문자열이 깨지기 때문이다.

사용법
  translate_table.py --run-meta _workspace/{slug}/run_meta.json --id l10n_en        # 매니페스트 에셋 기준
  translate_table.py --run-meta ... --lang ja [--only ui.menu.start,ch1_intro_002] [--refresh]
  translate_table.py --run-meta ... --lang en --source-csv marketing/copy.csv --out marketing/copy_en.json
      # 게임 문자열 대신 임의 CSV(string_id,text_ko[,max_len,context]) 번역. 마케팅 문구용

  --dry-run 이거나 run_meta.varco_mode 가 live 가 아니면 호출하지 않고 "[{lang}] 원문" 자리표시로 파일 구조를 만든다.
  번역 API 는 단가 미공개라 실제 호출에는 --allow-unknown-price(또는 run_meta.allow_unknown_price=true)가 필요하다.

출력
  data/strings/ko.json(원문), data/strings/{lang}.json, 보고서 _workspace/{slug}/03_l10n_{lang}_report.json,
  호출 원본 _workspace/{slug}/03_l10n_raw/{lang}/{id}.json(실제 호출 결과는 캐시로 다시 쓴다),
  표준 출력에 워크플로 PRODUCE 스키마 형태의 요약 JSON
"""
import argparse
import csv
import json
import pathlib
import re
import subprocess
import sys

CLIENT = pathlib.Path(__file__).resolve().parents[2] / "varco-api" / "scripts" / "varco_client.py"
API_LANGS = {"ko", "en", "ja", "tw", "cn", "de", "ru", "es", "pt", "fr"}
STOP = {3: "budget_blocked", 4: "auth_failed", 10: "auth_failed", 11: "credit_exhausted"}
PH_RE = re.compile(r"\{([a-z0-9_]+)\}")
TOKEN_RE = re.compile(r"⟦\s*([PG])\s*(\d+)\s*⟧")


def read_csv(path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def collect_game_strings(game_dir):
    rows = []
    for d in read_csv(game_dir / "data" / "dialogue.csv"):
        rows.append({"id": d["line_id"], "text": d["text_ko"], "max_len": None, "kind": "dialogue",
                     "context": f"{d.get('speaker_id', '')} / {d.get('direction', '')}"})
    for u in read_csv(game_dir / "data" / "ui_strings.csv"):
        ml = (u.get("max_len") or "").strip()
        rows.append({"id": u["string_id"], "text": u["text_ko"], "max_len": int(ml) if ml.isdigit() else None,
                     "kind": "ui", "context": u.get("context", "")})
    return rows


def protect(text, glossary, lang):
    """자리표시자와 용어를 토큰으로 바꾼다. 되돌릴 값 목록을 함께 돌려준다."""
    restore = {}
    n = 0

    def ph(m):
        nonlocal n
        tok = f"⟦P{n}⟧"
        restore[("P", n)] = m.group(0)
        n += 1
        return tok

    text = PH_RE.sub(ph, text)
    # 긴 용어부터 바꿔야 짧은 용어가 긴 용어 일부를 먼저 먹지 않는다
    for i, g in enumerate(sorted(glossary, key=lambda g: -len(g["term_ko"]))):
        term = g["term_ko"]
        if not term or term not in text:
            continue
        if (g.get("do_not_translate") or "").lower() == "y":
            target = term                                  # 번역하지 않을 말은 원문 그대로 보호한다
        else:
            target = (g.get(f"term_{lang}") or "").strip()  # 대상 언어 지정 번역어가 있으면 강제한다
        if not target:
            continue      # 지정 번역어가 없으면 번역기에 맡긴다
        tok = f"⟦G{i}⟧"
        restore[("G", i)] = target
        text = text.replace(term, tok)
    return text, restore


def unprotect(text, restore):
    found = set()

    def back(m):
        key = (m.group(1), int(m.group(2)))
        found.add(key)
        return restore.get(key, m.group(0))

    out = TOKEN_RE.sub(back, text)
    lost = [restore[k] for k in restore if k not in found]
    return out, lost


def visible_len(text):
    return len(PH_RE.sub("00", text))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-meta", required=True)
    ap.add_argument("--id", help="매니페스트 현지화 에셋 id (예: l10n_en)")
    ap.add_argument("--lang", help="대상 언어 API 코드(en, ja, tw, cn, de, ru, es, pt, fr)")
    ap.add_argument("--provider", help="chat | content (기본: 에셋 params 또는 content)")
    ap.add_argument("--only", help="이 id 들만 다시 번역(쉼표)")
    ap.add_argument("--refresh", action="store_true", help="캐시를 무시하고 다시 호출")
    ap.add_argument("--source-csv", help="게임 문자열 대신 번역할 CSV")
    ap.add_argument("--out", help="--source-csv 결과 JSON 경로")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-unknown-price", action="store_true")
    a = ap.parse_args()

    meta_path = pathlib.Path(a.run_meta)
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    slug = meta["slug"]
    workspace = meta_path.parent
    game_dir = workspace.parent.parent / "games" / slug
    src_lang = meta.get("source_lang", "ko")
    dry = a.dry_run or meta.get("varco_mode") != "live"
    allow_unknown = a.allow_unknown_price or bool(meta.get("allow_unknown_price"))
    ledger = workspace / "varco_ledger.jsonl"

    lang, provider, asset_id = a.lang, a.provider, a.id
    if a.id:
        m = json.loads((game_dir / "manifest.json").read_text(encoding="utf-8"))
        asset = next((x for x in m["assets"] if x["id"] == a.id), None)
        if not asset:
            print(json.dumps({"id": a.id, "status": "failed", "outputs": [], "calls": 0, "notes": "매니페스트에 없는 id",
                              "error": "asset not found"}, ensure_ascii=False))
            return
        p = (asset.get("steps") or [{}])[0].get("params", {})
        lang = lang or p.get("target_lang")
        provider = provider or p.get("provider")
    provider = provider or "content"
    asset_id = asset_id or f"l10n_{lang}"
    if lang not in API_LANGS or lang == src_lang:
        print(json.dumps({"id": asset_id, "status": "failed", "outputs": [], "calls": 0,
                          "notes": f"대상 언어 '{lang}' 가 API 코드가 아니거나 원문 언어와 같다", "error": "bad lang"},
                         ensure_ascii=False))
        return

    if a.source_csv:
        rows = [{"id": r["string_id"], "text": r["text_ko"], "kind": "custom",
                 "max_len": int(r["max_len"]) if (r.get("max_len") or "").isdigit() else None,
                 "context": r.get("context", "")} for r in read_csv(pathlib.Path(a.source_csv))]
        out_path = pathlib.Path(a.out or pathlib.Path(a.source_csv).with_name(f"{pathlib.Path(a.source_csv).stem}_{lang}.json"))
    else:
        rows = collect_game_strings(game_dir)
        out_path = game_dir / "data" / "strings" / f"{lang}.json"
        src_out = game_dir / "data" / "strings" / f"{src_lang}.json"
        src_out.parent.mkdir(parents=True, exist_ok=True)
        src_doc = {"_meta": {"lang": src_lang, "source": src_lang, "generated_by": "source", "reviewed": True}}
        src_doc.update({r["id"]: r["text"] for r in rows})
        src_out.write_text(json.dumps(src_doc, ensure_ascii=False, indent=2), encoding="utf-8")
    glossary = read_csv(game_dir / "data" / "glossary.csv")
    glossary_warning = None
    if glossary and f"term_{lang}" not in glossary[0]:
        glossary_warning = f"glossary.csv 에 term_{lang} 열이 없다. 지정 번역어 없이 번역기에 맡긴다(do_not_translate 보호는 적용)"

    existing = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {}
    only = set(a.only.split(",")) if a.only else None
    raw_dir = workspace / "03_l10n_raw" / lang
    raw_dir.mkdir(parents=True, exist_ok=True)
    result = {"_meta": {"lang": lang, "source": src_lang, "generated_by": "dry-run" if dry else "mt.translate",
                        "reviewed": False}}
    report = {"lang": lang, "total": len(rows), "translated": 0, "cached": 0, "failed": [], "placeholder_lost": [],
              "over_length": [], "dry_run": dry}
    calls, spent, unknown_calls, stop = 0, 0.0, 0, None

    for r in rows:
        sid = r["id"]
        if only is not None and sid not in only and sid in existing:
            result[sid] = existing[sid]
            continue
        protected, restore = protect(r["text"], glossary, lang)
        raw = raw_dir / f"{re.sub(r'[^A-Za-z0-9_.-]', '_', sid)}.json"
        target = None
        if dry:
            target = f"[{lang}] {protected}"
        elif raw.exists() and not a.refresh:
            try:
                target = json.loads(raw.read_text(encoding="utf-8")).get("target_text")
                report["cached"] += 1
            except json.JSONDecodeError:
                target = None
        if target is None or dry:
            params = {"TID": f"{slug}-{lang}-{sid}", "svc": "varco-translation", "provider": provider,
                      "source_lang": src_lang, "target_lang": lang, "source_text": protected}
            pfile = raw_dir / f"{raw.stem}.params.json"
            pfile.write_text(json.dumps(params, ensure_ascii=False), encoding="utf-8")
            cmd = [sys.executable, str(CLIENT), "call", "mt.translate", "--params", str(pfile), "--out", str(raw),
                   "--ledger", str(ledger), "--asset-id", asset_id]
            if dry:
                cmd.append("--dry-run")
            else:
                if meta.get("budget_credits") is not None:
                    cmd += ["--budget", str(meta["budget_credits"])]
                if allow_unknown:
                    cmd.append("--allow-unknown-price")
            calls += 1
            proc = subprocess.run(cmd, capture_output=True, text=True)
            try:
                res = json.loads(proc.stdout)
            except json.JSONDecodeError:
                res = {"error": (proc.stdout + proc.stderr)[-300:]}
            if proc.returncode in STOP:
                stop = (STOP[proc.returncode], res.get("error", ""))
                break
            if proc.returncode != 0:
                report["failed"].append({"id": sid, "error": res.get("error"), "problems": res.get("problems")})
                continue
            if not dry:
                if res.get("est_credits") is None:
                    unknown_calls += 1
                else:
                    spent += res["est_credits"]
                target = json.loads(raw.read_text(encoding="utf-8")).get("target_text")
            if not target:
                report["failed"].append({"id": sid, "error": "응답에 target_text 없음"})
                continue
        text, lost = unprotect(target, restore)
        if lost:
            report["placeholder_lost"].append({"id": sid, "lost": lost, "text": text})
        if set(PH_RE.findall(text)) != set(PH_RE.findall(r["text"])):
            report["placeholder_lost"].append({"id": sid, "expected": PH_RE.findall(r["text"]),
                                               "got": PH_RE.findall(text)})
        if not dry and r.get("max_len") and visible_len(text) > r["max_len"]:   # 드라이런은 접두사 때문에 길이가 무의미
            report["over_length"].append({"id": sid, "len": visible_len(text), "max_len": r["max_len"], "text": text})
        result[sid] = text
        report["translated"] += 1

    missing = [r["id"] for r in rows if r["id"] not in result]
    if missing:
        result["_meta"]["partial"] = True
    report.update(glossary_warning=glossary_warning, missing=missing, calls=calls, est_credits_spent=spent, unknown_price_calls=unknown_calls)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    rep_path = workspace / f"03_l10n_{lang}_report.json" if not a.source_csv else out_path.with_suffix(".report.json")
    rep_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    notes = [f"{report['translated']}/{len(rows)}개 번역(캐시 {report['cached']})",
             f"자리표시자·용어 손실 {len(report['placeholder_lost'])}건", f"글자 수 초과 {len(report['over_length'])}건"]
    if dry:
        notes.append("드라이런: '[언어] 원문' 자리표시로 채웠다")
    if glossary_warning:
        notes.append(glossary_warning)
    if unknown_calls:
        notes.append(f"단가 미공개 호출 {unknown_calls}건(추정 크레딧 합계에서 빠짐)")
    if stop:
        status, err = stop
    elif report["translated"] == 0:
        status, err = "failed", "번역된 문자열이 없다"
    else:
        status, err = ("dry-run" if dry else "generated"), ("; ".join(f["id"] for f in report["failed"])[:500])
    print(json.dumps({"id": asset_id, "status": status, "outputs": [str(out_path)] + ([] if a.source_csv else [str(src_out)]),
                      "calls": calls, "est_credits_spent": spent, "notes": "; ".join(notes),
                      "error": err, "report": str(rep_path)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
