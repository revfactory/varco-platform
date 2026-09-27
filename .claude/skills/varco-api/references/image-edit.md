# Art Fashion · 이미지 편집 API
> 원문: api.varco.ai 문서(2026-09 수집). 가이드와 레퍼런스가 다르면 **레퍼런스를 기준으로 한다** (공식 안내: "엔드포인트 별 최신 버전은 항상 API Reference 페이지를 기준으로 확인").

## 목차 (절 이름 — 시작 줄)

- [가이드] fashion-overview — 26줄
- [레퍼런스] vton-clothes — 130줄
- [레퍼런스] vton-accessories — 210줄
- [레퍼런스] headswap — 278줄
- [레퍼런스] generative-edit-eraser — 328줄
- [레퍼런스] generative-edit-inpaint — 374줄
- [레퍼런스] generative-edit-inpaint-image — 425줄
- [레퍼런스] generative-edit-texture — 473줄
- [레퍼런스] generative-edit-perspective — 529줄
- [레퍼런스] generative-edit-graphic — 575줄
- [레퍼런스] generative-edit-background — 631줄
- [레퍼런스] upscale — 719줄


---

# 제1부. 가이드

---

## [가이드] fashion-overview

## Art Fashion API
VARCO Art Fashion SaaS 서비스의 다양한 기능을 API로 사용할 수 있습니다.\
모델의 얼굴을 바꾸고 원하는 의상을 착장해 고퀄리티의 패션 마케팅
이미지를 손쉽게 생성할 수 있습니다.

