---
name: balance-simulation
description: "밸런스 분석가가 쓰는 작업법. 밸런스 CSV 를 스키마로 검사하고(check_balance_tables.py), 몬테카를로·경제 유입·유출·성장 곡선·처치 시간(TTK) 시뮬레이션을 세워 돌리고(sim_template.py), 판정 기준을 먼저 정해 pass/fail 을 내고, systems 에게 구체적인 수정 권고를 보내는 절차와 보고서 템플릿을 담았다. 출시 준비 단계에서 구현 코드의 수치를 확정 CSV 와 대조하는 절차도 포함한다. 밸런스 검증, 난이도·경제 시뮬레이션, 기획 수치와 구현 수치 대조를 할 때 사용한다. 수치 자체를 설계하는 일은 game-systems-design 스킬을 쓴다. check_balance_tables.py 는 game-qa 와 gameplay-engineer 도 확정 CSV 검사에 쓴다."
---

# 밸런스 시뮬레이션과 구현 대조

밸런스 분석의 목적은 "수치가 좋다"는 의견이 아니라 "컨셉이 약속한 경험이 이 수치로 나온다/나오지 않는다"는 판정이다. 그러려면 기준을 먼저 정하고, 같은 입력으로 같은 결과가 나오게 돌리고, 결과를 표·열 단위의 수정 권고로 바꿔야 한다.

파일 경로는 산출물 계약서(`.claude/skills/varco-game-studio/references/contracts.md` 3절, 7-3절)를 따른다.

## 1. 1단계 작업 순서

1. **표 검사:** systems 가 "CSV 준비됨"을 알리면 먼저 검사한다. 실패하면 시뮬레이션을 돌리지 않고 검사 결과를 systems 에게 보낸다.
   `python3 .claude/skills/balance-simulation/scripts/check_balance_tables.py _workspace/{slug}/01_systems_balance`
2. **판정 기준 정하기:** 컨셉의 성공 기준과 레벨 문서의 플레이 시간 목표에서 지표와 합격 범위를 뽑아 `_workspace/{slug}/01_balance_criteria.json` 에 쓴다(3절). **결과를 보기 전에 정한다.** 결과를 본 뒤 기준을 정하면 어떤 수치든 통과시킬 수 있다.
3. **모델 세우기:** `scripts/sim_template.py` 를 `_workspace/{slug}/01_balance_sim.py` 로 복사하고 `simulate_once()` 를 시스템 명세의 규칙·공식대로 바꾼다(2절).
4. **돌리기:** 시드를 고정하고 충분히 반복한다(보통 5,000회, 분포가 넓으면 20,000회).
   ```bash
   python3 _workspace/{slug}/01_balance_sim.py --balance _workspace/{slug}/01_systems_balance \
     --criteria _workspace/{slug}/01_balance_criteria.json --runs 5000 --seed 42 \
     --out _workspace/{slug}/01_balance_result.json
   ```
5. **판정과 권고:** 실패한 지표마다 원인이 되는 표·열을 찾고, 권장값을 넣어 다시 돌려 효과를 확인한 뒤 systems 에게 보낸다(4절).
6. **반복:** systems 가 고친 표로 1~5를 다시 한다. 주고받는 수정은 최대 3회다.
7. **보고서:** `_workspace/{slug}/01_balance_report.md` 를 쓴다(5절). 3회 뒤에도 기준을 넘지 못하면 판정을 `fail` 로 두고 남은 차이와 위험을 적는다.

## 2. 모델 세우기

시뮬레이션은 게임 전체를 흉내 내지 않는다. 판정 기준에 영향을 주는 규칙만 옮긴다. 무엇을 옮길지는 기준 지표에서 거꾸로 정한다.

| 확인하려는 것 | 모델 | 주요 지표 |
| --- | --- | --- |
| 전투 난이도 | 처치 시간(TTK)·피격 시뮬레이션. 명중·치명타 같은 무작위는 명세의 확률 그대로 | 적별 TTK, 레벨 클리어 시간, 사망 횟수 |
| 경제 | 시간 단위로 재화 유입(보상)·유출(구매·강화)을 누적 | 목표 아이템까지 걸리는 판 수, 판당 순유입, 인플레이션(보유량 증가 속도) |
| 성장 | 레벨·강화 단계별 능력치와 적 능력치를 나란히 계산 | 단계별 TTK 변화, 성장이 적보다 느려지는 지점 |
| 운 요소 | 드롭·가챠·치명타의 분포를 많이 반복 | 최악 10%(p10/p90) 플레이어의 경험 |
| 레이싱·타이밍 | 구간별 속도·부스트를 누적 | 구간 시간, 랩 타임, 부스트 사용률 |

### 모델 작성 규칙

- **무작위는 `rng` 로만 뽑는다.** 파이썬 `random` 이나 시드 없는 numpy 를 섞으면 같은 시드로 같은 결과가 나오지 않는다.
- **수치는 표에서만 읽는다.** 모델 안에 숫자를 적으면 CSV 를 고쳐도 결과가 바뀌지 않는다. 표에 없는 값(플레이어 실력 가정)은 `--param` 으로 넘기고 보고서 「가정」 절에 적는다.
- **공식은 명세 문구 그대로 옮긴다.** 반올림·최솟값까지 명세와 같게 한다. 명세가 모호하면 systems 에게 묻고, 답을 받기 전에 정한 가정은 보고서에 적는다.
- **플레이어 모델을 단순하게 밝힌다.** 명중률·반응 시간 같은 실력 가정을 두세 단계(초보·보통·숙련)로 나눠 돌리면 난이도 폭을 볼 수 있다.

## 3. 판정 기준 — `01_balance_criteria.json`

