"""하네스 구조 검증(6-1·6-2단계): 파일 위치, 프론트매터, 이름 참조, v1 잔재, 줄 수."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path("/Users/robin/Downloads/varco-platform")
AG = ROOT / ".claude/agents"
SK = ROOT / ".claude/skills"
problems, notes = [], []


def front(path):
    t = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if not m:
        return None, t
    fm = {}
    key = None
    for line in m.group(1).splitlines():
        if re.match(r"^\s*#", line) or not line.strip():
            continue
        if re.match(r"^\s+-\s+", line) and key:
            fm.setdefault(key, []).append(line.strip()[2:].strip())
            continue
        k, _, v = line.partition(":")
        key = k.strip()
        fm[key] = v.strip().strip('"') if v.strip() else []
    return fm, t


agents = {}
for p in sorted(AG.glob("*.md")):
    fm, t = front(p)
    if fm is None:
        problems.append(f"에이전트 프론트매터 없음: {p.name}")
        continue
    for k in ("name", "description", "model"):
        if not fm.get(k):
            problems.append(f"{p.name}: {k} 없음")
    if fm.get("name") != p.stem:
        problems.append(f"{p.name}: name({fm.get('name')}) ≠ 파일 이름")
    if fm.get("model") not in ("fable", "opus", "sonnet"):
        problems.append(f"{p.name}: model 값 {fm.get('model')}")
    if "# 모델:" not in t:
        problems.append(f"{p.name}: 모델 선택 이유 주석 없음")
    for sec in ("핵심 역할", "작업 원칙", "입력·출력 규칙", "다시 호출할 때", "오류 처리", "협업"):
        if f"## {sec}" not in t:
            problems.append(f"{p.name}: '## {sec}' 절 없음")
    if "## 통신 규칙" not in t and "## 구조화 출력" not in t and "## 반환" not in t:
        notes.append(f"{p.name}: 통신 규칙·구조화 출력 절이 없다(단발 서브에이전트면 정상)")
    for s in fm.get("skills", []) if isinstance(fm.get("skills"), list) else []:
        if not (SK / s / "SKILL.md").exists():
            problems.append(f"{p.name}: skills 의 '{s}' 스킬이 없다")
    agents[p.stem] = fm

skills = {}
for d in sorted(SK.iterdir()):
    if not d.is_dir():
        continue
    sk = d / "SKILL.md"
    if not sk.exists():
        problems.append(f"스킬 폴더에 SKILL.md 없음: {d.name}")
        continue
    fm, t = front(sk)
    if not fm or not fm.get("name") or not fm.get("description"):
        problems.append(f"{d.name}/SKILL.md: name/description 없음")
        continue
    if fm["name"] != d.name:
        problems.append(f"{d.name}/SKILL.md: name({fm['name']}) ≠ 폴더 이름")
    n = len(t.splitlines())
    if n >= 500:
        problems.append(f"{d.name}/SKILL.md: {n}줄(500줄 이상)")
    for ref in d.glob("references/*.md"):
        lines = ref.read_text(encoding="utf-8").splitlines()
        if len(lines) > 300 and not any("목차" in l or "Contents" in l for l in lines[:40]):
            notes.append(f"{d.name}/references/{ref.name}: {len(lines)}줄인데 앞부분에 목차가 없다")
    # 스킬 본문이 가리키는 스크립트·참조 파일이 실제로 있는가
    for m in re.finditer(r"`((?:scripts|references)/[A-Za-z0-9_./-]+)`", t):
        if not (d / m.group(1)).exists():
            problems.append(f"{d.name}/SKILL.md: 참조 파일 없음 {m.group(1)}")
    for m in re.finditer(r"\.claude/skills/([a-z0-9-]+)/((?:scripts|references)/[A-Za-z0-9_./-]+)", t):
        if not (SK / m.group(1) / m.group(2)).exists():
            problems.append(f"{d.name}/SKILL.md: 다른 스킬의 파일 없음 {m.group(1)}/{m.group(2)}")
    skills[d.name] = n

# 에이전트 본문이 가리키는 스킬 파일
for p in AG.glob("*.md"):
    t = p.read_text(encoding="utf-8")
    for m in re.finditer(r"\.claude/skills/([a-z0-9-]+)/((?:SKILL\.md|scripts/[A-Za-z0-9_./-]+|references/[A-Za-z0-9_./-]+))", t):
        if not (SK / m.group(1) / m.group(2)).exists():
            problems.append(f"{p.name}: 참조 파일 없음 {m.group(1)}/{m.group(2)}")

# 오케스트레이터가 부르는 subagent_type / agentType 이 모두 정의돼 있는가
orch = (SK / "varco-game-studio/SKILL.md").read_text(encoding="utf-8")
wf = (SK / "varco-game-studio/scripts/asset_production.workflow.js").read_text(encoding="utf-8")
used = set(re.findall(r'subagent_type: "([a-z-]+)"', orch)) | set(re.findall(r"\| [a-z—-]+ \| ([a-z-]+) \| (?:fable|opus|sonnet) \|", orch))
used |= set(re.findall(r"agentType: '([a-z-]+)'", wf))
BUILTIN = {"general-purpose", "Explore", "Plan", "claude"}
for u in sorted(used - BUILTIN):
    if u not in agents:
        problems.append(f"오케스트레이터가 부르는 유형 '{u}' 의 에이전트 정의가 없다")
unused = sorted(set(agents) - used)
if unused:
    notes.append(f"오케스트레이터 표에 없는 에이전트: {unused}")

# 계약서의 owner 값이 에이전트로 존재하는가
contracts = (SK / "varco-game-studio/references/contracts.md").read_text(encoding="utf-8")
for owner in ("sound-designer", "voice-director", "visual-artist", "localization-specialist", "marketing-artist"):
    if owner not in agents:
        problems.append(f"계약서 owner '{owner}' 의 에이전트가 없다")

# v1 잔재, commands 폴더
for p in list(AG.glob("*.md")) + list(SK.rglob("*.md")) + list(SK.rglob("*.js")) + [ROOT / "CLAUDE.md"]:
    t = p.read_text(encoding="utf-8")
    for bad in ("TeamCreate", "TeamDelete", "team_name", "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"):
        if bad in t:
            problems.append(f"v1 잔재 '{bad}': {p.relative_to(ROOT)}")
if (ROOT / ".claude/commands").exists():
    problems.append(".claude/commands 폴더가 있다")

# 워크플로 스크립트 규칙
if re.search(r"Date\.now\(|Math\.random\(|new Date\(\)", wf):
    problems.append("워크플로에 Date.now/Math.random/new Date() 사용")
if ".filter(Boolean)" not in wf:
    problems.append("워크플로에 .filter(Boolean) 없음")
meta_titles = set(re.findall(r"title: '([^']+)'", wf.split("}\n", 1)[0] + wf[:1500]))
for ph in set(re.findall(r"phase: '([^']+)'", wf)):
    if ph not in meta_titles:
        problems.append(f"워크플로 phase '{ph}' 가 meta.phases 에 없다")

models = {}
for k, v in agents.items():
    models.setdefault(v.get("model"), []).append(k)

print(json.dumps({"agents": len(agents), "skills": len(skills), "models": models,
                  "skill_lines": skills, "problems": problems, "notes": notes}, ensure_ascii=False, indent=1))
sys.exit(1 if problems else 0)
