# VARCO Sound API
> 원문: api.varco.ai 문서(2026-09 수집). 가이드와 레퍼런스가 다르면 **레퍼런스를 기준으로 한다** (공식 안내: "엔드포인트 별 최신 버전은 항상 API Reference 페이지를 기준으로 확인").

## 목차 (절 이름 — 시작 줄)

- [가이드] sound-overview — 27줄
- [가이드] sound-texttosound — 108줄
- [가이드] sound-variation — 181줄
- [가이드] sound-looping — 265줄
- [가이드] sound-monotostereo — 343줄
- [가이드] sound-conversion — 405줄
- [가이드] sound-enhance — 474줄
- [레퍼런스] sound-text2sound — 541줄
- [레퍼런스] sound-variation — 585줄
- [레퍼런스] sound-looping — 640줄
- [레퍼런스] sound-mono2stereo — 687줄
- [레퍼런스] sound-conversion — 726줄
- [레퍼런스] sound-enhance — 772줄


---

# 제1부. 가이드

---

## [가이드] sound-overview

**AI로 가속화하는 오디오 워크플로우**

Sound API는 게임, 영상, 메타버스 등에 필요한 사운드 제작을 위한 **올인원 오디오 솔루션**입니다. 텍스트 프롬프트로 새로운 사운드를 창조하는 것부터, 기존 리소스를 프로덕션 품질로 최적화하는 과정까지. 파편화된 오디오 작업을 하나의 API 파이프라인으로 통합하세요.

## 핵심 가치

* **게임/영상 제작 최적화**  
    짧은 효과음(SFX)부터 긴 길이의 앰비언스까지, 프로덕션 레벨에서 즉시 사용할 수 있는 고품질 사운드를 제공합니다. 생성된 리소스는 별도의 후가공 없이 엔진에 바로 적용 가능한 수준의 퀄리티를 보장합니다.

* **사운드 작업 파이프라인 모듈화**  
    생성, 변환, 후처리의 모든 기능이 독립적인 API로 제공됩니다. 필요한 기능만 골라 기존 개발 환경(Unity, Unreal, Web)이나 자동화 툴에 유연하게 통합할 수 있습니다.

* **텍스트·오디오 기반 정밀 제어**  
    텍스트 프롬프트로 원하는 분위기를 묘사하거나, 레퍼런스 오디오로 스타일을 지정하여 기획자가 의도한 톤과 질감을 결과물에 정확하게 반영합니다.

## 제공 서비스

사운드 제작의 전 과정을 커버하는 6가지 핵심 모듈입니다.

### [Text to Sound](https://api.varco.ai/ko/docs/sound-texttosound)
**상상한 사운드를 텍스트로 실체화**
* 텍스트 프롬프트를 분석하여 고품질의 환경음(Ambience)과 효과음(SFX)을 생성합니다.
* **추천 용도:** 게임/영상 사운드 에셋, 저작권 없는 방송용 효과음, 아이디어 스케치

### [Variation](https://api.varco.ai/ko/docs/sound-variation)
**하나의 샘플로 만드는 무한한 다양성**
* 원본 사운드의 톤은 유지하되 파형이 미세하게 다른 변형 버전을 생성하여, 반복 재생 시의 청각적 피로를 줄입니다.
* **추천 용도:** 총소리/발자국 등 반복 효과음 확장, 에셋 라이브러리 구축

### [Mono to Stereo](https://api.varco.ai/ko/docs/sound-monotostereo)
**공간감과 깊이감의 확장**
* 평면적인 모노 오디오를 현장감이 살아있는 입체적인 스테레오 사운드로 확장합니다.
* **추천 용도:** 구형 리소스 업스케일링, 밋밋한 환경음 개선

### [Looping](https://api.varco.ai/ko/docs/sound-looping)
**편집 없이 완성하는 무한 배경음**
* 오디오의 시작과 끝을 AI가 정교하게 연결하여, 끊김 없이 무한 재생 가능한 루프 사운드로 변환합니다.
* **추천 용도:** 게임 배경음, 전시 공간 앰비언스, 명상 및 수면 사운드

### [Conversion](https://api.varco.ai/ko/docs/sound-conversion)
**캐릭터에 생명을 불어넣는 보이스 체인저**
* 사람의 목소리에 몬스터나 크리쳐의 질감을 입혀 압도적인 캐릭터 보이스로 변환합니다.
* **추천 용도:** 보스 몬스터, 크리쳐 사운드, NPC 대사

### [Enhance](https://api.varco.ai/ko/docs/sound-enhance)
**열악한 녹음본의 스튜디오급 복원**
* 배경 잡음은 제거하고 목소리는 선명하게 만들어, 녹음실에서 작업한 듯한 고품질 음성으로 정제합니다.
* **추천 용도:** 현장 인터뷰 복구, 홈 레코딩 품질 향상, 대사 오디오 클린업

## 워크플로우 예시

Sound API의 핵심 기능들을 활용하여, 반복적인 오디오 작업을 자동화하고 리소스 제작 효율을 극대화하는 실무 시나리오입니다.

