# 에셋 전수 감사 — demo

- 판정: **fail** (모드 live, 엔진 web)

| 검사 | 결과 | 내용 |
| --- | --- | --- |
| code_scanned | pass | web: 코드 파일 1개, 정적 참조 6, 동적 접두사 1 |
| code_refs_exist | fail | 깨진 참조 4 |
| p0_files_exist | fail | P0 누락 2 |
| status_consistent | fail | 불일치 2 |
| all_files_exist | fail | P1·P2 누락 1 |
| unused_files | pass | 미사용 1 |

## 문제와 정보

- 코드가 가리키는데 없는 파일: assets/audio/sfx/sfx_door_03.wav ← web/src/audio.js:2; assets/audio/voice/korean/${lineId}.wav ← web/src/audio.js:3; assets/audio/music/bgm_title.wav ← web/src/audio.js:4; assets/models/mdl_crate.glb ← web/src/audio.js:5
- P0 결과 누락: ["sfx_door: ['assets/audio/sfx/sfx_door_03.wav']", "vo_ch1_intro: ['assets/audio/voice/korean/ch1_intro_002.wav', 'assets/anim/face/ch1_intro_001.json', 'assets/anim/face/ch1_intro_002.json']"]
- 상태 불일치: ['sfx_door status=qa_passed 인데 파일 2/3', 'vo_ch1_intro status=qa_passed 인데 파일 1/4']
- P1·P2 결과 누락: ["mdl_crate: ['assets/models/mdl_crate.glb']"]
- 정보: 코드에서 쓰지 않는 에셋 1개: ['assets/images/img_orphan.png']
- 정보: 매니페스트에 없는 파일 1개(후보·중간 파일?): ['assets/images/img_orphan.png']

고칠 방향: 파일을 만들거나 코드 경로를 매니페스트 output 규칙에 맞춘다(자리표시 대체가 있는지도 확인) / 해당 에셋만 3단계를 다시 돌린다 / 리더가 매니페스트 status 를 실제에 맞게 고친다 / 출시 판정에서 디렉터가 허용 여부를 정한다
