Mono to Stereo API는 평범한 모노 오디오를 분석하여, 깊이감과 공간감이 살아있는 스테레오 사운드로 확장합니다. 단순한 채널 복제가 아닌, AI 모델이 원본 사운드에 적합한 공간적 뉘앙스를 생성하여 청각적 몰입감을 극대화합니다.

샘플을 들어보세요:

<table>
<tr>
<td align="center">
<strong>모노</strong><br>
<audio controls src="https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/mono2stereo_mono.wav"></audio><br>
<!-- <img src="https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/mono2stereo_mono.png" width="90%"> -->
</td>
<td align="center">
<strong>스테레오</strong><br>
<audio controls src="https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/mono2stereo_stereo.wav"></audio><br>
<!-- <img src="https://github.com/nc-ai/openapi-varco-sound-examples/raw/refs/heads/main/resources/mono2stereo_stereo.png" width="90%"> -->
</td>
</tr>
</table>

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



<!-- ## 가격 정책

| 서비스 | 과금 단위 | 기본 단가 |
| :--- | :--- | :--- | :--- |
| Mono to Stereo | 호출당 | 50 크레딧 | -->
