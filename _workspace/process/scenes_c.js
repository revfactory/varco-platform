// ============================================================================
// 장면 C: 05 출시 · 결과물 · 엔딩
// ============================================================================
function initScenesC() {
  addScene('release', sceneRelease);
  addScene('deliver', sceneDeliver);
  addScene('outro', sceneOutro);
}

// ------------------------------------------------------------------ 05 출시
const REPORTS = [
  { t: '에셋 전수 감사', r: 'asset-qa', v: '21 / 21', c: C.cyan, done: 1.4 }, { t: '회귀 테스트', r: 'game-qa', v: '42 PASS', c: C.lime, done: 1.9 },
  { t: '밸런스 구현 대조', r: 'balance-analyst', v: 'CSV = 코드', c: C.violet, done: 2.3 }, { t: '스토어 이미지', r: 'marketing-artist', v: 'capsule ×3', c: C.coral, done: 2.8 },
];
const CHECKS = [['버그 S1·S2 미해결', '0건'], ['P0 에셋 qa_passed', '21 / 21'], ['데이터 정합성 불일치', '0건'], ['현지화 누락 · 글자 수 초과', '0건'], ['밸런스 판정', 'PASS'], ['크레딧 사용 / 예산', '1,118 / 1,364']];
function sceneRelease(t) {
  const T = S0('release'), l = t - T;
  const dark = seg(l, 7.6, 7.7) * (1 - seg(l, 8.0, 8.02));
  if (l < 8.0) {
    const push = 1 + seg(l, 6.3, 7.65, E.inCubic) * 0.06;
    ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(push, push); ctx.translate(-W / 2, -H / 2); ctx.globalAlpha *= 1 - dark;
    planLeft(t, '05', T, '출시', 'SHIP · 병렬 검사 4개 → 디렉터 판정', C.coral);
    withA(seg(l, 0.6, 1.0), () => {
      txt('계약서 9절 기준표로만 판정한다.', 124, 590, { size: 20, w: 500, color: C.dim });
      txt('Agent × 4 · 한 메시지에서 동시에 실행', 1800, 124, { mono: true, size: 13, w: 700, color: C.coral, align: 'right', track: 1 });
    });
    REPORTS.forEach((rp, k) => {
      const p = seg(l, 0.3 + k * 0.08, 0.75 + k * 0.08, E.outBack); if (p <= 0) return;
      const x = 760 + k * 265, y = 140, done = l >= rp.done;
      at(x + 122, y + 110, p, 0, () => {
        panel(-122, -110, 244, 220, { fill: '#0C0D13', stroke: hexA(rp.c, done ? 0.7 : 0.35), lw: done ? 2 : 1.2 });
        txt(rp.r, -100, -70, { mono: true, size: 12, w: 600, color: rp.c });
        txt(rp.t, -100, -36, { size: 21, w: 800, color: C.ink });
        if (!done) {
          ctx.save(); ctx.strokeStyle = rp.c; ctx.lineWidth = 4; ctx.lineCap = 'round'; ctx.beginPath(); const a0 = t * 6 + k; ctx.arc(-76, 26, 20, a0, a0 + 4.2); ctx.stroke(); ctx.restore();
          txt('검사 중', -40, 34, { size: 20, w: 700, color: C.dim });
          return;
        }
        const dp = seg(l, rp.done, rp.done + 0.25, E.outBack);
        at(0, 0, lerp(0.8, 1, dp), 0, () => {
          if (k === 3) {
            const g = ctx.createLinearGradient(-100, -10, 100, 80); g.addColorStop(0, '#2A1420'); g.addColorStop(1, '#0F2230');
            rr(-100, -12, 200, 92, 8); ctx.fillStyle = g; ctx.fill();
            circle(60, 40, 14, C.gold); circle(30, 58, 8, C.gold);
            txt('COIN RUNNER', -86, 38, { size: 22, w: 800, color: C.ink });
            ctx.fillStyle = C.lime; rr(-86, 50, 14, 20, 3); ctx.fill();
          } else txt(rp.v, -100, 50, { size: 34, w: 800, color: rp.c });
        });
        txt('✓ 보고서 제출', -100, 96, { size: 14, w: 700, color: C.green, alpha: dp });
      });
      if (l >= rp.done) shockRing(x + 122, y + 110, t, T + rp.done, rp.c, { r: 200, r0: 40, lw: 4, life: 0.5 });
    });
    withA(seg(l, 3.4, 3.7), () => {
      const x = 760, y = 400, w = 1040;
      panel(x, y, w, 490, { fill: 'rgba(255,94,98,0.05)', stroke: hexA(C.coral, 0.4) });
      txt('RELEASE CRITERIA', x + 32, y + 46, { mono: true, size: 16, w: 700, color: C.coral, track: 4 });
      txt('game-director · fable', x + w - 32, y + 46, { mono: true, size: 13, w: 600, color: C.gold, align: 'right' });
      CHECKS.forEach(([lb, v], i) => {
        const ct = 3.8 + i * 0.45, yy = y + 108 + i * 64;
        const on = l >= ct, cp = seg(l, ct, ct + 0.2, E.outBackBig);
        if (on) { ctx.fillStyle = hexA(C.green, 0.08 * (1 - inv(ct, ct + 0.6, l)) + 0.03); ctx.fillRect(x + 2, yy - 34, w - 4, 54); }
        circle(x + 52, yy - 8, 18, on ? C.green : 'rgba(255,255,255,0.05)', on ? null : 'rgba(255,255,255,0.25)', 1.5);
        if (on) at(x + 52, yy - 8, cp, 0, () => txt('✓', 0, 8, { size: 22, w: 800, color: '#05060A', align: 'center' }));
        txt(lb, x + 92, yy, { size: 25, w: 700, color: on ? C.ink : C.dim });
        withA(on ? 1 : 0.3, () => txt(v, x + w - 34, yy, { size: 25, w: 800, color: on ? C.green : C.dim, align: 'right' }));
      });
    });
    ctx.restore();
    const conv = seg(l, 6.4, 7.65, E.inCubic);
    if (conv > 0) { ctx.save(); ctx.globalCompositeOperation = 'lighter'; const r = rng(49); for (let k = 0; k < 40; k++) { const a = r() * Math.PI * 2, d0 = 1400 * (1 - conv) + 200 * r(); ctx.globalAlpha = 0.25 * conv; line(W / 2 + Math.cos(a) * d0, H / 2 + Math.sin(a) * d0, W / 2 + Math.cos(a) * (d0 + 180), H / 2 + Math.sin(a) * (d0 + 180), k % 2 ? C.coral : '#fff', 2); } ctx.restore(); }
    if (dark > 0) withA(dark, () => { ctx.fillStyle = '#000'; ctx.fillRect(-50, -50, W + 100, H + 100); txt('게임 디렉터 판정 중', W / 2, H / 2 + 10, { mono: true, size: 18, w: 600, color: C.dim, align: 'center', track: 6 }); });
    return;
  }
  // GO
  const d = t - GO_T;
  const ray = Math.max(0, 1 - d * 0.5);
  ctx.save(); ctx.translate(W / 2, 520); ctx.rotate(d * 0.15); ctx.globalCompositeOperation = 'lighter';
  for (let k = 0; k < 24; k++) { ctx.rotate(Math.PI * 2 / 24); ctx.globalAlpha = 0.07 + 0.05 * ray; ctx.fillStyle = k % 2 ? C.coral : C.amber; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(1500, -70); ctx.lineTo(1500, 70); ctx.closePath(); ctx.fill(); }
  ctx.restore();
  shockRing(W / 2, 520, t, GO_T, C.coral, { r: 1500, lw: 16, life: 1.0 });
  shockRing(W / 2, 520, t, GO_T + 0.08, '#fff', { r: 1200, lw: 8, life: 0.8 });
  shockRing(W / 2, 520, t, GO_T + 0.2, C.amber, { r: 1000, lw: 5, life: 0.9 });
  burst(W / 2, 520, t, GO_T, 160, 505, [C.coral, C.amber, C.lime, C.cyan, C.violet, '#fff'], { speed: 2600, life: 1.5, grav: true });
  const p = seg(t, GO_T, GO_T + 0.22, E.outExpo);
  const pulse = 1 + kickPulse(t) * 0.03;
  at(W / 2, 520, lerp(2.2, 1, p) * pulse, 0, () => {
    txt('GO', 0, 170, { size: 480, w: 800, color: C.coral, align: 'center', glow: 80, glowColor: hexA(C.coral, 0.9), track: -10, blur: (1 - p) * 30 });
    txt('GO', 0, 170, { size: 480, w: 800, color: '#FFFFFF', align: 'center', track: -10, alpha: 0.9 * (1 - seg(t, GO_T + 0.05, GO_T + 0.4)) });
  });
  withA(seg(t, GO_T + 0.25, GO_T + 0.6), () => {
    txt('출시 가능', W / 2, 800, { size: 44, w: 800, color: C.ink, align: 'center' });
    txt('RELEASE_REPORT.md · 기준 6/6 통과', W / 2, 850, { mono: true, size: 18, w: 600, color: C.dim, align: 'center', track: 3 });
  });
}

