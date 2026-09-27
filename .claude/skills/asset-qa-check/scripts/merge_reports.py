#!/usr/bin/env python3
"""여러 검사 스크립트의 결과를 에셋 하나의 QA 결과(계약서 7-1)로 합친다.

사용법
  merge_reports.py /tmp/a.json /tmp/b.json --id vo_ch1_intro --mode live --out _workspace/x/03_assetqa_vo_ch1_intro.json

합치는 규칙: checks·issues 를 이어 붙이고(검사 이름 앞에 원래 스크립트의 id 를 붙인다), 하나라도 fail 이면 fail,
fail 은 없지만 cannot_verify 가 있으면 cannot_verify, 모두 통과해야 pass. retryable 은 fail 이 있는 보고서들이
모두 retryable 일 때만 true 다(하나라도 담당이 고칠 수 없는 실패면 재작업해도 소용없다).
"""
import argparse
import json
import pathlib
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reports", nargs="+")
    ap.add_argument("--id", required=True)
    ap.add_argument("--mode", default="live")
    ap.add_argument("--retryable", choices=["auto", "true", "false"], default="auto")
    ap.add_argument("--out")
    args = ap.parse_args()
    checks, issues, hints, verdicts, retry = [], [], [], [], []
    for path in args.reports:
        d = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        src = d.get("id", pathlib.Path(path).stem)
        for c in d.get("checks", []):
            checks.append(dict(c, name=f"{src}/{c['name']}"))
        issues += d.get("issues", [])
        if d.get("fix_hint"):
            hints.append(d["fix_hint"])
        verdicts.append(d.get("verdict"))
        if d.get("verdict") == "fail":
            retry.append(bool(d.get("retryable")))
    verdict = "fail" if "fail" in verdicts else ("cannot_verify" if "cannot_verify" in verdicts or not verdicts else "pass")
    retryable = (all(retry) and bool(retry)) if args.retryable == "auto" else args.retryable == "true"
    out = {"id": args.id, "verdict": verdict, "mode": args.mode, "checks": checks, "issues": issues,
           "retryable": retryable if verdict == "fail" else False, "fix_hint": " / ".join(hints),
           "sources": args.reports}
    text = json.dumps(out, ensure_ascii=False, indent=2)
    if args.out:
        pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    sys.exit(0 if verdict == "pass" else 1)


if __name__ == "__main__":
    main()
