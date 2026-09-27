---
name: game-qa-testing
description: "게임 프로토타입의 기능·통합 QA 방법. GDD 와 화면 흐름으로 테스트 계획을 세우고, 엔지니어가 모듈을 끝낼 때마다 바로 검사하고(점진 QA), 버그 리포트·모듈 보고서·최종 회귀 보고서를 쓴다. 웹은 Playwright MCP 로 실제 플레이·data-testid 조작·window.__game 상태 확인·콘솔 오류 수집·스크린샷을 하고, Unity 는 배치 모드 테스트 결과를 읽는다. 밸런스 CSV↔코드, 문자열 키↔코드, 에셋 경로↔파일, 화면 흐름↔씬 전환, 상태 전이↔코드를 양쪽 함께 읽어 대조한다. 게임 QA, 테스트 계획, 버그 리포트, 회귀 테스트, '플레이해 보고 버그 찾아줘', 'QA 다시 돌려줘' 요청에 사용한다. 에셋 파일 자체의 품질 측정은 asset-qa-check, 밸런스 수치의 적정성 판단은 balance-simulation 이 맡는다."
---

# 게임 QA — 모듈마다 바로, 연결된 양쪽을 함께

게임 QA 는 4단계에서 엔지니어와 한 쌍으로 일하고, 5단계에서 최종 회귀 테스트를 한다. 두 가지를 기본으로 삼는다.

1. **다 만든 뒤가 아니라 모듈이 끝날 때마다 검사한다.** 초기 모듈의 잘못된 약속(데이터 형식, 이벤트 이름, 화면 id)이 뒤 모듈로 번지기 전에 잡기 위해서다.
2. **존재가 아니라 대조를 본다.** "로더가 있다"가 아니라 "로더가 읽은 hp 가 CSV 의 hp 와 같다", "버튼이 있다"가 아니라 "btn_start 를 누르면 scr_game 으로 간다"를 확인한다. 한쪽 코드만 읽으면 양쪽 약속이 어긋난 버그를 놓친다.

파일 위치와 형식은 `.claude/skills/varco-game-studio/references/contracts.md` 7절(QA 산출물)을 따른다.

## 1. 테스트 계획 `games/{slug}/qa/test-plan.md`

엔지니어가 첫 모듈을 끝내기 전에 쓴다. 근거 문서의 절을 테스트마다 적어, 기획이 바뀌면 어떤 테스트를 고칠지 찾을 수 있게 한다.

```markdown
# 테스트 계획 — {게임 제목}

## 범위와 환경
- 엔진: web | unity, 실행 방법: …
- 제외: (컨셉의 "만들지 않을 것")

## 합격 기준
- S1·S2 열린 버그 0건, 콘솔(실행) 오류 0건, 누락 문자열 0건, 코드가 참조하는 누락 에셋 0건(자리표시 대체는 따로 집계)

## 테스트 케이스
| id | 모듈 | 전제 | 절차 | 기대 결과 | 근거 | 자동화 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-combat-01 | combat | ?scene=scr_game&seed=1 | 슬라임에게 공격 3회 | slime hp 40→0, 처치, gold +7 | systems.md §전투, enemies.csv | Playwright |
| TC-flow-01 | ui-l10n | 첫 화면 | btn_start 클릭 | __game.scene == 'scr_game' | ux.md §화면 흐름 | Playwright |
```

테스트 케이스를 뽑는 곳:
- **GDD·systems.md:** 규칙과 공식마다 정상값·경계값(0, 최대, 음수 입력) 한 개씩
- **ux.md 화면 흐름:** 화면 사이 전환 하나당 한 개. 모든 화면에서 나가는 길이 있는지(막다른 화면은 S1)
- **ux.md HUD:** 요소 id 마다 표시 값의 출처(상태 값)와 갱신 시점
- **levels.md:** 레벨마다 시작·목표 달성·실패
- **dialogue.csv:** 장면마다 대사 재생, 자막 문구, 화자 이름
- **엔지니어 모듈 계획의 완료 기준:** 한 줄마다 한 개

## 2. 모듈 검사 절차

engineer 에게서 "[모듈 완료] …" 메시지를 받으면 바로 시작한다.

1. **바뀐 파일과 근거 문서를 함께 읽는다.** 코드가 소비자라면 생산자(CSV, strings, manifest, ux.md)를 같이 연다.
2. **정적 대조를 돌린다.**
   - `python3 .claude/skills/game-qa-testing/scripts/check_data_contracts.py --game-dir games/{slug} --out _workspace/{slug}/04_gameqa_contracts.json` — 없는 string_id·line_id 는 오류, 하드코딩 의심·미사용 열은 경고
   - `python3 .claude/skills/balance-simulation/scripts/check_balance_tables.py games/{slug}/data/balance` — 밸런스 표 형식
   - `python3 .claude/skills/game-narrative/scripts/check_story_data.py --game-dir games/{slug}` — 대사·문자열 CSV 형식
   - 에셋 참조가 바뀐 모듈이면 `python3 .claude/skills/asset-qa-check/scripts/audit_assets.py --game-dir games/{slug}` 의 `code_refs_exist`
