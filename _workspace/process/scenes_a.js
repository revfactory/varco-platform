// ============================================================================
// 장면 A: 콜드 오픈 · 타이틀 · 전체 흐름 · 00 준비 · 01 기획
// 장면 안의 시각은 모두 장면 시작(S0) 기준 상대 시각으로 적는다.
// ============================================================================

// ------------------------------------------------------------------ 공용 조각
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
// 왼쪽 큰 단계 번호와 이름
function planLeft(t, no, t0, title, sub, color) {
  const p = seg(t, t0, t0 + 0.6);
  maskUp(no, 116, 330, p, { size: 240, w: 800, stroke: 2.5, strokeColor: color, color, track: -8 });
  maskUp(title, 120, 468, seg(t, t0 + 0.1, t0 + 0.7), { size: 118, w: 800, color: C.ink, track: -3 });
  withA(seg(t, t0 + 0.3, t0 + 0.8), () => txt(sub, 124, 522, { mono: true, size: 17, w: 600, color: C.dim, track: 2 }));
  return p;
}
function stepList(x, y, t, items, color, gap = 46) {
  items.forEach((it, i) => {
    const yy = y + i * gap, a = seg(t, it.show, it.show + 0.3); if (a <= 0) return;
    withA(a, () => {
      const done = t >= it.done;
      circle(x + 12, yy - 6, 11, done ? color : 'rgba(255,255,255,0.06)', done ? null : hexA(color, 0.6), 1.5);
      if (done) at(x + 12, yy - 6, seg(t, it.done, it.done + 0.25, E.outBack), 0, () => txt('✓', 0, 5, { size: 14, w: 800, color: '#05060A', align: 'center' }));
      else txt(String(i + 1), x + 12, yy - 1, { mono: true, size: 12, w: 700, color, align: 'center' });
      txt(it.s, x + 36, yy, { size: 21, w: 600, color: done ? C.ink : C.dim });
    });
  });
}
function drawNode(x, y, r, color, tag, p, o = {}) {
  if (p <= 0) return;
  const s = E.outBack(clamp(p));
  at(x, y, s, 0, () => {
    glowDot(0, 0, r * 2.4, color, 0.35 + (o.hot || 0) * 0.5);
    circle(0, 0, r, '#0B0D14', color, o.lw || 2.5);
    if (o.dash) { ctx.save(); ctx.setLineDash([4, 4]); circle(0, 0, r + 5, null, hexA(color, 0.5), 1.2); ctx.restore(); }
    if (o.inner) circle(0, 0, r - 7, null, hexA(color, 0.35), 1);
    txt(tag, 0, r * 0.18, { mono: true, size: o.tagSize || 15, w: 700, color, align: 'center' });
  });
  if (p < 1) { ctx.save(); ctx.globalAlpha = 0.6 * (1 - p); circle(x, y, r + p * 70, null, color, 2); ctx.restore(); }
}
function burst(cx, cy, t, t0, n, seed, colors, o = {}) {
  const d = t - t0; if (d < 0 || d > (o.life || 1.4)) return;
  const r = rng(seed), life = o.life || 1.4, sp = o.speed || 900;
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < n; i++) {
    const ang = r() * Math.PI * 2, v = sp * (0.3 + r() * 0.9), len = 6 + r() * 28;
    const k = 1 - Math.exp(-d * 3.2);
    const x = cx + Math.cos(ang) * v * k / 3.2, y = cy + Math.sin(ang) * v * k / 3.2 + d * d * 120 * (o.grav ? 1 : 0);
    ctx.globalAlpha = (1 - d / life) * (0.6 + r() * 0.4); ctx.strokeStyle = colors[i % colors.length]; ctx.lineWidth = 2 + r() * 2;
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
function drawCursor(x, y, s = 1) {
  at(x, y, s, 0, () => {
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, 34); ctx.lineTo(9, 26); ctx.lineTo(16, 40); ctx.lineTo(22, 37); ctx.lineTo(15, 23); ctx.lineTo(27, 23); ctx.closePath();
    ctx.fillStyle = '#fff'; ctx.fill(); ctx.strokeStyle = '#000'; ctx.lineWidth = 2; ctx.stroke();
  });
}
// 사람에게 묻는 대화상자(AskUserQuestion). 버튼 가운데 좌표를 돌려준다.
function modalLayout(cx, cy, w, h, buttons, rowY) {
  let x = cx - w / 2 + 40; const out = [];
  for (const b of buttons) { const bw = tw(b.s, 800, 22) + 56; out.push({ x: x + bw / 2, y: cy + rowY, w: bw }); x += bw + 14; }
  return out;
}
function askModal(t, o) {
  const { cx, cy, w, h, t0, t1 = 1e9, color = C.gold, head, title, sub, buttons, press = null, rowY = 70 } = o;
  const pin = seg(t, t0, t0 + 0.32, E.outBack), pout = seg(t, t1, t1 + 0.3, E.inCubic);
  if (pin <= 0 || pout >= 1) return;
  const vis = clamp(pin * 2) * (1 - pout);
  withA(vis * 0.6, () => { ctx.fillStyle = '#000'; ctx.fillRect(-60, -60, W + 120, H + 120); });
  const L = modalLayout(0, 0, w, h, buttons, rowY);
  at(cx, cy, lerp(0.86, 1, pin) * (1 - pout * 0.1), 0, () => withA(vis, () => {
    panel(-w / 2, -h / 2, w, h, { fill: '#100F0A', stroke: color, lw: 2, glow: 50, glowColor: hexA(color, 0.45), r: 22 });
    txt(head, -w / 2 + 40, -h / 2 + 52, { mono: true, size: 14, w: 700, color, track: 2 });
    txt(title, -w / 2 + 40, -h / 2 + 106, { size: 36, w: 800, color: C.ink });
    if (sub) txt(sub, -w / 2 + 40, -h / 2 + 146, { size: 19, w: 500, color: C.dim });
    buttons.forEach((b, i) => {
      const q = L[i]; const pr = press && press.i === i ? seg(t, press.t, press.t + 0.08) * (1 - seg(t, press.t + 0.08, press.t + 0.22)) : 0;
      const chosen = press && press.i === i && t >= press.t + 0.1;
      at(q.x, q.y, 1 - pr * 0.08, 0, () => {
        rr(-q.w / 2, -32, q.w, 64, 14); ctx.fillStyle = b.primary ? color : 'rgba(255,255,255,0.08)'; ctx.fill();
        if (chosen) { ctx.save(); ctx.strokeStyle = '#fff'; ctx.lineWidth = 3; rr(-q.w / 2 - 5, -37, q.w + 10, 74, 17); ctx.stroke(); ctx.restore(); }
        txt(b.s, 0, 8, { size: 22, w: 800, color: b.primary ? '#05060A' : C.ink, align: 'center' });
      });
    });
    if (o.extra) o.extra();
  }));
  return L.map(q => ({ x: cx + q.x, y: cy + q.y }));
}
// 로고: VARCO / GAME STUDIO / 단계 색 막대
function drawLogotype(t, t0, cy, o = {}) {
  if (t < t0) return;
  const word = 'VARCO', size = o.size || 196, track = 28;
  const total = tw(word, 800, size, false, track) - track;
  let zoom = 1, za = 1, zx = W / 2, zy = cy;
  const oW = tw('O', 800, size, false, 0);
  const oX = W / 2 + total / 2 - oW / 2, oY = cy - size * 0.36;
  if (o.zoomFrom) { const zp = seg(t, o.zoomFrom, o.zoomTo, E.inExpo); zoom = lerp(1, 40, zp); za = 1 - seg(t, o.zoomTo - 0.12, o.zoomTo); zx = oX; zy = oY; }
  ctx.save(); ctx.translate(zx, zy); ctx.scale(zoom, zoom); ctx.translate(-zx, -zy); ctx.globalAlpha *= za;
  if (o.over) withA(seg(t, t0 + 0.2, t0 + 0.6), () => staggerText(o.over, W / 2, cy - size * 0.82, t, t0 + 0.2, { mono: true, size: 18, w: 700, color: C.lime, align: 'center', track: 10, per: 0.015, rise: 10 }));
  let x = W / 2 - total / 2;
  [...word].forEach((ch, i) => {
    const p = seg(t, t0 + i * 0.05, t0 + i * 0.05 + 0.5, E.outBackBig);
    const cw = tw(ch, 800, size, false, track);
    txt(ch, x, cy + (1 - p) * -160, { size, w: 800, color: C.ink, alpha: clamp(p * 2), track, blur: (1 - clamp(p)) * 12 });
    x += cw;
  });
  const g = seg(t, t0 + 0.25, t0 + 0.65);
  maskUp('GAME STUDIO', W / 2, cy + 104, g, { size: 56, w: 700, color: C.ink, align: 'center', track: 30 });
  const bw = 132, gap = 10, bx = W / 2 - (bw * 5 + gap * 4) / 2;
  PHASE.forEach((ph, k) => {
    const p = seg(t, t0 + 0.35 + k * 0.06, t0 + 0.75 + k * 0.06);
    ctx.fillStyle = ph.color; ctx.fillRect(bx + k * (bw + gap), cy + 146, bw * p, 6);
  });
  withA(seg(t, t0 + 0.5, t0 + 0.9), () => txt(o.tagline || 'HARNESS v2 · CLAUDE CODE · 기획부터 QA까지', W / 2, cy + 200, { mono: true, size: 18, w: 500, color: C.dim, align: 'center', track: 4 }));
  ctx.restore();
}

