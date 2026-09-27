---
name: varco-api
description: "VARCO API 플랫폼(openapi.ai.nc.com)을 호출하는 공용 방법과 명세. 사운드(Text to Sound, Variation, Looping, Mono to Stereo, Conversion, Enhance), 음성(TTS Lite/Standard, Voice Conversion·Custom·Acting), Voice-to-Face 블렌드셰이프, Image to 3D, Art Fashion 이미지 편집(배경 합성, 시점 변경, 텍스처, 그래픽, 지우기, 인페인트, 업스케일, 가상 착장, 헤드스왑), 번역(Translate)을 다룬다. OPENAPI_KEY 인증, base64·multipart 요청, 3D 비동기 결과 조회, 크레딧 견적, 드라이런, 예산 차단, 호출 장부를 공용 스크립트 varco_client.py 로 처리한다. VARCO API 를 부르거나, 파라미터를 확인하거나, 크레딧을 계산하거나, 'VARCO', '바르코', 'openapi.ai.nc.com', 'OPENAPI_KEY' 가 나오면 사용한다. 게임 전체 제작 흐름은 varco-game-studio 가 맡는다."
---

# VARCO API 공용 사용법

VARCO API 를 부르는 에이전트는 모두 이 스킬을 따른다. 요청 코드를 새로 짜지 말고 `scripts/varco_client.py` 를 쓴다. 에이전트마다 호출 코드를 따로 만들면 키 보호, 예산 확인, 결과 저장 위치, 장부 기록이 제각각이 되어 사후에 무엇을 얼마나 썼는지 알 수 없게 된다.

## 먼저 알아 둘 사실

- **기본 주소:** `https://openapi.ai.nc.com`. 모든 요청 헤더에 `OPENAPI_KEY` 를 넣는다. 없거나 틀리면 401 이다.
- **키 보관:** 환경변수 `OPENAPI_KEY` 또는 프로젝트 루트 `.env` 의 `OPENAPI_KEY=...`. 키 값을 출력하거나, 파일·문서·커밋·프런트엔드 코드에 옮겨 적지 않는다. 유출되면 남이 크레딧을 쓴다.
- **과금:** 호출마다 워크스페이스 크레딧이 빠진다. 크레딧이 모자라면 호출이 실패한다.
- **단가는 추정치다.** 공식 Pricing 페이지는 "공개 예정"이다. 이 스킬의 숫자는 각 문서에 주석으로 숨겨진 가격표에서 가져왔다. 번역, Voice-to-Face, 음성 변환 Acting 은 단가가 공개되지 않았다.
- **없는 기능:** 텍스트로 이미지를 만드는 API, 음악(멜로디)을 만드는 REST API, 글을 생성하는 API 는 없다. 배경음악은 VARCO Sound Unity 플러그인의 Music 탭에서만 만들 수 있다(`references/unity-plugin.md`).
- **가이드와 레퍼런스가 다를 때:** 레퍼런스를 따른다. 예: Text to Sound 가이드는 `num_samples`, 레퍼런스는 `num_sample` 이다. 레퍼런스의 `num_sample` 을 쓴다.

## 어떤 API 를 고를까

