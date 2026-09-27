#!/usr/bin/env python3
"""밸런스 시뮬레이션 뼈대. 복사해서 simulate_once() 만 게임에 맞게 바꿔 쓴다.

복사 위치: _workspace/{slug}/01_balance_sim.py
실행:
  python3 01_balance_sim.py --balance _workspace/{slug}/01_systems_balance \
      --criteria criteria.json --runs 5000 --seed 42 --out _workspace/{slug}/01_balance_result.json

criteria.json (판정 기준 — 시뮬레이션을 돌리기 전에 컨셉의 성공 기준에서 정한다)
  {"clear_time_s": {"stat": "median", "min": 60, "max": 120},
   "deaths":       {"stat": "mean",   "max": 1.5}}
  stat 은 mean | median | p10 | p90 | min | max 중 하나다.

출력 JSON 에는 입력 CSV 해시, 시드, 반복 횟수, 지표별 분포, 기준별 판정이 들어간다.
같은 입력·시드면 같은 결과가 나온다. 수정 전후 비교는 두 결과 파일을 나란히 놓고 한다.
"""
import argparse
import json
import math
import pathlib
import sys

import numpy as np

# check_balance_tables.py 를 이 파일 옆이나 스킬 폴더에서 찾는다
for cand in (pathlib.Path(__file__).resolve().parent,
             pathlib.Path(".claude/skills/balance-simulation/scripts").resolve()):
    if (cand / "check_balance_tables.py").exists():
        sys.path.insert(0, str(cand))
        break
from check_balance_tables import check  # noqa: E402

STATS = {
    "mean": lambda a: float(np.mean(a)),
    "median": lambda a: float(np.median(a)),
    "p10": lambda a: float(np.percentile(a, 10)),
    "p90": lambda a: float(np.percentile(a, 90)),
    "min": lambda a: float(np.min(a)),
    "max": lambda a: float(np.max(a)),
}


# ============================================================================ 게임에 맞게 바꾸는 부분
def simulate_once(tables, rng, params):
    """한 판을 시뮬레이션하고 지표 dict 를 돌려준다. 값은 숫자여야 한다.

    tables: {"표이름": {"행id": {"열": 값}}} — 스키마 타입으로 변환돼 있다
    rng:    numpy Generator (무작위는 반드시 이것만 쓴다. 그래야 시드로 재현된다)
    params: --param key=value 로 넘긴 값(플레이어 실력 가정 등)

    아래는 예시 모델이다: 플레이어가 enemies 표의 적을 순서대로 처치하는 데 걸리는 시간.
    player.csv(id=default: attack, attack_interval_s, crit_rate_pct, crit_mult, hp)와
    enemies.csv(hp, attack, defense_pct, attack_interval_s)를 쓴다. 게임 규칙에 맞게 통째로 바꾼다.
    """
    player = tables["player"]["default"]
    accuracy = float(params.get("accuracy", 0.85))       # 가정: 플레이어 명중률
    t, hp_left, deaths = 0.0, float(player["hp"]), 0
    per_enemy_ttk = []
    for eid, e in tables["enemies"].items():
        enemy_hp = float(e["hp"])
        start = t
        while enemy_hp > 0:
            t += float(player["attack_interval_s"])
            if rng.random() > accuracy:
                continue
            dmg = max(1, math.floor(player["attack"] * (1 - e["defense_pct"] / 100)))
            if rng.random() < player["crit_rate_pct"] / 100:
                dmg = math.floor(dmg * player["crit_mult"])
            enemy_hp -= dmg
        ttk = t - start
        per_enemy_ttk.append(ttk)
        # 적이 싸우는 동안 플레이어에게 준 피해
        hits = math.floor(ttk / float(e["attack_interval_s"]))
        hp_left -= hits * float(e["attack"])
        if hp_left <= 0:
            deaths += 1
            hp_left = float(player["hp"])
    return {"clear_time_s": t, "deaths": deaths, "max_ttk_s": max(per_enemy_ttk)}
# ============================================================================


def summarize(values):
    a = np.asarray(values, dtype=float)
    return {k: round(f(a), 4) for k, f in STATS.items()}


def judge(dist, criteria):
    verdicts = {}
    for metric, rule in criteria.items():
        if metric not in dist:
            verdicts[metric] = {"result": "missing", "detail": "시뮬레이션이 이 지표를 내지 않았다"}
            continue
        stat = rule.get("stat", "median")
        val = dist[metric][stat]
        ok = ("min" not in rule or val >= rule["min"]) and ("max" not in rule or val <= rule["max"])
        verdicts[metric] = {"result": "pass" if ok else "fail", "stat": stat, "value": val,
                            "range": [rule.get("min"), rule.get("max")]}
    return verdicts


def parse_value(raw):
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return raw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--balance", required=True, help="밸런스 CSV 폴더(_schema.json 포함)")
    ap.add_argument("--criteria", help="판정 기준 JSON")
    ap.add_argument("--runs", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--param", action="append", default=[], help="key=value (모델 가정)")
    ap.add_argument("--out", help="결과 JSON 경로")
    args = ap.parse_args()

    errors, warnings, tables, summary = check(args.balance)
    if errors:
        print(json.dumps({"ok": False, "stage": "table_check", "errors": errors}, ensure_ascii=False, indent=2))
        sys.exit(1)
    params = {k: parse_value(v) for k, v in (p.split("=", 1) for p in args.param)}
    rng = np.random.default_rng(args.seed)
    runs = []
    for _ in range(args.runs):
        runs.append(simulate_once(tables, rng, params))
    metrics = sorted({k for r in runs for k in r})
    dist = {m: summarize([r[m] for r in runs if m in r]) for m in metrics}
    criteria = json.loads(pathlib.Path(args.criteria).read_text(encoding="utf-8")) if args.criteria else {}
    verdicts = judge(dist, criteria)
    overall = ("pass" if verdicts and all(v["result"] == "pass" for v in verdicts.values())
               else "fail" if verdicts else "no_criteria")
    result = {"ok": True, "verdict": overall, "runs": args.runs, "seed": args.seed, "params": params,
              "input_hashes": summary["hashes"], "distribution": dist, "criteria": criteria,
              "verdicts": verdicts, "table_warnings": warnings}
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        pathlib.Path(args.out).write_text(text, encoding="utf-8")
    print(text)
    sys.exit(0)


if __name__ == "__main__":
    main()
