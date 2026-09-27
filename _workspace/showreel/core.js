// ============================================================================
// VARCO GAME STUDIO 쇼릴 — 공통 엔진
// 모든 그리기는 시간 t(초)만으로 결정된다. 같은 t 면 같은 프레임이 나온다.
// ============================================================================
const W = 1920, H = 1080, FPS = 60;
const DUR = CUES.duration, BEAT = CUES.beat;
let cv, ctx, fxA, fxB, grainTiles = [];

const C = {
  bg: '#05060A', ink: '#F4F5F7', dim: '#8A90A0', mute: '#4A4F5C',
  lime: '#C8FF3D', violet: '#9D7BFF', amber: '#FFB938', cyan: '#2EE6FF', coral: '#FF5E62',
  gold: '#FFD166', opus: '#B69CFF', sonnet: '#5EEAD4', green: '#4ADE80', red: '#FF4D5E',
};
const PHASE = [
  { no: '01', name: '기획', en: 'PLAN', color: C.violet },
  { no: '02', name: '명세', en: 'SPEC', color: C.amber },
  { no: '03', name: '제작', en: 'MAKE', color: C.cyan },
  { no: '04', name: '개발', en: 'BUILD', color: C.lime },
  { no: '05', name: '출시', en: 'SHIP', color: C.coral },
];

