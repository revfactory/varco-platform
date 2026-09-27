---
name: marketing-kit
description: "출시 준비 단계에서 VARCO 이미지 편집 API(배경 합성, 업스케일, 시점 변경)로 스토어 키 아트·캡슐 이미지·아이콘을 만들고, 스토어 설명 문구를 쓰고 번역하는 방법. Steam·App Store·Google Play·itch.io 규격 맞추기, 한 장의 키 아트로 여러 크기를 잘라 쓰기, 제목 얹기, 실제 게임 화면 스크린샷 정리를 다룬다. varco-game-studio 5단계에서 매니페스트의 phase=release(marketing) 에셋을 만들거나 '스토어 이미지 만들어줘', '키 아트', '캡슐 이미지', '스토어 설명 써줘', '마케팅 이미지 다시' 요청에 marketing-artist 가 사용한다. 게임 안에 쓰는 이미지·3D 는 varco-visual-production 이 맡는다."
---

# 스토어 출시 이미지와 문구

5단계에서 게임 화면과 캐릭터 이미지를 받아 스토어에 올릴 이미지와 문구를 만든다. 매니페스트에서 `phase: release` 인 `mkt_*` 에셋만 만들고, 승인받은 `steps` 보다 많이 부르지 않는다. 규격은 `references/store-specs.md` 를 따른다.

## 입력과 출력

| 구분 | 경로 |
| --- | --- |
| 입력 | `run_meta.json`, `games/{slug}/manifest.json`(`phase: release`), `docs/concept.md`(한 줄 소개·핵심 재미·톤), `qa/screenshots/`(game-qa 가 4단계에서 남긴 실제 화면), `assets/images/`, `assets/models/` |
| 출력 | `games/{slug}/marketing/{id}[_NN].png`, `marketing/copy.csv`, `marketing/copy_{lang}.json`, `marketing/README.md`(파일별 스토어 자리), 작업 기록 `_workspace/{slug}/05_marketing_log.json` |

## 원칙

- **스크린샷은 실제 게임 화면만 쓴다.** 생성형 편집으로 게임에 없는 장면을 만들면 구매자를 속이게 되고, 스토어 심사에서도 거절 사유가 된다. 스크린샷은 자르기·크기 맞추기·업스케일까지만 한다.
- **키 아트는 한 장을 여러 크기로 잘라 쓴다.** 배경 합성 한 번이 120~215 크레딧이다. 21:9 4K 한 장이면 Steam Header·Small·Library Hero 를, 16:9 2K 한 장이면 Main Capsule·Page Background 를 얻는다.
- **제목은 마지막에 얹는다.** 규격 크기로 먼저 자른 뒤 `overlay_title.py` 로 제목을 넣는다. 제목을 얹고 자르면 제목이 잘린다. Library Hero 처럼 로고를 넣지 않는 자리도 있으니 규격표를 확인한다.
- **호출은 `varco_client.py` 로만 한다.** 드라이런이면 요청 명세만 만든다.

## 작업 순서

### 1. 원본 모으기

- 스크린샷: `games/{slug}/qa/screenshots/` 에서 코어 루프가 잘 보이는 화면 5~8장을 고른다. 없으면 리더에게 game-qa 캡처를 요청하고, 이 자리는 비워 둔 채 진행한다.
- 키 아트 주인공: `assets/images/` 의 캐릭터 이미지 또는 3D 모델. 3D 모델은 `blender` 로 투명 배경 렌더를 뽑을 수 있다(`blender -b -P` 스크립트). 둘 다 없고 매니페스트에 원본 계획(`source_image_plan: generate`)이 있으면 이미지 생성 스킬(codex-image 등)로 만들고 출처를 기록한다.

### 2. 키 아트 만들기

```bash
V=.claude/skills/varco-visual-production/scripts/prep_image.py
python3 $V remove-bg hero.png work/hero_cut.png            # 배경이 단색일 때
python3 $V gray-bg work/hero_cut.png work/hero_gray.png      # image.background 입력 형태
python3 .claude/skills/varco-api/scripts/varco_client.py call image.background \
  --file image=work/hero_gray.png --param mode=person \
  --param background_prompt="neon city street at night, rain reflections, subject centered, wide margins" \
  --param lighting_prompt="strong rim light, magenta and cyan neon" \
  --param output_aspect_ratio=21:9 --param output_image_size=4K \
  --out games/{slug}/marketing/_work/keyart_21x9.png --ledger _workspace/{slug}/varco_ledger.jsonl \
  --asset-id mkt_keyart --budget {budget_credits}
```

