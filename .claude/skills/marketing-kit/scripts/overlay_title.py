#!/usr/bin/env python3
"""키 아트 위에 게임 제목(로고 이미지 또는 텍스트)을 얹는다.

VARCO 에는 글자를 그리는 API 가 없다. Steam 캡슐처럼 제목이 읽혀야 하는 이미지는 여기서 제목을 얹는다.
로고 PNG 가 있으면 그것을 쓰고, 없으면 시스템 글꼴로 텍스트를 그린다(임시 로고). 임시 로고를 썼다는 사실을
결과 JSON 의 temporary_logo 로 알린다.

사용법
  overlay_title.py in.png out.png --logo logo.png [--pos center|bottom|top|left] [--scale 0.6]
  overlay_title.py in.png out.png --text "네온 드리프트" [--pos bottom] [--scale 0.7] [--font 경로]
"""
import argparse
import json
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_CANDIDATES = [
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
]


def place(canvas, layer, pos):
    W, H = canvas.size
    w, h = layer.size
    m = int(min(W, H) * 0.06)
    return {"center": ((W - w) // 2, (H - h) // 2), "bottom": ((W - w) // 2, H - h - m),
            "top": ((W - w) // 2, m), "left": (m, (H - h) // 2)}[pos]


def text_layer(text, target_w, font_path):
    path = font_path or next((f for f in FONT_CANDIDATES if pathlib.Path(f).exists()), None)
    if not path:
        raise OSError("글꼴을 찾지 못했다. --font 로 지정한다")
    size = 200
    font = ImageFont.truetype(path, size)
    w = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), text, font=font)[2]
    font = ImageFont.truetype(path, max(12, int(size * target_w / max(w, 1))))
    x0, y0, x1, y1 = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), text, font=font)
    pad = int((y1 - y0) * 0.3)
    layer = Image.new("RGBA", (x1 - x0 + pad * 2, y1 - y0 + pad * 2), (0, 0, 0, 0))
    shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text((pad - x0 + 4, pad - y0 + 4), text, font=font, fill=(0, 0, 0, 200))
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(layer).text((pad - x0, pad - y0), text, font=font, fill=(255, 255, 255, 255))
    return layer, path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--logo")
    g.add_argument("--text")
    ap.add_argument("--pos", choices=["center", "bottom", "top", "left"], default="center")
    ap.add_argument("--scale", type=float, default=0.6, help="제목 폭 / 이미지 폭")
    ap.add_argument("--font")
    a = ap.parse_args()
    try:
        canvas = Image.open(a.src).convert("RGBA")
        target_w = int(canvas.size[0] * a.scale)
        font_used = None
        if a.logo:
            layer = Image.open(a.logo).convert("RGBA")
            ratio = target_w / layer.size[0]
            layer = layer.resize((target_w, int(layer.size[1] * ratio)), Image.LANCZOS)
        else:
            layer, font_used = text_layer(a.text, target_w, a.font)
        if layer.size[1] > canvas.size[1] * 0.8:
            ratio = canvas.size[1] * 0.8 / layer.size[1]
            layer = layer.resize((int(layer.size[0] * ratio), int(layer.size[1] * ratio)), Image.LANCZOS)
        canvas.alpha_composite(layer, place(canvas, layer, a.pos))
        out = pathlib.Path(a.dst)
        out.parent.mkdir(parents=True, exist_ok=True)
        (canvas.convert("RGB") if out.suffix.lower() in (".jpg", ".jpeg") else canvas).save(out)
        print(json.dumps({"ok": True, "out": str(out), "size": list(canvas.size), "temporary_logo": bool(a.text),
                          "font": font_used}, ensure_ascii=False))
    except (OSError, ValueError) as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