// ---------------------------------------------------------------- 수학·이징
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const inv = (a, b, x) => clamp((x - a) / (b - a));
const E = {
  lin: t => t,
  outExpo: t => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t)),
  inExpo: t => (t <= 0 ? 0 : Math.pow(2, 10 * t - 10)),
  inOutExpo: t => (t <= 0 ? 0 : t >= 1 ? 1 : t < 0.5 ? Math.pow(2, 20 * t - 10) / 2 : (2 - Math.pow(2, -20 * t + 10)) / 2),
  outCubic: t => 1 - Math.pow(1 - t, 3),
  inCubic: t => t * t * t,
  inOutCubic: t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  outQuart: t => 1 - Math.pow(1 - t, 4),
  inQuart: t => t * t * t * t,
  outBack: t => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  outBackBig: t => { const c1 = 3.2, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  outElastic: t => (t <= 0 ? 0 : t >= 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * (2 * Math.PI) / 3) + 1),
  inOutSine: t => -(Math.cos(Math.PI * t) - 1) / 2,
};
const seg = (t, a, b, ease = E.outExpo) => ease(inv(a, b, t));
const hash = n => { let x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
function rng(seed) { let s = seed >>> 0; return () => { s += 0x6D2B79F5; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const noise1 = x => { const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f); return lerp(hash(i), hash(i + 1), u) * 2 - 1; };
function hexA(hex, a) {
  const h = hex.replace('#', ''); const n = parseInt(h.length === 3 ? h.split('').map(c => c + c).join('') : h, 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
}
function mixHex(a, b, t) {
  const pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16);
  const ch = s => Math.round(lerp((pa >> s) & 255, (pb >> s) & 255, t));
  return `#${((1 << 24) + (ch(16) << 16) + (ch(8) << 8) + ch(0)).toString(16).slice(1)}`;
}

// ---------------------------------------------------------------- 큐
const EV = CUES.events;
const evOf = kind => EV.filter(e => e.kind === kind);
const IMPACTS = evOf('impact'), SLAMS = evOf('slam'), GLITCHES = evOf('glitch');
function sinceLast(t, list) { let best = Infinity; for (const e of list) { if (e.t <= t && t - e.t < best) best = t - e.t; } return best; }
function sectionAt(t) { for (const s of CUES.sections) if (t >= s.start && t < s.end) return s; return CUES.sections[CUES.sections.length - 1]; }
// 킥이 도는 구간(음악과 같은 규칙)
function kickOn(t) { return (t >= 8 && t < 25.75) || (t >= 26 && t < 46) || (t >= 51 && t < 58); }
function kickPulse(t, k = 9) { if (!kickOn(t)) return 0; const b = t % BEAT; return Math.exp(-b * k); }

// ---------------------------------------------------------------- 그리기 도구
function F(w, size, mono = false) { return `${w} ${size}px ${mono ? 'SFMono, Menlo, monospace' : 'Pretendard, sans-serif'}`; }
function txt(s, x, y, o = {}) {
  const { w = 700, size = 40, color = C.ink, align = 'left', base = 'alphabetic', alpha = 1, track = 0, mono = false,
    blur = 0, glow = 0, glowColor = null, stroke = 0, strokeColor = null } = o;
  ctx.save();
  ctx.font = F(w, size, mono); ctx.textAlign = align; ctx.textBaseline = base;
  ctx.letterSpacing = `${track}px`;
  ctx.globalAlpha *= alpha;
  if (blur > 0.2) ctx.filter = `blur(${blur}px)`;
  if (glow) { ctx.shadowColor = glowColor || color; ctx.shadowBlur = glow; }
  if (stroke) { ctx.lineWidth = stroke; ctx.strokeStyle = strokeColor || color; ctx.strokeText(s, x, y); }
  else { ctx.fillStyle = color; ctx.fillText(s, x, y); }
  ctx.restore();
}
function tw(s, w, size, mono = false, track = 0) { ctx.save(); ctx.font = F(w, size, mono); ctx.letterSpacing = `${track}px`; const m = ctx.measureText(s).width; ctx.restore(); return m; }
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function panel(x, y, w, h, o = {}) {
  const { r = 18, fill = 'rgba(255,255,255,0.035)', stroke = 'rgba(255,255,255,0.10)', lw = 1.2, glow = 0, glowColor = null } = o;
  ctx.save();
  if (glow) { ctx.shadowColor = glowColor; ctx.shadowBlur = glow; }
  rr(x, y, w, h, r); ctx.fillStyle = fill; ctx.fill();
  ctx.shadowBlur = 0;
  if (stroke) { ctx.lineWidth = lw; ctx.strokeStyle = stroke; ctx.stroke(); }
  ctx.restore();
}
function chip(x, y, s, o = {}) {
  const { color = C.ink, fill = 'rgba(255,255,255,0.06)', stroke = null, size = 15, mono = true, w = 600, padX = 12, h = 30, alpha = 1, align = 'left' } = o;
  const tw_ = tw(s, w, size, mono) + padX * 2;
  const x0 = align === 'center' ? x - tw_ / 2 : align === 'right' ? x - tw_ : x;
  ctx.save(); ctx.globalAlpha *= alpha;
  rr(x0, y - h / 2, tw_, h, h / 2); ctx.fillStyle = fill; ctx.fill();
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = 1.2; ctx.stroke(); }
  txt(s, x0 + padX, y + size * 0.36, { w, size, color, mono });
  ctx.restore();
  return tw_;
}
function withA(a, fn) { if (a <= 0.001) return; ctx.save(); ctx.globalAlpha *= a; fn(); ctx.restore(); }
function at(x, y, s, rot, fn) { ctx.save(); ctx.translate(x, y); if (rot) ctx.rotate(rot); if (s !== 1) ctx.scale(s, s); fn(); ctx.restore(); }
function line(x1, y1, x2, y2, color, lw = 1, alpha = 1) { ctx.save(); ctx.globalAlpha *= alpha; ctx.strokeStyle = color; ctx.lineWidth = lw; ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke(); ctx.restore(); }
function circle(x, y, r, fill, stroke, lw = 2) { ctx.beginPath(); ctx.arc(x, y, Math.max(0, r), 0, Math.PI * 2); if (fill) { ctx.fillStyle = fill; ctx.fill(); } if (stroke) { ctx.lineWidth = lw; ctx.strokeStyle = stroke; ctx.stroke(); } }
function glowDot(x, y, r, color, a = 1) {
  ctx.save(); ctx.globalAlpha *= a; ctx.globalCompositeOperation = 'lighter';
  const g = ctx.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, hexA(color, 0.9)); g.addColorStop(0.25, hexA(color, 0.35)); g.addColorStop(1, hexA(color, 0));
  ctx.fillStyle = g; ctx.fillRect(x - r, y - r, r * 2, r * 2); ctx.restore();
}
// 한 글자씩 드러나는 텍스트: 각 글자가 아래에서 올라오며 흐림이 걷힌다
function staggerText(s, x, y, t, t0, o = {}) {
  const { per = 0.035, dur = 0.5, rise = 40, align = 'left', ease = E.outExpo, blurFrom = 10, ...rest } = o;
  const chars = [...s]; const size = rest.size || 40, w = rest.w || 700, mono = rest.mono || false, track = rest.track || 0;
  const total = tw(s, w, size, mono, track);
  let cx = align === 'center' ? x - total / 2 : align === 'right' ? x - total : x;
  for (let i = 0; i < chars.length; i++) {
    const ch = chars[i]; const cw = tw(ch, w, size, mono, track);
    const p = seg(t, t0 + i * per, t0 + i * per + dur, ease);
    if (p > 0) txt(ch, cx, y + (1 - p) * rise, { ...rest, alpha: (rest.alpha ?? 1) * clamp(p * 1.4), blur: (1 - p) * blurFrom });
    cx += cw;
  }
  return total;
}
// 암호처럼 섞였다가 풀리는 텍스트
const SCR = '#%@&$ABCDEFGHJKLMNPQRSTUVWXYZ0123456789';
function scrambleText(s, x, y, t, t0, dur, o = {}) {
  const chars = [...s]; let out = '';
  const p = inv(t0, t0 + dur, t);
  for (let i = 0; i < chars.length; i++) {
    const reveal = i / chars.length < p;
    if (chars[i] === ' ' || reveal) out += chars[i];
    else if (i / chars.length < p + 0.35) out += SCR[Math.floor(hash(i * 13 + Math.floor(t * 30)) * SCR.length)];
    else out += '';
  }
  txt(out, x, y, o);
}
// 마스크 안에서 밀려 올라오는 텍스트
function maskUp(s, x, y, p, o = {}) {
  const size = o.size || 40;
  ctx.save(); ctx.beginPath(); ctx.rect(x - 4000 * (o.align === 'center' ? 0.5 : o.align === 'right' ? 1 : 0), y - size * 1.05, 4000, size * 1.35); ctx.clip();
  txt(s, x, y + (1 - p) * size * 1.2, o); ctx.restore();
}

