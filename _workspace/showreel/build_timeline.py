"""쇼릴 큐 시트: 화면(index.html)과 소리(audio/synth.py)가 같은 시간표를 쓰게 한다.

실행하면 timeline.json(오디오용)과 cues.js(화면용, window.CUES)를 만든다.
시간 단위는 초. 120 BPM → 1박 0.5초, 1마디 2초, 60초 = 30마디.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
BPM = 120
BEAT = 60 / BPM
DUR = 60.0

PROMPT = "무너지는 금고에서 코인을 모아 탈출하는 웹게임 만들어줘"
TYPE_START, TYPE_END = 0.55, 2.95

# 장면: 이름, 시작, 끝, 에너지(0~1, 음악 편곡 참고), 색
SECTIONS = [
    ("cold_open", 0.0, 4.0, 0.15, "#C8FF3D"),
    ("title", 4.0, 8.0, 0.55, "#FFFFFF"),
    ("team", 8.0, 14.0, 0.65, "#9D7BFF"),
    ("plan", 14.0, 22.0, 0.70, "#9D7BFF"),
    ("spec", 22.0, 26.0, 0.75, "#FFB938"),
    ("produce", 26.0, 36.0, 1.00, "#2EE6FF"),
    ("develop", 36.0, 46.0, 0.85, "#C8FF3D"),
    ("release", 46.0, 52.0, 0.90, "#FF5E62"),
    ("outro", 52.0, 60.0, 0.80, "#FFFFFF"),
]


def typing_times():
    n = len(PROMPT)
    out = []
    for i, ch in enumerate(PROMPT):
        # 사람 손처럼 약간 흔들리는 간격(결정적). 공백 뒤는 조금 길게.
        base = TYPE_START + (TYPE_END - TYPE_START) * i / (n - 1)
        jitter = ((i * 37) % 11 - 5) * 0.006
        out.append(round(base + jitter + (0.02 if ch == " " else 0), 3))
    return out


def events():
    ev = []
    add = lambda t, kind, **kw: ev.append(dict(t=round(t, 3), kind=kind, **kw))
    # 콜드 오픈: 타자, 엔터, 선이 뻗어 나가는 소리
    for i, t in enumerate(typing_times()):
        add(t, "key", ch=PROMPT[i], space=PROMPT[i] == " ")
    add(3.45, "enter")
    add(3.5, "riser", dur=0.5, size="small")
    add(3.75, "whoosh")
    # 타이틀: 단어가 박힐 때마다 강타
    add(4.0, "impact", size="big")
    add(4.0, "slam")
    add(5.0, "slam")
    add(6.0, "slam")
    add(6.0, "glitch")
    add(6.5, "riser", dur=1.5, size="mid")
    add(7.0, "shimmer")
    add(7.75, "whoosh")
    # 팀: 노드 15개가 16분음표마다 튀어나온다
    for k in range(15):
        add(8.0 + k * BEAT / 4, "pop", idx=k)
    add(8.0, "impact", size="mid")
    for k in range(8):
        add(10.0 + k * 0.25, "tick")
    add(12.0, "sweep")
    add(13.75, "whoosh")
    # 기획
    add(14.0, "impact", size="mid")
    for k in range(5):
        add(16.0 + k * 0.25, "card", idx=k)
    for k, t in enumerate([18.0, 18.5, 19.0, 19.5, 18.25, 18.75, 19.25]):
        add(t, "packet", idx=k)
    add(19.5, "confirm")
    add(20.5, "error")
    add(21.0, "confirm")
    add(21.25, "stamp")
    add(21.75, "whoosh")
    # 명세·승인
    add(22.0, "impact", size="mid")
    for k in range(12):
        add(22.4 + k * 0.09, "chip", idx=k)
    add(23.5, "counter", dur=1.3)
    add(25.0, "click")
    add(25.2, "stamp")
    add(24.0, "riser", dur=2.0, size="big")
    # 제작(드롭)
    add(26.0, "impact", size="huge")
    add(26.0, "drop")
    for k, t in enumerate([28.0, 28.5, 29.0, 29.5]):
        add(t, "panel", idx=k)
    for k, t in enumerate([32.0, 32.25, 32.5, 32.75]):
        add(t, "qa_pass", idx=k)
    for k in range(10):
        add(34.0 + k * 0.15, "tick")
    add(35.75, "whoosh")
    # 개발·QA
    add(36.0, "impact", size="mid")
    add(38.0, "boot")
    add(40.0, "error")
    add(40.5, "packet", idx=99)
    add(41.0, "type_burst")
    add(41.5, "stamp")
    for k in range(5):
        add(42.0 + k * 0.6, "confirm", idx=k)
    add(45.75, "whoosh")
    # 출시 판정
    add(46.0, "impact", size="mid")
    for k in range(4):
        add(46.25 + k * 0.4, "card", idx=k)
    for k in range(6):
        add(48.0 + k * BEAT * 2 / 3, "check", idx=k)
    add(49.0, "riser", dur=1.5, size="big")
    add(50.5, "impact", size="huge")
    add(50.5, "go")
    add(51.75, "whoosh")
    # 아웃트로
    for k in range(8):
        add(52.0 + k * 0.25, "cut", idx=k)
    add(54.0, "impact", size="big")
    add(56.0, "shimmer")
    add(58.0, "impact", size="final")
    ev.sort(key=lambda e: e["t"])
    return ev


def main():
    data = {
        "bpm": BPM, "beat": BEAT, "duration": DUR,
        "prompt": PROMPT, "typing": typing_times(),
        "sections": [dict(name=n, start=s, end=e, energy=en, color=c) for n, s, e, en, c in SECTIONS],
        "events": events(),
    }
    (HERE / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "cues.js").write_text("window.CUES = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"events {len(data['events'])}, sections {len(SECTIONS)}")


if __name__ == "__main__":
    main()
