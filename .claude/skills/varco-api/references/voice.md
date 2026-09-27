# VARCO Voice API (TTS · Voice Conversion)
> 원문: api.varco.ai 문서(2026-09 수집). 가이드와 레퍼런스가 다르면 **레퍼런스를 기준으로 한다** (공식 안내: "엔드포인트 별 최신 버전은 항상 API Reference 페이지를 기준으로 확인").

## 목차 (절 이름 — 시작 줄)

- [가이드] voice-overview — 25줄
- [가이드] voice-text-to-speech-lite — 148줄
- [가이드] voice-text-to-speech-standard — 259줄
- [가이드] voice-voice-conversion — 375줄
- [가이드] voice-voice-conversion-acting — 558줄
- [레퍼런스] text-to-speech-lite — 728줄
- [레퍼런스] text-to-speech-standard — 791줄
- [레퍼런스] voice-conversion — 854줄
- [레퍼런스] voice-conversion-custom — 901줄
- [레퍼런스] voice-conversion-acting — 947줄
- [레퍼런스] voice-conversion-acting-custom — 996줄


---

# 제1부. 가이드

---

## [가이드] voice-overview

### VARCO Voice: 당신의 서비스에 목소리를 더하다

**텍스트는 말하게 하고, 목소리를 새롭게 만드는 강력한 Text To Speech, Voice Conversion 등의 API**를 제공합니다.
어떤 서비스에도 더 생생하고 매력적인 음성을 쉽고 빠르게 적용할 수 있습니다.

---

## 주요 기능

### 서비스 목적에 맞춘 고속형·고품질 연기형 Text To Speech

Text To Speech는 두 가지 Lite, Standard 모델을 제공합니다.
Text To Speech (Lite)는 **빠른 응답 속도로 실시간 인터랙션에 최적화**되어 있으며, Text To Speech (Standard)는 **자연스러운 감정 표현과 연기력**으로 더 몰입감 있는 음성 생성이 가능합니다.
서비스 성격에 따라 속도 중심 또는 자연스러움 중심 모델을 선택해 사용할 수 있습니다.

### 내용은 그대로 목소리만 바꿔주는 Voice Conversion

Voice Conversion은 입력 음성의 **내용·리듬·스타일은 그대로 유지하면서 화자 목소리만 원하는 보이스로 바꿔주는 생성형 음성 변환 모델**입니다.

기본 Voice Conversion 모델은 서비스에서 제공하는 보이스 화자로 음성을 변환할 수 있으며, Voice Conversion Custom 모델은 사용자가 직접 제공한 음성을 화자로 삼아 특정 인물이나 캐릭터의 목소리로 변환할 수 있습니다.
또한 Voice Conversion Acting/Acting Custom은 **연기체 입력 음성의 감정선과 극적인 표현력**을 더 잘 살려 변환할 수 있어, 더빙·게임·오디오 드라마처럼 표현력이 중요한 콘텐츠에 특히 효과적입니다.

스튜디오급 음질과 자연스러운 음색 변환을 통해 더빙, 캐릭터 보이스 교체, 버추얼 인플루언서, 게임 NPC 등 다양한 미디어 환경에서 활용할 수 있고, 생성된 TTS 결과물의 보정이나 정교한 운율 제어가 필요할 때도 유연하게 사용할 수 있습니다.

---

## 제공 서비스

### Text To Speech (Lite)

* **실시간 인터랙션에 최적화**
* 텍스트를 입력하여 음성을 생성합니다.
* **추천 용도:** 챗봇, 안내, 네비게이션 등
* Text To Speech (Lite) [🔗 API 도큐먼트 바로가기](voice-text-to-speech-lite)

### Text To Speech (Standard)

*  **자연스러운 감정 표현과 연기력으로 더 몰입감 있는 음성 생성**
* 텍스트를 입력하여 음성을 생성합니다.
* **추천 용도:** 광고, 숏폼, 연기, 게임 등
* Text To Speech (Standard) [🔗 API 도큐먼트 바로가기](voice-text-to-speech-standard)

### Voice Conversion
* **내용·리듬·스타일은 그대로 유지하면서 화자 목소리만 원하는 보이스로 바꿔주는 생성형 음성 변환**
* Voice Conversion
  * **서비스에서 제공하는 보이스 화자 (1293명)** 에 대한 음성 변환 기능을 제공합니다.
  * 예시: 입력 음성 + 변환 화자: 서비스 제공 화자 = 서비스 제공 화자가 말하는 입력 음성
