---
name: asset-manifest
description: "확정된 게임 기획 문서(docs/, data/)에서 필요한 에셋을 뽑아 VARCO API 제작 계획인 에셋 매니페스트(manifest.json)와 크레딧 견적을 만든다. 에셋마다 분류·담당·우선순위·API 호출 순서(steps)·검수 기준(acceptance)을 정하고, 대사 음성은 장면 단위로 묶는다. '에셋 목록 뽑아줘', '매니페스트 만들어줘', '크레딧 견적', '어떤 VARCO API 로 만들지 정해줘', '에셋 추가/수정' 요청이나 varco-game-studio 2단계에서 asset-producer 가 사용한다. 실제 에셋 생성은 각 제작 스킬(varco-sound-production 등)이, 단일 API 호출법은 varco-api 가 맡는다."
---

# 에셋 매니페스트 작성

기획 문서를 읽고 "무엇을, 어떤 VARCO API 로, 몇 번 불러, 어떤 기준으로 합격시킬지"를 한 파일에 정한다. 이 파일이 크레딧 승인의 근거가 되고, 3단계 워크플로는 이 파일에 적힌 호출만 실행한다. 여기서 빠진 에셋은 만들어지지 않고, 여기서 부풀린 에셋은 그대로 크레딧이 된다.

형식은 `.claude/skills/varco-game-studio/references/contracts.md` 5절(매니페스트)과 6절(저장 위치)을 따른다. API id 와 파라미터 제약은 `.claude/skills/varco-api/SKILL.md` 표와 `varco_client.py catalog` 로 확인한다.

## 입력과 출력

| 구분 | 경로 |
| --- | --- |
| 입력 | `_workspace/{slug}/run_meta.json`, `games/{slug}/docs/*.md`, `games/{slug}/data/*.csv` |
| 출력 | `_workspace/{slug}/02_producer_manifest.json`, `_workspace/{slug}/02_producer_estimate.md` |

## 작성 절차

### 1. 에셋 필요 지점을 문서별로 훑는다

| 읽을 곳 | 찾을 것 | 보통 나오는 분류 |
| --- | --- | --- |
| `docs/systems.md` | 공격·피격·획득·레벨업·UI 확인음처럼 플레이어 행동에 붙는 소리, 상태 이상 표현 | `sfx` |
| `docs/levels.md` | 레벨별 사운드 구역(환경음), 필요한 프랍 목록, 배경 분위기 | `ambience`, `model_3d`, `image` |
| `data/dialogue.csv` + `data/characters.csv` | `voice` 가 `none` 이 아닌 대사, 얼굴 애니메이션이 필요한 화자, 크리처 화자 | `voice_line`, `creature_voice` |
| `docs/ux.md` | 버튼·전환·알림 소리, 타이틀·결과 화면 음악 | `sfx`, `music` |
| `docs/narrative.md` | 캐릭터 초상·일러스트 가공, 보스 등장 연출 | `image`, `creature_voice` |
| `run_meta.json` 의 `target_langs` | 번역할 언어 | `localization` |
| 컨셉의 플랫폼 | 출시용 스토어 이미지 | `marketing` (`phase: release`) |

문서에 근거가 없는 에셋은 넣지 않는다. 모든 에셋의 `source_ref` 에 근거 위치를 적는다. 근거를 적을 수 없다면 그 에셋은 기획에 없는 것이다.

### 2. 대사 음성은 스크립트로 초안을 만든다

```bash
python3 .claude/skills/asset-manifest/scripts/draft_voice_assets.py --game-dir games/{slug} \
  --voice-lang korean --out _workspace/{slug}/02_producer_voice_drafts.json
```

- 같은 장면·같은 제작 방식의 대사를 한 에셋으로 묶고 20줄이 넘으면 `_a`, `_b` 로 나눈다(계약서 5절).
- `voice=tts` → `vo_{scene}`, `voice=acting` → `vo_{scene}_acting`(TTS → VC Acting), `voice=creature` → `crv_{scene}`(sound-designer 담당).
- `face_anim=y` 인 화자의 줄에만 `face.blendshape` 를 붙인다(`"when": "speaker_face_anim"`).
- 표준 오류에 나온 `problems`(자리표시자가 든 음성 대사, 1,200바이트 초과, 허용되지 않는 emotion)는 견적서의 "기획에 되물을 점"에 옮긴다. 음성 대사에는 자리표시자를 쓰지 않는 것이 규칙이라, 고치지 않으면 voice_batch.py 가 그 줄을 합성하지 않는다.
- 대사·캐릭터·문자열 CSV 형식 자체가 의심스러우면 `.claude/skills/game-narrative/scripts/check_story_data.py` 로 먼저 검사한다(새 검사 스크립트를 만들지 않는다).
- 원문 외 음성 언어(`voice_langs` 에 `english` 등)가 있으면 그 언어로 한 번 더 실행한다. 이 에셋은 번역 문자열을 읽으므로 `blocked_by: l10n_{lang}` 이 붙는다. 같은 워크플로 회차에서 번역과 동시에 만들 수 없으므로 견적서에 "현지화 뒤 3단계 두 번째 회차에서 제작"이라고 적는다.

