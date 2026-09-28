#!/usr/bin/env python3
"""2분 제작 과정 영상 사운드트랙 합성기 — ../timeline.json 하나로 음악과 효과음을 모두 만든다.

사용법
  python3 synth.py              # soundtrack.wav, soundtrack_wave.png 생성 + 측정값 출력
  python3 synth.py --no-master  # 마스터링 없이 pre_master.wav 만(빠른 확인용)

- 120 BPM, A 단조, 진행 Am–F–C–G. 시각은 코드에 적지 않고 모두 timeline.json 에서 읽는다.
  sections[].music(편성 플래그), kick(킥 구간), rolls(스네어 롤), swells(필터가 열리는 긴 베이스),
  silences(흡입 정적), bursts(꽉 찬 편성), events(효과음).
- 장면 시각을 바꾸면 `python3 build_timeline.py && python3 audio/synth.py` 만 다시 돌리면 된다.
- 난수는 시드와 이벤트 키로만 정해지므로 실행할 때마다 같은 결과가 나온다.
- 도구: numpy + 표준 라이브러리 wave + ffmpeg(측정·리미터).
"""
import json
import pathlib
import re
import subprocess
import sys
import wave
import zlib

import numpy as np

SR = 48000
HERE = pathlib.Path(__file__).resolve().parent
TL = json.loads((HERE.parent / "timeline.json").read_text(encoding="utf-8"))
BPM = TL["bpm"]
BEAT = 60.0 / BPM
S16 = BEAT / 4
BAR = BEAT * 4
DUR = float(TL["duration"])
N = int(round(DUR * SR))
SECTIONS = TL["sections"]
SEC = {s["name"]: (s["start"], s["end"]) for s in SECTIONS}
MUSIC = {s["name"]: s.get("music", {}) for s in SECTIONS}
EVENTS = TL["events"]
ROLLS = [tuple(r) for r in TL.get("rolls", [])]
SWELLS = TL.get("swells", [])
SILENCES = [tuple(r) for r in TL.get("silences", [])]
BURSTS = [tuple(r) for r in TL.get("bursts", [])]
KICK = [tuple(r) for r in TL.get("kick", [])]
BIG_IMPACTS = [e for e in EVENTS if e["kind"] == "impact" and e.get("size") in ("big", "huge", "final")]
FINAL_T = max([e["t"] for e in EVENTS if e["kind"] == "impact" and e.get("size") == "final"], default=DUR - 2.0)
# 꽉 찬 편성(원본 produce 와 같은 규칙)
BURST_MUSIC = dict(kick=True, clap=True, hats="open", bass="sixteenth", lead=True, pad=1.0)
SEED = 20260928
TARGET_LUFS = -14.0
TP_CEIL = -1.0
TWO_PI = 2 * np.pi


# ============================================================================ 기본 도구
def rng(*keys):
    """이벤트마다 독립적이고 재현 가능한 난수(내장 hash 는 실행마다 바뀌므로 crc32 를 쓴다)."""
    return np.random.default_rng([SEED, zlib.crc32(repr(keys).encode())])


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(n):
    return np.arange(n) / SR


def ns(sec):
    return max(1, int(round(sec * SR)))


def section_at(t):
    for s in SECTIONS:
        if s["start"] <= t < s["end"]:
            return s["name"]
    return SECTIONS[-1]["name"]


def inside(t, name, a=None, b=None):
    s0, s1 = SEC[name]
    a = s0 if a is None else a
    b = s1 if b is None else b
    return a <= t < b


def in_ranges(t, ranges):
    return any(a <= t < b for a, b in ranges)


def range_at(t, ranges):
    for r in ranges:
        if r[0] <= t < r[1]:
            return r
    return None


def music_at(t):
    """그 시각의 편성. bursts 가 section 편성을 덮고, 롤·정적 구간에서는 박수·햇·베이스·아르페지오를 쉰다."""
    if in_ranges(t, BURSTS):
        return BURST_MUSIC
    return MUSIC[section_at(t)]


def kick_on(t):
    return in_ranges(t, KICK)


def resting(t):
    return in_ranges(t, ROLLS) or in_ranges(t, SILENCES)


def new_bus():
    return np.zeros((2, N))


def pan_gains(pan):
    ang = (np.clip(pan, -1, 1) + 1) * np.pi / 4
    return np.cos(ang) * np.sqrt(2), np.sin(ang) * np.sqrt(2)


def place(bus, t0, sig, gain=1.0, pan=0.0, send=0.0):
    """버스에 소리를 얹는다. sig 는 모노(n,) 또는 스테레오(2, n). send 는 리버브 보내기 양."""
    i0 = int(round(t0 * SR))
    if sig.ndim == 1:
        gl, gr = pan_gains(pan)
        st = np.vstack([sig * gl, sig * gr])
    else:
        st = sig
    if i0 < 0:
        st = st[:, -i0:]
        i0 = 0
    if i0 >= N or st.shape[1] == 0:
        return
    n = min(st.shape[1], N - i0)
    bus[:, i0:i0 + n] += st[:, :n] * gain
    if send:
        REV[:, i0:i0 + n] += st[:, :n] * gain * send


# ---------------------------------------------------------------------------- 오실레이터
def phase(freq, n, ph0=0.0):
    if np.isscalar(freq):
        return (ph0 + np.arange(n) * (freq / SR)) % 1.0
    return (ph0 + np.cumsum(freq) / SR) % 1.0


def _blep(ph, dt):
    y = np.zeros_like(ph)
    m = ph < dt
    x = ph[m] / dt[m]
    y[m] = x + x - x * x - 1
    m = ph > 1 - dt
    x = (ph[m] - 1) / dt[m]
    y[m] = x * x + x + x + 1
    return y


def saw(freq, n, ph0=0.0):
    ph = phase(freq, n, ph0)
    dt = np.full(n, freq / SR) if np.isscalar(freq) else np.asarray(freq) / SR
    return 2 * ph - 1 - _blep(ph, dt)


def pulse(freq, n, pw=0.5, ph0=0.0):
    return saw(freq, n, ph0) - saw(freq, n, (ph0 + pw) % 1.0)


def tri(freq, n, ph0=0.0):
    ph = phase(freq, n, ph0)
    return 4 * np.abs(ph - 0.5) - 1


def sine(freq, n, ph0=0.0):
    return np.sin(TWO_PI * phase(freq, n, ph0))


def noise(n, *keys):
    return rng("noise", *keys).standard_normal(n)


# ---------------------------------------------------------------------------- 필터
def fft_filter(x, lp=None, hp=None, order=2):
    """긴 신호용 영위상 필터(패드·리버브). 짧은 타악기에는 쓰지 않는다(앞울림)."""
    n = x.shape[-1]
    X = np.fft.rfft(x, axis=-1)
    f = np.fft.rfftfreq(n, 1 / SR)
    H = np.ones_like(f)
    if lp:
        H *= 1 / np.sqrt(1 + (f / lp) ** (2 * order))
    if hp:
        H *= 1 / np.sqrt(1 + (hp / np.maximum(f, 1e-3)) ** (2 * order))
    return np.fft.irfft(X * H, n=n, axis=-1)


def biquad(x, kind, f0, q=0.707):
    """인과적 RBJ 바이쿼드(짧은 효과음용 파이썬 루프)."""
    f0 = min(max(f0, 10.0), SR * 0.45)
    w0 = TWO_PI * f0 / SR
    c, s = np.cos(w0), np.sin(w0)
    a = s / (2 * q)
    if kind == "lp":
        b0, b1, b2 = (1 - c) / 2, 1 - c, (1 - c) / 2
    elif kind == "hp":
        b0, b1, b2 = (1 + c) / 2, -(1 + c), (1 + c) / 2
    else:  # bp, 최대 이득 0 dB
        b0, b1, b2 = a, 0.0, -a
    a0, a1, a2 = 1 + a, -2 * c, 1 - a
    b0, b1, b2, a1, a2 = b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0
    out = [0.0] * len(x)
    x1 = x2 = y1 = y2 = 0.0
    for i, xi in enumerate(x.tolist()):
        yi = b0 * xi + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, xi, y1, yi
        out[i] = yi
    return np.array(out)


