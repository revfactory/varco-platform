<p>
  <span style="background-color:#49cc90; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    POST
  </span>
  <span style="font-size:1.5em; font-weight:bold; margin-left:4px;">
    /vc/acting/v1/api/voice-conversion-custom
  </span>
</p>

### Description
입력된 원본 음성과 커스텀 화자의 음성을 함께 업로드하여,  
원본 음성을 해당 화자의 목소리로 변환합니다. 특히 **연기체 입력 음성** 에 담긴 감정선과 극적인 표현력을 더 잘 살리도록 최적화되어 있습니다.  

- 입력 오디오는 **WAV, FLAC, MP3 형식**을 지원합니다.  
- 각 음성(`audio`, `speaker_audio`)의 길이는 **최대 60초** 까지만 허용됩니다.  
- 반환되는 `audio`는 Base64로 인코딩된 WAV 형식의 오디오입니다.

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
| `speaker_audio` | bytes | 커스텀 화자 음성의 Base64 인코딩 데이터 (최대 60초, WAV/FLAC/MP3) | - | - | Yes |
| `speaker_name` | string | 커스텀 화자 음성 파일 이름 (optional) | `` | - | No |

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