3. **실행해서 테스트 케이스를 돌린다.** 웹은 5절, Unity 는 6절.
4. **결과를 쓴다.** 모듈 보고서와 버그 파일(3·4절).
5. **engineer 에게 알린다.** 통과면 "[검사 통과] {모듈}", 실패면 버그 목록(파일 경로, 심각도, 한 줄 요약).
6. **재검사:** "[수정 완료] BUG-…" 를 받으면 해당 테스트와 인접 테스트를 다시 돌리고 버그 상태를 `verified` 로 바꾸거나 다시 `open` 으로 돌린다. 한 모듈에서 수정·재검사가 3회를 넘으면 리더에게 올린다.

## 3. 버그 리포트 `games/{slug}/qa/bugs/BUG-{NNN}.md`

형식은 계약서 7-2절이다. 번호는 `ls games/{slug}/qa/bugs` 로 마지막 번호 다음을 쓴다. 쓰기 전에 같은 증상의 버그가 있는지 찾아 중복을 만들지 않는다.

| 심각도 | 기준 | 예 |
| --- | --- | --- |
| S1 | 진행 불가, 크래시, 데이터 손상 | 결승선을 지나도 결과 화면이 안 뜬다, 막다른 화면 |
| S2 | 핵심 기능이 기획과 다름 | CSV 의 hp 가 아니라 코드의 상수를 씀, 보상이 안 들어옴 |
| S3 | 부분 오류, 우회 가능 | 특정 언어에서만 문구 누락, 효과음 하나가 자리표시 |
| S4 | 외관·문구 | 버튼 글자가 살짝 넘침 |

버그마다 **근거**(스크린샷 경로, `__game` 스냅샷, 콘솔 오류, 파일:줄)와 **관련 계약**(어느 생산자 ↔ 어느 소비자)을 적는다. 재현 절차는 URL 파라미터(`?scene=…&seed=…`)까지 적어 누가 해도 같은 결과가 나오게 한다.

## 4. 보고서

**모듈 보고서** `_workspace/{slug}/04_gameqa_module-{모듈}.md`

```markdown
# 모듈 QA — 02 combat (1회차)
- 판정: 통과 | 실패
- 테스트: 통과 7 / 실패 1 / 미검증 1(사유)
- 정적 대조: check_data_contracts 오류 0, 경고 2(하드코딩 의심 1 → BUG-014)
- 새 버그: BUG-014(S2) …
- 자리표시로 대신한 에셋: sfx_hit
- 스크린샷: qa/screenshots/combat-01.png
```

**최종 회귀 보고서** `games/{slug}/qa/reports/regression.md`(5단계)
- 전체 테스트 케이스 통과율과 실패 목록
- 버그 집계: 심각도 × 상태(open, fixed, verified, wontfix)
- 정적 대조 결과 요약, 콘솔 오류 수, 누락 문자열·자리표시 에셋 수(`__game.missingStrings`, `missingAssets`)
- 마케팅용 스크린샷 목록(7절)
- 출시 기준(계약서 9절) 중 QA 가 판단할 수 있는 항목의 통과·실패

"미검증"은 통과로 세지 않는다. 테스트를 못 돌린 이유를 적는다.

## 5. 웹 — Playwright MCP 로 실제 플레이

1. **서버를 띄운다.** Bash 를 백그라운드로 실행한다(`run_in_background`).
   `python3 -m http.server 8765 --directory games/{slug}`
   localhost 는 프록시를 거치지 않는다. 포트가 쓰이고 있으면 다른 번호를 쓴다.
2. **도구를 한 번에 불러온다.** ToolSearch 로
   `select:mcp__plugin_playwright_playwright__browser_navigate,mcp__plugin_playwright_playwright__browser_resize,mcp__plugin_playwright_playwright__browser_click,mcp__plugin_playwright_playwright__browser_press_key,mcp__plugin_playwright_playwright__browser_type,mcp__plugin_playwright_playwright__browser_evaluate,mcp__plugin_playwright_playwright__browser_wait_for,mcp__plugin_playwright_playwright__browser_take_screenshot,mcp__plugin_playwright_playwright__browser_console_messages,mcp__plugin_playwright_playwright__browser_snapshot,mcp__plugin_playwright_playwright__browser_close`
