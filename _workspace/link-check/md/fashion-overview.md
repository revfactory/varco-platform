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

<!-- ### API 서비스 별 가격 표
API 서비스별로 최적화된 과금 단위를 제공합니다. 사용자는 필요한 기능만
선택해 사용할 수 있으며, 각 API의 사용량에 따라 명확하고 일관된 요금이
산정됩니다.\
모든 요금은 1회 호출 단가 기준으로 계산되며, 사용량은 대시보드에서
확인할 수 있습니다.

| Category | Service | 과금 단위 | 기본 단가 | 호출에 필요한 최소 크레딧 |
|--------|--------|----------|----------|----------------|
| Image | Virtual Try On | 출력 Pixel 크기 | 1메가픽셀 / 75크레딧 | 75 |
| Image | Virtual Try On for Accessories | 출력 Pixel 크기 | 1메가픽셀 / 120크레딧 | 120 |
| Image | Headswap | 출력 Pixel 크기 | 1메가픽셀 / 16크레딧 | 16 |
| Image | Eraser | 출력 Pixel 크기 | 1메가픽셀 / 30크레딧 | 30 |
| Image | Inpaint (text) | 출력 Pixel 크기 | 1메가픽셀 / 120크레딧 | 120 |
| Image | Inpaint (image) | 출력 Pixel 크기 | 1메가픽셀 / 120크레딧 | 120 |
| Image | Texture | 출력 Pixel 크기 | 1메가픽셀 / 120크레딧 | 120 |
| Image | Perspective | 출력 Pixel 크기 | 1메가픽셀 / 30크레딧 | 30 |
| Image | Graphic | 출력 Pixel 크기 | 1메가픽셀 / 30크레딧 | 30 |
| Image | Background | 출력 Pixel 크기 | 해상도 1K, 2K: 120<br>해상도 4K: 215 | 120 |
| Image | Upscale | 출력 Pixel 크기 | ≤ 4MP: 50<br>≤ 8MP: 100<br>≤ 16MP: 200<br>≤ 25MP: 400<br>≤ 50MP: 800<br>≤ 100MP: 1,600<br>≤ 200MP: 3,200 | 50 |

*자세한 기술 명세와 파라미터는 각 서비스별 상세 페이지를 참고하세요.* -->
