"""VARCO API 카탈로그: 엔드포인트, 요청 형식, 파라미터 제약, 추정 단가.

varco_client.py(호출)와 estimate_cost.py(견적)가 함께 쓴다. 명세가 바뀌면 이 파일만 고친다.
출처: .claude/skills/varco-api/references/*.md (api.varco.ai, 2026-09 수집)

body 형식
  json       : application/json. b64 필드는 파일을 읽어 base64 문자열로 넣는다.
  multipart  : multipart/form-data. file 필드는 파일로 첨부하고, 객체 값은 JSON 문자열로 보낸다.
  none       : 본문 없음(GET)

out 형식
  audio_list : [{"audio": b64}, ...]  → 파일 여러 개
  audio      : {"audio": b64, "media_type"?}
  image      : 응답 본문이 이미지 바이트(image/png)
  json       : JSON 그대로 저장
  async_3d   : {"requestId"} → /inference/result/{id} 폴링 → model_url(GLB, 7일 유효) 다운로드

price 형식 (estimate_credits 참고). 모든 단가는 **추정치**다.
  공식 Pricing 페이지는 "공개 예정" 상태이고, 아래 숫자는 각 개요 문서에 주석으로 숨겨진 가격표에서 가져왔다.
  known=False 인 항목은 단가를 모른다는 뜻이며 견적에서 0으로 치지 않고 '미상'으로 표시한다.
"""

