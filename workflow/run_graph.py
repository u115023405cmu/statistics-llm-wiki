#!/usr/bin/env python3
"""統計學 Wiki → HTML 工作流程原型。僅使用本專案的 Wiki Markdown 內容。

命令：python workflow/run_graph.py
輸出：workflow/artifacts、slides/workflow-preview.html、reports/workflow/*。

這不是自主修改統計事實的 AI 代理；程式把 Graph 的關卡、輸入輸出、停止條件與
可機械驗證的局部 Loop 實作出來。統計語義與原 PDF 忠實度需另行獨立審查。
"""
import csv
import datetime
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import shutil
import sys
import traceback
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'workflow/artifacts'; CARDS=ART/'cards'; REP=ROOT/'reports/workflow'; SLIDES=ROOT/'slides'
SOURCES=ROOT/'wiki/sources/source_registry.csv'
SPEC=ROOT/'workflow/lesson_spec.json'
CIT_RE=re.compile(r'\[(S\d{2}), PDF p\.(\d+)\]')
MAX_REVISIONS=3

class GraphFailure(Exception):
    def __init__(self,node,kind,message,return_to=None):
        super().__init__(message);self.node=node;self.kind=kind;self.return_to=return_to

def now():
    return datetime.datetime.now(ZoneInfo('Asia/Taipei')).isoformat(timespec='seconds')
def relative(p):
    try: return str(p.relative_to(ROOT))
    except ValueError: return str(p)
def put_json(p,data):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def registry():
    with SOURCES.open(encoding='utf-8-sig',newline='') as f:
        return {r['id']:r for r in csv.DictReader(f)}

def log(events,node,status,detail,attempt=1,**extra):
    data={'time':now(),'node':node,'attempt':attempt,'status':status,'detail':detail}
    data.update(extra);events.append(data)
    print(f"[{node}][{status}][{attempt}] {detail}")

# A: 正式 Wiki 狀態檢查。檢查不通過就停下，不繞過來源問題。
def gate_wiki(events):
    p=ROOT/'scripts/audit_wiki.py'
    result=subprocess.run([sys.executable,str(p)],capture_output=True,text=True,cwd=ROOT)
    raw=registry()
    if result.returncode!=0 or sum(x['ingested']=='是' for x in raw.values())<5:
        log(events,'A: Wiki 核對','FAIL',result.stdout.strip()+' '+result.stderr.strip())
        raise GraphFailure('A','wiki_audit', 'Wiki 自動稽核失敗：請先修來源或 Wiki，不能繼續',None)
    print(result.stdout.strip())
    log(events,'A: Wiki 核對','PASS',f'{len(raw)} 份來源、{len(list((ROOT/"wiki/entries").glob("*.md")))} 篇條目；既有腳本通過',files=['reports/audit_wiki.json','wiki/sources/source_registry.csv'])
    return raw

def extract_block(doc,anchor):
    blocks=[b.strip() for b in re.split(r'\n\s*\n',doc) if b.strip()]
    for i,b in enumerate(blocks):
        if anchor in b:
            refs=CIT_RE.findall(b)
            # 公式引文可能置於其後的解釋段落：只允許在下一個同節段落內尋找，並保留查核旗標。
            adjacent=False
            if not refs:
                for candidate in blocks[i+1:i+4]:
                    if candidate.startswith('## ') or candidate.startswith('### '):break
                    refs=CIT_RE.findall(candidate)
                    if refs:
                        adjacent=True;break
            return b,refs,adjacent
    raise ValueError(f'Wiki 找不到指定的逐字錨點：{anchor}')

def evidence_text(block,anchor):
    # 純粹裁切已存在的 Wiki 句子，不生成／擴寫新的統計主張。
    lines=[x.strip(' -\n\t') for x in block.splitlines() if x.strip() and not x.startswith('|')]
    target=next((x for x in lines if anchor in x),lines[0] if lines else '')
    target=CIT_RE.sub('',target)
    target=re.sub(r'\*\*|(?<!\\)\*','',target)
    target=target.replace('\\(','').replace('\\)','').replace('\\[','').replace('\\]','')
    target=re.sub(r'\s+',' ',target).strip()
    # 避免任意半句截斷: 單行過長時只取最早完整的 1-2 句。
    if len(target)>200:
        segs=re.split(r'(?<=。)',target)
        chosen=''
        for s in segs:
            if len(chosen+s)>200 and chosen:break
            chosen+=s
        if chosen and len(chosen)<=240:target=chosen
    # 公式後面若仍有未完結的提示子句（如『常見公式是』），不把半句放進簡報。
    if target.endswith(('是','則','時：','如下：')) and '。' in target:
        target=target[:target.rfind('。')+1]
    return target

