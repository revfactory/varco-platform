<p>
  <span style="background-color:#49cc90; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    POST
  </span>
  <span style="font-size:1.5em; font-weight:bold; margin-left:4px;">
    /sound/varco/v1/api/looping
  </span>
</p>

### Description
입력된 오디오 파일을 매끄럽게 연결하여 무한 반복 재생이 가능하도록 처리합니다.

시작과 끝이 자연스럽게 연결되어 끊김 없는 루프를 생성합니다.
source는 오디오 파일의 base64 인코딩 문자열입니다.

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
| `source` | string | Base64 encoded sound to loop. | - | - | Yes |
| `preserve` | object | 보존할 영역을 지정합니다. | - | - | No |

<span style="font-weight:bold;">
  Body Parameters - preserve
</span>

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `begin` | number | 영역의 시작 시간 (초 단위). | `0` | - | No |
| `end` | number | 영역의 끝 시간 (초 단위). | `0` | - | No |

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
  "audio": "string"
}
```