### 3. 나머지 에셋의 API 순서를 정한다

| 필요한 것 | steps | 이유 |
| --- | --- | --- |
| 한 번 나는 효과음(문, 획득) | `sound.text2sound`(num_sample 2~3) | 후보 중 고르면 충분하다 |
| 자주 반복되는 효과음(발소리, 타격, 총성) | `sound.text2sound` → `sound.variation`(num_sample 3~5) | 같은 소리가 반복되면 귀가 금방 알아챈다. 변형을 랜덤 재생한다 |
| 레벨 환경음 | `sound.text2sound` → `sound.mono2stereo` → `sound.looping` | 공간감을 넓힌 뒤 이음매 없는 루프로 만든다 |
| 몬스터 울음·포효(대사 없음) | `sound.text2sound` (+ `sound.variation`) | 목소리 연기가 필요 없으면 변환보다 싸다 |
| 크리처 대사 | 초안 스크립트 결과(`crv_`). 사람이 녹음한 가이드가 있으면 `inputs` 에 넣고 TTS step 을 뺀다 | 말의 호흡은 가이드가, 음색은 참조음이 정한다 |
| 녹음 품질이 나쁜 음성 | `sound.enhance` | |
| 배경음악 | `manual.unity_music` | REST API 가 없다. Unity 플러그인 Music 탭에서 사람이 만든다 |
| 3D 프랍·캐릭터 | `3d.image_to_3d` (원본 이미지는 `inputs`) | 원본 확보 방법은 아래 「원본 이미지 계획」 |
| 이미지 배경 교체·시점 변경·해상도 | `image.background` / `image.perspective` / `image.upscale` | |
| 현지화 | 언어마다 `mt.translate` 에셋 하나 | 문자열 전체를 한 에셋으로 묶는다 |
| 스토어 이미지 | `image.background` → `image.upscale` 등, `phase: release` | 5단계에서 게임 화면이 나온 뒤 만든다 |

호출 수를 줄이는 쪽을 먼저 고른다. 효과음 다섯 개가 필요하면 Text to Sound 다섯 번보다 한 번 + Variation 한 번이 싸다(25+50 대 125).

**원본 이미지 계획:** VARCO 에는 텍스트로 이미지를 만드는 API 가 없다. 이미지가 필요한 에셋에는 `source_image_plan` 을 적는다.

| 값 | 뜻 | 매니페스트 작성 |
| --- | --- | --- |
| `provided` | 사용자가 이미 준 파일이 있다 | 그 경로를 `inputs` 에 적는다 |
| `generate` | visual-artist 가 이미지 생성 스킬(codex-image 등)로 원본을 만든다 | 만들 경로를 `inputs` 에 적고 원하는 그림을 `brief` 에 쓴다 |
| `manual` | 사람이 그려서 줘야 한다 | 첫 step 을 `manual.source_image` 로 둔다. 워크플로는 이 에셋을 `manual_pending` 으로 넘긴다 |

`manual` 은 원본이 올 때까지 에셋이 멈춘다는 뜻이다. 프로토타입에서는 `generate` 를 기본으로 하고, 사용자가 자기 그림을 쓰겠다고 했을 때만 `provided`·`manual` 을 쓴다.

### 4. 줄마다·문자열마다 채우는 파라미터는 템플릿으로 적는다

매니페스트 검사기는 필수 파라미터가 비어 있으면 오류를 낸다. 제작 스크립트가 줄마다 채우는 값은 아래 템플릿 문자열로 자리를 채운다.

| API | 필드 | 템플릿 |
| --- | --- | --- |
| `mt.translate` | `TID` | `"{slug}-{lang}-{string_id}"` |
| `mt.translate` | `source_text` | `"{text}"` |
| `tts.*`, `vc.*` | `voice`, `speaker_uuid` | 비워 둔다(검사기가 경고만 한다. voice-director 가 캐스팅으로 채운다) |
| 묶음 대사의 `text`, `face.blendshape` 의 `id` | | 비워 둔다(`lines` 가 있으면 검사기가 건너뛴다) |

현지화 에셋 예:

