<p>
  <span style="background-color:#49cc90; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    POST
  </span>
  <span style="font-size:1.5em; font-weight:bold; margin-left:4px;">
    /fashion/edit/v1/inpaint
  </span>
</p>

### Description
이미지상 mask_image로 명시한 부분을 prompt로 생성하여 합성하는 API

두가지의 모델 중 하나를 선택하여 사용할 수 있습니다.
- `sdxl`, `nano_banana`

#### Inputs
- `model` (_required_): `sdxl`, `nano_banana` 중 하나
- `image` (_required_): 입력 이미지
- `mask_image` (_required_): 입력 mask 이미지
- `prompt` (_required_): 생성할 영역을 설명하는 프롬프트

#### Output
- inpainting 결과 이미지: image bytes

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
| `model` | string | select model | - | [`sdxl`, `nano_banana`] | Yes |
| `image` | bytes | input image | - | - | Yes |
| `mask_image` | bytes | input mask image | - | - | Yes |
| `prompt` | string | describe what to fill | - | - | Yes |

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
