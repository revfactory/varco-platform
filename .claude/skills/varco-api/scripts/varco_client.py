#!/usr/bin/env python3
"""VARCO API 공용 클라이언트 (호출 · 드라이런 · 크레딧 장부 · 예산 차단).

에이전트가 VARCO API 를 부를 때는 요청 코드를 새로 짜지 말고 이 스크립트를 쓴다.
같은 규칙(키 보호, 예산 확인, 결과 저장 위치, 장부 기록)을 모든 에이전트가 똑같이 지키게 하기 위해서다.

사용 예
  # 파라미터 검사만 (네트워크 없음)
  varco_client.py validate sound.text2sound --param prompt="sword swing whoosh" --param num_sample=3

  # 호출 (드라이런)
  varco_client.py call sound.text2sound --params p.json --out games/x/assets/audio/sfx/swing.wav \
      --ledger _workspace/x/varco_ledger.jsonl --asset-id sfx_swing --dry-run

  # 호출 (실제) — 예산 5000 크레딧을 넘으면 호출하지 않는다
  varco_client.py call sound.variation --file source=swing_01.wav --param num_sample=4 \
      --out .../swing_var.wav --ledger ... --budget 5000 --asset-id sfx_swing

  # 3D 비동기 결과 이어받기
  varco_client.py result <requestId> --out model.glb

  # 화자 목록
  varco_client.py call voices.tts_standard --out _workspace/x/voices_tts_standard.json

  # 장부 요약
  varco_client.py ledger --ledger _workspace/x/varco_ledger.jsonl

종료 코드
  0 성공 · 2 사용법 오류 · 3 예산 초과로 호출 안 함 · 4 키 없음(실제 호출 불가)
  10 인증 실패(401) · 11 크레딧 부족/권한 거부(402·403) · 12 요청 검증 실패(400·422 또는 사전 검사)
  13 서버 오류 반복(5xx) · 14 3D 작업 실패 또는 시간 초과 · 15 응답 형식 이상
  10·11 은 다시 시도해도 결과가 같다. 재시도하지 말고 리더에게 보고한다.
"""
import argparse
import base64
import datetime as _dt
import json
import os
import pathlib
import sys
import time
import wave

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from varco_catalog import APIS, BASE_URL as _DEFAULT_BASE, RESULT_PATH, estimate_credits, validate_params  # noqa: E402

# 테스트용 모의 서버를 가리킬 때만 VARCO_BASE_URL 을 쓴다. 평소에는 설정하지 않는다.
BASE_URL = os.environ.get("VARCO_BASE_URL", _DEFAULT_BASE).rstrip("/")

EXIT = dict(ok=0, usage=2, budget=3, nokey=4, auth=10, credit=11, invalid=12, server=13, async_fail=14, format=15)


# ----------------------------------------------------------------------------- 키
def load_key():
    """OPENAPI_KEY 를 환경변수 → 상위 디렉터리의 .env 순서로 찾는다. 값은 절대 출력하지 않는다."""
    for name in ("OPENAPI_KEY", "VARCO_OPENAPI_KEY"):
        if os.environ.get(name):
            return os.environ[name].strip()
    here = pathlib.Path.cwd()
    for d in [here, *here.parents]:
        env = d / ".env"
        if env.is_file():
            for line in env.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() in ("OPENAPI_KEY", "VARCO_OPENAPI_KEY") and v.strip():
                    return v.strip().strip('"').strip("'")
            break
    return None


# ----------------------------------------------------------------------------- 장부
def now_iso():
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def ledger_append(path, entry):
    if not path:
        return
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def ledger_read(path):
    p = pathlib.Path(path) if path else None
    if not p or not p.exists():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def ledger_spent(path):
    """실제 호출에 쓴(또는 진행 중이라 예약된) 추정 크레딧 합계와 단가 미상 호출 수.

    예약(type=reserve) 뒤 결과가 아직 없으면 진행 중인 호출로 보고 합계에 넣는다.
    결과가 실패(ok=false)면 예약을 풀어 합계에서 뺀다.
    """
    rows = ledger_read(path)
    resolved = {r.get("reserve_id") for r in rows if r.get("reserve_id") and r.get("type") != "reserve"}
    spent, unknown = 0, 0
    for r in rows:
        if r.get("type") == "reserve":
            if r.get("reserve_id") not in resolved:
                spent += r.get("est_credits") or 0
            continue
        if r.get("mode") == "live" and r.get("ok"):
            if r.get("est_credits") is None:
                unknown += 1
            else:
                spent += r["est_credits"]
    return spent, unknown


