// ============================================================================
// 장면 B: 02 명세 · 03 제작 · 04 개발
// ============================================================================
let MESH = null;
function initScenesB() {
  MESH = buildGolemMesh();
  addScene('spec', sceneSpec);
  addScene('produce', sceneProduce);
  addScene('develop', sceneDevelop);
}

// ------------------------------------------------------------------ 02 명세
const MANIFEST_LINES = [
  '{', '  "game": "coin-runner",', '  "varco_mode": "live",', '  "budget_credits": null,', '  "assets": [',
  '    { "id": "sfx_coin_pickup",', '      "category": "sfx", "priority": "P0",', '      "owner": "sound-designer",', '      "steps": [', '        { "api": "sound.text2sound" },', '        { "api": "sound.variation" } ],', '      "acceptance": { "peak_dbfs": -1.0 } },',
  '    { "id": "amb_vault_collapse",', '      "category": "ambience",', '      "steps": [', '        { "api": "sound.text2sound" },', '        { "api": "sound.mono2stereo" },', '        { "api": "sound.looping" } ] },',
  '    { "id": "vo_intro",', '      "category": "voice_line",', '      "lines": ["intro_001", "…"],', '      "steps": [', '        { "api": "tts.standard" },', '        { "api": "face.blendshape" } ] },',
  '    { "id": "mdl_vault_golem",', '      "category": "model_3d",', '      "steps": [', '        { "api": "3d.image_to_3d" } ] },',
  '    { "id": "l10n_en",', '      "category": "localization",', '      "steps": [', '        { "api": "mt.translate" } ] },',
  '    { "id": "bgm_title",', '      "steps": [{ "api": "manual.unity_music" }] },', '    { "id": "mkt_capsule", "phase": "release" }', '  ]', '}',
];
const BINS = [['효과음', 10, C.cyan], ['환경음', 3, C.cyan], ['대사 음성', 4, C.violet], ['3D 모델', 2, C.amber], ['현지화', 2, C.lime], ['마케팅', 3, C.coral]];
function sceneSpec(t) {
  const T = S0('spec'), l = t - T;
  planLeft(t, '02', T, '명세', 'SPEC · 서브에이전트 1명 · 크레딧 승인', C.amber);
  stepList(120, 612, t, [
    { s: '기획 문서에서 에셋 뽑기', show: T + 0.3, done: T + 1.6 }, { s: 'VARCO API 호출 순서 정하기', show: T + 0.45, done: T + 2.8 },
    { s: '매니페스트 검사', show: T + 0.6, done: T + 4.6 }, { s: '크레딧 견적', show: T + 0.75, done: T + 8.2 },
    { s: '사용자 승인', show: T + 0.9, done: T + 11.0 },
  ], C.amber, 44);
  const est = seg(l, 6.5, 6.85, E.inOutCubic);
  const dimBack = 1 - est * 0.8;
  // 매니페스트 코드
  withA(seg(l, 0.05, 0.45) * dimBack, () => {
    const x = 760, y = 140, w = 560, h = 660;
    panel(x, y, w, h, { fill: '#0B0C12', stroke: hexA(C.amber, 0.35) });
    txt('02_producer_manifest.json', x + 24, y + 38, { mono: true, size: 14, w: 600, color: C.amber });
    chip(x + w - 20, y + 32, 'asset-producer · sonnet', { size: 11, h: 22, padX: 8, color: C.sonnet, fill: hexA(C.sonnet, 0.1), align: 'right' });
    ctx.save(); rr(x + 1, y + 58, w - 2, h - 60, 12); ctx.clip();
    const scroll = Math.min(Math.max(0, (l - 0.3) * 150), MANIFEST_LINES.length * 28 - 540);
    MANIFEST_LINES.forEach((s, i) => { const yy = y + 96 + i * 28 - scroll; if (yy > y + 40 && yy < y + h + 20) codeLine(s, x + 24, yy, { size: 16 }); });
    ctx.restore();
    ctx.fillStyle = hexA(C.amber, 0.08); ctx.fillRect(x + 1, y + 300 + Math.sin(t * 3) * 120, w - 2, 28);
  });
  // 분류함
  withA(seg(l, 0.2, 0.5) * dimBack, () => {
    BINS.forEach(([name, n, col], k) => {
      const x = 1350, y = 140 + k * 108, a = seg(l, 0.25 + k * 0.05, 0.55 + k * 0.05);
      withA(a, () => {
        panel(x, y, 450, 92, { fill: 'rgba(255,255,255,0.03)', stroke: hexA(col, 0.3) });
        ctx.fillStyle = col; ctx.fillRect(x, y + 16, 4, 60);
        txt(name, x + 28, y + 56, { size: 26, w: 700, color: C.ink });
        const got = Math.round(n * seg(l, 0.8 + k * 0.18, 3.0, E.outCubic));
        txt(String(got), x + 420, y + 62, { size: 46, w: 800, color: col, align: 'right' });
      });
    });
    withA(seg(l, 2.4, 2.8), () => txt('+ 배경음악 1 · 수동 제작(Unity 플러그인) → 합계 25', 1352, 794, { size: 16, w: 600, color: C.dim }));
  });
  // 칩이 코드에서 분류함으로 날아간다
  for (let k = 0; k < 12; k++) {
    const t0 = 0.8 + k * 0.18, u = inv(t0 - 0.3, t0, l); if (u <= 0 || u >= 1) continue;
    const b = k % 6, sx = 1300, sy = 300 + (k * 97) % 420, ex = 1380, ey = 186 + b * 108;
    const e = E.inOutCubic(u);
    const px = lerp(sx, ex, e), py = lerp(sy, ey, e) - Math.sin(Math.PI * e) * 60;
    glowDot(px, py, 30, BINS[b][2], 1); chip(px, py, ['sfx', 'amb', 'vo', 'mdl', 'l10n', 'mkt'][b] + '_' + k, { size: 12, h: 22, padX: 8, color: '#05060A', fill: BINS[b][2], align: 'center' });
  }
  // 검사 스크립트
  withA(seg(l, 3.9, 4.2) * dimBack, () => {
    const x = 760, y = 820, w = 1040, h = 88;
    panel(x, y, w, h, { fill: '#0A0C11', stroke: 'rgba(255,255,255,0.14)', r: 14 });
    const L = [[4.2, '$ python3 validate_manifest.py 02_producer_manifest.json', '✓ 오류 0 · 에셋 25', 4.6],
      [5.4, '$ python3 estimate_cost.py 02_producer_manifest.json --write', '→ 1,240 크레딧 · 단가 미공개 3건', 6.0]];
    L.forEach(([lt, cmd, res, rt], i) => {
      const yy = y + 36 + i * 32, s = typed(cmd, l, lt, 140); if (!s) return;
      txt(s, x + 24, yy, { mono: true, size: 15, w: 500, color: C.ink });
      if (l >= rt) withA(seg(l, rt, rt + 0.2), () => txt(res, x + w - 24, yy, { mono: true, size: 15, w: 700, color: i ? C.amber : C.green, align: 'right' }));
    });
  });
  // 크레딧 견적
  if (est > 0) {
    const cx = 1280, cy = 470, out = seg(l, 8.8, 9.0);
    withA(est * (1 - out * 0.7), () => {
      txt('예상 크레딧', cx, cy - 196, { size: 28, w: 700, color: C.dim, align: 'center' });
      const v = Math.round(1240 * seg(l, 6.8, 8.2, E.outCubic));
      txt(v.toLocaleString('en-US'), cx, cy, { size: 200, w: 800, color: C.amber, align: 'center', glow: 40, glowColor: hexA(C.amber, 0.5), track: -6 });
      const bw = 820, bx = cx - bw / 2, by = cy + 60;
      const parts = [['P0', 780, C.amber], ['P1', 330, mixHex(C.amber, '#000000', 0.35)], ['P2', 130, mixHex(C.amber, '#000000', 0.6)]];
      let acc = 0; const g = seg(l, 7.0, 7.9, E.outCubic);
      parts.forEach(([lb, n, col]) => {
        const w0 = bw * n / 1240; ctx.fillStyle = col; ctx.fillRect(bx + acc * g, by, w0 * g - 4, 18);
        withA(g, () => txt(`${lb} ${n}`, bx + acc * g, by + 50, { mono: true, size: 16, w: 700, color: C.ink }));
        acc += w0;
      });
      withA(seg(l, 7.7, 8.0), () => txt('번역 · 얼굴 애니메이션 · 연기 변환은 단가가 공개되지 않아 합계에서 빠집니다', cx, by + 100, { size: 18, w: 500, color: C.dim, align: 'center' }));
    });
  }
  // 사람 확인 ②
  const zoom = 1 + seg(l, 13.3, 13.75, E.inExpo) * 3;
  ctx.save(); ctx.translate(1280, 560); ctx.scale(zoom, zoom); ctx.translate(-1280, -560);
  const tg = { x: 0, y: 0 };
  const btns = askModal(t, {
    cx: 1280, cy: 540, w: 900, h: 420, t0: T + 9.0, head: 'AskUserQuestion · 사람 확인 2/2',
    title: '크레딧 승인이 필요합니다', sub: '예상 1,240 · 권장 예산 1,364 (여유 10%) · P0 780 · P1 330 · P2 130',
    buttons: [{ s: '전체 승인', primary: true }, { s: 'P0만 승인' }, { s: '드라이런' }, { s: '매니페스트 수정' }], press: { i: 0, t: T + 10.95 }, rowY: 20, color: C.amber,
    extra: () => {
      const y = 120, on = l >= 10.25;
      line(-410, y - 42, 410, y - 42, 'rgba(255,255,255,0.08)', 1);
      txt('단가 미공개 호출 3건(번역 · 얼굴 애니메이션 · 연기 변환)도 실행할까요?', -410, y + 8, { size: 19, w: 600, color: C.ink });
      const sw = seg(l, 10.25, 10.4, E.outCubic);
      rr(330, y - 14, 64, 32, 16); ctx.fillStyle = on ? C.amber : 'rgba(255,255,255,0.15)'; ctx.fill();
      circle(lerp(346, 378, sw), y + 2, 12, on ? '#05060A' : '#fff');
      tg.x = 1280 + 362; tg.y = 540 + y + 2;
    },
  });
  if (btns) {
    const b = btns[0];
    const c1 = seg(l, 9.6, 10.1, E.outCubic), c2 = seg(l, 10.45, 10.9, E.outCubic);
    const mx = lerp(lerp(1680, tg.x + 4, c1), b.x + 10, c2), my = lerp(lerp(900, tg.y + 6, c1), b.y + 8, c2);
    const press = l > 10.5 ? seg(l, 10.95, 11.0) * (1 - seg(l, 11.0, 11.12)) : seg(l, 10.2, 10.25) * (1 - seg(l, 10.25, 10.37));
    withA(seg(l, 9.3, 9.5), () => drawCursor(mx, my, 1 - press * 0.15));
    const sp = seg(l, 11.2, 11.36, E.inExpo);
    if (sp > 0) {
      shockRing(1500, 700, t, T + 11.36, C.amber, { r: 700, lw: 8 });
      withA(clamp(sp * 2), () => at(1500, 700, lerp(2.6, 1, sp), -0.16, () => {
        ctx.save(); ctx.strokeStyle = C.amber; ctx.lineWidth = 8; rr(-210, -78, 420, 156, 16); ctx.stroke(); ctx.restore();
        txt('승인', 0, 10, { size: 88, w: 800, color: C.amber, align: 'center' });
        txt('APPROVED · budget 1,364', 0, 52, { mono: true, size: 16, w: 700, color: C.amber, align: 'center', track: 3 });
      }));
    }
  }
  ctx.restore();
}

