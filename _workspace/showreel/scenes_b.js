// ============================================================================
// 장면 B: 02 명세 · 03 제작 · 04 개발 · 05 출시 · 엔딩
// ============================================================================
let MESH = null;
function initScenesB() {
  MESH = buildGolemMesh();
  SCENES.push({ name: 'spec', start: 22, end: 26, draw: sceneSpec });
  SCENES.push({ name: 'produce', start: 26, end: 36, draw: sceneProduce });
  SCENES.push({ name: 'develop', start: 36, end: 46, draw: sceneDevelop });
  SCENES.push({ name: 'release', start: 46, end: 52, draw: sceneRelease });
  SCENES.push({ name: 'outro', start: 52, end: 60, draw: sceneOutro });
}

// 방사형 입자 폭발
function burst(cx, cy, t, t0, n, seed, colors, o = {}) {
  const d = t - t0; if (d < 0 || d > (o.life || 1.4)) return;
  const r = rng(seed), life = o.life || 1.4, sp = o.speed || 900;
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < n; i++) {
    const ang = r() * Math.PI * 2, v = sp * (0.3 + r() * 0.9), len = 6 + r() * 28;
    const k = 1 - Math.exp(-d * 3.2);
    const x = cx + Math.cos(ang) * v * k / 3.2, y = cy + Math.sin(ang) * v * k / 3.2 + d * d * 120 * (o.grav ? 1 : 0);
    const a = (1 - d / life) * (0.6 + r() * 0.4);
    ctx.globalAlpha = a; ctx.strokeStyle = colors[i % colors.length]; ctx.lineWidth = 2 + r() * 2;
    ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - Math.cos(ang) * len * (1 - k), y - Math.sin(ang) * len * (1 - k)); ctx.stroke();
    ctx.fillStyle = colors[i % colors.length]; ctx.fillRect(x - 1.5, y - 1.5, 3, 3);
  }
  ctx.restore();
}
function shockRing(cx, cy, t, t0, color, o = {}) {
  const d = t - t0, life = o.life || 0.8; if (d < 0 || d > life) return;
  const p = E.outCubic(d / life);
  ctx.save(); ctx.globalAlpha = (1 - d / life) * (o.alpha || 0.8); ctx.strokeStyle = color; ctx.lineWidth = (o.lw || 6) * (1 - p) + 1;
  ctx.beginPath(); ctx.ellipse(cx, cy, (o.r0 || 60) + p * (o.r || 900), ((o.r0 || 60) + p * (o.r || 900)) * (o.flat || 1), 0, 0, Math.PI * 2); ctx.stroke(); ctx.restore();
}
function stepList(x, y, t, items, color) {
  items.forEach((it, i) => {
    const yy = y + i * 46, a = seg(t, it.show, it.show + 0.3); if (a <= 0) return;
    withA(a, () => {
      const done = t >= it.done;
      circle(x + 12, yy - 6, 11, done ? color : 'rgba(255,255,255,0.06)', done ? null : hexA(color, 0.6), 1.5);
      if (done) txt('✓', x + 12, yy - 1, { size: 14, w: 800, color: '#05060A', align: 'center' });
      else txt(String(i + 1), x + 12, yy - 1, { mono: true, size: 12, w: 700, color, align: 'center' });
      txt(it.s, x + 36, yy, { size: 21, w: 600, color: done ? C.ink : C.dim });
    });
  });
}

// ------------------------------------------------------------------ 02 명세
const MANIFEST_LINES = [
  '{', '  "game": "coin-runner",', '  "varco_mode": "live",', '  "budget_credits": 1364,', '  "assets": [',
  '    { "id": "sfx_coin_pickup",', '      "category": "sfx", "priority": "P0",', '      "steps": [', '        { "api": "sound.text2sound" },', '        { "api": "sound.variation" } ] },',
  '    { "id": "amb_vault_collapse",', '      "category": "ambience",', '      "steps": [', '        { "api": "sound.text2sound" },', '        { "api": "sound.mono2stereo" },', '        { "api": "sound.looping" } ] },',
  '    { "id": "vo_intro",', '      "category": "voice_line",', '      "lines": ["intro_001", "…"],', '      "steps": [', '        { "api": "tts.standard" },', '        { "api": "face.blendshape" } ] },',
  '    { "id": "mdl_vault_golem",', '      "category": "model_3d",', '      "steps": [', '        { "api": "3d.image_to_3d" } ] },',
  '    { "id": "l10n_en",', '      "category": "localization",', '      "steps": [', '        { "api": "mt.translate" } ] },',
  '    { "id": "bgm_title",', '      "steps": [{ "api": "manual.unity_music" }] },', '    { "id": "mkt_capsule", "phase": "release" }', '  ]', '}',
];
const BINS = [['효과음', 10, C.cyan], ['환경음', 3, C.cyan], ['대사 음성', 4, C.violet], ['3D 모델', 2, C.amber], ['현지화', 2, C.lime], ['마케팅', 3, C.coral]];
function codeLine(s, x, y, o = {}) {
  // 아주 단순한 JSON/JS 문법 색칠
  const size = o.size || 17; let cx = x;
  const re = /(\/\/.*$)|("[^"]*")(\s*:)?|('[^']*')|(\b\d[\d,.]*\b)|([{}\[\],:()])|(\b(?:const|await|import|from|window|function|return)\b)|([^"'\d{}\[\],:()\/]+|\/)/g;
  let m;
  while ((m = re.exec(s))) {
    let col = C.ink, piece = m[0];
    if (m[1]) col = C.mute; else if (m[2] && m[3]) col = C.amber; else if (m[2] || m[4]) col = '#A7F3D0'; else if (m[5]) col = C.cyan; else if (m[6]) col = C.dim; else if (m[7]) col = C.opus;
    if (m[2] && m[2].includes('"api"')) col = C.amber;
    if ((m[2] || m[4]) && /sound\.|tts\.|face\.|3d\.|mt\.|manual\.|sfx_|intro_/.test(m[2] || m[4])) col = C.lime;
    txt(piece, cx, y, { mono: true, size, w: 500, color: col, alpha: o.alpha ?? 1 });
    cx += tw(piece, 500, size, true);
  }
}
function sceneSpec(t) {
  planLeft(t, { no: '02', t0: 22.0 }, '명세', 'SPEC · 서브에이전트 · 크레딧 승인', C.amber);
  stepList(120, 612, t, [
    { s: '기획 문서에서 에셋 추출', show: 22.3, done: 22.9 }, { s: 'VARCO API 호출 순서 결정', show: 22.45, done: 23.4 },
    { s: '크레딧 견적', show: 22.6, done: 24.8 }, { s: '사용자 승인', show: 22.75, done: 25.2 },
  ], C.amber);
  const est = seg(t, 23.45, 23.8, E.inOutCubic);
  const dimBack = 1 - est * 0.8;
  // 매니페스트 코드
  const cp = seg(t, 22.05, 22.45);
  withA(cp * dimBack, () => {
    const x = 760, y = 140, w = 560, h = 760;
    panel(x, y, w, h, { fill: '#0B0C12', stroke: hexA(C.amber, 0.35) });
    txt('02_producer_manifest.json', x + 24, y + 38, { mono: true, size: 14, w: 600, color: C.amber });
    ctx.save(); rr(x + 1, y + 58, w - 2, h - 60, 12); ctx.clip();
    const scroll = Math.min((t - 22.1) * 330, MANIFEST_LINES.length * 28 - 600);
    MANIFEST_LINES.forEach((s, i) => { const yy = y + 96 + i * 28 - Math.max(0, scroll); if (yy > y + 40 && yy < y + h + 20) codeLine(s, x + 24, yy, { size: 16 }); });
    ctx.restore();
    const hl = ((t * 3) % 1); ctx.fillStyle = hexA(C.amber, 0.08); ctx.fillRect(x + 1, y + 300 + Math.sin(t * 5) * 120, w - 2, 28);
  });
  // 분류함
  withA(seg(t, 22.2, 22.5) * dimBack, () => {
    BINS.forEach(([name, n, col], k) => {
      const x = 1350, y = 140 + k * 108, a = seg(t, 22.25 + k * 0.05, 22.55 + k * 0.05);
      withA(a, () => {
        panel(x, y, 450, 92, { fill: 'rgba(255,255,255,0.03)', stroke: hexA(col, 0.3) });
        ctx.fillStyle = col; ctx.fillRect(x, y + 16, 4, 60);
        txt(name, x + 28, y + 56, { size: 26, w: 700, color: C.ink });
        const got = Math.round(n * seg(t, 22.4 + k * 0.09, 23.5, E.outCubic));
        txt(String(got), x + 420, y + 62, { size: 46, w: 800, color: col, align: 'right' });
      });
    });
    withA(seg(t, 22.9, 23.2), () => txt('+ 배경음악 1 · 수동 제작(Unity 플러그인)', 1352, 812, { size: 16, w: 600, color: C.dim }));
  });
  // 칩이 코드에서 분류함으로 날아간다
  for (let k = 0; k < 12; k++) {
    const t0 = 22.4 + k * 0.09, u = inv(t0 - 0.28, t0, t); if (u <= 0 || u >= 1) continue;
    const b = k % 6, sx = 1300, sy = 300 + (k * 97) % 420, ex = 1380, ey = 186 + b * 108;
    const e = E.inOutCubic(u);
    const px = lerp(sx, ex, e), py = lerp(sy, ey, e) - Math.sin(Math.PI * e) * 60;
    glowDot(px, py, 30, BINS[b][2], 1); chip(px, py, ['sfx', 'amb', 'vo', 'mdl', 'l10n', 'mkt'][b] + '_' + k, { size: 12, h: 22, padX: 8, color: '#05060A', fill: BINS[b][2], align: 'center' });
  }
  // 크레딧 견적
  if (est > 0) {
    const cx = 1280, cy = 470, out = seg(t, 24.75, 24.95);
    withA(est * (1 - out * 0.7), () => {
      txt('예상 크레딧', cx, cy - 196, { size: 28, w: 700, color: C.dim, align: 'center' });
      const v = Math.round(1240 * seg(t, 23.5, 24.8, E.outCubic));
      txt(v.toLocaleString('en-US'), cx, cy, { size: 200, w: 800, color: C.amber, align: 'center', glow: 40, glowColor: hexA(C.amber, 0.5), track: -6 });
      const bw = 820, bx = cx - bw / 2, by = cy + 60;
      const parts = [['P0', 780, C.amber], ['P1', 330, mixHex(C.amber, '#000000', 0.35)], ['P2', 130, mixHex(C.amber, '#000000', 0.6)]];
      let acc = 0; const g = seg(t, 23.7, 24.6, E.outCubic);
      parts.forEach(([l, n, col]) => {
        const w0 = bw * n / 1240; ctx.fillStyle = col; ctx.fillRect(bx + acc * g, by, w0 * g - 4, 18);
        withA(g, () => txt(`${l} ${n}`, bx + acc * g, by + 50, { mono: true, size: 16, w: 700, color: C.ink }));
        acc += w0;
      });
      withA(seg(t, 24.2, 24.5), () => txt('단가 미공개 호출 3건(번역·얼굴·연기 변환)은 따로 승인', cx, by + 100, { size: 18, w: 500, color: C.dim, align: 'center' }));
    });
  }
  // 승인 모달과 도장
  const mp = seg(t, 24.8, 25.05, E.outBack);
  if (mp > 0) {
    const zoom = 1 + seg(t, 25.55, 26.0, E.inExpo) * 3;
    ctx.save(); ctx.translate(1280, 520); ctx.scale(zoom, zoom); ctx.translate(-1280, -520);
    at(1280, 520, lerp(0.85, 1, mp), 0, () => withA(clamp(mp * 2), () => {
      panel(-360, -170, 720, 340, { fill: '#12100A', stroke: C.amber, lw: 2, glow: 50, glowColor: hexA(C.amber, 0.5), r: 22 });
      txt('크레딧 승인이 필요합니다', -320, -100, { size: 36, w: 800, color: C.ink });
      txt('예상 1,240 · 예산 1,364 (여유 10%)', -320, -56, { size: 20, w: 500, color: C.dim });
      const press = seg(t, 25.0, 25.08) * (1 - seg(t, 25.08, 25.2));
      [['전체 승인', C.amber, '#05060A'], ['P0만', 'rgba(255,255,255,0.08)', C.ink], ['드라이런', 'rgba(255,255,255,0.08)', C.ink]].forEach(([s, bg, fg], i) => {
        const bx = -320 + i * 220, sc = i === 0 ? 1 - press * 0.08 : 1;
        at(bx + 95, 60, sc, 0, () => { rr(-95, -34, 190, 68, 14); ctx.fillStyle = bg; ctx.fill(); txt(s, 0, 9, { size: 24, w: 800, color: fg, align: 'center' }); });
      });
    }));
    // 커서
    const cu = seg(t, 24.85, 25.0, E.outCubic);
    const mx = lerp(1540, 1055, cu), my = lerp(760, 585, cu);
    withA(mp, () => at(mx, my, 1 - seg(t, 25.0, 25.06) * 0.15 + seg(t, 25.06, 25.2) * 0.15, 0, () => {
      ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, 34); ctx.lineTo(9, 26); ctx.lineTo(16, 40); ctx.lineTo(22, 37); ctx.lineTo(15, 23); ctx.lineTo(27, 23); ctx.closePath();
      ctx.fillStyle = '#fff'; ctx.fill(); ctx.strokeStyle = '#000'; ctx.lineWidth = 2; ctx.stroke();
    }));
    const sp = seg(t, 25.2, 25.36, E.inExpo);
    if (sp > 0) {
      shockRing(1470, 640, t, 25.36, C.amber, { r: 700, lw: 8 });
      withA(clamp(sp * 2), () => at(1470, 640, lerp(2.6, 1, sp), -0.16, () => {
        ctx.save(); ctx.strokeStyle = C.amber; ctx.lineWidth = 8; rr(-210, -78, 420, 156, 16); ctx.stroke(); ctx.restore();
        txt('승인', 0, 10, { size: 88, w: 800, color: C.amber, align: 'center' });
        txt('APPROVED · budget 1,364', 0, 52, { mono: true, size: 16, w: 700, color: C.amber, align: 'center', track: 3 });
      }));
    }
    ctx.restore();
  }
}