// ------------------------------------------------------------------ 결과물
const TREE = [
  ['games/coin-runner/', '확정본 · 사람과 다음 단계가 보는 결과', C.ink, 1],
  ['├─ docs/', 'GDD · 시스템 · 시나리오 · 레벨 · UX · 밸런스 보고서', C.violet, 0],
  ['├─ data/', '밸런스 CSV · 대사 · UI 문자열 · strings/ko·en·ja', C.violet, 0],
  ['├─ assets/', '효과음 · 환경음 · 대사 음성 · 얼굴 애니메이션 · 3D', C.cyan, 0],
  ['├─ manifest.json', '에셋 25건 · qa_passed 21 · 수동 제작 1', C.amber, 0],
  ['├─ web/', 'Phaser 3 프로토타입 · 브라우저에서 바로 실행', C.lime, 0],
  ['├─ qa/', '테스트 계획 · 버그 리포트 · 회귀 보고서', C.red, 0],
  ['├─ marketing/', '스토어 캡슐 · 키 아트', C.coral, 0],
  ['└─ RELEASE_REPORT.md', '출시 판정서', C.coral, 2],
];
const FOLLOW = [
  ['대사 음성만 다시 뽑아줘', '03 제작 · 해당 에셋만', C.cyan],
  ['적이 너무 세, 밸런스 수정해줘', '01 시스템 · 밸런스 → 구현 수치 대조', C.violet],
  ['중국어 번역도 추가해줘', '02 명세 → 크레딧 승인 → 03 제작', C.amber],
  ['버그 고쳐줘', '04 엔지니어 ⇄ QA 한 쌍만', C.lime],
];
function sceneDeliver(t) {
  const T = S0('deliver'), l = t - T;
  maskUp('결과물', 120, 196, seg(l, 0.0, 0.5), { size: 58, w: 800, color: C.ink });
  withA(seg(l, 0.2, 0.6), () => txt('games/coin-runner  ·  _workspace/coin-runner', 124, 236, { mono: true, size: 16, w: 600, color: C.paper, track: 2 }));
  // 폴더
  withA(seg(l, 0.1, 0.4), () => {
    const x = 120, y = 262, w = 880, h = 640;
    panel(x, y, w, h, { fill: '#0A0C11', stroke: 'rgba(255,255,255,0.14)' });
    TREE.forEach(([name, desc, col, kind], i) => {
      const lt = 0.3 + i * 0.2, a = seg(l, lt, lt + 0.25); if (a <= 0) return;
      const yy = y + 62 + i * 56;
      withA(a, () => {
        txt(name, x + 32 + (1 - a) * 16, yy, { mono: true, size: 19, w: 700, color: kind === 1 ? C.ink : col });
        if (kind === 2) chip(x + 330, yy - 6, 'GO', { size: 14, h: 26, w: 800, color: '#05060A', fill: C.coral });
        txt(desc, x + (kind === 2 ? 400 : 330), yy, { size: 17, w: 500, color: kind === 1 ? C.dim : C.ink });
      });
    });
    withA(seg(l, 2.1, 2.4), () => {
      const yy = y + 62 + TREE.length * 56 + 14;
      line(x + 32, yy - 34, x + w - 32, yy - 34, 'rgba(255,255,255,0.08)', 1);
      txt('_workspace/coin-runner/', x + 32, yy, { mono: true, size: 19, w: 700, color: C.dim });
      txt('초안 · 메시지 기록 · 크레딧 장부 · 동결 해시', x + 330, yy, { size: 17, w: 500, color: C.dim });
    });
  });
  // 이어서 요청하기
  withA(seg(l, 2.8, 3.1), () => {
    const x = 1040, y = 262, w = 760, h = 640;
    panel(x, y, w, h, { fill: 'rgba(255,255,255,0.03)', stroke: 'rgba(255,255,255,0.12)' });
    txt('이어서 요청하기', x + 32, y + 52, { size: 26, w: 800, color: C.ink });
    txt('바뀐 부분만 다시 돌린다', x + w - 32, y + 52, { size: 15, w: 600, color: C.dim, align: 'right' });
    FOLLOW.forEach(([q, a, col], k) => {
      const q0 = 3.0 + k * 0.6, a0 = 3.3 + k * 0.6, yy = y + 128 + k * 128;
      const qp = seg(l, q0, q0 + 0.3, E.outBack); if (qp <= 0) return;
      const qw = tw(q, 700, 21) + 52;
      at(x + w - 32 - qw / 2, yy, qp, 0, () => { rr(-qw / 2, -26, qw, 52, 26); ctx.fillStyle = hexA(C.lime, 0.12); ctx.fill(); ctx.strokeStyle = hexA(C.lime, 0.5); ctx.lineWidth = 1.2; ctx.stroke(); txt(q, 0, 8, { size: 21, w: 700, color: C.ink, align: 'center' }); });
      txt('❯', x + w - 32 - qw - 22, yy + 7, { size: 20, w: 700, color: C.lime, alpha: qp });
      const ap = seg(l, a0, a0 + 0.3, E.outCubic);
      if (ap > 0) withA(ap, () => { txt('→', x + 40, yy + 58, { size: 20, w: 700, color: col }); chip(x + 72 + (1 - ap) * 20, yy + 52, a, { size: 17, h: 34, w: 700, color: '#05060A', fill: col, mono: false }); });
    });
  });
}

