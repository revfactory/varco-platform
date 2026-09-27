"""body.html·cover.html → PDF. 1차 렌더의 책갈피로 쪽수를 구해 목차를 채운 뒤 다시 렌더하고 표지를 붙인다."""
import asyncio
import json
import os
import re
import sys

from playwright.async_api import async_playwright
from pypdf import PdfReader, PdfWriter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
meta = json.load(open(os.path.join(HERE, "meta.json")))
ANCHORS = [tuple(a) for a in meta["anchors"]]  # (단계, id) — 문서 순서

FOOTER = (
    '<div style="width:100%;box-sizing:border-box;padding:0 18mm;display:flex;justify-content:space-between;'
    "align-items:center;font-family:Pretendard,'Apple SD Gothic Neo',sans-serif;font-size:7.5pt;color:#9aa1ac;\">"
    '<span>VARCO API Platform 레퍼런스 매뉴얼</span>'
    '<span class="pageNumber" style="color:#697180;font-weight:600;"></span></div>'
)


async def render(page, html_path, pdf_path, cover=False):
    await page.goto("file://" + html_path, wait_until="load")
    await page.evaluate("document.fonts.ready")
    await page.wait_for_function("Array.from(document.images).every(i => i.complete)")
    broken = await page.evaluate("Array.from(document.images).filter(i => !i.naturalWidth).map(i => i.src)")
    if broken:
        raise RuntimeError(f"깨진 이미지: {broken}")
    opts = {"path": pdf_path, "format": "A4", "print_background": True}
    if cover:
        opts.update(margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}, prefer_css_page_size=True)
    else:
        opts.update(margin={"top": "18mm", "bottom": "20mm", "left": "18mm", "right": "18mm"},
                    display_header_footer=True, header_template="<div></div>", footer_template=FOOTER,
                    outline=True, tagged=True)
    await page.pdf(**opts)


def heading_pages(pdf_path):
    """책갈피에서 1~3단계(부·묶음·장) 제목의 쪽 번호(1부터)를 문서 순서대로 뽑는다."""
    r = PdfReader(pdf_path)
    out = []

    def walk(items, level):
        for it in items:
            if isinstance(it, list):
                walk(it, level + 1)
            elif level <= 3:
                out.append((level, it.title, r.get_destination_page_number(it) + 1))

    walk(r.outline, 1)
    return out, len(r.pages)


def fill_toc(src_html, pages):
    s = open(src_html, encoding="utf-8").read()
    for (_, aid), pg in pages.items():
        s, n = re.subn(rf'(data-for="{re.escape(aid)}">)00(<)', rf"\g<1>{pg}\g<2>", s)
        assert n == 1, aid
    return s


async def main():
    body_html = os.path.join(HERE, "body.html")
    final_html = os.path.join(HERE, "body_final.html")
    pass1, pass2 = os.path.join(HERE, "pass1.pdf"), os.path.join(HERE, "pass2.pdf")
    cover_pdf = os.path.join(HERE, "cover.pdf")
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        page = await b.new_page()
        await render(page, body_html, pass1)
        h1, _ = heading_pages(pass1)
        if [lv for lv, _, _ in h1] != [lv for lv, _ in ANCHORS]:
            raise RuntimeError(f"책갈피 구조가 예상과 다름: {len(h1)} vs {len(ANCHORS)}")
        pages = {a: pg for a, (_, _, pg) in zip(ANCHORS, h1)}
        open(final_html, "w", encoding="utf-8").write(fill_toc(body_html, pages))
        await render(page, final_html, pass2)
        h2, n_body = heading_pages(pass2)
        if [pg for _, _, pg in h2] != [pg for _, _, pg in h1]:
            raise RuntimeError("2차 렌더에서 쪽수가 달라짐")
        await render(page, os.path.join(HERE, "cover.html"), cover_pdf, cover=True)
        await b.close()

    w = PdfWriter(clone_from=pass2)
    w.insert_page(PdfReader(cover_pdf).pages[0], 0)
    w.set_page_label(0, 0, prefix="표지")
    w.set_page_label(1, n_body, style="/D", start=1)
    w.page_mode = "/UseOutlines"
    w.add_metadata({
        "/Title": "VARCO API Platform 레퍼런스 매뉴얼 (한국어판)",
        "/Subject": "api.varco.ai 도큐먼트·API 레퍼런스 한국어 문서 모음 (2026-09-28 기준)",
        "/Keywords": "VARCO, API, 도큐먼트, API 레퍼런스",
    })
    with open(OUT, "wb") as f:
        w.write(f)
    print(json.dumps({"body_pages": n_body, "total_pages": n_body + 1,
                      "toc": [(lv, t, pg) for lv, t, pg in h2 if lv <= 2]}, ensure_ascii=False))


asyncio.run(main())