* Voice Conversion Custom
  * 서비스에서 제공하는 보이스 화자 외 **사용자가 입력 가능한 음성**의 화자에 대한 음성 변환 기능을 제공합니다.
  * 예시: 입력 음성 + 변환 화자: 사용자 입력 음성(스폰지밥) = 사용자 입력 음성 화자(스폰지밥)이 말하는 입력 음성
* **추천 용도:** 더빙, 캐릭터 보이스 교체, 버추얼 인플루언서, 게임 NPC 음성 등
* Voice Conversion [🔗 API 도큐먼트 바로가기](voice-voice-conversion)

### Voice Conversion Acting
* **연기체 입력 음성의 감정선과 극적인 표현력을 살린 음성 변환**
* Voice Conversion Acting
  * 서비스 제공 화자로 변환하며 연기 톤과 표현력을 보존해 전달합니다.
* Voice Conversion Acting Custom
  * 사용자 입력 화자 음성으로 변환하며 연기체 표현을 반영합니다.
* **추천 용도:** 더빙, 오디오 드라마, 게임 컷신, 캐릭터 중심 숏폼 콘텐츠
* Voice Conversion Acting [🔗 API 도큐먼트 바로가기](voice-voice-conversion-acting)

---

## 활용 시나리오

  
    
      
        
      
    
    
      📺 Drama Playlist
      감정 표현과 연기를 담은 TTS 드라마 음성 샘플 모음입니다.

      ▶️ 재생목록 바로가기
    
  

   
    
      
        
      
    
    
      📢 Advertisement Playlist
      광고·홍보 콘텐츠 제작에 적합한 다양한 TTS 광고 보이스 샘플입니다.

      ▶️ 재생목록 바로가기
    
  

   
    
      
        
      
    
    
      🎧 Audio Book Playlist
      오디오북 제작에 활용할 수 있는 차분하고 자연스러운 TTS 낭독 샘플입니다.

      ▶️ 재생목록 바로가기
    
  
   
    
      
        
      
    
    
      🕹️ Game Playlist
      게임 캐릭터와 상황에 어울리는 다양한 TTS 게임 보이스 샘플입니다.

      ▶️ 재생목록 바로가기

---

## [가이드] voice-text-to-speech-lite

**Text To Speech (Lite)** 는 대규모 실시간 음성 합성을 위한 저지연·고처리량 엔진입니다. 특히 다양한 보이스를 제공하며, 세션마다 **안정적이고 일관된 음성 품질**을 유지합니다.
AR 기반 모델에서 발생할 수 있는 불규칙한 발음이나 음질 흔들림을 방지하기 위해 **피치·길이·에너지 예측을 안정적으로 제어**하고, 결정론적 합성(deterministic synthesis)을 적용해 언제나 같은 품질의 음성을 제공합니다.

---

## Highlights
* **안정적인 음질**: 결정론적 합성으로 재현성 보장, 랜덤 아티팩트 최소화
* **저지연 응답**:  빠른 응답이 필요한 콘텐츠에 최적

---

## Sample Code - Jupyter

* Text To Speech  (Lite) [🔗 API 레퍼런스 바로가기](../reference/text-to-speech-lite)

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
response = requests.get("https://openapi.ai.nc.com/tts/lite/v1/api/voices/varco",headers=header)
print("보이스 화자 수: ",len(response.json()))
print("보이스 화자 상위 5개 보기: ",json.dumps(response.json()[:5],ensure_ascii=False, indent=2))
```

**Out [1]:**
```
보이스 화자 수:  1293
보이스 화자 상위 5개 보기: [
  {
    "speaker_uuid": "3b2daafa-1f83-580a-a846-d5fc7fd6f3e7",
    "speaker_name": "데리온(분노)",
    "saas_name": null,
    "description": "남성, 노년, 고음, 거침, 고약한"
  },
  {
    "speaker_uuid": "c03c02e0-e190-5091-bfc4-609d14265398",
    "speaker_name": "실라린(분노)",
    "saas_name": null,
    "description": "남성, 노년, 고음, 거침, 고집스러운"
  },
  {
    "speaker_uuid": "22f973e7-9b51-5133-aa81-88a2f75cc0bf",
    "speaker_name": "실라린(행복)",
    "saas_name": null,
    "description": "남성, 노년, 고음, 거침, 노련한"
  },
  {
    "speaker_uuid": "d7da3489-245d-5691-8f55-7f5552b0431e",
    "speaker_name": "실라린(중립)",
    "saas_name": "공현도",
    "description": "남성, 노년, 고음, 거침, 노련한"
  },
  {
    "speaker_uuid": "115c2e5d-043c-5606-b469-4edd8745acc8",
    "speaker_name": "실라린(슬픔)",
    "saas_name": null,
    "description": "남성, 노년, 고음, 거침, 노련한"
  }
]
```
**In [2]:**
```python
text = "안녕하세요. 바르코 보이스 음성합성 API 입니다."
language = "korean"
voice = "d7da3489-245d-5691-8f55-7f5552b0431e"
data={
    "text":text, #  필수, 범위: 최대 1200바이트
    "language": language, # 필수
    "voice":voice, # 필수: speaker_uuid
    "properties": {
      "speed": 1, # 옵션, 기본값 1, 범위: 0.5 ~ 1.5, 권장 범위 0.8 ~ 1.2
      "pitch": 1  # 옵션, 기본값 1, 범위: 0.5 ~ 1.5, 권장 범위 0.8 ~ 1.2
    },
  "return_metadata": False  # 옵션, 기본값 False
  }