// ---------------------------------------------------------------- 초기화
const DUST = [];
function initReel() {
  cv = document.getElementById('cv'); ctx = cv.getContext('2d');
  fxA = document.createElement('canvas'); fxA.width = W; fxA.height = H;
  fxB = document.createElement('canvas'); fxB.width = W; fxB.height = H;
  // 필름 그레인 타일 6장(프레임 번호로 돌려 쓴다)
  for (let k = 0; k < 6; k++) {
    const g = document.createElement('canvas'); g.width = g.height = 256; const gx = g.getContext('2d');
    const img = gx.createImageData(256, 256); const r = rng(1000 + k);
    for (let i = 0; i < img.data.length; i += 4) { const v = r() * 255; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255; }
    gx.putImageData(img, 0, 0); grainTiles.push(g);
  }
  const r = rng(7);
  for (let i = 0; i < 90; i++) DUST.push({ x: r() * W, y: r() * H, z: 0.3 + r() * 0.7, s: r() * 1000 });
  if (typeof initScenesA === 'function') initScenesA();
  if (typeof initScenesB === 'function') initScenesB();
}

// ---------------------------------------------------------------- 배경
function accentAt(t) {
  const s = sectionAt(t); const i = CUES.sections.indexOf(s); const nx = CUES.sections[i + 1];
  if (nx && t > s.end - 0.4) return mixHex(s.color, nx.color, inv(s.end - 0.4, s.end, t));
  return s.color;
}
function drawBackground(t, o = {}) {
  const acc = o.accent || accentAt(t);
  ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
  if (t < 0.4) return;
  const kp = kickPulse(t);
  // 큰 번짐 빛
  const gx = W * (0.5 + 0.18 * Math.sin(t * 0.21)), gy = H * (0.45 + 0.1 * Math.cos(t * 0.17));
  const intro = seg(t, 0.4, 3.0, E.inOutSine);
  ctx.save(); ctx.globalAlpha = (0.13 + kp * 0.06) * intro;
  const g = ctx.createRadialGradient(gx, gy, 0, gx, gy, 1100);
  g.addColorStop(0, acc); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.restore();
  // 점 격자와 지나가는 빛의 띠
  const sp = 48, band = ((t * 0.35) % 1.6) * (W + H) - H * 0.3;
  ctx.save(); ctx.fillStyle = '#fff';
  for (let y = sp / 2; y < H; y += sp) for (let x = sp / 2; x < W; x += sp) {
    const d = Math.abs((x + y * 0.6) - band);
    const a = (0.045 + Math.max(0, 1 - d / 220) * 0.16) * intro;
    ctx.globalAlpha = a; ctx.fillRect(x - 1, y - 1, 2, 2);
  }
  ctx.restore();
  // 떠다니는 먼지
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (const d of DUST) {
    const x = (d.x + t * 18 * d.z) % W, y = (d.y - t * 9 * d.z + H * 10) % H;
    ctx.globalAlpha = (0.12 + 0.25 * d.z) * intro * (0.6 + 0.4 * Math.sin(t * 1.3 + d.s));
    ctx.fillStyle = acc; ctx.fillRect(x, y, 2 * d.z, 2 * d.z);
  }
  ctx.restore();
}