def produce_evidence(spec,raw,events):
    slides=[];used=set();adjacent=[]
    for slide in spec['slides']:
        material=[]
        for claim in slide['claims']:
            source_file=ROOT/'wiki/entries'/claim['entry']
            if not source_file.is_file():raise GraphFailure('B','missing_entry',relative(source_file),'B')
            content=source_file.read_text(encoding='utf-8')
            try: block,refs,adj=extract_block(content,claim['anchor'])
            except ValueError as e:raise GraphFailure('B','anchor_not_found',str(e),'B')
            if not refs:raise GraphFailure('B','missing_citation',f'{claim["entry"]}: {claim["anchor"]}','B')
            valid=[]
            for sid,page in refs:
                if sid not in raw or not 1<=int(page)<=int(raw[sid]['pdf_pages']):
                    raise GraphFailure('C','invalid_citation',f'{sid} p.{page}: Wiki 引文無效','B')
                valid.append({'source_id':sid,'pdf_page':int(page),'reference':f'[{sid}, PDF p.{page}]'})
                used.add(sid)
            # 依前兩個來源標記保留相鄰段落引用的資訊，供真人覆核來源對應。
            card={'slide_id':slide['id'],'entry':f'wiki/entries/{claim["entry"]}',
                  'anchor':claim['anchor'],'exact_wiki_passage':block,
                  'teaching_excerpt':evidence_text(block,claim['anchor']),
                  'citations':valid[:4],'citation_from_adjacent_paragraph':adj}
            if adj:adjacent.append(f'{slide["id"]}: {claim["entry"]} / {claim["anchor"]}')
            material.append(card)
        output={**{k:v for k,v in slide.items() if k!='claims'},'evidence':material}
        put_json(CARDS/f'{slide["id"]}.json',output)
        slides.append(output)
    if len(used)<5:raise GraphFailure('C','insufficient_sources',f'僅 {len(used)} 個來源ID','B')
    put_json(ART/'evidence_cards.json',slides)
    put_json(ART/'coverage.json',{'source_ids':sorted(used),'source_count':len(used),
       'slides':len(slides),'adjacent_paragraph_citations_to_review':adjacent,
       'meaning':'來源 ID 與 Wiki 字串存在，不等於語意審查已通過'})
    log(events,'B: Wiki 證據卡','PASS',f'{len(slides)} 張卡、{sum(len(s["evidence"]) for s in slides)} 項來源段落',files=['workflow/artifacts/cards/','workflow/artifacts/evidence_cards.json'])
    log(events,'C: 來源覆蓋檢查','PASS',f'覆蓋 {len(used)} 份已 ingest 講義（{", ".join(sorted(used))}）；{len(adjacent)} 條引用須確認相鄰段落',files=['workflow/artifacts/coverage.json'])
    return slides,adjacent

def outline(slides,events):
    content=['# 教學 HTML 簡報大綱（由 Wiki 證據卡生成）','',
        '> 這是 Step 4 中間成果；來源是 `wiki/entries/`，不是重新讀取 PDF 或外部搜尋。','',
        f'共 {len(slides)} 頁；對象：未接觸統計學的大學生。','']
    for slide in slides:
        content+= [f'## {slide["id"]}. {slide["title"]}',f'- 教學定位：{slide["subtitle"]}']
        for e in slide['evidence']:
            refs=' '.join(x['reference'] for x in e['citations'])
            content.append(f'- Wiki 證據：{e["teaching_excerpt"]}（{refs}；`{e["entry"]}`）')
        content.append('')
    (ART/'outline.md').write_text('\n'.join(content)+'\n',encoding='utf-8')
    log(events,'D: 教學大綱','PASS',f'以來源卡生成 {len(slides)} 頁大綱',files=['workflow/artifacts/outline.md'])

