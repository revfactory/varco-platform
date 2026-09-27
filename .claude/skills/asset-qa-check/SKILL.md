---
name: asset-qa-check
description: "VARCO 로 만든 게임 에셋을 측정해 매니페스트 acceptance 기준과 대조하는 검증 절차와 스크립트. 오디오(길이·채널·피크·LUFS·루프 이음매), 얼굴 애니메이션 JSON(구조·음성 싱크), 3D GLB(구조·삼각형 수·텍스처), 이미지(크기·비율·알파·단색), 현지화 문자열(누락·자리표시자·글자 수·용어집), 드라이런 요청 명세, 출시 전 에셋 전수 감사(매니페스트↔파일↔코드 참조)를 다룬다. 에셋 QA, 에셋 검증, 03_assetqa 결과 작성, asset-audit 보고서, '이 사운드/모델/이미지 검사해줘', '에셋 누락 확인' 요청에 사용한다. 게임 기능·플레이 버그 검사는 game-qa-testing, 밸런스 수치 검증은 balance-simulation 이 맡는다."
---

# 에셋 QA — 파일이 있는지가 아니라 값이 맞는지 본다

에셋 QA 는 두 번 일한다. 3단계 워크플로에서 에셋 하나가 만들어질 때마다 바로 검사하고, 5단계에서 모든 에셋을 코드와 함께 전수 감사한다. 어느 쪽이든 파일이 있다는 사실만으로 통과시키지 않는다. 길이, 피크, 삼각형 수, 글자 수처럼 acceptance 가 요구하는 값을 스크립트로 재서 기준과 대조한다. 파일이 있어도 10초짜리 무음이거나 GLB 가 반쯤 잘려 있으면 게임에서 쓸 수 없기 때문이다.

파일 위치와 형식은 `.claude/skills/varco-game-studio/references/contracts.md`(산출물 계약서) 5~7절을 따른다.

## 스크립트

모두 `.claude/skills/asset-qa-check/scripts/` 에 있고, 계약서 7-1절 QA 결과 JSON(`id, verdict, mode, checks, issues, retryable, fix_hint`)을 표준 출력에 쓰며 `--out` 으로 파일에도 쓴다. 종료 코드는 pass 면 0, 아니면 1이다.

| 스크립트 | 대상 | 주요 옵션 |
| --- | --- | --- |
| `audio_check.py` | 효과음·환경음·크리처·대사 음성 | `--acceptance JSON`, `--expect-count N`, `--loop` |
| `face_check.py` | Voice-to-Face 응답 JSON | `--face-dir --audio-dir --lines …` |
| `glb_check.py` | 3D 모델 | `--acceptance '{"face_max":…, "has_texture":…}'` |
| `image_check.py` | 이미지·마케팅 | `--acceptance '{"min_size":[w,h], "aspect":"16:9"}'`, `--require-alpha` |
| `strings_check.py` | 현지화 문자열 | `--game-dir --langs en ja`, `--allow-dryrun` |
| `dryrun_check.py` | 드라이런 요청 명세 | `--manifest --id --game-dir --ledger` |
| `merge_reports.py` | 여러 결과를 에셋 하나로 합침 | `--id --mode --out` |
| `audit_assets.py` | 5단계 전수 감사 | `--game-dir --engine --md` |
| `qa_common.py` | 공통 모듈(결과 형식, 기대 파일 경로 계산) | 직접 실행하지 않는다 |

## 3단계: 에셋 하나 검증

워크플로 프롬프트로 에셋 id, 제작 결과(`status`, `outputs`, `notes`), 모드가 들어온다.