| 하려는 일 | API id | 입력 → 출력 | 추정 단가 |
| --- | --- | --- | --- |
| 효과음·환경음을 글로 만들기 | `sound.text2sound` | 프롬프트(200자 이내) → 10초 WAV 1~3개 | 25/호출 |
| 같은 소리의 다른 테이크 | `sound.variation` | WAV → 변형 1~5개(`strength` 0~3) | 50/호출 |
| 끊김 없는 반복 배경음 | `sound.looping` | WAV → 루프 WAV | 150/호출 |
| 모노를 스테레오로 | `sound.mono2stereo` | WAV → WAV | 50/호출 |
| 사람 목소리를 몬스터 음색으로 | `sound.conversion` | 목소리 + 크리처 참조음 → WAV | 150/호출 |
| 녹음 잡음 제거 | `sound.enhance` | WAV → WAV | 25/호출 |
| 빠른 음성 합성(안내·챗봇) | `tts.lite` | 텍스트(1,200바이트 이내) + 화자 → 음성 | 20자당 1 |
| 감정 연기 음성 합성(게임 대사) | `tts.standard` | 텍스트 + 화자 → 음성 | 10자당 1 |
| 목소리만 다른 화자로 | `vc.convert` / `vc.convert_custom` | 음성 + 화자 uuid(또는 화자 음성) → 음성 | 10초당 15 |
| 연기 톤을 살려 목소리 바꾸기 | `vc.acting` / `vc.acting_custom` | 연기 음성 + 화자 → 음성 | 미공개(10초당 15로 가정) |
| 음성으로 얼굴 애니메이션 | `face.blendshape` | 음성 → 프레임별 블렌드셰이프 JSON | 미공개 |
| 이미지로 3D 모델 | `3d.image_to_3d` | PNG → GLB(비동기) | 200(텍스처 없으면 100) |
| 배경 합성 | `image.background` | 전경(배경은 회색 128) → 이미지 | 120(4K 215) |
| 시점 변경 | `image.perspective` | 이미지 → front/side/top/back/isometric | 30/MP |
| 해상도 키우기 | `image.upscale` | 이미지 → 2~6배 | 출력 크기 구간별 50~3,200 |
| 지우기·인페인트·텍스처·그래픽 | `image.eraser` 등 | 이미지 + 마스크 → 이미지 | 30~120/MP |
| 가상 착장·헤드스왑 | `image.vton_*`, `image.headswap` | 인물 + 의상/얼굴 → 이미지 | 16~120/MP |
| 게임 텍스트 번역 | `mt.translate` | 원문 + 언어 → 번역(용어집 반영) | 미공개 |
| 화자 목록 | `voices.tts_lite`, `voices.tts_standard`, `voices.vc`, `voices.vc_acting` | → 화자 JSON | 무료로 가정 |

`python3 .claude/skills/varco-api/scripts/varco_client.py catalog` 로 엔드포인트·요청 형식·단가 전체를 볼 수 있다.

## 공용 스크립트 사용법

스크립트 위치: `.claude/skills/varco-api/scripts/`

| 파일 | 하는 일 |
| --- | --- |
| `varco_client.py` | 검사·호출·드라이런·3D 폴링·장부 요약 |
| `varco_catalog.py` | 엔드포인트, 파라미터 제약, 단가. 명세가 바뀌면 이 파일만 고친다 |
| `estimate_cost.py` | 매니페스트 전체 견적 |

### 호출 전: 검사

```bash
python3 .claude/skills/varco-api/scripts/varco_client.py validate sound.text2sound \
  --param prompt="heavy wooden door creaking open" --param num_sample=3 --param version=v2
```

필수 파라미터, 허용값, 범위, 글자·바이트 한도, 파일 형식(3D 는 PNG 만)을 검사하고 추정 크레딧을 알려 준다. 422 로 크레딧과 시간을 버리기 전에 여기서 잡는다.

### 호출

```bash
python3 .claude/skills/varco-api/scripts/varco_client.py call sound.variation \
  --file source=games/{slug}/assets/audio/sfx/sfx_door_01.wav \
  --param num_sample=4 --param strength=0.7 \
  --out games/{slug}/assets/audio/sfx/sfx_door_var.wav \
  --ledger _workspace/{slug}/varco_ledger.jsonl --asset-id sfx_door \
  --budget {run_meta.budget_credits}          # 실제 호출일 때
  # --dry-run                                 # 드라이런일 때(네트워크 없음)
```

- `--param key=value`: 값이 JSON 으로 읽히면 숫자·불리언·객체로 보낸다. 여러 개면 `--params p.json` 이 편하다.
- `--file field=path`: JSON 본문 API 는 파일을 base64 로 넣고, multipart API 는 파일로 첨부한다. 어느 쪽인지는 스크립트가 안다.
- `--out`: 결과가 여러 개면 `_01`, `_02` 가 붙는다. 확장자가 실제 형식과 다르면 실제 형식으로 바꿔 저장하고 경고한다.
- `--dry-run`: 호출하지 않고 `{out}.dryrun.json` 에 요청 명세(키는 가림)와 추정 크레딧을 쓴다. 앞 단계 결과처럼 아직 없는 입력 파일도 받아 '예정 입력'으로 적는다. 실제 호출에서는 입력 파일이 반드시 있어야 한다.
- `--budget`: 장부의 누적 사용·예약 크레딧에 이번 추정치를 더해 예산을 넘으면 호출하지 않는다. 여러 에이전트가 동시에 불러도 잠금으로 예약하므로 넘치지 않는다. 단가 미공개 API 는 `--allow-unknown-price` 를 붙여야 호출된다. `run_meta.json` 의 `allow_unknown_price` 가 `true` 일 때만 붙인다.
- 결과는 표준 출력에 JSON 으로 나온다(`ok`, `outputs`, `est_credits`, `error`). 이 JSON 을 그대로 작업 기록에 남긴다.