def generate_html(slides,scale,events,attempt=1):
    pieces=[]
    for j,s in enumerate(slides):
        body=[]
        for k,e in enumerate(s['evidence']):
            text=html.escape(e['teaching_excerpt']);refs=' · '.join(html.escape(c['reference']) for c in e['citations'])
            link='../'+e['entry']
            body.append(f'<div class="point"><div class="point-label">重點 {k+1}</div><p>{text}</p><div class="cite">{refs} <a href="{html.escape(link,quote=True)}">對應 Wiki</a></div></div>')
        if s['id']=='01':
            body=['<div class="hero-label">WIKI → EVIDENCE → SLIDES</div><p class="hero-desc">用資料、抽樣、描述、機率與推論，學會更有根據地做判斷。</p><p class="preview-notice">STEP 4 工作流程原型｜正式教學設計與獨立內容審查仍待 STEP 5</p>']
        elif s['id']=='12':
            body.append('<p class="lesson-note">回想一下：研究問題決定如何蒐集資料；資料特性決定如何描述；推論結論仍受抽樣與模型假設限制。</p>')
        pieces.append(f'<section class="slide{" active" if j==0 else ""}" id="s-{s["id"]}" data-index="{j}" role="group" aria-label="第 {j+1} 頁">'
                      f'<div class="number">{j+1:02d} / {len(slides):02d}</div><div class="eyebrow">統計學入門 · Wiki 引用版</div>'
                      f'<h1>{html.escape(s["title"])}</h1><div class="subtitle">{html.escape(s["subtitle"])}</div>'
                      f'<div class="points">{"".join(body)}</div></section>')
    stylesheet='''
      :root{--ink:#243e33;--muted:#667a70;--green:#3b6b57;--cream:#faf8f1;--paper:#ffffff;--scale:SCALE}
      *{box-sizing:border-box}html,body{margin:0;height:100%;font-family:"Noto Sans TC","Microsoft JhengHei",Arial,sans-serif;background:#e8ece6;color:var(--ink)}
      body{display:flex;align-items:center;justify-content:center;padding:14px}
      .deck{position:relative;width:min(1200px,100%);height:min(760px,calc(100dvh - 28px));min-height:520px;background:var(--cream);border-radius:22px;box-shadow:0 16px 50px #34493b22;overflow:hidden}
      .slide{display:none;height:calc(100% - 76px);padding:36px 56px 18px;overflow:hidden}.slide.active{display:block}
      .number{float:right;letter-spacing:1.2px;color:var(--muted);font-weight:700;font-size:13px}
      .eyebrow{font-size:12px;font-weight:700;letter-spacing:.14em;color:var(--green);text-transform:uppercase;margin:5px 0 14px}
      h1{font-size:calc(42px * var(--scale));line-height:1.2;letter-spacing:-.03em;margin:0 0 12px;max-width:96%}
      .subtitle{font-size:calc(19px * var(--scale));color:var(--muted);margin-bottom:29px}
      .points{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px;align-items:stretch}
      .point{background:#fff;padding:23px 23px 17px;border:1px solid #e4e9e0;border-radius:17px;box-shadow:0 2px 8px #253b2609;min-width:0}
      .point-label{font-size:12px;letter-spacing:.12em;font-weight:800;color:var(--green);margin-bottom:10px}
      .point p{font-size:calc(17px * var(--scale));line-height:1.7;margin:0 0 17px;overflow-wrap:anywhere}
      .cite{font-size:12px;color:var(--muted);line-height:1.7}.cite a{color:var(--green);text-decoration:underline;text-underline-offset:2px}
      .lesson-note{grid-column:1/-1;font-size:calc(15px * var(--scale));color:var(--muted);margin:2px 0}
      .hero-label{grid-column:1/-1;color:var(--green);font-weight:750;letter-spacing:.2em;margin:50px 0 0}
      .hero-desc{grid-column:1/-1;font-size:calc(22px * var(--scale));max-width:660px;line-height:1.8;margin:0}
      .preview-notice{grid-column:1/-1;color:var(--muted);font-size:13px}
      .bottom{display:flex;align-items:center;justify-content:space-between;position:absolute;bottom:0;left:0;right:0;padding:16px 24px;border-top:1px solid #dfebdf;background:#faf8f1}
      .bottom button{border:1px solid #d1ddd0;background:#fff;color:var(--ink);border-radius:10px;font-size:14px;padding:9px 18px;cursor:pointer}
      .bottom button:focus-visible{outline:3px solid #4c8771}.bottom button:hover{background:#eaf3ed}.bottom button:disabled{opacity:.38;cursor:default}
      .progress{flex:1;height:5px;border-radius:6px;background:#dce6de;margin:0 30px;overflow:hidden}.progress .fill{height:100%;width:8.3333%;background:var(--green);transition:width .16s}
      @media(max-width:650px){body{padding:0}.deck{width:100%;height:100dvh;min-height:0;border-radius:0}.slide{padding:28px 21px 12px;height:calc(100% - 66px);overflow-y:auto}.eyebrow{margin:0 0 11px}h1{font-size:calc(29px * var(--scale));margin:0 0 9px}.subtitle{font-size:calc(15px * var(--scale));margin-bottom:17px}.points{grid-template-columns:1fr;gap:12px}.point{padding:13px 16px}.point p{font-size:calc(14px * var(--scale));line-height:1.5;margin-bottom:8px}.cite{font-size:11px}.bottom{padding:12px 16px}.bottom button{font-size:13px;padding:8px 12px}.progress{margin:0 14px}.hero-label{margin-top:20px}.hero-desc{font-size:19px}}
      @media print{body{padding:0;display:block;background:white}.deck{height:auto;max-width:100%;box-shadow:none}.slide,.slide.active{display:block!important;height:190mm;page-break-after:always;border-bottom:1px solid #ddd}.bottom{display:none}}
      '''.replace('SCALE',str(scale))
    js='''
      const sections=[...document.querySelectorAll('.slide')];let current=0;
      function showPage(n){current=Math.max(0,Math.min(sections.length-1,n));sections.forEach((e,i)=>e.classList.toggle('active',i===current));
        document.querySelector('#prev').disabled=current===0;document.querySelector('#next').disabled=current===sections.length-1;
        document.querySelector('#position').textContent=`${current+1} / ${sections.length}`;
        document.querySelector('.fill').style.width=`${(current+1)*100/sections.length}%`;
        location.hash=`s-${sections[current].id.split('-')[1]}`;}
      document.querySelector('#prev').addEventListener('click',()=>showPage(current-1));
      document.querySelector('#next').addEventListener('click',()=>showPage(current+1));
      document.addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();showPage(current+1)}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();showPage(current-1)}});
      let h=document.location.hash.match(/^#s-(\\d+)$/);if(h){const idx=sections.findIndex(s=>s.id===`s-${h[1]}`);showPage(idx>=0?idx:0)}else showPage(0);
      '''
    page='''<!doctype html><html lang="zh-Hant"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>統計學入門：Graph 工作流程原型</title><style>'''+stylesheet+'''</style></head><body><main class="deck" aria-label="統計學教學簡報原型">'''+''.join(pieces)+'''<nav class="bottom" aria-label="簡報導覽"><button id="prev" type="button">上一頁</button><div class="progress"><div class="fill"></div></div><span id="position">1 / 12</span><button id="next" type="button">下一頁</button></nav></main><script>'''+js+'''</script></body></html>'''
    out=SLIDES/'workflow-preview.html';out.write_text(page,encoding='utf-8')
    log(events,'E: HTML 原型生成','PASS',f'{len(slides)} 頁 HTML 原型；文字縮放 {scale:.2f}',attempt=attempt,files=['slides/workflow-preview.html'])
    return out

