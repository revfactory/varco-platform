#!/usr/bin/env python3
"""이미지 에셋 검사: 크기·비율·모드·알파·단색 여부를 PIL 로 측정해 acceptance 와 대조한다.

사용법
  image_check.py games/x/assets/images/img_hero_01.png --id img_hero --acceptance '{"min_size":[1024,1024]}'
  image_check.py games/x/marketing/mkt_capsule_*.png --id mkt_capsule --acceptance '{"min_size":[616,353],"aspect":"616:353"}'

aspect 는 "16:9" 처럼 쓰며 1% 오차까지 허용한다. 픽셀 표준편차가 2 미만이면 단색(자리표시·빈 이미지)으로 본다.
"""
import argparse
import pathlib
import sys

from PIL import Image, ImageStat

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from qa_common import Report, load_acceptance  # noqa: E402


def measure(path):
    with Image.open(path) as im:
        im.load()
        w, h = im.size
        alpha = im.mode in ("RGBA", "LA", "PA") or "transparency" in im.info
        rgb = im.convert("RGB")
        std = max(ImageStat.Stat(rgb).stddev)
        alpha_min = None
        if alpha:
            alpha_min = im.convert("RGBA").getchannel("A").getextrema()[0]
        return {"format": im.format, "mode": im.mode, "width": w, "height": h, "has_alpha": alpha,
                "alpha_min": alpha_min, "pixel_stddev": round(std, 2)}


def ratio(text):
    a, b = text.split(":")
    return float(a) / float(b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--id", default="image")
    ap.add_argument("--acceptance")
    ap.add_argument("--acceptance-file")
    ap.add_argument("--expect-count", type=int)
    ap.add_argument("--require-alpha", action="store_true", help="투명 배경이 필요한 이미지(아이콘·누끼)")
    ap.add_argument("--out")
    args = ap.parse_args()
    acc = load_acceptance(args.acceptance, args.acceptance_file)
    rep = Report(args.id)

    existing = [f for f in args.files if pathlib.Path(f).is_file()]
    missing = [f for f in args.files if not pathlib.Path(f).is_file()]
    if args.expect_count is not None or missing:
        exp = args.expect_count if args.expect_count is not None else len(args.files)
        rep.add("file_count", len(existing) == exp, f"{len(existing)}/{exp}", f"이미지 없음: {missing[:5]}",
                "빠진 이미지를 다시 생성한다")
    if not existing:
        rep.cannot_verify("검사할 이미지가 없다")
        sys.exit(rep.emit(args.out))

    infos, errors = {}, []
    for f in existing:
        try:
            infos[pathlib.Path(f).name] = measure(f)
        except Exception as e:
            errors.append(f"{pathlib.Path(f).name}: {e}")
    rep.add("decodable", not errors, f"{len(infos)}/{len(existing)}", f"열 수 없는 이미지: {errors}", "다시 생성한다")
    for name, i in infos.items():
        rep.add(f"{name}:not_blank", i["pixel_stddev"] >= 2, f"표준편차 {i['pixel_stddev']}",
                f"{name} 단색 이미지(빈 결과 또는 자리표시)", "입력·마스크를 확인해 다시 생성한다")
        if "min_size" in acc:
            mw, mh = acc["min_size"]
            rep.add(f"{name}:min_size", i["width"] >= mw and i["height"] >= mh, f"{i['width']}x{i['height']}",
                    f"{name} {i['width']}x{i['height']} < 최소 {mw}x{mh}", "image.upscale 로 키운다")
        if "aspect" in acc:
            want = ratio(acc["aspect"])
            got = i["width"] / i["height"]
            rep.add(f"{name}:aspect", abs(got - want) / want <= 0.01, f"{got:.3f} vs {want:.3f}",
                    f"{name} 비율 {got:.3f} 이 {acc['aspect']} 와 다르다",
                    "output_aspect_ratio 를 맞추거나 잘라낸다(PIL crop)")
        if args.require_alpha:
            rep.add(f"{name}:alpha", i["has_alpha"] and (i["alpha_min"] or 0) < 255, f"alpha={i['has_alpha']}",
                    f"{name} 투명 영역이 없다", "배경을 지우고(image.eraser 또는 마스크) 다시 저장한다")
    rep.extra["images"] = infos
    sys.exit(rep.emit(args.out))


if __name__ == "__main__":
    main()
