
**Text To Speech (Standard)** 는 **실감나고 다이나믹한 음성 합성을 제공하는 생성형 음성** 모델입니다. 일반적인 TTS가 동일한 입력에 항상 같은 결과를 내는 것과 달리, **샘플링 기법**을 활용해 **같은 텍스트라도 매번 다른 억양·리듬·표현**으로 합성할 수 있습니다. 덕분에 음성이 반복적이지 않고 사람처럼 **다채롭고 몰입감 있는 경험**을 제공합니다.

또한, 스튜디오급 음질과 함께 다이나믹한 억양을 구현해 스토리텔링, 미디어 로컬라이징, 게임 등 다양한 글로벌 환경에서 활용 가능합니다.

<div style="height:20px;"></div>

---

## Highlights
* **샘플링 기반 다양성**: 동일한 텍스트도 매번 다른 억양과 스타일로 합성 가능
* **실감나고 다이나믹한 음성**: 반복적이지 않고 몰입감 있는 음성 제공
* **스튜디오급 음질**: 전문 제작 환경에 적합한 선명하고 풍부한 음성

<div style="height:20px;"></div>

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