![overview](https://cdn-api.varco.ai/document/7cf19c8ba46e42638684e587bcd2f070.png)

---

### 제공 서비스

#### Virtual Try On
모델 이미지에 마스크로 지정한 영역에 원하는 의상을 착장합니다.

- VARCO Art Fashion SaaS 서비스의 '인물 착장' 기능의 API입니다. 
- 상의, 하의, 전신 의상에 대한 착장을 지원합니다. 
- 추천 용도: 인물 이미지 가상 착장, 마케팅 콘텐츠 생성 

#### Virtual Try On for Accessories
모델 이미지에 원하는 모자, 신발,가방을 착장합니다.

- VARCO Art Fashion SaaS 서비스의 '인물 착장' 기능의 API입니다. 
- 모자, 신발, 가방에 대한 착장을 지원합니다. 
- 추천 용도: 인물 이미지 가상 착장, 마케팅 콘텐츠 생성

#### Headswap
모델 이미지에 원하는 얼굴을 합성합니다. 

- VARCO Art Fashion SaaS 서비스의 '인물 착장' 기능의 API입니다. 
- 추천 용도: 마케팅 콘텐츠 생성

#### Eraser
원본 이미지에서 마스크로 지정한 영역을 자연스럽게 지우고 주변 영역과 유사하게 채웁니다.

- VARCO Art Fashion SaaS 서비스의 '에디팅 > 인페인팅 > 지우기' 기능의 API입니다.
- 추천 용도: 이미지 수정

#### Inpaint (Text)
원본 이미지에서 마스크로 지정한 영역에 텍스트 프롬프트로 이미지를 생성합니다.

- VARCO Art Fashion SaaS 서비스의 '에디팅 > 인페인팅' 기능의 API입니다.
- 추천 용도 : 이미지 수정

#### Inpaint (Image)
원본 이미지에서 마스크로 지정한 영역에 참고 이미지를 활용하여 이미지를 생성합니다.

- 추천 용도 : 이미지 수정

#### Texture
원본 이미지에서 마스크로 지정한 영역에 참고 이미지를 활용하여 이미지를 생성합니다.

- VARCO Art Fashion SaaS 서비스의 '에디팅 > 텍스쳐 변경' 기능의 API입니다.
- 추천 용도 : 제품 이미지의 텍스쳐/패턴 변경

#### Perspective
원본 이미지를 활용하여 다른 각도의 이미지를 생성합니다.

- VARCO Art Fashion SaaS 서비스의 '에디팅 > 시점 변경' 기능의 API입니다.
- 옵션으로 정면, 후면, 윗면, 측면, 쿼터뷰 시점 변경을 지원합니다.
- 추천 용도 : 제품 또는 인물 이미지의 시점 변경

#### Graphic
원본 이미지에서 원하는 부분에 참고 이미지(그래픽, 로고 등)를 올려 놓으면 자연스럽게 참고 이미지가 합성된 이미지를 생성합니다. 

- VARCO Art Fashion SaaS 서비스의 '에디팅 > 그래픽 삽입' 기능의 API입니다.
- 옵션으로 엠보싱, 디보싱, 자수, 프린트, 메탈 텍스쳐를 지원합니다.
- 추천 용도 : 제품 또는 인물 이미지에 그래픽 합성

#### Background
입력된 전경 이미지를 제외한 부분에 텍스트 프롬프트로 배경 이미지를 생성합니다.

- VARCO Art Fashion SaaS 서비스의 '배경 > 배경 합성' 기능의 API입니다.
- 배경과 어울리게 전경 이미지에는 자연스러운 조명이 적용됩니다.
- 추천 용도 : 마케팅 콘텐츠 생성

#### Upscale
입력 이미지를 2~6x 업스케일하는 기능입니다.

- VARCO Art Fashion SaaS 서비스의 이미지 상세 정보 창 내 업스케일 기능의 API입니다. 
- 상의, 하의, 전신 의상에 대한 착장을 지원합니다. 
- 추천 용도: 저해상도 이미지의 화질 개선

---

### 활용 시나리오

#### 1. 이미지의 배경을 다양하게 변경해 마케팅 콘텐츠로 활용
추가 촬영없이 이미지의 누끼컷 만으로 배경을 다양하게 변경해 마케팅 콘텐츠로 활용할 수 있습니다.

![overview](https://cdn-api.varco.ai/document/8de22557804c459eb1f634192c432cb7.png)

#### 2. 제품의 시점을 변경하고 그래픽 삽입하여 샘플 제작
제품의 옆면 컷을 활용하여 앞면을 만들고 원하는 그래픽을 삽입하여 샘플을 미리 제작할 수 있습니다.

![overview](https://cdn-api.varco.ai/document/d02fea049ed44d67af9e4ab6a0a98f22.png)

---

# 제2부. API 레퍼런스

---

## [레퍼런스] vton-clothes

**POST** `/fashion/vton/v1/clothes`

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

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters multipart/form-data

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `model_image` | bytes | model image | - | - | No |
| `mask_image` | bytes | mask image | - | - | No |
| `clothes_image` | bytes | clothes image | - | - | No |
| `vton` | object | virtual try on options | `{"category":"dresses","generator_seed":null}` | - | No |
| `clothes_spec` | object | clothes specification | - | - | No |

##### Body Parameters - vton

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `category` | string | VtonCategory | `dresses` | [`upper_body`, `lower_body`, `dresses`] | No |
| `generator_seed` | integer | generator seed | - | `>= 0` and `<= 2147483647` | No |

##### Body Parameters - clothes_spec

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

#### Example - Response 200 image/png

```json

```

---

## [레퍼런스] vton-accessories

**POST** `/fashion/vton/v1/accessories`

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

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters multipart/form-data

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `model_image` | bytes | model image | - | - | Yes |
| `bag_image` | bytes | bag image | - | - | No |
| `hat_image` | bytes | hat image | - | - | No |
| `shoes_image` | bytes | shoes image | - | - | No |
| `specs` | object | wearing specifications | - | - | No |

##### Body Parameters - specs

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

#### Example - Response 200 image/png

```json

```

---

## [레퍼런스] headswap

**POST** `/fashion/vton-headswap/v1/headswap`

### Description
Headswap을 수행하는 API

❗조건 및 제약 사항
* 주어진 이미지(image)의 크기가 (100, 100)보다 작은 경우 400 에러
* 주어진 이미지(image)의 크기가 (3500, 3500)보다 큰 경우 400 에러
* image에서 사람 얼굴을 찾을 수 없는 경우 400 에러

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters multipart/form-data

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `model_image` | bytes | Image of the person whose face you want to swap | - | - | Yes |
| `face_image` | bytes | Image of the target face to be applied | - | - | Yes |
| `headswap` | object | JSON string representing HEADSWAP options | `{"prompt": "", "generator_seed": null}` | - | No |

##### Body Parameters - headswap

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

#### Example - Response 200 image/png

```json

```

---

## [레퍼런스] generative-edit-eraser

**POST** `/fashion/edit/v1/eraser`

### Description
이미지 제품내 로고나 마크 등을 지우는 API

입력 이미지에서 mask 이미지 부분을 지웁니다.

#### Inputs
- `image` (_required_): 입력 이미지
- `mask_image` (_required_): 입력 mask 이미지

#### Output
- erased 결과 이미지: image bytes

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters multipart/form-data

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `image` | bytes | input image | - | - | Yes |
| `mask_image` | bytes | input mask image | - | - | Yes |

### Responses

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `400` | Bad Request |
| `422` | Validation Error |
| `500` | Internal Server Error |

#### Example - Response 200 image/png

```json

```

---

## [레퍼런스] generative-edit-inpaint

**POST** `/fashion/edit/v1/inpaint`

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

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters multipart/form-data

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

#### Example - Response 200 image/png

```json

```

---

## [레퍼런스] generative-edit-inpaint-image

**POST** `/fashion/edit/v1/inpaint-image`

### Description
이미지상 mask_image로 명시한 부분을 reference_image 및 reference_mask_image로 생성하여 합성하는 API

#### Inputs
- `image` (_required_): 입력 이미지
- `mask_image` (_required_): 입력 mask 이미지
- `reference_image` (_required_): 입력 reference 이미지
- `reference_mask_image` (_required_): 입력 reference mask 이미지

#### Output
- inpainting 결과 이미지: image bytes

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters multipart/form-data

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

#### Example - Response 200 image/png

```json

```

---

## [레퍼런스] generative-edit-texture

**POST** `/fashion/edit/v1/texture`

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

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters multipart/form-data

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

#### Example - Response 200 image/png

```json

```

---

## [레퍼런스] generative-edit-perspective

**POST** `/fashion/edit/v1/perspective`

### Description
이미지 상 제품의 시점을 변경 및 생성하는 API

#### Inputs
- `image` (_required_): 입력 이미지
- `view` (_required_): 생성되길 원하는 시점
- `prompt` (_optional_): 이미지 내 시점을 바꾸고 싶은 제품을 설명하는 프롬프트

#### Output
- 시점 변경 결과 이미지: image bytes

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters multipart/form-data

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `image` | bytes | input image | - | - | Yes |
| `view` | string | select perspective view to change | - | [`front`, `side`, `top`, `back`, `isometric`] | Yes |
| `prompt` | string | describe the object to change the view | - | - | No |

### Responses

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `400` | Bad Request |
| `422` | Validation Error |
| `500` | Internal Server Error |

#### Example - Response 200 image/png

```json

```

---

## [레퍼런스] generative-edit-graphic

**POST** `/fashion/edit/v1/graphic`

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

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters multipart/form-data

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

#### Example - Response 200 image/png

```json

```

---

## [레퍼런스] generative-edit-background

**POST** `/fashion/edit/v1/background`

### Description
전경 이미지에 새로운 배경 이미지를 합성하는 API

#### Inputs
- `mode` (_required_): 이미지 구성 형태
  * 사람 중심: `person`
  * 제품 중심: `product`
- `image` (_required_): 입력 이미지
  * 사전에 이미지에서 전경 이미지 및 배경 이미지를 분리 한 후 전경 이미지 + 배경을 회색 `(128, 128, 128)`으로 색칠한 이미지를 입력 이미지로 사용
- `prompt` (_optional_): 사용자 입력 프롬프트
- `background_prompt` (_optional_): 배경 설명 프롬프트
  * examples
    - "lush green forest, tall trees, fresh leaves, dense green"
    - "modern city street with tall glass buildings and clean sidewalks"
    - "plain indoor studio, white wall"
    - "minimal coffee shop interior, warm natural tones, stylish and cozy atmosphere"
- `season_prompt` (_optional_): 계절 설명 프롬프트
  * examples
    - "spring season"
    - "summer season"
    - "autumn season"
    - "winter season"
- `time_prompt` (_optional_): 시간 설명 프롬프트
  * examples
    - "bright daylight"
    - "night scene"
- `color_prompt` (_optional_): 색감 설명 프롬프트
  * examples
    - "soft, cozy, warm filter"
    - "cool vibe, high contrast"
    - "monochrome, grayscale tones, dramatic contrast"
- `lighting_prompt` (_optional_): 조명 설명 프롬프트
  * examples
    - "forest dappled sunlight, scattered natural spot highlights, organic shadow patterns, serene outdoor atmosphere"
    - "extremely strong front flash, harsh direct lighting, overexposed foreground, deep black background, sharp shadow edges, 1/200 shutter speed, f/18 aperture, ISO 100, point-and-shoot flash aesthetic, high-contrast exposure"
    - "soft light, diffused soft shadows, even illumination, minimal specular highlights, 1/160 shutter speed, f/8 aperture, ISO 100, clean studio aesthetic"
- `additional_prompt` (_optional_): 추가 설명 프롬프트
  * examples
    - "dynamic floating product photography"
- `output_aspect_ratio` (_required_): 결과 이미지 apsect ratio
- `output_image_size` (_required_): 결과 이미지 크기

#### Output
- synthesis 결과 이미지: image bytes

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters multipart/form-data

| Name | Type | Description | Default | Possible values | Required |
| --- | --- | --- | --- | --- | --- |
| `mode` | string | select mode | - | [`person`, `product`] | Yes |
| `image` | bytes | input image | - | - | Yes |
| `prompt` | string | user prompt | - | - | No |
| `background_prompt` | string | describe background | - | - | No |
| `season_prompt` | string | describe season | - | - | No |
| `time_prompt` | string | describe time | - | - | No |
| `color_prompt` | string | describe color | - | - | No |
| `lighting_prompt` | string | describe lighting | - | - | No |
| `additional_prompt` | string | additional prompt | - | - | No |
| `output_aspect_ratio` | string | output aspect ratio | `1:1` | [`1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`] | No |
| `output_image_size` | string | output image size | `2K` | [`1K`, `2K`, `4K`] | No |

### Responses

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `400` | Bad Request |
| `422` | Validation Error |
| `500` | Internal Server Error |

#### Example - Response 200 image/png

```json

```

---

## [레퍼런스] upscale

**POST** `/fashion/upscale/v1/super-resolution`

### Description
입력 이미지를 지정한 scale_factor 만큼 키우는 API입니다.

#### Inputs
- `image` (_required_): 입력 이미지 (input limit: 2048x2048)
- `scale_factor` (_optional_): 이미지 출력 크기 배수 (positive integer: 2 ~ 6, default: 4)

#### Output
- super-resolution 결과 이미지: image bytes

##### Header Parameters

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

##### Body Parameters multipart/form-data

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

#### Example - Response 200 image/png

```json

```
