"""VARCO API Platform 한국어 문서(/ko/docs, /ko/reference) → 인쇄용 HTML 책자.

산출물: book/body.html, book/cover.html, book/assets/*, book/meta.json
제목 단계: h1 부 · h2 메뉴 묶음 · h3 장 · h4 이하 문서 본문
"""
import concurrent.futures as cf
import hashlib
import html
import json
import os
import re
import subprocess
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
BASE = "https://api.varco.ai"
LANG = "ko"
os.makedirs(ASSETS, exist_ok=True)

SECTIONS = [
    {"key": "docs", "type": "DOCS", "no": "제1부", "title": "도큐먼트",
     "desc": "플랫폼을 시작하는 방법과 서비스별 기능, 활용 사례를 설명하는 문서입니다."},
    {"key": "reference", "type": "REFERENCE", "no": "제2부", "title": "API 레퍼런스",
     "desc": "API마다 엔드포인트, 요청 헤더와 파라미터, 응답 코드와 예시를 정리한 문서입니다."},
]


def curl(args, binary=False):
    r = subprocess.run(["curl", "-sS", "-L", "--fail", "--max-time", "120"] + args, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"curl failed {args[-1]}: {r.stderr.decode()}")
    return r.stdout if binary else r.stdout.decode("utf-8")


def gql(operation, query, variables):
    body = json.dumps({"operationName": operation, "variables": variables, "query": query})
    out = curl(["-X", "POST", f"{BASE}/graphql", "-H", "content-type: application/json", "--data-binary", body])
    data = json.loads(out)
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    return data["data"]


# ---------------------------------------------------------------- 1. 목록
TOPIC = "title path latestVersion pricingRefs versions { version markdownUrl }"
NAV_Q = (
    "query GetNavigationTree($type: NavigationTreeType!, $languageCode: String) {"
    " navigationTree(type: $type, languageCode: $languageCode) { title"
    f" subgroups {{ title subgroups {{ title topics {{ {TOPIC} }} }} topics {{ {TOPIC} }} }}"
    f" topics {{ {TOPIC} }} }} }}"
)
PRICE_Q = (
    "query GetPricingsV2($pricingRefs: [String!], $languageCode: String) {"
    " pricingsV2(pricingRefs: $pricingRefs, languageCode: $languageCode) {"
    " projIdx svcNameDtl category service priceUnit basePrice lang defaultCredit } }"
)


def collect(sec, group, node, sub, out):
    for t in node.get("topics") or []:
        ver = next(v for v in t["versions"] if v["version"] == t["latestVersion"])
        slug = t["path"].split("/")[-1]
        out.append({
            "sec": sec["key"], "group": group, "sub": sub, "slug": slug, "id": f'{sec["key"]}-{slug}',
            "title": t["title"], "path": t["path"], "md_url": ver["markdownUrl"],
            "pricing_refs": t.get("pricingRefs") or [],
        })
    for s in node.get("subgroups") or []:
        collect(sec, group, s, s["title"], out)


for sec in SECTIONS:
    sec["groups"] = []
    for g in gql("GetNavigationTree", NAV_Q, {"type": sec["type"], "languageCode": LANG})["navigationTree"]:
        chs = []
        collect(sec, g["title"], g, None, chs)
        sec["groups"].append({"title": g["title"], "chapters": chs})

chapters = [c for s in SECTIONS for g in s["groups"] for c in g["chapters"]]
KNOWN = {(c["sec"], c["slug"]) for c in chapters}
print("chapters:", {s["key"]: sum(len(g["chapters"]) for g in s["groups"]) for s in SECTIONS})


# ---------------------------------------------------------------- 2. 본문·요금
def fetch_chapter(c):
    c["md"] = curl([f"{BASE}/api/markdown?url=" + urllib.parse.quote(c["md_url"], safe="")])
    c["pricing"] = (
        gql("GetPricingsV2", PRICE_Q, {"pricingRefs": c["pricing_refs"], "languageCode": LANG})["pricingsV2"]
        if c["pricing_refs"] else []
    )
    return c


with cf.ThreadPoolExecutor(6) as ex:
    list(ex.map(fetch_chapter, chapters))


# ---------------------------------------------------------------- 3. 변환
def pandoc(md, prefix):
    r = subprocess.run(
        ["pandoc", "-f", "gfm", "-t", "html", "--wrap=none", f"--id-prefix={prefix}"],
        input=md.encode("utf-8"), capture_output=True, check=True)
    return r.stdout.decode("utf-8")


