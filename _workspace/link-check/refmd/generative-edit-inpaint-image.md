<p>
  <span style="background-color:#49cc90; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    POST
  </span>
  <span style="font-size:1.5em; font-weight:bold; margin-left:4px;">
    /fashion/edit/v1/inpaint-image
  </span>
</p>

### Description
이미지상 mask_image로 명시한 부분을 reference_image 및 reference_mask_image로 생성하여 합성하는 API

#### Inputs
- `image` (_required_): 입력 이미지
- `mask_image` (_required_): 입력 mask 이미지
- `reference_image` (_required_): 입력 reference 이미지
- `reference_mask_image` (_required_): 입력 reference mask 이미지

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
| `image` | bytes | input image | - | - | Yes |
| `mask_image` | bytes | input mask image | - | - | Yes |
| `reference_image` | bytes | input reference image | - | - | Yes |
| `reference_mask_image` | bytes | input reference mask image | - | - | Yes |

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
