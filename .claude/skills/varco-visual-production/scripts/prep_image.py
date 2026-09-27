#!/usr/bin/env python3
"""VARCO 3D·이미지 편집 API 에 넣을 이미지를 준비한다(PIL).

VARCO 이미지 API 는 입력 형식이 까다롭다. Image to 3D 는 PNG 만 받고, 배경 합성(image.background)은
전경만 남기고 나머지를 회색(128,128,128)으로 칠한 이미지를 받고, 편집 API 는 원본과 같은 크기의 마스크를 받는다.
에이전트마다 손으로 가공하지 않도록 같은 명령으로 처리한다.

사용법
  prep_image.py info in.png
  prep_image.py to-png in.jpg out.png
  prep_image.py square in.png out.png [--size 1024] [--fill transparent|gray|white|#RRGGBB] [--margin 0.08]
  prep_image.py remove-bg in.png out.png [--color auto|R,G,B] [--tol 24]     # 단색 배경을 투명하게
  prep_image.py gray-bg in.png out.png                                       # 알파 → 회색(128) 배경
  prep_image.py mask-rect in.png out.png --box x,y,w,h [--invert]            # 흰색=편집 영역
  prep_image.py mask-alpha in.png out.png [--invert] [--grow 0]              # 알파가 있는 곳=흰색
  prep_image.py fit in.png out.png --size 1920x1080 [--mode cover|contain] [--fill ...]   # 스토어 규격 맞춤
  prep_image.py flatten in.png out.png [--fill "#000000"]                   # 알파 제거(App Store 아이콘 등)
  prep_image.py placeholder out.png [--size 512x512]                          # 드라이런 체인용 회색 이미지

결과는 JSON 한 줄로 출력한다.
"""
import argparse
import json
import pathlib
import sys

from PIL import Image, ImageChops, ImageFilter

GRAY = (128, 128, 128)