// ------------------------------------------------------------------ 엔딩
const MONTAGE = [['overview', 16.1, C.violet, '전체 흐름'], ['plan', 33.2, C.violet, '01 기획'], ['spec', 55.4, C.amber, '02 명세'], ['produce', 63.6, C.cyan, '03 제작'],
  ['produce', 70.4, C.cyan, '03 제작'], ['develop', 88.3, C.lime, '04 개발'], ['release', 101.9, C.coral, '05 출시'], ['release', 104.9, C.coral, '05 출시']];
function sceneOutro(t) {
  const T = S0('outro'), l = t - T;
  if (l < 2.0) {
    const i = Math.min(7, Math.floor(l / 0.25)), [name, ft, col, label] = MONTAGE[i];
    const lt = l - i * 0.25;
    drawBackground(ft, { accent: col });
    const z = 1.06 + lt * 0.35;
    ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.rotate((i % 2 ? 1 : -1) * 0.012); ctx.translate(-W / 2, -H / 2);
    drawSceneAt(name, ft + lt * 0.8);
    ctx.restore();
    ctx.save(); ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = 0.35; ctx.fillStyle = col; ctx.fillRect(0, 0, W, H); ctx.restore();
    if (lt < 0.035) { ctx.save(); ctx.globalAlpha = 0.6; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
    chip(W / 2, 70, label, { align: 'center', size: 16, w: 800, h: 34, color: '#05060A', fill: col, mono: false });
    return;
  }
  const up = seg(l, 3.3, 3.8, E.inOutCubic);
  withA(1 - up, () => {
    ctx.save(); ctx.translate(0, -up * 120);
    staggerText('한 줄의 아이디어에서', W / 2, 470, t, T + 2.0, { size: 84, w: 800, color: C.ink, align: 'center', per: 0.035, track: -2 });
    const l2 = '출시 판정까지.';
    staggerText(l2, W / 2, 590, t, T + 2.4, { size: 84, w: 800, color: C.ink, align: 'center', per: 0.035, track: -2 });
    const tot = tw(l2, 800, 84, false, -2), hiW = tw('출시 판정', 800, 84, false, -2);
    ctx.save(); ctx.beginPath(); ctx.rect(W / 2 - tot / 2, 480, hiW * seg(l, 2.8, 3.15, E.inOutCubic), 140); ctx.clip();
    txt('출시 판정', W / 2 - tot / 2, 590, { size: 84, w: 800, color: C.coral, track: -2 }); ctx.restore();
    ctx.restore();
  });
  const fin = 1 + seg(l, 6.0, 6.12, E.outCubic) * 0.03 + (l > 6 ? (l - 6) * 0.02 : 0);
  ctx.save(); ctx.translate(W / 2, 520); ctx.scale(fin, fin); ctx.translate(-W / 2, -520);
  drawLogotype(t, T + 3.55, 500, { size: 210 });
  withA(seg(l, 4.1, 4.5), () => {
    const items = ['15 에이전트', '17 스킬', '5단계', '사람 확인 2번'];
    let tot = 0; const gap = 56; items.forEach(s => tot += tw(s, 700, 30)); tot += gap * (items.length - 1);
    let x = W / 2 - tot / 2;
    items.forEach((s, i) => { txt(s, x, 812, { size: 30, w: 700, color: i === 3 ? C.gold : C.ink }); x += tw(s, 700, 30) + gap; if (i < 3) circle(x - gap / 2, 802, 4, C.mute); });
  });
  ctx.restore();
  withA(seg(l, 4.6, 5.0), () => {
    txt('MOTION GRAPHICS & DIRECTION — CLAUDE', W / 2, 948, { mono: true, size: 16, w: 700, color: C.dim, align: 'center', track: 6 });
    txt('Harness v2 on Claude Code · VARCO API Platform', W / 2, 980, { size: 16, w: 500, color: C.mute, align: 'center', track: 1 });
  });
  shockRing(W / 2, 480, t, T + 6.0, '#ffffff', { r: 1400, lw: 6, life: 1.0, alpha: 0.5 });
}
