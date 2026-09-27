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
