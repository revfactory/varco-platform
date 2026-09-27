---
name: varco-localization
description: "VARCO Translate API 로 게임 대사와 UI 문자열을 번역해 언어별 문자열 파일(data/strings/{lang}.json)을 만드는 방법. 문자열 수집(dialogue.csv, ui_strings.csv), 용어집 적용(지정 번역어 강제, 번역 금지어 보호), 자리표시자 보호, provider(content·chat) 선택, 글자 수 초과 처리, 캐시로 재작업 비용 줄이기를 다룬다. 매니페스트의 localization 에셋을 만들거나 '번역해줘', '영어·일본어 버전', '언어 추가', '현지화 다시' 요청에 localization-specialist 가 사용한다. 마케팅 문구 번역에도 같은 스크립트를 쓴다. 번역된 대사로 음성을 만드는 일은 varco-voice-production 이 맡는다."
---

# VARCO 게임 현지화

현지화 에셋(`l10n_{lang}`) 하나는 한 언어의 문자열 전체다. 원문(대사 + UI)을 모아 VARCO Translate 로 번역하고, 게임 코드가 읽을 `data/strings/{lang}.json` 을 만든다. 형식은 계약서 4-3(대사), 4-4(UI), 4-5(용어집), 4-6(결과)을 따른다.

## 작업 순서

1. `run_meta.json`(모드, 예산, `source_lang`, `target_langs`)과 매니페스트 에셋을 읽는다.
2. 원문 데이터를 확인한다. 형식이 의심스러우면 `python3 .claude/skills/game-narrative/scripts/check_story_data.py --game-dir games/{slug}` 로 검사한다.
3. `translate_table.py` 를 실행한다.
4. 보고서(`_workspace/{slug}/03_l10n_{lang}_report.json`)를 읽고 문제를 처리한다.
5. 작업 기록 `_workspace/{slug}/03_l10n_{id}.json` 에 스크립트 출력과 처리 내용을 남기고 PRODUCE 스키마로 반환한다.

## 번역 스크립트

```bash
python3 .claude/skills/varco-localization/scripts/translate_table.py \
  --run-meta _workspace/{slug}/run_meta.json --id l10n_en [--only ui.hud.lap,ch1_intro_002] [--allow-unknown-price]
```

- 원문 파일 `data/strings/{source_lang}.json`(보통 `ko.json`)도 함께 만든다. 코드는 원문도 이 형식으로 읽는다.
- 문자열마다 `varco_client.py call mt.translate` 를 부른다. `TID` 는 `{slug}-{lang}-{string_id}` 로 정해져 있어 같은 문자열의 호출을 장부에서 추적할 수 있다.
- 실제 호출 결과는 `_workspace/{slug}/03_l10n_raw/{lang}/` 에 캐시된다. 다시 실행하면 캐시를 쓰고 호출하지 않는다. 재작업 때는 `--only` 로 문제 문자열만 다시 번역하고, 캐시를 무시해야 하면 `--refresh` 를 붙인다.
- `run_meta.varco_mode` 가 live 가 아니면 드라이런이다. 번역문 자리에 `[en] 원문` 을 넣어 파일 구조와 키를 먼저 완성한다. 개발 단계가 언어 전환을 이 파일로 시험할 수 있다.
- 종료 코드 3·4·10·11 을 만나면 멈추고 `budget_blocked`·`auth_failed`·`credit_exhausted` 를 반환한다. 이때까지 번역한 문자열로 파일을 쓰고 `_meta.partial: true` 를 붙인다.

**단가 미공개:** 번역 API 단가는 공개되지 않았다. 예산을 건 실제 호출은 `--allow-unknown-price` 가 있어야 된다. 리더가 크레딧 승인 때 번역 포함을 승인했으면(`run_meta.json` 의 `"allow_unknown_price": true` 또는 워크플로 프롬프트의 명시) 붙인다. 승인이 없으면 첫 호출에서 `budget_blocked` 로 멈추고, 리더가 사용자에게 묻는다.

## 번역 품질을 지키는 장치

| 장치 | 동작 | 이유 |
| --- | --- | --- |
| 자리표시자 보호 | `{player_name}` → `⟦P0⟧` → 번역 → 되돌림 | 번역기가 중괄호 안을 번역하거나 지우면 코드가 값을 넣지 못한다 |
| 번역 금지어 | 용어집 `do_not_translate=y` 인 말은 원문 그대로 보호 | 고유명사·상표가 언어마다 달라지는 것을 막는다 |
| 지정 번역어 | 용어집 `term_{lang}` 열 값으로 강제 | 게임 제목·캐릭터 이름·스킬 이름이 문장마다 다르게 번역되는 것을 막는다 |
| 용어집 열 확인 | 대상 언어의 `term_{lang}` 열이 없으면 경고 | 번역 금지어 보호는 되지만 지정 번역어는 적용되지 않는다. 경고를 `notes` 에 옮기고 narrative 에 열 추가를 요청한다 |
| 글자 수 검사 | UI 문자열 `max_len` 초과를 보고서에 적는다 | 버튼·HUD 밖으로 글자가 넘친다 |

**provider:** 대사·UI·아이템 설명처럼 게임 콘텐츠는 `content`, 플레이어 채팅처럼 구어체 짧은 문장은 `chat`. 매니페스트 step 의 `params.provider` 를 따른다.

**언어 코드:** 번역 API 는 `ko`, `en`, `ja`, `tw`, `cn`, `de`, `ru`, `es`, `pt`, `fr` 을 쓴다. TTS 언어 이름(`english` 등)과 형식이 다르다.

## 보고서 문제 처리

| 항목 | 처리 |
| --- | --- |
| `placeholder_lost` | 번역문에서 자리표시자나 용어가 사라졌다. `--only {id} --refresh` 로 한 번 다시 번역한다. 그래도 사라지면 `notes` 에 적는다(QA 가 불합격시키고 사람이 고친다) |
| `over_length` | 한 번은 `--only` 로 다시 번역해 본다. 여전히 길면 `notes` 에 "UI 에 줄바꿈·축약 필요"로 적고 ux-designer 몫으로 남긴다. 번역문을 임의로 잘라 뜻을 망가뜨리지 않는다 |
| `failed` | 스크립트가 남긴 오류를 보고 `--only` 로 재시도. 반복되면 `notes` |
| `glossary_warning` | `notes` 에 옮긴다 |

사람이 번역문을 직접 고치는 일은 이 스킬의 범위가 아니다. 결과 파일의 `_meta.reviewed` 는 `false` 로 둔다.

## 마케팅 문구 번역

marketing-artist 가 스토어 설명을 번역할 때도 같은 스크립트를 쓴다.

```bash
python3 .claude/skills/varco-localization/scripts/translate_table.py --run-meta _workspace/{slug}/run_meta.json \
  --lang en --source-csv games/{slug}/marketing/copy.csv --out games/{slug}/marketing/copy_en.json
```

CSV 열: `string_id,text_ko[,max_len,context]`. 보고서는 결과 파일 옆 `.report.json` 에 생긴다.
