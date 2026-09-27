
**Text To Speech (Lite)** 는 대규모 실시간 음성 합성을 위한 저지연·고처리량 엔진입니다. 특히 다양한 보이스를 제공하며, 세션마다 **안정적이고 일관된 음성 품질**을 유지합니다.
AR 기반 모델에서 발생할 수 있는 불규칙한 발음이나 음질 흔들림을 방지하기 위해 **피치·길이·에너지 예측을 안정적으로 제어**하고, 결정론적 합성(deterministic synthesis)을 적용해 언제나 같은 품질의 음성을 제공합니다.

<div style="height:20px;"></div>

---

## Highlights
* **안정적인 음질**: 결정론적 합성으로 재현성 보장, 랜덤 아티팩트 최소화
* **저지연 응답**:  빠른 응답이 필요한 콘텐츠에 최적

<div style="height:20px;"></div>

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