def rewrite_href(href, cur_sec):
    """문서끼리의 링크는 책자 안 앵커로, 나머지 상대 경로는 사이트 절대 주소로 바꾼다."""
    if href.startswith(("#", "mailto:")):
        return href
    m = re.match(rf"^(?:{re.escape(BASE)})?/{LANG}/(docs|reference)/([^?#/]+)", href)
    if m and (m.group(1), m.group(2)) in KNOWN:
        return f"#{m.group(1)}-{m.group(2)}"
    m = re.match(r"^\.\./(docs|reference)/([^?#/]+)", href)
    if m:
        if (m.group(1), m.group(2)) in KNOWN:
            return f"#{m.group(1)}-{m.group(2)}"
        return f"{BASE}/{LANG}/{m.group(1)}/" + href[len("../" + m.group(1) + "/"):]
    if href.startswith("/"):
        return BASE + href
    bare = href.split("?")[0].split("#")[0]
    if not re.match(r"^[a-z]+:", href) and (cur_sec, bare) in KNOWN:
        return f"#{cur_sec}-{bare}"
    return href


def media_name(url):
    return urllib.parse.unquote(url.rstrip("/").split("/")[-1])


def audio_card(m):
    src = re.search(r'src="([^"]+)"', m.group(0)).group(1)
    return (f'<a class="media-card audio" href="{src}"><span class="ico">♪</span>'
            f'<span class="txt"><span class="k">오디오</span>{html.escape(media_name(src))}</span></a>')


VIDEOS = []


def video_card(m):
    src = re.search(r'src="([^"]+)"', m.group(0)).group(1)
    VIDEOS.append(src)
    return (f'<figure class="video"><a class="video-link" href="{src}">'
            f'<img class="poster" data-video="{src}" alt="영상 미리보기"></a>'
            f'<figcaption>영상 · <a href="{src}">{html.escape(media_name(src))}</a>'
            f'<span class="dur" data-video="{src}"></span></figcaption></figure>')


PRICE_HEAD = "API 서비스 별 가격 표(Per-Service Pricing)"
PRICE_DESC = ("API 서비스별로 최적화된 과금 단위를 제공합니다. 사용자는 필요한 기능만 선택해 사용할 수 있으며, "
              "각 API의 사용량에 따라 명확하고 일관된 요금이 산정됩니다. 모든 요금은 1회 호출 단가 또는 처리 단위 "
              "(Token, Image, Audio Second 등) 기준으로 계산되며, 사용량은 대시보드에서 확인할 수 있습니다.")


def pricing_html(c):
    if not c["pricing"]:
        return ""
    def e(v):  # 요금 데이터 안의 <br> 은 사이트처럼 줄바꿈으로 살리고 나머지는 이스케이프
        return re.sub(r"\s*&lt;br\s*/?&gt;\s*", "<br>", html.escape(v or ""))

    rows = "".join(
        f"<tr><td>{e(p['category'])}</td><td>{e(p['service'])}</td><td>{e(p['priceUnit'])}</td>"
        f"<td>{e(p['basePrice'])}</td><td class='num'>{e(p['defaultCredit'])}</td></tr>"
        for p in c["pricing"])
    keep = " keep" if len(c["pricing"]) <= 8 else ""   # 짧은 요금표는 쪽이 갈리지 않게 한 덩어리로
    return (f'<section class="pricing{keep}"><h4 id="{c["id"]}--pricing">{PRICE_HEAD}</h4><p>{PRICE_DESC}</p>'
            '<table class="price-table"><colgroup><col style="width:17%"><col style="width:22%">'
            '<col style="width:16%"><col style="width:31%"><col style="width:14%"></colgroup>'
            '<thead><tr><th>Category</th><th>Service</th><th>과금 단위</th>'
            '<th>기본 단가</th><th class="num">호출에 필요한<br>최소 크레딧</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></section>')


def convert(c):
    s = pandoc(c["md"], f"{c['id']}--")
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)                                   # 화면에 안 보이는 주석
    s = re.sub(r'<a href="#[^"]*" aria-hidden="true" tabindex="-1"></a>', "", s)  # 코드 줄 앵커
    s = re.sub(r"<audio\b[^>]*>.*?</audio>", audio_card, s, flags=re.S)
    s = re.sub(r"<video\b[^>]*>.*?</video>", video_card, s, flags=re.S)
    s = re.sub(r'href="([^"]*)"',
               lambda m: f'href="{html.escape(rewrite_href(html.unescape(m.group(1)), c["sec"]))}"', s)
    levels = [int(x) for x in re.findall(r"<h([1-6])\b", s)]
    if levels:
        shift = 4 - min(levels)
        s = re.sub(r"<(/?)h([1-6])\b", lambda m: f"<{m.group(1)}h{min(6, int(m.group(2)) + shift)}", s)
    # 16줄 이하 코드 블록은 쪽이 갈리지 않게 표시
    s = re.sub(r"<pre\b(?=[^>]*>(.*?)</pre>)",
               lambda m: "<pre data-keep" if m.group(1).count("\n") < 16 else "<pre", s, flags=re.S)
    s = re.sub(r'(<img\b[^>]*src="https://img\.shields\.io[^"]*")', r'\1 class="badge"', s)
    s = re.sub(r'<a href="(https://(?:www\.youtube\.com|youtu\.be)[^"]*)">(\s*<img)', r'<a class="yt" href="\1">\2', s)
    c["html"] = s + pricing_html(c)


