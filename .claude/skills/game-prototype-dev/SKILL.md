---
name: game-prototype-dev
description: "확정된 기획 문서·데이터·VARCO 에셋으로 플레이 가능한 게임 프로토타입을 만드는 방법. 웹(HTML5, Phaser 3·three.js, 빌드 도구 없음)과 Unity 6(배치 모드 빌드·테스트)을 지원한다. 데이터 주도 구현(밸런스 CSV·문자열 JSON), 매니페스트 경로로 에셋 불러오기와 자리표시 대체, 대사 음성·얼굴 애니메이션 재생, QA 자동화용 디버그 훅, 모듈 계획(04_engineer_plan.md)과 QA 인계 형식을 다룬다. 프로토타입 구현, 게임 코드 작성, 에셋 연동, 버그 수정, 'web/ 또는 unity/ 코드 고쳐줘' 요청에 사용한다. 기획 문서 작성이나 에셋 생성은 이 스킬의 범위가 아니다."
---

# 게임 프로토타입 개발

기획 문서가 약속한 코어 루프를 실제로 플레이할 수 있게 만든다. 목표는 완성품이 아니라 "기획이 재미있는지, 에셋이 게임 안에서 제대로 들리고 보이는지"를 확인할 수 있는 빌드다.

## 먼저 읽을 것

1. `_workspace/{slug}/run_meta.json` — `engine`(web | unity), `varco_mode`, 대상 언어
2. `games/{slug}/docs/GDD.md` 와 거기서 링크한 `systems.md`, `levels.md`, `ux.md`
3. `games/{slug}/data/` — 밸런스 CSV 와 `_schema.json`, `strings/*.json`, `dialogue.csv`, `characters.csv`
4. `games/{slug}/manifest.json` — 에셋 경로와 상태
5. `.claude/skills/varco-game-studio/references/contracts.md` — 4·5·6절(데이터·매니페스트·에셋 위치)
6. 엔진별 참조 문서 하나만: 웹이면 `references/web.md`, Unity 면 `references/unity.md`

## 원칙

### 1. 수치는 데이터에서 읽는다

밸런스 수치(체력, 공격력, 쿨다운, 보상)는 `data/balance/*.csv` 에서 읽는다. 코드에 숫자를 직접 적지 않는다. 기획 수치와 구현 수치가 갈라지면 밸런스 분석가의 시뮬레이션이 실제 게임을 설명하지 못하고, 밸런스를 고칠 때마다 코드를 뒤져야 한다. 불러올 때 `_schema.json` 의 타입과 최솟값으로 검사해, 잘못된 값이면 조용히 넘어가지 말고 화면과 콘솔에 오류를 띄운다. game-qa 는 `check_data_contracts.py` 로 CSV 값과 같은 숫자 리터럴을 찾아낸다.

레이아웃 픽셀, 애니메이션 프레임 수처럼 밸런스 표에 없는 구현 상수는 코드 상단 한 곳에 이름 붙인 상수로 모은다.

### 2. 화면 글자는 문자열 키로 쓴다

UI 와 대사는 `strings/{lang}.json` 의 키(`ui.menu.start`, `ch1_intro_003`)로만 가져온다. 한국어 문장을 코드에 적지 않는다. 키가 없으면 키 이름을 그대로 화면에 보여 준다(빈칸보다 찾기 쉽다). 대상 언어 파일에 키가 없으면 `ko.json` 으로 대신하고 `missingStrings` 에 기록한다. `{player_name}` 같은 자리표시자는 불러온 뒤 치환한다.

### 3. 에셋은 매니페스트 경로로 부르고, 없으면 자리표시로 대신한다

에셋 경로는 계약서 6절 규칙(`assets/audio/sfx/{id}_01.wav`, `assets/audio/voice/{lang}/{line_id}.wav` 등)을 따른다. 가장 확실한 방법은 실행 중에 `manifest.json` 을 읽어 id 로 경로를 찾는 것이다. 드라이런이거나 파일이 없거나 `manual_pending`(배경음악)이면 자리표시로 대신하고 게임은 계속 돈다.

| 에셋 | 자리표시 |
| --- | --- |
| 소리 | 무음(길이 0.1초) + 화면 구석에 에셋 id 를 잠깐 표시하는 디버그 표시 |
| 대사 음성 | 무음 + 자막은 정상 표시, 자막 표시 시간은 글자 수로 계산 |
| 얼굴 애니메이션 | 입 벌림(jawOpen) 사인파 |
| 3D 모델 | 회색 상자(크기는 기획 문서 기준) |
| 이미지 | 회색 사각형 + 에셋 id 글자 |

대신 쓴 에셋은 모두 `missingAssets` 목록에 넣는다. QA 와 에셋 감사가 이 목록을 본다.

### 4. VARCO 키를 게임 코드에 넣지 않는다

프로토타입은 미리 만든 에셋만 쓴다. 클라이언트 코드에서 VARCO API 를 직접 부르면 키가 그대로 노출된다. 기획이 실행 중 호출(예: 채팅 실시간 번역)을 꼭 요구하면, 키를 `.env` 에서 읽는 작은 로컬 프록시를 따로 두고 리더에게 먼저 알린다. 그 프록시는 배포물에 넣지 않는다.

### 5. 모듈 하나를 끝내면 바로 QA 에 넘긴다

전부 만든 뒤 한꺼번에 검사하면 초기 모듈의 잘못된 약속(데이터 형식, 이벤트 이름)이 뒤 모듈로 번진다. 모듈 하나를 완료 기준까지 끝내면 자체 점검을 하고 qa 에게 넘긴다.

### 6. 자동화할 수 있게 만든다

