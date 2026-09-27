---
name: varco-sound-production
description: "VARCO Sound API 로 게임 효과음(SFX), 환경음 루프, 몬스터·크리처 음성을 만들고 ffmpeg 로 게임용으로 다듬는 방법. Text to Sound 프롬프트 작성, Variation·Mono to Stereo·Looping·Conversion·Enhance 연결 순서, 후보 고르기, 10초 출력의 무음 자르기·페이드·레벨 맞추기, 드라이런 처리를 다룬다. 매니페스트의 sfx·ambience·creature_voice 에셋을 만들거나 '효과음 만들어줘', '환경음 루프', '몬스터 목소리', '사운드 다시 뽑아줘' 요청에 sound-designer 가 사용한다. 대사 음성(TTS)은 varco-voice-production, 배경음악은 API 가 없어 수동 제작이다."
---

# VARCO 사운드 제작

매니페스트 에셋 하나를 받아 VARCO Sound 로 만들고, 게임에 바로 넣을 수 있게 다듬는다. 호출은 `.claude/skills/varco-api/scripts/varco_client.py` 로만 하고, 매니페스트 `steps` 에 적힌 순서와 횟수를 지킨다. 저장 위치는 계약서 6절이다.

## 작업 순서

1. `_workspace/{slug}/run_meta.json` 에서 `varco_mode`, `budget_credits` 를 읽는다.
2. `games/{slug}/manifest.json` 에서 에셋을 찾아 `brief`, `steps`, `output`, `acceptance` 를 읽는다. 환경음이면 `games/{slug}/docs/levels.md` 의 사운드 구역 설명도 읽는다.
3. step 마다 `validate` → `call` 을 한다. 공통 인자:
   - 실제 호출: `--ledger _workspace/{slug}/varco_ledger.jsonl --asset-id {id} --budget {budget_credits}`
   - 드라이런: `--ledger ... --asset-id {id} --dry-run`
4. 후보가 여럿이면 고르고, 후처리한다.
5. 작업 기록 `_workspace/{slug}/03_sound_{id}.json` 에 호출별 출력 JSON, 고른 후보와 이유, 후처리 명령을 남긴다.
6. 워크플로 PRODUCE 스키마로 반환한다(에이전트 정의 「구조화 출력」).

중간 파일(후보, 루프 전 원본)은 `_workspace/{slug}/03_sound_work/{id}/` 에 두고, 최종 파일만 `games/{slug}/assets/audio/...` 에 둔다. 확정 폴더에 후보가 섞이면 개발자가 어느 파일을 써야 할지 모른다.

## Text to Sound 프롬프트

모델은 한국어·영어를 모두 이해한다. 200자를 넘기지 않는다. 출력은 항상 10초 WAV(44.1kHz, 16bit)다.

| 원칙 | 예 |
| --- | --- |
| 소리를 내는 물체와 동작을 먼저 쓴다 | `heavy iron sword slash, fast whoosh` |
| 재질·크기·거리를 한두 개만 더한다 | `small wooden crate breaking, close` |
| 공간을 적으면 잔향이 따라온다 | `footsteps on wet stone in a large cave` |
| 효과음은 한 번만 나게 한다 | `single`, `one shot` 을 넣고 여러 번 반복되는 묘사를 피한다 |
| 환경음은 지속되는 요소를 나열한다 | `neon city night ambience, distant traffic, light rain, humming signs` |
| 미사여구를 빼고 핵심 소리만 남긴다 | 문장이 길수록 모델이 모든 요소를 넣으려 해 소리가 탁해진다 |
| 음악을 요구하지 않는다 | 멜로디가 있는 음악은 이 모델의 용도가 아니다 |

`version` 은 매니페스트 값을 따른다(없으면 `v2`). `num_sample` 은 1~3 이다.

## 연결 레시피

앞 step 결과를 다음 step 입력으로 쓸 때는 `--file source={앞 결과 경로}` 로 넘긴다.

**반복 효과음(발소리·타격):** `text2sound`(num_sample 3) → 후보 선택 → 후처리 → `variation`(`--file source=선택본`, num_sample 3~5, strength 0.5~1.0) → 변형마다 후처리. 최종 파일은 선택본을 `{basename}_01.wav`, 변형을 `_02` 부터 이어 번호를 붙여 확정 폴더에 둔다. 매니페스트 `output.count` 는 선택본 1개 + 변형 수이므로 개수가 맞는지 끝나기 전에 센다. strength 가 1.5 를 넘으면 원래 소리와 달라지기 쉽다. 어택은 두고 꼬리만 바꾸려면 `include={"begin": 0.1, "end": 1.0}` 을 쓴다.