for c in chapters:
    convert(c)


# ---------------------------------------------------------------- 4. 이미지·영상
def ext_for(url, ctype):
    path_ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
    if path_ext in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"):
        return path_ext
    return {"image/svg+xml": ".svg", "image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp",
            "image/gif": ".gif"}.get(ctype.split(";")[0].strip(), ".bin")


def download(url):
    key = hashlib.sha1(url.encode()).hexdigest()[:16]
    for f in os.listdir(ASSETS):
        if f.startswith(key + ".") and not f.endswith(".part"):
            return url, "assets/" + f
    tmp = os.path.join(ASSETS, key + ".part")
    ctype = subprocess.run(["curl", "-sS", "-L", "--fail", "--max-time", "120", "-o", tmp, "-w", "%{content_type}", url],
                           capture_output=True, check=True, text=True).stdout
    name = key + ext_for(url, ctype)
    os.replace(tmp, os.path.join(ASSETS, name))
    return url, "assets/" + name


img_urls = sorted({html.unescape(u) for c in chapters
                   for u in re.findall(r'<img\b[^>]*?src="(https?://[^"]+)"', c["html"])})
def optimize(rel):
    """큰 PNG 는 흰 바탕에 합성해 JPEG(품질 90, 가로 최대 2000px)로 바꿔 PDF 용량을 줄인다.
    책자 바탕이 흰색이라 투명 영역을 흰색으로 채워도 보이는 모습은 같다."""
    from PIL import Image
    p = os.path.join(HERE, rel)
    if not rel.endswith(".png") or os.path.getsize(p) < 400_000:
        return rel
    im = Image.open(p).convert("RGBA")
    white = Image.new("RGBA", im.size, (255, 255, 255, 255))
    im = Image.alpha_composite(white, im).convert("RGB")
    if im.width > 2000:
        im = im.resize((2000, round(im.height * 2000 / im.width)), Image.LANCZOS)
    out = rel[:-4] + "-opt.jpg"
    im.save(os.path.join(HERE, out), "JPEG", quality=90, optimize=True)
    return out


with cf.ThreadPoolExecutor(8) as ex:
    local = {u: optimize(r) for u, r in ex.map(download, img_urls)}

video_info = {}
for v in sorted(set(VIDEOS)):
    key = hashlib.sha1(v.encode()).hexdigest()[:16]
    mp4 = os.path.join(ASSETS, key + ".mp4")
    poster = os.path.join(ASSETS, key + "-poster.jpg")
    if not os.path.exists(mp4):
        curl(["-o", mp4, v])
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4],
                               capture_output=True, text=True, check=True).stdout.strip())
    if not os.path.exists(poster):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{dur * 0.3:.2f}", "-i", mp4,
                        "-frames:v", "1", "-q:v", "3", poster], check=True)
    video_info[v] = {"poster": "assets/" + os.path.basename(poster), "dur": f"{int(dur) // 60}:{int(dur) % 60:02d}"}

for c in chapters:
    s = re.sub(r'(<img\b[^>]*?src=")(https?://[^"]+)(")',
               lambda m: m.group(1) + local[html.unescape(m.group(2))] + m.group(3), c["html"])
    s = re.sub(r'<img class="poster" data-video="([^"]+)"',
               lambda m: f'<img class="poster" src="{video_info[html.unescape(m.group(1))]["poster"]}"', s)
    s = re.sub(r'<span class="dur" data-video="([^"]+)"></span>',
               lambda m: f'<span class="dur"> · {video_info[html.unescape(m.group(1))]["dur"]}</span>', s)
    c["html"] = s

# ---------------------------------------------------------------- 5. 조립
e = html.escape


def label_of(c):
    return f'<span class="pre">{e(c["sub"])} · </span>{e(c["title"])}' if c["sub"] else e(c["title"])


def plain_of(c):
    return f'{c["sub"]} · {c["title"]}' if c["sub"] else c["title"]


