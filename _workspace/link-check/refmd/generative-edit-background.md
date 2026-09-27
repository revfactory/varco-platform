<p>
  <span style="background-color:#49cc90; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    POST
  </span>
  <span style="font-size:1.5em; font-weight:bold; margin-left:4px;">
    /fashion/edit/v1/background
  </span>
</P>

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
