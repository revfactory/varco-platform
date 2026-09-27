import json, subprocess, urllib.parse, concurrent.futures as cf
T=json.load(open('topics.json'))
def curl(url, body=False):
    fmt='%{http_code} %{size_download} %{url_effective} %{content_type}'
    args=['curl','-sS','-L','--max-time','30','-w',fmt]
    args += ['-o', '/dev/stdout' if body else '/dev/null']
    r=subprocess.run(args+[url],capture_output=True)
    out=r.stdout.decode('utf-8','replace')
    return out, r.stderr.decode()
def meta(url):
    out,err=curl(url)
    p=out.split(' ',3)
    return dict(code=p[0],size=int(p[1]) if len(p)>1 and p[1].isdigit() else 0,eff=p[2] if len(p)>2 else '',ct=p[3] if len(p)>3 else '',err=err.strip())
def check(t):
    base='https://api.varco.ai/ko/'+t['path']
    page=meta(base)
    # title in HTML
    r=subprocess.run(['curl','-sS','-L','--max-time','30',base],capture_output=True).stdout.decode('utf-8','replace')
    import re
    m=re.search(r'<title>(.*?)</title>',r)
    md_url='https://api.varco.ai/api/markdown?url='+urllib.parse.quote(t['md'],safe='')
    r2=subprocess.run(['curl','-sS','-L','--max-time','30','-w','\n%{http_code}',md_url],capture_output=True).stdout.decode('utf-8','replace')
    body,code=r2.rsplit('\n',1)
    imgs=[(u,meta(u)) for u in t['imgs']]
    return dict(path=t['path'],group=t['group'],title=t['title'],
        page_code=page['code'],page_eff=page['eff'],page_title=m.group(1) if m else None,
        md_code=code,md_len=len(body),md_head=body[:120].replace('\n',' '),
        imgs_total=len(imgs),imgs_bad=[(u,x['code'],x['ct']) for u,x in imgs if x['code']!='200' or not x['ct'].startswith('image')])
with cf.ThreadPoolExecutor(6) as ex: res=list(ex.map(check,T))
json.dump(res,open('result.json','w'),ensure_ascii=False,indent=1)
for r in res:
    print(f"{r['page_code']} md={r['md_code']}/{r['md_len']:>6}B img={r['imgs_total']-len(r['imgs_bad'])}/{r['imgs_total']}  {r['path']:<40} | {r['page_title']}")
    if r['imgs_bad']: print('   BAD IMG', r['imgs_bad'])
    if r['page_eff'] != 'https://api.varco.ai/ko/'+r['path']: print('   REDIRECT ->', r['page_eff'])
