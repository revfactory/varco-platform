<p>
  <span style="background-color:#49cc90; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    POST
  </span>
  <span style="font-size:1.5em; font-weight:bold; margin-left:4px;">
    /sound/varco/v1/api/variation
  </span>
</p>

### Description
입력된 오디오 파일을 기반으로 다양한 변형 버전의 사운드를 생성합니다.

원본의 특징을 유지하면서 새로운 변화를 추가할 수 있습니다.

생성 단계 수(10~50), 샘플 수(1~5개), 변화강도(0.0~3.0) 등을 조정할 수 있습니다.

source는 오디오 파일의 base64 인코딩 문자열입니다.
strength의 값이 클수록 큰 변화를 줍니다.

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
| `source` | string | Base64 encoded reference sound to create variations from. | - | - | Yes |
| `num_sample` | integer | Number of samples to generate variations for. | `1` | `>= 1` and `<= 5` | No |
| `strength` | number | Strength of the variation effect. | `1` | `>= 0` and `<= 3` | No |
| `include` | object | 변환할 영역을 지정합니다. | - | - | No |

<span style="font-weight:bold;">
  Body Parameters - include
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
[
  {
    "audio": "string"
  }
]
```