// ---------------------------------------------------------------- 카메라 흔들림
function shake(t) {
  let a = 0;
  for (const e of IMPACTS) { const d = t - e.t; if (d >= 0 && d < 0.5) { const s = { mid: 7, big: 12, huge: 22, final: 14 }[e.size] || 8; a += s * Math.exp(-d * 9); } }
  for (const e of SLAMS) { const d = t - e.t; if (d >= 0 && d < 0.3) a += 8 * Math.exp(-d * 14); }
  return { x: noise1(t * 40) * a, y: noise1(t * 40 + 99) * a };
}

// ---------------------------------------------------------------- 화면 틀(쇼릴 HUD)
function drawChrome(t) {
  const a = seg(t, 8.2, 9.0) * (1 - seg(t, 51.6, 52.0));
  if (a <= 0) return;
  withA(a * 0.9, () => {
    const acc = accentAt(t);
    // 모서리 표식
    const m = 44, L = 26;
    ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,0.35)'; ctx.lineWidth = 1.5;
    for (const [x, y, sx, sy] of [[m, m, 1, 1], [W - m, m, -1, 1], [m, H - m, 1, -1], [W - m, H - m, -1, -1]]) {
      ctx.beginPath(); ctx.moveTo(x, y + sy * L); ctx.lineTo(x, y); ctx.lineTo(x + sx * L, y); ctx.stroke();
    }
    ctx.restore();
    txt('VARCO GAME STUDIO', 84, 76, { mono: true, size: 14, w: 600, color: C.dim, track: 3 });
    txt('SHOWREEL · 2026', W - 84, H - 64, { mono: true, size: 14, w: 500, color: C.mute, track: 3, align: 'right' });
    // 단계 표시
    const cur = phaseIndex(t);
    let x = W - 84;
    for (let i = PHASE.length - 1; i >= 0; i--) {
      const p = PHASE[i]; const on = i === cur; const done = i < cur;
      const label = `${p.no} ${p.name}`;
      const wv = tw(label, 700, 15, false, 1);
      x -= wv;
      txt(label, x, 76, { size: 15, w: on ? 800 : 600, color: on ? p.color : done ? C.dim : C.mute, track: 1 });
      if (on) { ctx.fillStyle = p.color; ctx.fillRect(x, 86, wv * phaseProgress(t), 2); }
      x -= 26;
    }
    // 타임코드
    const fr = Math.floor(t * FPS), s = Math.floor(t), ff = fr % FPS;
    txt(`TC 00:00:${String(s).padStart(2, '0')}:${String(ff).padStart(2, '0')}`, 84, H - 64, { mono: true, size: 14, w: 500, color: C.mute, track: 2 });
    glowDot(76 + 0, H - 69, 10, acc, 0.6 + 0.4 * kickPulse(t));
  });
}
function phaseIndex(t) { return t < 14 ? -1 : t < 22 ? 0 : t < 26 ? 1 : t < 36 ? 2 : t < 46 ? 3 : t < 52 ? 4 : -1; }
function phaseProgress(t) { const b = [[14, 22], [22, 26], [26, 36], [36, 46], [46, 52]][phaseIndex(t)]; return b ? inv(b[0], b[1], t) : 0; }

