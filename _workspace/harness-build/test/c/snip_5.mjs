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