// ------------------------------------------------------------------ 에이전트 표
const AGENTS = {
  DIR: { name: '게임 디렉터', model: 'fable' }, SYS: { name: '시스템 기획', model: 'opus' }, NAR: { name: '시나리오', model: 'opus' },
  LVL: { name: '레벨 디자인', model: 'opus' }, UX: { name: 'UI/UX', model: 'sonnet' }, BAL: { name: '밸런스 분석', model: 'opus' },
  AST: { name: '에셋 프로듀서', model: 'sonnet' }, SND: { name: '사운드', model: 'sonnet' }, VOX: { name: '보이스', model: 'sonnet' },
  VIS: { name: '비주얼', model: 'sonnet' }, L10N: { name: '현지화', model: 'sonnet' }, AQA: { name: '에셋 QA', model: 'sonnet' },
  ENG: { name: '엔지니어', model: 'opus' }, GQA: { name: '게임 QA', model: 'opus' }, MKT: { name: '마케팅', model: 'sonnet' },
};
const MODEL_COLOR = { fable: C.gold, opus: C.opus, sonnet: C.sonnet };

function initScenesA() {
  addScene('cold_open', sceneColdOpen);
  addScene('title', sceneTitle);
  addScene('overview', sceneOverview);
  addScene('prep', scenePrep);
  addScene('plan', scenePlan);
}

// ------------------------------------------------------------------ 콜드 오픈
function sceneColdOpen(t) {
  const P = CUES.prompt, TT = CUES.typing, chars = [...P];
  const size = 56, y = 572;
  const fullW = tw(P, 600, size), x0 = Math.round(W / 2 - fullW / 2 + 30);
  const push = 1 + 0.035 * seg(t, 0.3, 3.45, E.inOutSine);
  ctx.save(); ctx.translate(W / 2, y); ctx.scale(push, push); ctx.translate(-W / 2, -y);
  withA(seg(t, 0.15, 0.7) * (1 - seg(t, 3.5, 3.7)), () => {
    txt('claude', x0 - 62, y - 92, { mono: true, size: 18, w: 700, color: C.lime });
    txt('~/varco-platform', x0 + 16, y - 92, { mono: true, size: 18, w: 500, color: C.dim });
  });
  const collapse = seg(t, 3.52, 3.7, E.inCubic);
  const lineGrow = seg(t, 3.68, 3.9, E.inOutCubic);
  let cx = x0, typedW = 0, lastT = -1, lastX = x0;
  ctx.save();
  if (collapse > 0) { ctx.translate(0, y - 16); ctx.scale(1, 1 - collapse); ctx.translate(0, -(y - 16)); }
  withA(seg(t, 0.2, 0.5), () => txt('❯', x0 - 62, y, { size, w: 700, color: C.lime, glow: 18 }));
  for (let i = 0; i < chars.length; i++) {
    const ch = chars[i]; const cw = tw(ch, 600, size);
    if (t >= TT[i]) {
      const p = seg(t, TT[i], TT[i] + 0.16, E.outBack);
      const col = mixHex(C.lime, C.ink, seg(t, TT[i], TT[i] + 0.35, E.lin));
      at(cx + cw / 2, y - size * 0.35, lerp(1.35, 1, p), 0, () => txt(ch, -cw / 2, size * 0.35, { size, w: 600, color: col, alpha: clamp(p * 2) }));
      const k = Math.exp(-(t - TT[i]) * 7);
      if (k > 0.02 && ch !== ' ') glowDot(cx + cw / 2, y - 14, 60, C.lime, 0.35 * k);
      typedW = cx + cw - x0; lastT = TT[i]; lastX = cx + cw;
    }
    cx += cw;
  }
  const typing = t < lastT + 0.18 && t < 3.0;
  const blink = Math.floor(t * 2.4) % 2 === 0;
  if ((typing || blink || t < 0.55) && t < 3.58) {
    const bx = lastT < 0 ? x0 : lastX + 6;
    ctx.fillStyle = C.lime; ctx.shadowColor = C.lime; ctx.shadowBlur = 16;
    ctx.fillRect(bx, y - size * 0.82, 24, size * 0.98); ctx.shadowBlur = 0;
  }
  ctx.restore();
  withA(seg(t, 3.05, 3.3) * (1 - seg(t, 3.45, 3.55)), () => chip(x0 + typedW + 50, y - 16, '↵ Enter', { color: C.bg, fill: C.lime, size: 16, w: 800 }));
  const flash = seg(t, 3.45, 3.5) * (1 - seg(t, 3.5, 3.75));
  if (flash > 0) glowDot(x0 + typedW / 2, y - 16, 900, C.lime, 0.5 * flash);
  if (lineGrow > 0) {
    const l = lerp(x0 - 62, 0, lineGrow), r = lerp(x0 + typedW, W, lineGrow);
    const th = lerp(3, 6, lineGrow) + seg(t, 3.88, 4.0, E.inExpo) * H;
    ctx.save(); ctx.shadowColor = C.lime; ctx.shadowBlur = 40;
    ctx.fillStyle = mixHex(C.lime, '#ffffff', seg(t, 3.8, 3.95)); ctx.fillRect(l, y - 16 - th / 2, r - l, th); ctx.restore();
  }
  ctx.restore();
}

