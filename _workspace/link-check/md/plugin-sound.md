## VARCO Sound 플러그인

### 상상이 들리는 순간, 아이디어로 완성하는 프로 사운드

Unity, Unreal, VST, AAX 환경에서 사운드를 생성하고 바로 사용할 수 있습니다. 더 이상 SFX 라이브러리를 찾을 필요가 없습니다.
<br>

### 지원 환경
| Engine | Version | Download |
|:---|:---|:---|
| Unity | 2021.3+ | [![Unitypackage](https://img.shields.io/badge/Unitypackage-1a73e8?style=for-the-badge)](https://cdn.varco.ai/bin/sound/260724/varcosound-1.0.1-direct.unitypackage) |
| Unreal | 5.5 · 5.6 · 5.7 | [![UnrealCPP](https://img.shields.io/badge/C++-1a73e8?style=for-the-badge)](https://cdn.varco.ai/bin/sound/260212/VarcoSound_v0.1.3_UE5.x_Win64_Source.zip) [![Unreal5.5](https://img.shields.io/badge/5.5_dll-1a73e8?style=for-the-badge)](https://cdn.varco.ai/bin/sound/260212/VarcoSound_v0.1.3_UE5.5_Win64.zip) [![Unreal5.6](https://img.shields.io/badge/5.6_dll-1a73e8?style=for-the-badge)](https://cdn.varco.ai/bin/sound/260212/VarcoSound_v0.1.3_UE5.6_Win64.zip) [![Unreal5.7](https://img.shields.io/badge/5.7_dll-1a73e8?style=for-the-badge)](https://cdn.varco.ai/bin/sound/260212/VarcoSound_v0.1.3_UE5.7_Win64.zip) |
| VST3 | | [![VST-Win](https://img.shields.io/badge/VST3(win)-1a73e8?style=for-the-badge)](https://cdn.varco.ai/bin/sound/260224/VARCO%20Sound%20VST.exe) [![VST-Mac](https://img.shields.io/badge/VST3(Mac)-1a73e8?style=for-the-badge)](https://cdn.varco.ai/bin/sound/260224/VARCO%20Sound-vst3-v0.1.3.pkg) |
| AAX | | [![AAX-Win](https://img.shields.io/badge/AAX(Win)-1a73e8?style=for-the-badge)](https://cdn.varco.ai/bin/sound/260224/VARCO%20Sound%20AAX.exe) [![AAX-Mac](https://img.shields.io/badge/AAX(Mac)-1a73e8?style=for-the-badge)](https://cdn.varco.ai/bin/sound/260224/VARCO%20Sound-aaxplugin-v0.1.3.pkg) |

<br>

### 주요 기능 및 API
* **사운드 생성**: 텍스트 프롬프트나 게임 씬 이미지를 기반으로 원하는 사운드를 즉시 생성할 수 있습니다.
* **변형 사운드 생성**: 반복되는 게임 액션이나 환경 효과에 적합한 다양한 사운드 변형을 빠르게 생성할 수 있습니다.
* **자동 루핑**: 별도의 편집 지식 없이도 자연스럽게 무한 반복 가능한 루프 사운드를 만들 수 있습니다.
* **음성 변환**: 음성을 녹음하고 원하는 톤을 선택하여 몬스터 보이스로 손쉽게 변환할 수 있습니다.
* **음악 생성**: 텍스트 또는 이미지를 기반으로 배경 음악이나 테마 음악을 생성할 수 있습니다.

<br>

### Unity 플러그인 설치
1. `.unitypackage` 파일을 다운로드합니다.
2. 프로젝트에서 패키지를 임포트합니다.
    * `Assets` 우클릭 → `Import Package` → `Custom Package...` 
    ![import](https://cdn-api.varco.ai/document/6a5040c09913485d8a8aa8b45931a6e3.jpg)
3. `Window > VARCO Sound` 메뉴에서 실행합니다.
    ![launch](https://cdn-api.varco.ai/document/99584144dd53439ca2689ad82acf56f4.jpg)  
<br><br>
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

<br>

### VST 플러그인 설치
1. `VST3` 파일을 다운로드합니다.
2. VST3 플러그인 형식을 지원하는 DAW를 실행합니다.
3. 인스트루먼트 트랙을 생성한 뒤, 해당 트랙에 **VARCO Sound** 플러그인을 인스트루먼트로 로드합니다.
    * **REAPER**처럼 전용 인스트루먼트 트랙 타입이 없는 DAW에서는 일반 트랙을 생성한 뒤 FX 체인에서 VARCO Sound를 로드해 주세요.
    * REAPER에서 공백 입력이 되지 않는 경우, FX 설정에서 **Send all keyboard input to plug-in** 옵션을 활성화해 주세요.

<br>

### AAX 플러그인 설치
1. `AAX` 파일을 다운로드합니다.
2. AAX 플러그인 형식을 지원하는 DAW를 실행합니다.
3. 인스트루먼트 트랙을 생성한 뒤, 해당 트랙에 **VARCO Sound** 플러그인을 인스트루먼트로 로드합니다.


<br>

### FAQ

**Q1. 상업적 프로젝트에 사용할 수 있나요?**
가능합니다. 생성된 사운드는 상업적 프로젝트에 사용할 수 있으며, 자세한 내용은 [이용약관](https://terms.varco.ai/2950435c2d75802584f9ea2807167283)을 확인하고 준수해 주세요.

**Q2. 인터넷 연결이 필요한가요?**
필요합니다. 사운드 생성은 온라인 API 호출을 통해 이루어지므로 사용 중 인터넷 연결이 필요합니다.

<br>

### 문의

도움이 필요하거나 궁금한 점이 있다면 언제든지 [문의](mailto:audioai@ncsoft.com)해 주세요. 또는 [피드백](https://forms.gle/triRfsxgotKr8MsWA)을 남겨주세요.

---

**공지:** 상업적 이익을 위한 무단 수정 및 재배포는 금지되어 있습니다.