def svf(x, fc, q=0.707, mode="lp"):
    """시간에 따라 차단 주파수가 바뀌는 TPT 상태변수 필터(라이저·스윕용)."""
    n = len(x)
    fc = np.broadcast_to(np.clip(fc, 20, SR * 0.45), (n,))
    g = np.tan(np.pi * fc / SR)
    k = 1.0 / q
    a1 = 1 / (1 + g * (g + k))
    a2 = g * a1
    a3 = g * a2
    out = [0.0] * n
    ic1 = ic2 = 0.0
    for i, (xi, b1, b2, b3) in enumerate(zip(x.tolist(), a1.tolist(), a2.tolist(), a3.tolist())):
        v3 = xi - ic2
        v1 = b1 * ic1 + b2 * v3
        v2 = ic2 + b2 * ic1 + b3 * v3
        ic1 = 2 * v1 - ic1
        ic2 = 2 * v2 - ic2
        out[i] = v2 if mode == "lp" else v1 if mode == "bp" else xi - k * v1 - v2
    return np.array(out)


def onepole_tv(x, fc):
    fc = np.broadcast_to(np.clip(fc, 10, SR * 0.45), (len(x),))
    a = (1 - np.exp(-TWO_PI * fc / SR)).tolist()
    out = [0.0] * len(x)
    y = 0.0
    for i, (xi, ai) in enumerate(zip(x.tolist(), a)):
        y += ai * (xi - y)
        out[i] = y
    return np.array(out)


def softclip(x, drive=1.5):
    return np.tanh(drive * x) / np.tanh(drive)


