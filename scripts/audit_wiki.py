#!/usr/bin/env python3
"""可重複執行的 Wiki 結構/引文/數值稽核；不宣稱取代內容專家審查。"""
from pathlib import Path
import csv,re,json,hashlib,math,sys,datetime
root=Path(__file__).resolve().parents[1]
reg=list(csv.DictReader((root/'wiki/sources/source_registry.csv').open(encoding='utf-8-sig',newline='')))
source={row['id']:row for row in reg}
errors=[];warnings=[];checks=[]
def chk(label,ok,detail):
    checks.append({'check':label,'ok':bool(ok),'detail':detail})
    if not ok:errors.append(f'{label}: {detail}')
chk('六個來源登記且 ingest 標記完成',len(reg)==6 and sum(r['ingested']=='是' for r in reg)>=5,f'登記 {len(reg)}，已 ingest {sum(r["ingested"]=="是" for r in reg)}')
entry_files=sorted((root/'wiki/entries').glob('*.md'))
chk('至少五篇知識條目',len(entry_files)>=5,f'有 {len(entry_files)} 篇')
cit_re=re.compile(r'\[(S\d{2}), PDF p\.(\d+)\]')
all_ids=set();counts={};total=0
for entry in entry_files:
 txt=entry.read_text(encoding='utf-8');cit=cit_re.findall(txt);counts[entry.name]=len(cit)
 chk('條目長度與引用 '+entry.name,len(txt)>=1500 and len(cit)>=8,f'文字數 {len(txt)}，引用數 {len(cit)}')
 for sid,pageno in cit:
  total+=1;all_ids.add(sid)
  if sid not in source:errors.append(f'{entry.name}: 未登記來源 {sid}')
  elif not 1 <= int(pageno) <= int(source[sid]['pdf_pages']):errors.append(f'{entry.name}: {sid} PDF p.{pageno} 不存在')
for sid,row in source.items():
 card=root/'wiki/sources/cards'/f'{sid}.md'
 mp=root/'wiki/sources/page_maps'/f'{sid}-page-map.md'
 chk('來源卡及頁面索引 '+sid,card.is_file() and mp.is_file(),f'{card.relative_to(root)} / {mp.relative_to(root)}')
 if card.is_file():
  c=card.read_text(encoding='utf-8');nums=[int(x) for x in re.findall(r'\| p\.(\d+) \|',c)]
  chk('來源卡至少5個定位點 '+sid,len(nums)>=5 and all(1<=n<=int(row['pdf_pages']) for n in nums),f'{len(nums)} 個定位頁')
 if mp.is_file():
  m=mp.read_text(encoding='utf-8');page_nums=[int(x) for x in re.findall(r'^- PDF p\.(\d+):',m,re.M)]
  chk('逐頁索引頁數 '+sid,page_nums==list(range(1,int(row['pdf_pages'])+1)),f'{len(page_nums)}/{row["pdf_pages"]} 頁')
 raw=root/row['local_location']
 if raw.exists():
  h=hashlib.sha256(raw.read_bytes()).hexdigest();chk('本機 PDF SHA-256 '+sid,h==row['sha256'],row['filename'])
 else:warnings.append(f'本機沒有私人 PDF {sid}，略過雜湊驗證（公開 ZIP 不含 raw PDF，預期情況）')
chk('六份來源都有被 Wiki 引用',all(r['id'] in all_ids for r in reg),f'已引用來源 {sorted(all_ids)}')
# 檢查自編例題數值；這僅檢查幾個關鍵演算，不構成全篇數學證明。
calc={
 'S02 sample variance':(sum((x-6)**2 for x in [2,4,4,6,8,12])/5,12.8,1e-9),
 'S03 expected revenue':(970*.6+800*.3,822,1e-9),
 'S03 variance revenue':(.6*(970-822)**2+.3*(800-822)**2+.1*(0-822)**2,80856,1e-9),
 'S03 conditional P':(197/219,.900,0.0007),
 'S04 geometric':((.4**4)*.6,.01536,1e-9),
 'S04 binomial':(4*.5**4,.25,1e-9),
 'S05 CI lower':(.887-1.96*math.sqrt(.887*.113/1000),.867,0.0005),
 'S05 CI upper':(.887+1.96*math.sqrt(.887*.113/1000),.907,0.0005),
 'S05 self example lower':(.6-1.96*math.sqrt(.6*.4/400),.552,0.0005),
 'S05 self example upper':(.6+1.96*math.sqrt(.6*.4/400),.648,0.0005),
 'S06 exact z':((.37-.50)/math.sqrt(.5*.5/1000),-8.22,0.01),
 'S06 rounded intermediate z':((.37-.5)/.016,-8.13,0.01),
 'S06 self example z':((.4-.5)/math.sqrt(.5*.5/200),-2.83,0.01),
}
for key,(got,want,tol) in calc.items():chk('計算驗證 '+key,abs(got-want)<=tol,f'實際 {got:.7f}，預期約 {want}，容許 {tol}')
# Content citation ranges only: semantics/visual layout must be independently checked later.
report={'time':'2026-11-23','source_count':len(reg),'ingested':sum(r['ingested']=='是' for r in reg),'wiki_entries':len(entry_files),'source_reference_count':total,'source_ids_in_entries':sorted(all_ids),'checks':checks,'passed':sum(c['ok'] for c in checks),'failed':len(errors),'errors':errors,'warnings':warnings,'scope_note':'本腳本只核對來源ID、PDF頁碼有效性、檔案SHA、索引完整性及部分自編數值。它不會自動判定整篇內容是否忠於原文，也不會檢查尚未產生的HTML簡報。'}
(root/'reports/audit_wiki.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Wiki audit: {report["passed"]}/{len(checks)} checks passed, {len(errors)} errors. {len(entry_files)} entries, {total} anchored citations.')
for e in errors:print('ERROR:',e)
for w in warnings:print('NOTE:',w)
sys.exit(0 if not errors else 1)
