---
name: varco-game-studio
description: "VARCO API 플랫폼으로 게임을 기획부터 QA까지 만드는 15인 에이전트 팀을 조율한다. 게임 아이디어 구체화, 컨셉·GDD·시스템·밸런스·시나리오·레벨·UI/UX 기획, VARCO 사운드·음성·3D·이미지·번역 에셋 제작과 크레딧 견적, 웹(HTML5) 또는 Unity 프로토타입 개발, 에셋·기능·밸런스 QA, 스토어 이미지와 출시 판정까지 맡는다. '게임 만들어줘', '게임 기획해줘', 'GDD 써줘', 'VARCO로 게임 에셋 만들어줘', '프로토타입 만들어줘', '게임 QA 해줘', '출시 준비' 같은 요청에 사용한다. 후속 요청에도 사용한다: '기획만 다시', '밸런스 수정', '사운드만 다시 뽑아줘', '대사 음성 다시', '3D 모델 재생성', '언어 추가', '버그 고쳐줘', 'QA 다시 돌려줘', '스토어 이미지 다시', '드라이런 말고 실제로 생성', '이전 결과를 바탕으로 개선', '재실행', '업데이트', '보완'. VARCO API 한두 번을 단순 호출하는 일은 varco-api 스킬로 충분하다."
---

# VARCO 게임 스튜디오 오케스트레이터

게임 아이디어 한 줄을 받아 기획 문서, VARCO로 만든 에셋, 플레이 가능한 프로토타입, QA 보고서, 출시 판정까지 만든다. 메인 에이전트가 리더를 맡아 단계마다 알맞은 실행 모드로 팀을 부린다.

파일 위치와 형식은 모두 `references/contracts.md`(산출물 계약서)를 따른다. 리더도 이 문서를 먼저 읽는다.

## 실행 모드: 혼합

| 단계 | 실행 모드 | 고른 이유 |
| --- | --- | --- |
| 0. 준비 | 리더가 직접 | 기존 작업 확인, 실행 설정 확정 |
| 1. 기획 | 지속형 에이전트 협업 | 시스템·시나리오·레벨·UI 문서가 서로 맞물려 여러 번 의견을 주고받아야 한다 |
| 2. 에셋 명세 | 서브에이전트 위임 + **크레딧 승인** | 매니페스트 한 벌만 받으면 된다. 돈이 드는 단계라 사용자 승인이 필요하다 |
| 3. 에셋 제작 | 워크플로 조율 | 에셋 목록이 매니페스트로 정해져 있고 검증·재작업 규칙을 코드로 표현할 수 있다 |
| 4. 개발 | 지속형 에이전트 한 쌍 | 엔지니어와 QA가 모듈마다 버그를 주고받으며 고친다 |
| 5. 통합 QA·출시 준비 | 서브에이전트 병렬 + 디렉터 판정 | 서로 독립인 검사 네 가지를 동시에 돌리고 마지막에 한 사람이 판정한다 |

## 팀 구성

에이전트 정의는 `.claude/agents/{이름}.md` 에 있다. 모델은 정의 파일에 지정했으므로 호출할 때 따로 넘기지 않는다.

