#!/usr/bin/env python3
"""코드 ↔ 데이터 계약 대조: 코드가 쓰는 문자열 키·대사 id·밸런스 열이 data 파일에 있는지, 밸런스 수치를 코드에 박았는지 찾는다.

사용법
  check_data_contracts.py --game-dir games/x [--engine web|unity] [--out _workspace/x/04_gameqa_contracts.json]

오류(errors, 종료 코드 1)
  - 코드가 쓰는 string_id 가 ui_strings.csv(또는 ko.json)에 없다
  - 코드가 쓰는 line_id 가 dialogue.csv 에 없다
경고(warnings) — 사람이 확인한다
  - 밸런스 표를 읽는 코드가 없다(표 이름이 코드에 안 나온다)
  - 밸런스 열이 코드 어디에도 안 나온다(기획 수치가 구현에 반영되지 않았을 수 있다)
  - 단위 접미사가 붙은 키(예: 'cooldown_s')를 코드가 쓰는데 어느 표에도 그런 열이 없다
  - 밸런스 CSV 의 값과 같은 숫자 리터럴이 코드에 있다(하드코딩 의심, 파일:줄)
  - 정의했지만 코드가 쓰지 않는 string_id

string_id 판별: 점으로 이은 소문자 키 중 첫 마디가 실제 string_id 의 첫 마디와 같은 것(예: ui.menu.start).
line_id 판별: `{scene_id}_{숫자}` 모양이면서 scene_id 가 dialogue.csv 에 있는 것.
코드에서 키를 조립하면(`'ui.menu.' + name`) 이 검사는 찾지 못한다. 그런 곳은 실행 테스트로 확인한다.
"""
import argparse
import csv
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "balance-simulation" / "scripts"))
try:  # 밸런스 표 형식 검사는 balance-simulation 스킬의 load_tables() 를 쓴다
    from check_balance_tables import load_tables
except ImportError:
    load_tables = None

CODE_EXT = {".js", ".mjs", ".ts", ".html", ".cs"}
SKIP_DIRS = {"vendor", "node_modules", "Plugins", "ThirdParty", "Library", "Temp", "Packages", "Tests"}
LIT = re.compile(r"""(["'`])((?:\\.|(?!\1)[^\\\n])*)\1""")
NUMLIT = re.compile(r"(?<![\w.$#])-?\d+(?:\.\d+)?(?![\w.])")
DOTTED = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z0-9_]+)+$")
LINE_ID = re.compile(r"^([a-z0-9]+(?:_[a-z0-9]+)*)_(\d{2,4})$")
UNIT_KEY = re.compile(r"^[a-z][a-z0-9_]*_(?:s|ms|pct|px|px_s|per_s|m|m_s|deg|hz)$")
TRIVIAL = {0, 1, 2, -1, 3, 4, 5, 10, 16, 20, 24, 30, 32, 45, 50, 60, 64, 90, 100, 128, 180, 255, 256, 360, 512,
           1000, 1024, 0.5, 0.25, 0.1, 1.5}