def color(spec):
    if spec in (None, "transparent"):
        return (0, 0, 0, 0)
    if spec == "gray":
        return GRAY + (255,)
    if spec == "white":
        return (255, 255, 255, 255)
    if spec.startswith("#") and len(spec) == 7:
        return tuple(int(spec[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
    raise ValueError(f"색 형식 오류: {spec}")


def save(im, out, **extra):
    p = pathlib.Path(out)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.suffix.lower() in (".jpg", ".jpeg") and im.mode == "RGBA":
        im = im.convert("RGB")
    im.save(p)
    print(json.dumps({"ok": True, "out": str(p), "size": list(im.size), "mode": im.mode, **extra}, ensure_ascii=False))


def alpha_stats(im):
    if im.mode != "RGBA":
        return {"has_alpha": False}
    a = im.getchannel("A")
    hist = a.histogram()
    total = sum(hist)
    return {"has_alpha": True, "transparent_pct": round(100 * hist[0] / total, 1),
            "bbox": list(a.getbbox()) if a.getbbox() else None}


def cmd_info(a):
    im = Image.open(a.src)
    print(json.dumps({"file": a.src, "format": im.format, "size": list(im.size), "mode": im.mode,
                      "megapixels": round(im.size[0] * im.size[1] / 1e6, 2), **alpha_stats(im.convert("RGBA") if "A" in im.mode else im)},
                     ensure_ascii=False))


def cmd_to_png(a):
    im = Image.open(a.src)
    im = im.convert("RGBA") if ("A" in im.mode or im.mode == "P") else im.convert("RGB")
    save(im, a.dst)


def cmd_square(a):
    im = Image.open(a.src).convert("RGBA")
    bbox = im.getchannel("A").getbbox() if a.crop_alpha else None
    if bbox:
        im = im.crop(bbox)
    side = int(max(im.size) * (1 + 2 * a.margin))
    canvas = Image.new("RGBA", (side, side), color(a.fill))
    canvas.alpha_composite(im, ((side - im.size[0]) // 2, (side - im.size[1]) // 2))
    if a.size:
        canvas = canvas.resize((a.size, a.size), Image.LANCZOS)
    save(canvas, a.dst)


def cmd_remove_bg(a):
    im = Image.open(a.src).convert("RGBA")
    if a.color == "auto":
        w, h = im.size
        corners = [im.getpixel(p)[:3] for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
        bg = tuple(sum(c[i] for c in corners) // 4 for i in range(3))
    else:
        bg = tuple(int(x) for x in a.color.split(","))
    px = im.load()
    removed = 0
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b, al = px[x, y]
            if abs(r - bg[0]) <= a.tol and abs(g - bg[1]) <= a.tol and abs(b - bg[2]) <= a.tol:
                px[x, y] = (r, g, b, 0)
                removed += 1
    save(im, a.dst, background=list(bg), removed_pct=round(100 * removed / (im.size[0] * im.size[1]), 1),
         note="단색 배경에만 쓴다. 복잡한 배경은 사람이 누끼를 따거나 원본을 다시 만든다")


def cmd_gray_bg(a):
    im = Image.open(a.src).convert("RGBA")
    if alpha_stats(im).get("transparent_pct", 0) == 0:
        print(json.dumps({"ok": False, "error": "투명 영역이 없다. 먼저 remove-bg 나 누끼 작업으로 배경을 투명하게 만든다"},
                         ensure_ascii=False))
        sys.exit(1)
    base = Image.new("RGBA", im.size, GRAY + (255,))
    base.alpha_composite(im)
    save(base.convert("RGB"), a.dst, note="image.background 입력: 전경 + 회색(128,128,128) 배경")


def cmd_mask_rect(a):
    im = Image.open(a.src)
    x, y, w, h = (int(v) for v in a.box.split(","))
    m = Image.new("L", im.size, 0)
    m.paste(255, (x, y, x + w, y + h))
    if a.invert:
        m = ImageChops.invert(m)
    save(m, a.dst, box=[x, y, w, h])


def cmd_mask_alpha(a):
    im = Image.open(a.src).convert("RGBA")
    m = im.getchannel("A").point(lambda v: 255 if v > 8 else 0)
    if a.grow > 0:
        m = m.filter(ImageFilter.MaxFilter(a.grow * 2 + 1))
    if a.invert:
        m = ImageChops.invert(m)
    save(m, a.dst)


def cmd_fit(a):
    tw, th = (int(v) for v in a.size.lower().split("x"))
    im = Image.open(a.src).convert("RGBA")
    sw, sh = im.size
    if a.mode == "cover":
        s = max(tw / sw, th / sh)
        im = im.resize((round(sw * s), round(sh * s)), Image.LANCZOS)
        left, top = (im.size[0] - tw) // 2, (im.size[1] - th) // 2
        out = im.crop((left, top, left + tw, top + th))
    else:
        s = min(tw / sw, th / sh)
        im = im.resize((round(sw * s), round(sh * s)), Image.LANCZOS)
        out = Image.new("RGBA", (tw, th), color(a.fill))
        out.alpha_composite(im, ((tw - im.size[0]) // 2, (th - im.size[1]) // 2))
    upscale = max(tw / sw, th / sh) if a.mode == "cover" else min(tw / sw, th / sh)
    save(out, a.dst, scale=round(upscale, 3),
         warning="원본보다 1.5배 넘게 키웠다. image.upscale 로 먼저 키우는 편이 낫다" if upscale > 1.5 else "")


def cmd_flatten(a):
    im = Image.open(a.src).convert("RGBA")
    base = Image.new("RGBA", im.size, color(a.fill))
    base.alpha_composite(im)
    save(base.convert("RGB"), a.dst, note="알파 채널 없음")


def cmd_placeholder(a):
    w, h = (int(v) for v in a.size.lower().split("x"))
    save(Image.new("RGB", (w, h), GRAY), a.dst, placeholder=True)


def main():
    ap = argparse.ArgumentParser(description="VARCO 이미지 입력 준비")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("info"); p.add_argument("src"); p.set_defaults(f=cmd_info)
    p = sub.add_parser("to-png"); p.add_argument("src"); p.add_argument("dst"); p.set_defaults(f=cmd_to_png)
    p = sub.add_parser("square"); p.add_argument("src"); p.add_argument("dst")
    p.add_argument("--size", type=int); p.add_argument("--fill", default="transparent")
    p.add_argument("--margin", type=float, default=0.08); p.add_argument("--crop-alpha", action="store_true", default=True)
    p.set_defaults(f=cmd_square)
    p = sub.add_parser("remove-bg"); p.add_argument("src"); p.add_argument("dst")
    p.add_argument("--color", default="auto"); p.add_argument("--tol", type=int, default=24); p.set_defaults(f=cmd_remove_bg)
    p = sub.add_parser("gray-bg"); p.add_argument("src"); p.add_argument("dst"); p.set_defaults(f=cmd_gray_bg)
    p = sub.add_parser("mask-rect"); p.add_argument("src"); p.add_argument("dst"); p.add_argument("--box", required=True)
    p.add_argument("--invert", action="store_true"); p.set_defaults(f=cmd_mask_rect)
    p = sub.add_parser("mask-alpha"); p.add_argument("src"); p.add_argument("dst")
    p.add_argument("--invert", action="store_true"); p.add_argument("--grow", type=int, default=0); p.set_defaults(f=cmd_mask_alpha)
    p = sub.add_parser("fit"); p.add_argument("src"); p.add_argument("dst"); p.add_argument("--size", required=True)
    p.add_argument("--mode", choices=["cover", "contain"], default="cover"); p.add_argument("--fill", default="transparent")
    p.set_defaults(f=cmd_fit)
    p = sub.add_parser("flatten"); p.add_argument("src"); p.add_argument("dst"); p.add_argument("--fill", default="#000000")
    p.set_defaults(f=cmd_flatten)
    p = sub.add_parser("placeholder"); p.add_argument("dst"); p.add_argument("--size", default="512x512")
    p.set_defaults(f=cmd_placeholder)
    a = ap.parse_args()
    try:
        a.f(a)
    except (OSError, ValueError) as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