| 이름(SendMessage 주소) | `subagent_type` | 모델 | 단계 | 스킬 | 주요 산출물 |
| --- | --- | --- | --- | --- | --- |
| director | game-director | fable | 1, 5 | game-concept | 컨셉, 통합 리뷰, GDD, 출시 판정 |
| systems | systems-designer | opus | 1 | game-systems-design | 시스템 명세, 밸런스 CSV |
| narrative | narrative-designer | opus | 1 | game-narrative | 세계관, 캐릭터, 대사, 용어집 |
| level | level-designer | opus | 1 | level-design | 레벨 설계, 사운드 구역, 프랍 목록 |
| ux | ux-designer | sonnet | 1 | game-ux-design | 화면 흐름, HUD, UI 문자열 |
| balance | balance-analyst | opus | 1, 5 | balance-simulation | 밸런스 시뮬레이션 보고서, 구현 대조 |
| — | asset-producer | sonnet | 2 | asset-manifest, varco-api | 에셋 매니페스트, 견적 |
| — | sound-designer | sonnet | 3 | varco-sound-production, varco-api | 효과음, 환경음, 크리처 음성 |
| — | voice-director | sonnet | 3 | varco-voice-production, varco-api | 대사 음성, 얼굴 애니메이션 |
| — | visual-artist | sonnet | 3 | varco-visual-production, varco-api | 3D 모델, 편집 이미지 |
| — | localization-specialist | sonnet | 3 | varco-localization, varco-api | 언어별 문자열 |
| — | marketing-artist | sonnet | 5 | marketing-kit, varco-api | 스토어 이미지, 키 아트 |
| engineer | gameplay-engineer | opus | 4 | game-prototype-dev | 웹 또는 Unity 프로토타입 |
| — | asset-qa | sonnet | 3, 5 | asset-qa-check | 에셋 검증 결과, 전수 감사 |
| qa | game-qa | opus | 4, 5 | game-qa-testing | 테스트 계획, 버그, 회귀 보고서 |

## 0단계: 준비와 기존 작업 확인

**실행 모드:** 리더가 직접

1. **게임 식별자(`slug`)를 정한다.** 사용자 요청에서 영문 kebab-case 이름을 짓는다. 이미 진행 중인 게임을 가리키면 그 이름을 쓴다(`ls _workspace games`).
2. **기존 작업을 확인해 실행 범위를 정한다.**

   | 상황 | 판단 | 할 일 |
   | --- | --- | --- |
   | `_workspace/{slug}/` 없음 | 처음 실행 | 1단계부터 |
   | 있음 + 일부만 고치라는 요청 | 부분 재실행 | 「후속 요청 처리」 표에서 다시 돌릴 단계만 |
   | 있음 + 전혀 새 아이디어 | 새 실행 | 기존 폴더를 `_workspace/{slug}_{YYYYMMDD-HHMM}/` 로 옮기고 새로 시작 |
   | 3단계 워크플로가 중간에 멈춤 | 재개 | `run_meta.json` 의 `workflow_runs` 에서 runId 를 찾아 `resumeFromRunId` 로 재개 |

3. **실행 설정을 확정해 `_workspace/{slug}/run_meta.json` 에 쓴다**(계약서 2절).
   - 엔진: 사용자가 말하지 않으면 `web`. Unity 를 원하면 `unity`.
   - VARCO 키 확인(값은 출력하지 않는다):
     `python3 -c "import os,pathlib; print('set' if os.environ.get('OPENAPI_KEY') or any('OPENAPI_KEY' in l for l in (pathlib.Path('.env').read_text().splitlines() if pathlib.Path('.env').exists() else [])) else 'unset')"`
     키가 없으면 `varco_mode` 를 `dry-run` 으로 두고 사용자에게 알린다. 키는 `.env` 에 `OPENAPI_KEY=...` 로 넣으면 되고, `.env` 는 절대 커밋하거나 문서에 옮겨 적지 않는다.
   - 대상 언어: 말하지 않으면 원문 `ko`, 번역 `en`, `ja`. 음성 언어는 `korean`.
   - 사용자에게 한꺼번에 물을 것은 엔진과 대상 언어 정도로 줄인다. 예산은 2단계 견적을 본 뒤 묻는다.
4. 사용자의 원래 요청을 `_workspace/{slug}/00_input.md` 에 그대로 저장한다.

## 1단계: 기획

**실행 모드:** 지속형 에이전트 협업(감독자: 리더, 검토자: director)

### 1-1. 컨셉

1. `Agent(name: "director", subagent_type: "game-director", prompt: ...)` 로 디렉터를 실행한다. 프롬프트에는 `00_input.md`, `run_meta.json` 경로와 "컨셉 문서 `01_director_concept.md` 를 쓰고 핵심 결정 세 가지를 요약해 보고하라"를 넣는다.
2. `gates` 가 `confirm` 이면 컨셉 요약을 보여 주고 `AskUserQuestion` 으로 묻는다: 승인 / 고칠 점 알려 주기 / 다른 방향으로 다시. 고칠 점은 SendMessage 로 director 에게 전한다.