**환경음 루프:** `text2sound` → 후보 선택 → `mono2stereo`(이미 스테레오면 매니페스트에 있어도 효과가 작다. 작업 기록에 적는다) → `looping`. 반드시 남길 구간(새 울음 같은 특징음)은 `preserve={"begin": 2.0, "end": 4.5}` 로 지정한다. 루프 결과는 자르지 않는다. 자르면 이음매가 생긴다. 레벨은 `normalize --lufs -23` 정도로 낮게 맞춘다.

**크리처 대사(`crv_`):** 매니페스트 `steps` 가 `tts.standard`(가이드) + `sound.text2sound`(참조음) → `sound.conversion` 이다.
1. 가이드 TTS 는 voice-director 의 캐스팅 파일 `_workspace/{slug}/03_voice_casting.json` 의 화자를 쓴다. 파일이 없으면 `python3 .claude/skills/varco-voice-production/scripts/voice_cast.py --run-meta _workspace/{slug}/run_meta.json` 을 먼저 실행한다(잠금이 있어 다른 에이전트와 겹쳐도 안전하다). 대사 문장은 `data/dialogue.csv` 의 `text_ko` 다.
2. 참조음은 에셋당 한 번만 만든다(`num_sample` 1). 프롬프트는 `brief` 의 음색 설명을 쓴다. 예: `deep rumbling stone golem growl, gravelly`.
3. 줄마다 `sound.conversion --file source={가이드} --file reference={참조음} --param ratio=1.0`. 가이드가 폰 녹음처럼 잡음이 있으면 `--param enhance=true`.
4. 결과 파일 이름은 `{line_id}.wav`, 위치는 `assets/audio/creature/`.

**잡음 제거:** `enhance` 한 번. 여러 번 반복해도 좋아지지 않고 음색이 얇아진다.

## 후보 고르기

`scripts/audio_post.py rank` 가 클리핑이 없고 목표 길이에 가까운 순서로 정렬한다. 점수는 참고일 뿐이고 최종 선택은 다음 기준으로 한다.

1. `brief` 가 말한 소리가 맞는가(칼 소리를 원했는데 바람 소리만 나면 탈락)
2. 앞부분에 불필요한 잡음이나 늦은 시작이 없는가(`info` 의 `active_s` 와 원래 길이 비교)
3. 클리핑이 없는가(`peak_dbfs` 가 -0.1 보다 크면 탈락)

모든 후보가 기준에 못 미쳐도 승인받은 호출 수를 넘겨 더 부르지 않는다. 가장 나은 후보를 쓰고 작업 기록에 부족한 점을 적는다. asset-qa 가 불합격시키면 재작업 때 프롬프트를 바꿔 다시 부른다.

## 후처리

`scripts/audio_post.py` (ffmpeg 필요):

| 명령 | 쓰는 곳 |
| --- | --- |
| `sfx in.wav out.wav --peak -1.0` | 효과음 기본 처리: 앞뒤 무음 자르기 → 짧은 페이드 → 피크 -1dBFS |
| `trim`, `fade`, `normalize --peak` / `--lufs` | 따로 조정할 때 |
| `mono` | 위치 효과(3D 사운드)용으로 모노가 필요할 때 |
| `info a.wav b.wav` | 길이·채널·피크·유효 길이 측정 |
| `rank a.wav b.wav --target-s 0.6` | 후보 정렬 |
| `placeholder out.wav --seconds 1` | 드라이런에서 다음 step 입력 자리를 채울 무음 파일 |

후처리한 파일이 최종본이다. 원본 VARCO 출력은 작업 폴더에 남긴다.

## 드라이런

드라이런이면 네트워크 호출도 파일 생성도 없다. `varco_client.py` 가 `{out}.dryrun.json` 에 요청 명세만 쓴다.

- `varco_client.py` 는 `--file` 로 넘긴 파일이 실제로 있어야 명세를 만든다. 앞 step 결과가 필요한 자리에는 `audio_post.py placeholder` 로 만든 무음 파일을 `_workspace/{slug}/03_sound_work/{id}/_placeholder.wav` 에 두고 넘긴다. 작업 기록에 "앞 step 예정 출력: {경로}"를 함께 적는다.
- 후처리는 하지 않는다. 반환 `outputs` 에는 `.dryrun.json` 경로를 적고 `status` 는 `dry-run` 이다.

## 오류 대응

| 종료 코드 | 할 일 |
| --- | --- |
| 3 | `budget_blocked` 로 즉시 반환 |
| 10 / 11 | `auth_failed` / `credit_exhausted` 로 즉시 반환. 재시도하지 않는다 |
| 12 | 서버 메시지를 읽고 파라미터를 고쳐 한 번 더. 그래도 안 되면 `failed` |
| 13 | 한 번 더 시도하고 안 되면 `failed` |
| 기타 | 출력 JSON 을 작업 기록에 남기고 `failed` |
