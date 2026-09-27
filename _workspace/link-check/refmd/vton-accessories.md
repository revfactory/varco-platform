<p>
  <span style="background-color:#49cc90; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    POST
  </span>
  <span style="font-size:1.5em; font-weight:bold; margin-left:4px;">
    /fashion/vton/v1/accessories
  </span>
</p>

### Description
모델에 원하는 악세사리를 입혀보는 API

#### Inputs
- `model_image` (_required_): 모델 이미지
- `bag_image` (_optional_): 가방 이미지
- `hat_image` (_optional_): 모자 이미지
- `shoes_image` (_optional_): 신발 이미지
- `specs` (_optional_): 착장 조건 정보

#### 입력 가능 조합
- `model_image`, `bag_image`, `hat_image`, `shoes_image`, `specs`: `specs`에 맞춰 `bag`, `hat`, `shoes`에 대한 vton 실행
- `model_image`, `bag_image`, `shoes_image`, `specs`: `specs`에 맞춰 `bag`, `shoes`에 대한 vton 실행
- `model_image`, `bag_image`, `hat_image`, `specs`: `specs`에 맞춰 `bag`, `hat`에 대한 vton 실행
- `model_image`, `hat_image`, `shoes_image`, `specs`: `hat`, `shoes`에 대한 vton 실행
- `model_image`, `hat_image`, `shoes_image`: `hat`, `shoes`에 대한 vton 실행
- `model_image`, `hat_image`, `specs`: `hat`에 대한 vton 실행
- `model_image`, `hat_image`: `hat`에 대한 vton 실행
- `model_image`, `shoes_image`, `specs`: `shoes`에 대한 vton 실행
- `model_image`, `shoes_image`: `shoes`에 대한 vton 실행

#### Output
- 생성 결과 이미지: image bytes

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
| `model_image` | bytes | model image | - | - | Yes |
| `bag_image` | bytes | bag image | - | - | No |
| `hat_image` | bytes | hat image | - | - | No |
| `shoes_image` | bytes | shoes image | - | - | No |
| `specs` | object | wearing specifications | - | - | No |

<span style="font-weight:bold;">
  Body Parameters - specs
</span>

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `bag_carry_style` | string | bag carry style | - | [`hands`, `shoulder`, `cross`] | Yes |
| `bag_size` | string | bag size | - | [`small`, `medium`, `large`] | Yes |

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