### 1-2. 상세 기획

한 메시지에서 다섯 명을 동시에 실행한다. 모두 `01_director_concept.md` 를 읽고 시작한다.

```
Agent(name: "systems",   subagent_type: "systems-designer",   prompt: "...컨셉 경로, 산출물 경로, 통신 대상...")
Agent(name: "narrative", subagent_type: "narrative-designer", prompt: "...")
Agent(name: "level",     subagent_type: "level-designer",     prompt: "...")
Agent(name: "ux",        subagent_type: "ux-designer",        prompt: "...")
Agent(name: "balance",   subagent_type: "balance-analyst",    prompt: "...systems 의 밸런스 CSV 가 나오면 검증을 시작한다...")
```

공유 작업 목록에 아래 작업을 등록한다(TaskCreate). 공유 작업 도구를 쓸 수 없으면 `_workspace/{slug}/01_tasks.md` 에 같은 표를 만들어 리더가 갱신한다.

| 작업 | 담당 | 먼저 끝나야 할 작업 | 산출물 |
| --- | --- | --- | --- |
| T1 시스템 명세·밸런스 테이블 | systems | 컨셉 | `01_systems_spec.md`, `01_systems_balance/*.csv` |
| T2 세계관·캐릭터·대사·용어집 | narrative | 컨셉 | `01_narrative_*.md/csv` |
| T3 레벨 설계 | level | T1 초안, T2 초안 | `01_level_design.md` |
| T4 화면 흐름·HUD·UI 문자열 | ux | T1 초안 | `01_ux_spec.md`, `01_ux_strings.csv` |
| T5 밸런스 시뮬레이션 | balance | T1 | `01_balance_report.md` |
| T6 통합 리뷰 | director | T1~T5 | `01_director_review.md` |
| T7 통합 GDD | director | T6 처리 완료 | `01_director_gdd.md` |

**통신 경로:** 에이전트끼리 직접 SendMessage 로 주고받되, 결정 사항은 반드시 파일에 남긴다.

| 보내는 쪽 → 받는 쪽 | 내용 |
| --- | --- |
| systems → balance | "밸런스 CSV 준비됨: 경로" |
| balance → systems | 시뮬레이션에서 나온 수정 요청(표·열·권장값·근거). 최대 3회 주고받는다 |
| systems → ux, level | 플레이어에게 보여 줄 수치, 새 메커닉 |
| narrative → level | 장면 목록, 퀘스트 장소 |
| level → narrative | 레벨에 필요한 대사·장면 요청 |
| 누구든 → director | 컨셉과 부딪히는 결정이 필요할 때 |
| director → 담당 | 통합 리뷰의 수정 요청. 최대 2회 |

T3·T4 는 초안이 먼저 나온 문서로 시작하고, 앞 문서가 바뀌면 받은 메시지를 보고 고친다. 에이전트가 오래 응답하지 않으면 SendMessage 로 상태를 묻는다.

### 1-3. 동결과 승격

T7 이 끝나면 계약서 8절대로 동결한다.

1. 기획 담당 여섯 명에게 "1단계 산출물 동결. 이후 수정은 `_v2` 파일로 쓰고 리더에게 알려라"를 보낸다.
2. `shasum _workspace/{slug}/01_* _workspace/{slug}/01_systems_balance/* > _workspace/{slug}/freeze_01.sha`
3. 계약서 3절 표대로 `games/{slug}/docs/`, `games/{slug}/data/` 로 복사한다.
4. 데이터 파일 형식을 빠르게 확인한다: CSV 열 이름이 계약서와 같은지, `dialogue.csv` 의 `speaker_id` 가 모두 `characters.csv` 에 있는지.
5. `run_meta.json` 의 `phases_done` 에 `01` 을 넣는다.

## 2단계: 에셋 명세와 크레딧 승인

**실행 모드:** 서브에이전트 위임(단발, `name` 없음)

