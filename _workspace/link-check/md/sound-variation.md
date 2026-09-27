Variation API는 입력된 오디오를 기반으로 원본의 톤과 질감은 유지하면서도 새롭게 생성된 변형 사운드를 제공합니다. 단 하나의 사운드만으로도 풍성한 Foley/SFX 라이브러리를 빠르게 확장할 수 있습니다.

아래 예시는 하나의 원본 사운드로부터 여러 변형 사운드를 생성하고, 실제 장면에 적용한 결과를 보여줍니다.

**원본 사운드**  
<audio controls="" src="https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/variation_original.wav"></audio>

**변형 사운드**  
<audio controls="" src="https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/variation_var1.wav"></audio>  
<audio controls="" src="https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/variation_var2.wav"></audio>  
<audio controls="" src="https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/variation_var3.wav"></audio>

**변형 사운드 적용 예시**  
<video controls="" src="https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/variation_video.mp4" width="560" height="315"></video>

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
| `strength` | number | **0.0 \~ 3.0**<br>(Default: 1.0) | **변형 강도 조절**<br>값이 높을수록 원본 오디오와의 차이가 커집니다. 원본의 느낌을 유지하려면 낮은 값을, 실험적인 결과를 원하면 높은 값을 설정하세요. |
| `include` | object | **begin, end**<br>(초 단위) | **구간 선택 변형**<br>사운드 내에서 변형하고 싶은 특정 구간의 시작(`begin`)과 끝(`end`) 시간을 지정합니다. 지정되지 않은 구간은 원본 그대로 유지됩니다. |
| `num_samples` | integer | **1 \~ 5**<br>(Default: 1) | **생성 개수 지정**<br>한 번의 요청으로 여러 후보를 생성해 선택할 수 있습니다. |

* 개발에 필요한 상세 기술 명세는 [Variation API Reference](https://api.varco.ai/ko/reference/sound-variation)에서 확인하실 수 있습니다.

### 참고 사항
* **출력 길이 및 공백**   
  생성된 오디오는 항상 10초 길이입니다. 만약 입력된 원본 오디오가 10초보다 짧을 경우, 사운드가 재생된 후 나머지 시간은 무음이나 잔향으로 채워질 수 있습니다. 필요에 따라 후편집(Trimming)이 권장됩니다.
  
* **음악 및 음성 변형 불가**   
  이 기능은 효과음(SFX/Foley)과 환경음(Ambience)의 텍스처 변형에 특화되어 있습니다. 구조적인 음악, 멜로디가 뚜렷한 악기 연주, 인간의 목소리 등은 변형 시 품질을 보장하지 않거나 의도치 않게 뭉개질 수 있습니다.

* **구간 선택 변형 활용**   
  `include` 옵션은 사운드의 특정 부분에 튀는 잡음이 있거나, 마음에 들지 않는 구간만 콕 집어 수정하고 싶을 때 유용하게 사용됩니다.


<!-- ## 가격 정책

| 서비스 | 과금 단위 | 기본 단가 |
| :--- | :--- | :--- 
| Variation | 호출당 | 50 크레딧 | -->