toc_cols, body, anchors = [], [], []   # anchors: 목차에 쪽수를 채울 제목 (단계, id) — 문서 순서
for si, sec in enumerate(SECTIONS):
    sid = f'sec-{sec["key"]}'
    n_ch = sum(len(g["chapters"]) for g in sec["groups"])
    sec["n_ch"] = n_ch
    anchors.append((1, sid))
    rows = [f'<li class="toc-sec"><a href="#{sid}"><span class="no">{sec["no"]}</span>'
            f'<span class="t">{e(sec["title"])}</span><span class="dots"></span>'
            f'<span class="pg" data-for="{sid}">00</span></a></li>']
    overview = []
    for gi, g in enumerate(sec["groups"]):
        gid = f'{sid}-g{gi + 1}'
        g["id"] = gid
        anchors.append((2, gid))
        rows.append(f'<li class="toc-grp"><a href="#{gid}"><span class="t">{e(g["title"])}</span>'
                    f'<span class="dots"></span><span class="pg" data-for="{gid}">00</span></a></li>')
        for c in g["chapters"]:
            anchors.append((3, c["id"]))
            rows.append(f'<li class="toc-ch"><a href="#{c["id"]}"><span class="t">{label_of(c)}</span>'
                        f'<span class="dots"></span><span class="pg" data-for="{c["id"]}">00</span></a></li>')
        # 서비스(하위 묶음)별로 한 줄씩: "Sound  Overview · Conversion · …"
        lines, by_sub = [], {}
        for c in g["chapters"]:
            by_sub.setdefault(c["sub"], []).append(c)
        for sub, chs in by_sub.items():
            names = " · ".join(f'<a href="#{c["id"]}">{e(c["title"])}</a>' for c in chs)
            lines.append(f'<div class="ov-line">{f"<span class=ov-sub>{e(sub)}</span>" if sub else ""}{names}</div>')
        overview.append(f'<div class="ov-row"><div class="ov-grp">{e(g["title"])}</div>'
                        f'<div class="ov-chs">{"".join(lines)}</div></div>')
    toc_cols.append(f'<ol class="toc-col">{"".join(rows)}</ol>')

    body.append(
        f'<section class="sec-div" id="{sid}-page"><div class="sec-no">{sec["no"]}</div>'
        f'<h1 class="sec-title" id="{sid}">{e(sec["title"])}</h1>'
        f'<p class="sec-desc">{e(sec["desc"])} 모두 {n_ch}편입니다.</p>'
        f'<div class="ov">{"".join(overview)}</div></section>')
    for g in sec["groups"]:
        for ci, c in enumerate(g["chapters"]):
            grp = (f'<h2 class="grp" id="{g["id"]}">{e(g["title"])}</h2>' if ci == 0
                   else f'<span class="grp">{e(g["title"])}</span>')
            sub = f'<span class="grp-sub"> / {e(c["sub"])}</span>' if c["sub"] else ""
            src = f'{BASE}/{LANG}/{c["path"]}'
            body.append(
                f'<article class="chapter {c["sec"]}" id="{c["id"]}-page"><header class="ch-head">'
                f'<div class="crumb">{grp}{sub}</div>'
                f'<h3 class="ch-title" id="{c["id"]}">{label_of(c)}</h3>'
                f'<div class="src">원문 <a href="{src}">{src.replace("https://", "")}</a></div></header>'
                f'<div class="doc">{c["html"]}</div></article>')

stats = {
    "chapters": {s["key"]: s["n_ch"] for s in SECTIONS},
    "images": len(local),
    "videos": len(video_info),
    "audios": sum(c["html"].count('class="media-card audio"') for c in chapters),
    "pricing_tables": sum(1 for c in chapters if c["pricing"]),
}
n_docs, n_ref = stats["chapters"]["docs"], stats["chapters"]["reference"]

template = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
out = (template.replace("{{TOC}}", "\n".join(toc_cols)).replace("{{BODY}}", "\n".join(body))
       .replace("{{N_DOCS}}", str(n_docs)).replace("{{N_REF}}", str(n_ref)))
open(os.path.join(HERE, "body.html"), "w", encoding="utf-8").write(out)

cover = open(os.path.join(HERE, "cover_template.html"), encoding="utf-8").read()
cover_secs = "".join(
    f'<div class="c-sec"><div class="c-no">{s["no"]}</div><div class="c-t">{e(s["title"])}</div>'
    f'<div class="c-g">{" · ".join(e(g["title"]) for g in s["groups"])}</div></div>' for s in SECTIONS)
cover = (cover.replace("{{SECTIONS}}", cover_secs).replace("{{N_DOCS}}", str(n_docs))
         .replace("{{N_REF}}", str(n_ref)))
open(os.path.join(HERE, "cover.html"), "w", encoding="utf-8").write(cover)

json.dump({"stats": stats, "anchors": anchors,
           "labels": {c["id"]: plain_of(c) for c in chapters}},
          open(os.path.join(HERE, "meta.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(stats, ensure_ascii=False))