# Voice Text To Speech (lite) API 호출
response = requests.post("https://openapi.ai.nc.com/tts/lite/v1/api/synthesize",headers=header, json=data)
audio = response.json().get("audio")
wav_bytes = base64.b64decode(audio)
## Bytes 데이터를 메모리 버퍼로 변환
wav_buffer = io.BytesIO(wav_bytes)
## WAV 파일을 NumPy 배열로 로드
wav, sr = sf.read(wav_buffer)

# 미리 듣기
IPython.display.display(IPython.display.Audio(wav, rate=sr))

#파일 저장
with open("varco_tts_lite_smaple_01.wav", 'wb') as f:
  f.write(wav_bytes)
```

**Out [2]:**
```
 audioplayer
```

---

## [가이드] voice-text-to-speech-standard

**Text To Speech (Standard)** 는 **실감나고 다이나믹한 음성 합성을 제공하는 생성형 음성** 모델입니다. 일반적인 TTS가 동일한 입력에 항상 같은 결과를 내는 것과 달리, **샘플링 기법**을 활용해 **같은 텍스트라도 매번 다른 억양·리듬·표현**으로 합성할 수 있습니다. 덕분에 음성이 반복적이지 않고 사람처럼 **다채롭고 몰입감 있는 경험**을 제공합니다.

또한, 스튜디오급 음질과 함께 다이나믹한 억양을 구현해 스토리텔링, 미디어 로컬라이징, 게임 등 다양한 글로벌 환경에서 활용 가능합니다.

---

## Highlights
* **샘플링 기반 다양성**: 동일한 텍스트도 매번 다른 억양과 스타일로 합성 가능
* **실감나고 다이나믹한 음성**: 반복적이지 않고 몰입감 있는 음성 제공
* **스튜디오급 음질**: 전문 제작 환경에 적합한 선명하고 풍부한 음성

---

## Sample Code - Jupyter

* Text To Speech (Standard) [🔗 API 레퍼런스 바로가기](../reference/text-to-speech-standard)

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
response = requests.get("https://openapi.ai.nc.com/tts/standard/v1/api/voices/varco",headers=header)
print("보이스 화자 수: ",len(response.json()))
print("보이스 화자 상위 5개 보기: ",json.dumps(response.json()[:5],ensure_ascii=False, indent=2))
```

