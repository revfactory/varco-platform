// ============================================================================
// 장면 A: 콜드 오픈 · 타이틀 · 팀 · 01 기획
// ============================================================================

// ------------------------------------------------------------------ 00 콜드 오픈
function sceneColdOpen(t) {
  const P = CUES.prompt, TT = CUES.typing, chars = [...P];
  const size = 56, y = 572;
  const fullW = tw(P, 600, size), x0 = Math.round(W / 2 - fullW / 2 + 30);
  const push = 1 + 0.035 * seg(t, 0.3, 3.45, E.inOutSine);
  ctx.save(); ctx.translate(W / 2, y); ctx.scale(push, push); ctx.translate(-W / 2, -y);

  // 터미널 머리말
  withA(seg(t, 0.15, 0.7) * (1 - seg(t, 3.5, 3.7)), () => {
    txt('claude', x0 - 62, y - 92, { mono: true, size: 18, w: 700, color: C.lime });
    txt('~/varco-platform', x0 + 16, y - 92, { mono: true, size: 18, w: 500, color: C.dim });
    txt('› varco-game-studio', x0 + 206, y - 92, { mono: true, size: 18, w: 500, color: C.mute });
  });

  const collapse = seg(t, 3.52, 3.7, E.inCubic);
  const lineGrow = seg(t, 3.68, 3.9, E.inOutCubic);
  let cx = x0;
  let typedW = 0, lastT = -1, lastX = x0;
  ctx.save();
  if (collapse > 0) { ctx.translate(0, y - 16); ctx.scale(1, 1 - collapse); ctx.translate(0, -(y - 16)); }
  withA(seg(t, 0.2, 0.5), () => txt('❯', x0 - 62, y, { size: size, w: 700, color: C.lime, glow: 18 }));
  for (let i = 0; i < chars.length; i++) {
    const ch = chars[i]; const cw = tw(ch, 600, size);
    if (t >= TT[i]) {
      const p = seg(t, TT[i], TT[i] + 0.16, E.outBack);
      const col = mixHex(C.lime, C.ink, seg(t, TT[i], TT[i] + 0.35, E.lin));
      at(cx + cw / 2, y - size * 0.35, lerp(1.35, 1, p), 0, () => {
        txt(ch, -cw / 2, size * 0.35, { size, w: 600, color: col, alpha: clamp(p * 2) });
      });
      const k = Math.exp(-(t - TT[i]) * 7);
      if (k > 0.02 && ch !== ' ') glowDot(cx + cw / 2, y - 14, 60, C.lime, 0.35 * k);
      typedW = cx + cw - x0; lastT = TT[i]; lastX = cx + cw;
    }
    cx += cw;
  }
  // 커서
  const typing = t < lastT + 0.18 && t < 3.0;
  const blink = Math.floor(t * 2.4) % 2 === 0;
  if ((typing || blink || t < 0.55) && t < 3.58) {
    const bx = lastT < 0 ? x0 : lastX + 6;
    ctx.fillStyle = C.lime; ctx.shadowColor = C.lime; ctx.shadowBlur = 16;
    ctx.fillRect(bx, y - size * 0.82, 24, size * 0.98); ctx.shadowBlur = 0;
  }
  ctx.restore();
  // 엔터 표시와 줄 전체 빛
  withA(seg(t, 3.05, 3.3) * (1 - seg(t, 3.45, 3.55)), () => chip(x0 + typedW + 50, y - 16, '↵ Enter', { color: C.bg, fill: C.lime, size: 16, w: 800 }));
  const flash = seg(t, 3.45, 3.5) * (1 - seg(t, 3.5, 3.75));
  if (flash > 0) glowDot(x0 + typedW / 2, y - 16, 900, C.lime, 0.5 * flash);
  // 한 줄의 빛으로 접히고 화면 끝까지 뻗는다
  if (lineGrow > 0) {
    const l = lerp(x0 - 62, 0, lineGrow), r = lerp(x0 + typedW, W, lineGrow);
    const th = lerp(3, 6, lineGrow) + seg(t, 3.88, 4.0, E.inExpo) * H;
    ctx.save(); ctx.shadowColor = C.lime; ctx.shadowBlur = 40;
    ctx.fillStyle = mixHex(C.lime, '#ffffff', seg(t, 3.8, 3.95)); ctx.fillRect(l, y - 16 - th / 2, r - l, th); ctx.restore();
  }
  ctx.restore();
}

