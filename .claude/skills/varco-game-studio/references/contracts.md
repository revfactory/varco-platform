# 산출물 계약서 — 에이전트끼리 주고받는 파일의 위치와 형식

이 문서는 VARCO 게임 스튜디오 하네스에서 에이전트가 만들고 읽는 모든 파일의 위치와 형식을 정한다. 에이전트는 다른 에이전트의 산출물을 읽을 때 이 문서의 형식을 믿고 읽는다. 형식을 바꿔야 하면 이 문서를 먼저 고치고 리더에게 알린다. 한쪽만 바꾸면 읽는 쪽이 조용히 틀린 값을 쓰게 된다.

## 목차

1. [경로 규칙](#1-경로-규칙)
2. [run_meta.json — 실행 설정](#2-run_metajson--실행-설정)
3. [기획 산출물](#3-기획-산출물)
4. [데이터 파일 — 코드와 에셋이 읽는 원본](#4-데이터-파일--코드와-에셋이-읽는-원본)
5. [에셋 매니페스트 manifest.json](#5-에셋-매니페스트-manifestjson)
6. [에셋 저장 위치와 이름](#6-에셋-저장-위치와-이름)
7. [QA 산출물](#7-qa-산출물)
8. [동결과 승격](#8-동결과-승격)
9. [출시 판정 기준](#9-출시-판정-기준)

---

## 1. 경로 규칙

| 구분 | 경로 | 용도 |
| --- | --- | --- |
| 게임 식별자 | `{slug}` | 영문 소문자·숫자·하이픈. 예: `neon-drift`. 한 번 정하면 바꾸지 않는다. |
| 작업 폴더 | `_workspace/{slug}/` | 초안, 중간 산출물, 장부, 워크플로 결과. 지우지 않고 남겨 사후 검증에 쓴다. |
| 확정 폴더 | `games/{slug}/` | 동결을 거쳐 승격된 확정본. 다음 단계는 여기서 읽는다. |
| 크레딧 장부 | `_workspace/{slug}/varco_ledger.jsonl` | 모든 VARCO 호출 기록. `varco_client.py` 만 쓴다. |

**작업 폴더 파일 이름:** `{단계}_{에이전트}_{산출물}.{확장자}`

- 단계 번호: `00` 입력, `01` 기획, `02` 에셋 명세, `03` 에셋 제작, `04` 개발, `05` 출시 준비
- 에이전트 약칭: `director`, `systems`, `narrative`, `level`, `ux`, `balance`, `producer`, `sound`, `voice`, `visual`, `l10n`, `marketing`, `engineer`, `assetqa`, `gameqa`
- 예: `01_systems_spec.md`, `03_assetqa_sfx_sword_swing.json`, `04_gameqa_module-combat.md`
- 확정본을 고쳐야 하면 기존 파일을 덮지 말고 `_v2`, `_v3` 을 붙인 새 파일을 만든다.

**확정 폴더 구조:**

```
games/{slug}/
├── docs/            concept.md, GDD.md, systems.md, narrative.md, levels.md, ux.md, balance-report.md
├── data/            balance/*.csv, balance/_schema.json, characters.csv, dialogue.csv, ui_strings.csv,
│                    glossary.csv, strings/{lang}.json
├── assets/          audio/, anim/, models/, images/ (6절)
├── manifest.json    승인된 에셋 매니페스트 + 제작 상태
├── web/ 또는 unity/ 프로토타입 (run_meta.engine 에 따라)
├── qa/              test-plan.md, bugs/*.md, reports/*.md
├── marketing/       스토어 이미지, 키 아트, 설명 문구
└── RELEASE_REPORT.md
```

## 2. run_meta.json — 실행 설정

위치: `_workspace/{slug}/run_meta.json`. 리더(메인 에이전트)만 쓴다. 모든 에이전트는 작업 전에 읽는다.

```json
{
  "slug": "neon-drift",
  "title": "네온 드리프트",
  "created": "2026-09-28T10:00:00+09:00",
  "engine": "web",
  "varco_mode": "dry-run",
  "budget_credits": 5000,
  "approved_scope": "all",
  "source_lang": "ko",
  "target_langs": ["en", "ja"],
  "voice_langs": ["korean"],
  "gates": "confirm",
  "allow_unknown_price": false,
  "phases_done": ["01"],
  "workflow_runs": [{"phase": "03", "runId": "wf_abc123", "at": "2026-09-28T12:00:00+09:00"}],
  "notes": []
}
```

| 필드 | 값 | 의미 |
| --- | --- | --- |
| `engine` | `web` \| `unity` | 사용자가 정하지 않으면 `web` |
| `varco_mode` | `live` \| `dry-run` | 키가 없거나 사용자가 원하면 `dry-run`. 드라이런이면 실제 호출 없이 요청 명세만 만든다. |
| `budget_credits` | 숫자 | 사용자가 승인한 크레딧 상한. 모든 실제 호출에 `--budget` 으로 넘긴다. |
| `approved_scope` | `all` \| `P0` \| `P0+P1` | 제작을 승인받은 우선순위 범위 |
| `voice_langs` | TTS 언어 | `korean`, `english`, `japanese`, `taiwanese` 중에서 고른다 |
| `allow_unknown_price` | `true` \| `false` | 단가가 공개되지 않은 API(번역, Voice-to-Face, 음성 변환 Acting)의 실제 호출을 사용자가 승인했는가. `true` 면 제작 에이전트가 `--allow-unknown-price` 를 붙인다 |
| `gates` | `confirm` \| `auto` | `confirm` 이면 컨셉과 크레딧 단계에서 사용자 승인을 받는다. 크레딧 승인은 `auto` 여도 생략하지 않는다. |

## 3. 기획 산출물

| 파일(작업 폴더) | 작성 | 승격 위치 | 필수 내용 |
| --- | --- | --- | --- |
| `01_director_concept.md` | director | `docs/concept.md` | 한 줄 소개, 장르·플랫폼, 핵심 재미, 코어 루프, 대상 플레이어, 범위(만들 것/만들지 않을 것), 성공 기준, 참고작 |
| `01_systems_spec.md` | systems | `docs/systems.md` | 시스템별 규칙, 공식, 상태 전이, 밸런스 테이블 목록 |
| `01_systems_balance/*.csv` | systems | `data/balance/*.csv` | 4-1절 형식 |
| `01_narrative_bible.md` | narrative | `docs/narrative.md` | 세계관, 캐릭터, 장면 목록, 퀘스트 |
| `01_narrative_characters.csv` | narrative | `data/characters.csv` | 4-2절 |
| `01_narrative_dialogue.csv` | narrative | `data/dialogue.csv` | 4-3절 |
| `01_narrative_glossary.csv` | narrative | `data/glossary.csv` | 4-5절 |
| `01_level_design.md` | level | `docs/levels.md` | 레벨별 목표·배치·페이싱, 사운드 구역, 필요한 프랍 목록 |
| `01_ux_spec.md` | ux | `docs/ux.md` | 화면 목록과 흐름, HUD, 입력, 접근성 |
| `01_ux_strings.csv` | ux | `data/ui_strings.csv` | 4-4절 |
| `01_balance_report.md` | balance | `docs/balance-report.md` | 시뮬레이션 방법, 결과, 판정, 수정 권고 |
| `01_balance_criteria.json`, `01_balance_sim.py`, `01_balance_result.json` | balance | (승격하지 않음) | 결과를 보기 전에 정한 판정 기준, 시뮬레이션 모델, 결과. 재현용으로 남긴다 |
| `01_director_review.md` | director | (승격하지 않음) | 문서 간 불일치 목록과 처리 결과 |
| `01_director_gdd.md` | director | `docs/GDD.md` | 전체 요약과 각 문서 링크, 확정한 결정 사항 |

## 4. 데이터 파일 — 코드와 에셋이 읽는 원본

데이터 파일은 사람이 아니라 코드와 스크립트가 읽는다. 그래서 형식을 엄격히 지킨다. 인코딩은 UTF-8(BOM 없음), 구분자는 쉼표, 첫 줄은 열 이름이다. 쉼표나 줄바꿈이 든 값은 큰따옴표로 감싼다.

### 4-1. 밸런스 테이블 `data/balance/{table}.csv`

- 첫 열은 `id`(영문 snake_case, 파일 안에서 유일)다.
- 열 이름은 영문 snake_case 다. 단위는 열 이름 뒤에 붙인다. 예: `cooldown_s`, `move_speed_px_s`, `drop_rate_pct`.
- 표마다 `data/balance/_schema.json` 에 열 설명을 적는다. 프로토타입 코드와 밸런스 시뮬레이션이 이 파일로 값을 검증한다.

```json
{
  "enemies": {
    "description": "적 기본 능력치",
    "columns": {
      "id": {"type": "string"},
      "hp": {"type": "int", "min": 1},
      "attack": {"type": "int", "min": 0},
      "move_speed_px_s": {"type": "float", "min": 0},
      "reward_gold": {"type": "int", "min": 0}
    }
  }
}
```

코드에는 밸런스 수치를 직접 적지 않고 이 CSV 에서 읽는다. 기획 수치와 구현 수치가 갈라지는 일을 막기 위해서다.

### 4-2. 캐릭터 `data/characters.csv`

| 열 | 예 | 설명 |
| --- | --- | --- |
| `speaker_id` | `hero` | 대사·음성·얼굴 애니메이션이 모두 이 값으로 캐릭터를 찾는다 |
| `name_ko` | `리아` | 표시 이름 |
| `role` | `주인공` | |
| `gender` | `female` | 목소리의 성별. `male` \| `female` \| `none`(크리처 등). 캐스팅이 이 값으로 화자를 거른다 |
| `age_band` | `20s` | 목소리의 나이대. `child` \| `teen` \| `20s` \| `30s` \| `40s` \| `50s+` \| `n/a` |
| `personality` | `냉소적이지만 동료를 챙긴다` | |
| `voice_brief` | `낮고 건조한 20대 여성, 빠른 말투` | 보이스 캐스팅 기준 |
| `voice_type` | `human` | `human` \| `creature` \| `none`. `creature` 면 사운드 변환(Conversion)으로 만든다 |
| `face_anim` | `y` | 립싱크·표정 애니메이션이 필요한가 |

### 4-3. 대사 스크립트 `data/dialogue.csv`

| 열 | 예 | 설명 |
| --- | --- | --- |
| `line_id` | `ch1_intro_003` | `{장면}_{순번}`. 문자열 키이자 음성 파일 이름 |
| `scene_id` | `ch1_intro` | |
| `speaker_id` | `hero` | `characters.csv` 에 있어야 한다 |
| `text_ko` | `또 너야? 이번엔 안 봐줘.` | 원문. 자리표시자는 `{snake_case}` 이며 `voice` 가 `none` 인 줄에만 쓴다 |
| `emotion` | `angry` | `neutral` \| `angry` \| `happy` \| `sad` \| `surprise` (Voice-to-Face 의 emotion 과 같은 값) |
| `direction` | `한숨 섞어, 작게` | 연기 지시 |
| `voice` | `tts` | `tts` \| `acting` \| `creature` \| `none`. 음성 제작 방식. `creature` 줄의 `text_ko` 에는 울음·의성어를 묘사해 적는다(예: `(낮고 긴 으르렁거림)`). 사람이 가이드를 녹음한다면 그 대본을 적는다 |
| `priority` | `P0` | 5절의 `priority` 와 같은 기준. 대사라면 `P0` 는 없으면 코어 루프를 이해할 수 없는 줄이다 |

TTS 입력 한도가 UTF-8 기준 1,200바이트(한글 약 400자)이므로 한 줄은 그보다 짧게 쓴다. 음성이 있는 대사(`voice` ≠ `none`)에는 자리표시자를 쓰지 않는다. 음성 파일에는 플레이어 이름 같은 값을 넣을 수 없기 때문이다. 형식 검사: `.claude/skills/game-narrative/scripts/check_story_data.py`

### 4-4. UI 문자열 `data/ui_strings.csv`

| 열 | 예 | 설명 |
| --- | --- | --- |
| `string_id` | `ui.menu.start` | 점으로 구분한 영문 키 |
| `context` | `메인 메뉴 시작 버튼` | 번역자가 쓰임새를 알 수 있게 적는다 |
| `text_ko` | `시작하기` | |
| `max_len` | `12` | 화면에 들어가는 최대 글자 수. 제한이 없으면 빈칸 |
| `placeholders` | `count` | 쓰는 자리표시자 이름(공백 구분) |

### 4-4-1. 화면·요소 id

`docs/ux.md` 에서 화면 id 는 `scr_`, 요소 id 는 종류 접두사(`btn_` 버튼, `lbl_` 글자, `bar_` 게이지, `ico_` 아이콘)를 붙인 영문 snake_case 로 짓는다. 웹 프로토타입은 이 값을 해당 DOM 요소의 `data-testid` 로 그대로 쓰고, 캔버스로만 그리는 요소는 `window.__game` 에 같은 id 로 상태를 노출한다. Unity 는 GameObject 이름으로 쓴다. QA 자동화가 이 id 로 요소를 찾으므로 기획·구현·테스트가 같은 id 를 써야 한다.

### 4-5. 용어집 `data/glossary.csv`

`term_ko`, 대상 언어마다 `term_{lang}`(`run_meta.target_langs` 기준. 예: 대상이 `en`, `ja` 면 `term_en`, `term_ja`), `note`, `do_not_translate` 열을 둔다. 대상 언어가 아닌 언어의 열은 만들지 않는다. 고유명사처럼 번역하지 않을 말은 `do_not_translate` 에 `y` 를 적는다. 현지화 담당은 번역 전후로 이 표를 대조한다.

### 4-6. 현지화 결과 `data/strings/{lang}.json`

```json
{ "_meta": {"lang": "en", "source": "ko", "generated_by": "mt.translate", "reviewed": false},
  "ui.menu.start": "Start",
  "ch1_intro_003": "You again? Not this time.",
  "ui.result.score": "Score: {score}" }
```

대사(`line_id`)와 UI 문자열(`string_id`)을 한 파일에 담는다. 원문 언어도 `ko.json` 으로 만든다. 코드는 이 파일만 읽는다.

드라이런이면 번역 대신 `"[en] 시작하기"` 처럼 `[{lang}] 원문` 으로 채워 파일 구조만 만든다. QA 는 이 표시가 실제 모드 결과에 남아 있으면 실패로 잡는다.

## 5. 에셋 매니페스트 manifest.json

작업본은 `_workspace/{slug}/02_producer_manifest.json`, 승인본은 `games/{slug}/manifest.json` 이다. 검증 스크립트: `.claude/skills/asset-manifest/scripts/validate_manifest.py`. 견적 스크립트: `.claude/skills/varco-api/scripts/estimate_cost.py`.

```json
{
  "game": "neon-drift",
  "version": 1,
  "varco_mode": "dry-run",
  "budget_credits": 5000,
  "assets": [
    {
      "id": "sfx_sword_swing",
      "category": "sfx",
      "owner": "sound-designer",
      "phase": "production",
      "priority": "P0",
      "source_ref": "docs/systems.md#근접-공격",
      "brief": "가벼운 단검을 빠르게 휘두르는 소리. 연타에 쓰므로 변형 4개가 필요하다.",
      "inputs": [],
      "steps": [
        {"api": "sound.text2sound", "params": {"prompt": "quick light dagger swing whoosh", "num_sample": 3, "version": "v2"}},
        {"api": "sound.variation", "input_from": "best_of_previous", "params": {"num_sample": 4, "strength": 0.8}}
      ],
      "output": {"dir": "assets/audio/sfx", "basename": "sfx_sword_swing", "format": "wav", "count": 5},
      "acceptance": {"duration_s": [0.1, 2.0], "channels": null, "loop": false, "peak_dbfs_max": -1.0},
      "est_credits": 75,
      "status": "planned",
      "result": null
    }
  ]
}
```

| 필드 | 규칙 |
| --- | --- |
| `id` | 영문 snake_case, 매니페스트 안에서 유일. 분류 접두사를 붙인다: `sfx_`, `amb_`, `crv_`(크리처 음성), `bgm_`, `vo_`(대사 음성), `face_`, `mdl_`, `img_`, `l10n_`, `mkt_` |
| `category` | `sfx` \| `ambience` \| `creature_voice` \| `music` \| `voice_line` \| `face_anim` \| `model_3d` \| `image` \| `localization` \| `marketing` |
| `owner` | 에이전트 이름: `sound-designer` \| `voice-director` \| `visual-artist` \| `localization-specialist` \| `marketing-artist` |
| `phase` | `production`(3단계 워크플로에서 제작) \| `release`(5단계에서 마케팅 아티스트가 제작) |
| `priority` | `P0` 출시 필수(없으면 코어 루프가 성립하지 않거나 이해할 수 없다) \| `P1` 있으면 좋음 \| `P2` 여유가 있을 때 |
| `source_ref` | 이 에셋이 필요한 근거. 확정 폴더 기준 경로와 앵커 또는 `data/dialogue.csv:{line_id}` |
| `inputs` | 제작에 필요한 기존 파일(사용자 제공 이미지, 녹음 파일 등). 없으면 빈 배열 |
| `steps` | 순서대로 실행할 호출. `api` 는 `varco_catalog.py` 의 id 또는 `manual.*`. 앞 단계 결과를 쓰면 `input_from` 에 `previous` 또는 `best_of_previous` |
| `output` | 확정 폴더 기준 저장 위치. 결과가 여러 개면 `{basename}_01.{format}` 처럼 번호를 붙인다. `count` 는 확정 폴더에 남는 최종 파일 수다(예: 원본 하나를 고르고 변형 4개를 만들면 5) |
| `acceptance` | 에셋 QA 가 검사할 기준(7-1절). 알 수 없는 항목은 `null` |
| `lines` | 대사 음성만 쓴다. 한 에셋에 묶을 `line_id` 목록. `steps` 는 줄마다 반복할 호출이고 `output.basename` 은 `{line_id}` 로 둔다 |
| `status` | `planned` → `generated` \| `dry-run` \| `manual_pending` → `qa_passed` \| `qa_failed` \| `failed`(제작 실패) \| `budget_blocked` \| `halted`(인증·크레딧 문제로 전체 중단) \| `skipped` |
| `result` | 제작 후 채운다: `{"outputs": [...], "qa": "03_assetqa_{id}.json", "credits_est": 75}` |

**하나의 에셋 = 하나의 독립 작업:** 워크플로가 에셋을 병렬로 처리하므로 에셋끼리 서로 기다리면 안 된다. 앞 결과를 이어 쓰는 호출(예: 대사 TTS → 연기 변환 → 얼굴 애니메이션)은 한 에셋의 `steps` 안에 넣는다. 한 음성 파일에서 얼굴 애니메이션이 나오면 `category` 는 `voice_line` 으로 두고 `output` 에 두 결과를 함께 적는다.

**단가 미공개 단계는 선택 단계다:** `vc.acting`, `face.blendshape` 는 단가가 공개되지 않았다. 실제 모드에서 `run_meta.allow_unknown_price` 가 `false` 면 제작 스크립트가 이 두 단계만 건너뛰고 TTS 결과를 최종 음성으로 쓴다. `mt.translate` 는 대체할 방법이 없어 현지화 에셋이 `budget_blocked` 가 된다.

**대사 음성은 장면 단위로 묶는다:** 대사 한 줄마다 에셋을 만들면 에이전트 호출이 대사 수만큼 늘어난다. 같은 장면(`scene_id`)의 대사를 한 에셋으로 묶고 `lines` 에 `line_id` 를 나열한다. id 는 `vo_{scene_id}` 로 짓는다. 한 장면이 20줄을 넘으면 `vo_{scene_id}_a`, `_b` 로 나눈다. 견적을 정확히 하려면 TTS step 에 `calls`(줄 수)와 `per_call_chars`(줄별 글자 수 목록)를 적는다.

```json
{"id": "vo_ch1_intro", "category": "voice_line", "owner": "voice-director", "lines": ["ch1_intro_001", "ch1_intro_002"],
 "steps": [{"api": "tts.standard", "params": {"language": "korean"}, "calls": 2, "per_call_chars": [14, 22]},
           {"api": "face.blendshape", "input_from": "previous", "params": {"fps": 30}, "calls": 2}],
 "output": {"dir": "assets/audio/voice/korean", "basename": "{line_id}", "format": "wav", "count": 2,
            "extra": [{"dir": "assets/anim/face", "basename": "{line_id}", "format": "json"}]}}
```

**확장 필드:** 제작 담당 스킬이 쓰는 선택 필드다. 검사기는 모르는 필드를 무시한다.

| 필드 | 위치 | 뜻 |
| --- | --- | --- |
| `source_image_plan` | 에셋 | 3D·이미지 원본을 어떻게 구하는가: `provided`(사용자 제공, `inputs` 에 경로) \| `generate`(visual-artist 가 이미지 생성 스킬로 만든다) \| `manual`(사람이 그림, 첫 step 이 `manual.source_image`) |
| `blocked_by` | 에셋 | 먼저 끝나야 하는 에셋 id. 예: 원문 외 언어 음성은 `l10n_{lang}` 번역이 끝나야 만든다. 3단계 두 번째 회차에서 제작한다 |
| `when` | step | 조건부 호출. 예: `speaker_face_anim` 이면 `characters.csv` 의 `face_anim=y` 인 화자 줄에만 호출 |
| `text_source` | step | 줄마다 넣을 문장 출처. 예: `data/strings/en.json` |

**API 가 없는 에셋:** 배경음악은 공개 REST API 가 없어 `manual.unity_music` 으로, 3D 원본 이미지처럼 사람이 줘야 하는 파일은 `manual.source_image` 로 적는다. 이런 에셋은 워크플로에서 `manual_pending` 으로 표시만 하고 넘어간다.

## 6. 에셋 저장 위치와 이름

| 분류 | 위치(`games/{slug}/` 기준) | 형식 |
| --- | --- | --- |
| 효과음 | `assets/audio/sfx/{id}[_NN].wav` | WAV 44.1kHz |
| 환경음 | `assets/audio/ambience/{id}.wav` | 루프 처리한 WAV |
| 크리처 음성 | `assets/audio/creature/{id}[_NN].wav` | |
| 배경음악 | `assets/audio/music/{id}.wav` | 수동 제작 |
| 대사 음성 | `assets/audio/voice/{voice_lang}/{line_id}.wav` | 파일 이름은 `line_id` 와 같게 |
| 얼굴 애니메이션 | `assets/anim/face/{line_id}.json` | Voice-to-Face 응답 JSON. 원문이 아닌 음성 언어는 `assets/anim/face/{voice_lang}/{line_id}.json` |
| 3D 모델 | `assets/models/{id}.glb` | GLB |
| 이미지 | `assets/images/{id}[_NN].png` | PNG |
| 마케팅 | `marketing/{id}[_NN].png` | 스토어 규격(마케팅 스킬 참고) |

드라이런이면 같은 자리에 `{파일}.dryrun.json` 이 생긴다. 코드는 실제 파일이 없을 때 자리표시 에셋(무음, 회색 상자)을 쓰도록 만든다.

## 7. QA 산출물

### 7-1. 에셋 QA 결과 `_workspace/{slug}/03_assetqa_{id}.json`

```json
{
  "id": "sfx_sword_swing",
  "verdict": "pass",
  "mode": "live",
  "checks": [
    {"name": "file_count", "result": "pass", "detail": "5/5"},
    {"name": "duration_s", "result": "pass", "detail": "0.42~0.61"},
    {"name": "peak_dbfs", "result": "fail", "detail": "-0.2 > -1.0"}
  ],
  "issues": ["sfx_sword_swing_03.wav 클리핑 직전"],
  "retryable": true,
  "fix_hint": "variation strength 를 낮추거나 게인 -2dB 후처리"
}
```

`verdict`: `pass` \| `fail` \| `cannot_verify`(검증 도구가 없거나 입력이 없음). `cannot_verify` 는 통과로 세지 않는다.

`acceptance` 에서 쓰는 검사 이름: `duration_s`([최소, 최대]), `channels`(1\|2), `sample_rate`, `loop`(true 면 이음매 검사), `peak_dbfs_max`, `lufs_range`([최소, 최대]), `face_max`(3D 면 수 상한), `has_texture`, `min_size`([가로, 세로]), `aspect`("16:9" 등), `lang_coverage`(현지화 누락 0), `max_len_ok`(UI 글자 수 초과 0), `face_sync_s`(얼굴 애니메이션 길이와 음성 길이 차이의 허용치, 초. 기본 0.25).

### 7-2. 버그 리포트 `games/{slug}/qa/bugs/BUG-{NNN}.md`

```markdown
# BUG-012 전투: 적 체력이 0 아래로 내려가도 사망 처리가 안 됨

- 심각도: S1 (S1 진행 불가·크래시 | S2 핵심 기능 오류 | S3 부분 오류·우회 가능 | S4 외관·문구)
- 모듈: combat
- 발견: game-qa, 2026-09-28, 빌드 {커밋 또는 해시}
- 상태: open | fixed | verified | wontfix
- 담당: gameplay-engineer

## 재현 절차
1. ...
## 기대 결과 / 실제 결과
## 근거
스크린샷·로그·파일:줄 번호
## 관련 계약
data/balance/enemies.csv 의 hp 열 ↔ web/src/combat.js:88
```

### 7-3. QA 보고서

- 모듈별 보고서: `_workspace/{slug}/04_gameqa_module-{module}.md` — 검사 항목, 통과·실패·미검증 수, 새 버그 목록
- 최종 회귀 보고서: `games/{slug}/qa/reports/regression.md`
- 에셋 전수 감사: `games/{slug}/qa/reports/asset-audit.md`(사람용)와 `_workspace/{slug}/05_assetqa_audit.json`(검사 스크립트 원본 결과)
- 밸런스 구현 대조: `games/{slug}/qa/reports/balance-impl.md`

## 8. 동결과 승격

단계가 끝나면 리더가 다음 순서로 산출물을 동결하고 확정 폴더로 올린다.

1. 해당 단계 담당이 모두 완료를 보고했는지 확인한다.
2. 담당에게 동결을 알린다. 이후 고칠 내용은 `_v2` 새 파일로 쓰고 리더에게 알리게 한다.
3. `shasum _workspace/{slug}/{단계}_* > _workspace/{slug}/freeze_{단계}.sha`
4. 3절 표의 승격 위치로 복사한다.
5. 다음 단계 에이전트에게는 확정 폴더 경로만 넘긴다.

다음 단계를 시작하기 전에 `shasum -c _workspace/{slug}/freeze_{단계}.sha` 로 동결본이 바뀌지 않았는지 확인한다.

## 9. 출시 판정 기준

게임 디렉터가 5단계에서 아래 기준으로 판정한다. 하나라도 어기면 `No-Go` 이며, 어긴 항목과 처리 방안을 `RELEASE_REPORT.md` 에 적는다.

| 기준 | 통과 조건 |
| --- | --- |
| 버그 | S1·S2 가 `open` 인 버그 0건 |
| 에셋 | `P0` 에셋이 모두 `qa_passed`. 드라이런이면 `P0` 요청 명세가 모두 검증을 통과 |
| 데이터 정합성 | 밸런스 CSV 와 구현 값 불일치 0건, 코드가 참조하는 에셋 파일 누락 0건 |
| 현지화 | 대상 언어별 문자열 누락 0건, UI 글자 수 초과 0건 |
| 밸런스 | 밸런스 보고서의 판정이 `pass`, 또는 남은 위험을 디렉터가 받아들인다는 기록 |
| 크레딧 | 장부의 실제 사용 추정치가 승인 예산 이하 |