def fade_edges(x, fin=0.002, fout=0.004):
    n = x.shape[-1]
    a, b = min(ns(fin), n // 2), min(ns(fout), n // 2)
    env = np.ones(n)
    env[:a] = np.linspace(0, 1, a)
    env[n - b:] = np.linspace(1, 0, b)
    return x * env


def expenv(n, tau):
    return np.exp(-tt(n) / tau)


def curve(keys, n=N, log=False):
    """(초, 값) 키프레임을 샘플 곡선으로. log=True 면 주파수처럼 로그 보간."""
    ts = np.array([k[0] for k in keys])
    vs = np.array([k[1] for k in keys], dtype=float)
    x = tt(n)
    if log:
        return np.exp(np.interp(x, ts, np.log(vs)))
    return np.interp(x, ts, vs)


# ============================================================================ 화성
CHORDS = {
    "Am": (45, [57, 60, 64]),
    "F": (41, [57, 60, 65]),
    "C": (48, [55, 60, 64]),
    "G": (43, [55, 59, 62]),
    "A5": (45, [57, 64, 69]),
}
# 구간마다 마디(2초) 단위로 도는 진행(길면 되풀이). outro 만 1초 단위. 목록에 없는 구간은 DEFAULT_SEQ.
DEFAULT_SEQ = ["Am", "F", "C", "G"]
SEQ = {
    "cold_open": ["Am"],
    "title": ["F", "G", "Am"],
    "overview": ["Am", "F", "C", "G"],
    "prep": ["Am", "F", "C", "G"],
    "plan": ["Am", "F", "C", "G"],
    "spec": ["Am", "F", "C", "G"],
    "produce": ["Am", "F", "C", "G"],
    "develop": ["F", "C", "G", "Am"],
    "release": ["Am", "F", "G"],
    "deliver": ["Am", "C", "G"],
    "outro": ["F", "G", "Am", "Am", "F", "G", "Am", "Am"],
}
SILENCE_ENDS = [b for _, b in SILENCES]


def chord_at(t):
    # 빌드업: 스웰이 시작한 마디는 스웰 코드(원본 spec 끝의 G, release 의 F)
    for sw in SWELLS:
        if sw["t"] <= t < sw["t"] + BAR:
            return sw["chord"]
    # 정적 직후 터지는 bursts(출시 GO)는 A5 로 연다
    br = range_at(t, BURSTS)
    if br and any(abs(br[0] - e) < 1e-6 for e in SILENCE_ENDS):
        return "A5"
    name = section_at(t)
    s0, _ = SEC[name]
    seq = SEQ.get(name, DEFAULT_SEQ)
    step = 1.0 if name == "outro" else BAR
    return seq[int((t - s0 + 1e-9) // step) % len(seq)]


def chord_segments():
    segs, cur, t0 = [], None, 0.0
    for k in range(int(DUR)):
        c = chord_at(k + 0.5)
        if c != cur:
            if cur is not None:
                segs.append((t0, float(k), cur))
            cur, t0 = c, float(k)
    segs.append((t0, DUR, cur))
    return segs


# ============================================================================ 버스
DRUMS, BASS, PAD, ARP, LEAD, SFX, DRONE = (new_bus() for _ in range(7))
REV = new_bus()
KICKS = []  # 사이드체인용 킥 시각


# ============================================================================ 드럼
def make_kick():
    n = ns(0.5)
    t = tt(n)
    f = 50 + (160 - 50) * np.exp(-t / 0.03)
    body = np.sin(TWO_PI * np.cumsum(f) / SR) * np.exp(-t / 0.19)
    click = biquad(noise(n, "kick") * np.exp(-t / 0.0015), "hp", 2500) * 0.6
    click += np.sin(TWO_PI * 1800 * t) * np.exp(-t / 0.004) * 0.25
    return fade_edges(softclip(body + click, 1.8), 0.0005, 0.02)


def make_clap():
    n = ns(0.35)
    t = tt(n)
    nz = noise(n, "clap")
    env = np.zeros(n)
    for k, off in enumerate([0.0, 0.009, 0.018]):
        i = ns(off)
        env[i:] += np.exp(-(t[: n - i]) / 0.006) * (0.8 + 0.1 * k)
    env += np.exp(-t / 0.13) * 0.45 * (t > 0.022)
    x = biquad(nz * env, "bp", 1500, 0.9) * 2.2
    x = biquad(x, "hp", 700)
    return fade_edges(x)


def make_snare():
    n = ns(0.28)
    t = tt(n)
    tone = (np.sin(TWO_PI * 185 * t) + 0.5 * np.sin(TWO_PI * 330 * t)) * np.exp(-t / 0.07)
    nz = biquad(noise(n, "snare") * np.exp(-t / 0.12), "hp", 1400) * 1.2
    return fade_edges(softclip(0.7 * tone + nz, 1.3))


def make_hat(open_=False, v=0):
    n = ns(0.35 if open_ else 0.08)
    t = tt(n)
    nz = noise(n, "hat", open_, v)
    # 금속성: 비정수 배음 사각파 몇 개 + 노이즈
    metal = sum(pulse(f, n, 0.5) for f in [3140 + 40 * v, 4410, 5690, 7250]) * 0.15
    x = biquad(nz + metal, "hp", 7200, 0.8)
    x *= np.exp(-t / (0.2 if open_ else 0.028))
    return fade_edges(x)


def make_glitch_blip(v):
    r = rng("gblip", v)
    n = ns(r.uniform(0.04, 0.09))
    f = r.choice([220, 330, 440, 660, 880]) * r.uniform(0.98, 1.02)
    x = pulse(f, n, r.uniform(0.2, 0.5))
    hold = int(r.integers(6, 22))
    x = np.repeat(x[::hold], hold)[:n]  # 표본 유지(비트크러시)
    x = np.round(x * 6) / 6
    return fade_edges(x * np.exp(-tt(n) / 0.05))


def build_drums():
    kick, clap, snare = make_kick(), make_clap(), make_snare()
    hats_c = [make_hat(False, v) for v in range(4)]
    hats_o = [make_hat(True, v) for v in range(2)]
    blips = [make_glitch_blip(v) for v in range(6)]

    def hats_on(t):
        # 롤 앞쪽 절반까지는 햇을 이어 쳐서 에너지를 끊지 않는다(원본 spec 과 같은 느낌)
        for a, b in ROLLS:
            if a <= t < b:
                return t < a + (b - a) * 0.5
        return not in_ranges(t, SILENCES)

    total16 = int(round(DUR / S16))
    for i in range(total16):
        t = i * S16
        pos = i % 4
        beat = (i // 4) % 4
        mu = music_at(t)
        r = rng("drum", i)
        if pos == 0 and kick_on(t):
            vel = 1.0 if beat == 0 else 0.92
            place(DRUMS, t, kick, 0.95 * vel)
            KICKS.append(t)
        if pos == 0 and beat in (1, 3) and mu.get("clap") and not resting(t):
            place(DRUMS, t, clap, 0.42, pan=0.05, send=0.18)
        # 하이햇
        hat = None
        mode = mu.get("hats", "none")
        if hats_on(t):
            if mode == "offbeat" and pos == 2:
                hat = (hats_c[i % 4], 0.2)
            elif mode == "light" and pos in (2, 3):
                hat = (hats_c[i % 4], 0.16 if pos == 2 else 0.07)
            elif mode == "eighth" and pos in (0, 2):
                hat = (hats_c[i % 4], 0.17 if pos == 2 else 0.1)
            elif mode == "sixteenth":
                hat = (hats_c[i % 4], 0.17 if pos == 2 else 0.1)
            elif mode == "open":
                hat = (hats_o[i % 2], 0.15) if pos == 2 else (hats_c[i % 4], 0.11)
        if hat is not None:
            place(DRUMS, t + r.uniform(0, 0.004), hat[0], hat[1] * r.uniform(0.85, 1.0), pan=0.25)
        # 비트크러시 글리치 퍼커션
        if mu.get("glitch") and pos != 0 and not resting(t) and r.random() < 0.28:
            place(DRUMS, t, blips[int(r.integers(0, 6))], 0.22, pan=r.uniform(-0.7, 0.7), send=0.1)

    # 스네어 롤: 점점 촘촘하게, 점점 크게
    for a, b in ROLLS:
        t = a
        while t < b - 1e-6:
            p = (t - a) / (b - a)
            step = BEAT / 2 if p < 0.35 else BEAT / 4 if p < 0.7 else BEAT / 8
            place(DRUMS, t, snare, 0.18 + 0.42 * p ** 1.3, pan=0.0, send=0.12)
            t += step


# ============================================================================ 베이스
_BASS_CACHE = {}


def bass_note(midi, dur, bright=1.0):
    key = (midi, round(dur, 4), round(bright, 2))
    if key in _BASS_CACHE:
        return _BASS_CACHE[key]
    n = ns(dur)
    t = tt(n)
    f = mtof(midi)
    x = 0.6 * saw(f, n) + 0.42 * np.sin(TWO_PI * f / 2 * t)
    fc = 180 + 2800 * bright * np.exp(-t / 0.055)
    y = onepole_tv(onepole_tv(x, fc), fc)
    env = np.minimum(1, t / 0.003) * np.exp(-t / max(dur * 0.8, 0.05))
    y = fade_edges(softclip(y * env * 1.4, 1.2), 0.001, 0.006)
    _BASS_CACHE[key] = y
    return y


def bass_long(midi, dur, fc0, fc1):
    n = ns(dur)
    t = tt(n)
    f = mtof(midi)
    x = 0.6 * saw(f, n) + 0.42 * np.sin(TWO_PI * f / 2 * t)
    fc = fc0 * (fc1 / fc0) ** (t / dur)
    y = onepole_tv(onepole_tv(x, fc), fc)
    return fade_edges(softclip(y * 1.2, 1.2), 0.01, 0.02)


def build_bass():
    total16 = int(round(DUR / S16))
    for i in range(total16):
        t = i * S16
        pos = i % 4
        if resting(t):
            continue
        mu = music_at(t)
        mode = mu.get("bass", "none")
        root = CHORDS[chord_at(t)][0]
        r = rng("bass", i)
        # 에너지가 높은 구간일수록 필터를 더 연다
        bright = 0.75 + 0.2 * min(1.0, mu.get("pad", 0.5))
        if mode == "offbeat" and pos == 2:
            place(BASS, t, bass_note(root, 0.22, 0.7), 0.55)
        elif mode == "eighth" and pos in (0, 2):
            place(BASS, t, bass_note(root + (12 if pos == 2 else 0), 0.22, round(bright, 2)), 0.5)
        elif mode == "sixteenth" and pos != 0:
            place(BASS, t, bass_note(root + (12 if pos == 2 else 0), 0.11, 1.0), 0.55)
        elif mode == "sync" and (pos == 2 or (pos == 3 and r.random() < 0.3)):
            place(BASS, t, bass_note(root, 0.18, 0.75), 0.5)
    # 빌드업: 길게 끄는 스웰 코드 근음, 필터가 열린다
    for k, sw in enumerate(SWELLS):
        place(BASS, sw["t"], bass_long(CHORDS[sw["chord"]][0], sw["dur"], 150 - 10 * k, 1800 + 800 * k), 0.5 + 0.05 * k)
    # 아웃트로 컷: 스탭마다 베이스 한 방
    for ev in EVENTS:
        if ev["kind"] == "cut":
            place(BASS, ev["t"], bass_note(CHORDS[chord_at(ev["t"])][0], 0.2, 1.0), 0.6)


# ============================================================================ 패드 · 드론
def supersaw(midis, n, key, detune=16, voices=7, spread=0.85):
    r = rng("ss", key)
    out = np.zeros((2, n))
    for m in midis:
        f0 = mtof(m)
        for v in range(voices):
            d = (v - (voices - 1) / 2) / ((voices - 1) / 2)
            s = saw(f0 * 2 ** (d * detune / 1200), n, r.random())
            gl, gr = pan_gains(d * spread)
            out[0] += s * gl
            out[1] += s * gr
    return out / np.sqrt(len(midis) * voices)


def build_pad():
    raw = new_bus()
    for k, (a, b, c) in enumerate(chord_segments()):
        n = ns(b - a + 0.6)
        x = supersaw(CHORDS[c][1], n, ("pad", k))
        t = tt(n)
        env = np.minimum(1, t / 0.09) * np.clip((b - a + 0.6 - t) / 0.6, 0, 1)
        place(raw, a, x * env)
    # 시간에 따라 열리는 필터: 고정 차단 주파수 몇 벌을 만들어 섞는다
    cutoff, gain = pad_curves()
    bank_f = [250, 600, 1400, 3200, 7500]
    bank = [fft_filter(raw, lp=f, order=2) for f in bank_f]
    lf = np.log(np.clip(cutoff, bank_f[0], bank_f[-1]))
    lb = np.log(bank_f)
    out = np.zeros_like(raw)
    for j in range(len(bank_f) - 1):
        w = np.clip((lf - lb[j]) / (lb[j + 1] - lb[j]), 0, 1)
        m = (lf >= lb[j]) & (lf <= lb[j + 1] + 1e-9)
        out[:, m] += bank[j][:, m] * (1 - w[m]) + bank[j + 1][:, m] * w[m]
    PAD[:] += out * gain
    REV[:] += out * gain * 0.28


def pad_cut(p):
    """music.pad(0~1) → 패드 저역 통과 차단 주파수. 0.25≈580 Hz, 0.5≈1.3 kHz, 0.6≈1.9 kHz, 1.0=7 kHz."""
    return 250 * (7000 / 250) ** p


def pad_gain(p):
    return 0.2 + 0.8 * p


def pad_target(t):
    """패드의 목표 (차단 주파수, 음량). 원본의 흐름을 규칙으로 옮겼다.
    - 킥이 없는 도입부(cold_open·title)는 구간 안에서 필터가 서서히 열린다. 맨 앞 1.6초는 음량이 0에서 올라온다.
    - 롤(빌드업) 동안 필터가 6.5 kHz 까지 열리고 음량이 0.9 까지 오른다.
    - bursts 는 최대(7.2 kHz, 1.0). final 임팩트 뒤로는 닫히며 사라진다."""
    if t >= FINAL_T:
        u = (t - FINAL_T)
        c = 6500 * (700 / 6500) ** min(1.0, u / max(0.5, DUR - 0.3 - FINAL_T))
        g = 0.95 if u < 0.1 else float(np.interp(u, [0.1, 1.0, DUR - 0.3 - FINAL_T, DUR - FINAL_T], [0.95, 0.6, 0.0, 0.0]))
        return c, g
    if in_ranges(t, BURSTS):
        return 7200.0, 1.0
    rl = range_at(t, ROLLS)
    if rl:
        a, b = rl
        base_c, base_g = pad_target(a - 1e-3)
        u = (t - a) / (b - a)
        return base_c * (6500 / base_c) ** u, base_g + (0.9 - base_g) * u
    sl = range_at(t, SILENCES)
    if sl:
        return 6500.0, 0.9
    name = section_at(t)
    s0, s1 = SEC[name]
    p = MUSIC[name].get("pad", 0.5)
    c, g = pad_cut(p), pad_gain(p)
    if name == "outro":
        return 6000.0, 0.9
    if not MUSIC[name].get("kick"):
        u = (t - s0) / (s1 - s0)
        c = pad_cut(p * (0.6 + 0.4 * u))
        g = pad_gain(p) * (0.85 + 0.15 * u)
    if t < 1.6:
        g *= t / 1.6
    return c, g


def pad_curves():
    step = 0.005
    grid = np.arange(0.0, DUR + step, step)
    vals = np.array([pad_target(float(x)) for x in grid])
    x = tt(N)
    cutoff = np.exp(np.interp(x, grid, np.log(vals[:, 0])))
    gain = np.interp(x, grid, vals[:, 1])
    return cutoff, gain


def build_drone():
    # 첫 킥이 들어오기 직전까지 깔리는 저음 드론
    end = KICK[0][0] if KICK else SEC[SECTIONS[1]["name"]][1]
    n = ns(end + 0.2)
    t = tt(n)
    lfo = 0.75 + 0.25 * np.sin(TWO_PI * 0.23 * t)
    x = (np.sin(TWO_PI * 55 * t) * 0.7 + np.sin(TWO_PI * 82.41 * t) * 0.35 + np.sin(TWO_PI * 110.2 * t) * 0.18) * lfo
    air = fft_filter(noise(n, "air"), lp=1800, hp=400) * 0.08 * (0.6 + 0.4 * np.sin(TWO_PI * 0.11 * t))
    env = np.clip(t / 1.4, 0, 1) * np.clip((end - 0.4 - t) / 1.2, 0, 1)
    st = np.vstack([x + air, x + np.roll(air, 331)]) * env
    place(DRONE, 0.0, st, 0.55, send=0.2)


# ============================================================================ 아르페지오 · 리드
def pluck(f, dur, kind):
    n = ns(dur)
    t = tt(n)
    if kind == "soft":
        x = 0.65 * np.sin(TWO_PI * f * t) + 0.35 * tri(f * 2, n)
        x *= np.exp(-t / 0.09)
    else:
        x = 0.6 * saw(f, n) + 0.4 * saw(f * 1.004, n, 0.3)
        x = onepole_tv(x, 900 + 6500 * np.exp(-t / 0.05))
        x *= np.exp(-t / 0.12)
    return fade_edges(x, 0.001, 0.01)


_PLUCK = {}


def cached_pluck(m, dur, kind):
    k = (m, dur, kind)
    if k not in _PLUCK:
        _PLUCK[k] = pluck(mtof(m), dur, kind)
    return _PLUCK[k]


def pingpong(bus, delay=0.375, fb=0.38, taps=5, lp=3600):
    d = ns(delay)
    mono = bus.mean(axis=0)
    wet = np.zeros_like(bus)
    for k in range(1, taps + 1):
        wet[(k + 1) % 2, k * d:] += mono[:-k * d] * fb ** k
    return fft_filter(wet, lp=lp, hp=250)


def build_arps():
    pat_soft = [0, 1, 2, 3, 2, 1, 2, 3]
    pat_lead = [0, 2, 4, 5, 3, 1, 4, 2, 0, 3, 5, 4, 2, 1, 3, 5]
    # 아르페지오가 새로 시작하는 곳: 첫 등장은 2초, 쉬었다 다시 나올 때는 0.5초에 걸쳐 들어온다
    starts, prev_on, first = [], False, True
    for s in SECTIONS:
        on = s.get("music", {}).get("arp", "none") != "none"
        if on and not prev_on:
            starts.append((s["start"], 2.0 if first else 0.5))
            first = False
        prev_on = on

    def arp_fade(t):
        f = 1.0
        for a, d in starts:
            if a <= t < a + d:
                f = (t - a) / d
        return f

    total16 = int(round(DUR / S16))
    for i in range(total16):
        t = i * S16
        if resting(t):
            continue
        c = CHORDS[chord_at(t)][1]
        mu = music_at(t)
        mode = mu.get("arp", "none")
        dev = mode == "half" and i % 2 == 0          # 8분음표로 절반만
        if mode == "soft" or dev:
            tones = [m + 12 for m in c] + [c[0] + 24]
            fade = 0.8 if dev else arp_fade(t)
            acc = 1.0 if i % 4 == 0 else 0.7
            place(ARP, t, cached_pluck(tones[pat_soft[i % 8]], 0.16, "soft"), 0.16 * fade * acc,
                  pan=-0.3 if i % 2 else 0.3, send=0.25)
        if mu.get("lead"):
            tones = [m + 12 for m in c] + [m + 24 for m in c]
            acc = 1.0 if i % 4 == 0 else 0.75
            place(LEAD, t, cached_pluck(tones[pat_lead[i % 16]], 0.15, "bright"), 0.2 * acc,
                  pan=0.2 if i % 2 else -0.2, send=0.2)
    ARP[:] += pingpong(ARP)
    LEAD[:] += pingpong(LEAD, fb=0.33)


# ============================================================================ 효과음
def key_click(i, space=False, burst=False):
    r = rng("key", i, burst)
    n = ns(0.09)
    t = tt(n)
    click = biquad(noise(n, "kc", i, burst) * np.exp(-t / 0.0012), "hp", 3200) * 0.8
    body = np.sin(TWO_PI * r.uniform(1900, 2800) * t) * np.exp(-t / 0.01) * 0.22
    f = (135 if space else r.uniform(185, 265)) * (1 + 0.6 * np.exp(-t / 0.006))
    thock = np.sin(TWO_PI * np.cumsum(f) / SR) * np.exp(-t / (0.045 if space else 0.024)) * (0.85 if space else 0.5)
    ret = np.zeros(n)
    j = ns(0.032 + r.uniform(0, 0.01))
    ret[j:] = biquad(noise(n - j, "kr", i, burst) * np.exp(-tt(n - j) / 0.0009), "hp", 4500) * 0.25
    return fade_edges(click + body + thock + ret)


def sfx_riser(dur, size):
    amp = {"small": 0.3, "mid": 0.45, "big": 0.75}.get(size, 0.45)
    n = ns(dur)
    t = tt(n)
    p = t / dur
    fc = 300 * (7000 / 300) ** p
    nl = svf(noise(n, "riserL", dur), fc, 2.0, "bp")
    nr = svf(noise(n, "riserR", dur), fc * 1.05, 2.0, "bp")
    ton = sine(180 * (1500 / 180) ** p, n) * 0.35 + saw(90 * (720 / 90) ** p, n) * 0.08
    # 강박 60ms 앞에서 끊어 짧은 틈을 만든다(드롭의 타격감)
    env = p ** 2.2 * np.clip((dur - 0.06 - t) / 0.02, 0, 1)
    st = np.vstack([nl * 1.6 + ton, nr * 1.6 + ton]) * env
    return fade_edges(st, 0.01, 0.003) * amp


def sfx_whoosh(key):
    """전환용 흡입 우시: 이벤트 시각부터 다음 강박 직전까지 부풀었다가 강박 40ms 앞에서 멈춘다."""
    dur = 0.25
    n = ns(dur)
    t = tt(n)
    p = t / dur
    fc = 500 * (4200 / 500) ** p
    x = svf(noise(n, "wh", key), fc, 1.1, "bp") * 2.6
    env = p ** 1.8 * np.clip((dur - 0.04 - t) / 0.015, 0, 1)
    x *= env
    pan = -0.9 + 1.8 * p
    gl, gr = pan_gains(pan)
    return np.vstack([x * gl, x * gr])


def sfx_impact(size):
    s = {"mid": (0.7, 0.8, 0.5, 0.4), "big": (1.2, 1.0, 0.7, 0.7),
         "huge": (1.9, 1.15, 0.9, 1.0), "final": (2.8, 1.15, 0.8, 1.3)}[size]
    decay, lvl, crack_l, tail_l = s
    n = ns(decay * 2.2)
    t = tt(n)
    f = 36 + (100 - 36) * np.exp(-t / 0.07)
    sub = np.sin(TWO_PI * np.cumsum(f) / SR) * np.exp(-t / decay) * lvl
    crack = biquad(noise(n, "crack", size) * np.exp(-t / 0.06), "hp", 1400) * crack_l
    body = tri(110, n) * np.exp(-t / 0.16) * 0.35
    tail = fft_filter(noise(n, "itail", size), lp=2200, hp=120) * np.exp(-t / (0.35 * tail_l)) * 0.35 * tail_l
    x = softclip(sub + crack + body, 1.4) + tail
    st = np.vstack([x, x + 0.15 * np.roll(tail, 97)])
    return fade_edges(st, 0.0005, 0.05)


def sfx_slam(k):
    n = ns(0.45)
    t = tt(n)
    f = 45 + (120 - 45) * np.exp(-t / 0.03)
    x = np.sin(TWO_PI * np.cumsum(f) / SR) * np.exp(-t / 0.2)
    x += biquad(noise(n, "slam", k) * np.exp(-t / 0.04), "hp", 1800) * 0.7
    x += pulse(220, n) * np.exp(-t / 0.05) * 0.18
    return fade_edges(softclip(x, 2.0))


def sfx_glitch():
    out = []
    r = rng("glitch")
    for k in range(6):
        n = ns(0.0625)
        f = r.choice([110, 220, 440, 880, 1320])
        x = saw(f, n)
        hold = int(r.integers(8, 28))
        x = np.repeat(x[::hold], hold)[:n]
        x = np.round(x * 5) / 5
        gate = (tt(n) < 0.045).astype(float)
        out.append(x * gate * (0.9 if k % 2 == 0 else 0.6))
    x = np.concatenate(out)
    lr = np.vstack([x * (1 - 0.5 * (np.arange(len(x)) // ns(0.0625) % 2)), x * (0.5 + 0.5 * (np.arange(len(x)) // ns(0.0625) % 2))])
    return fade_edges(lr)


PENTA = [0, 3, 5, 7, 10]


def penta(base, idx):
    return base + 12 * (idx // 5) + PENTA[idx % 5]


def blip(m, dur=0.1, harm=0.3, drop=0.4):
    n = ns(dur)
    t = tt(n)
    f = mtof(m) * (1 + drop * np.exp(-t / 0.004))
    ph = np.cumsum(f) / SR
    x = np.sin(TWO_PI * ph) + harm * np.sin(TWO_PI * 2 * ph)
    return fade_edges(x * np.exp(-t / (dur * 0.35)), 0.0008, 0.005)


def sfx_tick(k):
    n = ns(0.03)
    t = tt(n)
    x = np.sin(TWO_PI * 3300 * t) * np.exp(-t / 0.004) + biquad(noise(n, "tick", k), "hp", 5000) * np.exp(-t / 0.001) * 0.5
    return fade_edges(x)


def sfx_sweep():
    n = ns(1.6)
    t = tt(n)
    p = t / 1.6
    fc = 200 * (8000 / 200) ** p
    x = svf(noise(n, "sweep"), fc, 1.5, "lp")
    y = svf(noise(n, "sweep2"), fc * 0.9, 1.5, "lp")
    env = np.sin(np.pi * p) ** 1.5
    return fade_edges(np.vstack([x, y]) * env * 1.6)


def sfx_card(k):
    n = ns(0.15)
    t = tt(n)
    fc = 3200 * (1100 / 3200) ** (t / 0.15)
    x = svf(noise(n, "card", k), fc, 1.4, "bp") * np.exp(-t / 0.05) * 3.0
    return fade_edges(x)


def sfx_packet(k):
    r = rng("packet", k)
    n = ns(0.075)
    t = tt(n)
    f = r.uniform(800, 1100) * (3.0 ** (t / 0.075))
    x = pulse(f, n, 0.3)
    x = np.repeat(x[::6], 6)[:n]
    return fade_edges(x * np.exp(-t / 0.03)), r.uniform(-0.6, 0.6)


def two_note(m1, m2, gap, dur, kind="bright"):
    n = ns(gap + dur)
    x = np.zeros(n)
    for j, m in enumerate([m1, m2]):
        nn = ns(dur)
        tj = tt(nn)
        f = mtof(m)
        if kind == "bright":
            s = 0.7 * np.sin(TWO_PI * f * tj) + 0.3 * tri(f * 2, nn)
        else:
            s = biquad(pulse(f, nn, 0.4) + pulse(f * 1.01, nn, 0.4), "lp", 1400) * 0.6
        s *= np.exp(-tj / (dur * 0.45))
        i0 = ns(gap * j) if j else 0
        x[i0:i0 + nn] += fade_edges(s)[: n - i0]
    return x


def sfx_stamp(k):
    n = ns(0.5)
    t = tt(n)
    f = 45 + (95 - 45) * np.exp(-t / 0.02)
    x = np.sin(TWO_PI * np.cumsum(f) / SR) * np.exp(-t / 0.18)
    x += biquad(noise(n, "stamp", k) * np.exp(-t / 0.035), "bp", 900, 0.8) * 1.8
    x += biquad(noise(n, "stamp2", k) * np.exp(-t / 0.012), "hp", 3000) * 0.4
    return fade_edges(softclip(x, 1.6))


def sfx_counter(dur):
    n = ns(dur + 0.45)
    x = np.zeros(n)
    step = 0.036
    k = 0
    while k * step < dur:
        p = k * step / dur
        m = ns(0.02)
        tm = tt(m)
        s = np.sin(TWO_PI * (1900 + 1500 * p) * tm) * np.exp(-tm / 0.004) * (0.5 + 0.5 * p)
        i0 = ns(k * step)
        x[i0:i0 + m] += s[: n - i0]
        k += 1
    i0 = ns(dur)
    m = n - i0
    tm = tt(m)
    ding = (np.sin(TWO_PI * 1760 * tm) + 0.5 * np.sin(TWO_PI * 2640 * tm)) * np.exp(-tm / 0.12)
    x[i0:] += ding * 0.8
    return fade_edges(x)


def sfx_click():
    n = ns(0.08)
    x = np.zeros(n)
    for j, off in enumerate([0.0, 0.045]):
        i0 = ns(off) if off else 0
        m = ns(0.02)
        tm = tt(m)
        s = biquad(noise(m, "click", j), "hp", 3500) * np.exp(-tm / 0.0012) + np.sin(TWO_PI * 1500 * tm) * np.exp(-tm / 0.003) * 0.4
        x[i0:i0 + m] += s * (1.0 if j == 0 else 0.7)
    return fade_edges(x)


def sfx_crash():
    n = ns(2.2)
    t = tt(n)
    nz = noise(n, "crash")
    x = biquad(nz, "hp", 3200) * np.exp(-t / 0.9)
    x = x + 0.5 * np.roll(x, ns(0.0011)) + 0.3 * np.roll(x, ns(0.0023))
    y = biquad(noise(n, "crash2"), "hp", 3000) * np.exp(-t / 0.85)
    return fade_edges(np.vstack([x, y]) * 0.7, 0.0005, 0.1)


def sfx_panel(k):
    n = ns(0.24)
    t = tt(n)
    base = 330 * 2 ** (k / 4)
    f = base * (1 + 0.5 * t / 0.24)
    mod = np.sin(TWO_PI * f * 2.01 * t) * 1.5 * np.exp(-t / 0.08)
    x = np.sin(TWO_PI * np.cumsum(f) / SR + mod) * np.exp(-t / 0.1)
    x += biquad(noise(n, "panel", k), "hp", 6000) * np.exp(-t / 0.03) * 0.3
    return fade_edges(x)


def sfx_bell(m):
    n = ns(1.2)
    t = tt(n)
    f = mtof(m)
    x = sum(a * np.sin(TWO_PI * f * r * t) * np.exp(-t / d)
            for r, a, d in [(1, 1.0, 0.7), (2.0, 0.5, 0.45), (2.76, 0.35, 0.3), (5.4, 0.2, 0.15)])
    return fade_edges(x, 0.001, 0.05)


def sfx_boot():
    n = ns(0.75)
    t = tt(n)
    f = 200 * (900 / 200) ** np.clip(t / 0.5, 0, 1)
    x = np.sin(TWO_PI * np.cumsum(f) / SR + np.sin(TWO_PI * f * 1.5 * t) * 0.8) * np.clip((0.55 - t) / 0.05, 0, 1)
    for m in [69, 76, 81]:
        seg = blip(m, 0.25, 0.2, 0.0)
        i0 = ns(0.5)
        x[i0:i0 + len(seg)] += seg[: n - i0] * 0.5
    return fade_edges(x * 0.7)


def sfx_go():
    n = ns(3.0)
    t = tt(n)
    formants = [(800, 90, 1.0), (1150, 100, 0.55), (2900, 160, 0.25)]
    vib = 1 + 0.004 * np.sin(TWO_PI * 5.2 * t) * np.clip(t / 0.4, 0, 1)
    out = np.zeros((2, n))
    for mi, m in enumerate([45, 52, 57, 64, 69]):
        for v in range(3):
            f0 = mtof(m) * 2 ** ((v - 1) * 7 / 1200)
            ph = np.cumsum(f0 * vib) / SR
            x = np.zeros(n)
            k = 1
            while f0 * k < 5500:
                fk = f0 * k
                g = sum(a / (1 + ((fk - fc) / bw) ** 2) for fc, bw, a in formants) + 0.02
                x += g / k ** 0.6 * np.sin(TWO_PI * k * ph + k * v)
                k += 1
            gl, gr = pan_gains((v - 1) * 0.6 + (mi - 2) * 0.1)
            out[0] += x * gl
            out[1] += x * gr
    env = np.clip(t / 0.06, 0, 1) * (0.55 + 0.45 * np.exp(-t / 0.3)) * np.clip((3.0 - t) / 1.6, 0, 1)
    out = fft_filter(out * env, hp=90) / 9.0
    return fade_edges(out, 0.001, 0.05)


def sfx_stab(t_ev, k):
    c = CHORDS[chord_at(t_ev)][1]
    n = ns(0.2)
    x = supersaw([m + 12 for m in c] + [c[0]], n, ("stab", k), detune=22)
    t = tt(n)
    x = fft_filter(x, lp=5000) * np.exp(-t / 0.07)
    # 1/32 스터터
    g = (np.floor(t / (BEAT / 8)) % 2 == 0).astype(float) * 0.7 + 0.3
    return fade_edges(x * g * 1.6)


def sfx_shimmer(key):
    r = rng("shimmer", key)
    n = ns(1.8)
    out = np.zeros((2, n))
    for _ in range(46):
        m = penta(88, int(r.integers(0, 12)))
        s = blip(m, r.uniform(0.25, 0.5), 0.1, 0.0)
        i0 = ns(r.uniform(0, 1.0))
        gl, gr = pan_gains(r.uniform(-0.9, 0.9))
        ln = min(len(s), n - i0)
        out[0, i0:i0 + ln] += s[:ln] * gl
        out[1, i0:i0 + ln] += s[:ln] * gr
    return out * np.clip(1 - tt(n) / 1.8, 0, 1) * 0.35


def sfx_file(idx):
    """파일 저장·복사: 부드럽게 위로 휘는 짧은 블립 두 개와 종이 스치는 듯한 아주 짧은 틱."""
    n = ns(0.16)
    t = tt(n)
    x = np.zeros(n)
    for j, (m, g, off) in enumerate([(penta(76, idx % 7), 1.0, 0.0), (penta(76, idx % 7) + 7, 0.45, 0.045)]):
        i0 = ns(off) if off else 0
        m_n = n - i0
        tj = tt(m_n)
        f = mtof(m) * (1 + 0.1 * (1 - np.exp(-tj / 0.02)))
        s = np.sin(TWO_PI * np.cumsum(f) / SR) * np.exp(-tj / 0.03)
        x[i0:] += s * g
    x += biquad(noise(n, "file", idx), "hp", 5500) * np.exp(-t / 0.0025) * 0.18
    return fade_edges(x, 0.001, 0.01)


def sfx_modal():
    """대화상자 열림: 아래에서 올라오는 부드러운 두 음 스웰 + 약한 흡입 바람."""
    n = ns(0.45)
    t = tt(n)
    x = np.zeros(n)
    for m, off, g in [(69, 0.0, 0.8), (76, 0.1, 0.6)]:
        i0 = ns(off) if off else 0
        tm = tt(n - i0)
        f = mtof(m)
        s = (0.75 * np.sin(TWO_PI * f * tm) + 0.25 * tri(f * 2, n - i0))
        env = np.clip(tm / 0.06, 0, 1) * np.exp(-tm / 0.16)
        x[i0:] += s * env * g
    p = t / 0.45
    air = svf(noise(n, "modal"), 400 * (3000 / 400) ** np.clip(p / 0.7, 0, 1), 1.2, "bp")
    air *= np.clip(p / 0.6, 0, 1) ** 1.5 * np.clip((0.45 - t) / 0.1, 0, 1) * 0.9
    st = np.vstack([x + air, x + np.roll(air, 211)])
    return fade_edges(st, 0.004, 0.02)


def sfx_scan(dur):
    """3D 스캔: 위로 훑는 대역 통과 필터 스윕 + 가는 사인 톤. 작게 깔린다."""
    n = ns(dur)
    t = tt(n)
    p = t / dur
    fc = 400 * (6000 / 400) ** p
    nl = svf(noise(n, "scanL", dur), fc, 3.0, "bp")
    nr = svf(noise(n, "scanR", dur), fc * 1.04, 3.0, "bp")
    tone = sine(800 * (2400 / 800) ** p, n) * 0.18
    # 스캔 줄이 지나가는 느낌: 30 Hz 로 살짝 떨리는 진폭
    trem = 0.8 + 0.2 * np.sin(TWO_PI * 30 * t)
    env = np.sin(np.pi * p) ** 0.8 * trem
    st = np.vstack([(nl * 1.3 + tone) * env, (nr * 1.3 + tone) * env])
    return fade_edges(st, 0.01, 0.03)


def build_sfx():
    for i, ev in enumerate(EVENTS):
        k, t = ev["kind"], ev["t"]
        idx = ev.get("idx", 0)
        if k == "key":
            place(SFX, t, key_click(i, ev.get("space", False)), 0.55,
                  pan=-0.35 + 0.7 * (i % 30) / 29, send=0.05)
        elif k == "enter":
            n = ns(0.2)
            tm = tt(n)
            x = np.sin(TWO_PI * np.cumsum(105 * (1 + 0.8 * np.exp(-tm / 0.008))) / SR) * np.exp(-tm / 0.06)
            kc = key_click(999, True)
            x[: len(kc)] += kc * 0.8
            x += np.sin(TWO_PI * 1250 * tm) * np.exp(-tm / 0.04) * 0.2
            place(SFX, t, fade_edges(x), 0.85, send=0.12)
        elif k == "riser":
            place(SFX, t, sfx_riser(ev.get("dur", 1.0), ev.get("size", "mid")), 0.7, send=0.3)
        elif k == "whoosh":
            place(SFX, t, sfx_whoosh(i), 0.5, send=0.2)
        elif k == "impact":
            size = ev.get("size", "mid")
            place(SFX, t, sfx_impact(size), {"mid": 0.7, "big": 0.85, "huge": 1.0, "final": 1.0}[size],
                  send={"mid": 0.25, "big": 0.35, "huge": 0.45, "final": 0.55}[size])
        elif k == "slam":
            place(SFX, t, sfx_slam(i), 0.65, send=0.15)
        elif k == "glitch":
            place(SFX, t, sfx_glitch(), 0.4, send=0.1)
        elif k == "pop":
            place(SFX, t, blip(penta(69, idx), 0.11), 0.28, pan=((idx * 7) % 15) / 7 - 1, send=0.3)
        elif k == "tick":
            place(SFX, t, sfx_tick(i), 0.2, pan=rng("tickpan", i).uniform(-0.4, 0.4))
        elif k == "sweep":
            place(SFX, t, sfx_sweep(), 0.35, send=0.3)
        elif k == "card":
            place(SFX, t, sfx_card(i), 0.4, pan=-0.6 + 0.3 * (idx % 5), send=0.1)
        elif k == "packet":
            x, pn = sfx_packet(i)
            place(SFX, t, x, 0.16, pan=pn, send=0.15)
        elif k == "confirm":
            place(SFX, t, two_note(76, 81, 0.07, 0.14), 0.3, send=0.25)
        elif k == "error":
            place(SFX, t, two_note(60, 56, 0.1, 0.14, "dark"), 0.4, send=0.15)
        elif k == "stamp":
            place(SFX, t, sfx_stamp(i), 0.75, send=0.25)
        elif k == "chip":
            place(SFX, t, blip(penta(81, idx % 10), 0.04, 0.1, 0.2), 0.16, pan=0.4 if idx % 2 else -0.4, send=0.1)
        elif k == "counter":
            place(SFX, t, sfx_counter(ev.get("dur", 1.0)), 0.22, send=0.15)
        elif k == "click":
            place(SFX, t, sfx_click(), 0.45)
        elif k == "drop":
            place(SFX, t, sfx_crash(), 0.45, send=0.35)
        elif k == "panel":
            place(SFX, t, sfx_panel(idx), 0.28, pan=[-0.6, -0.2, 0.2, 0.6][idx % 4], send=0.25)
        elif k == "qa_pass":
            place(SFX, t, sfx_bell([81, 84, 88, 93][idx % 4]), 0.2, pan=[-0.5, -0.15, 0.15, 0.5][idx % 4], send=0.45)
        elif k == "boot":
            place(SFX, t, sfx_boot(), 0.4, send=0.3)
        elif k == "type_burst":
            for j in range(12):
                place(SFX, t + j * 0.033 + rng("tb", j).uniform(0, 0.008), key_click(2000 + j, False, True),
                      0.4, pan=rng("tbp", j).uniform(-0.3, 0.3), send=0.05)
        elif k == "check":
            place(SFX, t, blip(penta(76, idx), 0.14, 0.35, 0.3), 0.33, send=0.25)
        elif k == "go":
            place(SFX, t, sfx_go(), 0.62, send=0.5)
            place(SFX, t, sfx_crash(), 0.4, send=0.3)
        elif k == "cut":
            place(SFX, t, sfx_stab(t, idx), 0.42, send=0.2)
        elif k == "shimmer":
            place(SFX, t, sfx_shimmer(i), 0.5, send=0.7)
        elif k == "file":
            place(SFX, t, sfx_file(idx), 0.22, pan=[-0.4, -0.15, 0.15, 0.4][idx % 4], send=0.2)
        elif k == "modal":
            place(SFX, t, sfx_modal(), 0.32, send=0.35)
        elif k == "scan":
            place(SFX, t, sfx_scan(ev.get("dur", 1.5)), 0.12, send=0.3)
        else:
            print(f"  경고: 모르는 효과음 종류 '{k}' @ {t}")


# ============================================================================ 리버브 · 사이드체인 · 믹스
def make_ir(seconds=2.6):
    n = ns(seconds)
    t = tt(n)
    nz = rng("ir").standard_normal((2, n))
    low = fft_filter(nz, lp=500)
    mid = fft_filter(nz, hp=500, lp=4000)
    high = fft_filter(nz, hp=4000)
    ir = low * np.exp(-t / 0.42) + mid * np.exp(-t / 0.34) + high * np.exp(-t / 0.16)
    ir *= np.clip(t / 0.01, 0, 1)
    pre = ns(0.022)
    ir = np.concatenate([np.zeros((2, pre)), ir[:, : n - pre]], axis=1)
    for d, g in [(0.011, 0.5), (0.017, 0.4), (0.023, 0.35), (0.031, 0.3)]:
        ir[0, ns(d)] += g
        ir[1, ns(d * 1.13)] += g
    return ir / np.sqrt((ir ** 2).sum(axis=1, keepdims=True))


def convolve(x, ir):
    n = x.shape[1] + ir.shape[1]
    nfft = 1 << (n - 1).bit_length()
    out = np.fft.irfft(np.fft.rfft(x, nfft, axis=1) * np.fft.rfft(ir, nfft, axis=1), nfft, axis=1)
    return out[:, : x.shape[1]]


def duck_curve(depth, release=0.24, attack=0.004):
    g = np.ones(N)
    L = ns(attack + release)
    tl = tt(L)
    shape = np.where(tl < attack, tl / attack, np.clip(1 - (tl - attack) / release, 0, 1) ** 2)
    for tk in KICKS:
        i0 = int(round(tk * SR))
        n = min(L, N - i0)
        if n > 0:
            g[i0:i0 + n] = np.minimum(g[i0:i0 + n], 1 - depth * shape[:n])
    return g


def silence_gates():
    """timeline 의 silences: 완전한 정적(흡입). 끝나는 순간의 임팩트는 곧바로 살아난다."""
    g = np.ones(N)
    for a, b in SILENCES:
        ia, ib = int(round(a * SR)), int(round(b * SR))
        fo = ns(0.012)
        g[ia - fo:ia] = np.minimum(g[ia - fo:ia], np.linspace(1, 0, fo))
        g[ia:ib] = 0
        fi = ns(0.002)
        g[ib:ib + fi] = np.linspace(0, 1, fi)
    return g


FADE_START, SILENT_FROM = DUR - 1.1, DUR - 0.3   # 120초 기준 118.9 → 119.7


def master_fade():
    t = tt(N)
    return np.clip(1 - (t - FADE_START) / (SILENT_FROM - FADE_START), 0, 1) ** 2


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)


def mix():
    duck_b = duck_curve(0.7)
    duck_p = duck_curve(0.6, release=0.3)
    duck_a = duck_curve(0.35)
    wet = convolve(REV, make_ir()) * 0.7
    music = DRUMS * 0.5 + BASS * duck_b * 0.9 + PAD * duck_p * 0.55 + ARP * duck_a * 2.2 + LEAD * duck_a * 2.6 + DRONE
    full = music + SFX * 1.0 + wet
    full = fft_filter(full, hp=34, order=2)
    full = full + fft_filter(full, hp=3500, order=1) * 0.45   # 고역 셸프(약 +3 dB): 밝기와 명료도
    full *= silence_gates() * master_fade()
    full[:, ns(SILENT_FROM):] = 0.0
    # 구간별 스템 음량(점검용)
    report = {}
    for name, s0, s1 in [(s["name"], s["start"], s["end"]) for s in SECTIONS]:
        a, b = ns(s0), ns(s1)
        report[name] = {k: round(rms_db(v[:, a:b]), 1) for k, v in
                        [("drums", DRUMS * 0.5), ("bass", BASS * duck_b * 0.9), ("pad", PAD * duck_p * 0.55),
                         ("arp", ARP * 2.2 + LEAD * 2.6), ("sfx", SFX), ("wet", wet), ("full", full)]}
    return full, report


# ============================================================================ 파일 쓰기 · 마스터링
def write_wav(path, x, peak=None):
    x = np.asarray(x, dtype=np.float64)
    if peak is not None:
        x = x / (np.max(np.abs(x)) + 1e-12) * peak
    x = np.clip(x, -1.0, 1.0)
    pcm = np.round(x.T * (2 ** 23 - 1)).astype(np.int32)
    b = pcm.astype("<i4").tobytes()
    b3 = bytearray()
    raw = np.frombuffer(b, dtype=np.uint8).reshape(-1, 4)[:, :3]
    b3 = raw.tobytes()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(3)
        w.setframerate(SR)
        w.writeframes(b3)


def read_wav(path):
    with wave.open(str(path), "rb") as w:
        n, ch, sw = w.getnframes(), w.getnchannels(), w.getsampwidth()
        raw = np.frombuffer(w.readframes(n), dtype=np.uint8)
    if sw == 3:
        a = raw.reshape(-1, 3)
        v = (a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8) | (a[:, 2].astype(np.int32) << 16))
        v = np.where(v >= 2 ** 23, v - 2 ** 24, v) / (2 ** 23 - 1)
    else:
        v = np.frombuffer(raw.tobytes(), dtype="<i2") / 32767.0
    return v.reshape(-1, ch).T


def measure(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True)
    txt = r.stderr[r.stderr.rfind("Summary:"):]
    I = float(re.search(r"I:\s+(-?[\d.]+) LUFS", txt).group(1))
    LRA = float(re.search(r"LRA:\s+([\d.]+) LU", txt).group(1))
    tp = float(re.search(r"True peak:\s+Peak:\s+(-?[\d.]+|-inf) dBFS", txt, re.S).group(1))
    return I, tp, LRA


def master(pre, out):
    I0, tp0, _ = measure(pre)
    gain = TARGET_LUFS - I0
    limit_db = -1.4
    I = tp = lra = None
    for it in range(7):
        af = (f"volume={gain:.3f}dB,alimiter=limit={10 ** (limit_db / 20):.5f}:attack=2:release=60:"
              f"level=false:latency=true,apad=whole_len={N},atrim=end_sample={N}")
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(pre), "-af", af,
                        "-ar", str(SR), "-c:a", "pcm_s24le", str(out)], check=True)
        I, tp, lra = measure(out)
        print(f"  마스터링 {it + 1}회: gain {gain:+.2f} dB, limit {limit_db:.1f} dB → I {I:.2f} LUFS, TP {tp:.2f} dBTP")
        ok_i = abs(I - TARGET_LUFS) <= 0.3
        ok_tp = tp <= TP_CEIL
        if ok_i and ok_tp:
            break
        if not ok_tp:
            limit_db -= max(0.2, tp - TP_CEIL + 0.1)
        if not ok_i:
            gain += (TARGET_LUFS - I) * 1.1
    return I, tp, lra


def sync_report(path):
    x = read_wav(path)
    mono = np.abs(x).max(axis=0)
    win = ns(0.01)

    def env_db(a, b):
        seg = mono[ns(a):ns(b)]
        return 20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9) if len(seg) else -120

    def onset(t, search=0.05, thr_db=-30):
        seg = mono[ns(t - search):ns(t + search)]
        thr = 10 ** (thr_db / 20) * mono.max()
        idx = np.argmax(seg > thr)
        return round(t - search + idx / SR, 4)

    rep = {}
    for e in BIG_IMPACTS:
        t = e["t"]
        rep[f"impact@{t}"] = {"size": e["size"], "before_db": round(env_db(t - 0.06, t - 0.005), 1),
                              "after_db": round(env_db(t, t + 0.06), 1)}
    for a, b in SILENCES:
        rep[f"silence_{a + 0.015:.2f}-{b - 0.005:.2f}_db"] = round(env_db(a + 0.015, b - 0.005), 1)
        rep[f"onset_{b}"] = onset(b, 0.1)
    rep[f"last_{DUR - SILENT_FROM:.1f}s_db"] = round(env_db(SILENT_FROM, DUR), 1)
    rep["samples"] = x.shape[1]
    return rep


def wave_png(wav, png):
    """어두운 배경 파형 + 구간 경계(흰 눈금) + 주요 임팩트(주황) + 정적 구간(붉은 띠)."""
    w, h = 1920, 300
    fx = [f"drawbox=x={int(a / DUR * w)}:y=0:w={max(2, int((b - a) / DUR * w))}:h={h}:color=0xFF5E62@0.45:t=fill"
          for a, b in SILENCES]
    fx += [f"drawbox=x={int(e['t'] / DUR * w)}:y=0:w=2:h={h}:color=0xFFB938@0.95:t=fill" for e in BIG_IMPACTS]
    fx += [f"drawbox=x={int(s['start'] / DUR * w)}:y=0:w=2:h=22:color=white@0.9:t=fill" for s in SECTIONS]
    fx += [f"drawbox=x={int(k / DUR * w)}:y={h - 10}:w=1:h=10:color=white@0.5:t=fill" for k in range(0, int(DUR) + 1, 2)]
    filt = (f"color=c=0x0B0D12:s={w}x{h}[bg];[0:a]showwavespic=s={w}x{h}:split_channels=0:scale=sqrt:colors=0x2EE6FF[wv];"
            f"[bg][wv]overlay=format=auto," + ",".join(fx))
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(wav),
                    "-filter_complex", filt, "-frames:v", "1", str(png)], check=True)


def main():
    import time
    t0 = time.time()
    build_drone()
    build_drums()
    build_bass()
    build_pad()
    build_arps()
    build_sfx()
    full, report = mix()
    print(f"합성 {time.time() - t0:.1f}초")
    for k, v in report.items():
        print(f"  {k:10s} {v}")
    pre = HERE / "pre_master.wav"
    write_wav(pre, full, peak=0.89)
    if "--no-master" in sys.argv:
        return
    out = HERE / "soundtrack.wav"
    I, tp, lra = master(pre, out)
    rep = sync_report(out)
    wave_png(out, HERE / "soundtrack_wave.png")
    summary = {"integrated_lufs": I, "true_peak_dbtp": tp, "lra": lra, "sync": rep,
               "duration_s": rep["samples"] / SR, "render_s": round(time.time() - t0, 1)}
    (HERE / "soundtrack_report.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
