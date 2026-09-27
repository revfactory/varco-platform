#!/usr/bin/env python3
"""에셋 매니페스트가 산출물 계약서(varco-game-studio/references/contracts.md 5절)를 지키는지 검사한다.

사용법
  validate_manifest.py _workspace/{slug}/02_producer_manifest.json
  validate_manifest.py manifest.json --game-dir games/{slug}     # 대사·캐릭터와의 대조까지

결과는 JSON 으로 출력한다. errors 가 하나라도 있으면 종료 코드 1.
warnings 는 제작은 가능하지만 사람이 확인해야 할 항목이다.
"""
import argparse
import csv
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "varco-api" / "scripts"))
from varco_catalog import APIS, MANUAL_APIS, validate_params  # noqa: E402

CATEGORY = {
    "sfx": ("sfx_", "sound-designer", "assets/audio/sfx"),
    "ambience": ("amb_", "sound-designer", "assets/audio/ambience"),
    "creature_voice": ("crv_", "sound-designer", "assets/audio/creature"),
    "music": ("bgm_", "sound-designer", "assets/audio/music"),
    "voice_line": ("vo_", "voice-director", "assets/audio/voice"),
    "face_anim": ("face_", "voice-director", "assets/anim/face"),
    "model_3d": ("mdl_", "visual-artist", "assets/models"),
    "image": ("img_", "visual-artist", "assets/images"),
    "localization": ("l10n_", "localization-specialist", "data/strings"),
    "marketing": ("mkt_", "marketing-artist", "marketing"),
}
OWNERS = {"sound-designer", "voice-director", "visual-artist", "localization-specialist", "marketing-artist"}
STATUS = {"planned", "generated", "dry-run", "manual_pending", "qa_passed", "qa_failed", "failed",
          "budget_blocked", "halted", "skipped"}
ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
ALL_IDS = set()
PER_LINE = {"text", "id", "TID", "source_text"}   # 줄·문자열마다 제작 스크립트가 채우는 필드
CASTING = {"voice", "speaker_uuid"}   # voice-director 가 캐스팅하며 채우는 화자 필드
REQUIRED = ["id", "category", "owner", "phase", "priority", "source_ref", "brief", "steps", "output", "status"]


def check_asset(a, seen, errors, warnings):
    aid = a.get("id", "?")
    where = f"[{aid}]"
    for f in REQUIRED:
        if f not in a or a[f] in (None, "", []):
            errors.append(f"{where} 필수 필드 누락: {f}")
    if not ID_RE.match(str(aid)):
        errors.append(f"{where} id 는 영문 소문자 snake_case 여야 한다")
    if aid in seen:
        errors.append(f"{where} id 중복")
    seen.add(aid)
    cat = a.get("category")
    if cat not in CATEGORY:
        errors.append(f"{where} category 허용값 아님: {cat}")
        return
    prefix, owner, out_dir = CATEGORY[cat]
    if not str(aid).startswith(prefix):
        warnings.append(f"{where} {cat} 에셋 id 는 '{prefix}' 로 시작하는 것이 규칙이다")
    if a.get("owner") not in OWNERS:
        errors.append(f"{where} owner 허용값 아님: {a.get('owner')}")
    elif a.get("owner") != owner:
        warnings.append(f"{where} {cat} 의 기본 담당은 {owner} 인데 {a.get('owner')} 로 되어 있다")
    if a.get("phase") not in ("production", "release"):
        errors.append(f"{where} phase 는 production|release")
    if cat == "marketing" and a.get("phase") != "release":
        warnings.append(f"{where} 마케팅 에셋은 보통 phase=release 다")
    if a.get("priority") not in ("P0", "P1", "P2"):
        errors.append(f"{where} priority 는 P0|P1|P2")
    if a.get("status") not in STATUS:
        errors.append(f"{where} status 허용값 아님: {a.get('status')}")
    out = a.get("output") or {}
    if out and not str(out.get("dir", "")).startswith(out_dir.split("/")[0]):
        warnings.append(f"{where} output.dir '{out.get('dir')}' 가 규칙 위치 '{out_dir}' 와 다르다")
    for k in ("dir", "basename", "format"):
        if out and k not in out:
            errors.append(f"{where} output.{k} 누락")

    if cat == "voice_line":
        lines = a.get("lines")
        if lines is not None:
            if not isinstance(lines, list) or not lines:
                errors.append(f"{where} lines 는 비어 있지 않은 line_id 목록이어야 한다")
            elif len(lines) > 20:
                warnings.append(f"{where} 한 에셋에 대사 {len(lines)}줄 — 20줄 이하로 나누는 것이 규칙이다")
            elif out and "{line_id}" not in str(out.get("basename", "")):
                errors.append(f"{where} lines 를 쓰면 output.basename 은 '{{line_id}}' 여야 한다")

    steps = a.get("steps") or []
    for i, s in enumerate(steps, 1):
        api = s.get("api")
        tag = f"{where} step{i}({api})"
        if api in MANUAL_APIS:
            continue
        if api not in APIS:
            errors.append(f"{tag} 알 수 없는 API. varco_client.py catalog 로 확인")
            continue
        spec = APIS[api]
        # 매니페스트 단계에서는 파일 입력(base64·첨부)이 아직 없다. 파일 필드는 input_from 이나 inputs 로 채워진다고 보고 넘긴다.
        file_fields = set(spec.get("b64", [])) | set(spec.get("files", []))
        fake_files = {f: "placeholder.png" for f in file_fields}
        problems = [p for p in validate_params(api, s.get("params", {}), fake_files)
                    if not any(p.startswith(f"{f}:") for f in file_fields)]
        for p in problems:
            field = p.split(": ", 1)[-1] if p.startswith("필수 파라미터 누락") else None
            if field in PER_LINE and (a.get("lines") or cat == "localization"):
                continue                      # 묶음 대사·현지화 에셋: 줄·문자열마다 채운다
            if field in CASTING:
                warnings.append(f"{tag} {field} 는 보이스 캐스팅 때 채운다(현재 비어 있음)")
                continue
            errors.append(f"{tag} {p}")
        needs_file = bool(set(spec.get("required", [])) & file_fields)
        if needs_file and i == 1 and not a.get("inputs") and not s.get("input_from"):
            errors.append(f"{tag} 파일 입력이 필요한데 inputs 도 input_from 도 없다")
        if i > 1 and needs_file and not s.get("input_from") and not a.get("inputs"):
            warnings.append(f"{tag} 앞 단계 결과를 쓰려면 input_from 을 적는다")
    deps = a.get("blocked_by") or []
    for dep in ([deps] if isinstance(deps, str) else deps):
        if dep not in ALL_IDS:
            errors.append(f"{where} blocked_by 의 '{dep}' 가 매니페스트에 없다")
    if steps and steps[0].get("api") in MANUAL_APIS and a.get("status") == "planned":
        warnings.append(f"{where} 수동 제작 에셋이다. 워크플로에서는 manual_pending 으로만 표시된다")