1. `Agent(subagent_type: "asset-producer", prompt: ...)` — 확정 폴더 경로와 `run_meta.json` 을 넘기고 `_workspace/{slug}/02_producer_manifest.json` 과 `02_producer_estimate.md` 를 받는다.
2. 리더가 직접 검사한다.
   - `python3 .claude/skills/asset-manifest/scripts/validate_manifest.py _workspace/{slug}/02_producer_manifest.json --game-dir games/{slug}`
   - `python3 .claude/skills/varco-api/scripts/estimate_cost.py _workspace/{slug}/02_producer_manifest.json --write`
   - 오류가 있으면 asset-producer 를 오류 목록과 함께 한 번 더 부른다.
3. **크레딧 승인(항상 사용자에게 묻는다).** 견적 합계, 우선순위별 합계, 단가를 모르는 호출 수, 수동 제작 에셋 목록을 보여 주고 `AskUserQuestion` 으로 묻는다.
   - 키가 있을 때: 전체 승인 / P0 만 승인 / 드라이런으로 진행 / 매니페스트 수정
   - 키가 없을 때: 드라이런으로 진행 / 키를 넣고 다시 확인
   - 승인한 예산(견적 합계에 여유 10%를 더한 값을 권한다)과 범위를 `run_meta.json` 의 `budget_credits`, `approved_scope`, `varco_mode` 에 적는다.
   - 단가 미공개 API(번역, Voice-to-Face, 음성 변환 Acting)는 합계에 빠져 있다는 점을 분명히 말하고, 이 호출을 실제로 해도 되는지 따로 묻는다. 허용하면 `run_meta.allow_unknown_price` 를 `true` 로 둔다. 허용하지 않으면 연기 변환은 TTS 로 대체되고 얼굴 애니메이션은 빠지며, 번역은 대체할 방법이 없어 현지화 에셋이 `budget_blocked` 가 된다. 이 결과를 질문에 함께 적는다.
   - 원문 외 언어 음성처럼 `blocked_by` 가 붙은 에셋은 번역이 끝난 뒤 두 번째 회차에서 만든다는 점도 알린다.
4. 승인본을 `games/{slug}/manifest.json` 으로 복사한다.

## 3단계: 에셋 제작

**실행 모드:** 워크플로 조율. 사용자가 이 스킬을 불러왔으므로 Workflow 사용에 동의한 것으로 본다.

0. **대사 음성이 있으면 캐스팅을 먼저 한 번 돌린다.** 워크플로에서 여러 voice-director 가 동시에 캐스팅하지 않게 하기 위해서다. 명령은 `varco-voice-production` 스킬의 `voice_cast.py` 절을 따른다. 결과는 `_workspace/{slug}/03_voice_casting.json` 이다. 드라이런이면 자리표시 uuid 가 들어간다.
1. 리더가 작업 목록을 만든다. `games/{slug}/manifest.json` 에서 `phase` 가 `production` 이고 `approved_scope` 안에 드는 에셋만 고른다. 우선순위(P0 → P2) 순으로 정렬해 예산이 P0 에 먼저 쓰이게 한다.
   - 항목 형식: `{id, owner, category, priority, manual}` (`manual` 은 첫 step 의 api 가 `manual.` 로 시작하면 true)
   - **회차를 나눈다.** 1회차에는 `blocked_by` 가 없는 에셋만 넣는다. 1회차가 끝나면 `blocked_by` 에셋 가운데 선행 에셋이 `qa_passed`(드라이런이면 `dry-run`)인 것만 모아 같은 스크립트로 2회차를 돌린다. 선행 에셋이 실패한 에셋은 `skipped` 로 두고 이유를 적는다.
