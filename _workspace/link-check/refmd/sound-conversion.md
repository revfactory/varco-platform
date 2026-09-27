<p>
  <span style="background-color:#49cc90; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    POST
  </span>
  <span style="font-size:1.5em; font-weight:bold; margin-left:4px;">
    /sound/varco/v1/api/conversion
  </span>
</p>

### Description
소스 오디오를 참조 오디오의 스타일로 변환합니다. 

음성이나 사운드의 특성을 다른 스타일로 변경할 수 있습니다.

변환 비율(0.0~2.0) 등을 조정할 수 있습니다.

ratio의 값이 클수록(1.2 이상) 참조 오디오의 음색과 멀어질 수 있습니다.
source와 reference는 오디오 파일의 base64 인코딩 문자열입니다.

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
| `source` | string | Base64 encoded source sound. | - | - | Yes |
| `reference` | string | Base64 encoded reference sound. | - | - | Yes |
| `ratio` | number | Conversion Ratio | `1` | `>= 0` and `<= 2` | No |
| `enhance` | boolean | Whether to enhance source sound. | `False` | - | No |

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