def read_csv(path):
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def cross_check(m, game_dir, errors, warnings):
    ids = {a.get("id") for a in m.get("assets", [])}
    text = json.dumps(m, ensure_ascii=False)
    dialogue = read_csv(game_dir / "data" / "dialogue.csv")
    chars = read_csv(game_dir / "data" / "characters.csv")
    if dialogue is None:
        warnings.append("data/dialogue.csv 가 없어 대사 대조를 건너뛴다")
    else:
        need = [d for d in dialogue if d.get("voice", "none") not in ("none", "")]
        missing = [d["line_id"] for d in need if d["line_id"] not in text]
        if missing:
            errors.append(f"음성이 필요한 대사 {len(missing)}줄이 매니페스트에 없다: {missing[:10]}")
    if chars is not None and dialogue is not None:
        known = {c["speaker_id"] for c in chars}
        unknown = sorted({d["speaker_id"] for d in dialogue if d.get("speaker_id") not in known})
        if unknown:
            errors.append(f"characters.csv 에 없는 speaker_id: {unknown}")
    meta_path = game_dir.parent.parent / "_workspace" / game_dir.name / "run_meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        for lang in meta.get("target_langs", []):
            if not any(a.get("category") == "localization" and lang in json.dumps(a) for a in m.get("assets", [])):
                warnings.append(f"대상 언어 {lang} 의 현지화 에셋이 없다")
    if not ids:
        errors.append("assets 가 비어 있다")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--game-dir", help="games/{slug} — 대사·캐릭터·현지화 대조")
    args = ap.parse_args()
    errors, warnings = [], []
    try:
        m = json.loads(pathlib.Path(args.manifest).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(json.dumps({"ok": False, "errors": [f"매니페스트를 읽을 수 없다: {e}"], "warnings": []},
                         ensure_ascii=False, indent=2))
        sys.exit(1)
    for k in ("game", "assets"):
        if k not in m:
            errors.append(f"최상위 필드 누락: {k}")
    seen = set()
    ALL_IDS.update(a.get("id") for a in m.get("assets", []))
    for a in m.get("assets", []):
        check_asset(a, seen, errors, warnings)
    if args.game_dir:
        cross_check(m, pathlib.Path(args.game_dir), errors, warnings)
    counts = {}
    for a in m.get("assets", []):
        counts[a.get("category")] = counts.get(a.get("category"), 0) + 1
    print(json.dumps({"ok": not errors, "assets": len(m.get("assets", [])), "by_category": counts,
                      "errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()