// ------------------------------------------------------------------ 00 타이틀
const TITLE_WORDS = [
  { s: '한 줄의 아이디어', hi: '아이디어', t: 4.0, color: C.lime },
  { s: '열다섯 명의 에이전트', hi: '에이전트', t: 5.0, color: C.violet },
  { s: '하나의 게임', hi: '게임', t: 6.0, color: C.coral },
];
const STACK = [{ y: 612, size: 168, a: 1 }, { y: 432, size: 78, a: 0.5 }, { y: 336, size: 58, a: 0.3 }];
function titleWord(t, i) {
  const wd = TITLE_WORDS[i]; if (t < wd.t) return;
  let lv = 0; for (let j = i + 1; j < TITLE_WORDS.length; j++) lv += seg(t, TITLE_WORDS[j].t, TITLE_WORDS[j].t + 0.4);
  const a = STACK[Math.floor(lv)], b = STACK[Math.min(2, Math.floor(lv) + 1)], f = lv - Math.floor(lv);
  let size = lerp(a.size, b.size, f), y = lerp(a.y, b.y, f), alpha = lerp(a.a, b.a, f);
  if (i === 2) size *= 1.12;
  const p = seg(t, wd.t, wd.t + 0.32, E.outExpo);
  const sc = lerp(1.6, 1, p);
  // 퇴장: 왼쪽으로 날아간다
  const out = seg(t, 6.55 + i * 0.06, 6.95 + i * 0.06, E.inExpo);
  const ox = -out * 2200;
  const total = tw(wd.s, 800, size, false, -2);
  const idx = wd.s.indexOf(wd.hi), pre = tw(wd.s.slice(0, idx), 800, size, false, -2);
  const x0 = W / 2 - total / 2 + ox;
  const draw = (dx, al) => at(W / 2 + dx, y - size * 0.35, sc, 0, () => {
    const bx = -total / 2;
    txt(wd.s, bx, size * 0.35, { size, w: 800, color: C.ink, alpha: al * alpha * clamp(p * 3), blur: (1 - p) * 22, track: -2 });
    txt(wd.hi, bx + pre, size * 0.35, { size, w: 800, color: wd.color, alpha: al * clamp(p * 3) * lerp(1, alpha * 1.4, lv > 0 ? 1 : 0), blur: (1 - p) * 22, track: -2 });
  });
  if (out > 0) for (let k = 1; k <= 4; k++) draw(ox + k * 90 * out, 0.12 / k);
  draw(ox, 1);
  // 강조 밑줄
  const u = seg(t, wd.t + 0.12, wd.t + 0.5) * (1 - lv * 0.7);
  if (u > 0 && out < 1) { ctx.fillStyle = wd.color; ctx.fillRect(x0 + pre, y + size * 0.14, tw(wd.hi, 800, size, false, -2) * u, Math.max(3, size * 0.045)); }
}
function sceneTitle(t) {
  // 박힐 때마다 번지는 충격파와 가로 속도선
  for (const wd of TITLE_WORDS) {
    const d = t - wd.t; if (d < 0 || d > 0.7) continue;
    ctx.save(); ctx.globalAlpha = 0.5 * (1 - d / 0.7); ctx.strokeStyle = wd.color; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.ellipse(W / 2, 560, 200 + d * 1600, 80 + d * 700, 0, 0, Math.PI * 2); ctx.stroke(); ctx.restore();
    const r = rng(Math.floor(wd.t * 100));
    for (let k = 0; k < 16; k++) {
      const yy = 300 + r() * 520, len = 200 + r() * 500, dir = r() < 0.5 ? -1 : 1;
      const xs = W / 2 + dir * (200 + d * 3000 * (0.5 + r()));
      line(xs, yy, xs - dir * len, yy, k % 3 === 0 ? wd.color : '#fff', 2, 0.35 * (1 - d / 0.7));
    }
  }
  for (let i = 0; i < 3; i++) titleWord(t, i);
  drawLogotype(t, 6.8, 560, { zoomFrom: 7.55, zoomTo: 8.0 });
}
// 로고: VARCO / GAME STUDIO / 단계 색 막대
function drawLogotype(t, t0, cy, o = {}) {
  if (t < t0) return;
  const word = 'VARCO', size = o.size || 196, track = 28;
  const total = tw(word, 800, size, false, track) - track;
  let zoom = 1, za = 1, zx = W / 2, zy = cy;
  // O 글자 가운데를 찾아 그 안으로 파고든다
  const oW = tw('O', 800, size, false, 0);
  const oX = W / 2 + total / 2 - oW / 2, oY = cy - size * 0.36;
  if (o.zoomFrom) { const zp = seg(t, o.zoomFrom, o.zoomTo, E.inExpo); zoom = lerp(1, 40, zp); za = 1 - seg(t, o.zoomTo - 0.12, o.zoomTo); zx = oX; zy = oY; }
  ctx.save(); ctx.translate(zx, zy); ctx.scale(zoom, zoom); ctx.translate(-zx, -zy); ctx.globalAlpha *= za;
  let x = W / 2 - total / 2;
  [...word].forEach((ch, i) => {
    const p = seg(t, t0 + i * 0.05, t0 + i * 0.05 + 0.5, E.outBackBig);
    const cw = tw(ch, 800, size, false, track);
    txt(ch, x, cy + (1 - p) * -160, { size, w: 800, color: C.ink, alpha: clamp(p * 2), track, blur: (1 - clamp(p)) * 12 });
    x += cw;
  });
  const g = seg(t, t0 + 0.25, t0 + 0.65);
  maskUp('GAME STUDIO', W / 2, cy + 104, g, { size: 56, w: 700, color: C.ink, align: 'center', track: 30 });
  // 단계 색 막대
  const bw = 132, gap = 10, bx = W / 2 - (bw * 5 + gap * 4) / 2;
  PHASE.forEach((ph, k) => {
    const p = seg(t, t0 + 0.35 + k * 0.06, t0 + 0.75 + k * 0.06);
    ctx.fillStyle = ph.color; ctx.fillRect(bx + k * (bw + gap), cy + 146, bw * p, 6);
  });
  withA(seg(t, t0 + 0.5, t0 + 0.9), () => txt('HARNESS v2 · CLAUDE CODE · 기획부터 QA까지', W / 2, cy + 200, { mono: true, size: 18, w: 500, color: C.dim, align: 'center', track: 4 }));
  ctx.restore();
}

