<p>
  <span style="background-color:#49cc90; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    POST
  </span>
  <span style="font-size:1.5em; font-weight:bold; margin-left:4px;">
    /fashion/vton-headswap/v1/headswap
  </span>
</p>

### Description
Headswap을 수행하는 API

❗조건 및 제약 사항
* 주어진 이미지(image)의 크기가 (100, 100)보다 작은 경우 400 에러
* 주어진 이미지(image)의 크기가 (3500, 3500)보다 큰 경우 400 에러
* image에서 사람 얼굴을 찾을 수 없는 경우 400 에러

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
| `model_image` | bytes | Image of the person whose face you want to swap | - | - | Yes |
| `face_image` | bytes | Image of the target face to be applied | - | - | Yes |
| `headswap` | object | JSON string representing HEADSWAP options | `{"prompt": "", "generator_seed": null}` | - | No |

<span style="font-weight:bold;">
  Body Parameters - headswap
</span>

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `prompt` | string | Text description of the additional details | `` | - | No |
| `generator_seed` | integer | Random seed | - | `>= 0` and `<= 2147483647` | No |

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
