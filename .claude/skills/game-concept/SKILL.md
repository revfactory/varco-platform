---
name: game-concept
description: "게임 디렉터가 쓰는 작업법. 막연한 게임 아이디어를 컨셉 문서로 구체화하고, 시스템·시나리오·레벨·UI·밸런스 문서를 서로 대조하는 통합 리뷰를 하고, 통합 GDD 를 쓰고, 출시 판정 보고서(RELEASE_REPORT.md)를 쓰는 절차와 템플릿을 담았다. 게임 컨셉 정리, 기획 문서 정합성 검토, GDD 통합, Go/No-Go 판정을 할 때 사용한다. 개별 시스템 설계나 대사 작성처럼 한 분야의 문서를 직접 쓰는 일에는 해당 분야 스킬(game-systems-design, game-narrative 등)을 쓴다."
---

# 게임 컨셉·통합 리뷰·출시 판정

게임 디렉터는 네 번 일한다. 처음에 컨셉을 정하고, 기획이 모이면 서로 맞는지 대조하고, GDD 로 묶고, 마지막에 출시 여부를 판정한다. 네 가지 모두 산출물 계약서(`.claude/skills/varco-game-studio/references/contracts.md`)의 경로와 이름을 따른다.

## 1. 아이디어를 컨셉으로 구체화하기

사용자 아이디어는 보통 한두 문장이다. 아래 순서로 빈칸을 채운다.

1. **핵심 재미를 한 문장으로 쓴다.** "플레이어는 ○○을 하면서 ○○을 느낀다" 꼴로 쓴다. 이 문장으로 뒤의 모든 결정을 거른다. 이 문장과 관계없는 기능은 범위에서 뺀다.
2. **코어 루프를 3~5단계로 쓴다.** 예: 달린다 → 코너에서 드리프트로 부스트를 모은다 → 부스트로 추월한다 → 결과 점수로 차를 강화한다. 루프가 한 바퀴 도는 데 걸리는 시간도 적는다.
3. **대상 플레이어와 플랫폼을 정한다.** 플랫폼은 `run_meta.json` 의 `engine`(web 또는 unity)과 맞춘다.
4. **범위를 표로 정한다.** "만들 것"과 "만들지 않을 것"을 나란히 적는다. 프로토타입은 코어 루프 하나를 증명하면 된다. 만들지 않을 것을 명시해야 기획 담당이 스스로 범위를 늘리지 않는다.
5. **VARCO 로 만들 수 있는지 확인한다.** 필요한 에셋을 크게 나눠 보고, 아래 제약에 걸리는 것은 대안을 적는다.

   | 에셋 | VARCO 로 가능한가 | 대안 |
   | --- | --- | --- |
   | 효과음·환경음 | 가능(Text to Sound, Variation, Looping) | |
   | 몬스터 음성 | 가능(Sound Conversion) | 가이드 녹음이 필요하면 사람이 녹음 |
   | 대사 음성 | 가능(TTS Standard, 음성 변환 Acting) | |
   | 얼굴 애니메이션 | 가능(Voice-to-Face) | |
   | 3D 모델 | 원본 이미지가 있으면 가능(Image to 3D, PNG) | 원본 이미지는 사용자 제공 또는 다른 이미지 생성 도구 |
   | 2D 원화·캐릭터 이미지 | **텍스트→이미지 API 없음.** 편집(배경 합성, 시점 변경, 업스케일)만 가능 | 사용자 제공, 이미지 생성 스킬, 도형·색 위주 그래픽 |
   | 배경음악 | **REST API 없음.** Unity 플러그인 Music 탭에서만 | 수동 제작, 환경음 루프로 대체 |
   | 번역 | 가능(Translate, 10개 언어) | |

6. **성공 기준을 측정할 수 있게 쓴다.** "재미있다"가 아니라 "첫 레벨 클리어 시간 중앙값 60~120초", "첫 판에서 코어 루프를 한 바퀴 이상 돈다"처럼 쓴다. balance-analyst 와 game-qa 가 이 숫자로 판정한다.
7. **가정을 밝힌다.** 아이디어에 없어서 당신이 정한 것은 문서 맨 앞 「가정」 절에 세 개 이하로 적는다. 리더가 사용자에게 확인할 수 있게 하기 위해서다.

### 컨셉 문서 템플릿 — `_workspace/{slug}/01_director_concept.md`