// ---------------------------------------------------------------- 장면 전환 와이프
const WIPES = [
  { t: 14, color: C.violet, label: '01 기획' }, { t: 22, color: C.amber, label: '02 명세' },
  { t: 36, color: C.lime, label: '04 개발' }, { t: 46, color: C.coral, label: '05 출시' },
];
function drawWipes(t) {
  for (const wp of WIPES) {
    const p = inv(wp.t - 0.3, wp.t + 0.3, t); if (p <= 0 || p >= 1) continue;
    const e = E.inOutCubic(p);
    const bw = W * 1.9, skew = 260, cx = lerp(-W * 1.05, W * 2.05, e);
    const band = (off, width, color, a) => {
      ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = color; ctx.beginPath();
      ctx.moveTo(cx + off - width / 2 + skew, 0); ctx.lineTo(cx + off + width / 2 + skew, 0);
      ctx.lineTo(cx + off + width / 2 - skew, H); ctx.lineTo(cx + off - width / 2 - skew, H); ctx.closePath(); ctx.fill(); ctx.restore();
    };
    band(-bw * 0.08, bw * 1.0, mixHex(wp.color, '#000000', 0.55), 1);
    band(0, bw * 0.9, wp.color, 1);
    band(bw * 0.47, 10, '#ffffff', 0.9);
    // 와이프 위의 큰 번호: 밝은 띠 안에서만 보이게 자른다
    const la = 1 - Math.abs(p - 0.5) * 2.2;
    if (la > 0) {
      ctx.save(); ctx.beginPath(); const wd = bw * 0.9;
      ctx.moveTo(cx - wd / 2 + skew, 0); ctx.lineTo(cx + wd / 2 + skew, 0); ctx.lineTo(cx + wd / 2 - skew, H); ctx.lineTo(cx - wd / 2 - skew, H); ctx.closePath(); ctx.clip();
      txt(wp.label, W / 2, H / 2 + 60, { size: 170, w: 800, color: '#05060A', align: 'center', alpha: clamp(la), track: -4 });
      ctx.restore();
    }
  }
}