// ------------------------------------------------------------------ 03 제작
const TOKENS = ['sfx_coin', 'sfx_jump', 'sfx_debris', 'amb_vault', 'amb_alarm', 'vo_intro', 'vo_boss', 'crv_golem', 'mdl_golem', 'mdl_crate', 'img_bg', 'l10n_en', 'l10n_ja', 'sfx_land', 'sfx_step', 'sfx_hit', 'vo_intro_b', 'amb_drip', 'sfx_ui', 'sfx_door', 'img_door'];
const REWORK = new Set([4, 13]);
const PANELS = [
  { x: 120, y: 262, role: 'sound-designer', api: 'sound.text2sound → sound.variation', title: '효과음', id: 'sfx_coin_pickup', draw: panelSound },
  { x: 970, y: 262, role: 'voice-director', api: 'tts.standard → face.blendshape', title: '대사 음성 · 립싱크', id: 'vo_intro', draw: panelVoice },
  { x: 120, y: 622, role: 'visual-artist', api: '3d.image_to_3d → GLB', title: '3D 모델', id: 'mdl_vault_golem', draw: panel3D },
  { x: 970, y: 622, role: 'localization-specialist', api: 'mt.translate · 용어집', title: '현지화', id: 'l10n_en · l10n_ja', draw: panelL10n },
];
const PW = 830, PH = 340;
function tokenPos(i, t) {
  const t0 = 26.95 + i * 0.045; const rw = REWORK.has(i);
  const S = [[140, 0], [560, 0], [960, 0], [960, 150], [960, 0], [1500, 0]];
  const plan = rw ? [[0, 1, 0.22], [1, 1, 0.14], [1, 2, 0.18], [2, 3, 0.16], [3, 4, 0.2], [4, 5, 0.22]] : [[0, 1, 0.22], [1, 1, 0.14], [1, 2, 0.18], [2, 2, 0.08], [2, 5, 0.24]];
  let tt = t - t0; if (tt < 0) return null;
  for (const [a, b, d] of plan) {
    const lane = ((i * 7) % 5 - 2) * 30;
    if (tt <= d) { const e = E.inOutCubic(tt / d); return { x: lerp(S[a][0], S[b][0], e) + (a === b ? ((i * 3) % 4 - 1.5) * 26 : 0), y: lerp(S[a][1], S[b][1], e) + (S[a][1] === 0 && S[b][1] === 0 ? lane : lane * 0.4), stage: b, rw }; }
    tt -= d;
  }
  return { x: 1500, y: 0, stage: 5, done: true, rw };
}
function sceneProduce(t) {
  // 드롭: 거대한 제목이 박히고 머리글 자리로 줄어든다
  const hp = seg(t, 26.55, 27.05, E.inOutCubic);
  shockRing(W / 2, 540, t, 26.0, C.cyan, { r: 1400, lw: 12, life: 0.9 });
  shockRing(W / 2, 540, t, 26.08, '#ffffff', { r: 1000, lw: 6, life: 0.7 });
  burst(W / 2, 540, t, 26.0, 90, 26, [C.cyan, '#ffffff', C.lime], { speed: 2200, life: 1.3 });
  // 빛줄기
  const ray = Math.exp(-(t - 26) * 2.2) * (t >= 26 ? 1 : 0);
  if (ray > 0.02) { ctx.save(); ctx.translate(W / 2, 540); ctx.globalCompositeOperation = 'lighter'; for (let k = 0; k < 18; k++) { ctx.rotate(Math.PI * 2 / 18); ctx.globalAlpha = ray * 0.12; ctx.fillStyle = C.cyan; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(1400, -40); ctx.lineTo(1400, 40); ctx.closePath(); ctx.fill(); } ctx.restore(); }
  const slam = seg(t, 26.0, 26.25, E.outExpo);
  const size = lerp(lerp(300, 240, slam), 58, hp), x = lerp(W / 2, 120, hp), y = lerp(620, 196, hp);
  txt('에셋 제작', x, y, { size, w: 800, color: C.ink, align: hp > 0.5 ? 'left' : 'center', blur: (1 - slam) * 24, alpha: clamp(slam * 3), track: -size * 0.03, glow: (1 - hp) * 50, glowColor: hexA(C.cyan, 0.8) });
  if (hp < 0.5) withA((1 - hp * 2) * slam, () => txt('03 · MAKE · WORKFLOW', W / 2, 700, { mono: true, size: 22, w: 700, color: C.cyan, align: 'center', track: 10 }));
  withA(seg(t, 26.9, 27.2), () => txt('03 · 워크플로 조율 · 제작 → 검증 → 재작업', 124, 236, { mono: true, size: 16, w: 600, color: C.cyan, track: 2 }));

  // 파이프라인(26.9 ~ 28.3 크게, 이후 위쪽 띠로 접힘)
  const fold = seg(t, 27.95, 28.35, E.inOutCubic);
  const pa = seg(t, 26.85, 27.1);
  if (pa > 0) {
    ctx.save();
    const py = lerp(560, 160, fold), sc = lerp(1, 0.42, fold), ox = lerp(0, 1000, fold);
    ctx.translate(ox, py); ctx.scale(sc, sc); ctx.globalAlpha *= pa;
    const stages = [['제작', 560, 0], ['검증', 960, 0], ['재작업', 960, 150], ['완료', 1500, 0]];
    line(140, 0, 1500, 0, 'rgba(255,255,255,0.12)', 2);
    ctx.save(); ctx.setLineDash([6, 8]); line(960, 0, 960, 150, hexA(C.amber, 0.5), 2); ctx.restore();
    stages.forEach(([s, sx, sy], i) => {
      const col = i === 2 ? C.amber : i === 3 ? C.green : C.cyan;
      panel(sx - 92, sy - 44, 184, 88, { fill: hexA(col, 0.08), stroke: hexA(col, 0.7), lw: 2, r: 16 });
      txt(s, sx, sy + 12, { size: 32, w: 800, color: col, align: 'center' });
    });
    txt(['sound-designer', 'voice-director', 'visual-artist', 'localization'][Math.floor(t * 4) % 4], 560, 78, { mono: true, size: 18, w: 600, color: C.dim, align: 'center' });
    txt('asset-qa', 960, -64, { mono: true, size: 18, w: 600, color: C.dim, align: 'center' });
    let doneN = 0, rwN = 0;
    TOKENS.forEach((id, i) => {
      const q = tokenPos(i, t); if (!q) return;
      if (q.done) { doneN++; return; }
      if (q.rw && q.stage >= 3) rwN = Math.max(rwN, 1);
      const col = q.stage === 3 || q.stage === 4 && q.rw ? C.amber : q.stage >= 2 ? C.green : C.cyan;
      glowDot(q.x, q.y, 34, col, 0.8);
      chip(q.x, q.y, id, { size: 14, h: 28, padX: 10, color: '#05060A', fill: col, align: 'center', w: 700 });
    });
    txt(String(doneN), 1500, 104, { size: 44, w: 800, color: C.green, align: 'center' });
    txt('qa_passed', 1500, 134, { mono: true, size: 16, w: 600, color: C.dim, align: 'center' });
    ctx.restore();

  }
  // 네 칸 작업 화면
  PANELS.forEach((pn, k) => {
    const t0 = 28.0 + k * 0.5, p = seg(t, t0, t0 + 0.45, E.outExpo); if (p <= 0) return;
    const ledgerDim = 1 - seg(t, 34.0, 34.3) * 0.65;
    withA(ledgerDim, () => {
      ctx.save();
      const cx = pn.x + PW / 2, cy = pn.y + PH / 2; ctx.translate(cx, cy); ctx.scale(lerp(0.94, 1, p), lerp(0.94, 1, p)); ctx.translate(-cx, -cy);
      ctx.beginPath(); ctx.rect(pn.x - 10, pn.y - 10, (PW + 20) * p, PH + 20); ctx.clip();
      panel(pn.x, pn.y, PW, PH, { fill: '#0A0D13', stroke: hexA(C.cyan, 0.28) });
      txt(pn.role, pn.x + 28, pn.y + 40, { mono: true, size: 15, w: 700, color: C.cyan });
      txt(pn.api, pn.x + 28 + tw(pn.role, 700, 15, true) + 16, pn.y + 40, { mono: true, size: 15, w: 500, color: C.mute });
      txt(pn.title, pn.x + 28, pn.y + 84, { size: 30, w: 800, color: C.ink });
      txt(pn.id, pn.x + 36 + tw(pn.title, 800, 30), pn.y + 84, { mono: true, size: 15, w: 500, color: C.dim });
      pn.draw(pn.x, pn.y, t, t0);
      // QA 통과 도장
      const qt = 32.0 + k * 0.25, qp = seg(t, qt, qt + 0.3, E.outBackBig);
      if (qp > 0) {
        shockRing(pn.x + PW - 110, pn.y + 44, t, qt, C.green, { r: 160, r0: 20, lw: 4, life: 0.5 });
        at(pn.x + PW - 110, pn.y + 44, qp, 0, () => chip(0, 0, '✓ qa_passed', { align: 'center', size: 15, w: 800, h: 32, color: '#05060A', fill: C.green }));
      }
      ctx.restore();
    });
  });
  // 장부
  const lp = seg(t, 34.0, 34.35, E.outExpo);
  if (lp > 0) withA(lp, () => {
    const x = 460, y = 360, w = 1000, h = 440;
    at(W / 2, y + h / 2, lerp(0.92, 1, lp), 0, () => {
      panel(-w / 2, -h / 2, w, h, { fill: 'rgba(8,12,18,0.94)', stroke: hexA(C.cyan, 0.6), lw: 2, glow: 60, glowColor: hexA(C.cyan, 0.35), r: 22 });
      txt('varco_ledger.jsonl', -w / 2 + 36, -h / 2 + 50, { mono: true, size: 18, w: 700, color: C.cyan });
      txt('예산 잠금 · 동시 호출에도 초과 없음', w / 2 - 36, -h / 2 + 50, { size: 17, w: 600, color: C.dim, align: 'right' });
      const rows = [['sound.text2sound', 'sfx_coin_pickup', 25], ['sound.variation', 'sfx_coin_pickup', 50], ['sound.looping', 'amb_vault_collapse', 150], ['tts.standard', 'vo_intro', 9], ['face.blendshape', 'vo_intro', '—'], ['3d.image_to_3d', 'mdl_vault_golem', 200], ['mt.translate', 'l10n_en', '—'], ['image.background', 'img_bg', 120]];
      const n = Math.min(rows.length, Math.floor((t - 34.0) / 0.15) + 1);
      rows.slice(0, n).slice(-6).forEach((r, i) => {
        const yy = -h / 2 + 100 + i * 36;
        txt(r[0], -w / 2 + 36, yy, { mono: true, size: 17, w: 600, color: C.lime });
        txt(r[1], -w / 2 + 330, yy, { mono: true, size: 17, w: 500, color: C.ink });
        txt(String(r[2]), w / 2 - 140, yy, { mono: true, size: 17, w: 700, color: r[2] === '—' ? C.amber : C.cyan, align: 'right' });
        txt('ok', w / 2 - 50, yy, { mono: true, size: 17, w: 700, color: C.green, align: 'right' });
      });
      const used = Math.round(1118 * seg(t, 34.1, 35.3, E.outCubic));
      const bx = -w / 2 + 36, by = h / 2 - 70, bw = w - 72;
      ctx.fillStyle = 'rgba(255,255,255,0.08)'; ctx.fillRect(bx, by, bw, 14);
      ctx.fillStyle = C.cyan; ctx.fillRect(bx, by, bw * used / 1364, 14);
      txt(`${used.toLocaleString('en-US')} / 1,364 크레딧`, bx, by + 44, { size: 22, w: 800, color: C.ink });
      txt(`${Math.round(used / 1364 * 100)}% · 예산 안`, bx + bw, by + 44, { size: 20, w: 700, color: C.green, align: 'right' });
    });
  });
}
// ---- 제작 패널: 효과음
function waveVal(u, seed, kind = 'sfx') {
  if (kind === 'sfx') { const env = u < 0.04 ? u / 0.04 : Math.exp(-(u - 0.04) * 5); return env * (0.55 + 0.45 * Math.abs(Math.sin(u * 90 + seed) * Math.sin(u * 23 + seed * 2))); }
  return (0.25 + 0.75 * Math.abs(Math.sin(u * 7 + seed))) * (0.4 + 0.6 * Math.abs(Math.sin(u * 61 + seed * 3))) * (u > 0.05 && u < 0.95 ? 1 : 0.2);
}
function drawWave(x, y, w, h, seed, reveal, color, o = {}) {
  const n = o.bars || 90, bw = w / n;
  for (let i = 0; i < n; i++) {
    const u = i / n; if (u > reveal) break;
    const v = waveVal(u, seed, o.kind) * h / 2;
    ctx.fillStyle = color; ctx.globalAlpha = (o.alpha ?? 1) * (u > reveal - 0.05 ? 1 : 0.85);
    ctx.fillRect(x + i * bw, y - v, Math.max(1, bw - 2), v * 2);
  }
  ctx.globalAlpha = 1;
}
function panelSound(x, y, t, t0) {
  const pr = '"bright short coin pickup chime, arcade"';
  withA(seg(t, t0 + 0.2, t0 + 0.4), () => {
    rr(x + 28, y + 108, 520, 34, 17); ctx.fillStyle = hexA(C.cyan, 0.1); ctx.fill();
    scrambleText(pr, x + 44, y + 131, t, t0 + 0.2, 0.6, { mono: true, size: 15, w: 600, color: C.cyan });
  });
  const rv = seg(t, t0 + 0.6, t0 + 1.8, E.inOutCubic);
  drawWave(x + 28, y + 230, 520, 140, 1.3, rv, C.cyan, { bars: 96 });
  if (rv > 0 && rv < 1) line(x + 28 + 520 * rv, y + 160, x + 28 + 520 * rv, y + 300, '#fff', 2, 0.9);
  withA(seg(t, t0 + 1.6, t0 + 2.0), () => { chip(x + 28, y + 318, '10.0s → 0.42s 무음 제거', { size: 13, h: 26, color: C.dim }); chip(x + 240, y + 318, 'peak -1.0 dBFS', { size: 13, h: 26, color: C.dim }); });
  for (let k = 0; k < 4; k++) {
    const vp = seg(t, t0 + 2.0 + k * 0.2, t0 + 2.4 + k * 0.2, E.outExpo); if (vp <= 0) continue;
    const vy = y + 130 + k * 50;
    withA(vp, () => {
      txt(`_0${k + 2}`, x + 586, vy + 6, { mono: true, size: 13, w: 600, color: C.dim });
      drawWave(x + 626, vy, 170 * vp, 36, 2.1 + k * 0.7, 1, mixHex(C.cyan, '#ffffff', k * 0.15), { bars: 34 });
    });
    if (vp > 0 && vp < 1) line(x + 548, y + 230, x + 620, vy, hexA(C.cyan, 0.4), 1.5, 1 - vp);
  }
  withA(seg(t, t0 + 2.2, t0 + 2.6), () => txt('variation ×4', x + 586, y + 330, { mono: true, size: 13, w: 600, color: C.cyan }));
}
// ---- 제작 패널: 음성 + 립싱크
function jaw(t) { const u = t * 7.3; return clamp(0.15 + 0.85 * Math.abs(Math.sin(u) * Math.sin(u * 0.37 + 1.2))); }
function panelVoice(x, y, t, t0) {
  const on = seg(t, t0 + 0.3, t0 + 0.6);
  const speak = t > t0 + 0.8 && t < t0 + 3.9;
  const jw = speak ? jaw(t) : 0.08;
  // 얼굴
  withA(on, () => {
    const fx = x + 128, fy = y + 222;
    glowDot(fx, fy, 170, C.violet, 0.35);
    circle(fx, fy, 88, '#100E1C', C.violet, 3);
    const blink = (t % 2.7) < 0.1 ? 0.15 : 1;
    ctx.fillStyle = C.ink; ctx.beginPath(); ctx.ellipse(fx - 30, fy - 18, 9, 11 * blink, 0, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.ellipse(fx + 30, fy - 18, 9, 11 * blink, 0, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = C.coral; ctx.beginPath(); ctx.ellipse(fx, fy + 36, 26 - jw * 6, 4 + jw * 20, 0, 0, Math.PI * 2); ctx.fill();
    txt('lockey', fx, fy + 120, { mono: true, size: 13, w: 600, color: C.dim, align: 'center' });
  });
  // 자막(노래방식 강조)
  const line1 = '침입자를 확인했습니다.';
  const kp = seg(t, t0 + 0.8, t0 + 3.4, E.lin);
  withA(on, () => {
    txt(line1, x + 270, y + 150, { size: 30, w: 700, color: 'rgba(255,255,255,0.3)' });
    ctx.save(); ctx.beginPath(); ctx.rect(x + 270, y + 110, tw(line1, 700, 30) * kp, 60); ctx.clip();
    txt(line1, x + 270, y + 150, { size: 30, w: 700, color: C.ink }); ctx.restore();
    drawWave(x + 270, y + 196, 330, 44, 4.2, kp, C.violet, { bars: 60, kind: 'voice' });
  });
  // 블렌드셰이프 막대
  const BS = [['jawOpen', jw], ['mouthFunnel', speak ? clamp(0.5 * Math.abs(Math.sin(t * 5.1))) : 0.05], ['mouthSmile', 0.12], ['eyeBlink', (t % 2.7) < 0.1 ? 0.9 : 0.04], ['browInnerUp', speak ? 0.2 + 0.2 * Math.sin(t * 1.7) : 0.1]];
  BS.forEach(([n, v], i) => {
    const a = seg(t, t0 + 0.5 + i * 0.08, t0 + 0.8 + i * 0.08); if (a <= 0) return;
    const yy = y + 250 + i * 18;
    withA(a, () => {
      txt(n, x + 270, yy + 5, { mono: true, size: 12, w: 500, color: C.dim });
      ctx.fillStyle = 'rgba(255,255,255,0.08)'; ctx.fillRect(x + 390, yy - 4, 200, 8);
      ctx.fillStyle = C.violet; ctx.fillRect(x + 390, yy - 4, 200 * v, 8);
      txt(v.toFixed(2), x + 604, yy + 5, { mono: true, size: 12, w: 600, color: C.ink });
    });
  });
  withA(seg(t, t0 + 0.6, t0 + 1.0), () => { chip(x + 660, y + 150, 'emotion: neutral', { size: 12, h: 24, color: C.dim }); chip(x + 660, y + 184, '30 fps', { size: 12, h: 24, color: C.dim }); chip(x + 660, y + 218, 'ARKit 52', { size: 12, h: 24, color: C.dim }); });
}
// ---- 제작 패널: 3D
function buildGolemMesh() {
  // 20면체를 두 번 나누고 결정적 잡음으로 울퉁불퉁한 바위 머리를 만든다
  const t_ = (1 + Math.sqrt(5)) / 2;
  let V = [[-1, t_, 0], [1, t_, 0], [-1, -t_, 0], [1, -t_, 0], [0, -1, t_], [0, 1, t_], [0, -1, -t_], [0, 1, -t_], [t_, 0, -1], [t_, 0, 1], [-t_, 0, -1], [-t_, 0, 1]].map(v => { const l = Math.hypot(...v); return v.map(c => c / l); });
  let Fc = [[0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11], [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8], [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9], [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]];
  for (let s = 0; s < 2; s++) {
    const cache = {}, nf = [];
    const mid = (a, b) => { const k = a < b ? `${a}_${b}` : `${b}_${a}`; if (cache[k] != null) return cache[k]; const m = V[a].map((c, i) => (c + V[b][i]) / 2); const l = Math.hypot(...m); V.push(m.map(c => c / l)); return (cache[k] = V.length - 1); };
    for (const [a, b, c] of Fc) { const ab = mid(a, b), bc = mid(b, c), ca = mid(c, a); nf.push([a, ab, ca], [b, bc, ab], [c, ca, bc], [ab, bc, ca]); }
    Fc = nf;
  }
  V = V.map(([x, y, z]) => {
    const n = 1 + 0.12 * Math.sin(x * 5.1 + y * 2.3) * Math.cos(z * 4.7) + 0.07 * Math.sin(y * 9.3 + z * 3.1);
    const jawCut = y < -0.55 ? 0.82 : 1; // 아래를 납작하게
    return [x * n * 1.05, y * n * 0.95 * jawCut, z * n];
  });
  return { V, F: Fc };
}
function drawMesh(cx, cy, R, rotY, rotX, reveal, color) {
  const { V, F } = MESH;
  const cy_ = Math.cos(rotY), sy = Math.sin(rotY), cx_ = Math.cos(rotX), sx = Math.sin(rotX);
  const P = V.map(([x, y, z]) => { let X = x * cy_ + z * sy, Z = -x * sy + z * cy_; let Y = y * cx_ - Z * sx; Z = y * sx + Z * cx_; const f = 3.2 / (3.2 + Z); return [cx + X * R * f, cy - Y * R * f, Z]; });
  const L = [-0.4, 0.6, -0.7];
  const faces = F.map((f, i) => { const [a, b, c] = f.map(k => P[k]); const z = (a[2] + b[2] + c[2]) / 3; const nx = (b[1] - a[1]) * (c[2] - a[2]) - (b[2] - a[2]) * (c[1] - a[1]), ny = (b[2] - a[2]) * (c[0] - a[0]) - (b[0] - a[0]) * (c[2] - a[2]), nz = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]); return { f, z, i, nz, shade: nz }; });
  faces.sort((p, q) => q.z - p.z);
  for (const fc of faces) {
    const [a, b, c] = fc.f.map(k => P[k]);
    const cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
    if (cross > 0) continue; // 뒷면
    // 스캔 드러남: 위에서 아래로
    const yMid = (a[1] + b[1] + c[1]) / 3; const rv = (yMid - (cy - R * 1.2)) / (R * 2.4);
    if (rv > reveal) continue;
    const lit = clamp(0.25 + 0.75 * Math.abs(cross) / 1800, 0, 1);
    ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.lineTo(c[0], c[1]); ctx.closePath();
    ctx.fillStyle = `rgba(${Math.round(20 + 40 * lit)},${Math.round(40 + 120 * lit)},${Math.round(60 + 140 * lit)},0.95)`; ctx.fill();
    ctx.strokeStyle = hexA(color, 0.35 + 0.4 * lit * (reveal - rv < 0.06 ? 2 : 1)); ctx.lineWidth = 1; ctx.stroke();
  }
  // 스캔선
  if (reveal < 1) { const sy2 = cy - R * 1.2 + R * 2.4 * reveal; line(cx - R * 1.3, sy2, cx + R * 1.3, sy2, '#fff', 2, 0.9); glowDot(cx, sy2, R * 1.2, color, 0.25); }
  // 두 눈
  if (reveal >= 1) { const ex = Math.sin(rotY) * R * 0.33; glowDot(cx - R * 0.28 * Math.cos(rotY) + ex * 0.2, cy - R * 0.08, 22, C.amber, 0.9); glowDot(cx + R * 0.28 * Math.cos(rotY) + ex * 0.2, cy - R * 0.08, 22, C.amber, 0.9); }
}
function panel3D(x, y, t, t0) {
  const a = seg(t, t0 + 0.2, t0 + 0.5);
  withA(a, () => {
    panel(x + 28, y + 112, 190, 190, { fill: '#10141C', stroke: 'rgba(255,255,255,0.14)', r: 12 });
    // 원본 이미지(평면 실루엣)
    ctx.save(); ctx.translate(x + 123, y + 212);
    ctx.fillStyle = '#5B6475'; ctx.beginPath(); ctx.moveTo(-58, 40); ctx.lineTo(-64, -10); ctx.lineTo(-40, -52); ctx.lineTo(0, -64); ctx.lineTo(42, -50); ctx.lineTo(64, -8); ctx.lineTo(56, 42); ctx.lineTo(20, 60); ctx.lineTo(-24, 60); ctx.closePath(); ctx.fill();
    ctx.fillStyle = C.amber; ctx.fillRect(-30, -12, 16, 8); ctx.fillRect(14, -12, 16, 8); ctx.restore();
    txt('source.png', x + 36, y + 324, { mono: true, size: 12, w: 600, color: C.dim });
    txt('→', x + 240, y + 222, { size: 36, w: 700, color: C.cyan });
  });
  const rv = seg(t, t0 + 0.7, t0 + 2.2, E.inOutSine);
  if (rv > 0) drawMesh(x + 470, y + 214, 108, t * 0.9, 0.18, rv, C.cyan);
  withA(seg(t, t0 + 1.0, t0 + 1.4), () => {
    const tris = Math.round(18432 * seg(t, t0 + 0.9, t0 + 2.2, E.outCubic));
    txt(tris.toLocaleString('en-US'), x + 640, y + 170, { size: 40, w: 800, color: C.ink });
    txt('tris · target 20,000', x + 640, y + 196, { mono: true, size: 12, w: 600, color: C.dim });
    chip(x + 640, y + 240, 'texture ✓', { size: 12, h: 24, color: C.cyan });
    chip(x + 640, y + 274, 'GLB 2.0', { size: 12, h: 24, color: C.cyan });
  });
}
// ---- 제작 패널: 현지화
const KANA = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワン';
function scrambleJa(s, x, y, t, t0, dur, o) {
  const chars = [...s], p = inv(t0, t0 + dur, t); let out = '';
  chars.forEach((c, i) => { const r = i / chars.length; out += r < p ? c : r < p + 0.4 ? KANA[Math.floor(hash(i * 5 + Math.floor(t * 30)) * KANA.length)] : ''; });
  txt(out, x, y, o);
}
function panelL10n(x, y, t, t0) {
  const rows = [['KO', '침입자를 확인했습니다.', null], ['EN', 'Intruder detected.', 'en'], ['JA', '侵入者を確認しました。', 'ja']];
  rows.forEach(([lang, s, k], i) => {
    const yy = y + 150 + i * 62, a = seg(t, t0 + 0.2 + i * 0.1, t0 + 0.5 + i * 0.1); if (a <= 0) return;
    withA(a, () => {
      chip(x + 28, yy - 9, lang, { size: 13, h: 26, w: 800, color: '#05060A', fill: i === 0 ? C.ink : C.lime });
      if (!k) txt(s, x + 96, yy, { size: 28, w: 700, color: C.ink });
      else if (k === 'en') scrambleText(s, x + 96, yy, t, t0 + 0.8, 0.8, { size: 28, w: 700, color: C.lime });
      else scrambleJa(s, x + 96, yy, t, t0 + 1.3, 0.9, { size: 28, w: 700, color: C.lime });
    });
  });
  withA(seg(t, t0 + 1.8, t0 + 2.2), () => {
    chip(x + 540, y + 142, '🔒 락키 → Lockey · 용어집', { size: 13, h: 28, color: C.lime, mono: false, w: 600 });
    chip(x + 540, y + 180, '자리표시자 보존 ✓', { size: 13, h: 28, color: C.dim, mono: false, w: 600 });
    chip(x + 540, y + 218, 'max_len 초과 0', { size: 13, h: 28, color: C.dim, mono: false, w: 600 });
    txt('strings/en.json · strings/ja.json', x + 28, y + 330, { mono: true, size: 13, w: 500, color: C.mute });
  });
}