// ------------------------------------------------------------------ 타이틀
function titleWords() {
  const T = S0('title');
  return [
    { s: '한 줄의 아이디어가', hi: '아이디어', t: T + 0.0, color: C.lime },
    { s: '게임이 되기까지', hi: '게임', t: T + 1.0, color: C.coral },
  ];
}
const TSTACK = [{ y: 600, size: 150, a: 1 }, { y: 424, size: 76, a: 0.45 }];
function titleWord(t, i, WD) {
  const wd = WD[i]; if (t < wd.t) return;
  let lv = 0; for (let j = i + 1; j < WD.length; j++) lv += seg(t, WD[j].t, WD[j].t + 0.4);
  const a = TSTACK[Math.floor(lv)], b = TSTACK[Math.min(1, Math.floor(lv) + 1)], f = lv - Math.floor(lv);
  const size = lerp(a.size, b.size, f) * (i === 1 ? 1.1 : 1), y = lerp(a.y, b.y, f), alpha = lerp(a.a, b.a, f);
  const p = seg(t, wd.t, wd.t + 0.32, E.outExpo);
  const sc = lerp(1.6, 1, p);
  const T = S0('title');
  const out = seg(t, T + 2.0 + i * 0.06, T + 2.4 + i * 0.06, E.inExpo);
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
  const u = seg(t, wd.t + 0.12, wd.t + 0.5) * (1 - lv * 0.7);
  if (u > 0 && out < 1) { ctx.fillStyle = wd.color; ctx.fillRect(x0 + pre, y + size * 0.14, tw(wd.hi, 800, size, false, -2) * u, Math.max(3, size * 0.045)); }
}
function sceneTitle(t) {
  const T = S0('title'), WD = titleWords();
  for (const wd of WD) {
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
  for (let i = 0; i < WD.length; i++) titleWord(t, i, WD);
  drawLogotype(t, T + 2.3, 560, { zoomFrom: T + 5.55, zoomTo: T + 6.0, over: 'THE MAKING OF COIN RUNNER', tagline: 'HARNESS v2 · CLAUDE CODE · VARCO API PLATFORM' });
  withA(seg(t, T + 3.2, T + 3.6) * (1 - seg(t, T + 5.3, T + 5.5)), () => staggerText('게임 한 편이 만들어지는 과정을 처음부터 끝까지 따라갑니다', W / 2, 850, t, T + 3.2, { size: 26, w: 600, color: C.ink, align: 'center', per: 0.012, rise: 12 }));
}

// ------------------------------------------------------------------ 전체 흐름
const OV = {
  cx: [300, 630, 960, 1290, 1620], y: 590, cw: 270, ch: 170,
  agents: [['DIR', 'SYS', 'NAR', 'LVL', 'UX', 'BAL'], ['AST'], ['SND', 'VOX', 'VIS', 'L10N', 'AQA'], ['ENG', 'GQA'], ['AQA', 'GQA', 'BAL', 'MKT', 'DIR']],
  mode: [['지속형 협업', 'SendMessage · 6명'], ['서브에이전트', 'Agent · 1명'], ['워크플로', 'Workflow · 제작 → 검증'], ['엔지니어 ⇄ QA', '지속형 한 쌍'], ['병렬 검사 → 판정', 'Agent × 4 → 디렉터']],
  gates: [{ k: 0, lt: 4.5, s: '확인 1 · 컨셉 승인' }, { k: 1, lt: 4.9, s: '확인 2 · 크레딧 승인' }],
  // 아이디어 점이 지나는 길: [상대 시각, x]
  path: [[5.5, 110], [5.9, 300], [6.25, 300], [6.55, 630], [6.9, 630], [7.1, 960], [7.3, 1290], [7.5, 1620], [7.72, 1810]],
};
function ovTokenX(l) {
  const P = OV.path; if (l <= P[0][0]) return null; if (l >= P[P.length - 1][0]) return null;
  for (let i = 1; i < P.length; i++) if (l <= P[i][0]) return lerp(P[i - 1][1], P[i][1], E.inOutCubic(inv(P[i - 1][0], P[i][0], l)));
  return null;
}
function sceneOverview(t) {
  const T = S0('overview'), l = t - T;
  const push = 1 + 0.03 * seg(l, 0, 8, E.inOutSine);
  maskUp('전체 흐름', 120, 196, seg(l, 0.05, 0.5), { size: 58, w: 800, color: C.ink });
  withA(seg(l, 0.2, 0.6), () => txt('5단계 · 에이전트 15명 · 사람 확인 2번', 124, 236, { mono: true, size: 16, w: 600, color: C.violet, track: 2 }));
  ctx.save(); ctx.translate(W / 2, OV.y); ctx.scale(push, push); ctx.translate(-W / 2, -OV.y);
  // 연결선
  const lp = seg(l, 0.2, 1.6, E.inOutCubic);
  line(110, OV.y, lerp(110, 1810, lp), OV.y, 'rgba(255,255,255,0.22)', 2);
  withA(seg(l, 0.2, 0.5), () => { circle(110, OV.y, 7, C.lime); txt('❯ 아이디어', 96, OV.y + 36, { mono: true, size: 13, w: 700, color: C.lime }); });
  // 카드
  PHASE.forEach((ph, k) => {
    const x = OV.cx[k], p = seg(l, 0.3 + k * 0.25, 0.75 + k * 0.25, E.outBack); if (p <= 0) return;
    const tok = ovTokenX(l), near = tok != null ? Math.max(0, 1 - Math.abs(tok - x) / 140) : 0;
    at(x, OV.y, p, 0, () => {
      panel(-OV.cw / 2, -OV.ch / 2, OV.cw, OV.ch, { fill: '#0B0C13', stroke: hexA(ph.color, 0.55 + near * 0.45), lw: 2, glow: 20 + near * 50, glowColor: hexA(ph.color, 0.35 + near * 0.4) });
      txt(ph.no, -OV.cw / 2 + 22, -12, { size: 64, w: 800, stroke: 2, strokeColor: ph.color, color: ph.color, track: -3 });
      txt(ph.name, -OV.cw / 2 + 24, 52, { size: 40, w: 800, color: C.ink });
      txt(ph.en, OV.cw / 2 - 22, -44, { mono: true, size: 13, w: 700, color: ph.color, align: 'right', track: 4 });
    });
    // 실행 방식
    withA(seg(l, 3.0 + k * 0.2, 3.4 + k * 0.2), () => {
      txt(OV.mode[k][0], x, OV.y + 150, { size: 22, w: 800, color: ph.color, align: 'center' });
      txt(OV.mode[k][1], x, OV.y + 180, { mono: true, size: 13, w: 600, color: C.dim, align: 'center' });
    });
  });
  // 에이전트 노드: 16분음표마다 하나씩
  let n = 0;
  OV.agents.forEach((row, k) => {
    const x = OV.cx[k], col = PHASE[k].color;
    row.forEach((tag, j) => {
      const r1 = j < 3 ? 0 : 1, inRow = r1 === 0 ? Math.min(3, row.length) : row.length - 3, jj = r1 === 0 ? j : j - 3;
      const nx = x + (jj - (inRow - 1) / 2) * 66, ny = OV.y - 138 - r1 * 62;
      const again = k === 4 && tag !== 'MKT';
      const pt = 1.5 + (again ? 15 : n) * BEAT / 4 + (again ? 0 : 0);
      const p = again ? seg(l, 2.6, 3.0, E.lin) : seg(l, pt, pt + 0.4, E.lin);
      drawNode(nx, ny, 24, col, tag, p * 2.5, { tagSize: tag.length > 3 ? 10 : 12, lw: 2, dash: again, hot: Math.exp(-Math.max(0, l - pt) * 5) });
      if (p > 0.3) circle(nx + 18, ny - 18, 5, MODEL_COLOR[AGENTS[tag].model], '#05060A', 2);
      if (!again) n++;
    });
  });
  withA(seg(l, 2.7, 3.1), () => txt('점선 = 앞 단계 담당이 다시 참여', OV.cx[4], OV.y - 268, { size: 13, w: 600, color: C.dim, align: 'center' }));
  // 사람 확인 배지
  OV.gates.forEach(g => {
    const x = OV.cx[g.k], p = seg(l, g.lt, g.lt + 0.35, E.outBackBig); if (p <= 0) return;
    const tok = ovTokenX(l), hot = tok != null && Math.abs(tok - x) < 6 ? 1 : 0;
    at(x, OV.y + OV.ch / 2, p, 0, () => {
      if (hot) glowDot(0, 0, 90, C.gold, 0.8);
      chip(0, 0, g.s, { align: 'center', size: 16, w: 800, h: 34, mono: false, color: '#05060A', fill: C.gold });
    });
    if (p < 1) shockRing(x, OV.y + OV.ch / 2, t, T + g.lt, C.gold, { r: 160, r0: 20, lw: 4, life: 0.5 });
  });
  // 아이디어 점
  const tx = ovTokenX(l);
  if (tx != null) {
    for (let k = 0; k < 10; k++) { const u = ovTokenX(l - k * 0.018); if (u != null) glowDot(u, OV.y, 40 - k * 3, k ? C.lime : '#ffffff', 1 - k / 10); }
  }
  ctx.restore();
}

// ------------------------------------------------------------------ 00 준비
const PREP_TERM = [
  [0.2, '❯ 무너지는 금고에서 코인을 모아 탈출하는 웹게임 만들어줘', C.dim],
  [0.4, '⏺ Skill(varco-game-studio)', C.lime],
  [0.85, '  ⎿  ls _workspace games  →  coin-runner 없음 · 처음 실행', C.ink],
  [1.3, '  ⎿  OPENAPI_KEY: set (값은 출력하지 않음)  →  varco_mode: live', C.ink],
  [1.75, '  ⎿  엔진 web · 원문 ko · 번역 en, ja · 음성 korean', C.ink],
  [2.2, '⏺ Write(_workspace/coin-runner/run_meta.json)', C.lime],
  [4.4, '⏺ Write(_workspace/coin-runner/00_input.md)', C.lime],
];
const RUN_META = ['{', '  "slug": "coin-runner",', '  "engine": "web",', '  "varco_mode": "live",', '  "source_lang": "ko",', '  "target_langs": ["en", "ja"],', '  "voice_langs": ["korean"],', '  "gates": "confirm",', '  "phases_done": []', '}'];
function scenePrep(t) {
  const T = S0('prep'), l = t - T;
  planLeft(t, '00', T, '준비', 'PREP · 리더(메인 에이전트)가 직접', C.paper);
  stepList(120, 612, t, [
    { s: '기존 작업 확인', show: T + 0.3, done: T + 0.95 }, { s: 'VARCO 키 확인', show: T + 0.45, done: T + 1.4 },
    { s: '실행 설정 기록', show: T + 0.6, done: T + 4.0 }, { s: '요청 원문 저장', show: T + 0.75, done: T + 4.6 },
  ], C.paper);
  // 터미널
  const tp = seg(l, 0.05, 0.4, E.outExpo);
  withA(tp, () => {
    const x = 760, y = 140, w = 1040, h = 330;
    panel(x, y, w, h, { fill: '#0A0C11', stroke: 'rgba(255,255,255,0.14)' });
    [C.coral, C.amber, C.green].forEach((c, i) => circle(x + 26 + i * 22, y + 24, 6, c));
    txt('claude — ~/varco-platform', x + w / 2, y + 30, { mono: true, size: 13, w: 600, color: C.dim, align: 'center' });
    PREP_TERM.forEach(([lt, s, col], i) => {
      const shown = typed(s, l, lt, 150); if (!shown) return;
      const yy = y + 84 + i * 36;
      txt(shown, x + 30, yy, { mono: true, size: 16, w: s.startsWith('⏺') ? 700 : 500, color: col });
      if (shown.length < s.length) { ctx.fillStyle = C.lime; ctx.fillRect(x + 32 + tw(shown, 500, 16, true), yy - 15, 9, 18); }
    });
  });
  // run_meta.json
  withA(seg(l, 2.25, 2.6), () => {
    const x = 760, y = 500, w = 620, h = 400;
    panel(x, y, w, h, { fill: '#0B0C12', stroke: hexA(C.paper, 0.3) });
    txt('run_meta.json', x + 24, y + 38, { mono: true, size: 14, w: 700, color: C.paper });
    chip(x + w - 20, y + 32, '계약서 2절', { size: 12, h: 24, color: C.dim, align: 'right' });
    let chars = Math.floor((l - 2.4) * 120);
    RUN_META.forEach((s, i) => {
      if (chars <= 0) return; const part = s.slice(0, Math.min(s.length, chars)); chars -= s.length;
      const yy = y + 86 + i * 30;
      if (/varco_mode|target_langs/.test(s) && l > 4.0) { ctx.fillStyle = hexA(C.lime, 0.1); ctx.fillRect(x + 2, yy - 21, w - 4, 29); }
      codeLine(part, x + 28, yy, { size: 16 });
    });
  });
  // 폴더
  withA(seg(l, 2.4, 2.75), () => {
    const x = 1410, y = 500, w = 390, h = 400;
    panel(x, y, w, h, { fill: 'rgba(255,255,255,0.03)', stroke: 'rgba(255,255,255,0.12)' });
    txt('작업 폴더', x + 24, y + 38, { size: 16, w: 700, color: C.dim });
    const rows = [[0, '_workspace/', C.ink, 0], [0.1, '└─ coin-runner/', C.ink, 0], [4.3, '   ├─ run_meta.json', C.lime, 1], [4.6, '   └─ 00_input.md', C.lime, 1], [0.2, 'games/', C.ink, 0], [0.3, '└─ (아직 비어 있음)', C.mute, 0]];
    rows.forEach(([lt, s, col, isNew], i) => {
      const a = seg(l, 2.4 + (isNew ? lt - 2.4 : lt), 2.6 + (isNew ? lt - 2.4 : lt)); if (a <= 0) return;
      const yy = y + 92 + i * 40 + (i >= 4 ? 30 : 0);
      withA(a, () => {
        txt(s, x + 28 + (1 - a) * 20, yy, { mono: true, size: 16, w: 600, color: col });
        if (isNew) chip(x + w - 24, yy - 6, 'new', { size: 11, h: 20, padX: 7, color: '#05060A', fill: C.lime, align: 'right' });
      });
    });
  });
  const dp = seg(l, 5.0, 5.3, E.outBack);
  if (dp > 0) at(124, 820, dp, 0, () => chip(0, 0, '✓ 준비 완료 · 1단계로', { size: 16, w: 800, h: 34, color: '#05060A', fill: C.paper }));
}

// ------------------------------------------------------------------ 01 기획
const PLAN_TASKS = [
  { id: 'T0', name: '컨셉', who: 'director', model: 'fable', start: 0.2, done: 2.0 },
  { id: 'T1', name: '시스템 명세 · 밸런스 표', who: 'systems', model: 'opus', start: 6.2, done: 11.2 },
  { id: 'T2', name: '세계관 · 캐릭터 · 대사', who: 'narrative', model: 'opus', start: 6.3, done: 9.8 },
  { id: 'T3', name: '레벨 설계', who: 'level', model: 'opus', start: 6.9, done: 15.0 },
  { id: 'T4', name: '화면 흐름 · HUD', who: 'ux', model: 'sonnet', start: 6.7, done: 10.2 },
  { id: 'T5', name: '밸런스 시뮬레이션', who: 'balance', model: 'opus', start: 7.2, done: 10.7 },
  { id: 'T6', name: '통합 리뷰', who: 'director', model: 'fable', start: 13.8, done: 15.0 },
  { id: 'T7', name: '통합 GDD', who: 'director', model: 'fable', start: 15.2, done: 16.1 },
];
const PLAN_PACKETS = [
  { a: 0, b: 4, lt: 8.0, msg: 'systems → balance   밸런스 CSV 준비됨: enemies.csv 외 3개' },
  { a: 4, b: 0, lt: 8.5, msg: 'balance → systems   grunt.hp 120 → 90 권장 (클리어 중앙값 150s)' },
  { a: 1, b: 2, lt: 9.0, msg: 'narrative → level   장면 목록 2개 전달 (intro, boss_appear)' },
  { a: 0, b: 3, lt: 9.5, msg: 'systems → ux        HUD 표시 수치: score · coins · hp' },
  { a: 0, b: 4, lt: 10.0, msg: 'systems → balance   반영 완료 · 재시뮬레이션 요청' },
  { a: 4, b: 0, lt: 10.5, msg: 'balance → systems   5,000회 재시뮬레이션: 중앙값 96s · PASS' },
  { a: 2, b: 1, lt: 11.0, msg: 'level → narrative   보스 등장 위치 = 3구간 끝' },
];
const CARD = { x: 760, y: 398, w: 196, h: 300, gap: 15 };
function cardPos(k, l) {
  const x = CARD.x + k * (CARD.w + CARD.gap), y = CARD.y;
  const raw = inv(6.0 + k * 0.25, 6.6 + k * 0.25, l), p = raw > 0 ? E.outBack(raw) : 0;
  const m = seg(l, 15.6 + k * 0.03, 16.0 + k * 0.03, E.inOutCubic);
  // 컨셉 카드에서 태어나 제자리로 간다 → GDD 로 빨려 들어간다
  return { x: lerp(lerp(1180, x, p), 1010, m), y: lerp(lerp(220, y, p), 330, m), rot: m * (k - 2) * 0.05, s: lerp(lerp(0.2, 1, clamp(p)), 0.4, m), a: raw > 0 ? 1 - m : 0, p: raw > 0 ? p : 0 };
}
function scenePlan(t) {
  const T = S0('plan'), l = t - T;
  planLeft(t, '01', T, '기획', 'PLAN · 지속형 에이전트 협업 · 6명', C.violet);
  // 작업 목록
  withA(seg(l, 0.3, 0.7), () => txt('공유 작업 목록', 124, 586, { mono: true, size: 13, w: 700, color: C.violet, track: 3 }));
  PLAN_TASKS.forEach((r, i) => {
    const y = 624 + i * 38, a = i === 0 ? seg(l, 0.3, 0.6) : seg(l, 5.8 + i * 0.06, 6.2 + i * 0.06); if (a <= 0) return;
    withA(a, () => {
      const working = l >= r.start && l < r.done, done = l >= r.done;
      const col = done ? C.green : working ? C.violet : C.mute;
      if (working) glowDot(132, y - 6, 20, C.violet, 0.6 + 0.4 * Math.sin(t * 12 + i));
      circle(132, y - 6, 6, col);
      if (done) at(132, y - 6, seg(l, r.done, r.done + 0.25, E.outBack), 0, () => { ctx.strokeStyle = '#05060A'; ctx.lineWidth = 2.4; ctx.beginPath(); ctx.moveTo(-3, 0); ctx.lineTo(-1, 2.5); ctx.lineTo(3.5, -2.5); ctx.stroke(); });
      txt(r.id, 152, y, { mono: true, size: 13, w: 700, color: C.mute });
      txt(r.name, 188, y, { size: 19, w: 600, color: done ? C.ink : working ? C.ink : C.dim });
      txt(r.who, 452, y, { mono: true, size: 13, w: 500, color: C.dim });
      chip(648, y - 6, r.model, { size: 11, h: 20, padX: 8, color: MODEL_COLOR[r.model], fill: hexA(MODEL_COLOR[r.model], 0.12), align: 'right' });
    });
  });
  // 컨셉 카드
  const cp = seg(l, 0.3, 0.9, E.outExpo), cm = seg(l, 15.6, 16.0, E.inOutCubic);
  withA(cp * (1 - cm), () => {
    const x = 760, y = lerp(170, 140, cp);
    panel(x, y, 1040, 232, { fill: 'rgba(157,123,255,0.07)', stroke: hexA(C.violet, 0.45) });
    txt('01_director_concept.md', x + 30, y + 40, { mono: true, size: 15, w: 500, color: C.violet });
    chip(x + 1010, y + 34, 'game-director · fable', { size: 12, h: 24, color: C.gold, fill: hexA(C.gold, 0.12), align: 'right' });
    staggerText('코인 러너', x + 30, y + 104, t, T + 0.5, { size: 50, w: 800, color: C.ink, per: 0.05 });
    withA(seg(l, 0.8, 1.3), () => {
      txt('무너지는 금고에서 코인을 모으며 탈출하는 2D 러너', x + 32, y + 146, { size: 20, w: 500, color: C.dim });
      txt('핵심 재미 · 아슬아슬하게 피하며 줍는 긴장감', x + 32, y + 184, { size: 18, w: 600, color: C.ink });
    });
    const steps = ['달린다', '피한다', '모은다', '탈출'];
    const lx = x + 560, ly = y + 112;
    steps.forEach((s, k) => {
      const p = seg(l, 1.0 + k * 0.15, 1.4 + k * 0.15, E.outBack); if (p <= 0) return;
      const nx = lx + k * 128;
      at(nx, ly, p, 0, () => { circle(0, 0, 30, '#12101E', C.violet, 2); txt(String(k + 1), 0, 7, { size: 20, w: 800, color: C.violet, align: 'center' }); });
      txt(s, nx, ly + 58, { size: 17, w: 700, color: C.ink, align: 'center', alpha: p });
      if (k < 3) line(nx + 36, ly, nx + 92, ly, hexA(C.violet, 0.6), 2, p);
    });
    const loopP = seg(l, 1.6, 2.0);
    if (loopP > 0) {
      ctx.save(); ctx.strokeStyle = hexA(C.violet, 0.5); ctx.lineWidth = 2; ctx.setLineDash([6, 6]);
      ctx.beginPath(); ctx.moveTo(lx + 384, ly + 30); ctx.bezierCurveTo(lx + 384, ly + 96, lx, ly + 96, lx, ly + 30); ctx.globalAlpha = loopP; ctx.stroke(); ctx.restore();
      const u = ((l - 1.6) / 2) % 1; const px = u < 0.75 ? lerp(lx, lx + 384, u / 0.75) : lerp(lx + 384, lx, (u - 0.75) / 0.25);
      glowDot(px, u < 0.75 ? ly : ly + 60 * Math.sin(Math.PI * (u - 0.75) / 0.25), 22, C.lime, loopP);
    }
  });
  // 핵심 결정 세 가지
  const kd = seg(l, 2.0, 2.4) * (1 - seg(l, 5.4, 5.8));
  withA(kd, () => {
    const x = 760, y = 398;
    panel(x, y, 1040, 300, { fill: 'rgba(255,255,255,0.03)', stroke: hexA(C.violet, 0.3) });
    txt('핵심 결정 세 가지', x + 30, y + 50, { size: 24, w: 800, color: C.ink });
    txt('director → 리더', x + 1010, y + 50, { mono: true, size: 13, w: 600, color: C.dim, align: 'right' });
    ['한 판 2분, 웹 브라우저에서 바로 실행', '무너지는 통로를 피하며 코인을 줍는 긴장감이 핵심 재미', '대사는 한국어 음성으로, 문자열은 영어·일본어로 번역'].forEach((s, i) => {
      const p = seg(l, 2.2 + i * 0.3, 2.5 + i * 0.3, E.outCubic); if (p <= 0) return;
      const yy = y + 118 + i * 60;
      withA(p, () => {
        circle(x + 48, yy - 8, 16, C.violet); txt(String(i + 1), x + 48, yy - 2, { size: 17, w: 800, color: '#05060A', align: 'center' });
        txt(s, x + 82 + (1 - p) * 30, yy, { size: 23, w: 600, color: C.ink });
      });
    });
  });
  // 사람 확인 ①
  const btns = askModal(t, {
    cx: 1280, cy: 548, w: 800, h: 300, t0: T + 3.2, t1: T + 5.3, head: 'AskUserQuestion · 사람 확인 1/2',
    title: '컨셉을 이대로 진행할까요?', sub: '코인 러너 · 핵심 결정 세 가지를 확인해 주세요',
    buttons: [{ s: '승인', primary: true }, { s: '고칠 점 알려 주기' }, { s: '다른 방향으로 다시' }], press: { i: 0, t: T + 4.45 }, rowY: 78,
  });
  if (btns && l < 5.3) {
    const cu = seg(l, 3.8, 4.35, E.outCubic), b = btns[0];
    withA(seg(l, 3.5, 3.7), () => drawCursor(lerp(1620, b.x + 10, cu), lerp(820, b.y + 8, cu), 1 - seg(l, 4.45, 4.5) * 0.15 + seg(l, 4.5, 4.62) * 0.15));
    const ap = seg(l, 4.6, 4.85, E.outBackBig);
    if (ap > 0) { shockRing(b.x, b.y, t, T + 4.6, C.gold, { r: 220, r0: 30, lw: 5, life: 0.6 }); }
  }
  // 문서 카드 다섯 장
  const CARDS = [
    { role: 'systems', title: '밸런스 테이블', draw: cardSystems }, { role: 'narrative', title: '대사 스크립트', draw: cardNarrative },
    { role: 'level', title: '레벨 1-1', draw: cardLevel }, { role: 'ux', title: 'HUD · 화면 흐름', draw: cardUX },
    { role: 'balance', title: '시뮬레이션', draw: cardBalance },
  ];
  withA(seg(l, 5.9, 6.2) * (1 - cm), () => txt('Agent × 5 · 한 메시지에서 동시에 실행', 1800, 388, { mono: true, size: 13, w: 700, color: C.violet, align: 'right', track: 1 }));
  CARDS.forEach((c, k) => {
    const q = cardPos(k, l); if (q.a <= 0) return;
    if (q.p < 1 && q.p > 0) { const e = clamp(q.p); for (let j = 0; j < 6; j++) glowDot(lerp(1180, q.x + CARD.w / 2, clamp(e - j * 0.05)), lerp(256, q.y + CARD.h / 2, clamp(e - j * 0.05)), 26 - j * 3, C.violet, (1 - j / 6) * (1 - e)); }
    withA(q.a, () => at(q.x + CARD.w / 2, q.y + CARD.h / 2, q.s, q.rot, () => {
      const x = -CARD.w / 2, y = -CARD.h / 2;
      const hot = PLAN_PACKETS.some(pk => pk.b === k && l >= pk.lt + 0.33 && l < pk.lt + 0.6);
      panel(x, y, CARD.w, CARD.h, { fill: '#0C0E17', stroke: hot ? C.violet : 'rgba(255,255,255,0.12)', lw: hot ? 2 : 1.2, glow: hot ? 30 : 0, glowColor: C.violet });
      txt(c.role, x + 16, y + 30, { mono: true, size: 13, w: 600, color: C.violet });
      txt(c.title, x + 16, y + 60, { size: 19, w: 800, color: C.ink });
      line(x + 16, y + 76, x + CARD.w - 16, y + 76, 'rgba(255,255,255,0.08)', 1);
      c.draw(x + 16, y + 92, CARD.w - 32, CARD.h - 108, l);
    }));
  });
  // 메시지 패킷
  PLAN_PACKETS.forEach(pk => {
    const u = inv(pk.lt, pk.lt + 0.34, l); if (u <= 0 || u >= 1) return;
    const A = cardPos(pk.a, l), B = cardPos(pk.b, l);
    const ax = A.x + CARD.w / 2, bx = B.x + CARD.w / 2, ay = CARD.y - 6, by = CARD.y - 6;
    const mx = (ax + bx) / 2, my = CARD.y - 90 - Math.abs(bx - ax) * 0.12;
    const e = E.inOutCubic(u);
    for (let k = 0; k < 8; k++) {
      const uu = clamp(e - k * 0.03); const px = (1 - uu) * (1 - uu) * ax + 2 * (1 - uu) * uu * mx + uu * uu * bx, py = (1 - uu) * (1 - uu) * ay + 2 * (1 - uu) * uu * my + uu * uu * by;
      glowDot(px, py, 26 - k * 2.5, k === 0 ? '#ffffff' : C.violet, 1 - k / 8);
    }
  });
  // 메시지 기록
  withA(seg(l, 7.6, 8.0) * (1 - cm), () => {
    panel(760, 724, 1040, 176, { fill: 'rgba(255,255,255,0.025)' });
    txt('SendMessage', 786, 756, { mono: true, size: 14, w: 700, color: C.violet, track: 2 });
    txt('결정 사항은 반드시 파일에 남긴다', 1776, 756, { size: 13, w: 600, color: C.dim, align: 'right' });
    const shown = PLAN_PACKETS.filter(pk => l >= pk.lt);
    shown.slice(-4).forEach((pk, i, arr) => txt(pk.msg, 786, 792 + i * 28, { mono: true, size: 15, w: 500, color: i === arr.length - 1 ? C.ink : C.dim, alpha: seg(l, pk.lt, pk.lt + 0.2) }));
  });
  // 통합 리뷰: 불일치 발견 → 결정
  const rv = seg(l, 14.0, 14.2) * (1 - seg(l, 15.5, 15.6));
  if (rv > 0) {
    const A = cardPos(1, l), B = cardPos(2, l);
    const ax = A.x + CARD.w / 2, bx = B.x + CARD.w / 2, y = CARD.y + CARD.h + 14;
    const ok = l >= 15.0, col = ok ? C.green : C.red;
    withA(rv, () => {
      ctx.save(); ctx.strokeStyle = col; ctx.lineWidth = 3; ctx.setLineDash(ok ? [] : [8, 6]);
      ctx.beginPath(); ctx.moveTo(ax, y); ctx.lineTo(ax, y + 16); ctx.lineTo(bx, y + 16); ctx.lineTo(bx, y); ctx.stroke(); ctx.restore();
      const s = seg(l, ok ? 15.0 : 14.0, (ok ? 15.0 : 14.0) + 0.25, E.outBack);
      at((ax + bx) / 2, y + 16, s, 0, () => chip(0, 0, ok ? '✓ director · 3구간 끝으로 결정' : '✕ 보스 등장 장소가 서로 다름', { align: 'center', color: '#05060A', fill: col, size: 15, w: 700, h: 32, mono: false }));
    });
  }
  // GDD 로 묶이고 동결 도장
  const gp = seg(l, 15.75, 16.05, E.outBack);
  if (gp > 0) {
    at(1110, 470, gp, -0.03, () => {
      panel(-190, -230, 380, 460, { fill: '#0E0C1A', stroke: hexA(C.violet, 0.7), lw: 2, glow: 40, glowColor: C.violet });
      txt('01_director_gdd.md', -160, -186, { mono: true, size: 14, w: 600, color: C.violet });
      txt('GDD', -160, -130, { size: 52, w: 800, color: C.ink });
      for (let k = 0; k < 8; k++) { ctx.fillStyle = k % 3 === 0 ? hexA(C.violet, 0.7) : 'rgba(255,255,255,0.16)'; ctx.fillRect(-160, -90 + k * 36, k % 3 === 0 ? 200 : 300 - (k * 37) % 90, 10); }
    });
    const sp = seg(l, 16.05, 16.22, E.inExpo);
    withA(clamp(sp * 2), () => at(1440, 330, lerp(2.4, 1, sp), -0.16, () => {
      ctx.save(); ctx.strokeStyle = C.violet; ctx.lineWidth = 6; rr(-150, -54, 300, 108, 12); ctx.stroke(); ctx.restore();
      txt('FREEZE', 0, 16, { size: 56, w: 800, color: C.violet, align: 'center', track: 6 });
      txt('shasum 01_* → freeze_01.sha', 0, 44, { mono: true, size: 12, w: 600, color: C.violet, align: 'center' });
    }));
  }
  // 확정본으로 승격
  const pr = seg(l, 16.7, 17.1, E.outExpo);
  if (pr > 0) withA(pr, () => {
    const y = 740, h = 160;
    panel(760, y, 400, h, { fill: 'rgba(255,255,255,0.03)', stroke: 'rgba(255,255,255,0.12)' });
    panel(1400, y, 400, h, { fill: hexA(C.violet, 0.06), stroke: hexA(C.violet, 0.5) });
    txt('_workspace/coin-runner/', 784, y + 36, { mono: true, size: 14, w: 700, color: C.dim });
    txt('games/coin-runner/', 1424, y + 36, { mono: true, size: 14, w: 700, color: C.violet });
    txt('작업 기록', 1136, y + 36, { size: 13, w: 600, color: C.mute, align: 'right' });
    txt('확정본', 1776, y + 36, { size: 13, w: 700, color: C.violet, align: 'right' });
    const F = [['01_director_gdd.md', 'docs/GDD.md'], ['01_systems_balance/*.csv', 'data/balance/'], ['01_narrative_dialogue.csv', 'data/dialogue.csv'], ['01_ux_strings.csv', 'data/ui_strings.csv']];
    F.forEach(([a, b], k) => {
      const t0 = 17.1 + k * 0.3, yy = y + 68 + k * 24;
      withA(seg(l, 16.9 + k * 0.05, 17.1 + k * 0.05), () => txt(a, 784, yy, { mono: true, size: 13, w: 500, color: l >= t0 + 0.3 ? C.mute : C.ink }));
      const u = inv(t0, t0 + 0.3, l);
      if (u > 0 && u < 1) { const e = E.inOutCubic(u); glowDot(lerp(1140, 1420, e), yy - 5 - Math.sin(Math.PI * e) * 30, 22, C.violet, 1); }
      if (l >= t0 + 0.3) withA(seg(l, t0 + 0.3, t0 + 0.45), () => txt('→ ' + b, 1424, yy, { mono: true, size: 13, w: 600, color: C.ink }));
    });
    line(1170, y + h / 2, 1390, y + h / 2, hexA(C.violet, 0.4), 2);
  });
}
// ---- 카드 내용(l: 기획 장면 상대 시각)
function cardSystems(x, y, w, h, l) {
  const cols = ['id', 'hp', 'atk', 'spd'], cx = [0, 76, 116, 150];
  cols.forEach((c, i) => txt(c, x + cx[i], y + 16, { mono: true, size: 12, w: 600, color: C.dim }));
  const morph = seg(l, 9.7, 10.0);
  const rows = [['grunt', morph < 0.5 ? '120' : ' 90', '14', '180'], ['golem', '900', '40', ' 90'], ['debris', ' —', '25', ' —'], ['coin', ' —', ' —', ' —'], ['player', '100', ' —', '420']];
  rows.forEach((r, j) => {
    const yy = y + 46 + j * 30, a = seg(l, 6.8 + j * 0.06, 7.1 + j * 0.06);
    if (j === 0 && l >= 9.7 && l < 10.6) { ctx.fillStyle = hexA(C.amber, 0.25 * (1 - inv(10.0, 10.6, l))); ctx.fillRect(x - 6, yy - 18, w + 12, 26); }
    r.forEach((v, i) => txt(v, x + cx[i], yy, { mono: true, size: 14, w: i === 0 ? 600 : 500, color: j === 0 && i === 1 && l >= 9.7 ? C.amber : C.ink, alpha: a }));
  });
  withA(seg(l, 7.2, 7.6), () => txt('data/balance/*.csv', x, y + h - 4, { mono: true, size: 11, w: 500, color: C.mute }));
}
function cardNarrative(x, y, w, h, l) {
  const L = [['락키', '침입자를 확인했습니다.', 'neutral'], ['도비', '붕괴? 잠깐만!', 'surprise'], ['락키', '출구는 통로 끝에 하나.', 'neutral'], ['골렘', '(낮은 으르렁)', 'creature']];
  L.forEach(([sp, s, em], j) => {
    const a = seg(l, 6.9 + j * 0.15, 7.2 + j * 0.15); if (a <= 0) return;
    const yy = y + 18 + j * 50;
    withA(a, () => {
      txt(sp, x, yy, { size: 13, w: 800, color: j % 2 ? C.lime : C.violet });
      txt(em, x + w, yy, { mono: true, size: 10, w: 500, color: C.mute, align: 'right' });
      txt(s, x, yy + 22, { size: 15, w: 500, color: C.ink });
    });
  });
}
function cardLevel(x, y, w, h, l) {
  const p = seg(l, 7.2, 8.2, E.inOutCubic);
  const pts = [[0, 130], [40, 130], [60, 100], [92, 100], [110, 130], [150, 130], [164, 70]];
  ctx.save(); ctx.strokeStyle = C.ink; ctx.lineWidth = 2.5; ctx.beginPath();
  const n = Math.max(1, Math.floor(p * (pts.length - 1)) + 1);
  pts.slice(0, n + 1).forEach(([px, py], i) => (i ? ctx.lineTo(x + px, y + py) : ctx.moveTo(x + px, y + py)));
  ctx.stroke(); ctx.restore();
  [[20, 118], [48, 100], [76, 88], [128, 118], [140, 118]].forEach(([cx, cy], i) => { if (p > i / 5) circle(x + cx, y + cy, 4.5, C.gold); });
  [[70, 92], [120, 124]].forEach(([dx, dy]) => { if (p > 0.5) { line(x + dx - 5, y + dy - 5, x + dx + 5, y + dy + 5, C.red, 2.5); line(x + dx + 5, y + dy - 5, x + dx - 5, y + dy + 5, C.red, 2.5); } });
  // 보스방 표시: 리뷰에서 위치가 바뀐다
  const moved = seg(l, 15.0, 15.4, E.inOutCubic);
  withA(seg(l, 8.0, 8.4), () => { const bx = lerp(x + 92, x + 158, moved); ctx.save(); ctx.strokeStyle = l >= 14.0 && l < 15.0 ? C.red : C.amber; ctx.lineWidth = 2; ctx.setLineDash([3, 3]); rr(bx - 16, y + 22, 32, 30, 4); ctx.stroke(); ctx.restore(); txt('boss', bx, y + 42, { mono: true, size: 9, w: 700, color: C.amber, align: 'center' }); });
  withA(seg(l, 7.8, 8.2), () => {
    circle(x + 40, y + 60, 30, hexA(C.cyan, 0.12), hexA(C.cyan, 0.5), 1);
    txt('amb_vault', x + 40, y + 64, { mono: true, size: 10, w: 600, color: C.cyan, align: 'center' });
    txt('사운드 구역 3 · 프랍 4', x, y + h - 4, { mono: true, size: 11, w: 500, color: C.mute });
  });
}
function cardUX(x, y, w, h, l) {
  withA(seg(l, 7.4, 7.8), () => {
    ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,0.4)'; ctx.lineWidth = 1.5; rr(x, y + 4, w, 104, 6); ctx.stroke(); ctx.restore();
    ctx.save(); ctx.setLineDash([4, 3]); ctx.strokeStyle = C.lime; rr(x + 8, y + 12, 58, 20, 3); ctx.stroke(); rr(x + w - 70, y + 12, 62, 20, 3); ctx.stroke(); rr(x + w / 2 - 34, y + 70, 68, 26, 13); ctx.stroke(); ctx.restore();
    txt('lbl_score', x + 12, y + 26, { mono: true, size: 9, w: 600, color: C.lime });
    txt('bar_hp', x + w - 64, y + 26, { mono: true, size: 9, w: 600, color: C.lime });
    txt('btn_start', x + w / 2, y + 87, { mono: true, size: 9, w: 600, color: C.lime, align: 'center' });
  });
  ['scr_title', 'scr_game', 'scr_result'].forEach((s, i) => { const p = seg(l, 7.7 + i * 0.12, 8.0 + i * 0.12); withA(p, () => { chip(x, y + 138 + i * 30, s, { size: 11, h: 22, padX: 8, color: C.ink }); if (i < 2) txt('↓', x + 12, y + 156 + i * 30, { size: 12, w: 700, color: C.mute }); }); });
}
function cardBalance(x, y, w, h, l) {
  const shift = seg(l, 10.2, 10.6, E.inOutCubic);
  const mean = lerp(150, 96, shift);
  const bx = x, by = y + 118, n = 14, bw = w / n;
  const X = s => bx + (s / 210) * w;
  ctx.fillStyle = hexA(C.green, 0.12); ctx.fillRect(X(60), y + 8, X(120) - X(60), 112);
  txt('목표 60–120s', X(60) + 3, y + 22, { mono: true, size: 9, w: 600, color: C.green });
  const grow = seg(l, 7.3, 7.9, E.outCubic);
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
    const cp = pass ? seg(l, 10.6, 10.85, E.outBack) : seg(l, 7.9, 8.1, E.outBack);
    at(x + w - 30, by + 58, cp, 0, () => chip(0, 0, pass ? 'PASS' : 'FAIL', { align: 'center', size: 13, w: 800, h: 26, color: '#05060A', fill: pass ? C.green : C.coral }));
    txt('5,000회', x + w, by + 32, { mono: true, size: 11, w: 600, color: C.mute, align: 'right' });
  });
}