### 3D 비동기

`3d.image_to_3d` 는 `requestId` 를 받은 뒤 스크립트가 알아서 `/inference/result/{id}` 를 폴링하고 GLB 를 내려받는다(기본 15분 대기). 오래 걸릴 것 같으면 `--no-wait` 로 id 만 받고, 나중에 `varco_client.py result {requestId} --out ...glb` 로 받는다. `model_url` 은 7일 뒤 만료되므로 바로 내려받는다.

### 종료 코드와 대응

| 코드 | 뜻 | 할 일 |
| --- | --- | --- |
| 0 | 성공 | |
| 3 | 예산 초과 또는 단가 미상이라 호출 안 함 | 재시도하지 않는다. `budget_blocked` 로 보고 |
| 4 | 키 없음 | 드라이런으로 바꾸거나 리더에게 보고 |
| 10 | 인증 실패(401) | **재시도 금지.** `auth_failed` 로 즉시 보고 |
| 11 | 크레딧 부족·권한 거부 | **재시도 금지.** `credit_exhausted` 로 즉시 보고 |
| 12 | 요청 검증 실패(400·422·사전 검사) | 서버 메시지를 읽고 파라미터를 고쳐 다시 호출 |
| 13 | 서버 오류 반복 | 스크립트가 이미 한 번 재시도했다. 한 번 더 해 보고 안 되면 `failed` |
| 14 | 3D 작업 실패·시간 초과 | 입력 이미지를 바꾸거나 `result` 로 다시 받아 본다 |
| 15 | 응답 형식 이상 | 원문을 기록하고 `failed` 로 보고 |

### 장부

`_workspace/{slug}/varco_ledger.jsonl` 에 모든 호출(드라이런 포함)이 한 줄씩 남는다. 요약: `varco_client.py ledger --ledger _workspace/{slug}/varco_ledger.jsonl`. 장부는 스크립트만 쓴다. 손으로 고치지 않는다.

## 요청 형식에서 헷갈리기 쉬운 점

- 사운드·음성·얼굴·번역 API 는 JSON 본문이고, 오디오는 base64 문자열 필드(`source`, `reference`, `audio`, `speaker_audio`)로 넣는다.
- 이미지 편집·3D 는 multipart 다. 객체 파라미터(`vton`, `clothes_spec`, `specs`, `headswap`)는 JSON 문자열로 보낸다. 레퍼런스에 이렇게 명시된 곳은 헤드스왑뿐이라, 다른 API 에서 422 가 나면 이 부분부터 의심한다.
- TTS 의 `voice` 에는 화자 목록의 `speaker_uuid` 를 넣는다. `text` 는 UTF-8 1,200바이트(한글 약 400자)까지다. SSML 을 넣으면 다른 옵션은 무시된다.
- TTS 언어는 `korean`, `english`, `japanese`, `taiwanese` 이고, 번역 언어 코드는 `ko`, `en`, `ja`, `tw`, `cn`, `de`, `ru`, `es`, `pt`, `fr` 이다. 둘은 형식이 다르다.
- `image.background` 입력은 전경만 남기고 나머지를 회색(128,128,128)으로 칠한 이미지다.
- Text to Sound 출력은 항상 10초다. 짧은 효과음은 뒤쪽 무음을 잘라 써야 한다(ffmpeg `silenceremove` 등).

## 자세한 명세

필요한 API 의 파일만 읽는다. 모두 api.varco.ai 문서를 정리한 것이며, 제1부는 가이드(활용법·예시), 제2부는 레퍼런스(파라미터·응답)다.

| 파일 | 내용 |
| --- | --- |
| `references/sound.md` | 사운드 6종 |
| `references/voice.md` | TTS, 음성 변환 4종, 화자 목록 |
| `references/face.md` | Voice-to-Face 입력 옵션과 응답 JSON 구조 |
| `references/3d.md` | Image to 3D, 결과 조회, 예제 코드 |
| `references/image-edit.md` | Art Fashion 이미지 편집 11종 |
| `references/translate.md` | 번역 API |
| `references/platform.md` | 가입, 워크스페이스·권한, API 키, 크레딧, 인증, VARCO Chat·Gentle Words 소개 |
| `references/unity-plugin.md` | VARCO Sound Unity 플러그인(음악 생성 포함) |