```json
{
  "clear_time_s": {"stat": "median", "min": 60, "max": 120, "source": "컨셉 성공 기준 1"},
  "deaths":       {"stat": "mean",   "max": 1.5,             "source": "컨셉: 첫 판 사망 2회 미만"},
  "max_ttk_s":    {"stat": "p90",    "max": 20,              "source": "레벨 문서: 보스전 20초 이내"}
}
```

- `stat`: `mean`, `median`, `p10`, `p90`, `min`, `max`. 운 요소가 큰 지표는 평균보다 `p90`(운 나쁜 10%)을 본다.
- `source` 에 기준의 출처를 적는다. 출처 없는 기준은 director 가 믿을 근거가 없다.
- 기준을 바꿔야 한다고 판단하면 혼자 바꾸지 않고 director 에게 제안한다.

## 4. 수정 권고 보내기

권고는 systems 가 그대로 반영할 수 있게 쓴다. 권장값은 스키마의 `min`·`max` 안에서 고르고, 그 값으로 다시 돌린 결과를 함께 보낸다.

> `systems` 에게: `max_ttk_s`(p90) 가 46초로 기준 20초를 넘는다. 원인은 `enemies.csv` 의 `boss_core.hp`(1200)와 `defense_pct`(25). `boss_core.hp` 를 1200 → 700 으로 낮추면 p90 이 19.5초가 된다(5,000회, 시드 42). `defense_pct` 는 그대로 둔다. 반영 여부와 이유를 알려 달라.

한 번에 여러 열을 바꾸면 무엇이 효과를 냈는지 알 수 없다. 지표 하나에 열 하나를 먼저 권한다.

## 5. 보고서 템플릿 — `_workspace/{slug}/01_balance_report.md`

```markdown
# 밸런스 시뮬레이션 보고서

## 판정: pass | fail
## 입력
- 밸런스 CSV 해시: (결과 JSON 의 input_hashes)
- 반복 횟수 / 시드 / 모델 파일: 01_balance_sim.py

## 가정
- 플레이어 명중률 85% (--param accuracy=0.85)
- …

## 판정 기준과 결과
| 지표 | 기준(stat, 범위) | 출처 | 결과 | 판정 |
| --- | --- | --- | --- | --- |

## 분포 요약
| 지표 | 평균 | 중앙값 | p10 | p90 |

## 수정 이력
| 회차 | 표:열 | 이전 → 이후 | 영향받은 지표(이전 → 이후) | systems 반영 여부 |

## 남은 위험
시뮬레이션이 다루지 못한 것(조작 숙련도, 물리 충돌 등)과 fail 로 남은 지표
```

## 6. 5단계 — 구현 수치 대조

출시 준비 단계에서 구현이 확정 CSV 를 그대로 쓰는지 확인한다. 결과는 `games/{slug}/qa/reports/balance-impl.md` 다.

1. **확정 CSV 검사:** `check_balance_tables.py games/{slug}/data/balance` 로 승격본이 여전히 스키마를 지키는지 본다. 해시가 1단계 보고서와 다르면 무엇이 바뀌었는지 먼저 확인한다.
2. **코드가 CSV 를 읽는지 확인한다.**
   - 웹: `games/{slug}/web/` 에서 `data/balance` 경로나 CSV 파일 이름을 불러오는 코드를 찾는다(`grep -rn "balance" games/{slug}/web --include=*.js --include=*.ts`).
   - Unity: `games/{slug}/unity/Assets` 에서 CSV 로더와 `StreamingAssets` 복사본을 찾는다.
   - 복사본이 있으면 원본과 해시를 비교한다. 복사본이 낡으면 구현이 옛 수치로 돈다.
3. **숫자를 직접 적은 곳을 찾는다.** 밸런스 열 이름이 붙은 상수나, CSV 에 있는 값과 같은 숫자 리터럴이 게임 로직에 있는지 찾는다. 찾으면 파일:줄 번호와 CSV 값을 나란히 적는다. 코드는 고치지 않는다(gameplay-engineer 의 일이다).
4. **구현 값으로 다시 돌린다.** 구현이 쓰는 값이 CSV 와 다르면 구현 값을 넣은 복사본 폴더로 시뮬레이션을 돌려 판정이 바뀌는지 본다.
5. **보고서:**

```markdown
# 밸런스 구현 대조

## 판정: pass | fail
## 확정 CSV
- 검사 결과, 해시(1단계와 같은가)
## 코드의 CSV 사용
| 표 | 읽는 코드(파일:줄) | 복사본 여부·해시 일치 |
## 불일치
| 표:열(id) | CSV 값 | 구현 값 | 위치(파일:줄) | 영향 |
## 구현 값 시뮬레이션
기준별 결과(불일치가 있을 때만)
## 권고
gameplay-engineer 에게 넘길 수정 목록
```

불일치 0건, 모든 표를 코드가 CSV 에서 읽음, 시뮬레이션 판정 유지 — 세 가지를 모두 만족해야 `pass` 다.

## 7. 스크립트

| 파일 | 쓰는 사람 | 하는 일 |
| --- | --- | --- |
| `scripts/check_balance_tables.py` | balance, systems, game-qa, gameplay-engineer | CSV ↔ `_schema.json` 대조(열, 타입, 범위, id). `load_tables()` 로 타입이 맞춰진 표를 불러 쓸 수 있다 |
| `scripts/sim_template.py` | balance | 시뮬레이션 뼈대. 복사해서 `simulate_once()` 만 바꾼다. 기준 판정, 입력 해시, 시드 기록을 해 준다 |

`sim_template.py` 의 예시 모델은 `player.csv`(id=`default`)와 `enemies.csv` 가 있을 때만 돈다. 게임마다 통째로 바꾼다.