class SlideParser(HTMLParser):
    def __init__(self):super().__init__();self.slide_ids=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='section' and 'slide' in a.get('class','').split(): self.slide_ids.append(a.get('id'))
        if tag=='a' and a.get('href'): self.links.append(a['href'])

def validate_static(cards,events):
    page=(SLIDES/'workflow-preview.html').read_text(encoding='utf-8')
    p=SlideParser();p.feed(page)
    checks=[];errors=[]
    def check(name,condition,details):
        checks.append({'name':name,'passed':bool(condition),'details':details})
        if not condition:errors.append(f'{name}：{details}')
    check('HTML 頁數 10–12',10<=len(p.slide_ids)<=12,f'{len(p.slide_ids)} 頁')
    check('頁面 ID 不重複',len(set(p.slide_ids))==len(p.slide_ids),str(p.slide_ids))
    check('所有 Wiki 連結有效',all((SLIDES/x).resolve().is_file() and (SLIDES/x).resolve().is_relative_to(ROOT) for x in p.links),f'{len(p.links)} 個引用連結')
    all_ids={};anchored=set();adjs=[]
    for s in cards:
        for e in s['evidence']:
            rawtext=(ROOT/e['entry']).read_text(encoding='utf-8')
            check('來源錨點 '+s['id']+' '+e['anchor'][:20],e['anchor'] in rawtext,'Wiki 存在指定的原文定位點')
            for c in e['citations']:
                anchored.add(c['source_id']);all_ids[c['source_id']]=all_ids.get(c['source_id'],0)+1
                if c['reference'] not in page:errors.append('HTML 缺少引用：'+c['reference'])
            if e['citation_from_adjacent_paragraph']:adjs.append(e['anchor'])
    check('至少五份來源',len(anchored)>=5,f'{sorted(anchored)}')
    check('導覽邏輯存在',all(f'id="{i}"' in page for i in ['prev','next','position']),'前進、後退、頁碼')
    result={'timestamp':now(),'checks':checks,'errors':errors,'passed':len(checks)-len(errors), 'failed':len(errors),
            'source_coverage':all_ids,'adjacent_citation_flags':adjs,'scope_note':'結構與來源標記檢查，並非語義忠實度或教學正確性的獨立審查'}
    put_json(REP/'static_validation.json',result)
    if errors:
        log(events,'F: 靜態檢查','FAIL',' / '.join(errors[:3]),files=['reports/workflow/static_validation.json'])
        raise GraphFailure('F','html_structure',str(errors[:3]),'E')
    log(events,'F: 靜態檢查','PASS',f'{len(checks)} 個檢查項目通過、{len(p.links)} 個引用連結',files=['reports/workflow/static_validation.json'])
    return result

