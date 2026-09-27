---
name: varco-voice-production
description: "VARCO Voice 로 게임 대사 음성과 립싱크·표정 애니메이션을 만드는 방법. 캐릭터별 화자 캐스팅(1,293명 화자 목록, 감정별 변형), TTS Lite/Standard 선택, SSML·속도·음높이·seed 고정, 연기 톤을 살리는 Voice Conversion Acting, Voice-to-Face 블렌드셰이프(ARKit 52) 생성, 장면 단위 묶음 제작 스크립트를 다룬다. 매니페스트의 voice_line 에셋을 만들거나 '대사 녹음', '캐릭터 목소리 정해줘', '음성 다시 뽑아줘', '립싱크 애니메이션' 요청에 voice-director 가 사용한다. 몬스터·크리처 음색 변환은 varco-sound-production, 번역 문자열은 varco-localization 이 맡는다."
---

# VARCO 대사 음성 제작

대사 묶음 에셋(`vo_{scene}`) 하나를 받아 줄마다 음성을 합성하고, 필요하면 연기 톤 변환과 얼굴 애니메이션까지 만든다. 모든 호출은 `varco_client.py` 를 거치며, 반복 작업은 `scripts/voice_batch.py` 가 처리한다. 형식과 위치는 계약서 4-2(캐릭터), 4-3(대사), 5절(묶음 규칙), 6절(저장 위치)을 따른다.

## 작업 순서

1. `run_meta.json` 에서 `varco_mode`, `budget_credits`, `voice_langs` 를 읽는다.
2. 매니페스트에서 에셋을 찾아 `lines`, `steps`, `output` 을 읽는다.
3. **캐스팅을 확인한다.** `_workspace/{slug}/03_voice_casting.json` 이 없거나 자리표시 상태인데 실제 호출이면 `voice_cast.py` 를 실행한다.
4. **묶음 제작:** `voice_batch.py` 를 실행한다.
5. 출력 JSON 을 검토한다. 실패한 줄이 있으면 원인을 `notes` 에 옮긴다.
6. PRODUCE 스키마로 반환한다.

## 캐스팅

```bash
python3 .claude/skills/varco-voice-production/scripts/voice_cast.py --run-meta _workspace/{slug}/run_meta.json [--acting]
```

- 화자 목록(`voices.tts_standard` 등)을 한 번 받아 `_workspace/{slug}/voices_{model}.json` 에 저장하고 다시 쓴다. 목록 조회는 무료로 가정하지만 매번 부를 이유가 없다.
- `characters.csv` 의 `gender`, `age_band`, `voice_brief`, `personality` 를 화자 설명(예: "여성, 청년, 저음, 건조, 냉소")과 대조해 점수를 매긴다. 성별이 다른 화자는 고르지 않는다. 대사가 많은 캐릭터가 먼저 고르고, 크리처는 가이드 음성용이라 마지막에 고르며 다른 캐릭터와 겹쳐도 된다.
- 화자 이름의 괄호는 감정 변형이다(`실라린(분노)`, `실라린(중립)`). 캐스팅은 캐릭터마다 `by_emotion`(neutral·angry·happy·sad·surprise → uuid)과 `default` 를 기록하고, 제작 때 대사의 `emotion` 에 맞는 변형을 쓴다.
- 캐릭터마다 결정적인 `seed` 를 넣는다. 같은 문장을 다시 합성해도 같은 결과가 나와야 재작업 때 통과한 줄과 새 줄의 목소리가 어긋나지 않는다.
- **캐스팅 파일이 있으면 그대로 쓴다.** 워크플로에서 voice-director 여러 명이 동시에 일하므로 각자 고르면 같은 캐릭터가 장면마다 다른 목소리가 된다. 스크립트는 잠금을 걸고 없는 캐릭터만 채운다. 바꾸려면 리더 승인 뒤 `--force` 를 쓴다.
- 드라이런이면 목록을 받을 수 없으므로 uuid 자리에 `<speaker_uuid:{speaker_id}>` 를 넣는다. 나중에 실제 호출로 바꿀 때 같은 명령을 다시 실행하면 자리표시만 실제 화자로 채운다.
- 결과를 읽고 `reason` 에 "(다른 캐릭터와 화자 겹침 — 확인 필요)"가 있으면 `notes` 에 적는다.

## 모델과 파라미터 고르기

| 상황 | 선택 |
| --- | --- |
| 게임 대사, 컷신, 감정 표현 | `tts.standard` (10자당 1 크레딧, 감정·연기 표현) |
| 실시간 안내, 튜토리얼 팝업처럼 빠른 응답이 중요 | `tts.lite` (20자당 1 크레딧) |
| 감정 기복이 큰 대사(`voice=acting`) | `tts.standard` → `vc.acting`. TTS 결과를 연기 전용 화자로 옮겨 표현을 살린다 |
| 발음·쉼을 세밀하게 조정 | `text` 에 SSML. SSML 을 쓰면 다른 옵션(language, properties)은 무시된다 |
| 캐릭터 말투 | `properties.speed`, `properties.pitch` (0.8~1.2 권장). 캐스팅 파일의 캐릭터별 값에 넣는다 |
| 품질과 속도 | `n_fm_steps` 8~20. 높을수록 좋고 느리다. 최종본은 12~16 을 권한다 |