// ------------------------------------------------------------------ 04 개발
const CODE = [
  "import { loadCSV, loadStrings } from './data.js'",
  "const enemies = await loadCSV('../data/balance/enemies.csv')",
  "const t = await loadStrings(lang)   // strings/en.json",
  "sfx.play('sfx_coin_pickup', { variation: true })",
  "face.play('intro_001', lockey)      // Voice-to-Face",
  "window.__game = state               // QA 훅",
];
const FIX = [['-', 'score += coin.value * 2'], ['+', 'score += coin.value']];
const GAME = { x: 960, y: 262, w: 840, h: 500, speed: 360, px: 170, ground: 402 };
const JUMPS = [0.95, 2.05, 3.25, 4.45, 5.6, 6.7];
function initGameData() {
  if (GAME.coins) return;
  GAME.debris = JUMPS.map(j => (j + 0.31) * GAME.speed);
  GAME.coins = [];
  for (let w = 380; w < 8 * GAME.speed; w += 100) {
    const near = GAME.debris.find(d => Math.abs(d - w) < 70);
    GAME.coins.push({ w, y: near != null ? GAME.ground - 150 : GAME.ground - 44 });
  }
}
function gameState(gt) {
  initGameData();
  const worldX = gt * GAME.speed; let score = 0, coins = 0, pops = [];
  for (const c of GAME.coins) {
    if (worldX >= c.w) {
      const tc = c.w / GAME.speed + 38.0; const val = tc < 41.5 ? 20 : 10;
      score += val; coins++;
      const age = gt - c.w / GAME.speed; if (age < 0.6) pops.push({ c, age, val });
    }
  }
  let jy = 0; for (const j of JUMPS) { const u = (gt - j) / 0.62; if (u >= 0 && u <= 1) jy = Math.sin(Math.PI * u) * 132; }
  return { worldX, score, coins, pops, jy };
}
function drawGame(t) {
  const gt = t - 38.0; const G = GAME; const s = gameState(gt);
  const vx = G.x, vy = G.y + 44, vw = G.w, vh = G.h - 44;
  ctx.save(); rr(vx, vy, vw, vh, 0); ctx.clip();
  const bg = ctx.createLinearGradient(0, vy, 0, vy + vh); bg.addColorStop(0, '#0B1118'); bg.addColorStop(1, '#16202A');
  ctx.fillStyle = bg; ctx.fillRect(vx, vy, vw, vh);
  // 먼 기둥
  for (let k = -1; k < 8; k++) { const x = vx + ((k * 160 - s.worldX * 0.25) % 160 + 160) % 160 + k * 0 + (k * 160) % 1; }
  for (let i = 0; i < 9; i++) { const x = vx + (((i * 150) - s.worldX * 0.25) % 1350 + 1350) % 1350 - 150; ctx.fillStyle = '#131C26'; ctx.fillRect(x, vy, 38, vh); ctx.fillStyle = '#1B2733'; ctx.fillRect(x + 6, vy, 6, vh); }
  // 금고 선반(중경)
  for (let i = 0; i < 7; i++) { const x = vx + (((i * 240) - s.worldX * 0.55) % 1680 + 1680) % 1680 - 240; ctx.fillStyle = '#1E2A36'; ctx.fillRect(x, vy + 150, 170, 10); ctx.fillRect(x, vy + 230, 170, 10);
    for (let k = 0; k < 5; k++) { ctx.fillStyle = hexA(C.gold, 0.25 + 0.2 * hash(i * 7 + k)); ctx.fillRect(x + 14 + k * 30, vy + 136, 16, 14); } }
  // 골렘 실루엣(뒤쪽)
  const gp = seg(gt, 4.6, 6.0, E.outCubic);
  if (gp > 0) { ctx.save(); ctx.globalAlpha = 0.85 * gp; ctx.translate(vx + vw - 150, vy + 330 - gp * 80); ctx.fillStyle = '#0A0F15';
    ctx.beginPath(); ctx.moveTo(-120, 120); ctx.lineTo(-130, 10); ctx.lineTo(-80, -70); ctx.lineTo(0, -95); ctx.lineTo(80, -70); ctx.lineTo(130, 10); ctx.lineTo(120, 120); ctx.closePath(); ctx.fill();
    glowDot(-40, -20, 28, C.amber, gp); glowDot(40, -20, 28, C.amber, gp); ctx.restore(); }
  // 바닥
  ctx.fillStyle = '#0E151C'; ctx.fillRect(vx, vy + G.ground, vw, vh - G.ground);
  line(vx, vy + G.ground, vx + vw, vy + G.ground, hexA(C.lime, 0.7), 2);
  for (let i = 0; i < 16; i++) { const x = vx + ((i * 60 - s.worldX) % 960 + 960) % 960 - 60; line(x, vy + G.ground + 4, x - 30, vy + vh, 'rgba(255,255,255,0.06)', 1); }
  // 잔해
  G.debris.forEach((dw, i) => {
    const sx = dw - s.worldX + G.px; if (sx < -80 || sx > vw + 80) return;
    const land = clamp((vw + 40 - sx) / 220); const e = E.inQuart(land);
    const dy = lerp(-80, G.ground - 44, e);
    ctx.save(); ctx.translate(vx + sx, vy + dy); ctx.rotate((1 - e) * 1.2 + i);
    ctx.fillStyle = '#6B5B4A'; ctx.fillRect(-24, -20, 48, 40); ctx.fillStyle = '#8A7560'; ctx.fillRect(-24, -20, 48, 8); ctx.restore();
    if (land >= 1) { const since = (vw + 40 - sx - 220) / G.speed; if (since < 0.4) { ctx.save(); ctx.globalAlpha = 0.5 * (1 - since / 0.4); ctx.fillStyle = '#A89A88'; for (let k = 0; k < 6; k++) ctx.fillRect(vx + sx - 40 + k * 14, vy + G.ground - 8 - since * 60 * hash(k + i), 6, 6); ctx.restore(); } }
  });
  // 코인
  G.coins.forEach(c => {
    const sx = c.w - s.worldX + G.px; if (sx < -30 || sx > vw + 30) return;
    if (s.worldX >= c.w) return;
    const spin = Math.abs(Math.cos(gt * 6 + c.w));
    ctx.save(); ctx.translate(vx + sx, vy + c.y); glowDot(0, 0, 26, C.gold, 0.5);
    ctx.fillStyle = C.gold; ctx.beginPath(); ctx.ellipse(0, 0, 12 * spin + 2, 12, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  });
  // 점수 팝업
  s.pops.forEach(({ c, age, val }) => {
    const bug = val === 20;
    txt(`+${val}`, vx + G.px + 10, vy + c.y - 20 - age * 80, { size: 24, w: 800, color: bug ? C.red : C.gold, alpha: 1 - age / 0.6 });
    ctx.save(); ctx.globalAlpha = 1 - age / 0.6; ctx.strokeStyle = C.gold; ctx.lineWidth = 2; circle(vx + G.px, vy + c.y, 10 + age * 50, null, C.gold, 2); ctx.restore();
  });
  // 플레이어
  const py = vy + G.ground - s.jy, px = vx + G.px, run = Math.sin(gt * 18);
  for (let k = 1; k <= 4; k++) { ctx.save(); ctx.globalAlpha = 0.12 / k; ctx.fillStyle = C.lime; rr(px - 17 - k * 14, py - 72, 34, 44, 8); ctx.fill(); ctx.restore(); }
  ctx.save(); ctx.strokeStyle = C.lime; ctx.lineWidth = 7; ctx.lineCap = 'round';
  if (s.jy < 2) { ctx.beginPath(); ctx.moveTo(px - 4, py - 30); ctx.lineTo(px - 4 + run * 14, py); ctx.moveTo(px + 4, py - 30); ctx.lineTo(px + 4 - run * 14, py); ctx.stroke(); }
  else { ctx.beginPath(); ctx.moveTo(px - 4, py - 30); ctx.lineTo(px - 14, py - 10); ctx.moveTo(px + 4, py - 30); ctx.lineTo(px + 16, py - 14); ctx.stroke(); }
  ctx.restore();
  ctx.fillStyle = C.lime; rr(px - 17, py - 72, 34, 44, 8); ctx.fill();
  circle(px + 2, py - 88, 15, C.lime); ctx.fillStyle = '#05060A'; ctx.fillRect(px + 2, py - 93, 14, 6);
  // 락키 음성 자막
  const sub = seg(gt, 0.6, 0.8) * (1 - seg(gt, 2.6, 2.8));
  if (sub > 0) withA(sub, () => { panel(vx + 230, vy + 28, 380, 52, { fill: 'rgba(5,6,10,0.8)', stroke: hexA(C.violet, 0.6), r: 26 });
    circle(vx + 258, vy + 54, 10, C.violet); ctx.fillStyle = '#05060A'; ctx.fillRect(vx + 252, vy + 52 + 0, 12, 2 + jaw(t) * 5);
    txt('락키  침입자를 확인했습니다.', vx + 280, vy + 61, { size: 20, w: 700, color: C.ink }); });
  // HUD
  txt(`SCORE ${String(s.score).padStart(5, '0')}`, vx + 24, vy + 44, { mono: true, size: 22, w: 700, color: C.ink });
  circle(vx + 34, vy + 72, 8, C.gold); txt(`× ${s.coins}`, vx + 48, vy + 79, { mono: true, size: 17, w: 700, color: C.gold });
  txt('HP', vx + vw - 196, vy + 44, { mono: true, size: 16, w: 700, color: C.dim }); ctx.fillStyle = 'rgba(255,255,255,0.12)'; ctx.fillRect(vx + vw - 164, vy + 32, 140, 14); ctx.fillStyle = C.coral; ctx.fillRect(vx + vw - 164, vy + 32, 140, 14);
  // QA 탐침
  const probe = seg(t, 39.7, 39.95) * (1 - seg(t, 41.6, 41.8));
  if (probe > 0) withA(probe, () => {
    ctx.save(); ctx.setLineDash([6, 5]); ctx.strokeStyle = C.red; ctx.lineWidth = 2; rr(vx + 14, vy + 18, 214, 36, 6); ctx.stroke();
    rr(vx + vw - 204, vy + 22, 190, 32, 6); ctx.strokeStyle = hexA(C.lime, 0.7); ctx.stroke(); ctx.restore();
    chip(vx + 18, vy + 104, 'data-testid="lbl_score"', { size: 12, h: 24, color: '#05060A', fill: C.red });
    const cxp = vx + lerp(420, 120, seg(t, 39.7, 40.0, E.outCubic)), cyp = vy + lerp(260, 36, seg(t, 39.7, 40.0, E.outCubic));
    line(cxp - 16, cyp, cxp + 16, cyp, C.red, 2); line(cxp, cyp - 16, cxp, cyp + 16, C.red, 2); circle(cxp, cyp, 9, null, C.red, 2);
  });
  ctx.restore();
}

const BOOT = [
  [36.6, '$ python3 -m http.server --directory games/coin-runner', C.ink],
  [36.85, 'Serving HTTP on 0.0.0.0 port 8000 …', C.dim],
  [37.0, 'GET /data/balance/enemies.csv              200', C.dim],
  [37.1, 'GET /data/strings/ko.json                  200', C.dim],
  [37.2, 'GET /assets/audio/sfx/sfx_coin_pickup_01.wav 200', C.dim],
  [37.3, 'GET /assets/audio/voice/korean/intro_001.wav 200', C.dim],
  [37.4, 'GET /assets/anim/face/intro_001.json       200', C.dim],
  [37.5, 'GET /assets/models/mdl_vault_golem.glb      200', C.dim],
  [37.68, 'window.__game ready ✓', C.lime],
];
function drawBoot(t) {
  const G = GAME, x = G.x + 30, y0 = G.y + 92;
  BOOT.forEach(([bt, s, col], i) => {
    if (t < bt) return;
    const n = Math.min(s.length, Math.floor((t - bt) * 160));
    const shown = s.slice(0, n);
    const m = shown.match(/^(.*?)(200)$/);
    if (m) { txt(m[1], x, y0 + i * 34, { mono: true, size: 16, w: 500, color: col }); txt('200', x + tw(m[1], 500, 16, true), y0 + i * 34, { mono: true, size: 16, w: 700, color: C.green }); }
    else txt(shown, x, y0 + i * 34, { mono: true, size: 16, w: i === 0 || i === 8 ? 700 : 500, color: col });
  });
  const p = seg(t, 36.9, 37.8, E.inOutCubic);
  const bx = G.x + 30, by = G.y + G.h - 56, bw = G.w - 60;
  ctx.fillStyle = 'rgba(255,255,255,0.08)'; ctx.fillRect(bx, by, bw, 10);
  ctx.fillStyle = C.lime; ctx.fillRect(bx, by, bw * p, 10);
  txt(`에셋 ${Math.round(22 * p)} / 22 불러오는 중`, bx, by - 14, { size: 16, w: 700, color: C.ink });
  txt(`${Math.round(p * 100)}%`, bx + bw, by - 14, { mono: true, size: 16, w: 700, color: C.lime, align: 'right' });
  if (Math.floor(t * 2.4) % 2 === 0 && t < 37.7) { const last = BOOT.filter(b => t >= b[0]).length - 1; ctx.fillStyle = C.lime; ctx.fillRect(x + tw(BOOT[Math.max(0, last)][1].slice(0, Math.floor((t - BOOT[Math.max(0, last)][0]) * 160)), 500, 16, true) + 4, y0 + last * 34 - 15, 9, 18); }
}
function sceneDevelop(t) {
  maskUp('개발', 120, 196, seg(t, 36.0, 36.5), { size: 58, w: 800, color: C.ink });
  withA(seg(t, 36.2, 36.6), () => { txt('04 · 엔지니어 ⇄ QA · 모듈마다 바로 검증', 124, 236, { mono: true, size: 16, w: 600, color: C.lime, track: 2 }); chip(W - 120, 222, 'engine: web · Phaser 3', { size: 14, h: 28, color: C.lime, align: 'right' }); });
  // 코드 편집기
  const ep = seg(t, 36.1, 36.5, E.outExpo);
  withA(ep, () => {
    const x = 120, y = 262, w = 800, h = 480;
    panel(x, y, w, h, { fill: '#0A0C11', stroke: 'rgba(255,255,255,0.12)' });
    [C.coral, C.amber, C.green].forEach((c, i) => circle(x + 26 + i * 22, y + 24, 6, c));
    chip(x + 110, y + 24, 'web/src/main.js', { size: 13, h: 26, color: C.ink });
    chip(x + 290, y + 24, 'gameplay-engineer · opus', { size: 13, h: 26, color: C.lime, fill: hexA(C.lime, 0.1) });
    let chars = Math.floor((t - 36.35) * 140);
    CODE.forEach((s, i) => {
      const yy = y + 86 + i * 40;
      txt(String(i + 1).padStart(2, ' '), x + 20, yy, { mono: true, size: 15, w: 500, color: C.mute });
      if (chars <= 0) return;
      const part = s.slice(0, Math.min(s.length, chars)); chars -= s.length;
      codeLine(part, x + 62, yy, { size: 16 });
      if (chars < 0 && chars > -s.length) { ctx.fillStyle = C.lime; ctx.fillRect(x + 62 + tw(part, 500, 16, true) + 2, yy - 16, 10, 20); }
    });
    // 버그 수정 diff
    const fp = seg(t, 40.95, 41.1);
    if (fp > 0) FIX.forEach(([sg, s], i) => {
      const yy = y + 86 + (CODE.length + 0.5 + i) * 40, a = seg(t, 41.0 + i * 0.15, 41.2 + i * 0.15);
      withA(a, () => { ctx.fillStyle = sg === '-' ? hexA(C.red, 0.18) : hexA(C.green, 0.18); ctx.fillRect(x + 2, yy - 26, w - 4, 36);
        txt(sg, x + 30, yy, { mono: true, size: 17, w: 800, color: sg === '-' ? C.red : C.green });
        codeLine(s, x + 62, yy, { size: 16 }); });
    });
  });
  // 모듈 진행
  const mods = ['코어 루프', '충돌 · 점프', 'HUD · 문자열', '사운드 · 음성', '얼굴 애니메이션'];
  withA(seg(t, 41.8, 42.1), () => {
    mods.forEach((m, i) => {
      const yy = 790 + i * 38, p = seg(t, 42.0 + i * 0.6, 42.5 + i * 0.6, E.outCubic);
      txt(m, 124, yy + 6, { size: 19, w: 700, color: p >= 1 ? C.ink : C.dim });
      ctx.fillStyle = 'rgba(255,255,255,0.08)'; ctx.fillRect(330, yy - 6, 470, 10);
      ctx.fillStyle = p >= 1 ? C.lime : hexA(C.lime, 0.6); ctx.fillRect(330, yy - 6, 470 * p, 10);
      if (p >= 1) { const cp = seg(t, 42.5 + i * 0.6, 42.75 + i * 0.6, E.outBack); at(840, yy - 1, cp, 0, () => chip(0, 0, '✓ qa', { align: 'center', size: 12, h: 24, w: 800, color: '#05060A', fill: C.lime })); }
    });
  });
  // 게임 창: 36.4 서버 부팅 → 38.0 브라운관처럼 켜지며 게임 시작
  const gp = seg(t, 36.4, 36.85, E.outExpo);
  if (gp > 0) {
    const G = GAME;
    at(G.x + G.w / 2, G.y + G.h / 2, lerp(0.9, 1, gp), 0, () => withA(clamp(gp * 2), () => {
      ctx.translate(-G.x - G.w / 2, -G.y - G.h / 2);
      panel(G.x, G.y, G.w, G.h, { fill: '#07090D', stroke: hexA(C.lime, 0.4), lw: 1.5, glow: 40, glowColor: hexA(C.lime, 0.18) });
      txt('coin-runner — localhost:8000/web/', G.x + 20, G.y + 29, { mono: true, size: 14, w: 600, color: C.dim });
      chip(G.x + G.w - 16, G.y + 22, 'game-qa · Playwright', { size: 12, h: 24, color: C.red, fill: hexA(C.red, 0.12), align: 'right' });
      if (t < 38.0) drawBoot(t); else drawGame(t);
      const crt = 1 - seg(t, 38.0, 38.35);
      if (t >= 38.0 && crt > 0) { ctx.save(); ctx.globalAlpha = crt; ctx.fillStyle = '#fff'; ctx.fillRect(G.x, G.y + 44 + (G.h - 44) / 2 * (1 - crt), G.w, (G.h - 44) * crt); ctx.restore(); }
    }));
  }
  // 버그 카드
  const bp = seg(t, 40.0, 40.3, E.outBack), bout = seg(t, 42.2, 42.5, E.inCubic);
  if (bp > 0 && bout < 1) {
    const ok = t >= 41.5, col = ok ? C.green : C.red;
    at(1380 + bout * 800, 880, bp, 0, () => {
      panel(-420, -86, 840, 172, { fill: ok ? '#0B140E' : '#160A0C', stroke: col, lw: 2, glow: 40, glowColor: hexA(col, 0.4) });
      txt('BUG-012', -390, -38, { mono: true, size: 20, w: 800, color: col });
      chip(-270, -45, 'S2', { size: 13, h: 24, w: 800, color: '#05060A', fill: col });
      txt('game-qa → engineer', 390, -38, { mono: true, size: 14, w: 600, color: C.dim, align: 'right' });
      txt('코인 1개에 점수가 두 번 올라간다', -390, 8, { size: 28, w: 800, color: C.ink });
      txt('기대 +10 · 실제 +20 · data/balance/items.csv  ↔  web/src/score.js:42', -390, 48, { mono: true, size: 14, w: 500, color: C.dim });
      const vp = seg(t, 41.5, 41.7, E.outBackBig);
      if (vp > 0) at(300, 18, vp * 1, -0.12, () => { ctx.save(); ctx.strokeStyle = C.green; ctx.lineWidth = 5; rr(-110, -34, 220, 68, 10); ctx.stroke(); ctx.restore(); txt('VERIFIED', 0, 11, { size: 32, w: 800, color: C.green, align: 'center', track: 3 }); });
    });
  }
  // 버그 → 엔지니어 패킷
  const pk = inv(40.5, 40.9, t);
  if (pk > 0 && pk < 1) { const e = E.inOutCubic(pk); for (let k = 0; k < 8; k++) { const u = clamp(e - k * 0.03); glowDot(lerp(1100, 700, u), lerp(800, 560, u) - Math.sin(Math.PI * u) * 120, 28 - k * 3, k ? C.red : '#fff', 1 - k / 8); } }
  // 빌드 동결
  withA(seg(t, 45.0, 45.25), () => chip(GAME.x + GAME.w, GAME.y + GAME.h + 34, 'BUILD FROZEN · freeze_04.sha', { size: 14, h: 30, w: 700, color: '#05060A', fill: C.lime, align: 'right' }));
}

// ------------------------------------------------------------------ 05 출시
const REPORTS = [
  { t: '에셋 전수 감사', r: 'asset-qa', v: '22/22', c: C.cyan }, { t: '회귀 테스트', r: 'game-qa', v: '42 PASS', c: C.lime },
  { t: '밸런스 구현 대조', r: 'balance-analyst', v: 'CSV = 코드', c: C.violet }, { t: '스토어 이미지', r: 'marketing-artist', v: 'capsule ×3', c: C.coral },
];
const CHECKS = [['버그 S1·S2 미해결', '0건'], ['P0 에셋 검증 통과', '22 / 22'], ['데이터 정합성 불일치', '0건'], ['현지화 누락 · 글자 수 초과', '0건'], ['밸런스 판정', 'PASS'], ['크레딧 사용 / 예산', '1,118 / 1,364']];
function sceneRelease(t) {
  const dark = seg(t, 50.2, 50.3) * (1 - seg(t, 50.5, 50.52));
  const go = t >= 50.5;
  if (!go) {
    const push = 1 + seg(t, 49.0, 50.25, E.inCubic) * 0.06;
    ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(push, push); ctx.translate(-W / 2, -H / 2); ctx.globalAlpha *= 1 - dark;
    planLeft(t, { no: '05', t0: 46.0 }, '출시', 'SHIP · 게임 디렉터 판정', C.coral);
    withA(seg(t, 46.6, 47.0), () => txt('계약서 9절 기준표로만 판정한다.', 124, 590, { size: 20, w: 500, color: C.dim }));
    REPORTS.forEach((rp, k) => {
      const p = seg(t, 46.25 + k * 0.4, 46.7 + k * 0.4, E.outBack); if (p <= 0) return;
      const x = 760 + k * 265, y = 140;
      at(x + 122, y + 110, p, 0, () => {
        panel(-122, -110, 244, 220, { fill: '#0C0D13', stroke: hexA(rp.c, 0.55) });
        txt(rp.r, -100, -70, { mono: true, size: 12, w: 600, color: rp.c });
        txt(rp.t, -100, -36, { size: 21, w: 800, color: C.ink });
        if (k === 3) { // 스토어 캡슐 미리보기
          const g = ctx.createLinearGradient(-100, -10, 100, 80); g.addColorStop(0, '#2A1420'); g.addColorStop(1, '#0F2230');
          rr(-100, -12, 200, 92, 8); ctx.fillStyle = g; ctx.fill();
          circle(60, 40, 14, C.gold); circle(30, 58, 8, C.gold);
          txt('COIN RUNNER', -86, 38, { size: 22, w: 800, color: C.ink });
          ctx.fillStyle = C.lime; rr(-86, 50, 14, 20, 3); ctx.fill();
        } else txt(rp.v, -100, 50, { size: 34, w: 800, color: rp.c });
        txt('✓ 보고서 제출', -100, 96, { size: 14, w: 700, color: C.green });
      });
    });
    // 기준표
    withA(seg(t, 47.7, 48.0), () => {
      const x = 760, y = 400, w = 1040;
      panel(x, y, w, 490, { fill: 'rgba(255,94,98,0.05)', stroke: hexA(C.coral, 0.4) });
      txt('RELEASE CRITERIA', x + 32, y + 46, { mono: true, size: 16, w: 700, color: C.coral, track: 4 });
      CHECKS.forEach(([l, v], i) => {
        const ct = 48.0 + i * BEAT * 2 / 3, yy = y + 108 + i * 64;
        const on = t >= ct, cp = seg(t, ct, ct + 0.2, E.outBackBig);
        if (on) { ctx.fillStyle = hexA(C.green, 0.08 * (1 - inv(ct, ct + 0.6, t)) + 0.03); ctx.fillRect(x + 2, yy - 34, w - 4, 54); }
        circle(x + 52, yy - 8, 18, on ? C.green : 'rgba(255,255,255,0.05)', on ? null : 'rgba(255,255,255,0.25)', 1.5);
        if (on) at(x + 52, yy - 8, cp, 0, () => txt('✓', 0, 8, { size: 22, w: 800, color: '#05060A', align: 'center' }));
        txt(l, x + 92, yy, { size: 25, w: 700, color: on ? C.ink : C.dim });
        withA(on ? 1 : 0.3, () => txt(v, x + w - 34, yy, { size: 25, w: 800, color: on ? C.green : C.dim, align: 'right' }));
      });
    });
    ctx.restore();
    // 판정 직전의 수렴선
    const conv = seg(t, 49.1, 50.25, E.inCubic);
    if (conv > 0) { ctx.save(); ctx.globalCompositeOperation = 'lighter'; const r = rng(49); for (let k = 0; k < 40; k++) { const a = r() * Math.PI * 2, d0 = 1400 * (1 - conv) + 200 * r(); ctx.globalAlpha = 0.25 * conv; line(W / 2 + Math.cos(a) * d0, H / 2 + Math.sin(a) * d0, W / 2 + Math.cos(a) * (d0 + 180), H / 2 + Math.sin(a) * (d0 + 180), k % 2 ? C.coral : '#fff', 2); } ctx.restore(); }
    if (dark > 0) withA(dark, () => { ctx.fillStyle = '#000'; ctx.fillRect(-50, -50, W + 100, H + 100); txt('게임 디렉터 판정 중', W / 2, H / 2 + 10, { mono: true, size: 18, w: 600, color: C.dim, align: 'center', track: 6 }); });
    return;
  }
  // GO
  const d = t - 50.5;
  const ray = Math.max(0, 1 - d * 0.5);
  ctx.save(); ctx.translate(W / 2, 520); ctx.rotate(d * 0.15); ctx.globalCompositeOperation = 'lighter';
  for (let k = 0; k < 24; k++) { ctx.rotate(Math.PI * 2 / 24); ctx.globalAlpha = 0.07 + 0.05 * ray; ctx.fillStyle = k % 2 ? C.coral : C.amber; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(1500, -70); ctx.lineTo(1500, 70); ctx.closePath(); ctx.fill(); }
  ctx.restore();
  shockRing(W / 2, 520, t, 50.5, C.coral, { r: 1500, lw: 16, life: 1.0 });
  shockRing(W / 2, 520, t, 50.58, '#fff', { r: 1200, lw: 8, life: 0.8 });
  shockRing(W / 2, 520, t, 50.7, C.amber, { r: 1000, lw: 5, life: 0.9 });
  burst(W / 2, 520, t, 50.5, 160, 505, [C.coral, C.amber, C.lime, C.cyan, C.violet, '#fff'], { speed: 2600, life: 1.5, grav: true });
  const p = seg(t, 50.5, 50.72, E.outExpo);
  const pulse = 1 + kickPulse(t) * 0.03;
  at(W / 2, 520, lerp(2.2, 1, p) * pulse, 0, () => {
    txt('GO', 0, 170, { size: 480, w: 800, color: C.coral, align: 'center', glow: 80, glowColor: hexA(C.coral, 0.9), track: -10, blur: (1 - p) * 30 });
    txt('GO', 0, 170, { size: 480, w: 800, color: '#FFFFFF', align: 'center', track: -10, alpha: 0.9 * (1 - seg(t, 50.55, 50.9)) });
  });
  withA(seg(t, 50.75, 51.1), () => {
    txt('출시 가능', W / 2, 800, { size: 44, w: 800, color: C.ink, align: 'center' });
    txt('RELEASE_REPORT.md · 기준 6/6 통과', W / 2, 850, { mono: true, size: 18, w: 600, color: C.dim, align: 'center', track: 3 });
  });
}

// ------------------------------------------------------------------ 엔딩
const MONTAGE = [['team', 12.3, C.violet], ['plan', 19.7, C.violet], ['spec', 24.4, C.amber], ['produce', 30.8, C.cyan], ['produce', 34.8, C.cyan], ['develop', 40.3, C.lime], ['release', 49.8, C.coral], ['release', 51.3, C.coral]];
function sceneOutro(t) {
  if (t < 54.0) {
    const i = Math.min(7, Math.floor((t - 52) / 0.25)), [name, ft, col] = MONTAGE[i];
    const lt = (t - 52) - i * 0.25;
    drawBackground(ft, { accent: col });
    const z = 1.06 + lt * 0.35;
    ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.rotate((i % 2 ? 1 : -1) * 0.012); ctx.translate(-W / 2, -H / 2);
    drawSceneAt(name, ft + lt * 0.8);
    ctx.restore();
    // 색 입힌 막
    ctx.save(); ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = 0.35; ctx.fillStyle = col; ctx.fillRect(0, 0, W, H); ctx.restore();
    if (lt < 0.035) { ctx.save(); ctx.globalAlpha = 0.6; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
    // 몽타주 표식: 작은 단계 번호만
    chip(W / 2, 70, ['THE TEAM', '01 기획', '02 명세', '03 제작', '03 제작', '04 개발', '05 출시', '05 출시'][i], { align: 'center', size: 16, w: 800, h: 34, color: '#05060A', fill: col });
    return;
  }
  // 최종 로고
  const up = seg(t, 55.3, 55.8, E.inOutCubic);
  withA(1 - up, () => {
    ctx.save(); ctx.translate(0, -up * 120);
    staggerText('한 줄의 아이디어에서', W / 2, 470, t, 54.0, { size: 84, w: 800, color: C.ink, align: 'center', per: 0.035, track: -2 });
    const l2 = '출시 판정까지.';
    staggerText(l2, W / 2, 590, t, 54.4, { size: 84, w: 800, color: C.ink, align: 'center', per: 0.035, track: -2 });
    const tot = tw(l2, 800, 84, false, -2), hiW = tw('출시 판정', 800, 84, false, -2);
    ctx.save(); ctx.beginPath(); ctx.rect(W / 2 - tot / 2, 480, hiW * seg(t, 54.8, 55.15, E.inOutCubic), 140); ctx.clip();
    txt('출시 판정', W / 2 - tot / 2, 590, { size: 84, w: 800, color: C.coral, track: -2 }); ctx.restore();
    ctx.restore();
  });
  const fin = 1 + seg(t, 58.0, 58.12, E.outCubic) * 0.03 - seg(t, 58.12, 59.8, E.inOutSine) * 0.0 + (t > 58 ? (t - 58) * 0.02 : 0);
  ctx.save(); ctx.translate(W / 2, 520); ctx.scale(fin, fin); ctx.translate(-W / 2, -520);
  drawLogotype(t, 55.55, 500, { size: 210 });
  withA(seg(t, 56.1, 56.5), () => {
    const items = ['15 에이전트', '17 스킬', '5단계', '명령 한 줄'];
    let tot = 0; const gap = 56; items.forEach(s => tot += tw(s, 700, 30)); tot += gap * (items.length - 1);
    let x = W / 2 - tot / 2;
    items.forEach((s, i) => { txt(s, x, 812, { size: 30, w: 700, color: i === 3 ? C.lime : C.ink }); x += tw(s, 700, 30) + gap; if (i < 3) circle(x - gap / 2, 802, 4, C.mute); });
  });
  ctx.restore();
  withA(seg(t, 56.6, 57.0), () => {
    txt('MOTION GRAPHICS & DIRECTION — CLAUDE', W / 2, 948, { mono: true, size: 16, w: 700, color: C.dim, align: 'center', track: 6 });
    txt('Harness v2 on Claude Code · VARCO API Platform', W / 2, 980, { size: 16, w: 500, color: C.mute, align: 'center', track: 1 });
  });
  shockRing(W / 2, 480, t, 58.0, '#ffffff', { r: 1400, lw: 6, life: 1.0, alpha: 0.5 });
}