APIS = {
    # ---------------- Sound ----------------
    "sound.text2sound": dict(
        method="POST", path="/sound/varco/v1/api/text2sound", body="json", out="audio_list",
        required=["prompt"],
        rules={"prompt": {"max_chars": 200}, "version": {"enum": ["v1", "v2"]},
               "num_sample": {"min": 1, "max": 3}},
        price={"unit": "call", "credits": 25, "known": True},
        note="출력은 항상 10초, 44.1kHz/16bit WAV. 음악(멜로디) 생성에는 맞지 않는다."),
    "sound.variation": dict(
        method="POST", path="/sound/varco/v1/api/variation", body="json", out="audio_list",
        b64=["source"], required=["source"],
        rules={"num_sample": {"min": 1, "max": 5}, "strength": {"min": 0, "max": 3}},
        price={"unit": "call", "credits": 50, "known": True},
        note="include={begin,end}(초)로 변형 구간만 지정할 수 있다."),
    "sound.looping": dict(
        method="POST", path="/sound/varco/v1/api/looping", body="json", out="audio",
        b64=["source"], required=["source"], rules={},
        price={"unit": "call", "credits": 150, "known": True},
        note="preserve={begin,end}(초)로 반드시 남길 구간을 지정한다."),
    "sound.mono2stereo": dict(
        method="POST", path="/sound/varco/v1/api/mono2stereo", body="json", out="audio",
        b64=["source"], required=["source"], rules={},
        price={"unit": "call", "credits": 50, "known": True}),
    "sound.conversion": dict(
        method="POST", path="/sound/varco/v1/api/conversion", body="json", out="audio",
        b64=["source", "reference"], required=["source", "reference"],
        rules={"ratio": {"min": 0, "max": 2}, "enhance": {"type": "bool"}},
        price={"unit": "call", "credits": 150, "known": True},
        note="사람 목소리(source)에 크리처 음색(reference)을 입힌다. enhance=true 면 잡음도 제거."),
    "sound.enhance": dict(
        method="POST", path="/sound/varco/v1/api/enhance", body="json", out="audio",
        b64=["source"], required=["source"], rules={},
        price={"unit": "call", "credits": 25, "known": True}),

    # ---------------- Voice: TTS ----------------
    "tts.lite": dict(
        method="POST", path="/tts/lite/v1/api/synthesize", body="json", out="audio",
        required=["voice", "text"],
        rules={"text": {"max_bytes": 1200}, "language": {"enum": ["korean", "english", "japanese", "taiwanese"]},
               "n_fm_steps": {"min": 8, "max": 20}, "media_type": {"enum": ["wav", "mp3", "flac"]}},
        price={"unit": "chars", "per": 20, "credits": 1, "known": True},
        note="빠른 응답(실시간 안내·챗봇). voice 에는 voices.tts_lite 의 speaker_uuid 를 넣는다."),
    "tts.standard": dict(
        method="POST", path="/tts/standard/v1/api/synthesize", body="json", out="audio",
        required=["voice", "text"],
        rules={"text": {"max_bytes": 1200}, "language": {"enum": ["korean", "english", "japanese", "taiwanese"]},
               "n_fm_steps": {"min": 8, "max": 20}, "media_type": {"enum": ["wav", "mp3", "flac"]}},
        price={"unit": "chars", "per": 10, "credits": 1, "known": True},
        note="감정·연기 표현(게임 대사·컷신). SSML 을 넣으면 다른 옵션은 무시된다. seed 고정으로 재현."),

    # ---------------- Voice: Conversion ----------------
    "vc.convert": dict(
        method="POST", path="/vc/varco/v1/api/voice-conversion", body="json", out="audio",
        b64=["audio"], required=["audio", "speaker_uuid"], rules={},
        price={"unit": "seconds", "per": 10, "credits": 15, "known": True, "input": "audio"}),
    "vc.convert_custom": dict(
        method="POST", path="/vc/varco/v1/api/voice-conversion-custom", body="json", out="audio",
        b64=["audio", "speaker_audio"], required=["audio", "speaker_audio"], rules={},
        price={"unit": "seconds", "per": 10, "credits": 15, "known": True, "input": "audio"}),
    "vc.acting": dict(
        method="POST", path="/vc/acting/v1/api/voice-conversion", body="json", out="audio",
        b64=["audio"], required=["audio", "speaker_uuid"], rules={},
        price={"unit": "seconds", "per": 10, "credits": 15, "known": False, "input": "audio",
               "assumed_from": "vc.convert"},
        note="연기체 입력의 감정선을 보존한다. 단가 미공개(일반 VC 단가로 가정)."),
    "vc.acting_custom": dict(
        method="POST", path="/vc/acting/v1/api/voice-conversion-custom", body="json", out="audio",
        b64=["audio", "speaker_audio"], required=["audio", "speaker_audio"], rules={},
        price={"unit": "seconds", "per": 10, "credits": 15, "known": False, "input": "audio",
               "assumed_from": "vc.convert_custom"}),

    # ---------------- Voice lists (GET, 무료로 가정) ----------------
    "voices.tts_lite": dict(method="GET", path="/tts/lite/v1/api/voices/varco", body="none", out="json",
                            required=[], rules={}, price={"unit": "free", "known": False}),
    "voices.tts_standard": dict(method="GET", path="/tts/standard/v1/api/voices/varco", body="none", out="json",
                                required=[], rules={}, price={"unit": "free", "known": False}),
    "voices.vc": dict(method="GET", path="/vc/varco/v1/api/voices", body="none", out="json",
                      required=[], rules={}, price={"unit": "free", "known": False}),
    "voices.vc_acting": dict(method="GET", path="/vc/acting/v1/api/voices", body="none", out="json",
                             required=[], rules={}, price={"unit": "free", "known": False}),

    # ---------------- Voice-to-Face ----------------
    "face.blendshape": dict(
        method="POST", path="/fa/asfa/v1.1/blendshape", body="json", out="json",
        b64=["audio"], required=["id", "audio"],
        rules={"lip_style": {"enum": ["balanced", "clear", "minimal", "moderate"]},
               "face_style": {"enum": ["natural", "energetic", "stoic", "timid"]},
               "emotion": {"enum": ["neutral", "angry", "happy", "sad", "surprise"]},
               "neck": {"enum": ["on", "off"]}, "eye": {"enum": ["on", "off"]}},
        price={"unit": "call", "credits": None, "known": False},
        note="음성 → 블렌드셰이프 가중치 JSON(프레임별). 단가 미공개."),

    # ---------------- 3D ----------------
    "3d.image_to_3d": dict(
        method="POST", path="/3d/varco/v1/image-to-3d", body="multipart", out="async_3d",
        files=["image"], required=["image"],
        rules={"image": {"ext": [".png"]}, "target_face_type": {"enum": ["tri", "quad"]},
               "target_face_num": {"min": 1000, "max": 300000}, "generate_texture": {"type": "bool"}},
        price={"unit": "call", "credits": 200, "known": True,
               "variants": {"generate_texture=false": 100}},
        note="PNG 만 받는다. 비동기: requestId → GET /inference/result/{id}. model_url 은 7일 뒤 만료."),

    # ---------------- Image edit (Art Fashion) ----------------
    "image.vton_clothes": dict(
        method="POST", path="/fashion/vton/v1/clothes", body="multipart", out="image",
        files=["model_image", "mask_image", "clothes_image"], required=["clothes_image"],
        objects=["vton", "clothes_spec"], rules={},
        price={"unit": "megapixel", "credits": 75, "min": 75, "known": True}),
    "image.vton_accessories": dict(
        method="POST", path="/fashion/vton/v1/accessories", body="multipart", out="image",
        files=["model_image", "bag_image", "hat_image", "shoes_image"], required=["model_image"],
        objects=["specs"], rules={},
        price={"unit": "megapixel", "credits": 120, "min": 120, "known": True}),
    "image.headswap": dict(
        method="POST", path="/fashion/vton-headswap/v1/headswap", body="multipart", out="image",
        files=["model_image", "face_image"], required=["model_image", "face_image"],
        objects=["headswap"], rules={},
        price={"unit": "megapixel", "credits": 16, "min": 16, "known": True}),
    "image.eraser": dict(
        method="POST", path="/fashion/edit/v1/eraser", body="multipart", out="image",
        files=["image", "mask_image"], required=["image", "mask_image"], rules={},
        price={"unit": "megapixel", "credits": 30, "min": 30, "known": True}),
    "image.inpaint": dict(
        method="POST", path="/fashion/edit/v1/inpaint", body="multipart", out="image",
        files=["image", "mask_image"], required=["model", "image", "mask_image", "prompt"],
        rules={"model": {"enum": ["sdxl", "nano_banana"]}},
        price={"unit": "megapixel", "credits": 120, "min": 120, "known": True}),
    "image.inpaint_image": dict(
        method="POST", path="/fashion/edit/v1/inpaint-image", body="multipart", out="image",
        files=["image", "mask_image", "reference_image", "reference_mask_image"],
        required=["image", "mask_image", "reference_image", "reference_mask_image"], rules={},
        price={"unit": "megapixel", "credits": 120, "min": 120, "known": True}),
    "image.texture": dict(
        method="POST", path="/fashion/edit/v1/texture", body="multipart", out="image",
        files=["image", "mask_image", "texture_image"],
        required=["image", "mask_image", "texture_image", "x", "y", "width", "height", "angle"], rules={},
        price={"unit": "megapixel", "credits": 120, "min": 120, "known": True}),
    "image.perspective": dict(
        method="POST", path="/fashion/edit/v1/perspective", body="multipart", out="image",
        files=["image"], required=["image", "view"],
        rules={"view": {"enum": ["front", "side", "top", "back", "isometric"]}},
        price={"unit": "megapixel", "credits": 30, "min": 30, "known": True}),
    "image.graphic": dict(
        method="POST", path="/fashion/edit/v1/graphic", body="multipart", out="image",
        files=["image", "graphic_image"],
        required=["image", "graphic_image", "x", "y", "width", "height", "angle"],
        rules={"texture": {"enum": ["embossed", "debossed", "embroidered", "printed", "metal"]}},
        price={"unit": "megapixel", "credits": 30, "min": 30, "known": True}),
    "image.background": dict(
        method="POST", path="/fashion/edit/v1/background", body="multipart", out="image",
        files=["image"], required=["mode", "image"],
        rules={"mode": {"enum": ["person", "product"]},
               "output_aspect_ratio": {"enum": ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]},
               "output_image_size": {"enum": ["1K", "2K", "4K"]}},
        price={"unit": "tier", "tiers": {"1K": 120, "2K": 120, "4K": 215}, "param": "output_image_size",
               "default": "2K", "known": True},
        note="입력: 전경만 남기고 배경을 회색(128,128,128)으로 칠한 이미지."),
    "image.upscale": dict(
        method="POST", path="/fashion/upscale/v1/super-resolution", body="multipart", out="image",
        files=["image"], required=["image"], rules={"scale_factor": {"min": 2, "max": 6}},
        price={"unit": "mp_tier", "tiers": [[4, 50], [8, 100], [16, 200], [25, 400], [50, 800],
                                             [100, 1600], [200, 3200]], "known": True}),

    # ---------------- Translate ----------------
    "mt.translate": dict(
        method="POST", path="/mt/chat-content/v1/translate", body="json", out="json",
        required=["TID", "svc", "source_text", "target_lang"],
        rules={"provider": {"enum": ["chat", "content"]},
               "source_lang": {"enum": ["ko", "en", "ja", "tw", "cn", "de", "ru", "es", "pt", "fr"]},
               "target_lang": {"enum": ["ko", "en", "ja", "tw", "cn", "de", "ru", "es", "pt", "fr"]}},
        defaults={"svc": "varco-translation"},
        price={"unit": "call", "credits": None, "known": False},
        note="용어집(Terminology) 기반 번역. provider=chat(채팅체) / content(게임 콘텐츠). 단가 미공개."),
}