한도: `text` 는 UTF-8 1,200바이트(한글 약 400자). 언어는 `korean`, `english`, `japanese`, `taiwanese`.

## 묶음 제작 스크립트

```bash
python3 .claude/skills/varco-voice-production/scripts/voice_batch.py \
  --run-meta _workspace/{slug}/run_meta.json --id vo_ch1_intro [--lines ch1_intro_002] [--allow-unknown-price]
```

- 줄마다 TTS → (VC Acting) → (Voice-to-Face) 를 잇고 계약서 6절 위치에 저장한다. 음성은 `assets/audio/voice/{voice_lang}/{line_id}.wav`, 얼굴 애니메이션은 `assets/anim/face/{line_id}.json`.
- VC Acting 을 거치는 줄의 TTS 원본은 `_workspace/{slug}/03_voice_raw/` 에 남고, 최종본만 확정 폴더에 간다.
- `run_meta.varco_mode` 가 live 가 아니면 자동으로 드라이런이다. 드라이런에서는 앞 단계 입력 자리에 1초 무음 파일을 넣어 요청 명세를 만든다.
- 종료 코드 3·4·10·11 을 만나면 남은 줄을 부르지 않고 `budget_blocked` / `auth_failed` / `credit_exhausted` 로 멈춘다.
- 일부 줄만 실패하면 `status` 는 `generated`(드라이런이면 `dry-run`)이고, 실패한 줄은 `error` 에 적힌다. asset-qa 가 파일 수 부족으로 불합격시키면 재작업 때 `--lines` 로 그 줄만 다시 만든다. 통과한 줄은 다시 부르지 않는다.
- 작업 기록은 `_workspace/{slug}/03_voice_{id}.json` 에 줄별로 남는다.

**단가 미공개 API:** `face.blendshape` 와 `vc.acting` 은 단가가 공개되지 않았다. 실제 호출에서 예산을 걸면 `varco_client.py` 가 단가 미상 호출을 막는다. 리더가 크레딧 승인 때 이를 포함해 승인했으면 `run_meta.json` 에 `"allow_unknown_price": true` 가 있거나 워크플로 프롬프트에 그렇게 적혀 있다. 그때만 `--allow-unknown-price` 를 붙인다. 승인이 없으면 이 단계가 `budget_blocked` 로 멈추고, 리더가 승인 여부를 사용자에게 묻는다.

## 대사에서 확인할 점

- **자리표시자가 든 대사는 합성하지 않는다.** 음성 파일에는 실행 중에 이름 같은 값을 넣을 수 없다. 음성 대사에 `{player_name}` 같은 자리표시자를 쓰지 않는 것이 규칙이고(`game-narrative` 의 `check_story_data.py` 가 오류로 잡는다), `voice_batch.py` 는 그런 줄을 실패로 기록한다. `notes` 에 "narrative 에 문장 수정 요청"을 적는다.
- `emotion` 이 `neutral`·`angry`·`happy`·`sad`·`surprise` 가 아니면 얼굴 애니메이션은 `neutral` 로 만든다.
- 원문 외 음성 언어 에셋(`blocked_by: l10n_{lang}`)은 `data/strings/{lang}.json` 을 읽는다. 파일이 없으면 스크립트가 `failed` 로 멈춘다. 현지화가 끝난 뒤 리더가 다시 부른다.

## Voice-to-Face

- 입력은 최종 음성(연기 변환까지 거친 파일)이다. 립싱크는 실제로 재생될 음성과 맞아야 한다.
- 옵션: `fps`(기본 30), `lip_style`(balanced·clear·minimal·moderate), `face_style`(natural·energetic·stoic·timid), `emotion`, `neck`·`eye`(on/off). 캐릭터 성격에 맞춰 매니페스트 step 의 `params` 를 따른다.
- 응답은 `blendshape.faceNames`(ARKit 52 이름)와 `weightMat`(프레임 × 포즈 가중치)을 담은 JSON 이다. 그대로 저장하고 가공하지 않는다. 엔진 적용은 gameplay-engineer 가 한다.

## 오류 대응

| 상황 | 할 일 |
| --- | --- |
| 캐스팅 없음·자리표시 상태에서 실제 호출 | `voice_cast.py` 실행 후 다시 |
| 종료 코드 12(검증 실패) | 스크립트 출력의 `problems` 를 보고 매니페스트 params 문제면 `notes` 에 적어 `failed`, 대사 길이 문제면 narrative 수정 요청을 `notes` 에 |
| 모든 줄 실패 | `failed` 로 반환하고 줄별 원인을 `error` 에 |
| 크리처 에셋(`crv_`)을 받음 | 담당이 아니다. `failed` 로 반환하고 "sound-designer 담당"을 적는다 |