// ------------------------------------------------------------------ 03 제작
const TOKENS = ['sfx_coin', 'sfx_jump', 'sfx_debris', 'amb_vault', 'sfx_land', 'vo_intro', 'vo_boss', 'crv_golem', 'mdl_golem', 'mdl_crate', 'img_bg', 'l10n_en', 'l10n_ja', 'sfx_hit', 'sfx_step', 'vo_intro_b', 'amb_drip', 'sfx_ui', 'sfx_door', 'img_door', 'amb_alarm'];
const REWORK = new Set([4, 20]);
const PANELS = [
  { x: 120, y: 262, role: 'sound-designer', api: 'sound.text2sound → sound.variation', title: '효과음', id: 'sfx_coin_pickup', draw: panelSound },
  { x: 970, y: 262, role: 'voice-director', api: 'tts.standard → face.blendshape', title: '대사 음성 · 립싱크', id: 'vo_intro', draw: panelVoice },
  { x: 120, y: 592, role: 'visual-artist', api: '3d.image_to_3d → GLB', title: '3D 모델', id: 'mdl_vault_golem', draw: panel3D },
  { x: 970, y: 592, role: 'localization-specialist', api: 'mt.translate · 용어집', title: '현지화', id: 'l10n_en · l10n_ja', draw: panelL10n },
];
const PW = 830, PH = 310;
function tokenStart(i) { return i === 20 ? 14.95 : i < 8 ? 0.95 + i * 0.06 : 1.43 + (i - 8) * 0.62; }
function tokenPos(i, l) {
  const rw = REWORK.has(i);
  const S = [[140, 0], [560, 0], [960, 0], [960, 150], [960, 0], [1500, 0]];
  const plan = rw ? [[0, 1, 0.22], [1, 1, 0.14], [1, 2, 0.18], [2, 3, 0.16], [3, 4, 0.2], [4, 5, 0.22]] : [[0, 1, 0.22], [1, 1, 0.14], [1, 2, 0.18], [2, 2, 0.08], [2, 5, 0.24]];
  let tt = l - tokenStart(i); if (tt < 0) return null;
  for (const [a, b, d] of plan) {
    const lane = ((i * 7) % 5 - 2) * 30;
    if (tt <= d) { const e = E.inOutCubic(tt / d); return { x: lerp(S[a][0], S[b][0], e) + (a === b ? ((i * 3) % 4 - 1.5) * 26 : 0), y: lerp(S[a][1], S[b][1], e) + (S[a][1] === 0 && S[b][1] === 0 ? lane : lane * 0.4), stage: b, rw }; }
    tt -= d;
  }
  return { x: 1500, y: 0, stage: 5, done: true, rw };
}
function focusAlpha(k, l) {
  // 2.0~11.6: 지금 설명하는 칸만 밝게
  if (l < 2.0 || l > 11.9) return 1;
  const a = Math.floor((l - 2.0) / 2.4), f = (l - 2.0) % 2.4;
  const on = k === a ? 1 : k === a - 1 ? 1 - clamp(f / 0.3) : 0;
  const lead = k === a ? clamp(f / 0.3) : 0;
  return a >= 4 ? lerp(0.4, 1, clamp((l - 11.6) / 0.3)) : lerp(0.4, 1, Math.max(on, lead));
}
function sceneProduce(t) {
  const T = S0('produce'), l = t - T;
  const hp = seg(l, 0.55, 1.05, E.inOutCubic);
  shockRing(W / 2, 540, t, T, C.cyan, { r: 1400, lw: 12, life: 0.9 });
  shockRing(W / 2, 540, t, T + 0.08, '#ffffff', { r: 1000, lw: 6, life: 0.7 });
  burst(W / 2, 540, t, T, 90, 26, [C.cyan, '#ffffff', C.lime], { speed: 2200, life: 1.3 });
  const ray = Math.exp(-l * 2.2) * (l >= 0 ? 1 : 0);
  if (ray > 0.02) { ctx.save(); ctx.translate(W / 2, 540); ctx.globalCompositeOperation = 'lighter'; for (let k = 0; k < 18; k++) { ctx.rotate(Math.PI * 2 / 18); ctx.globalAlpha = ray * 0.12; ctx.fillStyle = C.cyan; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(1400, -40); ctx.lineTo(1400, 40); ctx.closePath(); ctx.fill(); } ctx.restore(); }
  const slam = seg(l, 0.0, 0.25, E.outExpo);
  const size = lerp(lerp(300, 240, slam), 58, hp), x = lerp(W / 2, 120, hp), y = lerp(620, 196, hp);
  txt('에셋 제작', x, y, { size, w: 800, color: C.ink, align: hp > 0.5 ? 'left' : 'center', blur: (1 - slam) * 24, alpha: clamp(slam * 3), track: -size * 0.03, glow: (1 - hp) * 50, glowColor: hexA(C.cyan, 0.8) });
  if (hp < 0.5) withA((1 - hp * 2) * slam, () => txt('03 · MAKE · WORKFLOW', W / 2, 700, { mono: true, size: 22, w: 700, color: C.cyan, align: 'center', track: 10 }));
  withA(seg(l, 0.9, 1.2), () => txt('03 · 워크플로 조율 · 제작 → 검증 → 재작업(1회)', 124, 236, { mono: true, size: 16, w: 600, color: C.cyan, track: 2 }));
  // 파이프라인: 크게 보였다가 위쪽 띠로 접힌다. 토큰은 장면 내내 흐른다
  const fold = seg(l, 1.95, 2.35, E.inOutCubic);
  const pa = seg(l, 0.85, 1.1) * (1 - seg(l, 17.2, 17.5) * 0.6);
  if (pa > 0) {
    ctx.save();
    const py = lerp(560, 160, fold), sc = lerp(1, 0.42, fold), ox = lerp(0, 1000, fold);
    ctx.translate(ox, py); ctx.scale(sc, sc); ctx.globalAlpha *= pa;
    const stages = [['제작', 560, 0], ['검증', 960, 0], ['재작업', 960, 150], ['완료', 1500, 0]];
    line(140, 0, 1500, 0, 'rgba(255,255,255,0.12)', 2);
    ctx.save(); ctx.setLineDash([6, 8]); line(960, 0, 960, 150, hexA(C.amber, 0.5), 2); ctx.restore();
    const rwHot = l > 15.2 && l < 16.2 ? 1 : 0;
    stages.forEach(([s, sx, sy], i) => {
      const col = i === 2 ? C.amber : i === 3 ? C.green : C.cyan;
      panel(sx - 92, sy - 44, 184, 88, { fill: hexA(col, 0.08 + (i === 2 ? rwHot * 0.2 : 0)), stroke: hexA(col, 0.7), lw: 2, r: 16, glow: i === 2 && rwHot ? 40 : 0, glowColor: C.amber });
      txt(s, sx, sy + 12, { size: 32, w: 800, color: col, align: 'center' });
    });
    txt(['sound-designer', 'voice-director', 'visual-artist', 'localization'][Math.floor(t * 4) % 4], 560, 78, { mono: true, size: 18, w: 600, color: C.dim, align: 'center' });
    txt('asset-qa', 960, -64, { mono: true, size: 18, w: 600, color: C.dim, align: 'center' });
    let doneN = 0;
    TOKENS.forEach((id, i) => {
      const q = tokenPos(i, l); if (!q) return;
      if (q.done) { doneN++; return; }
      const col = q.stage === 3 || q.stage === 4 && q.rw ? C.amber : q.stage >= 2 ? C.green : C.cyan;
      glowDot(q.x, q.y, 34, col, 0.8);
      chip(q.x, q.y, id, { size: 14, h: 28, padX: 10, color: '#05060A', fill: col, align: 'center', w: 700 });
    });
    txt(String(doneN), 1500, 104, { size: 44, w: 800, color: C.green, align: 'center' });
    txt('qa_passed', 1500, 134, { mono: true, size: 16, w: 600, color: C.dim, align: 'center' });
    ctx.restore();
  }
  // 네 칸 작업 화면(차례로 하나씩 설명)
  PANELS.forEach((pn, k) => {
    const t0 = T + 2.0 + k * 2.4, p = seg(t, t0, t0 + 0.45, E.outExpo); if (p <= 0) return;
    const dimAll = 1 - seg(l, 15.0, 15.3) * 0.55 * (1 - seg(l, 16.9, 17.1)) - seg(l, 17.4, 17.7) * 0.65;
    withA(focusAlpha(k, l) * dimAll, () => {
      ctx.save();
      const cx = pn.x + PW / 2, cy = pn.y + PH / 2; ctx.translate(cx, cy); ctx.scale(lerp(0.94, 1, p), lerp(0.94, 1, p)); ctx.translate(-cx, -cy);
      ctx.beginPath(); ctx.rect(pn.x - 10, pn.y - 10, (PW + 20) * p, PH + 20); ctx.clip();
      const act = focusAlpha(k, l) > 0.95 && l < 11.9;
      panel(pn.x, pn.y, PW, PH, { fill: '#0A0D13', stroke: hexA(C.cyan, act ? 0.7 : 0.28), lw: act ? 2 : 1.2, glow: act ? 30 : 0, glowColor: hexA(C.cyan, 0.3) });
      txt(pn.role, pn.x + 28, pn.y + 40, { mono: true, size: 15, w: 700, color: C.cyan });
      txt(pn.api, pn.x + 28 + tw(pn.role, 700, 15, true) + 16, pn.y + 40, { mono: true, size: 15, w: 500, color: C.mute });
      txt(pn.title, pn.x + 28, pn.y + 84, { size: 30, w: 800, color: C.ink });
      txt(pn.id, pn.x + 36 + tw(pn.title, 800, 30), pn.y + 84, { mono: true, size: 15, w: 500, color: C.dim });
      pn.draw(pn.x, pn.y, t, t0);
      const qt = T + 14.0 + k * 0.25, qp = seg(t, qt, qt + 0.3, E.outBackBig);
      if (qp > 0) {
        shockRing(pn.x + PW - 110, pn.y + 44, t, qt, C.green, { r: 160, r0: 20, lw: 4, life: 0.5 });
        at(pn.x + PW - 110, pn.y + 44, qp, 0, () => chip(0, 0, '✓ qa_passed', { align: 'center', size: 15, w: 800, h: 32, color: '#05060A', fill: C.green }));
      }
      ctx.restore();
    });
  });
  // 측정 기준 칩(QA 가 재는 값)
  withA(seg(l, 13.7, 14.0) * (1 - seg(l, 15.0, 15.2)), () => {
    const items = ['길이 · 채널 · 피크 · LUFS', '블렌드셰이프 · 음성 싱크', 'GLB 구조 · 삼각형 수', '누락 · 자리표시자 · 글자 수'];
    PANELS.forEach((pn, k) => chip(pn.x + PW - 30, pn.y + 82, 'asset-qa 측정 · ' + items[k], { size: 13, h: 28, color: C.green, fill: hexA(C.green, 0.12), align: 'right', mono: false }));
  });
  // 재작업 카드
  const rp = seg(l, 15.2, 15.5, E.outBack), rout = seg(l, 16.9, 17.2, E.inCubic);
  if (rp > 0 && rout < 1) {
    const ok = l >= 16.1, col = ok ? C.green : C.amber;
    at(W / 2, 752 + rout * 400, rp, 0, () => {
      panel(-460, -92, 920, 184, { fill: ok ? '#0B140E' : '#17120A', stroke: col, lw: 2, glow: 40, glowColor: hexA(col, 0.4) });
      txt('asset-qa → sound-designer', -424, -44, { mono: true, size: 15, w: 700, color: col });
      txt(ok ? '재작업 1회 · 재검증 통과' : '1차 검증 실패 · 고칠 수 있는 실패', 424, -44, { size: 15, w: 700, color: C.dim, align: 'right' });
      txt(ok ? '✓ amb_alarm_loop · qa_passed' : '✕ amb_alarm_loop · 루프 이음매에서 소리가 튄다', -424, 6, { size: 30, w: 800, color: ok ? C.ink : C.ink });
      txt(ok ? 'sound.looping 다시 호출 → 이음매 −41 dB (기준 −30 dB 이하)' : '이음매 −9 dB · 기준 −30 dB 이하 · 재작업 대상', -424, 50, { mono: true, size: 15, w: 500, color: C.dim });
      const vp = seg(l, 16.1, 16.3, E.outBackBig);
      if (vp > 0) at(330, 10, vp, -0.12, () => { ctx.save(); ctx.strokeStyle = C.green; ctx.lineWidth = 5; rr(-100, -32, 200, 64, 10); ctx.stroke(); ctx.restore(); txt('PASS', 0, 12, { size: 36, w: 800, color: C.green, align: 'center', track: 4 }); });
    });
  }
  // 장부
  const lp = seg(l, 17.5, 17.85, E.outExpo);
  if (lp > 0) withA(lp, () => {
    const y = 330, w = 1000, h = 470;
    at(W / 2, y + h / 2, lerp(0.92, 1, lp), 0, () => {
      panel(-w / 2, -h / 2, w, h, { fill: 'rgba(8,12,18,0.95)', stroke: hexA(C.cyan, 0.6), lw: 2, glow: 60, glowColor: hexA(C.cyan, 0.35), r: 22 });
      txt('varco_ledger.jsonl', -w / 2 + 36, -h / 2 + 50, { mono: true, size: 18, w: 700, color: C.cyan });
      txt('예산 잠금 · 여러 에이전트가 동시에 호출해도 초과 없음', w / 2 - 36, -h / 2 + 50, { size: 17, w: 600, color: C.dim, align: 'right' });
      const rows = [['sound.text2sound', 'sfx_coin_pickup', 25], ['sound.variation', 'sfx_coin_pickup', 50], ['sound.looping', 'amb_alarm_loop', 150], ['tts.standard', 'vo_intro', 9], ['face.blendshape', 'vo_intro', '—'], ['3d.image_to_3d', 'mdl_vault_golem', 200], ['mt.translate', 'l10n_ja', '—'], ['image.background', 'img_bg', 120]];
      const n = Math.min(rows.length, Math.floor((l - 17.5) / 0.15) + 1);
      rows.slice(0, n).slice(-6).forEach((r, i) => {
        const yy = -h / 2 + 104 + i * 38;
        txt(r[0], -w / 2 + 36, yy, { mono: true, size: 17, w: 600, color: C.lime });
        txt(r[1], -w / 2 + 330, yy, { mono: true, size: 17, w: 500, color: C.ink });
        txt(String(r[2]), w / 2 - 140, yy, { mono: true, size: 17, w: 700, color: r[2] === '—' ? C.amber : C.cyan, align: 'right' });
        txt('ok', w / 2 - 50, yy, { mono: true, size: 17, w: 700, color: C.green, align: 'right' });
      });
      const used = Math.round(1118 * seg(l, 17.6, 18.8, E.outCubic));
      const bx = -w / 2 + 36, by = h / 2 - 76, bw = w - 72;
      ctx.fillStyle = 'rgba(255,255,255,0.08)'; ctx.fillRect(bx, by, bw, 14);
      ctx.fillStyle = C.cyan; ctx.fillRect(bx, by, bw * used / 1364, 14);
      ctx.fillStyle = C.amber; ctx.fillRect(bx + bw - 2, by - 8, 3, 30);
      txt(`${used.toLocaleString('en-US')} / 1,364 크레딧`, bx, by + 46, { size: 22, w: 800, color: C.ink });
      txt(`${Math.round(used / 1364 * 100)}% · 예산 안`, bx + bw, by + 46, { size: 20, w: 700, color: C.green, align: 'right' });
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
    rr(x + 28, y + 106, 520, 34, 17); ctx.fillStyle = hexA(C.cyan, 0.1); ctx.fill();
    scrambleText(pr, x + 44, y + 129, t, t0 + 0.2, 0.6, { mono: true, size: 15, w: 600, color: C.cyan });
  });
  const rv = seg(t, t0 + 0.6, t0 + 1.8, E.inOutCubic);
  drawWave(x + 28, y + 212, 520, 116, 1.3, rv, C.cyan, { bars: 96 });
  if (rv > 0 && rv < 1) line(x + 28 + 520 * rv, y + 152, x + 28 + 520 * rv, y + 272, '#fff', 2, 0.9);
  withA(seg(t, t0 + 1.6, t0 + 2.0), () => { chip(x + 28, y + 290, '10.0s → 0.42s 무음 제거', { size: 13, h: 26, color: C.dim }); chip(x + 240, y + 290, 'peak -1.0 dBFS', { size: 13, h: 26, color: C.dim }); });
  for (let k = 0; k < 4; k++) {
    const vp = seg(t, t0 + 2.0 + k * 0.2, t0 + 2.4 + k * 0.2, E.outExpo); if (vp <= 0) continue;
    const vy = y + 124 + k * 42;
    withA(vp, () => {
      txt(`_0${k + 2}`, x + 586, vy + 6, { mono: true, size: 13, w: 600, color: C.dim });
      drawWave(x + 626, vy, 170 * vp, 32, 2.1 + k * 0.7, 1, mixHex(C.cyan, '#ffffff', k * 0.15), { bars: 34 });
    });
    if (vp > 0 && vp < 1) line(x + 548, y + 212, x + 620, vy, hexA(C.cyan, 0.4), 1.5, 1 - vp);
  }
  withA(seg(t, t0 + 2.2, t0 + 2.6), () => txt('variation ×4', x + 586, y + 296, { mono: true, size: 13, w: 600, color: C.cyan }));
}
// ---- 제작 패널: 음성 + 립싱크
function jaw(t) { const u = t * 7.3; return clamp(0.15 + 0.85 * Math.abs(Math.sin(u) * Math.sin(u * 0.37 + 1.2))); }
function panelVoice(x, y, t, t0) {
  const on = seg(t, t0 + 0.3, t0 + 0.6);
  const speak = t > t0 + 0.8 && t < t0 + 3.9;
  const jw = speak ? jaw(t) : 0.08;
  withA(on, () => {
    const fx = x + 128, fy = y + 194;
    glowDot(fx, fy, 150, C.violet, 0.35);
    circle(fx, fy, 78, '#100E1C', C.violet, 3);
    const blink = (t % 2.7) < 0.1 ? 0.15 : 1;
    ctx.fillStyle = C.ink; ctx.beginPath(); ctx.ellipse(fx - 27, fy - 16, 8, 10 * blink, 0, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.ellipse(fx + 27, fy - 16, 8, 10 * blink, 0, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = C.coral; ctx.beginPath(); ctx.ellipse(fx, fy + 32, 23 - jw * 5, 4 + jw * 18, 0, 0, Math.PI * 2); ctx.fill();
    txt('lockey · 락키', fx, fy + 102, { mono: true, size: 13, w: 600, color: C.dim, align: 'center' });
  });
  const line1 = '침입자를 확인했습니다.';
  const kp = seg(t, t0 + 0.8, t0 + 3.4, E.lin);
  withA(on, () => {
    txt(line1, x + 270, y + 140, { size: 30, w: 700, color: 'rgba(255,255,255,0.3)' });
    ctx.save(); ctx.beginPath(); ctx.rect(x + 270, y + 100, tw(line1, 700, 30) * kp, 60); ctx.clip();
    txt(line1, x + 270, y + 140, { size: 30, w: 700, color: C.ink }); ctx.restore();
    drawWave(x + 270, y + 180, 330, 40, 4.2, kp, C.violet, { bars: 60, kind: 'voice' });
  });
  const BS = [['jawOpen', jw], ['mouthFunnel', speak ? clamp(0.5 * Math.abs(Math.sin(t * 5.1))) : 0.05], ['mouthSmile', 0.12], ['eyeBlink', (t % 2.7) < 0.1 ? 0.9 : 0.04], ['browInnerUp', speak ? 0.2 + 0.2 * Math.sin(t * 1.7) : 0.1]];
  BS.forEach(([n, v], i) => {
    const a = seg(t, t0 + 0.5 + i * 0.08, t0 + 0.8 + i * 0.08); if (a <= 0) return;
    const yy = y + 226 + i * 17;
    withA(a, () => {
      txt(n, x + 270, yy + 5, { mono: true, size: 12, w: 500, color: C.dim });
      ctx.fillStyle = 'rgba(255,255,255,0.08)'; ctx.fillRect(x + 390, yy - 4, 200, 8);
      ctx.fillStyle = C.violet; ctx.fillRect(x + 390, yy - 4, 200 * v, 8);
      txt(v.toFixed(2), x + 604, yy + 5, { mono: true, size: 12, w: 600, color: C.ink });
    });
  });
  withA(seg(t, t0 + 0.2, t0 + 0.6), () => { chip(x + 660, y + 132, '화자 1,293명 중 선택', { size: 12, h: 24, color: C.violet, fill: hexA(C.violet, 0.12), mono: false }); chip(x + 660, y + 166, 'emotion: neutral', { size: 12, h: 24, color: C.dim }); chip(x + 660, y + 200, 'ARKit 52 · 30fps', { size: 12, h: 24, color: C.dim }); });
}
// ---- 제작 패널: 3D
function buildGolemMesh() {
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
    const jawCut = y < -0.55 ? 0.82 : 1;
    return [x * n * 1.05, y * n * 0.95 * jawCut, z * n];
  });
  return { V, F: Fc };
}
function drawMesh(cx, cy, R, rotY, rotX, reveal, color) {
  const { V, F } = MESH;
  const cy_ = Math.cos(rotY), sy = Math.sin(rotY), cx_ = Math.cos(rotX), sx = Math.sin(rotX);
  const P = V.map(([x, y, z]) => { let X = x * cy_ + z * sy, Z = -x * sy + z * cy_; let Y = y * cx_ - Z * sx; Z = y * sx + Z * cx_; const f = 3.2 / (3.2 + Z); return [cx + X * R * f, cy - Y * R * f, Z]; });
  const faces = F.map((f, i) => { const [a, b, c] = f.map(k => P[k]); return { f, z: (a[2] + b[2] + c[2]) / 3 }; });
  faces.sort((p, q) => q.z - p.z);
  for (const fc of faces) {
    const [a, b, c] = fc.f.map(k => P[k]);
    const cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
    if (cross > 0) continue;
    const yMid = (a[1] + b[1] + c[1]) / 3; const rv = (yMid - (cy - R * 1.2)) / (R * 2.4);
    if (rv > reveal) continue;
    const lit = clamp(0.25 + 0.75 * Math.abs(cross) / 1800, 0, 1);
    ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.lineTo(c[0], c[1]); ctx.closePath();
    ctx.fillStyle = `rgba(${Math.round(20 + 40 * lit)},${Math.round(40 + 120 * lit)},${Math.round(60 + 140 * lit)},0.95)`; ctx.fill();
    ctx.strokeStyle = hexA(color, 0.35 + 0.4 * lit * (reveal - rv < 0.06 ? 2 : 1)); ctx.lineWidth = 1; ctx.stroke();
  }
  if (reveal < 1) { const sy2 = cy - R * 1.2 + R * 2.4 * reveal; line(cx - R * 1.3, sy2, cx + R * 1.3, sy2, '#fff', 2, 0.9); glowDot(cx, sy2, R * 1.2, color, 0.25); }
  if (reveal >= 1) { const ex = Math.sin(rotY) * R * 0.33; glowDot(cx - R * 0.28 * Math.cos(rotY) + ex * 0.2, cy - R * 0.08, 22, C.amber, 0.9); glowDot(cx + R * 0.28 * Math.cos(rotY) + ex * 0.2, cy - R * 0.08, 22, C.amber, 0.9); }
}
function panel3D(x, y, t, t0) {
  withA(seg(t, t0 + 0.2, t0 + 0.5), () => {
    panel(x + 28, y + 104, 176, 176, { fill: '#10141C', stroke: 'rgba(255,255,255,0.14)', r: 12 });
    ctx.save(); ctx.translate(x + 116, y + 196); ctx.scale(0.92, 0.92);
    ctx.fillStyle = '#5B6475'; ctx.beginPath(); ctx.moveTo(-58, 40); ctx.lineTo(-64, -10); ctx.lineTo(-40, -52); ctx.lineTo(0, -64); ctx.lineTo(42, -50); ctx.lineTo(64, -8); ctx.lineTo(56, 42); ctx.lineTo(20, 60); ctx.lineTo(-24, 60); ctx.closePath(); ctx.fill();
    ctx.fillStyle = C.amber; ctx.fillRect(-30, -12, 16, 8); ctx.fillRect(14, -12, 16, 8); ctx.restore();
    txt('source.png · 회색 배경', x + 32, y + 298, { mono: true, size: 12, w: 600, color: C.dim });
    txt('→', x + 232, y + 206, { size: 36, w: 700, color: C.cyan });
  });
  const rv = seg(t, t0 + 0.7, t0 + 2.2, E.inOutSine);
  if (rv > 0) drawMesh(x + 460, y + 196, 96, t * 0.9, 0.18, rv, C.cyan);
  withA(seg(t, t0 + 1.0, t0 + 1.4), () => {
    const tris = Math.round(18432 * seg(t, t0 + 0.9, t0 + 2.2, E.outCubic));
    txt(tris.toLocaleString('en-US'), x + 640, y + 158, { size: 40, w: 800, color: C.ink });
    txt('tris · target 20,000', x + 640, y + 184, { mono: true, size: 12, w: 600, color: C.dim });
    chip(x + 640, y + 222, 'texture ✓', { size: 12, h: 24, color: C.cyan });
    chip(x + 640, y + 256, 'GLB 2.0 · 비동기 조회', { size: 12, h: 24, color: C.cyan, mono: false });
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
    const yy = y + 144 + i * 56, a = seg(t, t0 + 0.2 + i * 0.1, t0 + 0.5 + i * 0.1); if (a <= 0) return;
    withA(a, () => {
      chip(x + 28, yy - 9, lang, { size: 13, h: 26, w: 800, color: '#05060A', fill: i === 0 ? C.ink : C.lime });
      if (!k) txt(s, x + 96, yy, { size: 28, w: 700, color: C.ink });
      else if (k === 'en') scrambleText(s, x + 96, yy, t, t0 + 0.8, 0.8, { size: 28, w: 700, color: C.lime });
      else scrambleJa(s, x + 96, yy, t, t0 + 1.3, 0.9, { size: 28, w: 700, color: C.lime });
    });
  });
  withA(seg(t, t0 + 1.8, t0 + 2.2), () => {
    chip(x + 540, y + 134, '락키 → Lockey · 용어집 고정', { size: 13, h: 28, color: C.lime, mono: false, w: 600 });
    chip(x + 540, y + 170, '자리표시자 보존 ✓', { size: 13, h: 28, color: C.dim, mono: false, w: 600 });
    chip(x + 540, y + 206, '글자 수 초과 0', { size: 13, h: 28, color: C.dim, mono: false, w: 600 });
    txt('data/strings/en.json · ja.json', x + 28, y + 298, { mono: true, size: 13, w: 500, color: C.mute });
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
const MODULES = [['코어 루프', '40초 한 바퀴를 끝까지 달린다'], ['충돌 · 점프', '잔해에 부딪히면 HP −25'], ['HUD · 문자열', 'ko · en · ja 전환, 글자 수 초과 없음'], ['사운드 · 음성', '효과음과 대사가 제때 재생된다'], ['얼굴 애니메이션', 'intro_001 입 모양이 음성과 맞다']];
const TESTS = ['TC-01  시작 화면 → 게임 화면', 'TC-07  코인 1개 = +10점', 'TC-12  잔해 충돌 → HP 감소', 'TC-19  출구 도착 → 결과 화면', 'TC-23  언어 전환 · 글자 수 초과 없음', 'TC-31  대사와 입 모양이 맞는다', 'TC-38  콘솔 오류 0건'];
const GAME = { x: 960, y: 262, w: 840, h: 500, speed: 360, px: 170, ground: 402 };
const JUMPS = [0.95, 2.05, 3.25, 4.45, 5.6, 6.7, 7.85, 9.0, 10.2, 11.3];
function initGameData() {
  if (GAME.coins) return;
  GAME.debris = JUMPS.map(j => (j + 0.31) * GAME.speed);
  GAME.coins = [];
  for (let w = 380; w < 13 * GAME.speed; w += 100) {
    const near = GAME.debris.find(d => Math.abs(d - w) < 70);
    GAME.coins.push({ w, y: near != null ? GAME.ground - 150 : GAME.ground - 44 });
  }
}
function gameState(gt, g0, fixAt) {
  initGameData();
  const worldX = gt * GAME.speed; let score = 0, coins = 0, pops = [];
  for (const c of GAME.coins) {
    if (worldX >= c.w) {
      const tc = c.w / GAME.speed + g0; const val = tc < fixAt ? 20 : 10;
      score += val; coins++;
      const age = gt - c.w / GAME.speed; if (age < 0.6) pops.push({ c, age, val });
    }
  }
  let jy = 0; for (const j of JUMPS) { const u = (gt - j) / 0.62; if (u >= 0 && u <= 1) jy = Math.sin(Math.PI * u) * 132; }
  return { worldX, score, coins, pops, jy };
}
function drawGame(t, g0, fixAt, probe) {
  const gt = t - g0; const G = GAME; const s = gameState(gt, g0, fixAt);
  const vx = G.x, vy = G.y + 44, vw = G.w, vh = G.h - 44;
  ctx.save(); rr(vx, vy, vw, vh, 0); ctx.clip();
  const bg = ctx.createLinearGradient(0, vy, 0, vy + vh); bg.addColorStop(0, '#0B1118'); bg.addColorStop(1, '#16202A');
  ctx.fillStyle = bg; ctx.fillRect(vx, vy, vw, vh);
  for (let i = 0; i < 9; i++) { const x = vx + (((i * 150) - s.worldX * 0.25) % 1350 + 1350) % 1350 - 150; ctx.fillStyle = '#131C26'; ctx.fillRect(x, vy, 38, vh); ctx.fillStyle = '#1B2733'; ctx.fillRect(x + 6, vy, 6, vh); }
  for (let i = 0; i < 7; i++) { const x = vx + (((i * 240) - s.worldX * 0.55) % 1680 + 1680) % 1680 - 240; ctx.fillStyle = '#1E2A36'; ctx.fillRect(x, vy + 150, 170, 10); ctx.fillRect(x, vy + 230, 170, 10);
    for (let k = 0; k < 5; k++) { ctx.fillStyle = hexA(C.gold, 0.25 + 0.2 * hash(i * 7 + k)); ctx.fillRect(x + 14 + k * 30, vy + 136, 16, 14); } }
  // 골렘(뒤쪽): 보스 등장
  const gp = seg(gt, 8.8, 10.2, E.outCubic);
  if (gp > 0) { ctx.save(); ctx.globalAlpha = 0.85 * gp; ctx.translate(vx + vw - 150, vy + 330 - gp * 80); ctx.fillStyle = '#0A0F15';
    ctx.beginPath(); ctx.moveTo(-120, 120); ctx.lineTo(-130, 10); ctx.lineTo(-80, -70); ctx.lineTo(0, -95); ctx.lineTo(80, -70); ctx.lineTo(130, 10); ctx.lineTo(120, 120); ctx.closePath(); ctx.fill();
    glowDot(-40, -20, 28, C.amber, gp); glowDot(40, -20, 28, C.amber, gp); ctx.restore(); }
  ctx.fillStyle = '#0E151C'; ctx.fillRect(vx, vy + G.ground, vw, vh - G.ground);
  line(vx, vy + G.ground, vx + vw, vy + G.ground, hexA(C.lime, 0.7), 2);
  for (let i = 0; i < 16; i++) { const x = vx + ((i * 60 - s.worldX) % 960 + 960) % 960 - 60; line(x, vy + G.ground + 4, x - 30, vy + vh, 'rgba(255,255,255,0.06)', 1); }
  G.debris.forEach((dw, i) => {
    const sx = dw - s.worldX + G.px; if (sx < -80 || sx > vw + 80) return;
    const land = clamp((vw + 40 - sx) / 220); const e = E.inQuart(land);
    const dy = lerp(-80, G.ground - 44, e);
    ctx.save(); ctx.translate(vx + sx, vy + dy); ctx.rotate((1 - e) * 1.2 + i);
    ctx.fillStyle = '#6B5B4A'; ctx.fillRect(-24, -20, 48, 40); ctx.fillStyle = '#8A7560'; ctx.fillRect(-24, -20, 48, 8); ctx.restore();
    if (land >= 1) { const since = (vw + 40 - sx - 220) / G.speed; if (since < 0.4) { ctx.save(); ctx.globalAlpha = 0.5 * (1 - since / 0.4); ctx.fillStyle = '#A89A88'; for (let k = 0; k < 6; k++) ctx.fillRect(vx + sx - 40 + k * 14, vy + G.ground - 8 - since * 60 * hash(k + i), 6, 6); ctx.restore(); } }
  });
  G.coins.forEach(c => {
    const sx = c.w - s.worldX + G.px; if (sx < -30 || sx > vw + 30) return;
    if (s.worldX >= c.w) return;
    const spin = Math.abs(Math.cos(gt * 6 + c.w));
    ctx.save(); ctx.translate(vx + sx, vy + c.y); glowDot(0, 0, 26, C.gold, 0.5);
    ctx.fillStyle = C.gold; ctx.beginPath(); ctx.ellipse(0, 0, 12 * spin + 2, 12, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  });
  s.pops.forEach(({ c, age, val }) => {
    const bug = val === 20;
    txt(`+${val}`, vx + G.px + 10, vy + c.y - 20 - age * 80, { size: 24, w: 800, color: bug ? C.red : C.gold, alpha: 1 - age / 0.6 });
    ctx.save(); ctx.globalAlpha = 1 - age / 0.6; circle(vx + G.px, vy + c.y, 10 + age * 50, null, C.gold, 2); ctx.restore();
  });
  const py = vy + G.ground - s.jy, px = vx + G.px, run = Math.sin(gt * 18);
  for (let k = 1; k <= 4; k++) { ctx.save(); ctx.globalAlpha = 0.12 / k; ctx.fillStyle = C.lime; rr(px - 17 - k * 14, py - 72, 34, 44, 8); ctx.fill(); ctx.restore(); }
  ctx.save(); ctx.strokeStyle = C.lime; ctx.lineWidth = 7; ctx.lineCap = 'round';
  if (s.jy < 2) { ctx.beginPath(); ctx.moveTo(px - 4, py - 30); ctx.lineTo(px - 4 + run * 14, py); ctx.moveTo(px + 4, py - 30); ctx.lineTo(px + 4 - run * 14, py); ctx.stroke(); }
  else { ctx.beginPath(); ctx.moveTo(px - 4, py - 30); ctx.lineTo(px - 14, py - 10); ctx.moveTo(px + 4, py - 30); ctx.lineTo(px + 16, py - 14); ctx.stroke(); }
  ctx.restore();
  ctx.fillStyle = C.lime; rr(px - 17, py - 72, 34, 44, 8); ctx.fill();
  circle(px + 2, py - 88, 15, C.lime); ctx.fillStyle = '#05060A'; ctx.fillRect(px + 2, py - 93, 14, 6);
  // 대사 자막(음성 + 입 모양)
  const SUBS = [[0.6, 2.8, '락키', '침입자를 확인했습니다.', C.violet], [9.4, 11.8, '락키', '금고 수호 골렘이 깨어났습니다.', C.violet]];
  for (const [a, b, who, s2, col] of SUBS) {
    const sub = seg(gt, a, a + 0.2) * (1 - seg(gt, b - 0.2, b)); if (sub <= 0) continue;
    withA(sub, () => { const ww = tw(`${who}  ${s2}`, 700, 20) + 90; panel(vx + 230, vy + 28, ww, 52, { fill: 'rgba(5,6,10,0.8)', stroke: hexA(col, 0.6), r: 26 });
      circle(vx + 258, vy + 54, 10, col); ctx.fillStyle = '#05060A'; ctx.fillRect(vx + 252, vy + 52, 12, 2 + jaw(t) * 5);
      txt(`${who}  ${s2}`, vx + 280, vy + 61, { size: 20, w: 700, color: C.ink }); });
  }
  txt(`SCORE ${String(s.score).padStart(5, '0')}`, vx + 24, vy + 44, { mono: true, size: 22, w: 700, color: C.ink });
  circle(vx + 34, vy + 72, 8, C.gold); txt(`× ${s.coins}`, vx + 48, vy + 79, { mono: true, size: 17, w: 700, color: C.gold });
  txt('HP', vx + vw - 196, vy + 44, { mono: true, size: 16, w: 700, color: C.dim }); ctx.fillStyle = C.coral; ctx.fillRect(vx + vw - 164, vy + 32, 140, 14);
  if (probe > 0) withA(probe, () => {
    ctx.save(); ctx.setLineDash([6, 5]); ctx.strokeStyle = C.red; ctx.lineWidth = 2; rr(vx + 14, vy + 18, 214, 36, 6); ctx.stroke(); ctx.restore();
    chip(vx + 18, vy + 104, 'data-testid="lbl_score"', { size: 12, h: 24, color: '#05060A', fill: C.red });
    const pp = seg(probe, 0, 1, E.outCubic), cxp = vx + lerp(420, 120, pp), cyp = vy + lerp(260, 36, pp);
    line(cxp - 16, cyp, cxp + 16, cyp, C.red, 2); line(cxp, cyp - 16, cxp, cyp + 16, C.red, 2); circle(cxp, cyp, 9, null, C.red, 2);
  });
  ctx.restore();
}
const BOOT = [
  [0.2, '$ python3 -m http.server --directory games/coin-runner', C.ink],
  [0.45, 'Serving HTTP on 0.0.0.0 port 8000 …', C.dim],
  [0.6, 'GET /data/balance/enemies.csv              200', C.dim],
  [0.7, 'GET /data/strings/ko.json                  200', C.dim],
  [0.8, 'GET /assets/audio/sfx/sfx_coin_pickup_01.wav 200', C.dim],
  [0.9, 'GET /assets/audio/voice/korean/intro_001.wav 200', C.dim],
  [1.0, 'GET /assets/anim/face/intro_001.json       200', C.dim],
  [1.1, 'GET /assets/models/mdl_vault_golem.glb      200', C.dim],
  [1.3, 'window.__game ready ✓', C.lime],
];
function drawBoot(t, b0) {
  const G = GAME, x = G.x + 30, y0 = G.y + 92, l = t - b0;
  BOOT.forEach(([bt, s, col], i) => {
    if (l < bt) return;
    const shown = s.slice(0, Math.min(s.length, Math.floor((l - bt) * 160)));
    const m = shown.match(/^(.*?)(200)$/);
    if (m) { txt(m[1], x, y0 + i * 34, { mono: true, size: 16, w: 500, color: col }); txt('200', x + tw(m[1], 500, 16, true), y0 + i * 34, { mono: true, size: 16, w: 700, color: C.green }); }
    else txt(shown, x, y0 + i * 34, { mono: true, size: 16, w: i === 0 || i === 8 ? 700 : 500, color: col });
  });
  const p = seg(l, 0.5, 1.4, E.inOutCubic);
  const bx = G.x + 30, by = G.y + G.h - 56, bw = G.w - 60;
  ctx.fillStyle = 'rgba(255,255,255,0.08)'; ctx.fillRect(bx, by, bw, 10);
  ctx.fillStyle = C.lime; ctx.fillRect(bx, by, bw * p, 10);
  txt(`에셋 ${Math.round(21 * p)} / 21 불러오는 중 · 배경음악은 자리표시 음원`, bx, by - 14, { size: 16, w: 700, color: C.ink });
  txt(`${Math.round(p * 100)}%`, bx + bw, by - 14, { mono: true, size: 16, w: 700, color: C.lime, align: 'right' });
}
function sceneDevelop(t) {
  const T = S0('develop'), l = t - T;
  const G0 = T + 6.2, FIX_AT = T + 10.4;
  const grow = seg(l, 14.2, 15.0, E.inOutCubic);     // 게임 창이 커지는 정도
  maskUp('개발', 120, 196, seg(l, 0.0, 0.5), { size: 58, w: 800, color: C.ink });
  withA(seg(l, 0.2, 0.6) * (1 - grow), () => { txt('04 · 엔지니어 ⇄ QA · 모듈마다 바로 검증', 124, 236, { mono: true, size: 16, w: 600, color: C.lime, track: 2 }); chip(W - 120, 222, 'engine: web · Phaser 3', { size: 14, h: 28, color: C.lime, align: 'right' }); });
  // 계획 두 장(0~4)
  const plans = seg(l, 0.3, 0.7, E.outExpo) * (1 - seg(l, 3.6, 4.0));
  if (plans > 0) withA(plans, () => {
    let x = 120, y = 262, w = 800, h = 500;
    panel(x, y, w, h, { fill: '#0A0C11', stroke: hexA(C.lime, 0.35) });
    txt('04_engineer_plan.md', x + 28, y + 42, { mono: true, size: 15, w: 700, color: C.lime });
    chip(x + w - 24, y + 36, 'gameplay-engineer · opus', { size: 12, h: 24, color: C.opus, fill: hexA(C.opus, 0.12), align: 'right' });
    txt('모듈', x + 28, y + 92, { size: 14, w: 700, color: C.dim }); txt('완료 기준', x + 300, y + 92, { size: 14, w: 700, color: C.dim });
    MODULES.forEach(([m, c], i) => {
      const a = seg(l, 0.6 + i * 0.12, 0.9 + i * 0.12); const yy = y + 144 + i * 66;
      withA(a, () => { circle(x + 44, yy - 8, 15, hexA(C.lime, 0.14), C.lime, 1.5); txt(String(i + 1), x + 44, yy - 2, { size: 15, w: 800, color: C.lime, align: 'center' });
        txt(m, x + 74, yy, { size: 23, w: 700, color: C.ink }); txt(c, x + 300, yy, { size: 18, w: 500, color: C.dim }); });
    });
    x = 960; w = 840;
    panel(x, y, w, h, { fill: '#0A0C11', stroke: hexA(C.red, 0.35) });
    txt('qa/test-plan.md', x + 28, y + 42, { mono: true, size: 15, w: 700, color: C.red });
    chip(x + w - 24, y + 36, 'game-qa · opus', { size: 12, h: 24, color: C.opus, fill: hexA(C.opus, 0.12), align: 'right' });
    TESTS.forEach((s, i) => { const a = seg(l, 1.2 + i * 0.2, 1.45 + i * 0.2); withA(a, () => txt(s, x + 28 + (1 - a) * 20, y + 100 + i * 42, { mono: true, size: 17, w: 500, color: C.ink })); });
    const n = Math.round(42 * seg(l, 1.2, 2.8, E.outCubic));
    txt(String(n), x + w - 40, y + h - 40, { size: 72, w: 800, color: C.red, align: 'right' });
    txt('테스트 케이스 · GDD 기준', x + w - 40, y + h - 118, { size: 15, w: 600, color: C.dim, align: 'right' });
    withA(seg(l, 2.4, 2.8), () => chip(x + 28, y + h - 50, 'engineer → qa: "모듈 끝나면 바로 알릴게요"', { size: 13, h: 28, color: C.lime, fill: hexA(C.lime, 0.1), mono: false }));
  });
  // 코드 편집기(4~)
  const ep = seg(l, 3.9, 4.3, E.outExpo) * (1 - grow);
  withA(ep, () => {
    const x = 120, y = 262, w = 800, h = 440;
    panel(x, y, w, h, { fill: '#0A0C11', stroke: 'rgba(255,255,255,0.12)' });
    [C.coral, C.amber, C.green].forEach((c, i) => circle(x + 26 + i * 22, y + 24, 6, c));
    chip(x + 110, y + 24, 'web/src/main.js', { size: 13, h: 26, color: C.ink });
    chip(x + 290, y + 24, 'gameplay-engineer · opus', { size: 13, h: 26, color: C.lime, fill: hexA(C.lime, 0.1) });
    let chars = Math.floor((l - 4.3) * 140);
    CODE.forEach((s, i) => {
      const yy = y + 80 + i * 38;
      txt(String(i + 1).padStart(2, ' '), x + 20, yy, { mono: true, size: 15, w: 500, color: C.mute });
      if (chars <= 0) return;
      const part = s.slice(0, Math.min(s.length, chars)); chars -= s.length;
      codeLine(part, x + 62, yy, { size: 16 });
      if (chars < 0 && chars > -s.length) { ctx.fillStyle = C.lime; ctx.fillRect(x + 62 + tw(part, 500, 16, true) + 2, yy - 16, 10, 20); }
    });
    if (l >= 9.55) FIX.forEach(([sg, s], i) => {
      const yy = y + 80 + (CODE.length + 0.4 + i) * 38, a = seg(l, 9.6 + i * 0.2, 9.8 + i * 0.2);
      withA(a, () => { ctx.fillStyle = sg === '-' ? hexA(C.red, 0.18) : hexA(C.green, 0.18); ctx.fillRect(x + 2, yy - 26, w - 4, 36);
        txt(sg, x + 30, yy, { mono: true, size: 17, w: 800, color: sg === '-' ? C.red : C.green });
        codeLine(s, x + 62, yy, { size: 16 }); });
    });
  });
  // 모듈 진행
  withA(seg(l, 10.4, 10.7) * (1 - grow), () => {
    MODULES.forEach(([m], i) => {
      const yy = 744 + i * 32, p = seg(l, 10.5 + i * 0.6, 11.0 + i * 0.6, E.outCubic);
      txt(m, 124, yy + 6, { size: 18, w: 700, color: p >= 1 ? C.ink : C.dim });
      ctx.fillStyle = 'rgba(255,255,255,0.08)'; ctx.fillRect(330, yy - 4, 470, 9);
      ctx.fillStyle = p >= 1 ? C.lime : hexA(C.lime, 0.6); ctx.fillRect(330, yy - 4, 470 * p, 9);
      if (p >= 1) at(846, yy, seg(l, 11.0 + i * 0.6, 11.25 + i * 0.6, E.outBack), 0, () => chip(0, 0, '✓ qa', { align: 'center', size: 12, h: 22, w: 800, color: '#05060A', fill: C.lime }));
    });
  });
  // 게임 창
  const gp = seg(l, 4.1, 4.55, E.outExpo);
  if (gp > 0) {
    const G = GAME, gx = G.x + G.w / 2, gy = G.y + G.h / 2;
    const cx = lerp(gx, 960, grow), cy = lerp(gy, 510, grow), sc = lerp(lerp(0.9, 1, gp), 1.3, grow);
    ctx.save(); ctx.translate(cx, cy); ctx.scale(sc, sc); ctx.translate(-gx, -gy); ctx.globalAlpha *= clamp(gp * 2);
    panel(G.x, G.y, G.w, G.h, { fill: '#07090D', stroke: hexA(C.lime, 0.4), lw: 1.5, glow: 40, glowColor: hexA(C.lime, 0.18) });
    txt('coin-runner — localhost:8000/web/', G.x + 20, G.y + 29, { mono: true, size: 14, w: 600, color: C.dim });
    chip(G.x + G.w - 16, G.y + 22, 'game-qa · Playwright', { size: 12, h: 24, color: C.red, fill: hexA(C.red, 0.12), align: 'right' });
    const probe = seg(l, 7.9, 8.15) * (1 - seg(l, 10.8, 11.0));
    if (t < G0) drawBoot(t, T + 4.4); else drawGame(t, G0, FIX_AT, probe);
    const crt = 1 - seg(t, G0, G0 + 0.35);
    if (t >= G0 && crt > 0) { ctx.save(); ctx.globalAlpha = crt; ctx.fillStyle = '#fff'; ctx.fillRect(G.x, G.y + 44 + (G.h - 44) / 2 * (1 - crt), G.w, (G.h - 44) * crt); ctx.restore(); }
    ctx.restore();
  }
  // 버그 카드
  const bp = seg(l, 8.2, 8.5, E.outBack), bout = seg(l, 11.3, 11.6, E.inCubic);
  if (bp > 0 && bout < 1) {
    const ok = l >= 10.6, col = ok ? C.green : C.red;
    at(1380 + bout * 800, 830, bp, 0, () => {
      panel(-420, -86, 840, 172, { fill: ok ? '#0B140E' : '#160A0C', stroke: col, lw: 2, glow: 40, glowColor: hexA(col, 0.4) });
      txt('BUG-012', -390, -38, { mono: true, size: 20, w: 800, color: col });
      chip(-270, -45, 'S2', { size: 13, h: 24, w: 800, color: '#05060A', fill: col });
      txt(ok ? 'engineer 수정 → game-qa 재확인' : 'game-qa → engineer', 390, -38, { mono: true, size: 14, w: 600, color: C.dim, align: 'right' });
      txt('코인 1개에 점수가 두 번 올라간다', -390, 8, { size: 28, w: 800, color: C.ink });
      txt('기대 +10 · 실제 +20 · data/balance/items.csv  ↔  web/src/score.js:42', -390, 48, { mono: true, size: 14, w: 500, color: C.dim });
      const vp = seg(l, 10.6, 10.8, E.outBackBig);
      if (vp > 0) at(300, 18, vp, -0.12, () => { ctx.save(); ctx.strokeStyle = C.green; ctx.lineWidth = 5; rr(-110, -34, 220, 68, 10); ctx.stroke(); ctx.restore(); txt('VERIFIED', 0, 11, { size: 32, w: 800, color: C.green, align: 'center', track: 3 }); });
    });
  }
  const pk = inv(8.8, 9.2, l);
  if (pk > 0 && pk < 1) { const e = E.inOutCubic(pk); for (let k = 0; k < 8; k++) { const u = clamp(e - k * 0.03); glowDot(lerp(1100, 700, u), lerp(790, 560, u) - Math.sin(Math.PI * u) * 120, 28 - k * 3, k ? C.red : '#fff', 1 - k / 8); } }
  // 동결: 커진 게임 창 아래에 모듈 다섯 개와 동결 표시
  if (grow > 0) withA(grow, () => {
    let x = 414;
    MODULES.forEach(([m], i) => { const a = seg(l, 14.6 + i * 0.08, 14.9 + i * 0.08); withA(a, () => { x += chip(x, 874, '✓ ' + m, { size: 14, h: 30, w: 700, color: '#05060A', fill: C.lime, mono: false }) + 10; }); });
    const fp = seg(l, 15.4, 15.6, E.outBackBig);
    if (fp > 0) at(1506, 874, fp, 0, () => chip(0, 0, 'BUILD FROZEN · freeze_04.sha', { size: 15, h: 34, w: 800, color: C.lime, fill: '#0B1206', stroke: C.lime, align: 'right' }));
  });
}
