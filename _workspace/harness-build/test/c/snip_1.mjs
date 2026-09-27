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
