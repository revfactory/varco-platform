#!/usr/bin/env python3
"""밸런스 CSV 가 _schema.json 과 산출물 계약서 4-1절을 지키는지 검사한다.

사용법
  check_balance_tables.py _workspace/{slug}/01_systems_balance
  check_balance_tables.py games/{slug}/data/balance --schema games/{slug}/data/balance/_schema.json

검사 항목: 스키마·CSV 짝, 첫 열 id, 열 이름 snake_case, 스키마 열 존재·초과 열, 타입(int·float·bool·string),
enum, min·max, 빈칸, id 형식·중복, UTF-8 BOM.
결과는 JSON 으로 출력한다. errors 가 하나라도 있으면 종료 코드 1.

다른 스크립트(시뮬레이션, QA 대조)는 load_tables() 로 타입이 맞춰진 표를 불러 쓴다.
    from check_balance_tables import load_tables
    tables = load_tables("games/x/data/balance")   # {"enemies": {"grunt": {"hp": 90, ...}}, ...}
"""
import argparse
import csv
import hashlib
import json
import pathlib
import re
import sys

SNAKE = re.compile(r"^[a-z][a-z0-9_]*$")
TYPES = {"string", "int", "float", "bool"}
BOOL_TRUE = {"true", "1", "y", "yes"}
BOOL_FALSE = {"false", "0", "n", "no"}


def convert(value, col_type):
    """문자열 값을 스키마 타입으로 바꾼다. 바꿀 수 없으면 ValueError."""
    v = value.strip()
    if col_type == "string":
        return v
    if col_type == "int":
        if not re.fullmatch(r"-?\d+", v):
            raise ValueError(f"정수가 아니다: {v!r}")
        return int(v)
    if col_type == "float":
        return float(v)
    if col_type == "bool":
        low = v.lower()
        if low in BOOL_TRUE:
            return True
        if low in BOOL_FALSE:
            return False
        raise ValueError(f"불리언이 아니다: {v!r} (true/false)")
    raise ValueError(f"알 수 없는 타입 {col_type}")


def file_hash(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()[:16]


def check(balance_dir, schema_path=None):
    """(errors, warnings, typed_tables, summary) 를 돌려준다."""
    d = pathlib.Path(balance_dir)
    schema_path = pathlib.Path(schema_path) if schema_path else d / "_schema.json"
    errors, warnings, tables, summary = [], [], {}, {"tables": {}, "hashes": {}}
    if not d.is_dir():
        return [f"폴더가 없다: {d}"], [], {}, summary
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"스키마가 없다: {schema_path}"], [], {}, summary
    except json.JSONDecodeError as e:
        return [f"스키마 JSON 오류: {e}"], [], {}, summary

    csvs = {p.stem: p for p in sorted(d.glob("*.csv"))}
    for name in schema:
        if name not in csvs:
            errors.append(f"[{name}] 스키마에는 있는데 {name}.csv 가 없다")
    for name in csvs:
        if name not in schema:
            errors.append(f"[{name}] {name}.csv 가 있는데 스키마에 정의가 없다")

    for name, path in csvs.items():
        spec = schema.get(name)
        if spec is None:
            continue
        cols = spec.get("columns", {})
        if not spec.get("description"):
            warnings.append(f"[{name}] 스키마에 description 이 없다")
        for cname, cdef in cols.items():
            if cdef.get("type") not in TYPES:
                errors.append(f"[{name}] 스키마 열 {cname}: type 은 {sorted(TYPES)} 중 하나여야 한다")
        raw = path.read_bytes()
        summary["hashes"][path.name] = file_hash(path)
        if raw.startswith(b"\xef\xbb\xbf"):
            errors.append(f"[{name}] UTF-8 BOM 이 있다. BOM 없이 저장한다")
            raw = raw[3:]
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as e:
            errors.append(f"[{name}] UTF-8 이 아니다: {e}")
            continue
        reader = csv.DictReader(text.splitlines())
        header = reader.fieldnames or []
        if not header or header[0] != "id":
            errors.append(f"[{name}] 첫 열은 id 여야 한다(현재: {header[:1]})")
        if "id" not in cols:
            errors.append(f"[{name}] 스키마에 id 열 정의가 없다")
        for h in header:
            if not SNAKE.match(h):
                errors.append(f"[{name}] 열 이름 {h!r} 는 영문 snake_case 여야 한다")
        missing = [c for c in cols if c not in header]
        extra = [h for h in header if h not in cols]
        if missing:
            errors.append(f"[{name}] 스키마 열이 CSV 에 없다: {missing}")
        if extra:
            errors.append(f"[{name}] 스키마에 없는 열: {extra}")
        typed, seen = {}, set()
        rows = list(reader)
        for i, r in enumerate(rows, 2):
            if None in r:
                errors.append(f"[{name}] {i}행: 열 수가 머리글보다 많다")
                continue
            rid = (r.get("id") or "").strip()
            if not SNAKE.match(rid):
                errors.append(f"[{name}] {i}행 id={rid!r}: 영문 snake_case 여야 한다")
            if rid in seen:
                errors.append(f"[{name}] {i}행 id 중복: {rid}")
            seen.add(rid)
            out = {}
            for cname, cdef in cols.items():
                if cname not in r:
                    continue
                val = r[cname]
                if val is None or val.strip() == "":
                    errors.append(f"[{name}] {i}행 {rid}.{cname}: 빈칸. 값이 없으면 기본값을 채운다")
                    continue
                try:
                    v = convert(val, cdef.get("type", "string"))
                except ValueError as e:
                    errors.append(f"[{name}] {i}행 {rid}.{cname}: {e}")
                    continue
                if "enum" in cdef and v not in cdef["enum"]:
                    errors.append(f"[{name}] {i}행 {rid}.{cname}={v!r}: 허용값 {cdef['enum']}")
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    if "min" in cdef and v < cdef["min"]:
                        errors.append(f"[{name}] {i}행 {rid}.{cname}={v}: 최소 {cdef['min']}")
                    if "max" in cdef and v > cdef["max"]:
                        errors.append(f"[{name}] {i}행 {rid}.{cname}={v}: 최대 {cdef['max']}")
                if cname.endswith("_pct") and isinstance(v, (int, float)) and not (0 <= v <= 100):
                    warnings.append(f"[{name}] {rid}.{cname}={v}: _pct 열은 0~100 으로 쓴다")
                out[cname] = v
            typed[rid] = out
        if not rows:
            errors.append(f"[{name}] 데이터 행이 없다")
        tables[name] = typed
        summary["tables"][name] = len(rows)
    return errors, warnings, tables, summary


def load_tables(balance_dir, schema_path=None):
    """검사를 통과한 표만 타입을 맞춰 돌려준다. 오류가 있으면 ValueError 를 던진다."""
    errors, _warnings, tables, _summary = check(balance_dir, schema_path)
    if errors:
        raise ValueError("밸런스 표 검사 실패:\n- " + "\n- ".join(errors))
    return tables


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("balance_dir")
    ap.add_argument("--schema", help="기본값: {balance_dir}/_schema.json")
    args = ap.parse_args()
    errors, warnings, _tables, summary = check(args.balance_dir, args.schema)
    print(json.dumps({"ok": not errors, "summary": summary, "errors": errors, "warnings": warnings},
                     ensure_ascii=False, indent=2))
    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()