2. 워크플로를 실행한다. 스크립트는 `scripts/asset_production.workflow.js` 에 있다.

   ```
   Workflow({
     scriptPath: "<프로젝트 절대 경로>/.claude/skills/varco-game-studio/scripts/asset_production.workflow.js",
     args: {
       slug, mode: run_meta.varco_mode, budget: run_meta.budget_credits, maxRework: 1,
       allowUnknownPrice: run_meta.allow_unknown_price,
       paths: { runMeta: "_workspace/{slug}/run_meta.json", manifest: "games/{slug}/manifest.json",
                ledger: "_workspace/{slug}/varco_ledger.jsonl", gameDir: "games/{slug}", workspace: "_workspace/{slug}" },
       items: [...]
     }
   })
   ```

   - 단계: 제작(에셋 담당 `agentType`) → 검증(`asset-qa`) → 재작업(고칠 수 있는 실패만 1회) → 재검증
   - 반환: `{results: [{id, final, reworks, prod, qa}], summary: {total, byFinal, dropped, missing}, halted}`
   - 인증 실패나 크레딧 소진이 한 번이라도 나오면 아직 시작하지 않은 에셋은 호출하지 않는다(`halted`).
   - 받은 runId 를 `run_meta.json` 의 `workflow_runs` 에 적는다. 완료 알림이 오기 전에 결과를 짐작해 보고하지 않는다.
3. 결과를 반영한다.
   - 반환값을 `_workspace/{slug}/03_workflow_result.json` 에 저장한다.
   - 매니페스트의 각 에셋 `status` 와 `result` 를 갱신한다(`final` 값을 그대로 `status` 에 쓴다).
   - `python3 .claude/skills/varco-api/scripts/varco_client.py ledger --ledger _workspace/{slug}/varco_ledger.jsonl` 로 실제 사용 추정치를 확인한다.
   - `halted` 가 있으면 멈추고 사용자에게 원인과 해결 방법을 알린다(키 확인, 크레딧 충전). 해결되면 같은 스크립트와 args 로 `resumeFromRunId` 재개한다.
   - `manual_pending` 에셋(배경음악 등)은 사용자에게 목록을 주고, 없으면 개발 단계에서 자리표시 에셋을 쓴다고 알린다.
   - 결과가 비어 있거나 이상하면 워크플로 transcript 의 `journal.jsonl` 로 실제 반환값을 확인한다.

## 4단계: 개발

**실행 모드:** 지속형 에이전트 한 쌍(생성: engineer, 검증: qa)

1. 한 메시지에서 두 명을 실행한다.
   - `Agent(name: "engineer", subagent_type: "gameplay-engineer", prompt: "엔진 {engine}. 확정 폴더 games/{slug}. 먼저 _workspace/{slug}/04_engineer_plan.md 에 모듈 목록과 모듈별 완료 기준을 써서 리더와 qa 에게 알려라.")`
   - `Agent(name: "qa", subagent_type: "game-qa", prompt: "games/{slug}/qa/test-plan.md 를 GDD 로 먼저 쓰고, engineer 가 모듈 완료를 알리면 그 모듈을 바로 검사하라.")`
2. engineer 의 모듈 목록으로 모듈마다 작업을 등록한다. 한 모듈의 흐름은 이렇다.
   - engineer → qa: "모듈 {이름} 완료: 바뀐 파일, 실행 방법, 확인할 점"
   - qa: 테스트 → `04_gameqa_module-{이름}.md` + 버그 파일 → engineer 에게 버그 목록 전달
   - engineer: 수정 → qa 재확인. 한 모듈에서 3회를 넘기면 qa 가 리더에게 올리고, 리더가 알려진 문제로 넘길지 정한다.
3. 두 사람 모두 끝나면 빌드를 동결한다. 웹이면 `games/{slug}/web/` 전체의 해시를 `_workspace/{slug}/freeze_04.sha` 에 기록한다. Unity 면 `Assets/`, `ProjectSettings/` 를 기록한다.

## 5단계: 통합 QA·출시 준비

**실행 모드:** 서브에이전트 병렬 위임 후 디렉터 판정