QA 가 사람 손 없이 검사할 수 있도록 디버그 훅을 둔다.
- UI 요소 id: `docs/ux.md` 의 화면 id(`scr_`)와 요소 id(`btn_`, `lbl_`, `bar_`, `ico_`)를 그대로 쓴다. 웹은 DOM 요소의 `data-testid` 속성에 넣는다. 캔버스에 그리는 UI 라면 DOM 오버레이에 붙이거나, `window.__game.ui[요소 id]` 로 같은 id 의 상태(보이는지, 표시 값, 누를 수 있는지)를 노출한다. Unity 는 GameObject 이름을 요소 id 로 짓는다. qa 는 이 id 로 요소를 찾으므로 id 를 바꾸면 테스트가 깨진다.
- 상태 노출: 웹은 `window.__game`, Unity 는 상태 스냅샷 JSON
- 결정적 실행: URL 파라미터나 명령줄 인자로 `seed`, `scene`, `lang`, `timeScale` 을 받는다
- 오류 수집: 잡히지 않은 오류를 `errors` 목록에 쌓는다

### 7. 범위를 지킨다

GDD 의 코어 루프와 컨셉의 "만들 것"만 만든다. 하고 싶은 기능이 생기면 모듈 계획의 "하지 않을 것"에 적고 리더에게 알린다.

## 모듈 계획 `_workspace/{slug}/04_engineer_plan.md`

```markdown
# 모듈 계획 — {게임 제목} ({engine})

## 실행 방법
{서버·빌드·테스트 명령}

## 모듈
| # | 모듈 | 내용 | 근거 문서 | 읽는 데이터 | 쓰는 에셋 | 완료 기준(측정 가능하게) | 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 00 | boot | 부트, 로더, 자리표시, 디버그 훅 | contracts 4~6절 | 전부 | 전부 | 모든 CSV·strings 를 읽고 __game.ready=true, 콘솔 오류 0 | 예정 |
| 01 | core-loop | ... | GDD §코어 루프 | ... | ... | ... | |
| 02 | {시스템} | 전투·경제 등 | systems.md §... | balance/*.csv | sfx_* | ... | |
| 03 | levels | 레벨 구성 | levels.md | ... | amb_*, mdl_* | ... | |
| 04 | ui-l10n | HUD·메뉴·언어 전환 | ux.md | ui_strings, strings/* | img_* | 모든 화면 전환 가능, 언어 전환 시 누락 키 0 | |
| 05 | audio-voice | 효과음·환경음·대사·얼굴 | levels.md §사운드 구역, dialogue.csv | dialogue.csv | vo_*, face_* | 대사 재생 시 자막·얼굴 싱크 ±0.1초 | |
| 06 | polish | 저장, 설정, 접근성 | ux.md §접근성 | | | | |

## 하지 않을 것
- ...
```

완료 기준은 qa 가 그대로 테스트로 옮길 수 있게 쓴다. "전투가 잘 된다"가 아니라 "슬라임 hp 40, 공격 6 을 CSV 에서 읽어 3회 공격에 처치된다"처럼 쓴다.

## QA 인계 메시지

모듈을 끝내면 qa 에게 아래 형식으로 보낸다. 같은 내용을 계획 문서의 해당 행에도 적는다.

```
[모듈 완료] 02 combat
- 바뀐 파일: web/src/combat.js, web/src/data.js
- 실행: python3 -m http.server 8765 --directory games/{slug} → http://localhost:8765/web/index.html?scene=combat&seed=1
- 완료 기준 자체 점검: ① CSV 값 로드 통과(__game.state.enemies.slime.hp=40) ② 처치 시 보상 7 골드 통과
- 자리표시로 대신한 에셋: sfx_hit(드라이런)
- 알려진 한계: 보스 패턴은 03 에서
- 확인할 상태: window.__game.state.combat
```

## 넘기기 전 자체 점검

1. 문법 검사: 웹은 `for f in $(find games/{slug}/web -name '*.js' -not -path '*/vendor/*'); do node --check "$f" || echo "FAIL $f"; done`, Unity 는 배치 모드 컴파일 로그에서 `error CS` 가 0건인지.
2. 데이터 계약: `python3 .claude/skills/game-qa-testing/scripts/check_data_contracts.py --game-dir games/{slug}` 의 errors 0건.
3. 밸런스 표 형식: `.claude/skills/balance-simulation/scripts/check_balance_tables.py` 가 있으면 실행한다.
4. 실행 확인: 웹은 서버를 띄워 페이지를 열고 `__game.ready` 와 `errors` 를 본다(Playwright MCP 사용법은 `game-qa-testing` 스킬). Unity 는 EditMode 테스트를 돌린다.

## 버그를 받았을 때

1. `games/{slug}/qa/bugs/BUG-{NNN}.md` 를 읽고 재현한다.
2. 고친 뒤 버그 파일의 `상태` 를 `fixed` 로 바꾸고 "수정: 파일:줄, 원인 한 줄"을 덧붙인다. `verified` 는 qa 만 쓴다.
3. qa 에게 "[수정 완료] BUG-012 …"를 보낸다.
4. 같은 모듈에서 수정·재검사가 3회를 넘으면 qa 가 리더에게 올린다. 그때까지 고치지 못한 이유를 버그 파일에 적어 둔다.

## 산출물

| 무엇 | 위치 |
| --- | --- |
| 코드 | `games/{slug}/web/` 또는 `games/{slug}/unity/` |
| 모듈 계획·진행 | `_workspace/{slug}/04_engineer_plan.md` |
| 빌드 로그 | `_workspace/{slug}/04_engineer_build.log` |

4단계가 끝나 리더가 빌드를 동결하면(`freeze_04.sha`) 그 뒤 수정은 리더 승인 후에만 한다.
