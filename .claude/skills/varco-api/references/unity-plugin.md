# VARCO Sound Unity 플러그인
> 원문: api.varco.ai 문서(2026-09 수집). 가이드와 레퍼런스가 다르면 **레퍼런스를 기준으로 한다** (공식 안내: "엔드포인트 별 최신 버전은 항상 API Reference 페이지를 기준으로 확인").

---

# 제1부. 가이드

---

## [가이드] plugin-sound

## VARCO Sound 플러그인

### 상상이 들리는 순간, 아이디어로 완성하는 프로 사운드

Unity, Unreal, VST, AAX 환경에서 사운드를 생성하고 바로 사용할 수 있습니다. 더 이상 SFX 라이브러리를 찾을 필요가 없습니다.

### 지원 환경
| Engine | Version | Download |
|:---|:---|:---|
| Unity | 2021.3+ | [![Unitypackage](https://img.shields.io/badge/Unitypackage-1a73e8?style=for-the-badge)](https://cdn.varco.ai/bin/sound/260724/varcosound-1.0.1-direct.unitypackage) |
| Unreal | 5.5 · 5.6 · 5.7 | [![UnrealCPP](https://img.shields.io/badge/C++-1a73e8?style=for-the-badge)](https://cdn.varco.ai/bin/sound/260212/VarcoSound_v0.1.3_UE5.x_Win64_Source.zip) [![Unreal5.5](https://img.shields.io/badge/5.5_dll-1a73e8?style=for-the-badge)](https://cdn.varco.ai/bin/sound/260212/VarcoSound_v0.1.3_UE5.5_Win64.zip) [![Unreal5.6](https://img.shields.io/badge/5.6_dll-1a73e8?style=for-the-badge)](https://cdn.varco.ai/bin/sound/260212/VarcoSound_v0.1.3_UE5.6_Win64.zip) [![Unreal5.7](https://img.shields.io/badge/5.7_dll-1a73e8?style=for-the-badge)](https://cdn.varco.ai/bin/sound/260212/VarcoSound_v0.1.3_UE5.7_Win64.zip) |
| VST3 | | [![VST-Win](https://img.shields.io/badge/VST3(win)-1a73e8?style=for-the-badge)](https://cdn.varco.ai/bin/sound/260224/VARCO%20Sound%20VST.exe) [![VST-Mac](https://img.shields.io/badge/VST3(Mac)-1a73e8?style=for-the-badge)](https://cdn.varco.ai/bin/sound/260224/VARCO%20Sound-vst3-v0.1.3.pkg) |
| AAX | | [![AAX-Win](https://img.shields.io/badge/AAX(Win)-1a73e8?style=for-the-badge)](https://cdn.varco.ai/bin/sound/260224/VARCO%20Sound%20AAX.exe) [![AAX-Mac](https://img.shields.io/badge/AAX(Mac)-1a73e8?style=for-the-badge)](https://cdn.varco.ai/bin/sound/260224/VARCO%20Sound-aaxplugin-v0.1.3.pkg) |

### 주요 기능 및 API
* **사운드 생성**: 텍스트 프롬프트나 게임 씬 이미지를 기반으로 원하는 사운드를 즉시 생성할 수 있습니다.
* **변형 사운드 생성**: 반복되는 게임 액션이나 환경 효과에 적합한 다양한 사운드 변형을 빠르게 생성할 수 있습니다.
* **자동 루핑**: 별도의 편집 지식 없이도 자연스럽게 무한 반복 가능한 루프 사운드를 만들 수 있습니다.
* **음성 변환**: 음성을 녹음하고 원하는 톤을 선택하여 몬스터 보이스로 손쉽게 변환할 수 있습니다.
* **음악 생성**: 텍스트 또는 이미지를 기반으로 배경 음악이나 테마 음악을 생성할 수 있습니다.

### Unity 플러그인 설치
1. `.unitypackage` 파일을 다운로드합니다.
2. 프로젝트에서 패키지를 임포트합니다.
    * `Assets` 우클릭 → `Import Package` → `Custom Package...` 
    ![import](https://cdn-api.varco.ai/document/6a5040c09913485d8a8aa8b45931a6e3.jpg)
3. `Window > VARCO Sound` 메뉴에서 실행합니다.
    ![launch](https://cdn-api.varco.ai/document/99584144dd53439ca2689ad82acf56f4.jpg)  

### Unreal 플러그인 설치

플러그인 버전에 따라 아래 설치 방법 중 하나를 선택해 주세요.

#### 옵션 A: 일반 설치 (사전 빌드된 DLL 바이너리, Windows 전용)
이 방식은 사전 빌드된 플러그인 바이너리를 엔진에 직접 설치하고 사용할 수 있습니다.

1. DLL `.zip` 파일을 다운로드하고 압축을 해제합니다.
2. 압축을 해제한 폴더(예: `VarcoSound_vx.x.x_UE5.x_Win64`)를 아래 경로에 복사합니다.
   > `Plugins` 아래에 `Marketplace` 폴더가 없는 경우 직접 생성해 주세요.
   ```
   C:\Program Files\Epic Games\UE_5.x\Engine\Plugins\Marketplace
   ```
3. Unreal Editor에서 `Edit → Plugins`로 이동한 뒤 **VARCO Sound**를 검색하고 활성화합니다.
![unreal](https://cdn-api.varco.ai/document/2779d4edede14620a09c2b9f8382882d.jpg)
4. 변경 사항을 적용하려면 Unreal Engine을 재시작합니다.

---

#### 옵션 B: 소스 코드 빌드 (수동 빌드)
이 방식은 소스 코드가 포함된 플러그인을 다운로드한 뒤, 프로젝트 내에서 직접 빌드하여 사용하는 방법입니다.

1. 소스 코드 버전 `.zip` 파일을 다운로드하고 압축을 해제합니다.
2. 압축을 해제한 폴더를 프로젝트의 `Plugins` 디렉토리에 복사합니다.
    > `Plugins` 폴더가 없는 경우 프로젝트 루트에 직접 생성해 주세요.
    ```
    YourProject/Plugins/
    ```
3. 프로젝트 파일을 생성합니다.
- 프로젝트 폴더에서 `.uproject` 파일을 우클릭합니다.
- **Generate Visual Studio project files**를 선택합니다.

4. 빌드하고 실행합니다.
- 프로젝트(`.sln`)를 엽니다.
- *"The following modules are missing or built with a different engine version... Would you like to rebuild them now?"* 메시지가 표시되면 **Yes**를 클릭합니다.
- 빌드가 완료되고 에디터가 실행될 때까지 기다립니다.

### VST 플러그인 설치
1. `VST3` 파일을 다운로드합니다.
2. VST3 플러그인 형식을 지원하는 DAW를 실행합니다.
3. 인스트루먼트 트랙을 생성한 뒤, 해당 트랙에 **VARCO Sound** 플러그인을 인스트루먼트로 로드합니다.
    * **REAPER**처럼 전용 인스트루먼트 트랙 타입이 없는 DAW에서는 일반 트랙을 생성한 뒤 FX 체인에서 VARCO Sound를 로드해 주세요.
    * REAPER에서 공백 입력이 되지 않는 경우, FX 설정에서 **Send all keyboard input to plug-in** 옵션을 활성화해 주세요.

### AAX 플러그인 설치
1. `AAX` 파일을 다운로드합니다.
2. AAX 플러그인 형식을 지원하는 DAW를 실행합니다.
3. 인스트루먼트 트랙을 생성한 뒤, 해당 트랙에 **VARCO Sound** 플러그인을 인스트루먼트로 로드합니다.

### FAQ

**Q1. 상업적 프로젝트에 사용할 수 있나요?**
가능합니다. 생성된 사운드는 상업적 프로젝트에 사용할 수 있으며, 자세한 내용은 [이용약관](https://terms.varco.ai/2950435c2d75802584f9ea2807167283)을 확인하고 준수해 주세요.

**Q2. 인터넷 연결이 필요한가요?**
필요합니다. 사운드 생성은 온라인 API 호출을 통해 이루어지므로 사용 중 인터넷 연결이 필요합니다.

### 문의

도움이 필요하거나 궁금한 점이 있다면 언제든지 [문의](mailto:audioai@ncsoft.com)해 주세요. 또는 [피드백](https://forms.gle/triRfsxgotKr8MsWA)을 남겨주세요.

---

**공지:** 상업적 이익을 위한 무단 수정 및 재배포는 금지되어 있습니다.

---

## [가이드] plugin-sound-unity

# VARCO Sound for Unity

VARCO Sound는 AI 오디오 제작을 Unity 에디터 안으로 가져옵니다. 사운드 라이브러리를 찾거나 외부 툴을 오갈 필요 없이, 필요한 소리를 설명하면 프로젝트를 벗어나지 않고 바로 생성할 수 있습니다. 효과음, 배경 음악, 크리처 보이스, 음성 대사까지 한 창에서 만들고, 생성한 결과는 곧바로 씬에 가져다 쓸 수 있습니다.

이 가이드에서는 플러그인 설치, 첫 사운드 생성, 그리고 각 도구의 기능을 다룹니다.

[![Unitypackage v1.0.1](https://img.shields.io/badge/Unitypackage_v1.0.1-1a73e8?style=for-the-badge&logo=unity&logoColor=white)](https://cdn.varco.ai/bin/sound/260724/varcosound-1.0.1-direct.unitypackage)

---

## 호환성 (Compatibility)

VARCO Sound는 Unity 에디터 안에서 동작하며, 아래 버전과 플랫폼을 지원합니다.

- **버전:** 2021.3 LTS, 2022.3 LTS, Unity 6 (6000.x)
- **플랫폼:** Windows, macOS (에디터)

오디오는 서버에서 생성되므로, 프로젝트의 렌더 파이프라인과 관계없이 동일하게 동작합니다.

### 사용에 필요한 것

- **인터넷 연결** — 사운드는 온라인 API 호출로 생성되므로, 작업 중에는 플러그인이 온라인 상태여야 합니다.
- **VARCO Sound API 키** — VARCO 계정에서 발급합니다. 발급 방법은 다음 섹션에서 안내합니다.

VARCO Sound는 에디터에서 작업할 때 사용하는 도구입니다. 게임을 만드는 동안 오디오를 생성하고 다듬은 뒤, 완성된 클립을 여느 에셋처럼 빌드에 포함하면 됩니다. 실시간(런타임) 생성은 지원하지 않습니다.

---

## 설치

### 1. 패키지 임포트

`.unitypackage` 파일을 다운로드한 뒤, Unity에서 **Assets → Import Package → Custom Package…** 로 이동해 파일을 선택하고 내용을 임포트합니다.

![import](https://cdn-api.varco.ai/document/a9e4ca61336f498d8dc0bd40b40f33a8.jpg)

### 2. 창 열기

메뉴 바의 **Window ▸ VARCO Sound** 에서 플러그인을 엽니다. 다른 에디터 창처럼 자유롭게 도킹할 수 있습니다.

![import](https://cdn-api.varco.ai/document/b7710ac4aa384330b247abd25e9d4de7.jpg)

### 3. API 키 연결

VARCO Sound를 처음 열면 첫 화면에서 API 키를 입력하라는 안내가 나타납니다.

1. **Get API Key** 를 클릭하면 브라우저에서 VARCO API 페이지가 열립니다.
2. 페이지에서 키를 발급해 복사합니다.
3. 복사한 키를 플러그인에 붙여넣습니다.

키는 이후 설정(⚙️) 메뉴에서 언제든 변경할 수 있으며, 같은 메뉴에서 현재 크레딧 잔액도 확인할 수 있습니다.

![VARCO Sound welcome](https://cdn-api.varco.ai/document/e1f52e008136482c83ae4823b57ba3e9.png)

---

## 시작하기 (Getting started)

VARCO Sound 창은 **Sound, Variation, Loop, Creature, Music, Voice** 여섯 개 탭과 오른쪽 위의 정보(ⓘ)·설정(⚙️) 버튼으로 구성됩니다.

![import](https://cdn-api.varco.ai/document/0c03706547e9407f94aa4c5df3a0dc4e.png)

아이디어를 씬 속 클립으로 만드는 가장 빠른 흐름은 다음과 같습니다.

1. **Sound** 탭을 열고 원하는 소리를 입력합니다 — 예: *"footsteps on wet gravel"*.
2. **Generate** 를 누릅니다. 잠시 후 후보 몇 개가 생성됩니다.
3. 결과를 미리 들어보고, 마음에 드는 것을 두 가지 방법 중 하나로 프로젝트에 가져옵니다.
   - **Save** 로 프로젝트에 `.wav` 파일로 저장하거나,
   - 씬의 Audio Source로 **드래그** 하면 클립이 저장되면서 동시에 할당됩니다.

**Save** 를 클릭하면 클립은 기본 저장 폴더(`Assets/VARCOSound/Generated`)에 저장됩니다. Save 옆 화살표를 눌러 **Save to…** 를 선택하면 파일 탐색기로 위치를 직접 지정해 저장할 수 있습니다. 기본 폴더는 설정 메뉴에서 언제든 바꿀 수 있습니다.

![import](https://cdn-api.varco.ai/document/30e5fbaaaaa74da29d09a4daa735069f.png)

여기서부터는 **도구 살펴보기** 에서 각 탭의 기능을, **예시** 에서 도구들이 실제 작업에서 어떻게 어우러지는지 확인할 수 있습니다.

---

## 도구 살펴보기

VARCO Sound는 각각 한 가지 오디오 작업을 담당하는 여섯 개 탭과, 어느 파형에서든 열 수 있는 오디오 에디터로 이뤄집니다.

### Sound — 설명으로 효과음 생성

소리를 설명하면 VARCO Sound가 여러 후보를 생성해 고를 수 있게 해줍니다. 한 번에 몇 개를 만들지, 스테레오로 출력할지 모노로 출력할지 선택할 수 있습니다.

프롬프트 옆에는 두 가지 도우미가 있습니다.

- **Improve Prompt** — 입력한 설명을 모델이 더 잘 처리할 수 있는 형태로 다듬어 줍니다. 영어 외의 언어로 프롬프트를 작성할 때도 이 기능을 사용합니다.
- **Suggest from Image** — 참조 이미지를 보고 그 장면에 어울리는 소리를 추천합니다. 만들고 있는 화면의 스크린샷을 주면 필요한 소리들의 프롬프트를 제안해 줍니다.

|  |  |
|---|---|
| ![Improve Prompt](https://cdn-api.varco.ai/document/aaa96c3d29384e3cb421401462e9e3af.png)
Improve Prompt | ![Suggest from Image](https://cdn-api.varco.ai/document/3f6208d95a1440deb42fbf97a172a5e7.png)
Suggest from Image |

> **이미지 선택 방법.** VARCO Sound가 이미지를 입력받는 곳이라면 어디서든 — Sound 탭의 Suggest from Image든, Music 탭의 참조 이미지든 — 네 가지 방법으로 이미지를 가져올 수 있습니다. **Scene View** 캡처, 프로젝트의 이미지를 고르는 **Select Asset**, 디스크의 파일을 불러오는 **Load Image**, 씬의 카메라 화면을 가져오는 **Select Camera** 입니다.

### Variation — 같은 소리의 다른 테이크

같은 발소리나 검 휘두르는 소리가 매번 똑같이 반복되면 금방 티가 납니다. Variation에 클립을 주면 원본의 느낌은 유지하면서 세부가 조금씩 다른 테이크들을 만들어 줍니다. 강도를 낮추면 미세하게, 높이면 더 크게 달라지며, 필요한 만큼 생성할 수 있습니다.

기본적으로는 클립 전체가 변형됩니다. 일부는 그대로 두고 특정 구간만 바꾸고 싶다면 — 예를 들어 소리의 어택은 그대로 두고 뒷부분만 바꾸고 싶다면 — 파형에서 그 구간만 선택하면 됩니다.

![import](https://cdn-api.varco.ai/document/cde6f27e799a4d2cb7dfb322ecfd4f11.png)

### Loop — 끊김 없는 환경음

바람, 비, 룸 톤 같은 환경음은 이음매가 들리지 않게 반복돼야 합니다. Loop에 클립을 주면 원하는 길이만큼 매끄럽게 반복되는 버전을 만들어 줍니다.

깔끔한 루프 지점을 찾기 위해, 도구가 반복 구간에 맞지 않는 부분을 덜어낼 수 있습니다. 반드시 남아야 하는 부분이 있다면 파형에서 보존 구간으로 선택해 두면, Loop가 그 부분을 유지하면서 작업합니다.

![import](https://cdn-api.varco.ai/document/3ea155e1d57e4cbba636350f9491381e.png)

### Creature — 목소리를 몬스터 소리로

직접 녹음하거나 클립을 불러온 뒤, Creature가 참조 클립으로 정한 대상 — 드래곤, 오크, 고블린 등 — 의 음색으로 목소리를 바꿔 줍니다. 변환은 원본 녹음을 따라가므로, 무엇을 어떤 호흡으로 말했는지는 그대로 유지되고 음색만 바뀝니다. 변환 강도는 살짝만 입히는 수준부터 완전한 변형까지 조절할 수 있습니다.

녹음의 일부만 변환하고 싶다면 소스 파형에서 그 구간을 선택하면 됩니다 — 선택한 구간만 변환됩니다.

![import](https://cdn-api.varco.ai/document/8d61956309de404481d5a49af57fd7df.png)

### Music — 텍스트나 이미지로 만드는 음악

분위기, 장르, 장면을 설명하거나 톤을 정할 참조 이미지를 제공해 배경·테마 음악을 생성합니다. 프롬프트만, 이미지만, 또는 둘 다 사용할 수 있습니다. 만들고 있는 장면의 스크린샷을 넣으면 화면에 어울리는 음악을 빠르게 얻을 수 있습니다.

![import](https://cdn-api.varco.ai/document/696bd91063ea42488181a6c36264e04c.png)

### Voice — 텍스트로 만드는 음성 대사

대사를 입력하고 화자를 고르면 Voice가 음성을 합성합니다 — 대사, 내레이션, 보이스오버에 두루 쓸 수 있습니다. 한국어, 영어, 일본어, 중국어를 지원하며, 캐릭터에 맞게 말속도와 음높이를 조절할 수 있습니다. Standard 모드에서는 시드(seed)를 고정할 수 있어, 같은 문장이 매번 같은 결과로 생성됩니다.

![import](https://cdn-api.varco.ai/document/e9cd9f36e4f740f588189c81f8e7d603.png)

### 오디오 에디터

모든 파형의 오른쪽 위에는 **Edit Audio** 버튼이 있어, 클릭하면 전용 편집 창이 열립니다. 간단한 수정을 위해 별도의 DAW를 오갈 필요가 없습니다. 클립을 자르고 다듬거나, 무음을 정리하거나, 게인을 조절하고 레벨을 노멀라이즈하거나, 페이드를 넣거나, 역재생하거나, 모노로 변환할 수 있으며, 작업 중에 원본과 비교하며 들어볼 수 있습니다.

작업을 마치면 **Apply** 는 편집한 오디오를 파일로 저장하지 않고 원래 탭으로 되돌려 보내고, **Save** (또는 **Save to…**)는 새 `.wav` 파일로 디스크에 저장합니다.

![import](https://cdn-api.varco.ai/document/656f9db4be0b47d69486a83332462b0d.png)
오디오 에디터 버튼

![import](https://cdn-api.varco.ai/document/58d2e9e6c8f1402baae5fd7b3f48a9ef.png)
오디오 에디터 창

### 설정 (Settings)

설정(⚙️) 메뉴에서는 API 키를 관리하고, 남은 크레딧을 확인하고, 생성된 오디오의 저장 위치를 지정할 수 있습니다. 각 탭이 보관하는 최근 결과 개수를 제한하거나, 문제 해결을 위한 상세 로깅을 켜거나, 모든 설정을 기본값으로 초기화할 수도 있습니다 — 이때 API 키는 유지됩니다.

![import](https://cdn-api.varco.ai/document/cb7b709e44824ca8bbf6db4e940297da.png)

---

## 예시

도구들을 엮어 처음부터 끝까지 이어지는 작업 흐름 몇 가지입니다.

### 발소리를 Variation으로 발전시키기

시작하기에서 발소리 하나를 생성했습니다. 반복될 때 기계적으로 들리지 않도록, 결과에서 **Send to Variation** 을 클릭하면 클립이 이미 로드된 채로 Variation 탭이 열립니다. 다른 테이크 몇 개를 생성해 무작위로 재생하면, 걷는 동작의 소리가 더 이상 똑같이 반복되지 않습니다.

|  |  |
|---|---|
| ![Send to Variation](https://cdn-api.varco.ai/document/4855a86942b248c0bd7218a594abcdf4.png)
1. Send to Variation | ![Variation tab loaded](https://cdn-api.varco.ai/document/2233dd9c8f6042008033e41140e6f01f.png)
2. 클립이 Variation 탭에 로드되어 다른 테이크를 생성할 준비가 된 상태 |

### 반복되는 배경 환경음 만들기

레벨에는 그 뒤를 채우는 지속적인 분위기가 필요합니다 — 나무 사이를 스치는 바람, 멀리 내리는 비, 기계실의 웅웅거림처럼요. *"Rustling leaves and distant animal calls in a jungle"* 같은 기본 환경음을 생성하거나 불러온 뒤, 결과에서 **Send to Loop** 를 클릭해 Loop 탭으로 가져옵니다. 끊김 없는 버전을 생성해 반복 재생되는 Audio Source에 올리면, 이음매 없이 이어지는 배경 분위기가 씬에 깔립니다.

|  |  |
|---|---|
| ![Send to Loop](https://cdn-api.varco.ai/document/5bed011d0ec24d4f89da867ff897a4c9.png)
1. Send to Loop | ![Loop tab loaded](https://cdn-api.varco.ai/document/bb3206774a7a4a53a24bc851d68181ab.png)
2. 클립이 Loop 탭에 로드되어 끊김 없는 루프를 생성할 준비가 된 상태 |

### 내 연기로 몬스터 목소리 만들기

**Sound** 에서 기본 몬스터 소리 — *"low guttural monster growl"* — 를 생성해 저장합니다. **Creature** 탭을 열고 그 클립을 **Creature Reference** 로 지정합니다. 그런 다음 대사를 직접 연기해 **Source Audio** 로 녹음합니다 — 여러분이 말한 대사와 그 연기가 크리처에게 그대로 이어집니다.

|  |  |
|---|---|
| ![Creature base generation](https://cdn-api.varco.ai/document/6d404f511ef64ac2a90a0cb5bfcc9787.png)
1. Sound 탭에서 기본 몬스터 소리를 생성해 저장 | ![Creature reference set](https://cdn-api.varco.ai/document/cddf3c96f8b341cfbf285b5ebd1f7267.png)
2. 저장한 소리를 Creature Reference로 지정 |
| ![Creature source recording](https://cdn-api.varco.ai/document/b8b08a16b23b425baef1e3ec70c701bf.png)
3. 직접 연기한 음성을 Source Audio로 녹음 | ![Creature converted result](https://cdn-api.varco.ai/document/6333a82488504cfb8029cd5d61648a83.png)
4. 변환하면 몬스터의 목소리로 돌아온 내 연기 |