// ------------------------------------------------------------------ 00 팀
const AGENTS = [
  { tag: 'SYS', name: '시스템 기획', model: 'opus', ph: 0 }, { tag: 'NAR', name: '시나리오', model: 'opus', ph: 0 },
  { tag: 'LVL', name: '레벨 디자인', model: 'opus', ph: 0 }, { tag: 'UX', name: 'UI/UX', model: 'sonnet', ph: 0 },
  { tag: 'BAL', name: '밸런스 분석', model: 'opus', ph: 0 }, { tag: 'AST', name: '에셋 프로듀서', model: 'sonnet', ph: 1 },
  { tag: 'SND', name: '사운드', model: 'sonnet', ph: 2 }, { tag: 'VOX', name: '보이스', model: 'sonnet', ph: 2 },
  { tag: 'VIS', name: '비주얼', model: 'sonnet', ph: 2 }, { tag: 'L10N', name: '현지화', model: 'sonnet', ph: 2 },
  { tag: 'AQA', name: '에셋 QA', model: 'sonnet', ph: 2 }, { tag: 'ENG', name: '엔지니어', model: 'opus', ph: 3 },
  { tag: 'GQA', name: '게임 QA', model: 'opus', ph: 3 }, { tag: 'MKT', name: '마케팅', model: 'sonnet', ph: 4 },
];
const MODEL_COLOR = { fable: C.gold, opus: C.opus, sonnet: C.sonnet };
const TEAM = { cx: 960, cy: 486, rx: 600, ry: 250 };
function initScenesA() {
  // 단계 사이에 빈 칸을 둬서 무리 지어 보이게 한다
  const slots = []; let s = 0;
  AGENTS.forEach((a, i) => { if (i > 0 && AGENTS[i - 1].ph !== a.ph) s += 0.9; slots.push(s); s += 1; });
  const total = s + 0.9, start = -Math.PI * 0.97;
  AGENTS.forEach((a, i) => {
    a.ang = start + (slots[i] / total) * Math.PI * 2;
    a.x = TEAM.cx + Math.cos(a.ang) * TEAM.rx; a.y = TEAM.cy + Math.sin(a.ang) * TEAM.ry;
  });
  SCENES.push({ name: 'cold_open', start: 0, end: 4, draw: sceneColdOpen });
  SCENES.push({ name: 'title', start: 4, end: 8, draw: sceneTitle });
  SCENES.push({ name: 'team', start: 8, end: 14, draw: sceneTeam });
  SCENES.push({ name: 'plan', start: 14, end: 22, draw: scenePlan });
}
function drawNode(x, y, r, color, tag, p, o = {}) {
  if (p <= 0) return;
  const s = E.outBack(clamp(p));
  at(x, y, s, 0, () => {
    glowDot(0, 0, r * 2.4, color, 0.35 + (o.hot || 0) * 0.5);
    circle(0, 0, r, '#0B0D14', color, o.lw || 2.5);
    if (o.inner) circle(0, 0, r - 7, null, hexA(color, 0.35), 1);
    txt(tag, 0, r * 0.18, { mono: true, size: o.tagSize || 15, w: 700, color, align: 'center' });
  });
  // 등장할 때 퍼지는 고리
  const d = p * 0.35; if (p < 1) { ctx.save(); ctx.globalAlpha = 0.6 * (1 - p); circle(x, y, r + p * 70, null, color, 2); ctx.restore(); }
}
function sceneTeam(t) {
  const lt = t - 8;
  // 13초부터 기획 무리로 파고든다
  const z = seg(t, 12.9, 14.0, E.inExpo);
  const plan = AGENTS.filter(a => a.ph === 0); const fx = plan.reduce((s, a) => s + a.x, 0) / plan.length, fy = plan.reduce((s, a) => s + a.y, 0) / plan.length;
  ctx.save(); ctx.translate(lerp(0, W / 2 - fx, z), lerp(0, H / 2 - fy, z)); ctx.translate(fx, fy); ctx.scale(1 + z * 1.8, 1 + z * 1.8); ctx.translate(-fx, -fy);
  const { cx, cy, rx, ry } = TEAM;
  // 궤도
  withA(seg(t, 8.0, 9.0) * 0.6, () => {
    ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,0.12)'; ctx.lineWidth = 1; ctx.setLineDash([2, 10]);
    ctx.beginPath(); ctx.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(cx, cy, rx * 0.55, ry * 0.55, 0, 0, Math.PI * 2); ctx.stroke(); ctx.restore();
  });
  // 중심에서 뻗는 선과 오가는 패킷
  AGENTS.forEach((a, k) => {
    const col = PHASE[a.ph].color, dim = a.ph === 0 ? 1 : 1 - z;
    const p = seg(t, 10 + k * 0.05, 10.5 + k * 0.05, E.outCubic);
    if (p > 0) withA(dim, () => {
      line(cx, cy, lerp(cx, a.x, p), lerp(cy, a.y, p), col, 1.4, 0.35);
      if (t > 10.6) { const u = ((t - 10.6) * 0.8 + k * 0.137) % 1; glowDot(lerp(cx, a.x, u), lerp(cy, a.y, u), 14, col, 0.9); }
    });
  });
  // 단계 호(弧)
  PHASE.forEach((ph, i) => {
    const g = AGENTS.filter(a => a.ph === i); const a0 = g[0].ang - 0.12, a1 = g[g.length - 1].ang + 0.12;
    const p = seg(t, 11 + i * 0.12, 11.6 + i * 0.12, E.inOutCubic); if (p <= 0) return;
    withA(i === 0 ? 1 : 1 - z, () => {
      ctx.save(); ctx.strokeStyle = ph.color; ctx.lineWidth = 4; ctx.shadowColor = ph.color; ctx.shadowBlur = 16;
      ctx.beginPath(); ctx.ellipse(cx, cy, rx + 58, ry + 46, 0, a0, lerp(a0, a1, p)); ctx.stroke(); ctx.restore();
      // 단계 이름
      const am = (a0 + a1) / 2, lx = cx + Math.cos(am) * (rx + 205), ly = cy + Math.sin(am) * (ry + 150);
      const lp = seg(t, 12 + i * 0.18, 12.5 + i * 0.18);
      maskUp(`${ph.no} ${ph.name}`, lx, ly + 10, lp, { size: 30, w: 800, color: ph.color, align: 'center' });
      withA(lp, () => txt(ph.en, lx, ly + 36, { mono: true, size: 13, w: 600, color: C.dim, align: 'center', track: 4 }));
    });
  });
  // 에이전트 노드
  AGENTS.forEach((a, k) => {
    const pt = 8.0 + (k + 1) * BEAT / 4;
    const p = seg(t, pt, pt + 0.4, E.lin);
    const col = PHASE[a.ph].color, dim = a.ph === 0 ? 1 : 1 - z;
    withA(dim, () => {
      const hot = Math.exp(-Math.max(0, t - pt) * 5) + (t > 12 ? 0.3 * kickPulse(t) : 0);
      drawNode(a.x, a.y, 34, col, a.tag, p * 2.5, { hot, tagSize: a.tag.length > 3 ? 13 : 15 });
      const lp = seg(t, pt + 0.08, pt + 0.5);
      if (lp > 0) {
        const ux = Math.cos(a.ang), uy = Math.sin(a.ang);
        const align = ux > 0.35 ? 'left' : ux < -0.35 ? 'right' : 'center';
        const lx = a.x + ux * 52, ly = a.y + uy * 50 + (align === 'center' ? (uy > 0 ? 18 : -2) : 7);
        staggerText(a.name, lx, ly, t, pt + 0.08, { size: 19, w: 700, color: C.ink, align, per: 0.02, dur: 0.35, rise: 12 });
        withA(lp, () => { circle(a.x + 27, a.y - 27, 7, MODEL_COLOR[a.model], '#05060A', 2.5); });
      }
    });
  });
  // 게임 디렉터(중심)
  const dp = seg(t, 8.0, 8.5, E.lin);
  withA(1 - z, () => {
    const pulse = kickPulse(t);
    drawNode(cx, cy, 64 + pulse * 4, C.violet, 'DIR', dp * 1.6, { hot: 0.6 + pulse * 0.4, tagSize: 22, lw: 3.5, inner: true });
    if (dp > 0.3) { txt('게임 디렉터', cx, cy + 110, { size: 24, w: 800, color: C.ink, align: 'center', alpha: seg(t, 8.15, 8.5) });
      withA(seg(t, 8.2, 8.6), () => chip(cx, cy + 140, 'fable', { size: 13, color: C.gold, fill: hexA(C.gold, 0.14), h: 24, align: 'center' })); }
  });
  ctx.restore();
  // 제목과 수치(카메라 밖, 고정)
  withA(1 - z, () => {
    withA(seg(t, 8.2, 8.5), () => txt('THE TEAM', 120, 866, { mono: true, size: 16, w: 700, color: C.lime, track: 6 }));
    staggerText('15명의 전문 에이전트', 120, 932, t, 8.25, { size: 58, w: 800, color: C.ink, per: 0.03, track: -1 });
    withA(seg(t, 8.8, 9.3), () => {
      let lx = 122;
      [['fable', 1], ['opus', 6], ['sonnet', 8]].forEach(([m, n]) => { circle(lx + 6, 972, 6, MODEL_COLOR[m]); txt(`${m} ${n}`, lx + 18, 978, { mono: true, size: 15, w: 600, color: C.dim }); lx += 126; });
    });
    const stats = [['15', 'AGENTS'], ['17', 'SKILLS'], ['26', 'SCRIPTS'], ['5', 'PHASES']];
    stats.forEach(([n, l], i) => {
      const p = seg(t, 10 + i * 0.4, 10.9 + i * 0.4, E.outCubic); if (p <= 0) return;
      const x = W - 760 + i * 190, y = 952;
      const v = Math.round(parseInt(n) * p);
      txt(String(v), x, y, { size: 52, w: 800, color: i === 0 ? C.lime : C.ink, align: 'center', alpha: clamp(p * 3) });
      txt(l, x, y + 26, { mono: true, size: 13, w: 600, color: C.dim, align: 'center', track: 4, alpha: clamp(p * 3) });
    });
  });
}

