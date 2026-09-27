<p>
  <span style="background-color:#49cc90; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    POST
  </span>
  <span style="font-size:1.5em; font-weight:bold; margin-left:4px;">
    /mt/chat-content/v1/translate
  </span>
</p>


### Description


### Translate API
* 용어집(Terminology)을 활용해 입력 텍스트를 번역하는 API


#### Inputs
- `TID`: Transaction ID
- `svc`: 서비스 코드
- `provider`: 호출 분류
- `source_lang`: 출발 언어 (e.g., 'ko', 'en', 'tw')
- `source_text`: 원문 텍스트 (e.g., "안녕하세요")
- `target_lang`: 도착 언어 (e.g., 'ko', 'en', 'tw')

#### output
- `TID`: Transaction ID
- `svc`: 서비스 코드
- `provider`: 호출 분류
- `source_lang`: 출발 언어 (e.g., 'ko', 'en', 'tw')
- `source_text`: 원문 텍스트 (e.g., "안녕하세요")
- `target_lang`: 도착 언어 (e.g., 'ko', 'en', 'tw')
- `target_text`: 번역 결과 (e.g., "Hello")

<br/>

<span style="font-weight:bold;">
  Header Parameters
</span>

| Name | Type | Description | Required |
| --- | --- | --- | --- |
| `openapi_key` | string | OpenAPI Key | Yes |

<br/>

<p>
  <span style="font-weight:bold;">
    Body Parameters
  </span>
  <span style="border:2px solid #77dd77; padding:4px 8px; border-radius:4px; color: #77dd77; display:inline-block; background-color:transparent; margin-left:4px;">
    application/json
  </span>
</p>

| Name | Type | Description | Default | Possible values | Required |
|---|---|---|---|---|---|
| `TID` | string | Transaction ID | - | | Yes |
| `svc` | string | 서비스 코드 | varco-translation | | Yes |
| `provider` | string | 호출 분류 | - | chat, content | No |
| `source_lang` | string | 입력 언어 | - | ko, en, ja, tw, cn, de, ru, es, pt, fr | No |
| `source_text` | string | 입력 텍스트 | - | 입력 텍스트 | Yes |
| `target_lang` | string | 출력 언어 | - | | Yes |

<br/>

### Responses
| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `401` | Unauthorized |
| `500` | Bad Request |

<br/>

### Request
<span style="font-size:1.5em; font-weight:bold;">
  Example - Request
</span>

```json
{
    "TID": "00000000-0000-0000-0000-00000000000",
    "svc": "varco-translation",
    "provider": "content",
    "source_lang": "en",
    "source_text": "lets eat lunch",
    "target_lang": "ko"
}
```
 
---

<br/>

### Response

<p>
  <span style="font-size:1.5em; font-weight:bold;">
    Example - Response
  </span>
  <span style="background-color: #49cc90; padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    200
  </span>
  <span style="border:2px solid #77dd77; padding:4px 8px; border-radius:4px; color: #77dd77; display:inline-block; background-color:transparent; margin-left:4px;">
    application/json
  </span>
</p>

```json
{
    "TID": "00000000-0000-0000-0000-00000000000",
    "target_lang": "ko",
    "source_lang": "en",
    "svc": "varco-translation",
    "provider": "content",
    "source_text": "lets eat lunch",
    "target_text": "점심 먹읍시다",
}
```

<br/>

<p>
  <span style="font-size:1.5em; font-weight:bold;">
    Example - Response
  </span>
  <span style="background-color:rgb(204, 73, 73); padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    401
  </span>
</p>

```json
{
    "message": "Unauthorized",
    "request_id": "eb7e214a7db6db54ef13fc6f2fa62f22"
}
```

<br/>

<p>
  <span style="font-size:1.5em; font-weight:bold;">
    Example - Response
  </span>
  <span style="background-color:rgb(204, 73, 73); padding:4px 8px; border-radius:4px; color:white; font-weight:bold; display:inline-block;">
    500
  </span>
</p>

```json
"call MT Controller failed"
```