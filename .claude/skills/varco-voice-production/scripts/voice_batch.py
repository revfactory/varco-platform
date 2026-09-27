#!/usr/bin/env python3
"""대사 묶음 에셋 하나(매니페스트 voice_line)를 줄마다 제작한다: TTS → (VC Acting) → (Voice-to-Face).

모든 호출은 varco_client.py 를 subprocess 로 불러 장부·예산·드라이런 규칙을 그대로 지킨다.
종료 코드 3(예산)·4(키 없음)·10(인증)·11(크레딧)을 만나면 남은 줄을 부르지 않고 바로 멈춘다.
다시 시도해도 결과가 같은 실패라 계속 부르면 남은 한도만 쓰기 때문이다.

사용법
  voice_batch.py --run-meta _workspace/{slug}/run_meta.json --id vo_ch1_intro [--lines ch1_intro_002,ch1_intro_003]
                 [--dry-run] [--allow-unknown-price]

입력
  games/{slug}/manifest.json 의 해당 에셋(lines, steps, output), data/dialogue.csv, data/characters.csv,
  _workspace/{slug}/03_voice_casting.json(voice_cast.py 결과), 원문 외 언어면 data/strings/{lang}.json
  자리표시자({player_name})가 든 줄은 합성하지 않고 실패로 기록한다(음성 대사에는 자리표시자를 쓰지 않는 규칙)
출력
  계약서 6절 위치의 WAV·JSON(드라이런이면 {파일}.dryrun.json), 작업 기록 _workspace/{slug}/03_voice_{id}.json,
  표준 출력에 워크플로 PRODUCE 스키마 형태의 요약 JSON
"""
import argparse
import csv
import json
import pathlib
import re
import subprocess
import sys
import wave

CLIENT = pathlib.Path(__file__).resolve().parents[2] / "varco-api" / "scripts" / "varco_client.py"
LANG_CODE = {"korean": "ko", "english": "en", "japanese": "ja", "taiwanese": "tw"}
FACE_EMOTIONS = {"neutral", "angry", "happy", "sad", "surprise"}
STOP = {3: "budget_blocked", 4: "auth_failed", 10: "auth_failed", 11: "credit_exhausted"}


def read_csv(path):
    with open(path, encoding="utf-8") as f:
        return {r.get("line_id") or r.get("speaker_id"): r for r in csv.DictReader(f)}


