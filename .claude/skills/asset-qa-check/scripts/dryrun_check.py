#!/usr/bin/env python3
"""드라이런 요청 명세 검사: 에셋 하나의 {파일}.dryrun.json 들이 매니페스트와 VARCO 명세에 맞는지 확인한다.

사용법
  dryrun_check.py --manifest games/x/manifest.json --id sfx_door --game-dir games/x \
      --ledger _workspace/x/varco_ledger.jsonl [--out _workspace/x/03_assetqa_sfx_door.json]

명세 파일 찾기: 장부에서 asset_id 가 같은 드라이런 기록의 outputs 를 먼저 쓰고, 장부가 없으면
매니페스트 output.dir 아래의 *.dryrun.json 중 basename 이 맞는 파일을 찾는다.

검사
  specs_found      명세가 하나 이상 있는가
  spec_params      명세마다 varco_catalog.validate_params 통과(필수값·허용값·범위·글자/바이트 한도·파일 형식)
  steps_covered    매니페스트 steps 의 API 마다 명세가 있는가. 묶음 대사(lines)나 calls 가 있으면 그 개수만큼
  api_in_manifest  매니페스트에 없는 API 를 부르지 않았는가(승인 범위 밖 호출 방지)
  output_location  마지막 step 명세의 intended_output 이 매니페스트 output.dir 아래인가
  ledger_ok        장부의 드라이런 기록이 모두 ok 인가
"""
import argparse
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[2] / "varco-api" / "scripts"))
from qa_common import Report, load_asset  # noqa: E402
from varco_catalog import APIS, MANUAL_APIS, validate_params  # noqa: E402

NUM = re.compile(r"^-?\d+(\.\d+)?$")


def spec_to_params(spec):
    """명세 body 를 validate_params 입력으로 되돌린다. 파일·base64 자리는 files 로, multipart 숫자 문자열은 숫자로."""
    params, files = {}, {}
    for k, v in (spec.get("body") or {}).items():
        if isinstance(v, str) and (v.startswith("<base64 ") or v.startswith("<file ")):
            m = re.search(r"from (.+)>$", v)
            files[k] = m.group(1) if m else "unknown"
        elif isinstance(v, str) and NUM.match(v):
            params[k] = float(v) if "." in v else int(v)
        elif isinstance(v, str) and v[:1] in "{[":
            try:
                params[k] = json.loads(v)
            except json.JSONDecodeError:
                params[k] = v
        else:
            params[k] = v
    return params, files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--game-dir", required=True)
    ap.add_argument("--ledger")
    ap.add_argument("--out")
    args = ap.parse_args()

    _, asset = load_asset(args.manifest, args.id)
    game = pathlib.Path(args.game_dir)
    rep = Report(args.id, mode="dry-run")
    out = asset.get("output") or {}
    out_dir = (game / out.get("dir", "")).resolve()

    spec_paths, ledger_rows = [], []
    if args.ledger and pathlib.Path(args.ledger).exists():
        for line in pathlib.Path(args.ledger).read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("asset_id") == args.id and r.get("mode") == "dry-run" and r.get("type") != "reserve":
                ledger_rows.append(r)
                spec_paths += [p for p in r.get("outputs", []) if p.endswith(".dryrun.json")]
    if not spec_paths and out_dir.exists():
        stem = out.get("basename", args.id).replace("{line_id}", "")
        spec_paths = [str(p) for p in out_dir.rglob("*.dryrun.json") if stem in p.name or not stem]

    specs = []
    for sp in dict.fromkeys(spec_paths):
        p = pathlib.Path(sp)
        if not p.is_absolute() and not p.exists():
            p = pathlib.Path.cwd() / sp
        try:
            specs.append((sp, json.loads(p.read_text(encoding="utf-8"))))
        except (OSError, json.JSONDecodeError) as e:
            rep.add(f"read:{pathlib.Path(sp).name}", False, str(e), f"명세를 읽을 수 없다: {sp}", "다시 드라이런한다")
    rep.add("specs_found", bool(specs), f"{len(specs)}개", "드라이런 명세가 하나도 없다",
            "varco_client.py call ... --dry-run --ledger ... --asset-id 로 명세를 만든다")
    if not specs:
        sys.exit(rep.emit(args.out))

    param_bad = []
    for sp, spec in specs:
        api = spec.get("api")
        if api not in APIS:
            param_bad.append(f"{pathlib.Path(sp).name}: 알 수 없는 API {api}")
            continue
        params, files = spec_to_params(spec)
        for prob in validate_params(api, params, files):
            param_bad.append(f"{pathlib.Path(sp).name}: {prob}")
    rep.add("spec_params", not param_bad, f"문제 {len(param_bad)}", f"명세 파라미터 문제: {param_bad[:10]}",
            "validate 로 확인하며 파라미터를 고쳐 다시 드라이런한다")

    steps = [s for s in asset.get("steps", []) if s.get("api") not in MANUAL_APIS]
    manifest_apis = {s["api"] for s in steps}
    lines = asset.get("lines") or []
    counts = {}
    for _, spec in specs:
        counts[spec.get("api")] = counts.get(spec.get("api"), 0) + 1
    short = []
    for s in steps:
        need = int(s.get("calls") or (len(lines) if lines else 1))
        have = counts.get(s["api"], 0)
        if have < need:
            short.append(f"{s['api']} {have}/{need}")
    rep.add("steps_covered", not short, json.dumps(counts, ensure_ascii=False), f"명세가 모자란 step: {short}",
            "빠진 step(또는 대사 줄)의 드라이런을 만든다")
    extra = sorted(set(counts) - manifest_apis)
    rep.add("api_in_manifest", not extra, f"매니페스트 API {sorted(manifest_apis)}",
            f"매니페스트에 없는 API 호출: {extra}", "승인된 steps 의 API 만 부른다")

    if steps:
        last_api = steps[-1]["api"]
        outside = []
        for sp, spec in specs:
            if spec.get("api") != last_api:
                continue
            target = pathlib.Path(spec.get("intended_output", ""))
            target = (target if target.is_absolute() else pathlib.Path.cwd() / target).resolve()
            extras = [(game / e.get("dir", "")).resolve() for e in (out.get("extra") or [])]
            if not any(str(target).startswith(str(d)) for d in [out_dir, *extras]):
                outside.append(spec.get("intended_output"))
        rep.add("output_location", not outside, str(out_dir.relative_to(pathlib.Path.cwd().resolve()))
                if str(out_dir).startswith(str(pathlib.Path.cwd().resolve())) else str(out_dir),
                f"최종 결과 경로가 output.dir 밖: {outside[:5]}", "--out 을 매니페스트 output 위치로 맞춘다")
    if ledger_rows:
        bad = [r.get("api") for r in ledger_rows if not r.get("ok")]
        rep.add("ledger_ok", not bad, f"기록 {len(ledger_rows)}건", f"장부의 실패한 드라이런: {bad}",
                "실패한 호출의 problems 를 읽고 고친다")
    else:
        rep.add("ledger_ok", None, "장부 기록 없음(파일 탐색으로 대체)")
    rep.extra["specs"] = [sp for sp, _ in specs]
    sys.exit(rep.emit(args.out))


if __name__ == "__main__":
    main()
