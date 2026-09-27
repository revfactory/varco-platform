<p>
  <span style="background-color:#49cc90; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    POST
  </span>
  <span style="font-size:1.5em; font-weight:bold; margin-left:4px;">
    /vc/varco/v1/api/voice-conversion
  </span>
</p>

### Description
입력된 음성을 선택한 화자의 목소리로 변환합니다.  
- 입력 오디오는 **WAV, FLAC, MP3 형식**을 지원합니다.  
- 음성(`audio`)의 길이는 **최대 60초** 까지만 허용됩니다.  
- `speaker_uuid` 필드를 통해 변환 대상 화자를 지정합니다.  
- 반환되는 `audio`는 Base64로 인코딩된 WAV 형식의 오디오입니다.

#### 화자 리스트 API
- GET `/vc/varco/v1/api/voices`

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
  "audio": "<Base64-encoded WAV data>"
}
```