BASE_URL = "https://openapi.ai.nc.com"
RESULT_PATH = "/inference/result/{request_id}"

# 공개 REST API 가 없어 사람이 만들거나 다른 경로로 확보해야 하는 에셋 유형
MANUAL_APIS = {
    "manual.unity_music": "배경음악(BGM). VARCO Sound Unity 플러그인의 Music 탭에서만 제공(REST API 없음).",
    "manual.source_image": "3D·이미지 편집의 원본 이미지. VARCO 에 텍스트→이미지 API 가 없다.",
    "manual.recording": "사람이 녹음한 가이드 음성(음성 변환·크리처 변환의 입력).",
}


def _megapixels(width, height):
    return (width * height) / 1_000_000


def estimate_credits(api_id, params=None, *, text=None, audio_seconds=None, out_size=None, calls=1):
    """한 번 호출(calls 회 반복)의 추정 크레딧을 계산한다.

    반환: (credits 또는 None, known: bool, 설명 문자열)
    - credits 가 None 이면 단가를 몰라 계산할 수 없다는 뜻이다.
    - known 이 False 면 추정 단가(다른 API 단가를 빌려 씀)이거나 미공개다.
    """
    params = params or {}
    if api_id in MANUAL_APIS:
        return 0, True, "수동 작업(크레딧 없음)"
    spec = APIS[api_id]
    price = spec["price"]
    unit = price["unit"]
    known = price.get("known", False)

    if unit == "free":
        return 0, known, "목록 조회(무료로 가정)"
    if unit == "call":
        if price.get("credits") is None:
            return None, False, "단가 미공개"
        c = price["credits"]
        if api_id == "3d.image_to_3d" and str(params.get("generate_texture", "true")).lower() == "false":
            c = price["variants"]["generate_texture=false"]
        return c * calls, known, f"{c}/호출"
    if unit == "chars":
        t = text if text is not None else params.get("text", "")
        n = len(t)
        per = price["per"]
        c = -(-n // per) * price["credits"] if n else price["credits"]   # 올림
        return c * calls, known, f"{n}자 ÷ {per}자당 {price['credits']}"
    if unit == "seconds":
        if audio_seconds is None:
            return None, False, "입력 음성 길이를 알아야 계산할 수 있다"
        per = price["per"]
        blocks = max(1, -(-int(round(audio_seconds * 1000)) // (per * 1000)))
        c = blocks * price["credits"]
        note = f"{audio_seconds:.1f}초 → {per}초당 {price['credits']}"
        if not known:
            note += f" ({price.get('assumed_from', '유사 API')} 단가로 가정)"
        return c * calls, known, note
    if unit == "megapixel":
        if not out_size:
            return price["min"] * calls, known, f"출력 크기 미상 → 최소 {price['min']}로 계산"
        mp = _megapixels(*out_size)
        c = max(price["min"], -(-int(mp * 1000) * price["credits"] // 1000))
        return c * calls, known, f"{mp:.2f}MP × {price['credits']}/MP"
    if unit == "tier":
        tier = params.get(price["param"], price["default"])
        c = price["tiers"].get(tier)
        return c * calls, known, f"{price['param']}={tier}"
    if unit == "mp_tier":
        if not out_size:
            return price["tiers"][0][1] * calls, known, "출력 크기 미상 → 최저 구간으로 계산"
        mp = _megapixels(*out_size)
        for limit, c in price["tiers"]:
            if mp <= limit:
                return c * calls, known, f"출력 {mp:.1f}MP ≤ {limit}MP"
        return None, False, f"출력 {mp:.1f}MP 가 200MP 를 넘는다(지원 범위 밖)"
    return None, False, f"알 수 없는 과금 단위 {unit}"


def validate_params(api_id, params, files=None):
    """카탈로그 제약으로 파라미터를 검사한다. 문제 목록(문자열)을 반환하며, 비어 있으면 통과다."""
    files = files or {}
    if api_id not in APIS:
        return [f"알 수 없는 API: {api_id}"]
    spec = APIS[api_id]
    merged = dict(spec.get("defaults", {}))
    merged.update(params or {})
    problems = []
    for key in spec.get("required", []):
        if key not in merged and key not in files:
            problems.append(f"필수 파라미터 누락: {key}")
    for key, rule in spec.get("rules", {}).items():
        if key in files:
            ext = rule.get("ext")
            if ext and not str(files[key]).lower().endswith(tuple(ext)):
                problems.append(f"{key}: 파일 형식은 {ext} 만 허용")
            continue
        if key not in merged:
            continue
        v = merged[key]
        if "enum" in rule and v not in rule["enum"]:
            problems.append(f"{key}={v!r}: 허용값 {rule['enum']}")
        if "min" in rule and isinstance(v, (int, float)) and v < rule["min"]:
            problems.append(f"{key}={v}: 최소 {rule['min']}")
        if "max" in rule and isinstance(v, (int, float)) and v > rule["max"]:
            problems.append(f"{key}={v}: 최대 {rule['max']}")
        if "max_chars" in rule and isinstance(v, str) and len(v) > rule["max_chars"]:
            problems.append(f"{key}: {len(v)}자 > 최대 {rule['max_chars']}자")
        if "max_bytes" in rule and isinstance(v, str) and len(v.encode("utf-8")) > rule["max_bytes"]:
            problems.append(f"{key}: {len(v.encode('utf-8'))}바이트 > 최대 {rule['max_bytes']}바이트(UTF-8)")
        if rule.get("type") == "bool" and not isinstance(v, bool) and str(v).lower() not in ("true", "false"):
            problems.append(f"{key}={v!r}: true/false 만 허용")
    return problems
