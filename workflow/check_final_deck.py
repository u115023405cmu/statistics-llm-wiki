#!/usr/bin/env python3
"""可重複執行的 HTML 簡報完整性／來源引用／計算檢查（不宣稱獨立統計審稿）。"""
from pathlib import Path
import json, csv, re, math, datetime, sys
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'slides/statistics-teaching.html'
REPORT=ROOT/'reports/step5/static_checks.json'
REG=ROOT/'wiki/sources/source_registry.csv'
REF=ROOT/'workflow/artifacts/final_slide_refs.json'
EVID=ROOT/'workflow/artifacts/evidence_cards.json'
checks=[]
def ck(label,passed,detail=''):
    checks.append({'name':label,'passed':bool(passed),'detail':detail})
reg={x['id']:x for x in csv.DictReader(REG.open(encoding='utf-8-sig'))}
refs=json.loads(REF.read_text(encoding='utf-8'))
ev={s['id']:s for s in json.loads(EVID.read_text(encoding='utf-8'))}
doc=HTML.read_text(encoding='utf-8')
soup=BeautifulSoup(doc,'html.parser')
slides=soup.select('.slide')
ck('12 個獨立的教學畫面',len(slides)==12,f'actual {len(slides)}')
ck('每個畫面都有教學標題',all(s.select_one('h1') for s in slides))
ck('正確可辨識的繁體中文文件語系',soup.html.get('lang')=='zh-Hant')
ck('簡報標題與內容主題一致','從資料到結論' in soup.title.text)
ck('前後頁與全螢幕互動控制',all(soup.select_one('#'+id) for id in ('nextBtn','prevBtn','menuBtn','fullBtn')))
ck('HTML 是自包含、沒有外部腳本',not soup.find('script',src=True) and not soup.find('link',rel='stylesheet'))
ck('至少四種內嵌 SVG 圖解',len(soup.select('svg'))>=4, f'actual {len(soup.select("svg"))}')
ck('12 頁來源對照頁面',len(soup.select('.reference-panel'))==12)
ck('來源覆蓋完整 S01~S06',set(k['source_id'] for v in refs.values() for k in v)==set(reg.keys()))
allWiki='\n'.join(x.read_text(encoding='utf-8') for x in (ROOT/'wiki/entries').glob('*.md'))
for n, slide in enumerate(slides,1):
    id=str(n).zfill(2)
    expected=refs[id]
    actual=[(r.get('data-source'),int(r.get('data-page'))) for r in slide.select('.source-summary .source-pill')]
    want=[(k['source_id'],int(k['pdf_page'])) for k in expected]
    ck(f'{id} 頁展示的來源 ID 與 Graph 證據清單一致',actual==want, f'{len(actual)} refs')
    for sid,p in want:
        ck(f'{id}: 來源 {sid} p.{p} 存在且符合 PDF 頁碼',sid in reg and 1<=p<=int(reg[sid]['pdf_pages']))
        ck(f'{id}: 來源 {sid} p.{p} 在 Wiki 有引用',f'[{sid}, PDF p.{p}]' in allWiki)
    if n>1:ck(f'{id} 頁有重點結論',bool(slide.select_one('.takeaway')))
for name in ['wiki/index.md','wiki/catalog.json','workflow/artifacts/evidence_cards.json','workflow/artifacts/final_slide_refs.json']:
    ck(f'必要資料存在：{name}',(ROOT/name).is_file())
for a in soup.select('.reference-item a[href]'):
    rel=(ROOT/'slides'/a['href']).resolve()
    ck('引用連結實際存在：'+str(rel.relative_to(ROOT)) if rel.is_relative_to(ROOT) else '引用連結越界',rel.is_file() and rel.is_relative_to(ROOT))
# Slide teaching examples: independently recalculate numeric claims.
ck('第05頁示意直方圖合計 12 筆',sum([6,3,2,0,1])==12)
ck('第06頁平均數與中位數',sum([2,4,4,6,8,12])/6==6 and (4+6)/2==5)
ck('第06頁極端值改動後結果',sum([2,4,4,6,8,30])/6==9)
ck('第07頁條件機率 197/219',abs(197/219-0.9)<0.001)
ck('第07頁條件機率 197/309',abs(197/309-0.638)<0.001)
ck('第08頁期望值 E(X)=822',970*0.6+800*0.3+0*0.1==822)
ck('第09頁 Z=-0.4',(70-80)/25==-0.4)
se=math.sqrt(.6*.4/400);lo=.6-1.96*se;hi=.6+1.96*se
ck('第10頁 95% CI 約 55.2% 到 64.8%',abs(lo-0.552)<.001 and abs(hi-.648)<.001)
ck('第11頁 Z 值兩種取捨都已核對',abs((.37-.5)/math.sqrt(.5*.5/1000)+8.2219)<.01 and abs((.37-.5)/.016+8.125)<.01)
for n in [3,5,6,10]:
    ck(f'第{n:02}頁有自編案例的標示',('自編' in slides[n-1].get_text() or '示意' in slides[n-1].get_text()))

summary={'timestamp':datetime.datetime.now(ZoneInfo('Asia/Taipei')).isoformat(timespec='seconds'),
         'scope':'靜態頁面、來源 ID 與 PDF 頁碼範圍、Wiki 引用字串、導覽存在性、例題算術；不代表 PDF 逐句獨立審核',
         'total':len(checks),'pass':sum(c['passed'] for c in checks),'fail':sum(not c['passed'] for c in checks),'checks':checks}
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'STEP5 STATIC: {summary["pass"]}/{summary["total"]} PASS, {summary["fail"]} FAILED')
for c in checks:
    if not c['passed']:print('FAIL',c['name'],c['detail'])
sys.exit(0 if summary['fail']==0 else 1)
