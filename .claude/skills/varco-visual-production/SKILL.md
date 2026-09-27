---
name: varco-visual-production
description: "VARCO 3D(Image to 3D)와 Art Fashion 이미지 편집 API 로 게임용 3D 모델(GLB)과 편집 이미지를 만드는 방법. 원본 이미지 확보(VARCO 에 텍스트→이미지 API 가 없으므로 사용자 제공 또는 이미지 생성 스킬), 배경 제거·정사각 패딩·회색 배경·마스크 만들기, face 수·타입·텍스처 설정, 비동기 결과 받기, 배경 합성·시점 변경·업스케일·지우기·인페인트 조합을 다룬다. 매니페스트의 model_3d·image 에셋을 만들거나 '3D 모델 만들어줘', '프랍 생성', '이미지 배경 바꿔줘', '업스케일' 요청에 visual-artist 가 사용한다. 스토어용 이미지 가공은 marketing-kit 이 맡는다."
---

# VARCO 3D·이미지 제작

매니페스트 에셋 하나를 받아 원본 이미지를 준비하고, VARCO 3D 나 이미지 편집 API 로 결과를 만든다. 호출은 `varco_client.py` 로만 하고 매니페스트 `steps` 의 순서와 횟수를 지킨다. 입력 가공은 `scripts/prep_image.py` 로 한다.

## 작업 순서

1. `run_meta.json` 과 매니페스트 에셋(`brief`, `inputs`, `source_image_plan`, `steps`, `output`, `acceptance`)을 읽는다.
2. 원본 이미지를 확보한다(아래 표).
3. API 가 요구하는 형태로 가공한다.
4. `validate` → `call`. 3D 는 비동기라 스크립트가 결과를 기다린다.
5. 작업 기록 `_workspace/{slug}/03_visual_{id}.json` 에 원본 출처, 가공 명령, 호출 결과를 남긴다.
6. PRODUCE 스키마로 반환한다.

중간 파일은 `_workspace/{slug}/03_visual_work/{id}/` 에 두고 최종 결과만 `games/{slug}/assets/models/`, `assets/images/` 에 둔다.

## 원본 이미지 확보

VARCO 에는 텍스트로 이미지를 그리는 API 가 없다. 매니페스트의 `source_image_plan` 을 따른다.

| 값 | 할 일 |
| --- | --- |
| `provided` | `inputs` 경로의 파일을 쓴다. 없으면 `failed` 로 반환하고 필요한 파일을 `notes` 에 적는다 |
| `generate` | 이 세션에 이미지 생성 스킬(`codex-image`, `gemini-imagegen` 등)이 있으면 그 스킬로 `brief` 의 그림을 만들어 `inputs` 경로에 저장한다. 작업 기록에 쓴 스킬과 프롬프트를 남긴다(출처 기록). 생성 도구가 없으면 `failed` 로 반환하고 "원본 이미지 필요"를 적는다 |
| `manual` | 워크플로가 `manual_pending` 으로 처리하므로 불리지 않는다. 불렸다면 원본이 준비된 것이니 `inputs` 를 확인한다 |

이미지 생성 호출은 VARCO 크레딧이 아니지만 외부 서비스 비용이 들 수 있다. 에셋당 원본은 한두 장으로 끝낸다.

**Image to 3D 원본 조건:** 3D 품질은 원본에서 거의 결정된다.
- 물체 하나만, 전체가 잘리지 않게, 정면에서 약간 위(3/4 시점)에서 본 모습
- 단색 또는 투명 배경, 그림자·바닥 반사 없음
- 부품이 많은 물체는 부품별로 나눠 만든다(VARCO 문서의 시네마틱 사례도 파츠 단위로 만들어 조립했다)
- 생성 프롬프트 예: `single wooden treasure chest, game prop, 3/4 view, plain white background, no shadow, full object visible`

## 입력 가공 — prep_image.py

| 명령 | 쓰는 곳 |
| --- | --- |
| `info in.png` | 크기·알파·메가픽셀 확인(업스케일·편집 단가가 출력 크기로 정해진다) |
| `to-png in.jpg out.png` | Image to 3D 는 PNG 만 받는다 |
| `remove-bg in.png out.png --color auto --tol 24` | 단색 배경을 투명하게. 복잡한 배경에는 쓰지 않는다 |
| `square in.png out.png --size 1024` | 물체를 가운데 두고 여백을 둔 정사각형으로 |
| `gray-bg in.png out.png` | `image.background` 입력: 전경 + 회색(128,128,128) 배경 |
| `mask-rect in.png out.png --box x,y,w,h` / `mask-alpha` | 지우기·인페인트·텍스처용 마스크(흰색이 편집 영역, 원본과 같은 크기) |
| `fit in.png out.png --size 1920x1080` | 결과를 정해진 크기로 자르거나 맞춤 |
| `flatten in.png out.png --fill "#RRGGBB"` | 알파 채널을 없애 RGB 로 저장 |
| `placeholder out.png --size 512x512` | 드라이런에서 원본 대신 넘길 회색 이미지 |