3. **연다.** `browser_resize` 1280×720 → `browser_navigate` `http://localhost:8765/web/index.html?seed=1&lang=ko`
4. **준비를 기다린다.** `browser_evaluate` 로 `() => window.__game?.ready === true` 를 확인한다. false 면 `browser_wait_for`(time 1) 뒤 다시, 10회 넘으면 실패로 기록하고 콘솔을 본다.
5. **조작한다.** UI 요소는 ux.md 의 요소 id 가 `data-testid` 로 붙어 있다. `browser_click` 의 target 에 `[data-testid="btn_start"]` 처럼 선택자를 준다. 게임 입력은 `browser_press_key`(ArrowLeft, Space 등). 캔버스에 그린 요소는 `__game.ui['lbl_lap']` 으로 상태를 읽는다.
6. **확인한다.** `browser_evaluate` 로 `() => window.__game.snapshot()` 을 받아 `scene`, `state`, `errors`, `missingAssets`, `missingStrings` 를 기대 결과와 대조한다. 화면 글자는 표시된 텍스트가 아니라 상태 값과 strings 파일을 대조한다.
7. **증거를 남긴다.** `browser_take_screenshot`(scale css, filename `games/{slug}/qa/screenshots/{모듈}-{nn}.png`), `browser_console_messages`(level error). 콘솔 오류는 한 건이라도 버그 후보다.
8. **언어 전환:** 대상 언어마다 `?lang=en` 으로 다시 열어 주요 화면의 `missingStrings` 가 비었는지 본다.
9. 끝나면 `browser_close`, 서버 작업을 중지한다.

도구 호출이 2~3회 연속 실패하면 같은 호출을 반복하지 말고 모듈 보고서에 "자동화 불가(사유)"로 적고 리더에게 알린다.

## 6. Unity — 배치 모드 테스트

명령은 `.claude/skills/game-prototype-dev/references/unity.md` 8절을 따른다. 엔지니어가 만든 테스트에 더해, 테스트 계획의 케이스 중 자동화할 수 있는 것을 PlayMode 테스트로 요청하거나 직접 추가한다(`Assets/Game/Tests/`). 결과 요약:

```bash
python3 .claude/skills/game-qa-testing/scripts/unity_results.py _workspace/{slug}/04_unity_editmode.xml _workspace/{slug}/04_unity_playmode.xml
```

결과 파일이 없으면 테스트가 돌지 않은 것이다. 로그에서 `error CS`, `license`, `Aborting batchmode` 를 찾아 원인을 버그나 보고서에 적는다. 요소 찾기는 GameObject 이름(= ux.md 요소 id), 화면은 씬 이름(= 화면 id), 상태는 `-qaState` 스냅샷 JSON 으로 한다.

## 7. 마케팅용 스크린샷

5단계 회귀 테스트에서 핵심 장면(타이틀, 코어 루프 한가운데, 보스·클라이맥스, 결과 화면)을 1920×1080 으로 다시 찍어 `games/{slug}/qa/screenshots/marketing-{nn}.png` 에 둔다(`browser_resize` 1920×1080, scale css). 디버그 표시가 보이면 `?debug=0` 같은 파라미터로 끄도록 engineer 에게 요청한다. marketing-artist 가 이 파일로 스토어 이미지를 만든다.

## 8. 통합 정합성 체크리스트

모듈마다 해당하는 줄을 확인한다. 한쪽만 보고 체크하지 않는다.

| 생산자 | 소비자 | 확인할 것 |
| --- | --- | --- |
| `data/balance/*.csv`, `_schema.json` | 코드 로더와 사용처 | 모든 표를 읽는가, 읽은 값이 실제 동작에 쓰이는가(`__game.state` 값 = CSV 값), 같은 숫자를 코드에 박지 않았는가 |
| `data/strings/*.json`, `ui_strings.csv` | 코드의 `t()` 호출, 화면 | 코드가 쓰는 키가 모두 있는가, 언어 전환 시 누락 0, `max_len` 초과로 잘리지 않는가 |
| `manifest.json`, `assets/` | 에셋 로더 | 경로 규칙이 같은가, 없을 때 자리표시로 넘어가고 `missingAssets` 에 남는가 |
| `ux.md` 화면 흐름 | 씬 전환 코드 | 문서의 모든 전환이 코드에 있는가, 코드에만 있는 전환은 없는가, 막다른 화면이 없는가 |
| `ux.md` 요소 id | `data-testid`, GameObject 이름 | id 가 같은가(다르면 자동화가 깨진다) |
| `systems.md` 상태 전이(예: 대기→전투→보상) | 상태를 바꾸는 코드 | 정의된 전이가 모두 실행되는가, 정의되지 않은 전이가 없는가, 중간 상태에서 최종 상태로 가는 처리가 빠지지 않았는가 |
| `dialogue.csv`, 얼굴 JSON | 대사 재생 코드 | 자막이 `line_id` 문구와 같은가, 음성·얼굴 파일 이름이 `line_id` 와 같은가, 얼굴이 소리보다 늦지 않은가 |
| 입력 설계(ux.md 입력) | 입력 처리와 HUD 안내 | 안내한 키가 실제로 동작하는가 |

## 하지 말 것

- 게임 코드를 직접 고치지 않는다. 테스트 코드와 QA 문서만 쓴다. 고칠 곳은 버그에 파일:줄로 적는다.
- 기대 결과를 코드에서 가져오지 않는다. 기대 결과의 출처는 기획 문서와 data 파일이다. 코드에서 가져오면 틀린 구현을 정답으로 만든다.
- "대체로 잘 동작함" 같은 인상 평가를 쓰지 않는다. 케이스마다 통과·실패·미검증과 근거를 쓴다.
