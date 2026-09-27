Image to 3D API는 입력 이미지를 분석하여 3D 모델(GLB)을 생성합니다.  
생성 요청 시 즉시 `requestId`를 반환하며, `inference/result` 조회를 통해 완료 후 `model_url`을 받습니다.


## 주요 사양 및 설정

API 사용 시 고려해야 할 입출력 사양과 기술적 특성입니다.

| 구분               | 사양                    | 비고                          |
| :----------------- | :---------------------- | :---------------------------- |
| 입력 이미지 형식   | PNG                     | RGBA 지원                     |
| 출력 파일 형식     | GLB (glTF Binary)       | 메시 + 텍스처 (선택)          |
| 응답 방식          | 비동기 JSON             | `requestId` 반환 후 결과 조회 |
| 결과 URL 만료 시간 | 7일                     | 생성된 결과 URL의 유효 기간   |
| 출력 메시 타입     | Tri or Quad Face 선택   | UV Unwrap 기본 적용           |
| 리메시 범위        | 1,000 ~ 300,000         | 기본값 = 300,000 (Highpoly)   |
| 제공 텍스처 유형   | Diffuse Map, Normal Map | Normal Map 기본 제공          |
| 평균 소요 시간     | 2분 / 1분               | 텍스처 생성 포함 / 미포함     |



## 참고 사항

- **입력 이미지 품질**  
  피사체가 명확하고 배경이 단순한 단일 오브젝트 이미지를 권장합니다.

- **출력 파일 크기**  
  GLB 파일 크기는 폴리곤 수와 텍스처 해상도에 따라 달라지며 일반적으로 수 MB ~ 수십 MB입니다.

- **결과 URL 유효 기간**  
  `model_url`은 생성 시점부터 7일간 유효합니다.



## Sample Code - Curl
```bash
#!/bin/bash

REQUEST_ID=$(
  curl -sSLk \
    -H "OPENAPI_KEY: <OPENAPI_KEY>" \
    -F 'image=@"test-image.png"' \
    -F 'target_face_type=tri' \
    -F 'target_face_num=300000' \
    -F 'generate_texture=true' \
    -F 'seed=-1' \
    "https://openapi.ai.nc.com/3d/varco/v1/image-to-3d" \
  | jq -r '.requestId'
)

while true; do
  RESULT=$(
    curl -sSLk \
      -H "OPENAPI_KEY: <OPENAPI_KEY>" \
      "https://openapi.ai.nc.com/inference/result/${REQUEST_ID}"
  )
  STATUS=$(echo "$RESULT" | jq -r '.status')
  if [ "$STATUS" != "processing" ]; then
    break
  fi
  sleep 1
done

curl -sSLk "$(echo "$RESULT" | jq -r '.model_url')" -o model.glb
```


## Sample Code - Python

```python
import time
import requests

headers = {"OPENAPI_KEY": "<OPENAPI_KEY>"}

with open("test-image.png", "rb") as f:
    response = requests.post(
        "https://openapi.ai.nc.com/3d/varco/v1/image-to-3d",
        headers=headers,
        files={"image": f},
        data={
            "target_face_type": "tri",      # tri or quad
            "target_face_num": 300000,      # 1000 ~ 300000
            "generate_texture": "true",     # true / false
            "seed": -1                      # -1 = random
        },
    ).json()

request_id = response["requestId"]

while True:
    result = requests.get(
        f"https://openapi.ai.nc.com/inference/result/{request_id}",
        headers=headers,
    ).json()

    if result["status"] != "processing":
        break

    time.sleep(1)

model = requests.get(result["model_url"])

with open("model.glb", "wb") as f:
    f.write(model.content)
```

## Sample Code - Javascript

```javascript
const fs = require("fs");
const axios = require("axios");
const FormData = require("form-data");

async function main() {
  const form = new FormData();

  form.append("image", fs.createReadStream("test-image.png"));

  // default parameters
  form.append("target_face_type", "tri");      // tri or quad
  form.append("target_face_num", "300000");    // 1000 ~ 300000
  form.append("generate_texture", "true");     // true / false
  form.append("seed", "-1");                   // -1 = random

  const upload = await axios.post(
    "https://openapi.ai.nc.com/3d/varco/v1/image-to-3d",
    form,
    {
      headers: {
        ...form.getHeaders(),
        OPENAPI_KEY: "<OPENAPI_KEY>",
      },
    }
  );

  const requestId = upload.data.requestId;
  let result;

  while (true) {
    const res = await axios.get(
      `https://openapi.ai.nc.com/inference/result/${requestId}`,
      { headers: { OPENAPI_KEY: "<OPENAPI_KEY>" } }
    );

    result = res.data;

    if (result.status !== "processing") break;

    await new Promise((r) => setTimeout(r, 1000));
  }

  const model = await axios.get(result.model_url, {
    responseType: "arraybuffer",
  });

  fs.writeFileSync("model.glb", Buffer.from(model.data));
}

main();
```

---

<!--
## 가격 정책

| 서비스 | 과금 단위 | 기본 단가 |
| :--- | :--- | :--- |
| Image to 3D (텍스처 포함) | 호출당 | 200 크레딧 |
| Image to 3D (메시만) | 호출당 | 100 크레딧 |
-->