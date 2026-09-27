<p>
  <span style="background-color:#49cc90; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    POST
  </span>
  <span style="font-size:1.5em; font-weight:bold; margin-left:4px;">
    /tts/standard/v1/api/synthesize
  </span>
</p>

### Description
입력된 문장을 합성하여 오디오(wav/mp3/flac, base64 encoded)를 반환합니다.  
- 언어를 지정하지 않을 경우, 기본값은 `korean` 입니다.  
- `properties` 필드를 통해 합성된 음성의 빠르기(`speed`)와 목소리의 높낮이(`pitch`)를 조절할 수 있습니다.  
- `text` 필드에는 일반 문자열 또는 SSML을 입력할 수 있습니다.  
  SSML이 사용된 경우, 다른 옵션은 무시됩니다.  
- `text` 필드의 최대 입력 크기는 **1,200 바이트 (UTF-8 기준)** 입니다.

#### 화자 리스트 API
- GET `/tts/standard/v1/api/voices/varco`


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
| `text` | string | Text | `음성 합성 서비스입니다.` | - | No |
| `voice` | string | 음성을 합성할 화자(목소리)의 `speaker_uuid` 입니다. | `` | - | Yes |
| `language` | string | - | `korean` | [`korean`, `english`, `japanese`, `taiwanese`] | No |
| `properties` | object | - | `{'speed': 1.0, 'pitch': 1.0}` | - | No |
| `n_fm_steps` | integer | 음성 합성의 품질. 낮을수록 품질 ↓, 속도↑ - 높을수록 품질↑, 속도 ↓ (입력 범위: 8 ~ 20) | `8` | - | No |
| `seed` | integer | 재생산성을 보장하기 위한 seed 값. -1: 랜덤 생성, 그 외의 정수: 전달 받은 seed 값 기준으로 동일한 음성을 생성. (입력 범위: 음/양의 정수 값) | `-1` | - | No |
| `return_metadata` | boolean | metadata response 여부. | `False` | - | No |
| `media_type` | string | 반환할 오디오 포맷 (wav, mp3, flac). | `wav` | [`wav`, `mp3`, `flac`] | No |

<span style="font-weight:bold;">
  Body Parameters - properties
</span>

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
  "audio": "<Base64-encoded WAV data>",
  "ssml": "<Optional: Processed SSML string>",
  "metadata": "<Optional: Synthesis metadata>",
  "media_type": "<Optional: Returned audio format>"
}
```