1. 한 메시지에서 네 가지를 동시에 실행한다.

   | 담당 | 호출 | 산출물 |
   | --- | --- | --- |
   | 에셋 전수 감사 | `Agent(subagent_type: "asset-qa")` — 매니페스트 ↔ 파일 ↔ 코드 참조 대조 | `qa/reports/asset-audit.md`, `_workspace/{slug}/05_assetqa_audit.json` |
   | 최종 회귀 테스트 | `qa` 가 살아 있으면 SendMessage, 아니면 `Agent(subagent_type: "game-qa")` | `qa/reports/regression.md` |
   | 밸런스 구현 대조 | `balance` 가 살아 있으면 SendMessage, 아니면 `Agent(subagent_type: "balance-analyst")` | `qa/reports/balance-impl.md` |
   | 스토어 이미지·키 아트 | `Agent(subagent_type: "marketing-artist")` — 매니페스트의 `phase: release` 에셋 | `marketing/` |

2. 네 결과가 모이면 director 에게 판정을 맡긴다(살아 있으면 SendMessage, 아니면 새로 실행). 계약서 9절 기준으로 판정해 `games/{slug}/RELEASE_REPORT.md` 를 쓰게 한다.
3. 리더는 보고서를 읽고 사용자에게 요약한다: Go/No-Go, 남은 버그, 사용한 크레딧(추정), 수동으로 만들어야 할 에셋, 실행 방법.

## 데이터 전달 요약

| 단계 경계 | 넘기는 것 | 방법 |
| --- | --- | --- |
| 1 → 2 | `games/{slug}/docs`, `data` | 파일(동결·승격 후) |
| 2 → 3 | 승인 매니페스트, 예산, 모드 | `games/{slug}/manifest.json` + Workflow `args` |
| 3 → 4 | 에셋 파일과 상태 | `games/{slug}/assets`, 갱신된 매니페스트, `03_workflow_result.json` |
| 4 → 5 | 동결된 빌드 | `games/{slug}/web` 또는 `unity`, `freeze_04.sha` |
| 5 → 사용자 | 판정과 보고 | `RELEASE_REPORT.md` |

## 오류 처리

| 상황 | 대응 |
| --- | --- |
| `Agent type '...' not found` (정의 파일을 만든 세션이라 아직 등록되지 않음) | 새 세션을 열면 해결된다. 지금 세션에서 계속해야 하면 `subagent_type: "general-purpose"` 로 부르고 프롬프트 첫 줄에 "먼저 `.claude/agents/{이름}.md` 를 읽고 그 정의대로 일하라"를 넣는다. 모델은 정의 파일의 `model` 값을 `model` 인자로 넘긴다. 워크플로의 `agentType` 도 같은 등록부를 쓰므로 3단계는 새 세션에서 돌린다 |
| 에이전트가 응답하지 않음 | SendMessage 로 상태를 묻고 다시 지시한다. 그래도 안 되면 같은 `subagent_type` 을 새 이름(예: `systems-b`)으로 실행하고 기존 산출물 경로를 넘긴다 |
| 사용량 한도 소진·인증 만료·권한 거부 | 재시도하지 않는다. 부분 산출물을 직접 열어 어디까지 됐는지 확인하고 `_workspace/{slug}/errors.md` 에 적은 뒤 사용자에게 알린다. 사용량 한도면 풀리는 시각도 알린다 |
| VARCO 401·크레딧 부족(종료 코드 10·11) | 워크플로가 `halted` 로 멈춘다. 키나 크레딧 문제를 사용자에게 알리고 해결 뒤 재개한다 |
| VARCO 422(종료 코드 12) | 담당 에이전트가 파라미터를 고친다. 워크플로의 재작업 한 번으로 안 되면 `qa_failed` 로 남기고 보고한다 |
| 예산 초과(종료 코드 3) | 그 에셋은 `budget_blocked`. 사용자에게 추가 예산을 묻거나 P1·P2 를 줄인다 |
| 워크플로 `agent()` 가 null | 스크립트가 `failed` 로 기록한다. 보고서에 누락으로 적고, 필요하면 해당 에셋만 다시 돌린다 |
| 기획 문서끼리 충돌 | 지우지 않는다. director 가 `01_director_review.md` 에 양쪽 근거를 적고 결정한다 |
| 절반이 넘는 에이전트 실패 | 사용자에게 알리고 계속할지 묻는다 |
| 리더가 빈칸을 메워야 할 때 | 직접 확인한 사실만 반영한다. 에이전트가 내렸어야 할 판단(무엇을 왜 뺐는지)은 추측해 채우지 않는다 |