// ------------------------------------------------------------------ 01 기획
const PLAN_ROWS = [
  { name: '게임 디렉터', model: 'fable', start: 14.2, done: 21.3 }, { name: '시스템 기획', model: 'opus', start: 16.0, done: 19.6 },
  { name: '시나리오', model: 'opus', start: 16.25, done: 18.6 }, { name: '레벨 디자인', model: 'opus', start: 16.5, done: 21.05 },
  { name: 'UI/UX', model: 'sonnet', start: 16.75, done: 19.0 }, { name: '밸런스 분석', model: 'opus', start: 17.0, done: 19.55 },
];
const PACKETS = [
  { a: 4, b: 0, t: 18.0, msg: 'balance → systems   grunt.hp 120 → 90 권장 (클리어 150s → 96s)' },
  { a: 0, b: 4, t: 18.25, msg: 'systems → balance   반영 완료 · 재시뮬레이션 요청' },
  { a: 1, b: 2, t: 18.5, msg: 'narrative → level   장면 목록 2개 전달 (intro, boss_appear)' },
  { a: 0, b: 3, t: 18.75, msg: 'systems → ux        HUD 표시 수치: score · coins · hp' },
  { a: 4, b: 0, t: 19.0, msg: 'balance → systems   5,000회 재시뮬레이션: 중앙값 96s' },
  { a: 0, b: 4, t: 19.25, msg: 'systems → balance   확정' },
  { a: 2, b: 1, t: 19.5, msg: 'level → narrative   보스 등장 위치 = 3구간 끝' },
];
const CARD = { x: 760, y: 398, w: 196, h: 300, gap: 15 };
function cardPos(k, t) {
  const x = CARD.x + k * (CARD.w + CARD.gap), y = CARD.y;
  const p = seg(t, 16 + k * 0.25, 16.55 + k * 0.25, E.outBack);
  // 21.25 부터 GDD 한 장으로 빨려 들어간다
  const m = seg(t, 21.2 + k * 0.03, 21.6 + k * 0.03, E.inOutCubic);
  return { x: lerp(lerp(1900, x, p), 1180, m), y: lerp(lerp(1150, y, p), 470, m), rot: lerp(0.5, 0, p) + m * (k - 2) * 0.05, s: lerp(1, 0.4, m), a: p > 0 ? 1 - m : 0, p };
}
function planLeft(t, idx, title, sub, color, rows) {
  const p = seg(t, idx.t0, idx.t0 + 0.6);
  maskUp(idx.no, 116, 330, p, { size: 240, w: 800, stroke: 2.5, strokeColor: color, color, track: -8 });
  maskUp(title, 120, 468, seg(t, idx.t0 + 0.1, idx.t0 + 0.7), { size: 118, w: 800, color: C.ink, track: -3 });
  withA(seg(t, idx.t0 + 0.3, idx.t0 + 0.8), () => txt(sub, 124, 522, { mono: true, size: 17, w: 600, color: C.dim, track: 2 }));
  return p;
}
function scenePlan(t) {
  planLeft(t, { no: '01', t0: 14.0 }, '기획', 'PLAN · 지속형 에이전트 협업 · 6명', C.violet);
  // 에이전트 상태 목록
  PLAN_ROWS.forEach((r, i) => {
    const y = 600 + i * 46, a = seg(t, 14.4 + i * 0.07, 14.8 + i * 0.07); if (a <= 0) return;
    withA(a, () => {
      const working = t >= r.start && t < r.done, done = t >= r.done;
      const col = done ? C.green : working ? C.violet : C.mute;
      if (working) glowDot(132, y - 6, 20, C.violet, 0.6 + 0.4 * Math.sin(t * 12 + i));
      circle(132, y - 6, 6, col);
      if (done) { const dp = seg(t, r.done, r.done + 0.25, E.outBack); at(132, y - 6, dp, 0, () => { ctx.strokeStyle = '#05060A'; ctx.lineWidth = 2.4; ctx.beginPath(); ctx.moveTo(-3, 0); ctx.lineTo(-1, 2.5); ctx.lineTo(3.5, -2.5); ctx.stroke(); }); }
      txt(r.name, 156, y, { size: 21, w: 600, color: done ? C.ink : C.dim });
      txt(done ? '완료' : working ? '작업 중' : '대기', 470, y, { mono: true, size: 14, w: 600, color: col });
      chip(640, y - 7, r.model, { size: 12, h: 22, padX: 9, color: MODEL_COLOR[r.model], fill: hexA(MODEL_COLOR[r.model], 0.12), align: 'right' });
    });
  });
  // 컨셉 카드
  const cp = seg(t, 14.3, 14.9, E.outExpo), cm = seg(t, 21.2, 21.6, E.inOutCubic);
  withA(cp * (1 - cm), () => {
    const x = 760, y = lerp(170, 140, cp);
    panel(x, y, 1040, 232, { fill: 'rgba(157,123,255,0.07)', stroke: hexA(C.violet, 0.45) });
    txt('01_director_concept.md', x + 30, y + 40, { mono: true, size: 15, w: 500, color: C.violet });
    staggerText('코인 러너', x + 30, y + 104, t, 14.5, { size: 50, w: 800, color: C.ink, per: 0.05 });
    withA(seg(t, 14.8, 15.3), () => {
      txt('무너지는 금고에서 코인을 모으며 탈출하는 2D 러너', x + 32, y + 146, { size: 20, w: 500, color: C.dim });
      txt('핵심 재미 · 아슬아슬하게 피하며 줍는 긴장감', x + 32, y + 184, { size: 18, w: 600, color: C.ink });
    });
    // 코어 루프
    const steps = ['달린다', '피한다', '모은다', '탈출'];
    const lx = x + 560, ly = y + 112;
    steps.forEach((s, k) => {
      const p = seg(t, 15.0 + k * 0.15, 15.4 + k * 0.15, E.outBack); if (p <= 0) return;
      const nx = lx + k * 128;
      at(nx, ly, p, 0, () => { circle(0, 0, 30, '#12101E', C.violet, 2); txt(String(k + 1), 0, 7, { size: 20, w: 800, color: C.violet, align: 'center' }); });
      txt(s, nx, ly + 58, { size: 17, w: 700, color: C.ink, align: 'center', alpha: p });
      if (k < 3) line(nx + 36, ly, nx + 92, ly, hexA(C.violet, 0.6), 2, p);
    });
    const loopP = seg(t, 15.6, 16.0);
    if (loopP > 0) {
      ctx.save(); ctx.strokeStyle = hexA(C.violet, 0.5); ctx.lineWidth = 2; ctx.setLineDash([6, 6]);
      ctx.beginPath(); ctx.moveTo(lx + 384, ly + 30); ctx.bezierCurveTo(lx + 384, ly + 96, lx, ly + 96, lx, ly + 30); ctx.globalAlpha = loopP; ctx.stroke(); ctx.restore();
      const u = ((t - 15.6) / 2) % 1; const px = u < 0.75 ? lerp(lx, lx + 384, u / 0.75) : lerp(lx + 384, lx, (u - 0.75) / 0.25);
      glowDot(px, u < 0.75 ? ly : ly + 60 * Math.sin(Math.PI * (u - 0.75) / 0.25), 22, C.lime, loopP);
    }
  });
  // 문서 카드 다섯 장
  const CARDS = [
    { role: 'systems', title: '밸런스 테이블', draw: cardSystems }, { role: 'narrative', title: '대사 스크립트', draw: cardNarrative },
    { role: 'level', title: '레벨 1-1', draw: cardLevel }, { role: 'ux', title: 'HUD · 화면 흐름', draw: cardUX },
    { role: 'balance', title: '시뮬레이션', draw: cardBalance },
  ];
  CARDS.forEach((c, k) => {
    const q = cardPos(k, t); if (q.a <= 0) return;
    withA(q.a, () => at(q.x + CARD.w / 2, q.y + CARD.h / 2, q.s, q.rot, () => {
      const x = -CARD.w / 2, y = -CARD.h / 2;
      const hot = PACKETS.some(pk => pk.b === k && t >= pk.t + 0.33 && t < pk.t + 0.6);
      panel(x, y, CARD.w, CARD.h, { fill: '#0C0E17', stroke: hot ? C.violet : 'rgba(255,255,255,0.12)', lw: hot ? 2 : 1.2, glow: hot ? 30 : 0, glowColor: C.violet });
      txt(c.role, x + 16, y + 30, { mono: true, size: 13, w: 600, color: C.violet });
      txt(c.title, x + 16, y + 60, { size: 19, w: 800, color: C.ink });
      line(x + 16, y + 76, x + CARD.w - 16, y + 76, 'rgba(255,255,255,0.08)', 1);
      c.draw(x + 16, y + 92, CARD.w - 32, CARD.h - 108, t);
    }));
  });
  // 메시지 패킷
  PACKETS.forEach(pk => {
    const u = inv(pk.t, pk.t + 0.34, t); if (u <= 0 || u >= 1) return;
    const A = cardPos(pk.a, t), B = cardPos(pk.b, t);
    const ax = A.x + CARD.w / 2, bx = B.x + CARD.w / 2, ay = CARD.y - 6, by = CARD.y - 6;
    const mx = (ax + bx) / 2, my = CARD.y - 90 - Math.abs(bx - ax) * 0.12;
    const e = E.inOutCubic(u);
    for (let k = 0; k < 8; k++) {
      const uu = clamp(e - k * 0.03); const px = (1 - uu) * (1 - uu) * ax + 2 * (1 - uu) * uu * mx + uu * uu * bx, py = (1 - uu) * (1 - uu) * ay + 2 * (1 - uu) * uu * my + uu * uu * by;
      glowDot(px, py, 26 - k * 2.5, k === 0 ? '#ffffff' : C.violet, 1 - k / 8);
    }
  });
  // 메시지 기록
  withA(seg(t, 17.6, 18.0) * (1 - cm), () => {
    panel(760, 724, 1040, 176, { fill: 'rgba(255,255,255,0.025)' });
    txt('SendMessage', 786, 756, { mono: true, size: 14, w: 700, color: C.violet, track: 2 });
    const shown = PACKETS.filter(pk => t >= pk.t);
    shown.slice(-4).forEach((pk, i, arr) => {
      const a = seg(t, pk.t, pk.t + 0.2);
      txt(pk.msg, 786, 792 + i * 28, { mono: true, size: 15, w: 500, color: i === arr.length - 1 ? C.ink : C.dim, alpha: a });
    });
  });
  // 통합 리뷰: 불일치 발견 → 해결
  const rv = seg(t, 20.5, 20.7) * (1 - seg(t, 21.2, 21.3));
  if (rv > 0) {
    const A = cardPos(1, t), B = cardPos(2, t);
    const ax = A.x + CARD.w / 2, bx = B.x + CARD.w / 2, y = CARD.y + CARD.h + 14;
    const ok = t >= 21.0, col = ok ? C.green : C.red;
    withA(rv, () => {
      ctx.save(); ctx.strokeStyle = col; ctx.lineWidth = 3; ctx.setLineDash(ok ? [] : [8, 6]);
      ctx.beginPath(); ctx.moveTo(ax, y); ctx.lineTo(ax, y + 16); ctx.lineTo(bx, y + 16); ctx.lineTo(bx, y); ctx.stroke(); ctx.restore();
      const s = seg(t, ok ? 21.0 : 20.5, (ok ? 21.0 : 20.5) + 0.25, E.outBack);
      at((ax + bx) / 2, y + 16, s, 0, () => chip(0, 0, ok ? '✓ director · 해결' : '✕ 장소 불일치: 보스방', { align: 'center', color: '#05060A', fill: col, size: 15, w: 700, h: 32 }));
    });
  }
  // GDD 로 묶이고 동결 도장
  const gp = seg(t, 21.35, 21.65, E.outBack);
  if (gp > 0) {
    at(1180 + 98, 620, gp, -0.04, () => {
      panel(-190, -230, 380, 460, { fill: '#0E0C1A', stroke: hexA(C.violet, 0.7), lw: 2, glow: 40, glowColor: C.violet });
      txt('GDD.md', -160, -180, { size: 34, w: 800, color: C.ink });
      for (let k = 0; k < 9; k++) { ctx.fillStyle = k % 3 === 0 ? hexA(C.violet, 0.7) : 'rgba(255,255,255,0.16)'; ctx.fillRect(-160, -140 + k * 36, k % 3 === 0 ? 200 : 300 - (k * 37) % 90, 10); }
    });
    const sp = seg(t, 21.25, 21.42, E.inExpo);
    const stampS = lerp(2.4, 1, sp);
    withA(clamp(sp * 2), () => at(1390, 470, stampS, -0.18, () => {
      ctx.save(); ctx.strokeStyle = C.violet; ctx.lineWidth = 6; rr(-150, -54, 300, 108, 12); ctx.stroke(); ctx.restore();
      txt('FREEZE', 0, 16, { size: 56, w: 800, color: C.violet, align: 'center', track: 6 });
      txt('shasum 01_* → freeze_01.sha', 0, 44, { mono: true, size: 12, w: 600, color: C.violet, align: 'center' });
    }));
  }
}
// ---- 카드 내용
function cardSystems(x, y, w, h, t) {
  const cols = ['id', 'hp', 'atk', 'spd'], cx = [0, 76, 116, 150];
  cols.forEach((c, i) => txt(c, x + cx[i], y + 16, { mono: true, size: 12, w: 600, color: C.dim }));
  const morph = seg(t, 19.0, 19.35);
  const rows = [['grunt', morph < 0.5 ? '120' : ' 90', '14', '180'], ['golem', '900', '40', ' 90'], ['debris', ' —', '25', ' —'], ['coin', ' —', ' —', ' —'], ['player', '100', ' —', '420']];
  rows.forEach((r, j) => {
    const yy = y + 46 + j * 30, a = seg(t, 16.5 + j * 0.06, 16.8 + j * 0.06);
    if (j === 0 && t >= 19.0 && t < 19.9) { ctx.fillStyle = hexA(C.amber, 0.25 * (1 - inv(19.3, 19.9, t))); ctx.fillRect(x - 6, yy - 18, w + 12, 26); }
    r.forEach((v, i) => txt(v, x + cx[i], yy, { mono: true, size: 14, w: i === 0 ? 600 : 500, color: j === 0 && i === 1 && t >= 19.0 ? C.amber : C.ink, alpha: a }));
  });
  withA(seg(t, 17.0, 17.4), () => txt('data/balance/*.csv', x, y + h - 4, { mono: true, size: 11, w: 500, color: C.mute }));
}
function cardNarrative(x, y, w, h, t) {
  const L = [['락키', '침입자를 확인했습니다.', 'neutral'], ['도비', '붕괴? 잠깐만!', 'surprise'], ['락키', '출구는 통로 끝에 하나.', 'neutral'], ['골렘', '(낮은 으르렁)', 'creature']];
  L.forEach(([sp, s, em], j) => {
    const a = seg(t, 16.7 + j * 0.12, 17.0 + j * 0.12); if (a <= 0) return;
    const yy = y + 18 + j * 50;
    withA(a, () => {
      txt(sp, x, yy, { size: 13, w: 800, color: j % 2 ? C.lime : C.violet });
      txt(em, x + w, yy, { mono: true, size: 10, w: 500, color: C.mute, align: 'right' });
      txt(s, x, yy + 22, { size: 15, w: 500, color: C.ink });
    });
  });
}
function cardLevel(x, y, w, h, t) {
  const p = seg(t, 16.9, 17.8, E.inOutCubic);
  const pts = [[0, 130], [40, 130], [60, 100], [92, 100], [110, 130], [150, 130], [164, 70]];
  ctx.save(); ctx.strokeStyle = C.ink; ctx.lineWidth = 2.5; ctx.beginPath();
  const n = Math.max(1, Math.floor(p * (pts.length - 1)) + 1);
  pts.slice(0, n + 1).forEach(([px, py], i) => (i ? ctx.lineTo(x + px, y + py) : ctx.moveTo(x + px, y + py)));
  ctx.stroke(); ctx.restore();
  [[20, 118], [48, 100], [76, 88], [128, 118], [140, 118]].forEach(([cx, cy], i) => { if (p > i / 5) circle(x + cx, y + cy, 4.5, C.gold); });
  [[70, 92], [120, 124]].forEach(([dx, dy]) => { if (p > 0.5) { line(x + dx - 5, y + dy - 5, x + dx + 5, y + dy + 5, C.red, 2.5); line(x + dx + 5, y + dy - 5, x + dx - 5, y + dy + 5, C.red, 2.5); } });
  withA(seg(t, 17.4, 17.8), () => {
    circle(x + 40, y + 60, 34, hexA(C.cyan, 0.12), hexA(C.cyan, 0.5), 1);
    txt('amb_vault', x + 40, y + 64, { mono: true, size: 10, w: 600, color: C.cyan, align: 'center' });
    txt('사운드 구역 3 · 프랍 4', x, y + h - 4, { mono: true, size: 11, w: 500, color: C.mute });
  });
}
function cardUX(x, y, w, h, t) {
  const a = seg(t, 17.1, 17.5);
  withA(a, () => {
    ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,0.4)'; ctx.lineWidth = 1.5; rr(x, y + 4, w, 104, 6); ctx.stroke(); ctx.restore();
    ctx.save(); ctx.setLineDash([4, 3]); ctx.strokeStyle = C.lime; rr(x + 8, y + 12, 58, 20, 3); ctx.stroke(); rr(x + w - 70, y + 12, 62, 20, 3); ctx.stroke(); rr(x + w / 2 - 34, y + 70, 68, 26, 13); ctx.stroke(); ctx.restore();
    txt('lbl_score', x + 12, y + 26, { mono: true, size: 9, w: 600, color: C.lime });
    txt('bar_hp', x + w - 64, y + 26, { mono: true, size: 9, w: 600, color: C.lime });
    txt('btn_start', x + w / 2, y + 87, { mono: true, size: 9, w: 600, color: C.lime, align: 'center' });
  });
  const f = ['scr_title', 'scr_game', 'scr_result'];
  f.forEach((s, i) => { const p = seg(t, 17.4 + i * 0.12, 17.7 + i * 0.12); withA(p, () => { chip(x, y + 138 + i * 30, s, { size: 11, h: 22, padX: 8, color: C.ink }); if (i < 2) txt('↓', x + 12, y + 156 + i * 30, { size: 12, w: 700, color: C.mute }); }); });
}
function cardBalance(x, y, w, h, t) {
  const shift = seg(t, 19.5, 19.95, E.inOutCubic);
  const mean = lerp(150, 96, shift);
  const bx = x, by = y + 118, n = 14, bw = w / n;
  // 목표 구간 60~120초 → 0~210초 축
  const X = s => bx + (s / 210) * w;
  ctx.fillStyle = hexA(C.green, 0.12); ctx.fillRect(X(60), y + 8, X(120) - X(60), 112);
  txt('목표 60–120s', X(60) + 3, y + 22, { mono: true, size: 9, w: 600, color: C.green });
  const grow = seg(t, 17.2, 17.9, E.outCubic);
  for (let i = 0; i < n; i++) {
    const s = (i + 0.5) * 210 / n; const v = Math.exp(-Math.pow((s - mean) / 28, 2));
    const hh = v * 92 * grow; const inb = s >= 60 && s <= 120;
    ctx.fillStyle = inb ? hexA(C.green, 0.85) : hexA(C.coral, 0.8); ctx.fillRect(bx + i * bw + 1, by - hh, bw - 2, hh);
  }
  line(bx, by, bx + w, by, 'rgba(255,255,255,0.3)', 1);
  const pass = shift > 0.5;
  withA(grow, () => {
    txt('클리어 시간 중앙값', x, by + 32, { size: 12, w: 600, color: C.dim });
    txt(`${Math.round(mean)}s`, x, by + 70, { size: 34, w: 800, color: pass ? C.green : C.coral });
    const cp = pass ? seg(t, 19.55, 19.8, E.outBack) : 1;
    at(x + w - 30, by + 58, cp, 0, () => chip(0, 0, pass ? 'PASS' : 'FAIL', { align: 'center', size: 13, w: 800, h: 26, color: '#05060A', fill: pass ? C.green : C.coral }));
  });
}