def test_browser(events,attempt=1):
    """實際開啟 Chrome 測試桌機/手機，需安裝 Playwright；缺少時明確標 pending。"""
    try:from playwright.sync_api import sync_playwright
    except ImportError:
        log(events,'G: 瀏覽器測試','PENDING','未安裝 Playwright，未宣稱通過')
        return {'status':'pending','errors':['Playwright unavailable']}
    issues=[];result={'time':now(),'viewports':[],'status':'pass'}
    with sync_playwright() as playwright:
        binary=shutil.which('chromium') or shutil.which('chromium-browser') or shutil.which('google-chrome')
        try:
            browser=playwright.chromium.launch(headless=True,**({'executable_path':binary} if binary else {}),args=['--no-sandbox'])
        except Exception as exc:
            log(events,'G: 瀏覽器測試','PENDING',f'無法啟動 Chromium: {exc}')
            return {'status':'pending','errors':['Chromium unavailable: '+str(exc)]}
        for w,h in [(1280,800),(390,844)]:
            page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1)
            page.set_content((SLIDES/'workflow-preview.html').read_text(encoding='utf-8'),wait_until='load')
            page.wait_for_timeout(250)
            r={'viewport':f'{w}x{h}','slides':[]}
            total=page.locator('.slide').count()
            for i in range(total):
                page.evaluate('i=>showPage(i)',i)
                m=page.locator('.slide.active').evaluate('el=>({clientWidth:el.clientWidth,scrollWidth:el.scrollWidth,clientHeight:el.clientHeight,scrollHeight:el.scrollHeight})')
                is_overflow=m['scrollWidth']>m['clientWidth']+2 or (w>650 and m['scrollHeight']>m['clientHeight']+3)
                r['slides'].append({'slide':i+1,'overflows':bool(is_overflow),'metrics':m})
                if is_overflow:issues.append(f'{w}x{h} 頁 {i+1} 超出顯示範圍')
            # Button navigation interaction, including back
            page.evaluate('showPage(0)');page.locator('#next').click()
            forward=page.locator('.slide.active').get_attribute('id')=='s-02'
            page.locator('#prev').click()
            back=page.locator('.slide.active').get_attribute('id')=='s-01'
            r['navigation']={'next':forward,'prev':back}
            if not forward or not back:issues.append(f'{w}x{h} 上下頁按鈕異常')
            if w==1280:
                page.screenshot(path=str(REP/'workflow-preview-desktop.png'))
            else:
                page.screenshot(path=str(REP/'workflow-preview-mobile.png'))
            page.close()
            result['viewports'].append(r)
        browser.close()
    result['issues']=issues;result['status']='pass' if not issues else 'fail'
    put_json(REP/'browser_validation.json',result)
    log(events,'G: 瀏覽器測試','PASS' if not issues else 'FAIL',f'Chrome 兩種尺寸、按鈕與 {len(result["viewports"])*total} 個頁面檢查；{len(issues)} 項問題',attempt=attempt,files=['reports/workflow/browser_validation.json'])
    return result

