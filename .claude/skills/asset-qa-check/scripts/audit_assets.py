#!/usr/bin/env python3
"""5단계 에셋 전수 감사: 매니페스트 ↔ 실제 파일 ↔ 코드 참조를 세 방향으로 대조한다.

사용법
  audit_assets.py --game-dir games/x [--engine web|unity] [--out _workspace/x/05_assetqa_audit.json] [--md games/x/qa/reports/asset-audit.md]

코드 위치: web 은 games/x/web/(vendor/ 제외), unity 는 games/x/unity/Assets/(Plugins/·ThirdParty/ 제외)
참조 찾기: 문자열 안의 'assets/…확장자' 와 'marketing/…확장자'. `${…}`, `{…}`, `" +` 처럼 조립하는 경로는
앞부분(접두사)을 동적 참조로 보고, 그 접두사로 시작하는 파일은 쓰이는 것으로 친다.
코드가 manifest.json 을 읽으면 매니페스트의 모든 결과물을 쓰이는 것으로 친다.

검사
  code_refs_exist     코드가 가리키는 정적 경로의 파일이 모두 있는가(없으면 실행 중 로드 실패) → 실패
  p0_files_exist      P0 에셋의 결과 파일이 모두 있는가(드라이런이면 명세 파일로 대신) → 실패
  status_consistent   매니페스트 status 가 실제와 맞는가(qa_passed 인데 파일 없음 등) → 실패
  all_files_exist     P1·P2 결과 파일 누락 → 실패로 표시하되 출시 판정은 디렉터가 한다
  unused_files        만들었는데 아무도 쓰지 않는 파일 → 정보(검사 결과는 통과, issues 에 목록)
"""
import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from qa_common import Report, expected_outputs  # noqa: E402

EXT = r"(?:wav|mp3|ogg|flac|glb|gltf|png|jpg|jpeg|webp|json)"
STATIC = re.compile(r"""["'`]([^"'`\n]*?((?:assets|marketing)/[^"'`\n]*?\.""" + EXT + r"""))["'`]""")
# Unity Resources.Load 처럼 확장자 없이 쓰는 경로(엔진이 unity 일 때만 쓴다)
BARE = re.compile(r"""["'`]([^"'`\n]*?((?:assets|marketing)/[A-Za-z0-9_./-]+?))["'`]""")
DYNAMIC = re.compile(r"""["'`]([^"'`\n]*?((?:assets|marketing)/[^"'`\n]*?))(?:\$\{|\{|["'`]\s*\+)""")
CODE_EXT = {".js", ".mjs", ".ts", ".html", ".css", ".json", ".cs", ".txt", ".uxml", ".asset"}
SKIP_DIRS = {"vendor", "node_modules", "Plugins", "ThirdParty", "Library", "Temp", "Packages"}
IGNORE_SUFFIX = (".dryrun.json", ".meta.json", ".request.json", ".meta")


