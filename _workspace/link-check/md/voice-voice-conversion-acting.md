
Voice Conversion Acting (VC Acting)은 **다이내믹한 감정선과 극적인 표현력이 요구되는 연기체 음성의 성능 향상에 특화된 생성형 음성 변환 모델**입니다. 입력 음성의 내용·리듬·스타일은 유지하면서, 특히 연기체 발화에 담긴 감정선과 표현력을 더 잘 살려 원하는 다른 화자의 목소리로 자연스럽게 변환할 수 있습니다.

감정 기복이 큰 대사, 캐릭터 중심 콘텐츠, 더빙, 오디오 드라마, 게임 컷신, 숏폼 광고 등 **표현력 있는 목소리 연출이 중요한 미디어 환경**에서 특히 효과적으로 활용할 수 있습니다. 원본 발화의 흐름은 살리면서도, 입력 음성에 담긴 감정 표현과 연기 톤을 더 충실하게 보존해 보다 생동감 있는 음성 경험을 구현할 수 있습니다.

또한 생성된 TTS 결과물에 추가적인 감정 표현이 필요하거나, 직접 녹음한 연기체 음성을 다른 화자의 보이스로 자연스럽게 옮기고 싶은 경우에도 유연하게 사용할 수 있습니다.

두 가지 버전의 Voice Conversion Acting API가 제공되며, 그 특징은 아래와 같습니다.

## Highlights
* Voice Conversion Acting
	* **연기체 입력 음성** 의 감정선과 극적인 표현력을 더 잘 살려, 서비스에서 제공하는 보이스 화자로 음성 변환 기능을 제공합니다.
	* 예시: 연기체 입력 음성 + 변환 화자: 서비스 제공 화자 = 서비스 제공 화자가 연기체 입력의 표현력을 살려 말하는 음성

* Voice Conversion Acting Custom
	* **연기체 입력 음성** 의 감정선과 극적인 표현력을 더 잘 살려, 사용자가 입력한 커스텀 화자 음성으로 음성 변환 기능을 제공합니다.
	* 예시: 연기체 입력 음성 + 변환 화자: 사용자 입력 화자 음성 = 사용자 입력 화자가 연기체 입력의 표현력을 살려 말하는 음성

<div style="height:20px;"></div>

---

## Sample Code - Jupyter

### Voice Conversion Acting

* Voice Conversion Acting [🔗 API 레퍼런스 바로가기](../reference/voice-conversion-acting)

**In [1]:**
```python
import base64
import requests
import io
import json
import soundfile as sf
import IPython
from pathlib import Path

# ❗OPENAPI_KEY  아래 입력하세요. ❗
OPENAPI_KEY = '...'
header = {'OPENAPI_KEY': OPENAPI_KEY}
response = requests.get("https://openapi.ai.nc.com/vc/acting/v1/api/voices", headers=header)
print("서비스 보이스 화자 수: ", len(response.json()))
print("보이스 화자 상위 5개 보기: ", json.dumps(response.json()[:5], ensure_ascii=False, indent=2))
```

**Out [1]:**
```
서비스 보이스 화자 수:  ...
보이스 화자 상위 5개 보기:  [
  {
    "speaker_name": "<화자 이름>",
    "description": "<성별_연령대_톤_스타일>"
  }
]
```
**In [2]:**
```python
# 입력 오디오 base64str 변환
file_path = Path("sample_audio/input_sample.wav")
with open(file_path, "rb") as f:
    encoded_audio = base64.b64encode(f.read()).decode("utf-8")

# API 요청 데이터 생성
data = {
    "audio": encoded_audio, # 필수: 입력 오디오 base64str
    "audio_name": str(file_path), # 옵션 값
    "speaker_uuid": "25f8c156-12e8-5662-a4ea-e4b6de4e5283", # 필수: 타겟 보이스 speaker_uuid
}

# voice conversion acting API 호출
response = requests.post(
  "https://openapi.ai.nc.com/vc/acting/v1/api/voice-conversion",
  headers=header,
  json=data
)
audio = response.json().get("audio")
wav_bytes = base64.b64decode(audio)

## Bytes 데이터를 메모리 버퍼로 변환
wav_buffer = io.BytesIO(wav_bytes)
## WAV 파일을 NumPy 배열로 로드
wav, sr = sf.read(wav_buffer)


# 미리 듣기
print("입력 음성")
IPython.display.display(IPython.display.Audio(file_path))
print("연기체 표현 음성 변환 결과")
IPython.display.display(IPython.display.Audio(wav, rate=sr))


# 음성 변환 결과 파일 저장
with open("varco_vc_acting.wav", 'wb') as f:
  f.write(wav_bytes)
```

**Out [2]:**
```
입력 음성
  audioplayer

연기체 표현 음성 변환 결과
  audioplayer
```
### Voice Conversion Acting Custom

* Voice Conversion Acting Custom [🔗 API 레퍼런스 바로가기](https://api.varco.ai/ko/reference/voice-conversion-acting-custom)

**In [3]:**
```python
# 입력 오디오 base64str 변환
file_path = Path("sample_audio/input_sample.wav")
with open(file_path, "rb") as f:
    encoded_audio = base64.b64encode(f.read()).decode("utf-8")
    
# Custom 타겟 보이스 오디오 base64str 변환
custom_speaker_file_path = Path("sample_audio/target_sample.wav")

with open(custom_speaker_file_path, "rb") as f:
    encoded_custom_speaker_audio = base64.b64encode(f.read()).decode("utf-8")

# API 요청 데이터 생성
data = {
    "audio": encoded_audio, # 필수: 입력 오디오 base64str
    "speaker_audio": encoded_custom_speaker_audio # Custom 타겟 보이스 오디오 base64str
}

# voice conversion acting custom API 호출
response = requests.post(
  "https://openapi.ai.nc.com/vc/acting/v1/api/voice-conversion-custom",
  headers=header,
  json=data,
)
audio = response.json().get("audio")
wav_bytes = base64.b64decode(audio)

## Bytes 데이터를 메모리 버퍼로 변환
wav_buffer = io.BytesIO(wav_bytes)
## WAV 파일을 NumPy 배열로 로드
wav, sr = sf.read(wav_buffer)


# 미리 듣기
print("입력 음성")
IPython.display.display(IPython.display.Audio(file_path))
print("Custom 타겟 보이스 오디오")
IPython.display.display(IPython.display.Audio(custom_speaker_file_path))
print("연기체 표현 음성 변환 결과")
IPython.display.display(IPython.display.Audio(wav, rate=sr))


# 음성 변환 결과 파일 저장
with open("varco_vc_acting_custom.wav", 'wb') as f:
  f.write(wav_bytes)
```

**Out [3]:**
```
입력 음성
  audioplayer

Custom 타겟 보이스 오디오
  audioplayer

연기체 표현 보존 음성 변환 결과
  audioplayer
```