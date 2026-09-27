---
name: game-narrative
description: "시나리오 기획자가 쓰는 작업법. 세계관·캐릭터 바이블·장면 목록·퀘스트를 쓰고, VARCO 음성 제작과 현지화가 그대로 읽는 characters.csv, dialogue.csv, glossary.csv 를 계약서 형식대로 만드는 규칙을 담았다. 대사를 VARCO TTS·음성 변환·크리처 변환으로 만들 때의 제약(1,200바이트, emotion 다섯 값, 음성 방식 선택)과 형식 검사 스크립트 check_story_data.py 를 포함한다. 게임 스토리·캐릭터 설정·대사 작성과 수정, 용어집 정리를 할 때 사용한다. UI 문자열 표는 game-ux-design, 실제 음성 생성은 varco-voice-production 스킬이 맡는다(단, ui_strings.csv 형식 검사는 이 스킬의 스크립트를 쓴다)."
---

# 게임 시나리오와 대사 데이터

시나리오 문서는 사람이 읽고, 캐릭터·대사·용어 CSV 는 음성 제작·번역·코드가 읽는다. 사람이 읽는 문서는 자유롭게 쓰되 CSV 는 계약서(`.claude/skills/varco-game-studio/references/contracts.md` 4-2, 4-3, 4-5절) 형식을 한 글자도 바꾸지 않는다. 열 이름 하나가 달라지면 뒤 단계 스크립트가 그 열을 빈 값으로 읽는다.

## 1. 작업 순서

1. 컨셉의 핵심 재미와 범위를 읽고 이야기의 분량을 정한다. 퍼즐·레이싱처럼 서사가 가벼운 장르는 튜토리얼 안내와 짧은 반응 대사 위주로 쓴다.
2. 세계관과 캐릭터를 바이블에 쓴다(2절).
3. 장면 목록을 만들고 `level` 에게 먼저 보낸다. 레벨 디자이너가 장면을 배치해야 하기 때문이다.
4. 캐릭터 표, 대사 스크립트, 용어집을 쓴다(3~5절).
5. 형식 검사를 돌리고 오류가 0건이면 완료를 알린다(6절).

## 2. 바이블 템플릿 — `_workspace/{slug}/01_narrative_bible.md`

```markdown
# {게임 제목} 시나리오 바이블

## 이야기 한 문단
## 세계관
- 시대·장소·분위기
- 플레이어가 알아야 할 규칙(세계 안의 설명)

## 캐릭터
### {speaker_id} — {이름}
- 역할 / 성격 / 말투 예시 두 줄
- 플레이어와의 관계
- 목소리 방향: characters.csv 의 voice_brief 와 같은 내용

## 장면 목록
| scene_id | 위치(레벨) | 계기 | 등장 캐릭터 | 대사 줄 수 | 목적 |
| --- | --- | --- | --- | --- | --- |

## 퀘스트
| id | 목표 | 시작 장면 | 완료 조건 | 보상(밸런스 표 id. systems 가 표를 확정하기 전이면 `미정` 으로 두고 확정 뒤 채운다) |

## 용어
새 고유명사는 glossary.csv 에 넣는다. 여기에는 설명이 필요한 것만 적는다.
```

`scene_id` 는 영문 snake_case 로 짓는다(`ch1_intro`, `boss_taunt`). 대사의 `line_id` 와 음성 파일 이름이 이 값에서 나온다.

## 3. 캐릭터 표 — `_workspace/{slug}/01_narrative_characters.csv`

열: `speaker_id,name_ko,role,gender,age_band,personality,voice_brief,voice_type,face_anim`

- `speaker_id`: 영문 snake_case. 대사·음성·얼굴 애니메이션이 모두 이 값으로 캐릭터를 찾는다.
- `gender`: 목소리의 성별. `male` \| `female` \| `none`(크리처처럼 성별이 없는 소리). 몸은 없고 목소리만 있는 AI 도 들리는 목소리 기준으로 적는다. 캐스팅이 이 값으로 화자를 거른다.
- `age_band`: 목소리의 나이대. `child` \| `teen` \| `20s` \| `30s` \| `40s` \| `50s+` \| `n/a`(크리처)
- `voice_brief`: 보이스 디렉터가 VARCO 화자 1,293명 가운데 고를 기준이다. 성별, 나이대, 음높이, 말 빠르기, 질감을 구체적으로 쓴다. "멋진 목소리"로는 고를 수 없다.
  - 좋은 예: `낮고 건조한 20대 여성, 말이 빠르고 끝을 흐린다`
- `voice_type`: `human` \| `creature` \| `none`. 몬스터·로봇처럼 사람 목소리가 아니면 `creature` 다. 사운드 디자이너가 사운드 변환(Conversion)으로 만든다. 크리처 줄의 `text_ko` 에는 울음·의성어를 묘사해 적는다(예: `(낮고 긴 으르렁거림)`). 사람이 가이드를 녹음할 예정이면 그 대본을 적는다.
- `face_anim`: `y` \| `n`. 얼굴이 화면에 나오고 입 모양이 보이는 캐릭터만 `y` 로 둔다. Voice-to-Face 호출이 줄마다 하나씩 늘기 때문이다.

## 4. 대사 스크립트 — `_workspace/{slug}/01_narrative_dialogue.csv`

열: `line_id,scene_id,speaker_id,text_ko,emotion,direction,voice,priority`

