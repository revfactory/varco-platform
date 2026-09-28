"""2분 제작 과정 영상의 큐 시트: 화면(index.html)과 소리(audio/synth.py)가 같은 시간표를 쓴다.

실행하면 timeline.json(오디오용)과 cues.js(화면용, window.CUES)를 만든다.
시간 단위는 초. 120 BPM → 1박 0.5초, 1마디 2초, 120초 = 60마디. 장면 경계는 모두 마디 위에 둔다.
이벤트 시각은 장면 시작 기준 상대 시각으로 적어서, 장면 길이를 바꿔도 소리와 화면이 함께 움직인다.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
BPM = 120
BEAT = 60 / BPM
DUR = 120.0

PROMPT = "무너지는 금고에서 코인을 모아 탈출하는 웹게임 만들어줘"
TYPE_START, TYPE_END = 0.55, 2.95

# 장면: 이름, 시작, 끝, 에너지(0~1), 색, 음악 편성
#   kick 4박 킥 · clap 2·4박 박수 · hats none|light|eighth|sixteenth|open · bass none|offbeat|eighth|sixteenth|sync
#   arp none|soft|half · lead 밝은 리드 아르페지오 · glitch 비트크러시 타악 · pad 패드 밝기(0~1)
SECTIONS = [
    ("cold_open", 0.0, 4.0, 0.15, "#C8FF3D", dict(pad=0.25, drone=True)),
    ("title", 4.0, 10.0, 0.55, "#FFFFFF", dict(pad=0.6)),
    ("overview", 10.0, 18.0, 0.55, "#9D7BFF", dict(kick=True, hats="offbeat", bass="offbeat", arp="soft", pad=0.5)),
    ("prep", 18.0, 24.0, 0.6, "#E6E8EE", dict(kick=True, hats="light", bass="eighth", arp="soft", pad=0.5)),
    ("plan", 24.0, 44.0, 0.7, "#9D7BFF", dict(kick=True, clap=True, hats="sixteenth", bass="eighth", arp="soft", pad=0.55)),
    ("spec", 44.0, 58.0, 0.75, "#FFB938", dict(kick=True, clap=True, hats="sixteenth", bass="eighth", arp="none", pad=0.6)),
    ("produce", 58.0, 78.0, 1.0, "#2EE6FF", dict(kick=True, clap=True, hats="open", bass="sixteenth", lead=True, pad=1.0)),
    ("develop", 78.0, 96.0, 0.85, "#C8FF3D", dict(kick=True, clap=True, hats="sixteenth", bass="sync", arp="half", glitch=True, pad=0.55)),
    ("release", 96.0, 106.0, 0.9, "#FF5E62", dict(kick=True, clap=True, hats="sixteenth", bass="eighth", arp="none", pad=0.6)),
    ("deliver", 106.0, 112.0, 0.8, "#E6E8EE", dict(kick=True, clap=True, hats="eighth", bass="eighth", arp="soft", pad=0.7)),
    ("outro", 112.0, 120.0, 0.8, "#FFFFFF", dict(pad=0.9)),
]
SEC = {n: (s, e) for n, s, e, *_ in SECTIONS}

# 빌드업(스네어 롤과 필터가 열리는 베이스), 흡입 정적, 킥이 도는 구간, 출시 직후 폭발 구간
ROLLS = [(56.0, 57.75), (102.0, 103.75)]
SWELLS = [dict(t=56.0, dur=1.75, chord="G"), dict(t=102.0, dur=1.75, chord="F")]
SILENCES = [(57.75, 58.0), (103.75, 104.0)]
BURSTS = [(104.0, 106.0), (114.0, 118.0)]      # produce 처럼 꽉 찬 편성으로 치는 구간
KICK = [(10.0, 56.0), (58.0, 102.0), (104.0, 112.0), (114.0, 118.0)]

# 화면 아래 자막(해설). 장면 기준 상대 시각
CAPTIONS = [
    ("overview", 0.6, 4.2, "아이디어 한 줄을 받으면 에이전트 15명이 다섯 단계로 나눠 게임을 만듭니다."),
    ("overview", 4.4, 7.8, "중간에 두 번 멈추고 사람에게 묻습니다. 방향을 정할 때와 크레딧을 쓸 때입니다."),
    ("prep", 0.4, 3.2, "리더 에이전트가 먼저 게임 이름과 엔진, 번역할 언어를 정합니다."),
    ("prep", 3.3, 5.8, "VARCO 키가 있는지 확인합니다. 키가 없으면 드라이런으로 진행합니다."),
    ("plan", 0.4, 3.0, "게임 디렉터가 아이디어를 컨셉 문서로 구체화합니다."),
    ("plan", 3.2, 6.0, "첫 번째 확인: 핵심 결정 세 가지를 보여 주고 이대로 갈지 묻습니다."),
    ("plan", 6.2, 9.8, "시스템·시나리오·레벨·UI·밸런스 담당 다섯 명이 동시에 기획을 시작합니다."),
    ("plan", 10.0, 13.8, "밸런스 분석가가 시뮬레이션으로 수치를 검증하고, 시스템 기획자가 표를 고칩니다."),
    ("plan", 14.0, 16.4, "디렉터가 문서끼리 어긋난 곳을 찾아 정리하고 GDD 한 권으로 묶습니다."),
    ("plan", 16.6, 19.8, "기획을 동결하고, 확정한 문서와 데이터만 games 폴더로 옮깁니다."),
    ("spec", 0.4, 3.8, "에셋 프로듀서가 기획 문서에서 에셋 25개를 뽑고 VARCO API 호출 순서를 정합니다."),
    ("spec", 4.0, 7.2, "리더가 검사 스크립트로 매니페스트를 확인하고 크레딧 견적을 냅니다."),
    ("spec", 7.4, 10.6, "두 번째 확인: 크레딧을 쓰기 전에 견적을 보여 주고 승인을 받습니다."),
    ("spec", 10.8, 13.6, "예산은 견적에 여유 10%를 더한 1,364 크레딧으로 정했습니다."),
    ("produce", 2.1, 4.3, "사운드 디자이너가 효과음을 만들고 변형 네 개를 더 뽑습니다."),
    ("produce", 4.4, 6.7, "보이스 디렉터는 캐릭터마다 화자를 골라 대사 음성과 입 모양 애니메이션을 만듭니다."),
    ("produce", 6.8, 9.1, "비주얼 아티스트는 이미지 한 장으로 3D 모델을 만듭니다."),
    ("produce", 9.2, 11.8, "현지화 담당은 용어집을 지키며 영어와 일본어로 번역합니다."),
    ("produce", 11.9, 13.9, "워크플로 스크립트가 에셋마다 제작과 검증을 동시에 돌립니다."),
    ("produce", 14.2, 17.3, "에셋 QA가 결과물을 하나씩 측정하고, 고칠 수 있는 실패는 한 번 다시 만듭니다."),
    ("produce", 17.5, 19.8, "모든 호출은 장부에 남고, 예산을 넘는 호출은 보내지 않습니다."),
    ("develop", 0.3, 3.8, "엔지니어가 모듈 계획을 세우는 동안 QA는 GDD로 테스트 계획을 씁니다."),
    ("develop", 4.0, 7.8, "모듈을 끝낼 때마다 QA가 브라우저에서 직접 실행해 확인합니다."),
    ("develop", 8.0, 10.6, "코인 하나에 점수가 두 번 오르는 버그를 찾아 엔지니어에게 보냅니다."),
    ("develop", 10.8, 14.2, "엔지니어가 고치면 QA가 다시 확인하고 다음 모듈로 넘어갑니다."),
    ("develop", 14.4, 17.8, "모듈 다섯 개가 모두 통과하면 빌드를 동결합니다."),
    ("release", 0.3, 3.6, "에셋 감사, 회귀 테스트, 밸런스 대조, 스토어 이미지를 동시에 진행합니다."),
    ("release", 3.8, 7.3, "게임 디렉터가 기준 여섯 가지로 출시 여부를 판정합니다."),
    ("deliver", 0.3, 2.9, "결과물은 games/coin-runner 에 모이고, 작업 기록은 _workspace 에 남습니다."),
    ("deliver", 3.0, 5.8, "고칠 곳이 생기면 필요한 단계만 다시 돌립니다."),
]


def typing_times():
    n = len(PROMPT)
    out = []
    for i, ch in enumerate(PROMPT):
        base = TYPE_START + (TYPE_END - TYPE_START) * i / (n - 1)
        jitter = ((i * 37) % 11 - 5) * 0.006
        out.append(round(base + jitter + (0.02 if ch == " " else 0), 3))
    return out


def events():
    ev = []

    def add(sec, lt, kind, **kw):
        t = SEC[sec][0] + lt if sec else lt
        ev.append(dict(t=round(t, 3), kind=kind, **kw))

    # 콜드 오픈
    for i, t in enumerate(typing_times()):
        add(None, t, "key", ch=PROMPT[i], space=PROMPT[i] == " ")
    add(None, 3.45, "enter")
    add(None, 3.5, "riser", dur=0.5, size="small")
    add(None, 3.75, "whoosh")
    # 타이틀
    add("title", 0.0, "impact", size="big")
    add("title", 0.0, "slam")
    add("title", 1.0, "slam")
    add("title", 2.0, "glitch")
    add("title", 2.35, "shimmer")
    add("title", 3.2, "chip", idx=3)
    add("title", 4.0, "riser", dur=1.5, size="mid")
    add("title", 5.75, "whoosh")
    # 전체 흐름
    add("overview", 0.0, "impact", size="mid")
    for k in range(5):
        add("overview", 0.3 + k * 0.25, "card", idx=k)
    for k in range(15):
        add("overview", 1.5 + k * BEAT / 4, "pop", idx=k)
    for k in range(5):
        add("overview", 3.0 + k * 0.2, "tick")
    add("overview", 4.5, "stamp")
    add("overview", 4.9, "stamp")
    add("overview", 5.5, "sweep")
    for k, lt in enumerate([5.9, 6.55, 7.1, 7.3, 7.5]):   # 아이디어 점이 단계 카드에 닿는 순간
        add("overview", lt, "chip", idx=k)
    add("overview", 7.75, "whoosh")
    # 00 준비
    add("prep", 0.0, "impact", size="mid")
    for k in range(5):
        add("prep", 0.4 + k * 0.45, "type_burst" if k in (0, 4) else "tick")
    add("prep", 2.6, "type_burst")
    add("prep", 3.3, "type_burst")
    add("prep", 4.3, "file", idx=0)
    add("prep", 4.6, "file", idx=1)
    add("prep", 5.0, "confirm")
    add("prep", 5.75, "whoosh")
    # 01 기획
    add("plan", 0.0, "impact", size="mid")
    add("plan", 0.3, "card", idx=0)
    for k in range(4):
        add("plan", 1.0 + k * 0.15, "tick")
    for k in range(3):
        add("plan", 2.2 + k * 0.3, "check", idx=k)
    add("plan", 3.2, "modal")
    add("plan", 4.5, "click")
    add("plan", 4.6, "confirm")
    for k in range(5):
        add("plan", 6.0 + k * 0.25, "card", idx=k)
    for k in range(7):
        add("plan", 8.0 + k * 0.5, "packet", idx=k)
    add("plan", 7.9, "error")
    add("plan", 10.6, "confirm")
    add("plan", 14.0, "error")
    add("plan", 15.0, "confirm")
    add("plan", 15.6, "sweep")
    add("plan", 16.2, "stamp")
    for k in range(4):
        add("plan", 17.4 + k * 0.3, "file", idx=k)
    add("plan", 19.75, "whoosh")
    # 02 명세
    add("spec", 0.0, "impact", size="mid")
    for k in range(12):
        add("spec", 0.8 + k * 0.18, "chip", idx=k)
    add("spec", 4.2, "type_burst")
    add("spec", 4.6, "confirm")
    add("spec", 5.4, "type_burst")
    add("spec", 6.0, "confirm")
    add("spec", 6.8, "counter", dur=1.4)
    add("spec", 9.0, "modal")
    add("spec", 10.2, "click")
    add("spec", 11.0, "click")
    add("spec", 11.2, "stamp")
    add("spec", 11.75, "riser", dur=2.0, size="big")
    # 03 제작(드롭)
    add("produce", 0.0, "impact", size="huge")
    add("produce", 0.0, "drop")
    for k in range(4):
        add("produce", 2.0 + k * 2.4, "panel", idx=k)
    add("produce", 7.5, "scan", dur=1.5)
    for k in range(4):
        add("produce", 14.0 + k * 0.25, "qa_pass", idx=k)
    add("produce", 15.2, "error")
    add("produce", 16.1, "qa_pass", idx=0)
    for k in range(8):
        add("produce", 17.5 + k * 0.15, "tick")
    add("produce", 17.6, "counter", dur=1.2)
    add("produce", 19.75, "whoosh")
    # 04 개발
    add("develop", 0.0, "impact", size="mid")
    add("develop", 0.3, "card", idx=0)
    add("develop", 0.6, "card", idx=1)
    add("develop", 1.2, "counter", dur=1.6)
    add("develop", 4.0, "type_burst")
    add("develop", 4.6, "boot")
    add("develop", 6.2, "boot")
    add("develop", 8.2, "error")
    add("develop", 8.8, "packet", idx=99)
    add("develop", 9.6, "type_burst")
    add("develop", 10.6, "stamp")
    for k in range(5):
        add("develop", 11.0 + k * 0.6, "confirm", idx=k)
    add("develop", 14.2, "sweep")
    add("develop", 15.4, "stamp")
    add("develop", 17.75, "whoosh")
    # 05 출시
    add("release", 0.0, "impact", size="mid")
    for k in range(4):
        add("release", 0.3 + k * 0.08, "card", idx=k)
    for k, lt in enumerate([1.4, 1.9, 2.3, 2.8]):
        add("release", lt, "confirm", idx=k)
    for k in range(6):
        add("release", 3.8 + k * 0.45, "check", idx=k)
    add("release", 6.25, "riser", dur=1.5, size="big")
    add("release", 8.0, "impact", size="huge")
    add("release", 8.0, "go")
    add("release", 9.75, "whoosh")
    # 결과물
    add("deliver", 0.0, "impact", size="mid")
    for k in range(9):
        add("deliver", 0.3 + k * 0.2, "file", idx=k)
    for k in range(4):
        add("deliver", 3.0 + k * 0.6, "packet", idx=20 + k)
        add("deliver", 3.3 + k * 0.6, "chip", idx=k)
    add("deliver", 5.75, "whoosh")
    # 아웃트로
    for k in range(8):
        add("outro", k * 0.25, "cut", idx=k)
    add("outro", 2.0, "impact", size="big")
    add("outro", 4.0, "shimmer")
    add("outro", 6.0, "impact", size="final")
    ev.sort(key=lambda e: e["t"])
    return ev


def main():
    data = {
        "bpm": BPM, "beat": BEAT, "duration": DUR,
        "prompt": PROMPT, "typing": typing_times(),
        "sections": [dict(name=n, start=s, end=e, energy=en, color=c, music=m) for n, s, e, en, c, m in SECTIONS],
        "rolls": ROLLS, "swells": SWELLS, "silences": SILENCES, "bursts": BURSTS, "kick": KICK,
        "captions": [dict(start=SEC[s][0] + a, end=SEC[s][0] + b, text=x, section=s) for s, a, b, x in CAPTIONS],
        "events": events(),
    }
    (HERE / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "cues.js").write_text("window.CUES = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
    kinds = sorted({e["kind"] for e in data["events"]})
    print(f"events {len(data['events'])}, sections {len(SECTIONS)}, captions {len(CAPTIONS)}")
    print("kinds:", ", ".join(kinds))


if __name__ == "__main__":
    main()
