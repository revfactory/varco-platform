<p>
  <span style="background-color:#49cc90; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    POST
  </span>
  <span style="font-size:1.5em; font-weight:bold; margin-left:4px;">
    /fashion/edit/v1/texture
  </span>
</p>

### Description
이미지 특정 부분의 texutre를 바꾸는 API

#### Inputs
- `image` (_required_): 입력 이미지
- `mask_image` (_required_): 입력 mask 이미지 (texture를 적용하고 싶은 영역)
- `texture_image` (_required_): 입력 texture 이미지
- `x` (_required_): 입력 이미지에서 texture 이미지를 합성 시킬 bounding box의 x 좌표
- `y` (_required_): 입력 이미지에서 texture 이미지를 합성 시킬 bounding box의 y 좌표
- `width` (_required_): 입력 이미지에서 texture 이미지를 합성 시킬 bounding box의 width
- `height` (_required_): 입력 이미지에서 texture 이미지를 합성 시킬 bounding box의 height
- `angle` (_required_): 입력 이미지에서 texture 이미지를 합성 시킬 bounding box의 rotation angle

#### Output
- texture가 변경된 결과 이미지: image bytes

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
| `mask_image` | bytes | input mask image | - | - | Yes |
| `texture_image` | bytes | input texture image | - | - | Yes |
| `x` | integer | location (upper left' x) of logo image | - | - | Yes |
| `y` | integer | location (upper left' y) of logo image | - | - | Yes |
| `width` | integer | target width of logo image | - | - | Yes |
| `height` | integer | target height of logo image | - | - | Yes |
| `angle` | number | rotation angle of logo image in degree | - | - | Yes |

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
