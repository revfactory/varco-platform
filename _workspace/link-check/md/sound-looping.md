Looping API는 입력된 오디오를 분석하여, 끊김 없이 무한 반복 가능한 형태로 변환합니다. 번거로운 편집 작업 없이, 시작과 끝이 자연스럽게 연결되는 배경 사운드를 즉시 제작할 수 있습니다.

샘플을 들어보세요:

<table>
<tr>
<td align="center" width="50%">
<strong>원본 사운드</strong><br>
<audio controls src="https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/looping_original.wav"></audio><br>
</td>
</table>

<table>
<tr>
<td align="center" width="50%">
<strong>원본 사운드를 그대로 반복 재생한 경우</strong><br>
<audio controls src="https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/looping_before.wav"></audio><br>
<!-- <img src="resources/looping_before.png" width="90%"> -->
</td>

<td align="center" width="50%">
<strong>자동 루프로 편집된 사운드를 반복 재생한 경우</strong><br>
<audio controls src="https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/looping_after.wav"></audio><br>
<!-- <img src="resources/looping_after.png" width="90%"> -->
</td>
</tr>
</table>

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
| `preserve` | object | **begin, end**<br>(초 단위) | **구간 보존**<br>루프 생성 과정에서 절대 잘려나가면 안 되는 시간 대역을 지정합니다. 앰비언스 중간에 중요한 효과음(예: 특정 새소리)이 포함된 경우, 해당 구간을 건드리지 않고 보존합니다. |

* 개발에 필요한 상세 기술 명세는 [Looping API Reference](https://api.varco.ai/ko/reference/sound-looping)에서 확인하실 수 있습니다.

### 참고 사항
* **출력 길이 변화**   
  자동 루핑을 구현하는 원리상 결과물 오디오는 원본보다 길이가 짧아집니다. 이는 오류가 아니라 자연스러운 연결을 위한 정상적인 처리 과정입니다.

* **음악 및 보컬 비권장**   
  이 기능은 앰비언스와 노이즈성 텍스처 처리에 특화되어 있습니다. 박자가 있는 음악이나 기승전결이 뚜렷한 보컬 곡을 입력할 경우, 루프 지점에서 박자가 어긋나거나 부자연스러운 연결이 발생할 수 있습니다.

* **입력 소스 의존성**   
  AI는 원본의 톤을 최대한 유지하며 루핑 처리를 수행합니다. 원본 오디오 자체가 너무 짧거나 급격한 변화가 포함되어 있을 경우, 루프의 자연스러움이 다소 떨어질 수 있습니다.


<!-- ## 가격 정책

| 서비스 | 과금 단위 | 기본 단가 |
| :--- | :--- | :--- |
| Looping | 호출당 | 150 크레딧 | -->





