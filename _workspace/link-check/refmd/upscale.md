<p>
  <span style="background-color:#49cc90; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    POST
  </span>
  <span style="font-size:1.5em; font-weight:bold; margin-left:4px;">
    /fashion/upscale/v1/super-resolution
  </span>
</p>

### Description
입력 이미지를 지정한 scale_factor 만큼 키우는 API입니다.

#### Inputs
- `image` (_required_): 입력 이미지 (input limit: 2048x2048)
- `scale_factor` (_optional_): 이미지 출력 크기 배수 (positive integer: 2 ~ 6, default: 4)

#### Output
- super-resolution 결과 이미지: image bytes

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
    multipart/form-data
  </span>
</p>

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `image` | bytes | input image | - | - | Yes |
| `scale_factor` | integer | scale factor | `4` | `>= 2` and `<= 6` | No |

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
    image/png
  </span>
</p>

```json
<png image bytes>
```