```markdown
# {게임 제목} 컨셉

## 가정
- (아이디어에 없어서 정한 것, 세 개 이하)

## 한 줄 소개
## 장르·플랫폼
- 장르:
- 플랫폼/엔진: web | unity
- 플레이 시간: 한 판 ○분, 전체 ○분

## 핵심 재미
플레이어는 ○○을 하면서 ○○을 느낀다.

## 코어 루프
1. …  (한 바퀴 약 ○초)

## 대상 플레이어
## 범위
| 만들 것 | 만들지 않을 것 |
| --- | --- |

## 에셋 방향
- 소리: …
- 음성: 캐릭터 ○명, 음성 대사 약 ○줄
- 3D/이미지: … (원본 이미지 확보 방법)
- 배경음악: 수동 제작 | 환경음으로 대체
- 언어: 원문 ko, 번역 {target_langs}

## 성공 기준
| 지표 | 목표 범위 | 확인 담당 |
| --- | --- | --- |

## 참고작
- {작품}: 가져올 점 / 가져오지 않을 점
```

리더에게는 "핵심 결정 세 가지"를 요약해 보고한다. 사용자가 컨셉을 승인할지 정하는 데 쓰인다.

## 2. 통합 리뷰 — 문서끼리 맞는지 대조하기

기획 담당 다섯 명의 문서가 모이면 한 문서만 읽어서는 보이지 않는 불일치를 찾는다. **한쪽 문서만 읽지 말고 두 문서를 함께 열어 값을 맞춰 본다.** 존재 여부만 보면 "레벨 문서에 적이 나온다"는 확인되지만 "그 적이 밸런스 표에 있는가"는 놓친다.

### 대조 점검표

| 대조 | 한쪽 | 다른 쪽 | 확인할 것 |
| --- | --- | --- | --- |
| 시스템 ↔ 레벨 | `01_systems_spec.md`, 밸런스 CSV | `01_level_design.md` | 레벨이 가리키는 적·아이템 `id` 가 CSV 에 모두 있는가. 레벨 난이도가 시스템의 성장 곡선과 맞는가 |
| 시스템 ↔ UI | 밸런스 CSV 열, 게임 상태 | `01_ux_spec.md` HUD 출처 | HUD 가 보여 주는 값의 출처가 실제로 있는 열·상태인가. 플레이어가 알아야 할 수치가 HUD 에서 빠지지 않았는가 |
| 시나리오 ↔ 레벨 | `01_narrative_bible.md` 장면·장소 | 레벨 문서의 장면 위치 | 모든 `scene_id` 가 레벨 어딘가에 배치됐는가. 레벨에 없는 장소가 대사에 나오지 않는가 |
| 대사 ↔ 캐릭터 | `01_narrative_dialogue.csv` 의 `speaker_id` | `01_narrative_characters.csv` | 모든 화자가 캐릭터 표에 있는가. `voice_type` 과 대사의 `voice` 방식이 맞는가(크리처가 `tts` 로 되어 있지 않은가) |
| 밸런스 판정 ↔ 시스템 | `01_balance_report.md` | 밸런스 CSV 최신본 | 보고서가 검증한 CSV 해시가 최신본과 같은가. 판정이 `pass` 인가, 아니면 남은 위험이 적혀 있는가 |
| 범위 ↔ 크레딧 | 컨셉 범위 | 레벨 사운드 구역, 프랍 목록, 음성 대사 줄 수 | 에셋 요구량이 프로토타입 범위에 맞는가. 음성 P0 줄이 코어 루프에 꼭 필요한 것뿐인가 |
| 용어 | `01_narrative_glossary.csv` | 모든 문서와 UI 문자열 | 같은 대상을 문서마다 다른 이름으로 부르지 않는가 |
| 컨셉 ↔ 전체 | 컨셉 「만들지 않을 것」 | 모든 문서 | 범위 밖 기능이 설계되지 않았는가 |

형식 검사는 스크립트로 먼저 돌린다. 사람이 대조해야 할 의미 문제에 시간을 쓰기 위해서다.

```bash
python3 .claude/skills/game-narrative/scripts/check_story_data.py \
  --characters _workspace/{slug}/01_narrative_characters.csv \
  --dialogue _workspace/{slug}/01_narrative_dialogue.csv \
  --glossary _workspace/{slug}/01_narrative_glossary.csv \
  --ui-strings _workspace/{slug}/01_ux_strings.csv
python3 .claude/skills/balance-simulation/scripts/check_balance_tables.py _workspace/{slug}/01_systems_balance
```

### 수정 요청 보내기

불일치 하나마다 담당에게 SendMessage 로 보낸다. 한 메시지에 문서·절·문제·원하는 결과를 담는다.

> `level` 에게: `01_level_design.md` 2-1절 3번 구간의 `elite_drone` 이 `enemies.csv` 에 없다. systems 에게 추가를 요청하거나 기존 `drone` 으로 바꿔 달라. 결정하면 리뷰 문서에 적을 수 있게 알려 달라.

담당마다 수정 요청은 2회까지 보낸다. 그래도 남은 불일치는 리뷰 문서에 적고 리더에게 결정을 넘긴다.

