# Voice-to-Face Animation (SyncFace)

**개요**

립싱크 애니메이션은 캐릭터와의 대화 몰입도를 크게 좌우하지만, 실제 제작에는 많은 시간과 노력이 필요합니다. <b>Voice-to-Face (SyncFace)</b>는 음성만으로 몇 초 안에 3D 캐릭터의 얼굴 애니메이션을 자동 생성해 이러한 문제를 해결합니다.
현재 Unreal Engine Plugin(UE Plugin) 형태로 제공되며, UE 환경에서 바로 3D 캐릭터에 애니메이션을 적용할 수 있습니다.

<div style="height:20px;"></div>

## 핵심 가치

* **음성 기반 3D 얼굴 애니메이션 생성**
  
    음성 파일만 넣으면, 해당 음성에 맞는 얼굴 애니메이션을 수 초 내에 자동 생성합니다. 포즈 기반으로 설계되어 사람뿐 아니라 동물형, stylized 캐릭터까지 폭넓게 대응합니다.

* **자연스러운 입술 움직임 및 표정 애니메이션**

    입력 음성의 발화 특성을 안정적으로 반영하여 후가공 없이 바로 게임에 적용할 수 있을 정도로 높은 퀄리티의 립싱크·표정 애니메이션을 생성합니다.

* **입술 및 얼굴 스타일 선택 기능**

    사용자가 원하는 스타일로 얼굴/입술 애니메이션 스타일을 만들 수 있습니다. 우물거리는 움직임, 크게 움직이는 움직임 등 다양한 모션을 만들 수 있습니다.

<div style="height:20px;"></div>

## 결과물 데모 영상

[![Voice-to-Face Animation (SyncFace) 데모 영상](https://cdn-api.varco.ai/document/eb11ac00c7be4b659e5d919b79dbd671.jpg)](https://receptive-barber-430.notion.site/VARCO-SyncFace-1c7dbdba4c0a814ebafec225ae384f89)

<p align="center">썸네일을 눌러 데모 영상을 확인하세요.</p>

<div style="height:20px;"></div>

## Unreal Engine(UE) 플러그인 사용자 매뉴얼
UE 플러그인을 사용하여, SyncFace에서 생성된 애니메이션을 UE의 3D 캐릭터에 적용하는 방법을 안내합니다.

[![Voice-to-Face Animation (SyncFace) UE 플러그인 사용자 매뉴얼](https://cdn-api.varco.ai/document/b6da7347acea414abeeb4b3f4321bf67.jpg)](https://receptive-barber-430.notion.site/SyncFace-UE-Plugin-1c7dbdba4c0a810ebb4bdc9d9ff0fc34)

<p align="center">썸네일을 눌러 UE 플러그인 사용자 매뉴얼을 확인하세요.</p>

<div style="height:20px;"></div>

## API 사용법
- 플러그인 없이 직접 API를 호출하여 음성 기반 3D 얼굴 애니메이션을 생성하는 방법을 안내합니다.
### API Request Example
```bash
#!/bin/bash
# Encode audio file to base64
AUDIO_BASE64=$(base64 -w 0 "/path/to/audio/file.wav")

# Create temporary JSON file
TEMP_JSON=$(mktemp)
echo "{\"id\": \"0001\", \"audio\": \"$AUDIO_BASE64\"}" > "$TEMP_JSON"

# Send request using temporary file
curl -L 'https://openapi.ai.nc.com/fa/asfa/v1.1/blendshape' \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json' \
    -H 'openapi_key: <place-your-openapi-key-here>' \
    -d @"$TEMP_JSON"

# Clean up temporary file
rm "$TEMP_JSON"
```

<div style="height:20px;"></div>

### 결과물(.json) 설명
- SyncFace API에서 생성된 .json 파일은 음성에 맞춘 얼굴 애니메이션 데이터를 포함하고 있습니다.
- Blendshape 형태의 애니메이션 데이터로, 각 프레임마다 얼굴의 다양한 부분(입술, 눈, 눈썹 등)의 움직임을 정의합니다.
- [Arkit 52 Blendshape](https://arkit-face-blendshapes.com/) 기준으로 애니메이션 데이터가 제공되며, Blender/Maya/Unreal Engine 등 다양한 3D 소프트웨어에서 활용할 수 있습니다.

<div style="height:20px;"></div>

### Response JSON Example
```json
{
  "id": "string",                      # identifier for the request or result
  "success": true,                     # Indicates whether the process succeeded (true/false)
  
  "blendshape": {
    "exportFps": 30,                   # Animation frame rate (e.g., 30 or 60 FPS)
    "numPoses": 52,                    # Total number of blendshape poses (e.g., 52 for ARKit)
    "numFrames": 240,                  # Total number of frames in the animation
    "faceNames": [                     # Ordered list of blendshape names
      "browInnerUp",
      "eyeBlinkLeft",
      "eyeBlinkRight"
    ],
    "weightMat": [                     # 2D matrix of blendshape weights [numFrames x numPoses]
      [0.0, 0.1, 0.2],
      [0.1, 0.0, 0.3]
    ],
    "joints": [],                      # Joint data - currently unused
    "rotations": [],                   # Rotation data - currently unused
    "translations": []                 # Translation data - currently unused
  },

  "timestamp": "2025-10-24T19:00:00Z", # Timestamp when the result was created
  "jobid": "job_123456789",            # Unique job identifier for tracking
  "credit": 0                          # Credit or cost used for this operation
}
```