**Scenario 1: 풍성한 SFX 라이브러리 구축**

단 하나의 샘플로 풍성한 사운드 라이브러리를 구축하고, 반복 재생의 지루함을 해결합니다.

* **소스 확보:** [Text to Sound](https://api.varco.ai/ko/docs/sound-texttosound)로 '레이저 발사음'을 생성하거나, 기존 파일 1개를 준비합니다.
* **배리에이션 생성:** [Variation](https://api.varco.ai/ko/docs/sound-variation)을 호출하여 톤은 유지하되 파형이 미세하게 다른 변형 파일들을 생성합니다.
* **랜덤 재생:** 게임 엔진에서 해당 사운드들을 랜덤하게 재생하여, 연사 시에도 자연스러운 디테일을 완성합니다.

**Scenario 2: 끊김 없는 몰입형 배경음 구현**

편집하기 까다로운 자연음이나 앰비언스를 완벽한 루프 사운드로 만듭니다.

* **리소스 생성:** [Text to Sound](https://api.varco.ai/ko/docs/sound-texttosound)를 통해 '비 내리는 숲'과 같은 환경음을 생성합니다.
* **스테레오 확장:** [Mono to Stereo](https://api.varco.ai/ko/docs/sound-monotostereo)를 적용하여 사운드의 공간감과 깊이를 확장합니다.
* **루프 완성:** [Looping](https://api.varco.ai/ko/docs/sound-looping)을 통해 시작과 끝이 자연스럽게 연결되도록 자동 처리하여, 무한히 지속되는 배경음을 완성합니다.

**Scenario 3: 손쉬운 몬스터 보이스 제작**

기획 단계의 가이드 녹음을 즉시 사용 가능한 인게임 리소스로 변환하여, 프로토타이핑 및 인디 게임 제작 효율을 높입니다.

* **가이드 녹음:** 스마트폰 등으로 대사 가이드를 녹음합니다. (Source)
* **스타일 변환:** [Conversion](https://api.varco.ai/ko/docs/sound-conversion)을 `enhance`파라미터와 함께 호출하여 녹음본의 배경 잡음을 제거하고 '오크'나 '악마'의 음색(Reference)을 입힙니다.
* **공간감 부여:** [Mono to Stereo](https://api.varco.ai/ko/docs/sound-monotostereo)를 통해 평면적인 목소리에 위압감 있는 공간감을 더해 최종 에셋을 완성합니다.

---

## [가이드] sound-texttosound

Text to Sound API는 텍스트 프롬프트를 분석하여 고품질의 환경음(Ambience)과 효과음(Foley/SFX)을 생성합니다. 아이디어 스케치부터 최종 프로덕션 단계까지, 영상 제작과 게임 개발 등 다양한 프로젝트에 필요한 사운드를 빠르게 확보할 수 있습니다.

## 주요 기능

단순한 키워드 입력부터 섬세한 상황 묘사까지, 크리에이터의 의도를 정확히 파악하여 사운드로 구현합니다.

* **고해상도 오디오 품질**
모든 결과물은 44.1kHz, 16bit의 표준 고해상도 포맷으로 생성되므로, 별도의 업스케일링이나 보정 작업 없이 상업용 영상 및 게임에 즉시 투입할 수 있습니다.

* **다국어 입력 지원**
언어의 장벽 없이 상상한 그대로 묘사할 수 있습니다. 한국어, 영어, 일본어 등 다양한 언어의 뉘앙스를 모델이 직접 이해하므로 별도의 번역 과정이 필요 없습니다.
  * **Example:** "타닥거리며 타오르는 장작불 소리"와 "Crackling campfire with popping embers" 모두 동일한 품질의 사운드를 생성합니다.  
    [샘플 오디오](https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/text2sound_campfire.wav)

* **지능형 맥락 이해**
복잡한 프롬프트 엔지니어링이 필요 없습니다. AI가 입력된 텍스트의 의도를 파악하여 최적의 사운드를 생성합니다.
  * **Simple**: "물 떨어지는 소리" 같은 단순 키워드만 입력해도 보편적이고 고품질인 소리를 생성합니다.  
    [샘플 오디오](https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/text2sound_water_simple.wav)
  * **Detailed**: "축축한 동굴 안에서 물방울이 떨어지며 울리는 소리"처럼 구체적으로 묘사하면, 해당 상황에 맞는 디테일한 사운드를 연출합니다.  
    [샘플 오디오](https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/text2sound_water_detailed.wav)

* **시네마틱 앰비언스 및 효과음**
영상의 공간감을 더하는 배경음부터, 오브젝트의 물리적 상호작용을 표현하는 효과음까지 폭넓게 커버합니다.
  * **Ambience:** 카페 소음, 숲속의 바람 소리, 우주선의 기계음 등 배경 사운드  
    [샘플 오디오](https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/text2sound_mysteryAmb.wav)  
  * **Foley/SFX:** 발자국 소리, 문 닫는 소리, 유리잔이 깨지는 소리 등 단발성 효과음  
    [샘플 오디오](https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/text2sound_dragon.wav)

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
| `num_samples` | integer | 1 \~ 3
(Default: 1) | **생성 개수 지정**
한 번의 호출로 최대 3개의 후보를 동시에 생성합니다. 같은 프롬프트라도 매번 다른 뉘앙스가 생성되므로, 최적의 결과를 고르기 위해 다수 생성을 권장합니다. |

* 개발에 필요한 상세 기술 명세는 [Text to Sound API Reference](https://api.varco.ai/ko/reference/sound-text2sound)에서 확인하실 수 있습니다.

### 참고 사항
* **음악 생성 관련**   
  이 API는 현실적인 질감과 환경음 구현에 특화된 모델입니다. 멜로디 라인이 있거나 기승전결이 있는 구조적인 음악 작곡에는 적합하지 않을 수 있습니다.

* **입력 길이**   
  모델은 문장이 길어질수록 서술된 모든 요소를 담으려 시도합니다. 미사여구가 많은 긴 문장보다는 표현하고자 하는 핵심 사운드와 분위기 위주로 작성하는 것이 효율적입니다.

---

## [가이드] sound-variation

Variation API는 입력된 오디오를 기반으로 원본의 톤과 질감은 유지하면서도 새롭게 생성된 변형 사운드를 제공합니다. 단 하나의 사운드만으로도 풍성한 Foley/SFX 라이브러리를 빠르게 확장할 수 있습니다.

아래 예시는 하나의 원본 사운드로부터 여러 변형 사운드를 생성하고, 실제 장면에 적용한 결과를 보여줍니다.

**원본 사운드**  
[샘플 오디오](https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/variation_original.wav)

**변형 사운드**  
[샘플 오디오](https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/variation_var1.wav)  
[샘플 오디오](https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/variation_var2.wav)  
[샘플 오디오](https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/variation_var3.wav)

**변형 사운드 적용 예시**  
[샘플 영상](https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/variation_video.mp4)

## 주요 기능

AI가 원본 사운드의 특징을 분석한 뒤, 유사한 느낌의 새로운 오디오를 생성합니다.

* **톤 & 질감 기반 변형**  
입력된 사운드의 음색과 질감을 AI가 분석하여 유지합니다. 원본과 함께 사용해도 이질감이 없으면서도, 표현이 다른 새로운 사운드를 만들어냅니다.

* **변형 강도 정밀 제어**  
`strength` 파라미터를 통해 원본 대비 변화의 폭을 조절할 수 있습니다. 미세한 뉘앙스만 바꾸거나, 원본의 느낌만 남기고 과감하게 새로운 표현으로 재창조하는 등 상황에 맞춰 유연하게 대응합니다.

* **구간 선택 변형**  
사운드 전체가 아닌 특정 구간만 변경할 수 있습니다. `include` 옵션으로 지정된 영역만 새롭게 생성되고, 나머지 부분은 원본 그대로 보존됩니다.

## 활용 사례

Variation API는 게임 및 실감형 콘텐츠 제작 시 필연적으로 발생하는 사운드 반복 재생의 단조로움을 해결하는 데 특화되어 있습니다.

* **오디오 에셋 확장**  
  발자국, 총소리, 타격음 등 빈번하게 반복 재생되는 Foley 사운드를 단조롭지 않게 만듭니다. 하나의 샘플로 수십 개의 자연스러운 변형 버전을 생성할 수 있습니다.

* **사운드 디자인 뉘앙스 조정**   
  "이 소리의 질감은 좋은데, 끝부분이 조금 달랐으면 좋겠다"는 상황에서, 원본을 바탕으로 미세하게 다른 여러 후보군을 빠르게 생성하여 최적의 결과물을 선택합니다.
  
* **기존 리소스 재활용**   
  이미 보유한 효과음을 프로젝트의 새로운 톤앤매너에 맞춰 변형하여, 새로운 녹음 없이도 리소스를 효율적으로 재활용합니다.

## 주요 사양 및 설정

API 사용 시 고려해야 할 입출력 사양과 모델의 기술적 특성입니다.

| 구분 | 사양 | 비고 |
| :--- | :--- | :--- |
| 입력 오디오 길이 | 0.5초 \~ 10초 | 너무 짧거나 긴 오디오는 지원하지 않음 |
| 출력 오디오 길이 | 10초 (고정) | 입력 길이에 관계없이 항상 10초로 생성됨 |
| 출력 오디오 채널 | Mono (1ch) | (유의) 스테레오 입력 시에도 모노로 변환되어 생성 |
| 출력 오디오 형식 | 44.1kHz, 16bit | 고해상도 WAV 파일 반환 |

### 파라미터 설정

변형의 범위와 강도를 세밀하게 조정할 수 있습니다.

| 파라미터 | 타입 | 범위 / 기본값 | 설명 |
| :--- | :--- | :--- | :--- |
| `strength` | number | **0.0 \~ 3.0**
(Default: 1.0) | **변형 강도 조절**
값이 높을수록 원본 오디오와의 차이가 커집니다. 원본의 느낌을 유지하려면 낮은 값을, 실험적인 결과를 원하면 높은 값을 설정하세요. |
| `include` | object | **begin, end**
(초 단위) | **구간 선택 변형**
사운드 내에서 변형하고 싶은 특정 구간의 시작(`begin`)과 끝(`end`) 시간을 지정합니다. 지정되지 않은 구간은 원본 그대로 유지됩니다. |
| `num_samples` | integer | **1 \~ 5**
(Default: 1) | **생성 개수 지정**
한 번의 요청으로 여러 후보를 생성해 선택할 수 있습니다. |

* 개발에 필요한 상세 기술 명세는 [Variation API Reference](https://api.varco.ai/ko/reference/sound-variation)에서 확인하실 수 있습니다.

### 참고 사항
* **출력 길이 및 공백**   
  생성된 오디오는 항상 10초 길이입니다. 만약 입력된 원본 오디오가 10초보다 짧을 경우, 사운드가 재생된 후 나머지 시간은 무음이나 잔향으로 채워질 수 있습니다. 필요에 따라 후편집(Trimming)이 권장됩니다.
  
* **음악 및 음성 변형 불가**   
  이 기능은 효과음(SFX/Foley)과 환경음(Ambience)의 텍스처 변형에 특화되어 있습니다. 구조적인 음악, 멜로디가 뚜렷한 악기 연주, 인간의 목소리 등은 변형 시 품질을 보장하지 않거나 의도치 않게 뭉개질 수 있습니다.

* **구간 선택 변형 활용**   
  `include` 옵션은 사운드의 특정 부분에 튀는 잡음이 있거나, 마음에 들지 않는 구간만 콕 집어 수정하고 싶을 때 유용하게 사용됩니다.

---

## [가이드] sound-looping

Looping API는 입력된 오디오를 분석하여, 끊김 없이 무한 반복 가능한 형태로 변환합니다. 번거로운 편집 작업 없이, 시작과 끝이 자연스럽게 연결되는 배경 사운드를 즉시 제작할 수 있습니다.

샘플을 들어보세요:

**원본 사운드**

[샘플 오디오](https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/looping_original.wav)

**원본 사운드를 그대로 반복 재생한 경우**

[샘플 오디오](https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/looping_before.wav)

**자동 루프로 편집된 사운드를 반복 재생한 경우**

[샘플 오디오](https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/looping_after.wav)

## 주요 기능

자연스러운 반복 재생을 위해 필요한 오디오 편집 및 최적화 작업을 AI가 자동으로 수행합니다.

* **끊김 없는 루프 자동 완성**  
오디오 파일의 시작 부분과 끝부분을 정교하게 분석하고 연결하여, 반복 재생 시 튀는 소리(Pop/Click)나 끊기는 느낌이 전혀 없는 완벽한 루프를 생성합니다.

* **앰비언스 및 환경음 최적화**  
바람 소리, 빗소리, 엔진 소음 등 지속적인 텍스처를 가진 사운드에 최적화되어 있습니다. 불규칙한 파형을 가진 자연음도 이질감 없이 자연스럽게 이어지도록 조정합니다.

* **편집 프로세스 자동화**  
DAW(Digital Audio Workstation)에서 일일이 파형을 자르고 붙이는 수고를 덜어줍니다. 원본 파일을 업로드하는 것만으로 게임 엔진이나 미디어 플레이어에서 즉시 반복 재생 가능한 에셋을 확보할 수 있습니다.

## 활용 사례

장시간 재생이 필요한 콘텐츠의 배경 사운드 제작에 효과적입니다.

* **게임 및 메타버스 배경음**  
숲, 도시, 우주선 내부 등 플레이어가 장시간 머무르는 공간의 환경음을 제작할 때, 짧은 샘플 하나로 무한히 지속되는 배경을 구축합니다.

* **전시 및 설치 미디어**   
미술관이나 팝업 스토어의 공간 연출을 위해, 특정 분위기의 사운드를 하루 종일 끊김 없이 재생해야 하는 상황에 활용합니다.

* **영상 씬 분위기 유지**   
특정 장면이 길어지거나 반복될 때,배경음이 튀지 않고 자연스럽게 유지되도록 합니다.

## 주요 사양 및 설정

API 사용 시 고려해야 할 입출력 사양과 모델의 기술적 특성입니다.

| 구분 | 사양 | 비고 |
| :--- | :--- | :--- |
| 입력 오디오 길이 | 1초~60분 | 너무 짧은 오디오는 루프 포인트 탐색이 어려움 |
| 출력 오디오 길이 | 입력보다 다소 짧아짐 | 최적의 루프 포인트 탐색 및 트리밍(Trimming) 발생 |
| 출력 오디오 형식 | 44.1kHz, 16bit | 고해상도 WAV 파일 반환 |

### 파라미터 설정

특정 구간을 보호해야 할 경우 옵션 파라미터를 사용할 수 있습니다.

| 파라미터 | 타입 | 구조 | 설명 |
| :--- | :--- | :--- | :--- |
| `preserve` | object | **begin, end**
(초 단위) | **구간 보존**
루프 생성 과정에서 절대 잘려나가면 안 되는 시간 대역을 지정합니다. 앰비언스 중간에 중요한 효과음(예: 특정 새소리)이 포함된 경우, 해당 구간을 건드리지 않고 보존합니다. |

* 개발에 필요한 상세 기술 명세는 [Looping API Reference](https://api.varco.ai/ko/reference/sound-looping)에서 확인하실 수 있습니다.

### 참고 사항
* **출력 길이 변화**   
  자동 루핑을 구현하는 원리상 결과물 오디오는 원본보다 길이가 짧아집니다. 이는 오류가 아니라 자연스러운 연결을 위한 정상적인 처리 과정입니다.

* **음악 및 보컬 비권장**   
  이 기능은 앰비언스와 노이즈성 텍스처 처리에 특화되어 있습니다. 박자가 있는 음악이나 기승전결이 뚜렷한 보컬 곡을 입력할 경우, 루프 지점에서 박자가 어긋나거나 부자연스러운 연결이 발생할 수 있습니다.

* **입력 소스 의존성**   
  AI는 원본의 톤을 최대한 유지하며 루핑 처리를 수행합니다. 원본 오디오 자체가 너무 짧거나 급격한 변화가 포함되어 있을 경우, 루프의 자연스러움이 다소 떨어질 수 있습니다.

---

## [가이드] sound-monotostereo

Mono to Stereo API는 평범한 모노 오디오를 분석하여, 깊이감과 공간감이 살아있는 스테레오 사운드로 확장합니다. 단순한 채널 복제가 아닌, AI 모델이 원본 사운드에 적합한 공간적 뉘앙스를 생성하여 청각적 몰입감을 극대화합니다.

샘플을 들어보세요:

**모노**

[샘플 오디오](https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/mono2stereo_mono.wav)

**스테레오**

[샘플 오디오](https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/mono2stereo_stereo.wav)

## 주요 기능

빈약한 모노 사운드를 현대적인 콘텐츠 품질에 맞는 풍성한 스테레오 사운드로 변환합니다.

* **AI 기반 입체감 형성**  
단일 채널의 평면적인 사운드를 분석하여 좌우 공간감이 느껴지는 입체적인 이미지로 재구성합니다. 청취자에게 소리가 중앙에만 뭉쳐 들리지 않고, 실제 공간에서 들리는 듯한 자연스러운 확산감을 제공합니다.

* **Foley 및 환경음 최적화**  
발자국 소리, 옷깃 스치는 소리, 충돌음, 그리고 다양한 앰비언스 처리에 특화되어 있습니다. 질감이 중요한 효과음에서 인위적인 느낌 없이 공간감을 향상시킵니다.

* **간편한 자동화**  
복잡한 파라미터 설정이 필요 없습니다. 파일을 업로드하기만 하면 AI가 사운드의 특성을 파악하고 가장 적합한 스테레오 사운드를 자동으로 생성합니다.

## 활용 사례

오래된 리소스의 품질을 높이거나, 밋밋한 효과음에 생동감을 불어넣는 데 활용됩니다.

* **게임 내 몰입감 강화**  
  플레이어 캐릭터 주변의 환경음이나 상호작용 사운드가 너무 정적으로 들릴 때, 공간감을 부여하여 게임의 현장감을 높입니다.

* **단조로움 해결**   
  밋밋하게 들리는 단일 모노 SFX를 더 풍부하고 꽉 찬 사운드로 변환하여 영상이나 게임 씬의 빈 공간을 청각적으로 채워줍니다.

* **기존 자산 업스케일링**   
  과거에 모노로 녹음되어 현재 프로젝트에 쓰기엔 품질이 아쉬운 구작 게임이나 영상의 사운드 라이브러리를 스테레오 포맷으로 업그레이드합니다.

## 주요 사양 및 설정

API 사용 시 고려해야 할 입출력 사양과 모델의 기술적 특성입니다.

| 구분 | 사양 | 비고 |
| :--- | :--- | :--- |
| 입력 오디오 길이 | 0.5초 \~ 10초 | 최대 10초의 사운드 처리 가능 |
| 출력 오디오 채널 | Stereo (2ch) | 항상 2채널로 변환되어 반환 |
| 출력 오디오 형식 | 44.1kHz, 16bit | 고해상도 WAV 파일 반환 |

* 개발에 필요한 상세 기술 명세는 [Mono to Stereo API Reference](https://api.varco.ai/ko/reference/sound-mono2stereo)에서 확인하실 수 있습니다.

### 참고 사항

* **생성 원리**   
  이 기능은 신호 처리(DSP) 방식이 아닌 생성형 AI 모델을 기반으로 동작합니다. 입력된 사운드를 바탕으로 공간감을 포함한 오디오를 새로 생성하므로 원본과 미세하게 다른 질감이 더해질 수 있습니다.

* **음악 및 멜로디 비권장**   
  구조적인 음악이나 멜로디가 뚜렷한 악기 소리에 적용할 경우, 위상(Phase) 문제가 발생하거나 음색이 왜곡될 수 있어 권장하지 않습니다. 효과음과 앰비언스 용도로 최적화되어 있습니다.

---

## [가이드] sound-conversion

Conversion API는 평범한 목소리에 괴물의 숨결을 불어넣는 기능입니다. 사람의 목소리를 다른 사람으로 바꾸는 일반적인 음성 변환(Voice Conversion)과 달리, 이 기술은 인간의 성대 구조를 뛰어넘는 비인간(Non-human) 캐릭터의 질감과 압도적인 분위기를 구현하는 데 특화되어 있습니다.

**몬스터 음색 변환 예시**  
[샘플 영상](https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/conversion_video.mp4)

## 주요 기능

단순한 이펙터나 필터링으로는 구현하기 힘든 고품질의 몬스터 보이스를 생성합니다.

* **샘플 하나로 끝내는 몬스터 음색**  
복잡한 데이터셋도, 긴 학습 시간도 필요 없습니다. 10초 내외의 짧은 오디오만 넣어주세요. AI가 레퍼런스의 특징을 추출하여, 당신의 목소리를 즉시 타겟 캐릭터로 변환합니다.

* **몬스터 질감 합성**  
그로울링, 금속음 등 참조 오디오의 고유한 질감을 원본 목소리의 억양과 연기에 자연스럽게 덧입힙니다.

* **정밀한 변환 제어**  
원본 소스의 특성을 유지할지, 몬스터의 색깔을 강하게 입힐지 선택할 수 있습니다. `ratio` 파라미터를 통해 원본의 음색과 참조 오디오의 스타일 사이의 균형을 자유롭게 조절하세요.

## 활용 사례

전문적인 성우나 복잡한 사운드 디자인 과정 없이도, 리얼하고 다채로운 몬스터 보이스를 확보할 수 있습니다.

* **자체 녹음으로 완성하는 캐릭터 목소리**   
  인디 게임 개발이나 프로토타이핑 단계에서, 개발자가 직접 녹음한 가이드 음성을 즉시 인게임에 적용 가능한 고퀄리티 몬스터 대사로 변환하여 리소스 제작 효율을 높입니다.
  
* **단일 소스로 만드는 수천 마리의 몬스터 (1 Source → Multi Targets)**   
  한 번 녹음한 대사 파일(`source`)에 다양한 몬스터 샘플(`reference`)을 적용해 보세요. 오크, 고블린, 악마 등 서로 다른 종족의 목소리를 한 번에 생성하여 NPC 대사를 대량으로 확보할 수 있습니다.

* **캐릭터 표현의 확장 (1 Target → Multi Sources)**   
  공들여 디자인한 몬스터 울음소리 파일(`reference`) 하나만 있다면, 이를 여러 대사(`source`)에 적용하여 해당 캐릭터의 아이덴티티를 유지한 채 공격, 피격, 사망 등 다양한 상황의 음성을 일관성 있게 제작할 수 있습니다.

## 주요 사양 및 설정

API 사용 시 고려해야 할 입출력 사양과 모델의 기술적 특성입니다.

API는 변환할 소스 오디오(`source`)와 입히고 싶은 몬스터 스타일(`reference`), 두 개의 오디오 입력을 기반으로 동작합니다.

| 구분 | 사양 | 비고 |
| :--- | :--- | :--- |
| 입력 오디오 길이 | 0.5초 \~ 10초 | Source와 Reference 오디오 모두 해당 범위 내 |
| 출력 오디오 길이 | Source와 동일 | 원본의 발화 속도와 길이를 그대로 유지 |
| 출력 오디오 형식 | 44.1kHz, 16bit | 고해상도 WAV 파일 반환 |

### 파라미터 설정

원하는 결과물의 뉘앙스를 만들기 위해 변환 강도와 소스 오디오 전처리 옵션을 조절할 수 있습니다.

| 파라미터 | 타입 | 범위 / 기본값 | 설명 |
| :--- | :--- | :--- | :--- |
| `ratio` | float | 0.0 \~ 2.0
(Default: 1.0) | **변환 강도 조절**
값이 0에 가까울수록 원본의 고유 음색이 많이 남고, 커질수록 참조 몬스터의 스타일이 강하게 입혀집니다. |
| `enhance` | boolean | true / false
(Default: false) | **소스 노이즈 제거**
Source 오디오에 잡음이 많을 경우 `true`로 설정하세요. 내부적으로 [Enhance API](https://api.varco.ai/ko/reference/sound-enhance)를 거쳐 깨끗한 상태로 변환을 수행합니다. |

* 개발에 필요한 상세 기술 명세는 [Conversion API Reference](https://api.varco.ai/ko/reference/sound-conversion)에서 확인하실 수 있습니다.
### 참고 사항

* **비선율적 발성 및 텍스처 특화**   
  이 모델은 대사(Speech)나 비발화(Non-verbal, 신음/포효 등) 사운드의 표현에 최적화되어 있습니다. 정확한 음정이 중요한 노래나 멜로디를 소스 오디오로 입력할 경우, 음가가 불안정해지거나 몬스터 특유의 텍스처로 인해 멜로디 라인이 뭉개질 수 있습니다.
  
* **참조 오디오 선정 팁**   
  레퍼런스 오디오는 변환의 '기준'이 됩니다. 배경음이 섞이지 않고, 캐릭터의 음색 특징이 뚜렷하게 드러나는 깨끗한 샘플을 사용할수록 훨씬 높은 품질의 결과물을 얻을 수 있습니다.

---

## [가이드] sound-enhance

Enhance API는 녹음 환경이 좋지 않거나 노이즈가 섞인 음성 파일을 분석하여, 배경 잡음은 제거하고 목소리의 명료도는 획기적으로 높여주는 음성 전용 품질 향상(Speech Enhancement) 기능입니다. 열악한 환경에서 녹음된 오디오도 스튜디오에서 녹음한 듯한 선명한 사운드로 복원합니다.

샘플을 들어보세요:

**noisy**

[샘플 오디오](https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/enhance_noisy.wav)

**clean**

[샘플 오디오](https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/enhance_clean.wav)

## 주요 기능

전문적인 오디오 엔지니어링 지식 없이도, 클릭 한 번으로 잡음 제거와 음성 강화 효과를 얻을 수 있습니다.

* **강력한 배경 소음 제거**  
에어컨 소리, 거리의 소음, 마이크의 화이트 노이즈 등 음성을 방해하는 배경 잡음을 AI가 식별하여 제거합니다. 목소리의 주파수 대역은 보존하면서 불필요한 환경음만 걷어내어 깨끗한 무음 배경을 만듭니다.

* **목소리 명료도 및 전달력 강화**  
울림(Reverb)이 심한 실내에서 녹음되었거나, 마이크 거리가 멀어 흐릿하게 들리는 목소리를 또렷하게 보정합니다. 발화의 뉘앙스를 해치지 않는 선에서 목소리를 배경과 분리하여 전달력을 높입니다W.

* **음성 최적화 엔진**  
인터뷰, 내레이션, 게임 대사 등 사람의 말소리 처리에 특화되어 있습니다. 다양한 화자의 톤과 언어를 학습한 모델이 적용되어, 남녀노소 구분 없이 자연스러운 정제 결과를 제공합니다.

## 활용 사례

재녹음이 불가능하거나 후처리 시간이 부족한 프로젝트에서 강력한 효율을 발휘합니다.

* **현장 녹음 복구**   
  야외나 소음이 심한 행사장에서 진행된 인터뷰, 브이로그 영상의 음성을 스튜디오 품질급으로 정제하여 콘텐츠의 몰입도를 높입니다.

* **홈 레코딩 품질 향상**   
  전문 방음 시설이 없는 집이나 사무실에서 녹음된 팟캐스트, 게임 보이스 오버 자료의 룸톤(Room Tone)과 반사음을 제거합니다.
  
* **오디오 자산 표준화**   
  서로 다른 환경에서 녹음되어 톤이 제각각인 여러 성우의 음성 파일들을 일관된 품질로 톤 앤 매너를 맞춥니다.

## 주요 사양 및 설정

API 사용 시 고려해야 할 입출력 사양과 모델의 기술적 특성입니다.

| 구분 | 사양 | 비고 |
| :--- | :--- | :--- |
| 출력 오디오 포맷 | 44.1kHz, 16bit | 노이즈 제거 후 변환된 포맷으로 반환 |

* 개발에 필요한 상세 기술 명세는 [Enhance API Reference](https://api.varco.ai/ko/reference/sound-enhance)에서 확인하실 수 있습니다.

### 참고 사항

* **음성 전용**   
  이 기능은 사람의 목소리를 분리하고 강화하는 데 최적화되어 있습니다. 음악, 악기 연주, 자연의 소리(새소리, 물소리 등)에 적용할 경우, AI가 이를 잡음으로 인식하여 소리를 깎아내거나 왜곡시킬 수 있으므로 권장하지 않습니다.

* **물리적 손상 복구 한계**   
  배경 소음이나 잔향은 훌륭하게 제거하지만, 오디오 자체가 찢어지게 녹음된 클리핑이나 데이터 유실로 인한 심각한 디지털 왜곡까지 완벽하게 복구하는 것은 불가능합니다.
  
* **길이 제한**   
  지원하는 최대 오디오 길이는 시스템 상황에 따라 달라질 수 있습니다. 자세한 스펙은 Reference 문서를 참고해 주세요.

---

# 제2부. API 레퍼런스

---

## [레퍼런스] sound-text2sound

**POST** `/sound/varco/v1/api/text2sound`

### Description
텍스트 프롬프트를 기반으로 AI가 사운드 이펙트를 생성합니다.

동시에 생성되는 샘플 수(1~3)를 조정 할 수 있습니다.

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters application/json

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `version` | string | Version of generation model | `v1` | [`v1`, `v2`] | No |
| `prompt` | string | The text prompt to generate sound from. | - | - | Yes |
| `num_sample` | integer | Number of samples to generate. | `1` | `>= 1` and `<= 3` | No |

### Responses

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `400` | Bad Request |
| `422` | Validation Error |
| `500` | Internal Server Error |

#### Example - Response 200 application/json

```json
[
  {
    "audio": "string"
  }
]
```

---

## [레퍼런스] sound-variation

**POST** `/sound/varco/v1/api/variation`

### Description
입력된 오디오 파일을 기반으로 다양한 변형 버전의 사운드를 생성합니다.

원본의 특징을 유지하면서 새로운 변화를 추가할 수 있습니다.

생성 단계 수(10~50), 샘플 수(1~5개), 변화강도(0.0~3.0) 등을 조정할 수 있습니다.

source는 오디오 파일의 base64 인코딩 문자열입니다.
strength의 값이 클수록 큰 변화를 줍니다.

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters application/json

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `source` | string | Base64 encoded reference sound to create variations from. | - | - | Yes |
| `num_sample` | integer | Number of samples to generate variations for. | `1` | `>= 1` and `<= 5` | No |
| `strength` | number | Strength of the variation effect. | `1` | `>= 0` and `<= 3` | No |
| `include` | object | 변환할 영역을 지정합니다. | - | - | No |

##### Body Parameters - include

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `begin` | number | 영역의 시작 시간 (초 단위). | `0` | - | No |
| `end` | number | 영역의 끝 시간 (초 단위). | `0` | - | No |

### Responses

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `422` | Validation Error |

#### Example - Response 200 application/json

```json
[
  {
    "audio": "string"
  }
]
```

---

## [레퍼런스] sound-looping

**POST** `/sound/varco/v1/api/looping`

### Description
입력된 오디오 파일을 매끄럽게 연결하여 무한 반복 재생이 가능하도록 처리합니다.

시작과 끝이 자연스럽게 연결되어 끊김 없는 루프를 생성합니다.
source는 오디오 파일의 base64 인코딩 문자열입니다.

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters application/json

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `source` | string | Base64 encoded sound to loop. | - | - | Yes |
| `preserve` | object | 보존할 영역을 지정합니다. | - | - | No |

##### Body Parameters - preserve

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `begin` | number | 영역의 시작 시간 (초 단위). | `0` | - | No |
| `end` | number | 영역의 끝 시간 (초 단위). | `0` | - | No |

### Responses

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `422` | Validation Error |

#### Example - Response 200 application/json

```json
{
  "audio": "string"
}
```

---

## [레퍼런스] sound-mono2stereo

**POST** `/sound/varco/v1/api/mono2stereo`

### Description
단일 채널 모노 오디오를 양쪽 채널을 가진 스테레오 오디오로 변환합니다.

AI를 사용하여 자연스러운 스테레오 효과를 생성합니다.
source는 오디오 파일의 base64 인코딩 문자열입니다.

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters application/json

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `source` | string | Base64 encoded mono sound to convert to stereo. | - | - | Yes |

### Responses

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `422` | Validation Error |

#### Example - Response 200 application/json

```json
{
  "audio": "string"
}
```

---

## [레퍼런스] sound-conversion

**POST** `/sound/varco/v1/api/conversion`

### Description
소스 오디오를 참조 오디오의 스타일로 변환합니다. 

음성이나 사운드의 특성을 다른 스타일로 변경할 수 있습니다.

변환 비율(0.0~2.0) 등을 조정할 수 있습니다.

ratio의 값이 클수록(1.2 이상) 참조 오디오의 음색과 멀어질 수 있습니다.
source와 reference는 오디오 파일의 base64 인코딩 문자열입니다.

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters application/json

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `source` | string | Base64 encoded source sound. | - | - | Yes |
| `reference` | string | Base64 encoded reference sound. | - | - | Yes |
| `ratio` | number | Conversion Ratio | `1` | `>= 0` and `<= 2` | No |
| `enhance` | boolean | Whether to enhance source sound. | `False` | - | No |

### Responses

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `422` | Validation Error |

#### Example - Response 200 application/json

```json
{
  "audio": "string"
}
```

---

## [레퍼런스] sound-enhance

**POST** `/sound/varco/v1/api/enhance`

### Description
입력된 오디오에서 노이즈를 제거합니다.

source는 오디오 파일의 base64 인코딩 문자열입니다.

노이즈 제거후 44100Hz 16Bit Wav 파일을 base64로 변환하여 반환합니다.

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters application/json

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `source` | string | Base64 encoded source sound. | - | - | Yes |

### Responses

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `422` | Validation Error |

#### Example - Response 200 application/json

```json
{
  "audio": "string"
}
```