def run():
    for directory in [ART,CARDS,REP,SLIDES]:directory.mkdir(parents=True,exist_ok=True)
    start=now();events=[];status='incomplete';problems=[]
    spec=json.loads(SPEC.read_text(encoding='utf-8'))
    try:
        raw=gate_wiki(events)
        cards,adj=produce_evidence(spec,raw,events)
        outline(cards,events)
        # 局部 Loop：只允許針對「版面」調整文字縮放，不重新生成統計事實。
        scale=1.0
        for attempt in range(1,MAX_REVISIONS+1):
            generate_html(cards,scale,events,attempt)
            validate_static(cards,events)
            browser=test_browser(events,attempt)
            if browser['status']=='pass':
                status='prototype_ready_review_pending';break
            if browser['status']=='pending':
                status='prototype_ready_browser_pending';break
            if attempt==MAX_REVISIONS:
                raise GraphFailure('G','layout_limit','版面局部 Loop 修正 3 輪後未通過，停止送件',None)
            log(events,'G → E: 局部版面 Loop','RETURN',f'依照瀏覽器問題調小字級：{scale:.2f} → {scale-0.08:.2f}（不改內容）',attempt=attempt)
            scale=round(scale-.08,2)
        log(events,'H: 原型交付','PASS','產出可以讀取的 HTML 工作流程原型；語義審查、教學精修與公開部署尚未完成',files=['slides/workflow-preview.html'])
    except GraphFailure as err:
        problems.append({'node':err.node,'kind':err.kind,'detail':str(err),'return_to':err.return_to})
        status='stopped';log(events,err.node,'STOP',f'{err.kind}: {err}；應退回 {err.return_to or "人工確認"}')
    except Exception as err:
        problems.append({'node':'unexpected','detail':repr(err),'traceback':traceback.format_exc()})
        status='stopped';log(events,'unexpected','STOP',repr(err))
    report={'started':start,'finished':now(),'status':status,'maximum_local_revisions':MAX_REVISIONS,
        'executed_nodes':events,'problems':problems,
        'limitations':['Wiki 自動稽核不代表逐句語義忠實','相鄰段落引用需要人工核對','HTML 為工作流程原型，不是最終教學簡報','未進行不同模型/不同對話的獨立內容審查','公開部署不在本步驟執行']}
    put_json(REP/'graph_execution.json',report)
    markdown=['# STEP 4｜Graph＋局部 Loop 真實執行紀錄','',f'- 執行時間：{start} 至 {now()}','- 本次狀態：`'+status+'`','- 重要說明：僅記錄本機實際程式執行結果。未通過的檢查不會寫成通過。','',
              '| 節點 | 次數 | 結果 | 實際輸出／觀察 |','|---|---:|---|---|']
    for event in events:
        markdown.append('| '+event['node']+' | '+str(event['attempt'])+' | '+event['status']+' | '+event['detail'].replace('|','／').replace('\n',' ')+' |')
    markdown+=['','## 局部 Loop 與退回','',
        '- Wiki 缺漏或來源不正確：**停止**，退回 B/C 查證，不自動捏造資料。',
        '- 教學大綱證據不足：退回來源對照，補查 Wiki 後重新產生大綱。',
        '- HTML 版面溢出：只回 E 重新渲染，字體等比例縮小，每次保留測試結果，最多三輪。',
        '- HTML 檢查引用失敗：退回 B 來源卡（而非只改 HTML 標記）。',
        '- 因資料不充分或三輪仍失敗則停止，必須人工處理。','',
        '## 限制及下一步','',
        '- **本次執行不等於獨立審稿**，來源標記存在只能確定可追溯，無法確認每句與原始 PDF 完全一致。',
        '- 步驟 5 仍需根據原型進行內容精修、全頁教學順序與來源忠實度的獨立審查。',
        '- 若所有檢查首輪通過，就如實記錄「沒有觸發回圈」；不可編造三輪失敗。',
        '- `reports/workflow/route_tests.json` 是**隔離的故障注入測試**，不得當成正式執行時真實的錯誤。','']
    (REP/'graph-run-log.md').write_text('\n'.join(markdown)+'\n',encoding='utf-8')
    print('Graph status:',status)
    return 0 if status.startswith('prototype_ready') else 1
if __name__=='__main__':sys.exit(run())
