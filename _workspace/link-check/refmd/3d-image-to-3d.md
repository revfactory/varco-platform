<p>
  <span style="background-color:#49cc90; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    POST
  </span>
  <span style="font-size:1.5em; font-weight:bold; margin-left:4px;">
    /3d/varco/v1/image-to-3d
  </span>
</p>

### Description

입력 이미지를 기반으로 3D 모델 생성 작업을 요청합니다.  
이 엔드포인트는 즉시 결과 파일을 반환하지 않고, `requestId`를 반환합니다.

<span style="font-weight:bold;">
  Header Parameters
</span>

| Name          | Type   | Description | Required |
| ------------- | ------ | ----------- | -------- |
| `openapi_key` | string | OpenAPI Key | Yes      |

<p>
  <span style="font-weight:bold;">
    Body Parameters
  </span>
  <span style="border:2px solid #77dd77; padding:4px 8px; border-radius:4px; color: #77dd77; display:inline-block; background-color:transparent; margin-left:4px;">
    multipart/form-data
  </span>
</p>

| Name               | Type    | Description                                                             | Default  | Possible values            | Required |
| ------------------ | ------- | ----------------------------------------------------------------------- | -------- | -------------------------- | -------- |
| `image`            | file    | 3D로 변환할 입력 이미지. PNG 형식만 지원합니다.                         | -        | PNG file                   | Yes      |
| `target_face_type` | string  | 생성할 메시의 face 타입.                                                | `tri`    | `tri`, `quad`              | No       |
| `target_face_num`  | integer | 생성할 메시의 face 개수.                                                | `300000` | `>= 1000` and `<= 300000` | No       |
| `generate_texture` | boolean | 텍스처 생성 여부. `false`이면 메시와 노말 맵만 포함된 결과를 생성합니다. | `true`   | `true`, `false`            | No       |
| `seed`             | integer | 랜덤 시드. `-1`이면 랜덤으로 설정됩니다.                               | `-1`     | -                          | No       |

### Responses

| Code  | Description           |
| ----- | --------------------- |
| `202` | Request Accepted      |
| `500` | Internal Server Error |

#### Response Example - `202 Request Accepted`
```json
{
  "requestId": "<request-id>",    
  "requestTime": "<request-time>",
  "message": "request accepted for async processing"
}
```

---
<p>
  <span style="background-color:#61affe; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    GET
  </span>
  <span style="font-size:1.5em; font-weight:bold; margin-left:4px;">
    /inference/result/{requestId}
  </span>
</p>

### Description

`requestId`로 작업 상태를 조회합니다.  
`status`가 `succeeded`일 때 작업이 완료되며, `model_url`에서 GLB 파일을 다운로드할 수 있습니다.  
`model_url`의 유효 기간은 7일입니다.

<span style="font-weight:bold;">
  Path Parameters
</span>

| Name        | Type   | Description            | Required |
| ----------- | ------ | ---------------------- | -------- |
| `requestId` | string | 생성 요청의 고유 식별자  | Yes      |

<span style="font-weight:bold;">
  Header Parameters
</span>

| Name          | Type   | Description | Required |
| ------------- | ------ | ----------- | -------- |
| `openapi_key` | string | OpenAPI Key | Yes      |

### Responses

| Code  | Description           |
| ----- | --------------------- |
| `202` | Processing            |
| `200` | Succeeded             |
| `500` | Failed                |

#### Response Example - `202 Processing`

```json
{
  "status": "processing"
}
```

#### Response Example - `200 Succeeded`

```json
{
  "status": "succeeded",
  "model_url": "https://3d.varco.ai/api/objects/<object-path>"
}
```

#### Response Example - `500 Failed`

```json
{
  "status": "failed"
}
```
