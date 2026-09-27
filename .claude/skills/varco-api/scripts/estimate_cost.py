#!/usr/bin/env python3
"""에셋 매니페스트의 VARCO 크레딧 견적을 계산한다.

사용법
  estimate_cost.py games/{slug}/manifest.json            # 표 출력
  estimate_cost.py manifest.json --write                 # 각 step/asset 의 est_credits 를 채워 저장
  estimate_cost.py manifest.json --md out.md --json out.json

step 에서 쓰는 견적 힌트(선택)
  calls              : 같은 요청을 몇 번 호출하는가 (기본 1)
  per_call_chars     : TTS 를 줄마다 호출할 때 줄별 글자 수 목록(대사 묶음 에셋)
  est_audio_seconds  : 음성 변환 입력 길이(초). 없으면 단가 계산 불가로 표시
  est_out_size       : [가로, 세로] 이미지 출력 크기. 없으면 최소 단가로 계산
  est_credits        : 직접 지정하면 그 값을 쓴다

단가는 varco_catalog.py 의 추정치다. 단가 미상 step 은 합계에 넣지 않고 개수로 따로 알린다.
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from varco_catalog import APIS, MANUAL_APIS, estimate_credits  # noqa: E402


def estimate_step(step):
    api = step.get("api", "")
    if "est_credits_override" in step:
        return step["est_credits_override"], True, "직접 지정"
    if api not in APIS and api not in MANUAL_APIS:
        return None, False, f"알 수 없는 API {api}"
    size = step.get("est_out_size")
    if step.get("per_call_chars"):
        # 줄마다 따로 호출하므로 줄 단위로 올림한 값을 더한다
        total, known, note = 0, True, ""
        for n in step["per_call_chars"]:
            c, known, note = estimate_credits(api, step.get("params", {}), text="가" * int(n))
            if c is None:
                return None, False, note
            total += c
        return total, known, f"{len(step['per_call_chars'])}줄, 줄 단위 올림 합계"
    return estimate_credits(api, step.get("params", {}), audio_seconds=step.get("est_audio_seconds"),
                            out_size=tuple(size) if size else None, calls=int(step.get("calls", 1)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--write", action="store_true", help="est_credits 를 매니페스트에 채워 저장")
    ap.add_argument("--md", help="견적 표를 Markdown 으로 저장")
    ap.add_argument("--json", help="요약을 JSON 으로 저장")
    ap.add_argument("--phase", help="이 phase(production|release) 에셋만 계산")
    args = ap.parse_args()

    path = pathlib.Path(args.manifest)
    m = json.loads(path.read_text(encoding="utf-8"))
    rows, total, unknown_steps, assumed_steps = [], 0, 0, 0
    by = {"owner": {}, "category": {}, "priority": {}}
    for a in m.get("assets", []):
        if args.phase and a.get("phase", "production") != args.phase:
            continue
        a_total, a_unknown, notes = 0, 0, []
        for s in a.get("steps", []):
            c, known, note = estimate_step(s)
            s["est_credits"] = c
            s["price_known"] = known
            if c is None:
                a_unknown += 1
                unknown_steps += 1
                notes.append(f"{s.get('api')}: {note}")
            else:
                a_total += c
                if not known:
                    assumed_steps += 1
                    notes.append(f"{s.get('api')}: {note}")
        a["est_credits"] = a_total
        a["est_unknown_steps"] = a_unknown
        total += a_total
        for dim in by:
            key = a.get(dim, "-")
            by[dim][key] = by[dim].get(key, 0) + a_total
        rows.append((a.get("id"), a.get("category"), a.get("owner"), a.get("priority"), a.get("phase", "production"),
                     a_total, a_unknown, "; ".join(notes)))

    budget = m.get("budget_credits")
    lines = ["| id | 분류 | 담당 | 우선순위 | 단계 | 추정 크레딧 | 단가 미상 step | 비고 |",
             "| --- | --- | --- | --- | --- | ---: | ---: | --- |"]
    for r in rows:
        lines.append("| " + " | ".join(str(x) if x not in (None, "") else "-" for x in r) + " |")
    lines += ["", f"- 합계(추정): **{total:,.0f} 크레딧**",
              f"- 단가 미상 step: {unknown_steps}건 (합계에 포함하지 않음)",
              f"- 다른 API 단가를 빌려 추정한 step: {assumed_steps}건"]
    if budget is not None:
        lines.append(f"- 예산: {budget:,} 크레딧 → {'예산 안' if total <= budget else '**예산 초과**'}")
    for dim, label in (("priority", "우선순위별"), ("owner", "담당별"), ("category", "분류별")):
        lines.append(f"- {label}: " + ", ".join(f"{k} {v:,.0f}" for k, v in sorted(by[dim].items(), key=str)))
    md = "\n".join(lines)
    print(md)

    summary = {"total_est_credits": total, "unknown_price_steps": unknown_steps, "assumed_price_steps": assumed_steps,
               "budget_credits": budget, "within_budget": (budget is None or total <= budget), "by": by,
               "assets": len(rows)}
    if args.md:
        pathlib.Path(args.md).write_text(md + "\n", encoding="utf-8")
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.write:
        path.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