## 후속 요청 처리

| 요청 예 | 다시 돌릴 범위 |
| --- | --- |
| "컨셉을 바꾸자", "기획만 다시" | 1단계부터. 이미 만든 에셋과 코드가 쓸모없어질 수 있다고 먼저 알린다 |
| "밸런스 수정", "적이 너무 세" | systems·balance 만 다시 실행 → `data/balance` 재승격 → engineer 에게 알림 → 밸런스 구현 대조 |
| "대사 추가", "시나리오 수정" | narrative → 매니페스트에 음성·현지화 에셋 추가(asset-producer) → 크레딧 승인 → 3단계를 해당 에셋만 |
| "사운드만 다시", "이 에셋 재생성" | 3단계를 해당 id 만 `items` 에 넣어 실행. 바뀌지 않은 호출은 `resumeFromRunId` 캐시를 쓴다 |
| "언어 추가" | `run_meta.target_langs` 수정 → asset-producer 가 현지화 에셋 추가 → 3단계 → engineer 가 언어 전환 확인 |
| "드라이런 말고 실제로 생성" | 키 확인 → 2단계 크레딧 승인(live) → 3단계 전체 |
| "버그 고쳐줘", "QA 다시" | 4단계 한 쌍만. 버그 파일 경로를 넘긴다 |
| "스토어 이미지 다시" | marketing-artist 만 |
| "출시 판정 다시" | 5단계 |

## 테스트 시나리오

### 정상 흐름 — 웹, 드라이런, 작은 게임

1. 입력: "3분짜리 네온 도시 드리프트 레이싱 웹게임 만들어줘". 키 없음 → `varco_mode: dry-run`, `engine: web`.
2. 1단계: director 컨셉 → 사용자 승인 → 다섯 명 병렬 기획 → balance 와 systems 가 두 번 주고받아 수치 확정 → director 통합 리뷰에서 레벨·시나리오 불일치 한 건 해결 → 동결·승격.
3. 2단계: 매니페스트 약 25건(효과음 10, 환경음 3, 대사 묶음 4, 3D 2, 현지화 2, 배경음악 1(수동), 마케팅 3). 견적 표를 보여 주고 "드라이런으로 진행" 승인.
4. 3단계: 워크플로가 production 에셋 22건을 처리한다. 요청 명세 검증 통과 21건(`dry-run`), 배경음악 1건 `manual_pending`.
5. 4단계: engineer 가 모듈 5개를 만들고 qa 가 모듈마다 검사한다. 자리표시 에셋으로 실행된다.
6. 5단계: 네 가지 검사 뒤 director 판정. 예상 결과: `games/neon-drift/RELEASE_REPORT.md` 에 "드라이런이라 실제 에셋 없음"을 남은 위험으로 적은 조건부 판정.

### 오류 흐름 1 — 제작 중 인증 실패

1. 3단계 실제 호출 중 voice-director 가 종료 코드 10을 받아 `auth_failed` 를 반환한다.
2. 워크플로가 `halted` 를 기록하고 남은 에셋을 호출하지 않는다. 이미 끝난 에셋은 결과가 남는다.
3. 리더는 매니페스트를 갱신하고 "키가 잘못됐다. `.env` 확인 후 알려 달라"고 보고한다. 사용자가 고치면 `resumeFromRunId` 로 재개하고, 이미 끝난 호출은 캐시를 쓴다.

### 오류 흐름 2 — 개발 중 엔지니어 무응답

1. 4단계에서 engineer 가 모듈 3 도중 응답하지 않는다.
2. 리더가 SendMessage 로 상태를 묻는다. 답이 없으면 `engineer-b` 를 같은 유형으로 실행하고 `04_engineer_plan.md`, 마지막 qa 보고서, 코드 경로를 넘긴다.
3. qa 에게 새 주소(`engineer-b`)를 알린다. 최종 보고서에 "모듈 3 담당 교체"를 적는다.
