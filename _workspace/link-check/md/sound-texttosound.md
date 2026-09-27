Text to Sound API는 텍스트 프롬프트를 분석하여 고품질의 환경음(Ambience)과 효과음(Foley/SFX)을 생성합니다. 아이디어 스케치부터 최종 프로덕션 단계까지, 영상 제작과 게임 개발 등 다양한 프로젝트에 필요한 사운드를 빠르게 확보할 수 있습니다.


## 주요 기능

단순한 키워드 입력부터 섬세한 상황 묘사까지, 크리에이터의 의도를 정확히 파악하여 사운드로 구현합니다.

* **고해상도 오디오 품질**
모든 결과물은 44.1kHz, 16bit의 표준 고해상도 포맷으로 생성되므로, 별도의 업스케일링이나 보정 작업 없이 상업용 영상 및 게임에 즉시 투입할 수 있습니다.

* **다국어 입력 지원**
언어의 장벽 없이 상상한 그대로 묘사할 수 있습니다. 한국어, 영어, 일본어 등 다양한 언어의 뉘앙스를 모델이 직접 이해하므로 별도의 번역 과정이 필요 없습니다.
  * **Example:** "타닥거리며 타오르는 장작불 소리"와 "Crackling campfire with popping embers" 모두 동일한 품질의 사운드를 생성합니다.  
    <audio controls="" src="https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/text2sound_campfire.wav"></audio>

* **지능형 맥락 이해**
복잡한 프롬프트 엔지니어링이 필요 없습니다. AI가 입력된 텍스트의 의도를 파악하여 최적의 사운드를 생성합니다.
  * **Simple**: "물 떨어지는 소리" 같은 단순 키워드만 입력해도 보편적이고 고품질인 소리를 생성합니다.  
    <audio controls="" src="https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/text2sound_water_simple.wav"></audio>
  * **Detailed**: "축축한 동굴 안에서 물방울이 떨어지며 울리는 소리"처럼 구체적으로 묘사하면, 해당 상황에 맞는 디테일한 사운드를 연출합니다.  
    <audio controls="" src="https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/text2sound_water_detailed.wav"></audio>

* **시네마틱 앰비언스 및 효과음**
영상의 공간감을 더하는 배경음부터, 오브젝트의 물리적 상호작용을 표현하는 효과음까지 폭넓게 커버합니다.
  * **Ambience:** 카페 소음, 숲속의 바람 소리, 우주선의 기계음 등 배경 사운드  
    <audio controls="" src="https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/text2sound_mysteryAmb.wav"></audio>  
  * **Foley/SFX:** 발자국 소리, 문 닫는 소리, 유리잔이 깨지는 소리 등 단발성 효과음  
    <audio controls="" src="https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/text2sound_dragon.wav"></audio>

## 활용 사례
Text to Sound API는 기획, 개발, 디자인 등 다양한 파이프라인에서 효율적인 리소스 확보 도구로 활용됩니다.

* **게임 사운드 에셋 제작**   
  인디 게임 및 캐주얼 프로젝트의 사운드 리소스로 활용하거나, 대규모 개발 과정에서 기획 의도를 시각화하는 고품질 플레이스홀더로 활용하여 개발 효율을 높입니다.

* **사운드 디자인 소스 확보**   
  기존 라이브러리에 없는 독창적인 질감이 필요할 때, AI로 기본 소스를 생성한 후 DAW에서 레이어링하여 복합적인 고퀄리티 SFX를 제작합니다.

* **영상 콘텐츠 제작**   
  스톡 오디오 사이트를 검색하는 시간 없이, 영상 씬에 정확히 부합하는 앰비언스를 즉시 생성하여 편집 효율을 높입니다.

## 주요 사양 및 설정

API 사용 시 고려해야 할 입출력 사양과 모델의 기술적 특성입니다.

| 구분 | 사양 | 비고 |
| :--- | :--- | :--- |
| 입력 텍스트 제한 | 최대 200자 | 핵심 사운드와 분위기 위주의 묘사 권장 |
| 출력 오디오 길이 | 10초 | 모든 결과물은 10초 길이로 생성 |
| 출력 오디오 형식 | 44.1kHz, 16bit | 고해상도 WAV 파일 반환 |

### 파라미터 설정

결과물의 개수를 조정하여 선택의 폭을 넓힐 수 있습니다.

| 파라미터 | 타입 | 범위 / 기본값 | 설명 |
| :--- | :--- | :--- | :--- |
| `num_samples` | integer | 1 \~ 3<br>(Default: 1) | **생성 개수 지정**<br>한 번의 호출로 최대 3개의 후보를 동시에 생성합니다. 같은 프롬프트라도 매번 다른 뉘앙스가 생성되므로, 최적의 결과를 고르기 위해 다수 생성을 권장합니다. |

* 개발에 필요한 상세 기술 명세는 [Text to Sound API Reference](https://api.varco.ai/ko/reference/sound-text2sound)에서 확인하실 수 있습니다.

### 참고 사항
* **음악 생성 관련**   
  이 API는 현실적인 질감과 환경음 구현에 특화된 모델입니다. 멜로디 라인이 있거나 기승전결이 있는 구조적인 음악 작곡에는 적합하지 않을 수 있습니다.

* **입력 길이**   
  모델은 문장이 길어질수록 서술된 모든 요소를 담으려 시도합니다. 미사여구가 많은 긴 문장보다는 표현하고자 하는 핵심 사운드와 분위기 위주로 작성하는 것이 효율적입니다.


<!-- ## 가격 정책

| 서비스 | 과금 단위 | 기본 단가 |
| :--- | :--- | :--- |
| Text to Sound | 호출당 | 25 크레딧 | -->




