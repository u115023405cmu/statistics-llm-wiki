#!/usr/bin/env python3
"""真實 Chromium 測試 12 頁桌機／手機版，測試時使用 set_content 避開沙盒 file:// 限制。"""
from pathlib import Path
import json, datetime, sys, shutil
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'slides/statistics-teaching.html'
OUT=ROOT/'reports/step5/browser_checks.json'
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print('SKIP: Playwright 未安裝，不能宣稱瀏覽器測試已通過')
    OUT.parent.mkdir(exist_ok=True,parents=True)
    OUT.write_text(json.dumps({'status':'not_run','reason':'Playwright 未安裝'},ensure_ascii=False,indent=2)+'\n')
    sys.exit(2)

cases=[]
def record(name,pass_,detail=''):
    cases.append({'check':name,'passed':bool(pass_),'detail':detail})
with sync_playwright() as p:
    opts={'headless':True,'args':['--no-sandbox','--disable-gpu']}
    if shutil.which('chromium'): opts['executable_path']=shutil.which('chromium')
    browser=p.chromium.launch(**opts)
    for label,w,h in [('desktop',1280,800),('mobile',390,844)]:
        page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1)
        errors=[]
        page.on('pageerror',lambda err:errors.append(str(err)))
        page.set_content(P.read_text(encoding='utf-8'),wait_until='load')
        page.wait_for_timeout(270)
        for i in range(12):
            if i:page.click('#nextBtn')
            page.wait_for_timeout(265)
            met=page.evaluate('''()=>{let e=document.querySelector('.slide.active');let b=document.querySelector('.presentation');let f=e.querySelector('.source-footer');return {id:e.id, horizontal:e.scrollWidth-e.clientWidth,vertical:e.scrollHeight-e.clientHeight,bodyOverflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,deckHeight:b.clientHeight,footerWidth:f.scrollWidth-f.clientWidth,visible:!!e.querySelector('h1')&&getComputedStyle(e).display!=='none'}}''')
            record(f'{label} 第{i+1}頁：可見、無水平溢出',met['visible'] and met['horizontal']<=1 and met['bodyOverflow']<=1,f"h-scroll {met['horizontal']}px; v-scroll {met['vertical']}px")
            if label=='desktop':record(f'{label} 第{i+1}頁：不需縱向捲動',met['vertical']<=1, f"v-scroll {met['vertical']}px")
            if (label=='desktop' and i in (0,6,9)) or (label=='mobile' and i in (0,9,10)):
                page.screenshot(path=str(ROOT/f'reports/step5/{label}-slide-{i+1:02}.png'))
            if i==2:
                page.locator('.slide.active .source-toggle').click()
                record(f'{label}：來源面板能開啟',page.locator('#overlay').get_attribute('aria-hidden')=='false')
                record(f'{label}：來源面板有 Wiki 檔案連結',page.locator('.reference-panel.visible a').count()>0)
                page.locator('#drawerClose').click()
            if i==3:
                page.locator('#menuBtn').click()
                record(f'{label}：可開啟 12 頁目錄',page.locator('#tocPanel .toc-entry').count()==12)
                page.locator('#drawerClose').click()
        page.keyboard.press('ArrowLeft')
        record(f'{label}：鍵盤上一頁可用',page.locator('.slide.active').get_attribute('id')=='slide-11')
        record(f'{label}：無 JavaScript 例外',not errors,'; '.join(errors[:2]))
        page.close()
    browser.close()
run={'time':datetime.datetime.now(ZoneInfo('Asia/Taipei')).isoformat(timespec='seconds'),'browser':'Chromium via Playwright; page.set_content() used because sandbox blocks file:// navigation','viewport_tests':['1280×800','390×844'],'checks_passed':sum(c['passed'] for c in cases),'checks_total':len(cases),'checks_failed':sum(not c['passed'] for c in cases),'checks':cases,'limitation':'這是自動瀏覽器檢查，不等於使用者已在 GitHub Pages 正式部署測試。'}
OUT.parent.mkdir(exist_ok=True,parents=True)
OUT.write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'STEP5 BROWSER: {run["checks_passed"]}/{run["checks_total"]} PASS, {run["checks_failed"]} FAIL')
for x in cases:
    if not x['passed']:print('FAIL',x)
sys.exit(0 if run['checks_failed']==0 else 1)