### 리뷰 문서 템플릿 — `_workspace/{slug}/01_director_review.md`

```markdown
# 통합 리뷰

## 요약
- 대조한 쌍: ○개, 발견한 불일치: ○건, 해결: ○건, 남음: ○건

## 불일치와 처리
| # | 대조 | 문제 | 근거(파일·절) | 요청 대상 | 결정 | 이유 | 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |

## 두 문서가 부딪힌 결정
- 쟁점: … / A 주장과 근거 / B 주장과 근거 / 고른 쪽과 이유

## 남은 위험
```

## 3. 통합 GDD — `_workspace/{slug}/01_director_gdd.md`

GDD 는 다른 문서를 다시 옮겨 적지 않는다. 내용을 복사하면 원본이 바뀔 때 GDD 가 낡는다. 요약과 링크, 그리고 리뷰에서 확정한 결정만 담는다. 링크는 승격 뒤 위치(`docs/*.md`, `data/*.csv`) 기준으로 쓴다.

```markdown
# {게임 제목} GDD

## 한눈에 보기
컨셉 요약 5줄 이내 → [컨셉](concept.md)

## 문서 지도
| 분야 | 문서 | 핵심 내용 한 줄 |
| --- | --- | --- |
| 시스템 | [systems.md](systems.md) · data/balance/ | |
| 시나리오 | [narrative.md](narrative.md) · data/dialogue.csv | |
| 레벨 | [levels.md](levels.md) | |
| UI/UX | [ux.md](ux.md) · data/ui_strings.csv | |
| 밸런스 | [balance-report.md](balance-report.md) | 판정: |

## 확정한 결정
| # | 결정 | 근거 | 영향받는 문서 |

## 에셋 요구 요약
- 사운드 구역 ○곳, 3D·프랍 ○개, 음성 대사 ○줄(P0 ○줄), 번역 언어 ○개
- 수동 제작이 필요한 것: …

## 개발 모듈 제안
엔지니어가 모듈 계획을 세울 때 참고할 순서(코어 루프 먼저)

## 성공 기준
컨셉의 표를 그대로 가져오고 확인 담당을 적는다.
```

## 4. 출시 판정 — `games/{slug}/RELEASE_REPORT.md`

5단계에서 아래 보고서를 모두 읽는다. 보고서끼리 모순되면(예: 에셋 감사는 누락 0건인데 회귀 보고서에 "소리 안 남"이 있다) 원본 파일을 직접 열어 확인한다.

- `games/{slug}/qa/reports/regression.md`, `asset-audit.md`, `balance-impl.md`
- `games/{slug}/qa/bugs/*.md` (상태가 `open` 인 S1·S2)
- `games/{slug}/manifest.json` (에셋 상태)
- 장부 요약: `python3 .claude/skills/varco-api/scripts/varco_client.py ledger --ledger _workspace/{slug}/varco_ledger.jsonl`
- `run_meta.json` 의 `budget_credits`, `varco_mode`

판정 기준은 계약서 9절이다. 기준마다 근거 파일을 적는다. 보고서가 없는 기준은 "미검증"이며 통과로 세지 않는다.

```markdown
# {게임 제목} 출시 판정 보고서

## 판정: Go | 조건부 Go | No-Go
한 문단으로 이유를 쓴다.

## 기준별 결과
| 기준 | 통과 조건 | 결과 | 근거 |
| --- | --- | --- | --- |
| 버그 | S1·S2 open 0건 | 통과/실패/미검증 | qa/bugs/…, regression.md |
| 에셋 | P0 모두 qa_passed (드라이런이면 명세 통과) | | manifest.json, asset-audit.md |
| 데이터 정합성 | CSV↔구현 불일치 0, 에셋 참조 누락 0 | | balance-impl.md, asset-audit.md |
| 현지화 | 언어별 누락 0, 글자 수 초과 0 | | asset-audit.md |
| 밸런스 | 판정 pass 또는 위험 수용 기록 | | balance-report.md, balance-impl.md |
| 크레딧 | 실제 사용 추정 ≤ 승인 예산 | | 장부 요약 |

## 받아들이는 위험
기준을 어겼는데도 Go/조건부 Go 를 준다면 여기에 어긴 기준, 위험, 받아들이는 이유를 쓴다.

## 남은 일
| 항목 | 담당 | 우선순위 |
(수동 제작 에셋, open 버그, 드라이런이면 실제 생성 등)

## 실행 방법
빌드를 실행하는 명령과 경로

## 사용한 크레딧
실제 사용 추정 / 승인 예산 / 단가 미상 호출 수
```

판정은 기준표로만 한다. 인상으로 Go 를 주면 다음 실행에서 무엇을 고쳐야 할지 아무도 알 수 없다.