def read_csv(p):
    if not p.exists():
        return None
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def to_num(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return v
    try:
        return float(v) if "." in v else int(v)
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game-dir", required=True)
    ap.add_argument("--engine", choices=["web", "unity"])
    ap.add_argument("--out")
    args = ap.parse_args()
    game = pathlib.Path(args.game_dir)
    engine = args.engine or ("unity" if (game / "unity").exists() and not (game / "web").exists() else "web")
    root = game / ("unity/Assets" if engine == "unity" else "web")
    errors, warnings = [], []

    # 데이터 읽기
    ui = read_csv(game / "data" / "ui_strings.csv") or []
    dia = read_csv(game / "data" / "dialogue.csv") or []
    string_ids = {r["string_id"] for r in ui}
    ko = game / "data" / "strings" / "ko.json"
    if not string_ids and ko.exists():
        string_ids = {k for k in json.loads(ko.read_text(encoding="utf-8")) if "." in k and not k.startswith("_")}
    prefixes = {s.split(".")[0] for s in string_ids}
    line_ids = {r["line_id"] for r in dia}
    scenes = {r.get("scene_id") for r in dia}
    tables = {}
    bdir = game / "data" / "balance"
    for p in sorted(bdir.glob("*.csv")) if bdir.exists() else []:
        rows = read_csv(p) or []
        tables[p.stem] = {"columns": list(rows[0].keys()) if rows else [], "rows": rows}
    if tables and load_tables:
        try:
            typed = load_tables(str(bdir))
            for name, by_id in typed.items():      # {"enemies": {"slime": {"hp": 40, ...}}}
                if name in tables:
                    tables[name]["rows"] = [dict(r, id=rid) for rid, r in by_id.items()]
        except ValueError as e:
            warnings.append(f"밸런스 표 형식 검사 실패 — 원본 CSV 로 대조를 계속한다: {str(e)[:300]}")
    elif tables:
        warnings.append("check_balance_tables.py 를 불러오지 못해 원본 CSV 로만 대조한다")

    files = [p for p in root.rglob("*") if p.is_file() and p.suffix in CODE_EXT
             and not any(part in SKIP_DIRS for part in p.relative_to(root).parts)] if root.exists() else []
    if not files:
        warnings.append(f"코드 파일이 없다: {root}")

    used_strings, used_lines, literals, code_text = set(), set(), [], ""
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        code_text += "\n" + text
        rel = f.relative_to(game).as_posix()
        for i, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith(("//", "#", "*", "/*")):
                continue
            for mt in LIT.finditer(line):
                s = mt.group(2)
                literals.append((s, f"{rel}:{i}"))
                if DOTTED.match(s) and s.split(".")[0] in prefixes:
                    used_strings.add(s)
                    if s not in string_ids:
                        errors.append(f"없는 string_id '{s}' ← {rel}:{i}")
                lm = LINE_ID.match(s)
                if lm and lm.group(1) in scenes:
                    used_lines.add(s)
                    if s not in line_ids:
                        errors.append(f"없는 line_id '{s}' ← {rel}:{i}")
            for nm in NUMLIT.finditer(LIT.sub('""', line)):
                v = to_num(nm.group(0))
                if v is not None and v not in TRIVIAL:
                    literals.append((v, f"{rel}:{i}"))

    unused = sorted(string_ids - used_strings)
    if unused and files:
        warnings.append(f"코드가 쓰지 않는 string_id {len(unused)}개(조립 키일 수 있음): {unused[:10]}")

    all_cols = {c for t in tables.values() for c in t["columns"]}
    for name, t in tables.items():
        if name not in code_text:
            warnings.append(f"밸런스 표 '{name}' 을 읽는 코드가 보이지 않는다")
        missing = [c for c in t["columns"] if c != "id" and not re.search(rf"\b{re.escape(c)}\b", code_text)]
        if missing:
            warnings.append(f"'{name}' 열 중 코드에 안 나오는 것: {missing}")
    for s, loc in literals:
        if isinstance(s, str) and UNIT_KEY.match(s) and s not in all_cols:
            warnings.append(f"어느 밸런스 표에도 없는 열 이름 '{s}' ← {loc}")

    value_map = {}
    for name, t in tables.items():
        for r in t["rows"]:
            for c, v in r.items():
                if c == "id":
                    continue
                n = to_num(v)
                if n is not None and n not in TRIVIAL:
                    value_map.setdefault(n, set()).add(f"{name}.{c}")
    hard = [f"{v} ({', '.join(sorted(value_map[v]))}) ← {loc}" for v, loc in literals
            if not isinstance(v, str) and v in value_map]
    if hard:
        warnings.append(f"밸런스 값과 같은 숫자 리터럴 {len(hard)}곳(하드코딩 의심): {hard[:15]}")

    result = {"ok": not errors, "engine": engine, "code_files": len(files),
              "stats": {"string_ids": len(string_ids), "string_ids_used": len(used_strings), "line_ids": len(line_ids),
                        "line_ids_used": len(used_lines), "tables": {k: len(v['rows']) for k, v in tables.items()}},
              "errors": errors, "warnings": warnings}
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()