def placeholder_wav(path):
    """드라이런에서 앞 단계 결과 대신 넣는 1초 무음. varco_client 가 입력 파일이 있어야 요청 명세를 만들기 때문이다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with wave.open(str(path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(44100)
            w.writeframes(b"\x00\x00" * 44100)
    return path


def fill(template, line_id):
    return template.replace("{line_id}", line_id)


class Runner:
    def __init__(self, a, meta, workspace, asset_id):
        self.dry = a.dry_run or meta.get("varco_mode") != "live"
        self.budget = meta.get("budget_credits")
        self.allow_unknown = a.allow_unknown_price or bool(meta.get("allow_unknown_price"))
        self.ledger = workspace / "varco_ledger.jsonl"
        self.params_dir = workspace / "03_voice_params"
        self.asset_id = asset_id
        self.calls = 0
        self.spent = 0.0
        self.unknown_price_calls = 0

    def call(self, api, params, files, out, tag):
        self.params_dir.mkdir(parents=True, exist_ok=True)
        pfile = self.params_dir / f"{tag}_{api.replace('.', '_')}.json"
        pfile.write_text(json.dumps(params, ensure_ascii=False, indent=2), encoding="utf-8")
        cmd = [sys.executable, str(CLIENT), "call", api, "--params", str(pfile), "--out", str(out),
               "--ledger", str(self.ledger), "--asset-id", self.asset_id]
        for k, v in files.items():
            cmd += ["--file", f"{k}={v}"]
        if self.dry:
            cmd.append("--dry-run")
        elif self.budget is not None:
            cmd += ["--budget", str(self.budget)]
        if self.allow_unknown and not self.dry:
            cmd.append("--allow-unknown-price")
        self.calls += 1
        r = subprocess.run(cmd, capture_output=True, text=True)
        try:
            res = json.loads(r.stdout)
        except json.JSONDecodeError:
            res = {"ok": False, "error": (r.stdout + r.stderr).strip()[-400:]}
        if r.returncode == 0 and not self.dry:
            if res.get("est_credits") is None:
                self.unknown_price_calls += 1
            else:
                self.spent += res["est_credits"]
        return r.returncode, res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-meta", required=True)
    ap.add_argument("--id", required=True, help="매니페스트 에셋 id")
    ap.add_argument("--lines", help="재작업할 line_id 만 쉼표로")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-unknown-price", action="store_true")
    a = ap.parse_args()

    meta_path = pathlib.Path(a.run_meta)
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    slug = meta["slug"]
    workspace = meta_path.parent
    game_dir = workspace.parent.parent / "games" / slug
    manifest = json.loads((game_dir / "manifest.json").read_text(encoding="utf-8"))
    asset = next((x for x in manifest["assets"] if x["id"] == a.id), None)

    def finish(status, outputs, notes, error="", lines=None, runner=None):
        summary = {"id": a.id, "status": status, "outputs": outputs, "calls": runner.calls if runner else 0,
                   "est_credits_spent": runner.spent if runner else 0, "notes": notes, "error": error}
        record = dict(summary, lines=lines or [], unknown_price_calls=runner.unknown_price_calls if runner else 0)
        (workspace / f"03_voice_{a.id}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2),
                                                         encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        sys.exit(0)

    if not asset:
        finish("failed", [], f"매니페스트에 {a.id} 가 없다", "asset not found")
    if asset.get("category") != "voice_line":
        finish("failed", [], f"{a.id} 는 voice_line 이 아니다({asset.get('category')}). 크리처 음성은 sound-designer 담당")

    runner = Runner(a, meta, workspace, a.id)
    dialogue = read_csv(game_dir / "data" / "dialogue.csv")
    chars = read_csv(game_dir / "data" / "characters.csv")
    steps = asset["steps"]
    tts = steps[0]
    model = tts["api"]
    lang = tts.get("params", {}).get("language", "korean")
    text_source = None
    if lang != "korean":
        p = game_dir / tts.get("text_source", f"data/strings/{LANG_CODE.get(lang, lang)}.json")
        if not p.exists():
            finish("failed", [], f"번역 문자열 {p} 가 없다. 현지화가 끝난 뒤 다시 만든다", "missing strings", runner=runner)
        text_source = json.loads(p.read_text(encoding="utf-8"))

    casting_path = workspace / "03_voice_casting.json"
    casting = json.loads(casting_path.read_text(encoding="utf-8")) if casting_path.exists() else {}

    acting = next((s for s in steps if s["api"] == "vc.acting"), None)
    face = next((s for s in steps if s["api"] == "face.blendshape"), None)
    out = asset["output"]
    extra = (out.get("extra") or [{}])[0]
    targets = asset.get("lines") or []
    if a.lines:
        wanted = set(a.lines.split(","))
        targets = [l for l in targets if l in wanted]
    raw_dir = workspace / "03_voice_raw"
    outputs, line_rows, notes = [], [], []

    # vc.acting 과 face.blendshape 는 단가 미공개 API 다. 실제 모드에서 사용자가 승인하지 않았으면
    # 에셋 전체를 막지 않고 이 두 단계만 건너뛴다. TTS 음성은 단가가 공개돼 있어 그대로 만든다.
    if not runner.dry and not runner.allow_unknown:
        if acting:
            notes.append("vc.acting 생략: 단가 미공개 호출이 승인되지 않아 TTS 결과를 최종 음성으로 쓴다")
            acting = None
        if face:
            notes.append("face.blendshape 생략: 단가 미공개 호출이 승인되지 않았다")
            face = None

    def voice_for(model_key, speaker, emotion):
        c = casting.get(model_key, {}).get(speaker)
        if not c:
            return None, None
        return c.get("by_emotion", {}).get(emotion) or c.get("default"), c

    for lid in targets:
        row = {"line_id": lid, "ok": False, "outputs": []}
        line_rows.append(row)
        d = dialogue.get(lid)
        if not d:
            row["error"] = "dialogue.csv 에 없는 line_id"
            continue
        speaker, emotion = d["speaker_id"], (d.get("emotion") or "neutral")
        text = text_source.get(lid) if text_source is not None else d["text_ko"]
        if not text:
            row["error"] = f"{lang} 문자열 없음"
            continue
        if re.search(r"\{[a-z0-9_]+\}", text):
            # 음성 파일에는 실행 중에 값을 넣을 수 없다. 음성 대사에 자리표시자를 쓰지 않는 것이 규칙이다(check_story_data.py).
            row["error"] = "자리표시자가 있는 대사라 합성하지 않았다. narrative 에 문장 수정을 요청한다"
            continue
        uuid, cinfo = voice_for(model, speaker, emotion)
        if not uuid:
            if runner.dry:
                uuid, cinfo = f"<speaker_uuid:{speaker}>", {}
            else:
                finish("failed", outputs, "캐스팅이 없다. voice_cast.py 를 먼저 실행한다", f"no casting for {speaker}",
                       line_rows, runner)
        if isinstance(uuid, str) and uuid.startswith("<speaker_uuid") and not runner.dry:
            finish("failed", outputs, "캐스팅이 자리표시 상태다. 실제 호출 전에 voice_cast.py 를 다시 실행한다",
                   f"placeholder casting for {speaker}", line_rows, runner)

        final_wav = game_dir / out["dir"] / f"{fill(out['basename'], lid)}.{out.get('format', 'wav')}"
        params = dict(tts.get("params", {}))
        params.update(text=text, voice=uuid)
        if cinfo:
            params.setdefault("seed", cinfo.get("seed", -1))
            if cinfo.get("properties"):
                params.setdefault("properties", cinfo["properties"])
        tts_out = raw_dir / f"{lid}_tts.wav" if acting else final_wav
        code, res = runner.call(model, params, {}, tts_out, lid)
        if code in STOP:
            row["error"] = res.get("error")
            finish(STOP[code], outputs, "; ".join(notes) or "치명적 실패로 중단", res.get("error", ""), line_rows, runner)
        if code != 0:
            row["error"] = f"{model} 실패(코드 {code}): {res.get('error')} {res.get('problems', '')}"
            continue
        cur = pathlib.Path(res["outputs"][0]) if not runner.dry else placeholder_wav(raw_dir / "_placeholder_1s.wav")
        row["outputs"] += res["outputs"]

        if acting:
            a_uuid, _ = voice_for("vc.acting", speaker, emotion)
            if not a_uuid:
                if runner.dry:
                    a_uuid = f"<speaker_uuid:{speaker}>"
                else:
                    row["error"] = "vc.acting 캐스팅 없음(voice_cast.py --acting)"
                    continue
            aparams = dict(acting.get("params", {}))
            aparams["speaker_uuid"] = a_uuid
            code, res = runner.call("vc.acting", aparams, {"audio": str(cur)}, final_wav, lid)
            if code in STOP:
                row["error"] = res.get("error")
                finish(STOP[code], outputs, "치명적 실패로 중단", res.get("error", ""), line_rows, runner)
            if code != 0:
                row["error"] = f"vc.acting 실패(코드 {code}): {res.get('error')}"
                continue
            row["outputs"] += res["outputs"]
            cur = pathlib.Path(res["outputs"][0]) if not runner.dry else cur

        if face:
            wants_face = face.get("when") != "speaker_face_anim" or \
                (chars.get(speaker, {}).get("face_anim", "n").lower() == "y")
            if wants_face:
                fparams = dict(face.get("params", {}))
                fparams.update(id=lid, emotion=emotion if emotion in FACE_EMOTIONS else "neutral")
                fdir = extra.get("dir", "assets/anim/face")
                fout = game_dir / fdir / f"{lid}.json"
                code, res = runner.call("face.blendshape", fparams, {"audio": str(cur)}, fout, lid)
                if code in STOP:
                    row["error"] = res.get("error")
                    finish(STOP[code], outputs, "치명적 실패로 중단", res.get("error", ""), line_rows, runner)
                if code != 0:
                    row["error"] = f"face.blendshape 실패(코드 {code}): {res.get('error')}"
                    continue
                row["outputs"] += res["outputs"]
        row["ok"] = True
        # 최종 산출물만 outputs 에 담는다(중간 TTS 원본은 작업 기록에만 남긴다)
        outputs += [o for o in row["outputs"] if "03_voice_raw" not in o]

    ok_lines = [r for r in line_rows if r["ok"]]
    failed = [f"{r['line_id']}: {r.get('error')}" for r in line_rows if not r["ok"]]
    if runner.unknown_price_calls:
        notes.append(f"단가 미공개 호출 {runner.unknown_price_calls}건은 est_credits_spent 에 빠져 있다")
    if runner.dry:
        notes.append("드라이런: 앞 단계 입력 자리에 1초 무음 자리표시 파일을 넣어 요청 명세를 만들었다")
    if not targets:
        finish("failed", [], "처리할 줄이 없다", "no lines", line_rows, runner)
    if not ok_lines:
        finish("failed", outputs, "; ".join(notes), "; ".join(failed)[:800], line_rows, runner)
    status = "dry-run" if runner.dry else "generated"
    msg = f"{len(ok_lines)}/{len(targets)}줄 완료"
    finish(status, outputs, "; ".join([msg] + notes), "; ".join(failed)[:800], line_rows, runner)


if __name__ == "__main__":
    main()