- 배경 프롬프트는 컨셉의 분위기에서 가져온다. 계절·시간·색감·조명은 `season_prompt`, `time_prompt`, `color_prompt`, `lighting_prompt` 로 나눠 쓰면 조절하기 쉽다.
- 사람 중심이면 `mode=person`, 물건·차량 중심이면 `mode=product`.
- 다른 각도가 필요하면 `image.perspective`(view: front·side·top·back·isometric)를 먼저 거친다.

### 3. 규격대로 자르고 제목 얹기

```bash
python3 $V fit work/keyart_21x9.png work/header_920x430.png --size 920x430
python3 .claude/skills/marketing-kit/scripts/overlay_title.py work/header_920x430.png \
  games/{slug}/marketing/mkt_steam_header.png --logo games/{slug}/assets/images/logo.png --pos center --scale 0.6
```

- 로고 파일이 없으면 `--text "{게임 제목}"` 으로 임시 로고를 얹는다. 결과 JSON 의 `temporary_logo: true` 를 작업 기록과 README 에 적는다. 정식 로고는 사람이 만들어야 한다.
- `fit` 결과에 `"원본보다 1.5배 넘게 키웠다"` 경고가 나오면 자르기 전에 `image.upscale` 을 거친다(매니페스트에 그 step 이 있을 때만).
- 아이콘은 1:1 로 자른다. App Store 아이콘은 알파 채널이 없어야 하므로 마지막에 `prep_image.py flatten icon.png mkt_icon_ios.png --fill "#101018"` 로 배경색을 채워 RGB PNG 로 저장한다.

### 4. 스크린샷 정리

- `fit --size 1920x1080 --mode contain` 으로 크기를 맞춘다. 원본이 더 작으면 업스케일 step 이 승인됐을 때만 `image.upscale` 을 쓴다.
- 파일 이름은 `mkt_screenshot_01.png` 처럼 번호를 붙인다.

### 5. 스토어 문구

`docs/concept.md` 의 한 줄 소개와 핵심 재미로 쓴다. 과장된 수식어("최고의", "혁명적인")를 빼고, 플레이어가 무엇을 하는 게임인지 첫 문장에 쓴다. 글자 수 한도는 `store-specs.md` 의 문구 표를 따른다.

`games/{slug}/marketing/copy.csv`:

```
string_id,text_ko,max_len,context
store.name,네온 드리프트,30,앱 이름
store.short,네온 도시의 밤을 3분 동안 미끄러지듯 달리는 드리프트 레이싱,80,Google Play 간단한 설명
store.long,...,4000,자세한 설명
```

번역은 varco-localization 의 스크립트를 그대로 쓴다.

```bash
python3 .claude/skills/varco-localization/scripts/translate_table.py --run-meta _workspace/{slug}/run_meta.json \
  --lang en --source-csv games/{slug}/marketing/copy.csv --out games/{slug}/marketing/copy_en.json
```

번역 API 는 단가 미공개라 실제 호출에는 리더 승인과 `--allow-unknown-price` 가 필요하다. 보고서의 `over_length` 가 있으면 한국어 원문을 줄여 다시 번역한다.

### 6. README 와 보고

`games/{slug}/marketing/README.md` 에 파일마다 스토어·자리·크기·임시 로고 여부·원본 출처를 표로 적는다. 중간 파일(`_work/`)은 남겨 두되 README 에서 제외한다.

## 드라이런

배경 합성·업스케일은 요청 명세만 만든다(`.dryrun.json`). 자르기와 제목 얹기는 로컬 작업이라 드라이런에서도 할 수 있지만, 입력이 자리표시 이미지뿐이면 하지 않는다. README 에 "드라이런: 실제 이미지 없음"을 적는다.

## 반환

단발 서브에이전트로 불리므로 리더에게 짧게 보고한다: 만든 파일 수(스토어별), 사용한 호출과 추정 크레딧, 임시 로고 여부, 빠진 자리(스크린샷 부족 등), 사람이 해야 할 일.
