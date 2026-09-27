
Voice Conversion은 입력 음성을 **화자의 목소리만 바꾸어 재생성하는 생성형 음성 변환 모델**입니다. 입력 음성의 내용·리듬·스타일은 그대로 유지하면서, 원하는 다른 화자의 목소리로 자연스럽게 치환할 수 있습니다.

고품질 스튜디오급 음질과 자연스러운 음색 변환을 지원해, 더빙·캐릭터 보이스 교체·버추얼 인플루언서·게임 NPC 음성 등 다양한 미디어 환경에서 활용할 수 있습니다. 원본 음성의 말하기 스타일을 살리면서도, 여러 캐릭터 목소리로 유연하게 바꿀 수 있어, 글로벌 서비스에서 일관된 톤&매너를 유지하면서도 높은 몰입감을 제공하는 음성 경험을 구현할 수 있습니다.

또한 생성된 TTS 결과물에 보완이 필요하거나, 정교한 운율 제어가 필요한 음성이 필요한 경우, 직접 녹음한 음성으로 원하는 목소리를 입혀 생성해 볼 수도 있습니다.

두 가지 버전의 Voice Conversion API가 제공이 되며, 그 특징은 아래와 같습니다.

## Highlights
* Voice Conversion
	* 서비스에서 제공하는 보이스 화자 (1293명)에 대한 음성 변환 기능을 제공합니다.
	* 예시: 입력 음성 + 변환 화자: 서비스 제공 화자 = 서비스 제공 화자가 말하는 입력 음성

* Voice Conversion Custom
	* 서비스에서 제공하는 보이스 화자 외 사용자가 입력 가능한 음성의 화자에 대한 음성 변환 기능을 제공합니다.
	* 예시: 입력 음성 + 변환 화자: 사용자 입력 음성(스폰지밥) = 사용자 입력 음성 화자(스폰지밥)이 말하는 입력 음성

<div style="height:20px;"></div>

---

## Sample Code - Jupyter

### voice conversion

* voice conversion [🔗 API 레퍼런스 바로가기](../reference/voice-conversion)

**In [1]:**
```python
import base64
import requests
import io
import json
import soundfile as sf
import IPython.display as ipd
import IPython

# ❗OPENAPI_KEY  아래 입력하세요. ❗
OPENAPI_KEY = '...'
header = {'OPENAPI_KEY': OPENAPI_KEY} 
response = requests.get("https://openapi.ai.nc.com/vc/varco/v1/api/voices",headers=header)
print("서비스 보이스 화자 수: ",len(response.json()))
print("보이스 화자 상위 5개 보기: ",json.dumps(response.json()[:5],ensure_ascii=False, indent=2))
```

**Out [1]:**
```
서비스 보이스 화자 수:  1293
보이스 화자 상위 5개 보기:  [
  {
    "speaker_name": "마틸다",
    "description": "남성_어린이_중음_거침_털털한"
  },
  {
    "speaker_name": "아멜리",
    "description": "여성_어린이_고음_얇음_소심한"
  },
  {
    "speaker_name": "마지",
    "description": "여성_중년_중음_거침_뻔뻔한"
  },
  {
    "speaker_name": "얼",
    "description": "남성_중년_중음_거침_느긋한"
  },
  {
    "speaker_name": "랜스",
    "description": "남성_청년_고음_얇음_탐욕스러운"
  }
]
```
**In [2]:**
```python
# 입력 오디오 base64str 변환
file_path = Path("sample_audio/input_sample.wav")
with open(file_path, "rb") as inF:
    encoded_audio = base64.b64encode(inF.read()).decode("utf-8")

# API 요청 데이터 생성
data = {
    "audio": encoded_audio, # 필수: 입력 오디오 base64str
    "audio_name": str(file_path), # 옵션 값
    "speaker_uuid": "25f8c156-12e8-5662-a4ea-e4b6de4e5283", # 필수: 타겟 보이스 speaker_uuid
}

# voice conversion API 호출
response = requests.post(
  "https://openapi.ai.nc.com/vc/varco/v1/api/voice-conversion",
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
print("음성 변환 결과")
IPython.display.display(IPython.display.Audio(wav, rate=sr))


# 음성 변환 결과 파일 저장
with open(f"varco_vc_{speaker_name}.wav", 'wb') as f:
  f.write(wav_bytes)
```

**Out [2]:**
```
입력 음성
  audioplayer

음성 변환 결과
  audioplayer
```
### Voice Conversion Custom

* Voice Conversion Custom [🔗 API 레퍼런스 바로가기](https://api.varco.ai/ko/reference/voice-conversion-custom)

**In [3]:**
```python
# 입력 오디오 base64str 변환
file_path = Path("sample_audio/input_sample.wav")
with open(file_path, "rb") as f:
    encoded_audio = base64.b64encode(f.read()).decode("utf-8")
    
# Custom 보이스(타켓 보이스) 오디오 base64str 변환
custom_speaker_file_path = Path("sample_audio/target_sample.wav")

# custom_speaker_file_path = "1. ENG.wav"
with open(custom_speaker_file_path, "rb") as f:
    encoded_custom_speaker_audio = base64.b64encode(f.read()).decode("utf-8")

# API 요청 데이터 생성
data = {
    "audio": encoded_audio, # 필수: 입력 오디오 base64str
    "speaker_audio":encoded_custom_speaker_audio # Custom 보이스(타켓 보이스) 오디오 base64str
}

# voice conversion custom API 호출
response = requests.post(
  "https://openapi.ai.nc.com/vc/varco/v1/api/voice-conversion-custom",
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
print("Custom 보이스(타켓 보이스) 오디오")
IPython.display.display(IPython.display.Audio(custom_speaker_file_path))
print("음성 변환 결과")
IPython.display.display(IPython.display.Audio(wav, rate=sr))


# 음성 변환 결과 파일 저장
with open(f"varco_vc_custom.wav", 'wb') as f:
  f.write(wav_bytes)
```

**Out [3]:**
```
입력 음성
  audioplayer

Custom 보이스(타켓 보이스) 오디오
  audioplayer

음성 변환 결과
  audioplayer
```