1. **기준을 읽는다.** `games/{slug}/manifest.json` 에서 id 가 같은 항목의 `output`, `acceptance`, `lines`, `steps` 를 읽는다. 기대 결과 파일 목록은 `qa_common.expected_outputs()` 규칙(단일 `{basename}.{format}`, 여러 개 `_01…`, 묶음 대사 `{line_id}`, `extra`)과 같다.
2. **모드에 따라 도구를 고른다.**

   | 모드·분류 | 실행할 검사 |
   | --- | --- |
   | dry-run (모든 분류) | `dryrun_check.py` 로 명세 검사. 현지화는 파일이 있으면 `strings_check.py --allow-dryrun` 도 |
   | live · sfx / creature_voice | `audio_check.py 결과파일들 --expect-count {output.count} --acceptance '{acceptance}'` |
   | live · ambience | 위와 같되 `--loop`(acceptance 에 loop 가 없어도 환경음은 루프로 쓴다) |
   | live · voice_line | 음성은 `audio_check.py`, `extra` 에 얼굴 JSON 이 있으면 `face_check.py --lines …` 로 싱크까지 |
   | live · model_3d | `glb_check.py` |
   | live · image / marketing | `image_check.py`. 투명 배경이 필요하다고 brief 에 적혀 있으면 `--require-alpha` |
   | live · localization | `strings_check.py --langs {에셋이 다루는 언어}` |
   | manual.* 에셋 | 검사하지 않는다(워크플로가 `manual_pending` 으로 넘긴다) |

3. **눈으로 확인할 수 있는 것은 직접 본다.** 이미지와 마케팅 결과는 Read 도구로 열어 brief 와 맞는지(엉뚱한 물체, 깨진 얼굴, 남은 마스크 자국) 확인하고 문제가 있으면 `visual_match` 검사로 추가한다. 3D 는 필요하면 Blender 배치 렌더로 썸네일을 만들어 본다:
   `blender -b --python-expr "import bpy,sys; bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath='{glb}'); bpy.ops.object.camera_add(location=(3,-3,2),rotation=(1.1,0,0.8)); bpy.context.scene.camera=bpy.context.object; bpy.ops.object.light_add(type='SUN'); bpy.context.scene.render.filepath='{png}'; bpy.ops.render.render(write_still=True)"`
   소리는 들을 수 없다. 기술 값만 판정하고, 청감 검토가 필요하다는 점은 `issues` 에 "정보:" 로 남긴다.
4. **여러 스크립트를 썼으면 합친다.** 각 결과를 임시 파일로 쓰고 `merge_reports.py … --id {id} --mode {mode} --out _workspace/{slug}/03_assetqa_{id}.json`. 재검증 회차면 파일 이름에 `_r2` 를 붙인다.
5. **retryable 을 판단한다.** 스크립트는 실패가 있으면 일단 true 로 둔다. 제작 담당이 파라미터·프롬프트·후처리로 고칠 수 있는 실패만 true 로 남긴다. 아래 경우는 false 로 바꾼다.
   - 원본 입력(사용자 제공 이미지, 녹음)이 없거나 쓸 수 없다
   - 매니페스트 기준 자체가 모순이다(예: 10초 고정 출력에 루프 기준 0.5초) — `issues` 에 "기준 수정 필요"라고 적는다
   - 예산 초과·단가 미상으로 막혔다
6. **반환한다.** 워크플로에는 QA 스키마(아래 「반환 형식」)로 돌려준다.

### acceptance 검사 이름별 측정 방법

| 검사 | 측정 | 스크립트 |
| --- | --- | --- |
| `duration_s` [최소, 최대] | ffprobe 길이 | audio_check |
| `channels`, `sample_rate` | ffprobe 스트림 정보 | audio_check |
| `peak_dbfs_max` | 디코딩 후 최대 절댓값(dBFS) | audio_check |
| `lufs_range` | ffmpeg ebur128 통합 라우드니스. 0.4초보다 짧으면 측정 불가(skip) | audio_check |
| `loop` | 끝·시작 50ms RMS 차이(6dB 초과 실패), 경계 샘플 점프(내부 인접 차이 99.9 백분위수의 4배와 0.05 초과 실패). 경험칙이므로 경계값 근처는 issues 에 적는다 | audio_check |
| `face_max` | 삼각형 수(quad 요청이면 삼각형이 약 2배) | glb_check |
| `has_texture` | 텍스처가 걸린 재질과 이미지가 모두 있는가 | glb_check |
| `min_size`, `aspect` | 픽셀 크기, 비율 1% 오차 | image_check |
| `lang_coverage` | 원문 키가 대상 언어에 모두 있는가(빈 문자열도 누락) | strings_check |
| `max_len_ok` | ui_strings.csv 의 max_len 대비 글자 수 | strings_check |
| 항상 | 디코딩 가능, 무음 아님(피크 -60dBFS 초과), 단색 아님(표준편차 2 이상), GLB 선언 길이 = 실제 크기 | 각 스크립트 |