**Out [1]:**
```
보이스 화자 수:  1293
보이스 화자 상위 5개 보기:
[
  {
    "speaker_uuid": "3b2daafa-1f83-580a-a846-d5fc7fd6f3e7",
    "speaker_name": "데리온(분노)",
    "saas_name": null,
    "description": "남성, 노년, 고음, 거침, 고약한"
  },
  {
    "speaker_uuid": "c03c02e0-e190-5091-bfc4-609d14265398",
    "speaker_name": "실라린(분노)",
    "saas_name": null,
    "description": "남성, 노년, 고음, 거침, 고집스러운"
  },
  {
    "speaker_uuid": "22f973e7-9b51-5133-aa81-88a2f75cc0bf",
    "speaker_name": "실라린(행복)",
    "saas_name": null,
    "description": "남성, 노년, 고음, 거침, 노련한"
  },
  {
    "speaker_uuid": "d7da3489-245d-5691-8f55-7f5552b0431e",
    "speaker_name": "실라린(중립)",
    "saas_name": "공현도",
    "description": "남성, 노년, 고음, 거침, 노련한"
  },
  {
    "speaker_uuid": "115c2e5d-043c-5606-b469-4edd8745acc8",
    "speaker_name": "실라린(슬픔)",
    "saas_name": null,
    "description": "남성, 노년, 고음, 거침, 노련한"
  }
]
```
**In [2]:**
```python
text = "안녕하세요. 바르코 보이스 음성합성 API 입니다."
language = "korean"
voice = "d7da3489-245d-5691-8f55-7f5552b0431e"
data={
    "text":text, #  필수, 범위: 최대 1,200바이트
    "language": language, # 필수
    "voice":voice, # 필수: speaker_uuid
    "properties": {
      "speed": 1, # 옵션, 기본값 1, 범위: 0.5 ~ 1.5, 권장 범위 0.8 ~ 1.2
      "pitch": 1  # 옵션, 기본값 1, 범위: 0.5 ~ 1.5, 권장 범위 0.8 ~ 1.2
  },
  "n_fm_steps": 8, # 옵션, 기본값 8 (음성 합성의 품질. 낮을수록 품질 ↓, 속도↑ - 높을수록 품질↑, 속도 ↓ (입력 범위: 8 ~ 20))
  "seed": -1, # 옵션, 기본값 -1 (-1: 호출 할 때 마다 매번 다른 생성, 양수 시 특정 음성 고정 생성, 같은 seed를 사용하면 항상 동일한 음성이 생성됨)
  "return_metadata": False # 옵션, 기본값 1
}

# Voice Text To Speech (standard) API 호출
response = requests.post("https://openapi.ai.nc.com/tts/standard/v1/api/synthesize",headers=header, json=data)
audio = response.json().get("audio")
wav_bytes = base64.b64decode(audio)
## Bytes 데이터를 메모리 버퍼로 변환
wav_buffer = io.BytesIO(wav_bytes)
## WAV 파일을 NumPy 배열로 로드
wav, sr = sf.read(wav_buffer)

# 미리 듣기
IPython.display.display(IPython.display.Audio(wav, rate=sr))

#파일 저장
with open("varco_tts_standard_smaple_01.wav", 'wb') as f:
  f.write(wav_bytes)
```

**Out [2]:**
```
 audioplayer
```

---

## [가이드] voice-voice-conversion

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

---

## [가이드] voice-voice-conversion-acting

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

---

# 제2부. API 레퍼런스

---

## [레퍼런스] text-to-speech-lite

**POST** `/tts/lite/v1/api/synthesize`

### Description
입력된 문장을 합성하여 오디오(wav/mp3/flac, base64 encoded)를 반환합니다.  
- 언어를 지정하지 않을 경우, 기본값은 `korean` 입니다.  
- `properties` 필드를 통해 합성된 음성의 빠르기(`speed`)와 목소리의 높낮이(`pitch`)를 조절할 수 있습니다.  
- `text` 필드에는 일반 문자열 또는 SSML을 입력할 수 있습니다.  
  SSML이 사용된 경우, 다른 옵션은 무시됩니다.  
- `text` 필드의 최대 입력 크기는 **1,200 바이트 (UTF-8 기준)** 입니다.

#### 화자 리스트 API
- GET `/tts/lite/v1/api/voices/varco`

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters application/json

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `text` | string | Text | `음성 합성 서비스입니다.` | - | No |
| `voice` | string | 음성을 합성할 화자(목소리)의 `speaker_uuid` 입니다. | `` | - | Yes |
| `language` | string | - | `korean` | [`korean`, `english`, `japanese`, `taiwanese`] | No |
| `properties` | object | - | `{'speed': 1.0, 'pitch': 1.0}` | - | No |
| `n_fm_steps` | integer | 음성 합성의 품질. 낮을수록 품질 ↓, 속도↑ - 높을수록 품질↑, 속도 ↓ (입력 범위: 8 ~ 20) | `8` | - | No |
| `seed` | integer | 재생산성을 보장하기 위한 seed 값. -1: 랜덤 생성, 그 외의 정수: 전달 받은 seed 값 기준으로 동일한 음성을 생성. (입력 범위: 음/양의 정수 값) | `-1` | - | No |
| `return_metadata` | boolean | metadata response 여부. | `False` | - | No |
| `media_type` | string | 반환할 오디오 포맷 (wav, mp3, flac). | `wav` | [`wav`, `mp3`, `flac`] | No |

