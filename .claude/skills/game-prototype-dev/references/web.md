# 웹(HTML5) 프로토타입 구현 참고

빌드 도구 없이 브라우저가 바로 읽는 ES 모듈로 만든다. 2D 는 Phaser 3, 3D(GLB) 는 three.js 를 쓴다. 설치·번들 단계를 없애야 qa 가 서버만 띄워 바로 검사할 수 있다.

## 목차

1. [폴더 구조](#1-폴더-구조)
2. [라이브러리 받기](#2-라이브러리-받기)
3. [index.html 과 import map](#3-indexhtml-과-import-map)
4. [서버 실행](#4-서버-실행)
5. [데이터 로더 — CSV·스키마·문자열](#5-데이터-로더--csv스키마문자열)
6. [에셋 로더와 자리표시](#6-에셋-로더와-자리표시)
7. [Phaser 3 골격](#7-phaser-3-골격)
8. [three.js 로 GLB 불러오기](#8-threejs-로-glb-불러오기)
9. [대사 음성과 얼굴 애니메이션](#9-대사-음성과-얼굴-애니메이션)
10. [QA 훅 — window.__game 과 data-testid](#10-qa-훅--window__game-과-data-testid)
11. [자체 점검](#11-자체-점검)

---

## 1. 폴더 구조

```
games/{slug}/
├── web/
│   ├── index.html
│   ├── vendor/            phaser.esm.js, three.module.js, addons/ (받아 둔 라이브러리)
│   └── src/
│       ├── main.js        진입점: 로더 → 첫 화면
│       ├── data.js        CSV·스키마·문자열 로더
│       ├── assets.js      매니페스트 기반 에셋 로더 + 자리표시
│       ├── debug.js       window.__game, URL 파라미터
│       └── scenes/        화면(scr_*)마다 파일 하나
├── data/  assets/  manifest.json   ← 확정 폴더(읽기만 한다)
```

코드는 `web/` 아래에만 쓴다. `data/`, `assets/`, `manifest.json` 은 다른 담당의 확정본이므로 읽기만 한다. 코드에서 이 파일들은 `../data/...`, `../assets/...`, `../manifest.json` 으로 부른다.

## 2. 라이브러리 받기

버전을 고정해 한 번 받아 `web/vendor/` 에 둔다. 네트워크는 설정된 프록시 정책을 그대로 따른다. 받을 수 없으면(프록시 차단 등) 우회하지 말고 리더에게 오류 메시지를 그대로 보고한다. 그동안은 Canvas 2D 로 직접 그려 진행할 수 있다.

```bash
V=games/{slug}/web/vendor; mkdir -p $V/addons/loaders $V/addons/utils
curl -fsSL -o $V/phaser.esm.js https://cdn.jsdelivr.net/npm/phaser@3.80.1/dist/phaser.esm.js
curl -fsSL -o $V/three.module.js https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js
curl -fsSL -o $V/addons/loaders/GLTFLoader.js https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/loaders/GLTFLoader.js
curl -fsSL -o $V/addons/utils/BufferGeometryUtils.js https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/utils/BufferGeometryUtils.js
```

GLTFLoader 는 `three` 와 `../utils/BufferGeometryUtils.js` 를 import 하므로 위 구조를 지킨다. 2D 게임이면 three.js 를, 3D 게임이면 Phaser 를 받지 않아도 된다.

## 3. index.html 과 import map

```html
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{게임 제목}</title>
  <script type="importmap">
  { "imports": {
      "phaser": "./vendor/phaser.esm.js",
      "three": "./vendor/three.module.js",
      "three/addons/": "./vendor/addons/" } }
  </script>
  <style>html,body{margin:0;background:#111;height:100%} #ui{position:absolute;inset:0;pointer-events:none}
         #ui [data-testid]{pointer-events:auto}</style>
</head>
<body>
  <div id="game"></div>
  <div id="ui"></div>   <!-- DOM 오버레이 UI: 버튼·라벨에 data-testid -->
  <script type="module" src="./src/main.js"></script>
</body>
</html>
```

## 4. 서버 실행

확정 폴더 전체를 서버 루트로 띄운다. 그래야 `web/` 의 코드가 `../data`, `../assets` 를 읽을 수 있다. `file://` 로 열면 fetch 가 막힌다.

```bash
python3 -m http.server 8765 --directory games/{slug}
# http://localhost:8765/web/index.html?seed=1&lang=ko
```

localhost 는 프록시를 거치지 않는다.

## 5. 데이터 로더 — CSV·스키마·문자열

```js
// src/data.js
export function parseCsv(text) {            // RFC 4180: 따옴표 안의 쉼표·줄바꿈·"" 처리
  const rows = []; let row = [], cell = '', q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) { if (c === '"' && text[i + 1] === '"') { cell += '"'; i++; } else if (c === '"') q = false; else cell += c; }
    else if (c === '"') q = true;
    else if (c === ',') { row.push(cell); cell = ''; }
    else if (c === '\n' || c === '\r') { if (c === '\r' && text[i + 1] === '\n') i++; row.push(cell); rows.push(row); row = []; cell = ''; }
    else cell += c;
  }
  if (cell !== '' || row.length) { row.push(cell); rows.push(row); }
  const [head, ...body] = rows.filter(r => r.length > 1 || r[0] !== '');
  return body.map(r => Object.fromEntries(head.map((h, i) => [h, r[i] ?? ''])));
}

const CAST = { int: v => parseInt(v, 10), float: v => parseFloat(v), string: v => v, bool: v => v === 'true' || v === '1' };

export async function loadBalance(table, schema) {   // schema = data/balance/_schema.json 전체
  const rows = parseCsv(await (await fetch(`../data/balance/${table}.csv`)).text());
  const cols = schema[table]?.columns ?? {};
  const byId = {};
  for (const r of rows) {
    for (const [c, spec] of Object.entries(cols)) {
      const v = CAST[spec.type ?? 'string'](r[c]);
      if ((spec.type === 'int' || spec.type === 'float') && (Number.isNaN(v) || (spec.min != null && v < spec.min)))
        throw new Error(`밸런스 값 오류 ${table}.${r.id}.${c}=${r[c]}`);   // 조용히 넘어가지 않는다
      r[c] = v;
    }
    byId[r.id] = r;
  }
  return byId;
}

let STR = {}, FALLBACK = {};
export async function loadStrings(lang) {
  FALLBACK = await (await fetch('../data/strings/ko.json')).json();
  STR = lang === 'ko' ? FALLBACK : await fetch(`../data/strings/${lang}.json`).then(r => r.ok ? r.json() : {});
}
export function t(key, vars = {}) {
  let s = STR[key];
  if (s == null) { s = FALLBACK[key]; window.__game?.missingStrings.add(key); }
  if (s == null) return key;                                  // 키 이름을 그대로 보여 준다
  return s.replace(/\{([a-zA-Z_]\w*)\}/g, (_, k) => vars[k] ?? `{${k}}`);
}
```

## 6. 에셋 로더와 자리표시

매니페스트의 `output` 규칙으로 id → 경로를 계산하고, 파일이 없거나 상태가 `qa_passed`·`generated` 가 아니면 자리표시를 쓴다.

```js
// src/assets.js
let MANIFEST = { assets: [] };
export async function loadManifest() { MANIFEST = await (await fetch('../manifest.json')).json(); return MANIFEST; }

export function assetPaths(id, lineId) {
  const a = MANIFEST.assets.find(x => x.id === id); if (!a) return [];
  const o = a.output; const base = `../${o.dir}/`;
  if (lineId) return [`${base}${o.basename.replace('{line_id}', lineId)}.${o.format}`];
  if ((o.count ?? 1) === 1) return [`${base}${o.basename}.${o.format}`];
  return Array.from({ length: o.count }, (_, i) => `${base}${o.basename}_${String(i + 1).padStart(2, '0')}.${o.format}`);
}
const USABLE = new Set(['qa_passed', 'generated']);
export function usable(id) { return USABLE.has(MANIFEST.assets.find(x => x.id === id)?.status); }

const ctx = new (window.AudioContext || window.webkitAudioContext)();
const SILENT = ctx.createBuffer(1, 4410, 44100);             // 0.1초 무음
export async function loadSound(id, lineId) {
  const paths = assetPaths(id, lineId);
  if (!usable(id) || !paths.length) return placeholder(id, [SILENT]);
  const out = [];
  for (const p of paths) {
    try { out.push(await ctx.decodeAudioData(await (await fetch(p)).arrayBuffer())); }
    catch { window.__game?.missingAssets.add(p); out.push(SILENT); }
  }
  return out;                                                // 변형이 여러 개면 무작위로 골라 재생
}
function placeholder(id, value) { window.__game?.missingAssets.add(id); return value; }
```

이미지 자리표시는 캔버스에 회색 사각형과 id 를 그려 텍스처로 쓰고, 3D 는 8절의 회색 상자를 쓴다.

## 7. Phaser 3 골격

```js
// src/main.js
import Phaser from 'phaser';
import { initDebug } from './debug.js';
import { loadBalance, loadStrings, t } from './data.js';
import { loadManifest } from './assets.js';

const g = initDebug();                                       // URL 파라미터·window.__game
const schema = await (await fetch('../data/balance/_schema.json')).json();
g.data = { enemies: await loadBalance('enemies', schema) }; // 표마다
await loadStrings(g.lang); await loadManifest();

class Title extends Phaser.Scene {
  constructor() { super('scr_title'); }
  create() {
    g.setScene('scr_title');
    const btn = g.dom.button('btn_start', t('ui.title.start'), () => this.scene.start('scr_game'));
    this.events.once('shutdown', () => btn.remove());
  }
}
new Phaser.Game({ type: Phaser.AUTO, parent: 'game', width: 1280, height: 720, scene: [Title /*, Game … */],
                  seed: [String(g.seed)] });
g.ready = true;
```

Phaser 의 소리는 6절 `loadSound` 로 디코딩한 AudioBuffer 를 WebAudio 로 직접 재생하거나, Phaser 로더에 경로를 넘기되 `loaderror` 이벤트에서 자리표시로 바꾼다. 무작위성은 `Phaser.Math.RND`(seed 고정)만 쓴다. `Math.random()` 을 쓰면 qa 가 같은 상황을 재현할 수 없다.

## 8. three.js 로 GLB 불러오기

```js
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { assetPaths, usable } from './assets.js';

export async function loadModel(id, size = [1, 1, 1]) {
  const [path] = assetPaths(id);
  if (usable(id) && path) {
    try { return (await new GLTFLoader().loadAsync(path)).scene; }
    catch { window.__game?.missingAssets.add(path); }
  } else window.__game?.missingAssets.add(id);
  const box = new THREE.Mesh(new THREE.BoxGeometry(...size), new THREE.MeshStandardMaterial({ color: 0x888888 }));
  box.name = `placeholder:${id}`;
  return box;
}
```

VARCO Image to 3D 결과는 크기·원점이 제각각이다. 불러온 뒤 `new THREE.Box3().setFromObject(obj)` 로 크기를 재서 기획 문서의 크기에 맞게 배율을 정하고 바닥에 붙인다.

## 9. 대사 음성과 얼굴 애니메이션

Voice-to-Face 응답(`assets/anim/face/{line_id}.json`)은 `blendshape.faceNames`(ARKit 52종 이름)와 `blendshape.weightMat`(프레임 × 포즈, 값 0~1), `exportFps` 를 준다. 캐릭터 메시의 모프 타깃 이름이 ARKit 이름과 같으면 그대로, 다르면 매핑 표를 둔다.

```js
export async function playLine(lineId, voiceLang, faceMesh, subtitleEl) {
  const audio = new Audio(`../assets/audio/voice/${voiceLang}/${lineId}.wav`);
  let face = null;
  try { face = (await (await fetch(`../assets/anim/face/${lineId}.json`)).json()).blendshape; } catch {}
  subtitleEl.textContent = t(lineId);
  const idx = face && faceMesh ? face.faceNames.map(n => faceMesh.morphTargetDictionary?.[n]) : [];
  const tick = () => {
    if (audio.paused || audio.ended) { if (faceMesh) faceMesh.morphTargetInfluences.fill(0); return; }
    if (face && faceMesh) {
      const f = Math.min(face.weightMat.length - 1, Math.floor(audio.currentTime * face.exportFps));
      face.weightMat[f].forEach((w, j) => { if (idx[j] != null) faceMesh.morphTargetInfluences[idx[j]] = w; });
    } else if (faceMesh) {                                    // 자리표시: jawOpen 사인파
      const j = faceMesh.morphTargetDictionary?.jawOpen; if (j != null) faceMesh.morphTargetInfluences[j] = 0.3 + 0.3 * Math.sin(audio.currentTime * 20);
    }
    requestAnimationFrame(tick);
  };
  audio.onerror = () => { window.__game?.missingAssets.add(lineId); setTimeout(() => (subtitleEl.textContent = ''), 80 * t(lineId).length); };
  window.__game.state.dialogue = { lineId, face: !!face };
  await audio.play().catch(() => {}); tick();
}
```

프레임은 오디오의 `currentTime` 으로 계산한다. `requestAnimationFrame` 횟수로 세면 프레임이 밀려 입 모양이 소리보다 늦어진다. 브라우저는 사용자 입력 전에 소리 재생을 막으므로 첫 화면에서 버튼을 한 번 누르게 한다.

## 10. QA 훅 — window.__game 과 data-testid

```js
// src/debug.js
export function initDebug() {
  const p = new URLSearchParams(location.search);
  const g = window.__game = {
    ready: false, scene: null, state: {}, ui: {},
    seed: Number(p.get('seed') ?? 1), lang: p.get('lang') ?? 'ko', timeScale: Number(p.get('timeScale') ?? 1),
    startScene: p.get('scene'), errors: [], missingAssets: new Set(), missingStrings: new Set(),
    setScene(id) { this.scene = id; },
    snapshot() { return JSON.parse(JSON.stringify({ ...this, missingAssets: [...this.missingAssets],
                                                   missingStrings: [...this.missingStrings], dom: undefined })); },
    dom: {
      button(testid, label, onClick) {
        const b = document.createElement('button'); b.dataset.testid = testid; b.textContent = label;
        b.onclick = onClick; document.getElementById('ui').append(b); g.ui[testid] = { visible: true, text: label };
        return b;
      },
    },
  };
  window.addEventListener('error', e => g.errors.push(String(e.message)));
  window.addEventListener('unhandledrejection', e => g.errors.push(String(e.reason)));
  return g;
}
```

규칙:
- **요소 id:** `docs/ux.md` 의 요소 id(`btn_start`, `lbl_lap`)를 `data-testid` 에 그대로 쓴다. 캔버스에 직접 그리는 요소는 `__game.ui[요소 id] = {visible, text, enabled}` 로 상태를 갱신한다. qa 는 이 두 경로로 요소를 찾는다.
- **화면 id:** 화면이 바뀔 때마다 `__game.setScene('scr_…')` 를 부른다. qa 는 이 값으로 화면 흐름을 검사한다.
- **상태:** 테스트가 확인해야 할 값(점수, 체력, 바퀴 수, 현재 대사)은 `__game.state` 아래에 둔다. 표시용 문자열이 아니라 원래 값으로 둔다.
- **파라미터:** `?scene=scr_game` 이면 그 화면으로 바로 가고, `?seed=` 로 무작위를 고정하고, `?timeScale=4` 로 게임 시간을 빠르게 한다. `?debug=0` 이면 자리표시 에셋 id 같은 디버그 표시를 화면에서 숨긴다(마케팅 스크린샷용). 숨겨도 `__game` 의 기록은 그대로 쌓는다.
- 배포용 빌드를 따로 만들지 않는 프로토타입이므로 훅을 지우지 않는다.

## 11. 자체 점검

```bash
# 문법
for f in $(find games/{slug}/web -name '*.js' -not -path '*/vendor/*'); do node --check "$f" || echo "FAIL $f"; done
# 데이터 계약
python3 .claude/skills/game-qa-testing/scripts/check_data_contracts.py --game-dir games/{slug}
# 실행: 서버를 백그라운드로 띄우고 Playwright MCP 로 열어 __game.ready, __game.errors 확인(game-qa-testing 스킬 5절)
```

`node --check` 는 import map 을 모르므로 import 경로 오류는 잡지 못한다. 실제로 열어 보는 단계를 건너뛰지 않는다.