| 열 | 규칙 | 이유 |
| --- | --- | --- |
| `line_id` | `{scene_id}_{세 자리 순번}`. 예: `ch1_intro_003`. 중복 금지 | 문자열 키이자 음성 파일 이름이다 |
| `speaker_id` | `characters.csv` 에 있는 값만 | 없는 화자는 캐스팅할 수 없다 |
| `text_ko` | UTF-8 1,200바이트 이하(한글 약 400자). 실제로는 한 호흡(80자 안팎)으로 끊는다 | TTS 입력 한도다. 짧을수록 음성 연기가 안정적이다 |
| `emotion` | `neutral` \| `angry` \| `happy` \| `sad` \| `surprise` | Voice-to-Face 의 emotion 값과 같다. 다른 값은 API 가 받지 않는다 |
| `direction` | 연기 지시(한숨, 속삭임, 외침) | 보이스 디렉터가 TTS 속도·음높이·SSML 이나 Acting 변환을 고를 때 쓴다 |
| `voice` | `tts` \| `acting` \| `creature` \| `none` | 음성 제작 방식(아래) |
| `priority` | `P0` \| `P1` \| `P2` | 크레딧이 모자라면 P0 만 만든다 |

### 음성 방식 고르기

| 방식 | 언제 | VARCO 호출 |
| --- | --- | --- |
| `tts` | 안내, 일반 대화, 짧은 반응 | TTS Standard |
| `acting` | 감정 기복이 큰 컷신, 외침·울음 | TTS 또는 가이드 녹음 → 음성 변환 Acting |
| `creature` | `voice_type` 이 `creature` 인 캐릭터 | 가이드 음성 → Sound Conversion(크리처 참조음) |
| `none` | 텍스트로만 보여 줄 대사 | 없음 |

`acting` 은 호출이 두 번 들고 단가도 공개되지 않았다. 꼭 필요한 장면에만 쓴다.

### 자리표시자

바뀌는 값은 `{player_name}`, `{count}` 처럼 중괄호 안에 영문 snake_case 로 쓴다. 번역 단계가 이 부분을 보호하고, 코드가 실제 값으로 바꾼다. 자리표시자가 든 대사를 음성으로 만들면 값이 들어가지 않으므로, 음성 대사에는 자리표시자를 쓰지 않거나 `voice` 를 `none` 으로 둔다.

### 예시

```csv
line_id,scene_id,speaker_id,text_ko,emotion,direction,voice,priority
ch1_intro_001,ch1_intro,hero,또 너야? 이번엔 안 놓쳐.,angry,"이를 악물고, 낮게",tts,P0
ch1_intro_002,ch1_intro,rival,잡을 수 있으면 잡아 봐.,happy,여유롭게 웃으며,tts,P0
boss_taunt_001,boss_taunt,core_beast,크르르… 여기가 끝이다.,angry,짐승처럼 으르렁,creature,P1
tut_hint_001,tut,system,{key_drift} 키를 눌러 드리프트하세요.,neutral,,none,P0
```

## 5. 용어집 — `_workspace/{slug}/01_narrative_glossary.csv`

열: `term_ko`, 대상 언어마다 `term_{lang}`(`run_meta.target_langs` 기준. 대상이 `en` 뿐이면 `term_en` 만), `note`, `do_not_translate`. 대상이 아닌 언어의 열은 만들지 않는다. 요청받지 않은 언어를 채우면 번역 담당이 쓰지 않을 값을 관리하게 된다.

- 고유명사(인물·장소·조직·아이템)와 게임 용어(부스트, 드리프트 게이지)를 모두 넣는다.
- 번역하지 않을 말은 `do_not_translate` 에 `y` 를 적고, 대상 언어 열(`term_{lang}`)에는 원문 그대로 또는 표기(음역)를 적는다.
- `run_meta.json` 의 `target_langs` 에 다른 언어가 있으면 `term_{lang}` 열을 더한다(`term_tw`, `term_de` 등). 현지화 담당이 번역 전후로 이 표를 대조한다.

## 6. 형식 검사 — `scripts/check_story_data.py`

```bash
python3 .claude/skills/game-narrative/scripts/check_story_data.py \
  --characters _workspace/{slug}/01_narrative_characters.csv \
  --dialogue _workspace/{slug}/01_narrative_dialogue.csv \
  --glossary _workspace/{slug}/01_narrative_glossary.csv
# UI 문자열도 같은 스크립트로 검사한다(ux-designer)
python3 .claude/skills/game-narrative/scripts/check_story_data.py --ui-strings _workspace/{slug}/01_ux_strings.csv
```

- 검사 항목: 열 이름, `emotion`·`voice`·`priority`·`gender`·`voice_type`·`face_anim` 허용값, `speaker_id` 존재, `line_id` 형식·중복·`scene_id` 접두사, `text_ko` 바이트 수, 자리표시자 형식, 음성 대사의 자리표시자, 크리처 화자와 `voice` 방식, UI 문자열의 `placeholders` 열과 실제 자리표시자 일치, `max_len` 초과.
- 결과는 JSON 이다. `errors` 가 있으면 종료 코드 1, 경고(`warnings`)는 사람이 판단한다.
- 확정 폴더를 한 번에 검사하려면 `--game-dir games/{slug}` 를 준다(`data/` 아래 네 파일을 찾는다).

## 7. 수정할 때

- 기존 `line_id` 는 바꾸지 않는다. 음성 파일과 번역이 이미 그 이름으로 있을 수 있다. 대사를 고치면 같은 `line_id` 의 `text_ko` 만 바꾸고, 바꾼 목록을 리더에게 알린다(음성·번역을 다시 만들어야 한다).
- 대사를 지우면 지운 `line_id` 목록을 리더에게 알린다.
- 동결 뒤에는 `_v2` 파일로 쓴다.