class LedgerLock:
    """장부 옆 .lock 파일로 예산 확인과 예약을 한 번에 처리한다(여러 에이전트가 동시에 호출할 때 초과 방지)."""

    def __init__(self, ledger):
        self.path = pathlib.Path(str(ledger) + ".lock")
        self.fh = None

    def __enter__(self):
        import fcntl
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.fh = self.path.open("w")
        fcntl.flock(self.fh, fcntl.LOCK_EX)
        return self

    def __exit__(self, *exc):
        import fcntl
        fcntl.flock(self.fh, fcntl.LOCK_UN)
        self.fh.close()


# ----------------------------------------------------------------------------- 입력 준비
def parse_value(raw):
    """--param 값: JSON 으로 해석되면 JSON(숫자·불리언·객체), 아니면 문자열."""
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return raw


def wav_seconds(path):
    try:
        with wave.open(str(path), "rb") as w:
            return w.getnframes() / float(w.getframerate())
    except Exception:
        pass
    try:
        import subprocess
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                              "default=nk=1:nw=1", str(path)], capture_output=True, text=True, timeout=30)
        return float(out.stdout.strip())
    except Exception:
        return None


def image_size(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except Exception:
        return None


def build_request(api_id, params, files):
    """(method, url, json_body, multipart_files, multipart_data, redacted_view) 를 만든다."""
    spec = APIS[api_id]
    body = dict(spec.get("defaults", {}))
    body.update(params)
    url = BASE_URL + spec["path"]
    redacted = {}
    if spec["body"] == "json":
        for field, fpath in files.items():
            if not pathlib.Path(fpath).is_file():          # 드라이런의 예정 입력
                redacted[field] = f"<planned input, not yet generated: {fpath}>"
                body[field] = redacted[field]
                continue
            data = pathlib.Path(fpath).read_bytes()
            body[field] = base64.b64encode(data).decode("ascii")
            redacted[field] = f"<base64 {len(data)} bytes from {fpath}>"
        view = {k: (redacted.get(k) or v) for k, v in body.items()}
        return spec["method"], url, body, None, None, view
    if spec["body"] == "multipart":
        mfiles = {}
        for field, fpath in files.items():
            p = pathlib.Path(fpath)
            if not p.is_file():                              # 드라이런의 예정 입력
                redacted[field] = f"<planned input, not yet generated: {fpath}>"
                continue
            mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg" if p.suffix.lower() in (".jpg", ".jpeg") else "application/octet-stream"
            mfiles[field] = (p.name, p.read_bytes(), mime)
            redacted[field] = f"<file {p.stat().st_size} bytes from {fpath}>"
        data = {}
        for k, v in body.items():
            # 객체 값은 JSON 문자열로 보낸다(headswap 레퍼런스: "JSON string representing ... options")
            data[k] = json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else (
                str(v).lower() if isinstance(v, bool) else str(v))
        view = dict(data)
        view.update(redacted)
        return spec["method"], url, None, mfiles, data, view
    return spec["method"], url, None, None, None, {}


# ----------------------------------------------------------------------------- 출력 저장
def sniff_ext(data):
    if data[:4] == b"RIFF":
        return ".wav"
    if data[:4] == b"fLaC":
        return ".flac"
    if data[:3] == b"ID3" or data[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"):
        return ".mp3"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if data[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if data[:4] == b"glTF":
        return ".glb"
    return None


def write_bytes(out, data, warnings):
    out = pathlib.Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    real = sniff_ext(data)
    if real and out.suffix.lower() != real:
        warnings.append(f"{out.name}: 확장자({out.suffix})와 실제 형식({real})이 다르다. 실제 형식으로 저장한다.")
        out = out.with_suffix(real)
    out.write_bytes(data)
    return str(out)


def numbered(out, i, n):
    out = pathlib.Path(out)
    return out if n == 1 else out.with_name(f"{out.stem}_{i:02d}{out.suffix}")


def save_response(api_id, resp, out, warnings):
    kind = APIS[api_id]["out"]
    if kind == "image":
        ctype = resp.headers.get("Content-Type", "")
        if "json" in ctype:
            raise ValueError(f"이미지 대신 JSON 응답: {resp.text[:300]}")
        return [write_bytes(out, resp.content, warnings)]
    payload = resp.json()
    if kind == "json":
        p = pathlib.Path(out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return [str(p)]
    if kind == "audio_list":
        items = payload if isinstance(payload, list) else [payload]
        written = []
        for i, it in enumerate(items, 1):
            written.append(write_bytes(numbered(out, i, len(items)), base64.b64decode(it["audio"]), warnings))
        return written
    if kind == "audio":
        items = payload if isinstance(payload, list) else [payload]
        written = []
        for i, it in enumerate(items, 1):
            written.append(write_bytes(numbered(out, i, len(items)), base64.b64decode(it["audio"]), warnings))
        meta = {k: v for k, v in (items[0] if items else {}).items() if k != "audio"}
        if meta:
            pathlib.Path(str(out) + ".meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2),
                                                            encoding="utf-8")
        return written
    raise ValueError(f"처리할 수 없는 출력 형식 {kind}")


# ----------------------------------------------------------------------------- HTTP
def http_call(method, url, key, *, json_body=None, mfiles=None, mdata=None, timeout=300):
    import requests
    headers = {"OPENAPI_KEY": key}
    attempt, server_retries, rate_retries = 0, 0, 0
    while True:
        attempt += 1
        try:
            if method == "GET":
                r = requests.get(url, headers=headers, timeout=timeout)
            elif mfiles is not None:
                r = requests.post(url, headers=headers, files=mfiles, data=mdata, timeout=timeout)
            else:
                r = requests.post(url, headers=headers, json=json_body, timeout=timeout)
        except requests.RequestException as e:
            if server_retries < 1:
                server_retries += 1
                time.sleep(5)
                continue
            raise ConnectionError(f"네트워크 오류: {e}") from e
        if r.status_code == 429 and rate_retries < 2:
            rate_retries += 1
            time.sleep(float(r.headers.get("Retry-After", 10)))
            continue
        if r.status_code >= 500 and server_retries < 1:
            server_retries += 1
            time.sleep(5)
            continue
        return r


def classify_error(status, text):
    low = (text or "").lower()
    if status == 401:
        return "auth", "인증 실패: OPENAPI_KEY 가 없거나 잘못됐다(재시도 금지)"
    if status in (402, 403) or "credit" in low or "크레딧" in low:
        return "credit", "크레딧 부족 또는 권한 거부(재시도 금지)"
    if status in (400, 422):
        return "invalid", "요청 검증 실패: 파라미터를 고친 뒤 다시 호출한다"
    if status >= 500:
        return "server", "서버 오류가 재시도 후에도 계속된다"
    return "format", f"예상하지 못한 상태 코드 {status}"


# ----------------------------------------------------------------------------- 3D 폴링
def poll_result(request_id, key, out, *, interval=10, timeout=900, warnings=None):
    import requests
    url = BASE_URL + RESULT_PATH.format(request_id=request_id)
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = http_call("GET", url, key)
        try:
            body = r.json()
        except ValueError:
            body = {}
        status = body.get("status")
        if r.status_code == 200 and status == "succeeded":
            model = requests.get(body["model_url"], timeout=300)
            model.raise_for_status()
            path = write_bytes(out, model.content, warnings if warnings is not None else [])
            return {"status": "succeeded", "model_url": body["model_url"], "outputs": [path]}
        if status == "failed" or (r.status_code >= 500 and status != "processing"):
            return {"status": "failed", "http": r.status_code, "body": body}
        time.sleep(interval)
    return {"status": "timeout"}


# ----------------------------------------------------------------------------- 명령
def collect(args):
    params = {}
    if args.params:
        params.update(json.loads(pathlib.Path(args.params).read_text(encoding="utf-8")))
    for kv in args.param or []:
        k, v = kv.split("=", 1)
        params[k] = parse_value(v)
    files = {}
    # 드라이런·검사에서는 앞 단계 결과처럼 아직 생기지 않은 파일도 '예정 입력'으로 받는다.
    allow_missing = getattr(args, "dry_run", False) or args.cmd == "validate"
    for kv in args.file or []:
        k, v = kv.split("=", 1)
        if not pathlib.Path(v).is_file() and not allow_missing:
            raise FileNotFoundError(f"--file {k}: 파일이 없다 → {v}")
        files[k] = v
    return params, files


def estimate_for(api_id, params, files, override):
    if override is not None:
        return override, True, "--est-credits 지정"
    spec = APIS[api_id]
    unit = spec["price"]["unit"]
    kw = {}
    if unit == "seconds":
        src = files.get(spec["price"].get("input", "audio"))
        kw["audio_seconds"] = wav_seconds(src) if src else None
    if unit in ("megapixel", "mp_tier"):
        img = next((files[f] for f in spec.get("files", []) if f in files), None)
        size = image_size(img) if img else None
        if size and api_id == "image.upscale":
            s = int(params.get("scale_factor", 4))
            size = (size[0] * s, size[1] * s)
        kw["out_size"] = size
    return estimate_credits(api_id, params, **kw)


def cmd_validate(args):
    params, files = collect(args)
    problems = validate_params(args.api, params, files)
    est, known, note = estimate_for(args.api, params, files, None)
    print(json.dumps({"api": args.api, "ok": not problems, "problems": problems,
                      "est_credits": est, "price_known": known, "price_note": note}, ensure_ascii=False, indent=2))
    return EXIT["ok"] if not problems else EXIT["invalid"]


def cmd_call(args):
    if args.api not in APIS:
        print(json.dumps({"ok": False, "error": f"알 수 없는 API {args.api}. `catalog` 로 목록 확인"}, ensure_ascii=False))
        return EXIT["usage"]
    params, files = collect(args)
    problems = validate_params(args.api, params, files)
    est, known, note = estimate_for(args.api, params, files, args.est_credits)
    base = {"ts": now_iso(), "asset_id": args.asset_id, "api": args.api, "est_credits": est,
            "price_known": known, "price_note": note}
    if problems:
        entry = dict(base, mode="dry-run" if args.dry_run else "live", ok=False, error="사전 검사 실패",
                     problems=problems)
        ledger_append(args.ledger, entry)
        print(json.dumps(entry, ensure_ascii=False, indent=2))
        return EXIT["invalid"]

    method, url, jbody, mfiles, mdata, view = build_request(args.api, params, files)

    if args.dry_run:
        spec_path = pathlib.Path(str(args.out) + ".dryrun.json")
        spec_path.parent.mkdir(parents=True, exist_ok=True)
        spec_path.write_text(json.dumps({"api": args.api, "method": method, "url": url,
                                         "headers": {"OPENAPI_KEY": "<redacted>"}, "body": view,
                                         "intended_output": str(args.out), "est_credits": est,
                                         "price_note": note}, ensure_ascii=False, indent=2), encoding="utf-8")
        entry = dict(base, mode="dry-run", ok=True, outputs=[str(spec_path)])
        ledger_append(args.ledger, entry)
        print(json.dumps(entry, ensure_ascii=False, indent=2))
        return EXIT["ok"]

    key = load_key()
    if not key:
        print(json.dumps(dict(base, ok=False, error="OPENAPI_KEY 가 없다. 환경변수나 프로젝트 .env 에 넣거나 --dry-run 으로 실행한다."),
                         ensure_ascii=False, indent=2))
        return EXIT["nokey"]

    reserve_id = None
    if args.budget is not None:
        if not args.ledger:
            print(json.dumps(dict(base, ok=False, error="--budget 에는 --ledger 가 필요하다"), ensure_ascii=False))
            return EXIT["usage"]
        with LedgerLock(args.ledger):
            spent, unknown = ledger_spent(args.ledger)
            if est is None and not args.allow_unknown_price:
                entry = dict(base, mode="live", ok=False,
                             error="단가 미상 API 는 --allow-unknown-price 없이 호출하지 않는다", spent=spent)
                ledger_append(args.ledger, entry)
                print(json.dumps(entry, ensure_ascii=False, indent=2))
                return EXIT["budget"]
            if spent + (est or 0) > args.budget:
                entry = dict(base, mode="live", ok=False,
                             error=f"예산 초과: 사용·예약 {spent} + 이번 {est} > 예산 {args.budget}",
                             spent=spent, unknown_price_calls=unknown)
                ledger_append(args.ledger, entry)
                print(json.dumps(entry, ensure_ascii=False, indent=2))
                return EXIT["budget"]
            import uuid
            reserve_id = uuid.uuid4().hex[:12]
            ledger_append(args.ledger, dict(base, type="reserve", reserve_id=reserve_id))
    base["reserve_id"] = reserve_id

    warnings = []
    try:
        r = http_call(method, url, key, json_body=jbody, mfiles=mfiles, mdata=mdata, timeout=args.timeout)
    except ConnectionError as e:
        entry = dict(base, mode="live", ok=False, error=str(e))
        ledger_append(args.ledger, entry)
        print(json.dumps(entry, ensure_ascii=False, indent=2))
        return EXIT["server"]

    request_id = r.headers.get("x-request-id") or r.headers.get("X-Request-Id")
    ok_status = (200, 202) if APIS[args.api]["out"] == "async_3d" else (200,)
    if r.status_code not in ok_status:
        kind, msg = classify_error(r.status_code, r.text)
        entry = dict(base, mode="live", ok=False, http=r.status_code, error=msg, server=r.text[:500],
                     request_id=request_id)
        ledger_append(args.ledger, entry)
        print(json.dumps(entry, ensure_ascii=False, indent=2))
        return EXIT[kind]

    try:
        if APIS[args.api]["out"] == "async_3d":
            body = r.json()
            rid = body.get("requestId")
            pathlib.Path(str(args.out) + ".request.json").parent.mkdir(parents=True, exist_ok=True)
            pathlib.Path(str(args.out) + ".request.json").write_text(json.dumps(body, ensure_ascii=False, indent=2),
                                                                    encoding="utf-8")
            if args.no_wait:
                entry = dict(base, mode="live", ok=True, http=r.status_code, request_id=rid, pending=True,
                             outputs=[str(args.out) + ".request.json"])
                ledger_append(args.ledger, entry)
                print(json.dumps(entry, ensure_ascii=False, indent=2))
                return EXIT["ok"]
            res = poll_result(rid, key, args.out, timeout=args.poll_timeout, warnings=warnings)
            ok = res["status"] == "succeeded"
            entry = dict(base, mode="live", ok=ok, http=r.status_code, request_id=rid,
                         outputs=res.get("outputs", []), async_status=res["status"], warnings=warnings)
            ledger_append(args.ledger, entry)
            print(json.dumps(entry, ensure_ascii=False, indent=2))
            return EXIT["ok"] if ok else EXIT["async_fail"]
        outputs = save_response(args.api, r, args.out, warnings)
    except (ValueError, KeyError) as e:
        entry = dict(base, mode="live", ok=False, http=r.status_code, error=f"응답 형식 이상: {e}",
                     request_id=request_id)
        ledger_append(args.ledger, entry)
        print(json.dumps(entry, ensure_ascii=False, indent=2))
        return EXIT["format"]

    entry = dict(base, mode="live", ok=True, http=r.status_code, request_id=request_id, outputs=outputs,
                 warnings=warnings)
    ledger_append(args.ledger, entry)
    print(json.dumps(entry, ensure_ascii=False, indent=2))
    return EXIT["ok"]


def cmd_result(args):
    key = load_key()
    if not key:
        print(json.dumps({"ok": False, "error": "OPENAPI_KEY 가 없다"}, ensure_ascii=False))
        return EXIT["nokey"]
    warnings = []
    res = poll_result(args.request_id, key, args.out, timeout=args.poll_timeout, warnings=warnings)
    res["warnings"] = warnings
    ledger_append(args.ledger, {"ts": now_iso(), "asset_id": args.asset_id, "api": "3d.result", "mode": "live",
                                "ok": res["status"] == "succeeded", "est_credits": 0, "request_id": args.request_id,
                                "outputs": res.get("outputs", [])})
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return EXIT["ok"] if res["status"] == "succeeded" else EXIT["async_fail"]


def cmd_ledger(args):
    rows = [r for r in ledger_read(args.ledger) if r.get("type") != "reserve"]
    spent, unknown = ledger_spent(args.ledger)
    by_api = {}
    for r in rows:
        k = (r.get("api"), r.get("mode"), bool(r.get("ok")))
        by_api[k] = by_api.get(k, 0) + 1
    summary = {"entries": len(rows), "live_spent_est": spent, "live_unknown_price_calls": unknown,
               "dry_run_calls": sum(1 for r in rows if r.get("mode") == "dry-run"),
               "failures": [r for r in rows if not r.get("ok")][-20:],
               "by_api": [{"api": a, "mode": m, "ok": o, "count": c} for (a, m, o), c in sorted(by_api.items(), key=str)]}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return EXIT["ok"]


def cmd_catalog(_args):
    for k, v in APIS.items():
        p = v["price"]
        if p["unit"] == "free":
            price = "무료(가정)"
        elif p["unit"] == "call" and p.get("credits") is None:
            price = "미상"
        else:
            price = json.dumps({x: y for x, y in p.items() if x != "known"}, ensure_ascii=False)
            price += "" if p.get("known") else " (추정)"
        print(f"{k:24s} {v['method']:4s} {v['path']:48s} body={v['body']:9s} out={v['out']:10s} price={price}")
    return EXIT["ok"]


def main():
    ap = argparse.ArgumentParser(description="VARCO API 공용 클라이언트")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add_io(p):
        p.add_argument("api")
        p.add_argument("--params", help="파라미터 JSON 파일")
        p.add_argument("--param", action="append", help="key=value (값은 JSON 으로 해석 가능하면 JSON)")
        p.add_argument("--file", action="append", help="field=path (json API 는 base64 로, multipart 는 첨부로)")

    p = sub.add_parser("validate", help="파라미터 사전 검사와 추정 크레딧")
    add_io(p)
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("call", help="API 호출")
    add_io(p)
    p.add_argument("--out", required=True, help="결과 파일 경로(여러 개면 _01, _02 … 가 붙는다)")
    p.add_argument("--ledger", help="크레딧 장부 JSONL 경로. 보통 _workspace/{slug}/varco_ledger.jsonl")
    p.add_argument("--asset-id", help="매니페스트 에셋 id (장부에 남긴다)")
    p.add_argument("--budget", type=float, help="이 장부의 실제 호출 누적 추정 크레딧 상한")
    p.add_argument("--est-credits", type=float, help="추정 크레딧을 직접 지정")
    p.add_argument("--allow-unknown-price", action="store_true", help="단가 미상 API 도 예산 모드에서 호출 허용")
    p.add_argument("--dry-run", action="store_true", help="네트워크 없이 요청 명세만 {out}.dryrun.json 에 쓴다")
    p.add_argument("--no-wait", action="store_true", help="3D: requestId 만 받고 폴링하지 않는다")
    p.add_argument("--timeout", type=float, default=300)
    p.add_argument("--poll-timeout", type=float, default=900)
    p.set_defaults(func=cmd_call)

    p = sub.add_parser("result", help="3D 비동기 결과 폴링·다운로드")
    p.add_argument("request_id")
    p.add_argument("--out", required=True)
    p.add_argument("--ledger")
    p.add_argument("--asset-id")
    p.add_argument("--poll-timeout", type=float, default=900)
    p.set_defaults(func=cmd_result)

    p = sub.add_parser("ledger", help="장부 요약")
    p.add_argument("--ledger", required=True)
    p.set_defaults(func=cmd_ledger)

    p = sub.add_parser("catalog", help="API 목록")
    p.set_defaults(func=cmd_catalog)

    args = ap.parse_args()
    try:
        sys.exit(args.func(args))
    except FileNotFoundError as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(EXIT["usage"])


if __name__ == "__main__":
    main()