```json
{"id": "l10n_en", "category": "localization", "owner": "localization-specialist", "phase": "production",
 "priority": "P0", "source_ref": "data/dialogue.csv, data/ui_strings.csv", "brief": "대사·UI 문자열 영어 번역",
 "inputs": ["data/dialogue.csv", "data/ui_strings.csv", "data/glossary.csv"],
 "steps": [{"api": "mt.translate", "calls": 132,
            "params": {"TID": "{slug}-{lang}-{string_id}", "source_text": "{text}", "source_lang": "ko",
                       "target_lang": "en", "provider": "content"}}],
 "output": {"dir": "data/strings", "basename": "en", "format": "json", "count": 1},
 "acceptance": {"lang_coverage": true, "max_len_ok": true}, "status": "planned"}
```

`calls` 는 대사 줄 수 + UI 문자열 수다.

### 5. 우선순위를 정한다

| 우선순위 | 기준 | 예 |
| --- | --- | --- |
| `P0` | 없으면 코어 루프가 성립하지 않거나 첫 5분에 반드시 들린다·보인다 | 기본 공격음, 첫 레벨 환경음, 튜토리얼 대사, 첫 번째 대상 언어 |
| `P1` | 없어도 플레이는 되지만 완성도가 눈에 띄게 떨어진다 | 보조 효과음 변형, 두 번째 레벨 프랍, 조연 대사 |
| `P2` | 여유가 있을 때 | 수집품 소리, 장식 프랍 |

크레딧 승인에서 사용자가 "P0 만"을 고를 수 있어야 하므로, P0 만 모아도 게임이 돌아가게 나눈다.

### 6. 검수 기준(acceptance)을 적는다

asset-qa 가 측정할 수 있는 값만 적는다(계약서 7-1절의 검사 이름). 모르면 `null` 로 둔다. 추측으로 좁게 잡으면 멀쩡한 에셋이 불합격한다.

| 분류 | 권장 기준 |
| --- | --- |
| `sfx` | `duration_s` [0.05, 3.0], `peak_dbfs_max` -1.0 |
| `ambience` | `loop` true, `duration_s` [5, 60], `lufs_range` [-30, -16] |
| `creature_voice`, `voice_line` | `duration_s` [0.2, 20], `peak_dbfs_max` -1.0. 파일 수 = `lines` 수 |
| `model_3d` | `face_max`(steps 의 `target_face_num` 이상), `has_texture`(`generate_texture` 와 같게) |
| `image` | `min_size` [가로, 세로], 필요하면 `aspect` |
| `localization` | `lang_coverage` true, `max_len_ok` true |
| `marketing` | 스토어 규격 크기를 `min_size` 와 `aspect` 로 |

### 7. 검사하고 견적을 낸다

```bash
python3 .claude/skills/asset-manifest/scripts/validate_manifest.py _workspace/{slug}/02_producer_manifest.json --game-dir games/{slug}
python3 .claude/skills/varco-api/scripts/estimate_cost.py _workspace/{slug}/02_producer_manifest.json --write \
  --md _workspace/{slug}/02_producer_estimate.md
```

`errors` 가 0 이 될 때까지 고친다. `warnings` 는 견적서에 옮기고 이유를 적는다. 견적서(`02_producer_estimate.md`)에는 스크립트 표 아래에 다음을 덧붙인다.

- 합계에서 빠진 단가 미공개 호출(번역, Voice-to-Face, VC Acting 은 추정 단가)과 그 호출 수
- 수동 제작 에셋 목록(`manual.*`)과 사람이 할 일
- 두 번째 회차가 필요한 에셋(`blocked_by`)
- 기획에 되물을 점(자리표시자 대사, 근거가 모호한 에셋)
- P0 만 승인할 때의 합계

## 흔한 실수

- **한 줄마다 대사 에셋을 만든다** → 워크플로 에이전트 호출이 대사 수만큼 늘어난다. 장면 단위로 묶는다.
- **Text to Sound 출력이 10초라는 점을 잊는다** → 짧은 효과음도 10초로 온다. 자르는 일은 sound-designer 후처리가 하므로 acceptance 의 `duration_s` 는 후처리 뒤 길이로 적는다.
- **첫 step 에 `manual.*` 을 두고 나머지를 이어 붙인다** → 워크플로가 에셋 전체를 `manual_pending` 으로 넘긴다. 원본이 곧 준비되면 `inputs` 로 처리한다.
- **3D 원본 이미지를 JPG 로 적는다** → Image to 3D 는 PNG 만 받는다.
- **마케팅 에셋을 `production` 으로 둔다** → 게임 화면이 없어 만들 수 없다. `release` 로 둔다.

## 반환

단발 서브에이전트로 불리므로 리더에게 짧게 보고한다: 에셋 수(분류별), 추정 합계와 P0 합계, 단가 미공개 호출 수, 수동 제작 목록, 검사 경고 수, 기획에 되물을 점.