##### Body Parameters - properties

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `speed` | number | Speed | `1` | - | No |
| `pitch` | number | Pitch | `1` | - | No |

### Responses

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `400` | Bad Request |
| `422` | Validation Error |
| `500` | Internal Server Error |

#### Example - Response 200 application/json

```json
{
  "audio": "<Base64-encoded WAV data>",
  "ssml": "<Optional: Processed SSML string>",
  "metadata": "<Optional: Synthesis metadata>",
  "media_type": "<Optional: Returned audio format>"
}
```

---

## [레퍼런스] text-to-speech-standard

**POST** `/tts/standard/v1/api/synthesize`

### Description
입력된 문장을 합성하여 오디오(wav/mp3/flac, base64 encoded)를 반환합니다.  
- 언어를 지정하지 않을 경우, 기본값은 `korean` 입니다.  
- `properties` 필드를 통해 합성된 음성의 빠르기(`speed`)와 목소리의 높낮이(`pitch`)를 조절할 수 있습니다.  
- `text` 필드에는 일반 문자열 또는 SSML을 입력할 수 있습니다.  
  SSML이 사용된 경우, 다른 옵션은 무시됩니다.  
- `text` 필드의 최대 입력 크기는 **1,200 바이트 (UTF-8 기준)** 입니다.

#### 화자 리스트 API
- GET `/tts/standard/v1/api/voices/varco`

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters application/json

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `text` | string | Text | `음성 합성 서비스입니다.` | - | No |
| `voice` | string | 음성을 합성할 화자(목소리)의 `speaker_uuid` 입니다. | `` | - | Yes |
| `language` | string | - | `korean` | [`korean`, `english`, `japanese`, `taiwanese`] | No |
| `properties` | object | - | `{'speed': 1.0, 'pitch': 1.0}` | - | No |
| `n_fm_steps` | integer | 음성 합성의 품질. 낮을수록 품질 ↓, 속도↑ - 높을수록 품질↑, 속도 ↓ (입력 범위: 8 ~ 20) | `8` | - | No |
| `seed` | integer | 재생산성을 보장하기 위한 seed 값. -1: 랜덤 생성, 그 외의 정수: 전달 받은 seed 값 기준으로 동일한 음성을 생성. (입력 범위: 음/양의 정수 값) | `-1` | - | No |
| `return_metadata` | boolean | metadata response 여부. | `False` | - | No |
| `media_type` | string | 반환할 오디오 포맷 (wav, mp3, flac). | `wav` | [`wav`, `mp3`, `flac`] | No |

##### Body Parameters - properties

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `speed` | number | Speed | `1` | - | No |
| `pitch` | number | Pitch | `1` | - | No |

### Responses

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `400` | Bad Request |
| `422` | Validation Error |
| `500` | Internal Server Error |

#### Example - Response 200 application/json

```json
{
  "audio": "<Base64-encoded WAV data>",
  "ssml": "<Optional: Processed SSML string>",
  "metadata": "<Optional: Synthesis metadata>",
  "media_type": "<Optional: Returned audio format>"
}
```

---

## [레퍼런스] voice-conversion

**POST** `/vc/varco/v1/api/voice-conversion`

### Description
입력된 음성을 선택한 화자의 목소리로 변환합니다.  
- 입력 오디오는 **WAV, FLAC, MP3 형식**을 지원합니다.  
- 음성(`audio`)의 길이는 **최대 60초** 까지만 허용됩니다.  
- `speaker_uuid` 필드를 통해 변환 대상 화자를 지정합니다.  
- 반환되는 `audio`는 Base64로 인코딩된 WAV 형식의 오디오입니다.

#### 화자 리스트 API
- GET `/vc/varco/v1/api/voices`

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters application/json

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `audio` | bytes | 변환할 원본 음성의 Base64 인코딩 데이터 (최대 60초, WAV/FLAC/MP3) | - | - | Yes |
| `audio_name` | string | 원본 음성 파일 이름 (optional) | `` | - | No |
| `speaker_uuid` | string | 변환 대상 화자의 uuid | - | - | Yes |

### Responses

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `400` | Bad Request |
| `422` | Validation Error |
| `500` | Internal Server Error |

#### Example - Response 200 application/json

```json
{
  "audio": "<Base64-encoded WAV data>"
}
```

