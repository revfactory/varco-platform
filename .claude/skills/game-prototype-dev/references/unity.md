# Unity 6 프로토타입 구현 참고

에디터를 띄우지 않고 배치 모드 명령으로 프로젝트를 만들고, 컴파일하고, 테스트하고, 빌드한다. 에이전트는 에디터 화면을 볼 수 없으므로 모든 확인을 로그와 테스트 결과 파일로 한다.

## 목차

1. [실행 파일과 버전](#1-실행-파일과-버전)
2. [프로젝트 만들기](#2-프로젝트-만들기)
3. [폴더 구조와 에셋 복사](#3-폴더-구조와-에셋-복사)
4. [패키지](#4-패키지)
5. [데이터 로더](#5-데이터-로더)
6. [오디오·대사·얼굴 애니메이션](#6-오디오대사얼굴-애니메이션)
7. [QA 훅](#7-qa-훅)
8. [테스트](#8-테스트)
9. [컴파일 확인과 빌드](#9-컴파일-확인과-빌드)
10. [VARCO Sound Unity 플러그인](#10-varco-sound-unity-플러그인)

---

## 1. 실행 파일과 버전

설치된 버전은 실행할 때마다 확인한다. 2026-09 기준 이 PC 에는 `6000.0.84f1` 하나가 있고, 빌드 대상은 macOS 독립 실행(MacStandaloneSupport)만 설치돼 있다. WebGL·Android 빌드가 필요하면 사용자가 Unity Hub 에서 모듈을 설치해야 하므로 리더에게 알린다.

```bash
ls /Applications/Unity/Hub/Editor
U="/Applications/Unity/Hub/Editor/$(ls /Applications/Unity/Hub/Editor | sort -V | tail -1)/Unity.app/Contents/MacOS/Unity"
ls "$(dirname "$U")/../PlaybackEngines"      # 설치된 빌드 대상
```

모든 명령에 `-logFile` 을 붙여 로그를 `_workspace/{slug}/` 에 남긴다. 로그가 없으면 실패 원인을 알 수 없다. 배치 모드 한 번에 수 분이 걸릴 수 있으므로 Bash 호출의 제한 시간을 넉넉히 주거나 백그라운드로 돌린다.

## 2. 프로젝트 만들기

```bash
"$U" -batchmode -nographics -quit -createProject games/{slug}/unity -logFile _workspace/{slug}/04_unity_create.log
```

첫 실행에서 라이선스 오류가 나면(로그에 `license` 가 보이면) 재시도하지 말고 리더에게 보고한다. 사용자가 Unity Hub 에 로그인해야 풀린다.

## 3. 폴더 구조와 에셋 복사

```
games/{slug}/unity/                 Unity 프로젝트 루트
├── Assets/
│   ├── Game/
│   │   ├── Scripts/                 Runtime 코드 (Game.Runtime.asmdef)
│   │   ├── Editor/                  BuildScript.cs, SyncAssets 메뉴 (Game.Editor.asmdef, Editor 전용)
│   │   ├── Scenes/                  scr_title.unity, scr_game.unity … (ux.md 의 화면 id)
│   │   ├── Resources/assets/        확정 폴더 assets/ 를 복사한 곳(Resources.Load 로 부른다)
│   │   └── Tests/EditMode, Tests/PlayMode   (각각 asmdef)
│   └── StreamingAssets/game/data/   확정 폴더 data/ 와 manifest.json 복사본
├── Packages/manifest.json
└── ProjectSettings/
```

**복사 규칙:** 확정 폴더(`games/{slug}/assets`, `data`, `manifest.json`)가 원본이다. Unity 쪽은 복사본이므로 직접 고치지 않고, 원본이 바뀌면 다시 복사한다. 상대 경로를 그대로 유지해야 코드의 `assets/audio/sfx/...` 문자열이 에셋 감사 스크립트와 맞는다.

```bash
G=games/{slug}; UA=$G/unity/Assets
rsync -a --delete --exclude '*.dryrun.json' --exclude '*.meta.json' --exclude '*.request.json' $G/assets/ $UA/Game/Resources/assets/
mkdir -p $UA/StreamingAssets/game && rsync -a --delete $G/data/ $UA/StreamingAssets/game/data/ && cp $G/manifest.json $UA/StreamingAssets/game/
```

Unity 가 복사본마다 `.meta` 를 만든다. 다음 배치 모드 실행에서 가져오기(import)가 끝난다.

`Resources.Load` 경로는 확장자를 뺀 `assets/audio/sfx/sfx_door_01` 꼴이다. 에셋 감사 스크립트는 Unity 모드에서 이런 확장자 없는 경로도 대조한다.

## 4. 패키지

`Packages/manifest.json` 의 `dependencies` 에 필요한 것만 더한다.

| 패키지 | 용도 |
| --- | --- |
| `com.unity.test-framework` | EditMode·PlayMode 테스트(새 프로젝트에 기본 포함) |
| `com.unity.cloud.gltfast` | GLB 를 실행 중에 불러오기(VARCO 3D 결과). 버전은 Package Manager 문서의 Unity 6 지원 버전을 적는다 |
| `com.unity.nuget.newtonsoft-json` | 얼굴 애니메이션 JSON 처럼 2차원 배열이 있는 JSON 파싱(`JsonUtility` 는 2차원 배열을 못 읽는다) |

패키지를 더한 뒤 배치 모드를 한 번 돌려 받아지는지 확인한다. 네트워크 오류로 받지 못하면 리더에게 로그를 보고한다.

## 5. 데이터 로더

`StreamingAssets` 는 에디터와 macOS 빌드에서 파일로 읽을 수 있다.

```csharp
// Assets/Game/Scripts/GameData.cs
using System.Collections.Generic; using System.IO; using System.Text; using UnityEngine;
public static class GameData {
    static string Root => Path.Combine(Application.streamingAssetsPath, "game");
    public static List<Dictionary<string,string>> ReadCsv(string rel) {
        var text = File.ReadAllText(Path.Combine(Root, rel), Encoding.UTF8);
        var rows = new List<List<string>>(); var row = new List<string>(); var cell = new StringBuilder(); bool q = false;
        for (int i = 0; i < text.Length; i++) {
            char c = text[i];
            if (q) { if (c == '"' && i + 1 < text.Length && text[i+1] == '"') { cell.Append('"'); i++; } else if (c == '"') q = false; else cell.Append(c); }
            else if (c == '"') q = true;
            else if (c == ',') { row.Add(cell.ToString()); cell.Clear(); }
            else if (c == '\n' || c == '\r') { if (c == '\r' && i + 1 < text.Length && text[i+1] == '\n') i++; row.Add(cell.ToString()); cell.Clear(); rows.Add(row); row = new List<string>(); }
            else cell.Append(c);
        }
        if (cell.Length > 0 || row.Count > 0) { row.Add(cell.ToString()); rows.Add(row); }
        var head = rows[0]; var outp = new List<Dictionary<string,string>>();
        for (int r = 1; r < rows.Count; r++) {
            if (rows[r].Count == 1 && rows[r][0] == "") continue;
            var d = new Dictionary<string,string>();
            for (int k = 0; k < head.Count; k++) d[head[k]] = k < rows[r].Count ? rows[r][k] : "";
            outp.Add(d);
        }
        return outp;
    }
    public static Dictionary<string, Dictionary<string,string>> Balance(string table) {
        var byId = new Dictionary<string, Dictionary<string,string>>();
        foreach (var r in ReadCsv($"data/balance/{table}.csv")) byId[r["id"]] = r;
        return byId;
    }
    public static int Int(Dictionary<string,string> row, string col) {
        if (!int.TryParse(row[col], out var v)) throw new System.FormatException($"밸런스 값 오류 {col}={row[col]}");
        return v;
    }
}
```

`_schema.json` 의 최솟값 검사는 EditMode 테스트에서 한다(8절). 문자열은 `data/strings/{lang}.json` 을 읽어 `Dictionary<string,string>` 으로 두고, 키가 없으면 `ko` 로, 그래도 없으면 키 이름을 보여 준다.

## 6. 오디오·대사·얼굴 애니메이션

```csharp
// 효과음: 변형이 여러 개면 무작위(시드 고정 System.Random)로 고른다. 없으면 자리표시(무음)와 기록.
public static AudioClip LoadClip(string pathNoExt) {
    var clip = Resources.Load<AudioClip>(pathNoExt);            // "assets/audio/sfx/sfx_door_01"
    if (clip == null) { QaState.MissingAsset(pathNoExt); clip = AudioClip.Create("silent", 4410, 1, 44100, false); }
    return clip;
}
```

얼굴 애니메이션은 `assets/anim/face/{line_id}.json` 을 `TextAsset` 으로 불러 Newtonsoft 로 `faceNames`, `weightMat`, `exportFps` 를 읽는다. `SkinnedMeshRenderer.sharedMesh.GetBlendShapeIndex(name)` 로 ARKit 이름을 인덱스로 바꾸고, 매 프레임 `AudioSource.time * exportFps` 로 행을 골라 `SetBlendShapeWeight(index, w * 100f)` 를 부른다(Unity 블렌드셰이프 가중치는 0~100). 프레임 수로 세지 않고 오디오 시간으로 계산해야 입 모양이 소리보다 늦지 않다.

## 7. QA 훅

- **GameObject 이름 = ux.md 요소 id:** 버튼·라벨 오브젝트 이름을 `btn_start`, `lbl_lap` 으로 짓는다. PlayMode 테스트가 `GameObject.Find("btn_start")` 로 찾는다.
- **씬 이름 = 화면 id:** `scr_title`, `scr_game`.
- **상태 스냅샷:** `QaState` 정적 클래스가 현재 씬, 주요 상태 값, `missingAssets`, `missingStrings`, 오류(`Application.logMessageReceived` 로 모은 Exception)를 들고 있다가, 명령줄에 `-qaState <경로>` 가 있으면 그 경로에 JSON 으로 쓴다.
- **명령줄 인자:** `-scene scr_game -seed 1 -lang en` 을 `System.Environment.GetCommandLineArgs()` 로 읽는다.

## 8. 테스트

Unity Test Framework 로 두 종류를 만든다.

| 종류 | 위치 | 검사할 것 |
| --- | --- | --- |
| EditMode | `Assets/Game/Tests/EditMode/` | CSV·strings 로더, 밸런스 값이 `_schema.json` 범위 안인지, 코드가 쓰는 string_id 가 strings 에 있는지, 매니페스트 경로 계산 |
| PlayMode | `Assets/Game/Tests/PlayMode/` | 씬 전환(ux.md 화면 흐름), 버튼이 있고 눌리는지, 코어 루프 한 바퀴 |

```bash
"$U" -batchmode -nographics -projectPath games/{slug}/unity -runTests -testPlatform EditMode \
     -testResults _workspace/{slug}/04_unity_editmode.xml -logFile _workspace/{slug}/04_unity_editmode.log
"$U" -batchmode -projectPath games/{slug}/unity -runTests -testPlatform PlayMode \
     -testResults _workspace/{slug}/04_unity_playmode.xml -logFile _workspace/{slug}/04_unity_playmode.log
```

- `-runTests` 에는 `-quit` 을 붙이지 않는다. 테스트가 끝나면 스스로 종료한다.
- PlayMode 에서 그래픽 관련 오류가 나면 `-nographics` 를 뺀다.
- 종료 코드: 0 전부 통과, 2 실패한 테스트 있음, 그 밖의 값은 실행 자체 실패(로그 확인).
- 결과 XML(NUnit 3)의 `test-run` 요소에 `total`, `passed`, `failed` 속성이 있다. 읽는 방법은 `game-qa-testing` 스킬에 있다.

## 9. 컴파일 확인과 빌드

```bash
# 컴파일만 확인
"$U" -batchmode -nographics -quit -projectPath games/{slug}/unity -logFile _workspace/{slug}/04_unity_compile.log
grep -E "error CS[0-9]+" _workspace/{slug}/04_unity_compile.log && echo "컴파일 오류 있음"

# macOS 빌드: Assets/Game/Editor/BuildScript.cs 의 정적 메서드
"$U" -batchmode -nographics -quit -projectPath games/{slug}/unity \
     -executeMethod Game.EditorTools.BuildScript.BuildMac -logFile _workspace/{slug}/04_unity_build.log
```

```csharp
// Assets/Game/Editor/BuildScript.cs
namespace Game.EditorTools {
  public static class BuildScript {
    public static void BuildMac() {
      var scenes = System.Array.ConvertAll(UnityEditor.EditorBuildSettings.scenes, s => s.path);
      var r = UnityEditor.BuildPipeline.BuildPlayer(scenes, "Builds/Mac/Game.app",
                UnityEditor.BuildTarget.StandaloneOSX, UnityEditor.BuildOptions.None);
      if (r.summary.result != UnityEditor.Build.Reporting.BuildResult.Succeeded) UnityEditor.EditorApplication.Exit(1);
    }
  }
}
```

씬을 Build Settings 에 등록하는 일도 Editor 스크립트로 한다(`EditorBuildSettings.scenes = …`). 에디터 GUI 를 열어야만 할 수 있는 작업은 만들지 않는다.

## 10. VARCO Sound Unity 플러그인

VARCO Sound 플러그인(`.claude/skills/varco-api/references/unity-plugin.md`)은 사람이 에디터 창에서 쓰는 제작 도구다. 게임 실행 코드가 아니며 실행 중 생성도 지원하지 않는다. 배경음악(`manual.unity_music`)은 이 플러그인의 Music 탭에서만 만들 수 있으므로, 사용자가 만들어 `games/{slug}/assets/audio/music/{id}.wav` 에 넣으면 3절 복사 규칙으로 가져온다. 플러그인을 프로젝트에 넣을지는 사용자가 정한다. 플러그인이 에디터 설정에 저장하는 API 키를 커밋하거나 파일로 옮겨 적지 않는다.
