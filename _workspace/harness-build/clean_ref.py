"""VARCO 문서(md/refmd)에서 HTML 장식을 걷어내 스킬 참조 문서로 묶는다."""
import re, pathlib

SRC = pathlib.Path("/Users/robin/Downloads/varco-platform/_workspace/link-check")
DST = pathlib.Path("/Users/robin/Downloads/varco-platform/.claude/skills/varco-api/references")
DST.mkdir(parents=True, exist_ok=True)

def clean(text: str) -> str:
    # 메서드 + 경로 배지 → "**POST** `/path`"
    text = re.sub(
        r"<p>\s*<span[^>]*>\s*(GET|POST|PUT|DELETE|PATCH)\s*</span>\s*<span[^>]*>\s*([^<]+?)\s*</span>\s*</p>",
        lambda m: f"\n**{m.group(1)}** `{m.group(2).strip()}`\n", text, flags=re.S | re.I)
    # 응답 예시 제목 배지
    text = re.sub(r"<p>\s*<span[^>]*font-size:1.5em[^>]*>\s*([^<]+?)\s*</span>(.*?)</p>",
                  lambda m: "\n#### " + m.group(1).strip() + " " +
                  " ".join(x.strip() for x in re.findall(r">\s*([^<>]+?)\s*<", m.group(2)) if x.strip()) + "\n",
                  text, flags=re.S | re.I)
    # 파라미터 구역 제목 배지
    text = re.sub(r"<p>\s*<span[^>]*font-weight:bold[^>]*>\s*([^<]+?)\s*</span>(.*?)</p>",
                  lambda m: "\n##### " + m.group(1).strip() + " " +
                  " ".join(x.strip() for x in re.findall(r">\s*([^<>]+?)\s*<", m.group(2)) if x.strip()) + "\n",
                  text, flags=re.S | re.I)
    text = re.sub(r"<span[^>]*font-weight:bold[^>]*>\s*([^<]+?)\s*</span>", r"\n##### \1\n", text, flags=re.S | re.I)
    text = re.sub(r'<audio[^>]*src="([^"]+)"[^>]*>\s*</audio>', r"[샘플 오디오](\1)", text)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S | re.I)          # 숨겨 둔 가격표 주석 제거
    text = re.sub(r"<div[^>]*>\s*</div>", "", text)
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"</?(p|span|div|b|sub|table|tr|td|h3|img|a)[^>]*>", "", text)
    text = re.sub(r"<strong>(.*?)</strong>", r"**\1**", text)
    text = re.sub(r'<video[^>]*src="([^"]+)"[^>]*>\s*</video>', r"[샘플 영상](\1)", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"

GROUPS = {
    "sound.md": ("VARCO Sound API", ["sound-overview", "sound-texttosound", "sound-variation", "sound-looping",
                  "sound-monotostereo", "sound-conversion", "sound-enhance"],
                 ["sound-text2sound", "sound-variation", "sound-looping", "sound-mono2stereo",
                  "sound-conversion", "sound-enhance"]),
    "voice.md": ("VARCO Voice API (TTS · Voice Conversion)", ["voice-overview", "voice-text-to-speech-lite",
                  "voice-text-to-speech-standard", "voice-voice-conversion", "voice-voice-conversion-acting"],
                 ["text-to-speech-lite", "text-to-speech-standard", "voice-conversion", "voice-conversion-custom",
                  "voice-conversion-acting", "voice-conversion-acting-custom"]),
    "face.md": ("Voice-to-Face (SyncFace) API", ["voice-to-face"], ["voice-to-face"]),
    "3d.md": ("VARCO 3D API", ["3d-overview", "3d-image-to-3d"], ["3d-image-to-3d"]),
    "image-edit.md": ("Art Fashion · 이미지 편집 API", ["fashion-overview"],
                 ["vton-clothes", "vton-accessories", "headswap", "generative-edit-eraser",
                  "generative-edit-inpaint", "generative-edit-inpaint-image", "generative-edit-texture",
                  "generative-edit-perspective", "generative-edit-graphic", "generative-edit-background", "upscale"]),
    "translate.md": ("Translate API", ["translate"], ["translate"]),
    "platform.md": ("플랫폼 공통: 인증 · 워크스페이스 · 크레딧 · 기타 서비스",
                 ["introduction", "quickstart", "chatbot-overview", "gentlewords-overview", "safety-overview"],
                 ["authentication"]),
    "unity-plugin.md": ("VARCO Sound Unity 플러그인", ["plugin-sound", "plugin-sound-unity"], []),
}

for out, (title, guides, refs) in GROUPS.items():
    parts = [f"# {title}\n",
             "> 원문: api.varco.ai 문서(2026-09 수집). 가이드와 레퍼런스가 다르면 **레퍼런스를 기준으로 한다**"
             " (공식 안내: \"엔드포인트 별 최신 버전은 항상 API Reference 페이지를 기준으로 확인\").\n"]
    if guides:
        parts.append("\n---\n\n# 제1부. 가이드\n")
        for g in guides:
            p = SRC / "md" / f"{g}.md"
            if p.exists():
                parts.append(f"\n---\n\n## [가이드] {g}\n\n" + clean(p.read_text()))
    if refs:
        parts.append("\n---\n\n# 제2부. API 레퍼런스\n")
        for r in refs:
            p = SRC / "refmd" / f"{r}.md"
            if p.exists():
                parts.append(f"\n---\n\n## [레퍼런스] {r}\n\n" + clean(p.read_text()))
    body = "".join(parts)
    # 목차: 절 제목과 시작 줄 번호. 에이전트가 Read 의 offset 으로 필요한 구간만 읽게 한다.
    lines = body.splitlines()
    heads = [(i, l[3:].strip()) for i, l in enumerate(lines) if l.startswith("## [")]
    if len(lines) > 300 and heads:
        toc_len = len(heads) + 4
        toc = ["", "## 목차 (절 이름 — 시작 줄)", ""] + [f"- {h} — {i + 1 + toc_len}줄" for i, h in heads] + [""]
        body = "\n".join(lines[:2] + toc + lines[2:]) + "\n"
    # 샘플 코드의 키 자리표시자를 한 형태로 맞춘다(실제 키가 아님)
    body = re.sub(r"8sh1XXXXX86H5iN5828Jjjjzyb3AAAAn", "<OPENAPI_KEY>", body)
    (DST / out).write_text(body)
    print(out, len(body.splitlines()), "lines")