def code_files(root):
    if not root.exists():
        return []
    return [p for p in root.rglob("*") if p.is_file() and p.suffix in CODE_EXT
            and not any(part in SKIP_DIRS for part in p.relative_to(root).parts)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game-dir", required=True)
    ap.add_argument("--engine", choices=["web", "unity"])
    ap.add_argument("--out")
    ap.add_argument("--md")
    args = ap.parse_args()
    game = pathlib.Path(args.game_dir)
    rep = Report("asset_audit")

    mpath = game / "manifest.json"
    if not mpath.exists():
        rep.add("manifest_exists", False, str(mpath), "매니페스트가 없다", "2단계 승인본을 복사한다")
        sys.exit(rep.emit(args.out))
    m = json.loads(mpath.read_text(encoding="utf-8"))
    dry = m.get("varco_mode") == "dry-run"
    rep.mode = "dry-run" if dry else "live"
    engine = args.engine or ("unity" if (game / "unity").exists() and not (game / "web").exists() else "web")
    code_root = game / ("unity/Assets" if engine == "unity" else "web")

    # 1) 실제 파일
    actual = set()
    for sub in ("assets", "marketing"):
        d = game / sub
        if d.exists():
            actual |= {p.relative_to(game).as_posix() for p in d.rglob("*")
                       if p.is_file() and not p.name.endswith(IGNORE_SUFFIX) and not p.name.startswith(".")}

    # 2) 코드 참조
    static, dynamic, manifest_loader = {}, set(), False
    files = code_files(code_root)
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        if "manifest.json" in text:
            manifest_loader = True
        for i, line in enumerate(text.splitlines(), 1):
            for mt in STATIC.finditer(line):
                if "{" in mt.group(2):        # `${id}` 처럼 조립하는 경로는 정적 참조가 아니다
                    continue
                static.setdefault(mt.group(2), []).append(f"{f.relative_to(game).as_posix()}:{i}")
            for mt in DYNAMIC.finditer(line):
                dynamic.add(mt.group(2))
            if engine == "unity":
                for mt in BARE.finditer(line):
                    ref = mt.group(2)
                    if "." in pathlib.PurePosixPath(ref).name or ref.endswith("/"):
                        continue
                    hit = next((a for a in actual if a.rsplit(".", 1)[0] == ref), None)
                    static.setdefault(hit or ref + ".*", []).append(f"{f.relative_to(game).as_posix()}:{i}")
    rep.add("code_scanned", bool(files), f"{engine}: 코드 파일 {len(files)}개, 정적 참조 {len(static)}, 동적 접두사 {len(dynamic)}",
            f"코드 폴더가 비었거나 없다: {code_root}", "4단계 산출물 위치를 확인한다")

    manual_files = set()
    for a in m.get("assets", []):
        if a.get("status") == "manual_pending":
            manual_files |= {p.relative_to(game).as_posix() for p in expected_outputs(a, game)}
    broken = {p: locs for p, locs in static.items() if p not in actual}
    rep.add("code_refs_exist", not broken, f"깨진 참조 {len(broken)}(수동 제작 대기 {len(set(broken) & manual_files)})",
            "코드가 가리키는데 없는 파일: " + "; ".join(
                f"{p}{' (수동 제작 대기)' if p in manual_files else ''} ← {locs[0]}" for p, locs in list(broken.items())[:10]),
            "파일을 만들거나 코드 경로를 매니페스트 output 규칙에 맞춘다(자리표시 대체가 있는지도 확인)")

    # 3) 매니페스트 기대 파일과 상태
    p0_missing, other_missing, status_bad, expected_all = [], [], [], set()
    for a in m.get("assets", []):
        if a.get("status") == "skipped":
            continue
        exp = [p.relative_to(game).as_posix() for p in expected_outputs(a, game)]
        expected_all |= set(exp)
        have = [e for e in exp if e in actual]
        spec = [e for e in exp if (game / (e + ".dryrun.json")).exists()]
        missing = [e for e in exp if e not in actual and not (dry and (game / (e + ".dryrun.json")).exists())]
        manual = a.get("status") == "manual_pending"
        if missing and not manual:
            (p0_missing if a.get("priority") == "P0" else other_missing).append(f"{a['id']}: {missing[:3]}")
        st = a.get("status")
        if st in ("qa_passed", "generated") and len(have) < len(exp):
            status_bad.append(f"{a['id']} status={st} 인데 파일 {len(have)}/{len(exp)}")
        if st == "dry-run" and not spec and not have:
            status_bad.append(f"{a['id']} status=dry-run 인데 명세 파일 없음")
        if st in ("planned", "failed", "qa_failed", "budget_blocked", "halted") and have:
            status_bad.append(f"{a['id']} status={st} 인데 파일 {len(have)}개 존재(상태 갱신 누락?)")
    rep.add("p0_files_exist", not p0_missing, f"P0 누락 {len(p0_missing)}", f"P0 결과 누락: {p0_missing[:10]}",
            "해당 에셋만 3단계를 다시 돌린다")
    rep.add("status_consistent", not status_bad, f"불일치 {len(status_bad)}", f"상태 불일치: {status_bad[:10]}",
            "리더가 매니페스트 status 를 실제에 맞게 고친다")
    rep.add("all_files_exist", not other_missing, f"P1·P2 누락 {len(other_missing)}",
            f"P1·P2 결과 누락: {other_missing[:10]}", "출시 판정에서 디렉터가 허용 여부를 정한다")

    # 4) 안 쓰이는 파일
    def used(path):
        return (path in static or any(path.startswith(d) for d in dynamic)
                or (manifest_loader and path in expected_all))
    unused = sorted(p for p in actual if not used(p) and not p.startswith("marketing/"))
    rep.add("unused_files", True, f"미사용 {len(unused)}")
    if unused:
        rep.issues.append(f"정보: 코드에서 쓰지 않는 에셋 {len(unused)}개: {unused[:15]}")
    unlisted = sorted(p for p in actual if p not in expected_all)
    if unlisted:
        rep.issues.append(f"정보: 매니페스트에 없는 파일 {len(unlisted)}개(후보·중간 파일?): {unlisted[:15]}")

    rep.extra.update({"engine": engine, "manifest_loader": manifest_loader, "dynamic_prefixes": sorted(dynamic),
                      "broken_refs": broken, "unused": unused, "unlisted": unlisted})
    code = rep.emit(args.out)
    if args.md:
        d = rep.to_dict()
        lines = [f"# 에셋 전수 감사 — {m.get('game')}", "", f"- 판정: **{d['verdict']}** (모드 {d['mode']}, 엔진 {engine})",
                 "", "| 검사 | 결과 | 내용 |", "| --- | --- | --- |"]
        lines += [f"| {c['name']} | {c['result']} | {c['detail']} |" for c in d["checks"]]
        lines += ["", "## 문제와 정보", ""] + [f"- {i}" for i in d["issues"]] + ["", f"고칠 방향: {d['fix_hint'] or '-'}"]
        pathlib.Path(args.md).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(args.md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    sys.exit(code)


if __name__ == "__main__":
    main()
