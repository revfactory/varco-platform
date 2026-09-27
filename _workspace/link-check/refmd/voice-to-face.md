<p>
  <span style="background-color:#49cc90; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    POST
  </span>
  <span style="font-size:1.5em; font-weight:bold; margin-left:4px;">
    /fa/asfa/v1.1/blendshape
  </span>
</p>

### Description
### Voice-to-Face Animation (SyncFace) API
* 입력 음성(목소리)를 사용하여 Facial Animation (Blendshape Weight)를 생성하는 API

### Inputs
- `id`: request 별 구분을 하기 위한 식별자  (애니메이션에는 영향이 없습니다.)
- `audio`: blendshape 생성을 위한 audio parameter, base64로 encoding 한 string
- `fps`: Animation frame rate
- `lip_style`: 입술 움직임 스타일 (`balanced`, `clear`, `minimal`, `moderate`)
- `face_style`: 표정 변화 스타일 (`natural`, `energetic`, `stoic`, `timid`)
- `emotion`: emotion (neutral, angry, happy, sad, surprise)
- `neck`: 목 움직임 여부 (`on` or `off`)
- `eye`: 눈동자 움직임 여부 (`on` or `off`)

### Output
- 결과물 json (하단의 예시 참고 바람)

<span style="font-weight:bold;">
  Header Parameters
</span>

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

<p>
  <span style="font-weight:bold;">
    Body Parameters
  </span>
  <span style="border:2px solid #77dd77; padding:4px 8px; border-radius:4px; color: #77dd77; display:inline-block; background-color:transparent; margin-left:4px;">
    application/json
  </span>
</p>

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `id` | string | - | - | - | Yes |
| `audio` | bytes | - | - | - | Yes |
| `fps` | number | - | `30` | - | No |
| `lip_style` | string | - | `balanced` | - | No |
| `face_style` | string | - | `natural` | - | No |
| `emotion` | string | - | `neutral` | - | No |
| `neck` | string | - | `off` | - | No |
| `eye` | string | - | `off` | - | No |

### Responses

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `422` | Validation Error |

<p>
  <span style="font-size:1.5em; font-weight:bold;">
    Example - Response
  </span>
  <span style="background-color: #49cc90; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    200
  </span>
  <span style="border:2px solid #77dd77; padding:4px 8px; border-radius:4px; color: #77dd77; display:inline-block; background-color:transparent; margin-left:4px;">
    application/json
  </span>
</p>

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