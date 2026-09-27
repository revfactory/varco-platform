"""에셋 QA 스크립트 공통 도우미: 계약서 7-1 절의 QA 결과 JSON 을 만든다.

형식
  {"id", "verdict": pass|fail|cannot_verify, "mode", "checks": [{name, result: pass|fail|skip, detail}],
   "issues": [...], "retryable": bool, "fix_hint": str, ...추가 필드}
"""
import json
import pathlib
import sys


class Report:
    def __init__(self, asset_id, mode="live"):
        self.id = asset_id
        self.mode = mode
        self.checks = []
        self.issues = []
        self.hints = []
        self.extra = {}
        self.unverifiable = []

    def add(self, name, ok, detail="", issue=None, hint=None):
        """ok: True(통과) / False(실패) / None(검사 안 함)."""
        result = "skip" if ok is None else ("pass" if ok else "fail")
        self.checks.append({"name": name, "result": result, "detail": detail})
        if ok is False:
            if issue:
                self.issues.append(issue)
            if hint and hint not in self.hints:
                self.hints.append(hint)
        return ok

    def cannot_verify(self, reason):
        """검사 도구나 입력이 없어 판단할 수 없는 경우. 통과로 세지 않는다."""
        self.unverifiable.append(reason)
        self.issues.append(f"검증 불가: {reason}")

    def to_dict(self, retryable=None):
        failed = [c for c in self.checks if c["result"] == "fail"]
        if failed:
            verdict = "fail"
        elif self.unverifiable or not any(c["result"] == "pass" for c in self.checks):
            verdict = "cannot_verify"
        else:
            verdict = "pass"
        d = {"id": self.id, "verdict": verdict, "mode": self.mode, "checks": self.checks, "issues": self.issues,
             "retryable": bool(failed) if retryable is None else retryable,
             "fix_hint": " / ".join(self.hints)}
        d.update(self.extra)
        return d

    def emit(self, out=None, retryable=None):
        d = self.to_dict(retryable)
        text = json.dumps(d, ensure_ascii=False, indent=2)
        if out:
            p = pathlib.Path(out)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text + "\n", encoding="utf-8")
        print(text)
        return 0 if d["verdict"] == "pass" else 1


def load_acceptance(raw=None, path=None):
    """--acceptance JSON 문자열 또는 --acceptance-file 경로에서 기준을 읽는다. null 값은 버린다."""
    data = {}
    if path:
        data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    elif raw:
        data = json.loads(raw)
    return {k: v for k, v in (data or {}).items() if v is not None}


def load_asset(manifest_path, asset_id):
    m = json.loads(pathlib.Path(manifest_path).read_text(encoding="utf-8"))
    for a in m.get("assets", []):
        if a.get("id") == asset_id:
            return m, a
    sys.exit(f"매니페스트에 id={asset_id} 가 없다: {manifest_path}")


def expected_outputs(asset, game_dir):
    """매니페스트 output 규칙으로 최종 결과 파일 경로 목록을 만든다(계약서 5·6절)."""
    out = asset.get("output") or {}
    base_dir = pathlib.Path(game_dir) / out.get("dir", "")
    fmt = out.get("format", "")
    basename = out.get("basename", asset.get("id", ""))
    files = []
    lines = asset.get("lines")
    if lines and "{line_id}" in basename:
        files = [base_dir / f"{basename.replace('{line_id}', lid)}.{fmt}" for lid in lines]
        for ex in out.get("extra", []) or []:
            ex_dir = pathlib.Path(game_dir) / ex.get("dir", "")
            files += [ex_dir / f"{ex.get('basename', '{line_id}').replace('{line_id}', lid)}.{ex.get('format', '')}"
                      for lid in lines]
        return files
    count = int(out.get("count", 1) or 1)
    if count == 1:
        files = [base_dir / f"{basename}.{fmt}"]
    else:
        files = [base_dir / f"{basename}_{i:02d}.{fmt}" for i in range(1, count + 1)]
    for ex in out.get("extra", []) or []:
        ex_dir = pathlib.Path(game_dir) / ex.get("dir", "")
        files.append(ex_dir / f"{ex.get('basename', basename)}.{ex.get('format', '')}")
    return files