### 드라이런 검증

드라이런은 실제 파일이 없으므로 "요청을 그대로 실제로 보냈을 때 통과할 명세인가"를 본다. `dryrun_check.py` 는 장부에서 해당 에셋의 드라이런 기록을 찾아 명세마다 `validate_params` 를 다시 돌리고, 매니페스트 step 마다(묶음 대사는 줄 수만큼) 명세가 있는지, 승인되지 않은 API 를 부르지 않았는지, 최종 출력 경로가 `output.dir` 아래인지, 장부에 실패한 드라이런이 없는지 확인한다. 통과하면 워크플로가 `dry-run` 상태로 기록한다.

## 5단계: 전수 감사

1. `python3 .claude/skills/asset-qa-check/scripts/audit_assets.py --game-dir games/{slug} --engine {engine} --out _workspace/{slug}/05_assetqa_audit.json --md games/{slug}/qa/reports/asset-audit.md`
   - 코드가 가리키는데 없는 파일, P0 결과 누락, 매니페스트 상태 불일치는 실패다. 수동 제작 대기(`manual_pending`) 파일은 따로 표시된다.
   - 코드가 경로를 조립하면(`${lineId}`) 앞부분을 동적 접두사로 보고, `manifest.json` 을 읽는 코드가 있으면 매니페스트 결과물 전체를 쓰이는 것으로 친다.
2. 현지화 전체: `strings_check.py --game-dir games/{slug} --langs {run_meta.target_langs}`
3. `qa_passed` 인 P0 에셋을 분류마다 두 개 이상 골라 3단계 검사를 다시 돌린다. 3단계 이후 누군가 파일을 바꿨는지 확인하기 위해서다.
4. 보고서 `games/{slug}/qa/reports/asset-audit.md` 에 스크립트 표와 함께 아래를 덧붙인다: 재검사 결과, 수동 제작 대기 목록, 장부 요약(`varco_client.py ledger`)의 실제 사용 추정 크레딧과 승인 예산 비교, 출시 판정(계약서 9절)에 걸리는 항목.

## 반환 형식(워크플로)

```json
{"id": "sfx_door", "verdict": "fail",
 "checks": [{"name": "audio/duration_s", "result": "fail", "detail": "10.0 (기준 0.2~3.0)"}],
 "issues": ["sfx_door_01.wav 뒤쪽 무음이 남아 10초"], "retryable": true,
 "fix_hint": "ffmpeg silenceremove 로 뒤쪽 무음을 자른다"}
```

`verdict` 는 `pass` | `fail` | `cannot_verify`. 검사 도구가 없거나 결과 파일을 찾을 수 없어 판단하지 못하면 `cannot_verify` 이고, 워크플로는 이것을 통과로 세지 않는다.

## 하지 말 것

- 에셋을 직접 고치지 않는다. 고칠 방법은 `fix_hint` 에 적고 제작 담당이 고친다. 검사하는 사람이 고치면 누가 무엇을 바꿨는지 기록이 흐려진다.
- 매니페스트를 고치지 않는다. 상태 갱신은 리더가 한다.
- 측정하지 않은 값을 통과로 적지 않는다. 도구가 실패했으면 그 검사는 `skip` 이나 `cannot_verify` 다.