---

## [레퍼런스] voice-conversion-custom

**POST** `/vc/varco/v1/api/voice-conversion-custom`

### Description
입력된 원본 음성과 커스텀 화자의 음성을 함께 업로드하여,  
원본 음성을 커스텀 화자의 목소리로 변환합니다.  

- 입력 오디오는 **WAV, FLAC, MP3 형식**을 지원합니다.  
- 각 음성(`audio`, `speaker_audio`)의 길이는 **최대 60초** 까지만 허용됩니다.  
- 반환되는 `audio`는 Base64로 인코딩된 WAV 형식의 오디오입니다.

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters application/json

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `audio` | bytes | 변환할 원본 음성의 Base64 인코딩 데이터 (최대 60초, WAV/FLAC/MP3) | - | - | Yes |
| `audio_name` | string | 원본 음성 파일 이름 (optional) | `` | - | No |
| `speaker_audio` | bytes | 화자 음성의 Base64 인코딩 데이터 (최대 60초, WAV/FLAC/MP3) | - | - | Yes |
| `speaker_name` | string | 화자 음성 파일 이름 (optional) | `` | - | No |

### Responses

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `400` | Bad Request |
| `422` | Validation Error |
| `500` | Internal Server Error |

#### Example - Response 200 application/json

```json
{
  "audio": "<Base64-encoded WAV data>"
}
```

---

## [레퍼런스] voice-conversion-acting

**POST** `/vc/acting/v1/api/voice-conversion`

### Description
입력된 음성을 선택한 화자의 목소리로 변환합니다.  
특히 **연기체 입력 음성** 에 담긴 다이내믹한 감정선과 극적인 표현력을 더 잘 살리도록 최적화되어 있어, 원본 음성의 내용·리듬·스타일은 유지하면서도 표현력 있는 발화를 자연스럽게 변환할 수 있습니다.  

- 입력 오디오는 **WAV, FLAC, MP3 형식**을 지원합니다.  
- 음성(`audio`)의 길이는 **최대 60초** 까지만 허용됩니다.  
- `speaker_uuid` 필드를 통해 변환 대상 화자를 지정합니다.  
- 반환되는 `audio`는 Base64로 인코딩된 WAV 형식의 오디오입니다.

#### 화자 리스트 API
- GET `/vc/acting/v1/api/voices`

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters application/json

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `audio` | bytes | 변환할 원본 음성의 Base64 인코딩 데이터 (최대 60초, WAV/FLAC/MP3) | - | - | Yes |
| `audio_name` | string | 원본 음성 파일 이름 (optional) | `` | - | No |
| `speaker_uuid` | string | 변환 대상 화자의 uuid | - | - | Yes |

### Responses

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `400` | Bad Request |
| `422` | Validation Error |
| `500` | Internal Server Error |

#### Example - Response 200 application/json

```json
{
  "audio": "<Base64-encoded WAV data>"
}
```

---

## [레퍼런스] voice-conversion-acting-custom

**POST** `/vc/acting/v1/api/voice-conversion-custom`

### Description
입력된 원본 음성과 커스텀 화자의 음성을 함께 업로드하여,  
원본 음성을 해당 화자의 목소리로 변환합니다. 특히 **연기체 입력 음성** 에 담긴 감정선과 극적인 표현력을 더 잘 살리도록 최적화되어 있습니다.  

- 입력 오디오는 **WAV, FLAC, MP3 형식**을 지원합니다.  
- 각 음성(`audio`, `speaker_audio`)의 길이는 **최대 60초** 까지만 허용됩니다.  
- 반환되는 `audio`는 Base64로 인코딩된 WAV 형식의 오디오입니다.

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters application/json

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `audio` | bytes | 변환할 원본 음성의 Base64 인코딩 데이터 (최대 60초, WAV/FLAC/MP3) | - | - | Yes |
| `audio_name` | string | 원본 음성 파일 이름 (optional) | `` | - | No |
| `speaker_audio` | bytes | 커스텀 화자 음성의 Base64 인코딩 데이터 (최대 60초, WAV/FLAC/MP3) | - | - | Yes |
| `speaker_name` | string | 커스텀 화자 음성 파일 이름 (optional) | `` | - | No |

### Responses

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `400` | Bad Request |
| `422` | Validation Error |
| `500` | Internal Server Error |

#### Example - Response 200 application/json

```json
{
  "audio": "<Base64-encoded WAV data>"
}
```
