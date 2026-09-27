#!/usr/bin/env python3
"""Unity Test Framework 결과(NUnit 3 XML)를 요약한다.

사용법
  unity_results.py _workspace/x/04_unity_editmode.xml [_workspace/x/04_unity_playmode.xml ...]

출력: 파일마다 total/passed/failed/skipped 와 실패한 테스트 이름·메시지(앞 300자). 실패가 있으면 종료 코드 1.
결과 파일이 없으면 테스트가 실행되지 못한 것이다(로그의 컴파일 오류·라이선스 오류를 확인한다).
"""
import json
import pathlib
import sys
import xml.etree.ElementTree as ET


def summarize(path):
    p = pathlib.Path(path)
    if not p.exists():
        return {"file": path, "ok": False, "error": "결과 파일 없음 — 테스트가 실행되지 않았다. -logFile 로그를 확인한다"}
    root = ET.parse(p).getroot()
    run = root if root.tag == "test-run" else root.find(".//test-run")
    attrs = run.attrib if run is not None else {}
    failed = []
    for case in root.iter("test-case"):
        if case.get("result") == "Failed":
            msg = case.find("./failure/message")
            failed.append({"name": case.get("fullname") or case.get("name"),
                           "message": (msg.text or "").strip()[:300] if msg is not None else ""})
    counts = {k: int(attrs.get(k, 0)) for k in ("total", "passed", "failed", "skipped")}
    return {"file": path, "ok": counts["failed"] == 0 and not failed and counts["total"] > 0, **counts, "failures": failed}


def main():
    results = [summarize(f) for f in sys.argv[1:]]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    sys.exit(0 if results and all(r["ok"] for r in results) else 1)


if __name__ == "__main__":
    main()