// ---------------------------------------------------------------- 후처리
function flashAmount(t) {
  let f = 0;
  for (const e of IMPACTS) { const d = t - e.t; if (d >= 0 && d < 0.6) f = Math.max(f, ({ huge: 0.85, big: 0.55, final: 0.7 }[e.size] || 0.25) * Math.exp(-d * 10)); }
  // 오프닝 끝 백색 폭발
  f = Math.max(f, seg(t, 3.9, 4.0, E.inExpo) * (t < 4.0 ? 1 : 0));
  f = Math.max(f, seg(t, 25.85, 26.0, E.inExpo) * (t < 26 ? 1 : 0));
  return f;
}
function aberration(t) {
  let a = 0;
  for (const e of IMPACTS) { const d = t - e.t; if (d >= 0 && d < 0.4) a = Math.max(a, ({ huge: 26, big: 16, final: 14 }[e.size] || 8) * Math.exp(-d * 12)); }
  for (const e of SLAMS) { const d = t - e.t; if (d >= 0 && d < 0.3) a = Math.max(a, 12 * Math.exp(-d * 14)); }
  for (const e of GLITCHES) { const d = t - e.t; if (d >= 0 && d < 0.35) a = Math.max(a, 18); }
  if (t >= 52 && t < 54) { const d = (t - 52) % 0.25; if (d < 0.06) a = Math.max(a, 20); }
  return a;
}
function glitchSlices(t) {
  let g = 0;
  for (const e of GLITCHES) { const d = t - e.t; if (d >= 0 && d < 0.35) g = 1 - d / 0.35; }
  if (t >= 52 && t < 54) { const d = (t - 52) % 0.25; if (d < 0.08) g = Math.max(g, 1 - d / 0.08); }
  if (t >= 50.5 && t < 50.62) g = Math.max(g, 0.8);
  return g;
}
function postFX(t) {
  const ab = aberration(t), gl = glitchSlices(t);
  if (ab > 0.5 || gl > 0.05) {
    const a = fxA.getContext('2d'); a.globalCompositeOperation = 'copy'; a.drawImage(cv, 0, 0);
    if (gl > 0.05) {
      ctx.save();
      const n = 14, fr = Math.floor(t * FPS);
      for (let i = 0; i < n; i++) {
        const y = Math.floor(hash(i * 7.3 + fr) * H), h = 8 + hash(i * 3.1 + fr) * 70;
        const dx = (hash(i * 9.7 + fr) - 0.5) * 220 * gl;
        ctx.drawImage(fxA, 0, y, W, h, dx, y, W, h);
      }
      ctx.restore();
      a.drawImage(cv, 0, 0);
    }
    if (ab > 0.5) {
      const b = fxB.getContext('2d');
      const chan = (color, dx) => {
        b.globalCompositeOperation = 'copy'; b.drawImage(fxA, 0, 0);
        b.globalCompositeOperation = 'multiply'; b.fillStyle = color; b.fillRect(0, 0, W, H);
        b.globalCompositeOperation = 'source-over';
        ctx.drawImage(fxB, dx, 0);
      };
      ctx.save(); ctx.globalCompositeOperation = 'copy'; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
      ctx.globalCompositeOperation = 'lighter';
      chan('#ff0000', ab); chan('#00ff00', 0); chan('#0000ff', -ab);
      ctx.restore();
    }
  }
  const fl = flashAmount(t);
  if (fl > 0.01) { ctx.save(); ctx.globalAlpha = fl; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  // 비네트
  ctx.save();
  const v = ctx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 1.0);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.62)');
  ctx.fillStyle = v; ctx.fillRect(0, 0, W, H); ctx.restore();
  // 필름 그레인
  const fr = Math.floor(t * FPS);
  ctx.save(); ctx.globalAlpha = 0.055; ctx.globalCompositeOperation = 'overlay';
  const tile = grainTiles[fr % grainTiles.length];
  const ox = Math.floor(hash(fr) * 256), oy = Math.floor(hash(fr + 5) * 256);
  for (let y = -oy; y < H; y += 256) for (let x = -ox; x < W; x += 256) ctx.drawImage(tile, x, y);
  ctx.restore();
  // 마지막 암전
  const fade = seg(t, 58.6, 59.85, E.inOutSine);
  if (fade > 0) { ctx.save(); ctx.globalAlpha = fade; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
}

// ---------------------------------------------------------------- 메인 렌더
const SCENES = [];   // {name, start, end, draw(t)}
function drawSceneAt(name, t) { const s = SCENES.find(x => x.name === name); if (s) s.draw(t); }
function render(t) {
  t = clamp(t, 0, DUR - 1e-6);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; ctx.filter = 'none';
  drawBackground(t);
  const sh = shake(t);
  ctx.save(); ctx.translate(sh.x, sh.y);
  for (const s of SCENES) if (t >= s.start && t < s.end) s.draw(t);
  ctx.restore();
  drawChrome(t);
  drawWipes(t);
  postFX(t);
}
