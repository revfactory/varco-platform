<p>
  <span style="background-color:#49cc90; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    POST
  </span>
  <span style="font-size:1.5em; font-weight:bold; margin-left:4px;">
    /fashion/vton/v1/clothes
  </span>
</p>

### Description
모델에 원하는 옷을 입혀보는 API

#### Inputs
- `clothes_image` (_required_): 의상 이미지
- `model_image` (_optional_): 모델 이미지
- `mask_image` (_optional_): 마스크 이미지
- `vton` (_optional_): vton config
- `clothes_spec` (_optional_): 의상 스펙 정보

#### 입력 가능 조합
- `model_image`, `clothes_image`, `vton`: `vton`에서 `category`값을 기준으로 마스크 이미지를 계산 한 후 vton 실행
- `model_image`, `clothes_image`, `mask_image`, `vton`: vton 실행
- `clothes_image`, `vton`, `clothes_spec`: `clothes_spec`값 기반으로 모델 이미지 및 마스크 이미지를 계산 한 후 vton 실행

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
| `model_image` | bytes | model image | - | - | No |
| `mask_image` | bytes | mask image | - | - | No |
| `clothes_image` | bytes | clothes image | - | - | No |
| `vton` | object | virtual try on options | `{"category":"dresses","generator_seed":null}` | - | No |
| `clothes_spec` | object | clothes specification | - | - | No |

<span style="font-weight:bold;">
  Body Parameters - vton
</span>

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `category` | string | VtonCategory | `dresses` | [`upper_body`, `lower_body`, `dresses`] | No |
| `generator_seed` | integer | generator seed | - | `>= 0` and `<= 2147483647` | No |

<span style="font-weight:bold;">
  Body Parameters - clothes_spec
</span>

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `shoulder_width` | number | shoulder width (in cm) | - | `>= 0` and `<= 250` | No |
| `arm_length` | number | arm length (in cm) | - | `>= 0` and `<= 250` | No |
| `rise_length` | number | rise length (in cm) | - | `>= 0` and `<= 250` | No |
| `waist_width` | number | waist width (in cm) | - | `>= 0` and `<= 250` | No |
| `thigh_width` | number | thigh width (in cm) | - | `>= 0` and `<= 250` | No |
| `hip_width` | number | hip width (in cm) | - | `>= 0` and `<= 250` | No |
| `gender` | string | gender of clothes | - | [`man`, `woman`, `unisex`] | Yes |
| `category` | string | category of clothes | - | [`apparel`, `kids`, `sports`] | Yes |
| `part` | string | part of clothes | - | [`dresses`, `outer`, `jumpsuit`, `upper`, `pants`, `skirt`] | Yes |
| `model_height` | number | model's height (in cm) | - | `>= 50` and `<= 250` | No |
| `total_length` | number | total length of clothes (in cm) | - | `>= 0` and `<= 250` | No |
| `hem_width` | number | hem width of clothes (in cm) | - | `>= 0` and `<= 250` | No |
| `chest_width` | number | chest width of clothes (in cm) | - | `>= 0` and `<= 250` | No |

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
