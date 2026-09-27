<p>
  <span style="background-color:#49cc90; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    POST
  </span>
  <span style="font-size:1.5em; font-weight:bold; margin-left:4px;">
    /fashion/edit/v1/graphic
  </span>
</p>

### Description
이미지 상 제품에 로고를 합성 시켜주는 API

#### Inputs
- `image` (_required_): 입력 이미지
- `graphic_image` (_required_): 그래픽 로고 이미지
- `x` (_required_): 입력 이미지에서 그래픽 이미지를 합성 시킬 bounding box의 x 좌표
- `y` (_required_): 입력 이미지에서 그래픽 이미지를 합성 시킬 bounding box의 y 좌표
- `width` (_required_): 입력 이미지에서 그래픽 이미지를 합성 시킬 bounding box의 width
- `height` (_required_): 입력 이미지에서 그래픽 이미지를 합성 시킬 bounding box의 height
- `angle` (_required_): 입력 이미지에서 그래픽 이미지를 합성 시킬 bounding box의 rotation angle
- `texture` (_optional_): 합성 되는 그래픽의 질감 선택

#### Output
- 로고가 합성된 결과 이미지: image bytes

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
| `graphic_image` | bytes | input graphic logo image | - | - | Yes |
| `x` | integer | location (upper left' x) of graphic image | - | - | Yes |
| `y` | integer | location (upper left' y) of graphic image | - | - | Yes |
| `width` | integer | target width of graphic image | - | - | Yes |
| `height` | integer | target height of graphic image | - | - | Yes |
| `angle` | number | rotation angle of graphic image in degree | - | - | Yes |
| `texture` | string | texture of graphic image | - | [`embossed`, `debossed`, `embroidered`, `printed`, `metal`] | No |

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