3D 입력의 기본 가공: `to-png` → `remove-bg`(필요 시) → `square --size 1024`.

## Image to 3D

```bash
python3 .claude/skills/varco-api/scripts/varco_client.py call 3d.image_to_3d \
  --file image=_workspace/{slug}/03_visual_work/{id}/src_sq.png \
  --param target_face_type=tri --param target_face_num=8000 --param generate_texture=true \
  --out games/{slug}/assets/models/{id}.glb --ledger ... --asset-id {id} --budget ...
```

| 파라미터 | 기준 |
| --- | --- |
| `target_face_num` | 1,000~300,000. 웹 프로토타입 소품 3,000~10,000, 주인공 20,000~50,000. 기본값 300,000 은 웹에서 무겁다 |
| `target_face_type` | `tri`(게임 엔진 기본) / `quad`(DCC 툴에서 다시 다듬을 때) |
| `generate_texture` | `false` 면 메시와 노말 맵만, 크레딧 절반(100). 색을 코드로 입히는 로우폴리 스타일이면 false |
| `seed` | 재작업 때 같은 결과를 원하면 고정 |

- 스크립트가 최대 15분 기다린다. 끝나지 않으면 종료 코드 14 와 함께 `{out}.request.json` 에 requestId 가 남는다. `varco_client.py result {requestId} --out ...glb` 로 이어 받는다. `model_url` 은 7일 뒤 만료된다.
- 결과 GLB 가 `acceptance.face_max` 를 넘을 수 있다. 검사는 asset-qa 가 하지만, 받은 뒤 `blender` 가 있으면 면 수를 확인해 작업 기록에 적어 둔다.

## 이미지 편집 조합

| 목적 | 순서 |
| --- | --- |
| 캐릭터·아이템을 새 배경에 | `remove-bg` → `gray-bg` → `image.background`(mode=person 또는 product, prompt·season·time·lighting) |
| 다른 각도 이미지 | `image.perspective`(view: front·side·top·back·isometric) |
| 원치 않는 부분 제거 | `mask-rect` → `image.eraser` |
| 일부를 글로 바꾸기 | 마스크 → `image.inpaint`(model: sdxl 또는 nano_banana, prompt) |
| 무늬·재질 바꾸기 | 마스크 → `image.texture`(texture_image, x·y·width·height·angle) |
| 로고·문양 넣기 | `image.graphic`(texture: embossed·debossed·embroidered·printed·metal) |
| 해상도 키우기 | `image.upscale`(scale_factor 2~6). 출력 메가픽셀 구간으로 과금되니 필요한 크기만큼만 |

편집 결과는 PNG 로 온다. `--out` 확장자가 달라도 스크립트가 실제 형식으로 바꿔 저장하고 경고한다.

## 드라이런

- 원본이 아직 없으면(`generate` 계획) 이미지 생성도 하지 않는다. `prep_image.py placeholder` 로 회색 이미지를 만들어 `--file` 에 넘기고 요청 명세만 만든다. 작업 기록에 "원본 예정 경로: {inputs}"를 적는다.
- 반환 `outputs` 에 `.dryrun.json` 경로를 적고 `status` 는 `dry-run` 이다.

## 오류 대응

| 상황 | 할 일 |
| --- | --- |
| 종료 코드 3 / 10 / 11 | `budget_blocked` / `auth_failed` / `credit_exhausted` 로 즉시 반환 |
| 종료 코드 12 | 파일 형식(PNG), 필수 파라미터, 객체 파라미터(JSON 문자열)를 확인해 한 번 더 |
| 종료 코드 14(3D 실패·시간 초과) | 시간 초과면 `result` 로 한 번 더 받는다. 실패면 원본을 바꿔야 하므로 `failed` 로 반환하고 원본 조건 중 무엇이 문제였을지 `notes` 에 적는다 |
| 원본 없음 | `failed`, `notes` 에 필요한 파일 |
