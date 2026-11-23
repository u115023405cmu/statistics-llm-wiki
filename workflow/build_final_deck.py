from pathlib import Path
import shutil, csv, json, html, math, datetime, re, textwrap
from zoneinfo import ZoneInfo
# Operates within the current repository; does not modify Wiki content.
ROOT=Path(__file__).resolve().parents[1]
REG={r['id']:r for r in csv.DictReader((ROOT/'wiki/sources/source_registry.csv').open(encoding='utf-8-sig'))}
EV={s['id']:s for s in json.loads((ROOT/'workflow/artifacts/evidence_cards.json').read_text(encoding='utf-8'))}
E=lambda s:html.escape(str(s),quote=True)
SVG_NS='http://www.w3.org/2000/svg'

def source_pills(refs):
    return ' '.join(f'<span class="source-pill" data-source="{E(id)}" data-page="{p}">{id} · PDF p.{p}</span>' for id,p in refs)

def coin_chart():
    # Probabilistic sales income scenario from Wiki (S03 pp 24-26).
    bars=[('970','60%',.60,'#418b74'),('800','30%',.30,'#85c9ac'),('0','10%',.10,'#cdded5')]
    out='<div class="prob-bars">'
    for name,p,height,color in bars:
        out+=f'<div class="prob-col"><b>{p}</b><div class="prob-track"><span style="height:{int(100*height)}%;background:{color}"></span></div><small>{name} 元</small></div>'
    return out+'</div>'

def histogram():
    # Data [0,1,1,2,2,2,3,4,4,6,8,12], groups [0-2,3-5,6-8,9-11,12-14]
    freq=[6,3,2,0,1]; labels=['0–2','3–5','6–8','9–11','12–14']
    W,H=560,270; left=48; bottom=220; bw=75; gap=21
    chunks=[f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="自編每週咖啡杯數，直方圖：0–2杯6人、3–5杯3人、6–8杯2人、9–11杯0人、12–14杯1人" preserveAspectRatio="xMidYMid meet">']
    for k in range(0,7,2):
        y=bottom-k*25
        chunks+=[f'<line x1="40" y1="{y}" x2="545" y2="{y}" stroke="#e5ece7" stroke-width="1"/>',f'<text x="32" y="{y+5}" text-anchor="end" font-size="14" fill="#60756f">{k}</text>']
    for i,(f,l) in enumerate(zip(freq,labels)):
        x=left+i*(bw+gap); h=f*25
        chunks += [f'<rect x="{x}" y="{bottom-h}" width="{bw}" height="{max(h,1)}" rx="8" fill="{("#278168" if i==0 else "#80bfaa")}"/>',f'<text x="{x+bw/2}" y="{bottom-h-9}" text-anchor="middle" font-weight="750" font-size="15" fill="#294e43">{f}</text>',f'<text x="{x+bw/2}" y="250" text-anchor="middle" font-size="13" fill="#54665f">{l}</text>']
    chunks += ['<text x="285" y="268" text-anchor="middle" fill="#54665f" font-size="12">每週杯數（分組）</text>','</svg>']
    return ''.join(chunks)

def mean_chart():
    vals=[2,4,4,6,8,12]
    W,H=560,260; base=210
    c=[f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="六位同學自編讀書時數 2 4 4 6 8 12，平均6小時、中位數5小時">']
    for i,v in enumerate(vals):
        x=45+i*84; h=v*12
        c.append(f'<rect x="{x}" y="{base-h}" width="58" height="{h}" rx="10" fill="{("#edac6b" if i==5 else "#82c5ab")}"/>')
        c.append(f'<text x="{x+29}" y="{base-h-10}" text-anchor="middle" fill="#294e43" font-size="18" font-weight="700">{v}</text>')
        c.append(f'<text x="{x+29}" y="238" text-anchor="middle" fill="#60756f" font-size="12">學生 {i+1}</text>')
    c+=['<line x1="20" y1="210" x2="548" y2="210" stroke="#99aba2"/>','</svg>']
    return ''.join(c)

def normal_chart():
    # classic standard normal bell curve and 68% within ±1; purely illustrative using normal density
    W,H=560,270; x0=34; x1=526; baseline=224
    xscale=lambda z:x0+(z+3.5)/7*(x1-x0)
    pdf=lambda z:math.exp(-z*z/2)/math.sqrt(2*math.pi)
    yscale=lambda p:baseline-p*420
    xs=[-3.5+i*7/140 for i in range(141)]
    curve=' '.join(f'{"M" if i==0 else "L"}{xscale(z):.1f},{yscale(pdf(z)):.1f}' for i,z in enumerate(xs))
    fillxs=[-1+i*2/80 for i in range(81)]
    fill=f'M{xscale(-1):.1f},{baseline:.1f} '+' '.join(f'L{xscale(z):.1f},{yscale(pdf(z)):.1f}' for z in fillxs)+f' L{xscale(1):.1f},{baseline:.1f} Z'
    v=['<svg viewBox="0 0 560 270" role="img" aria-label="標準常態鐘形曲線，平均數左右各一個標準差內的面積約68%">',f'<path d="{fill}" fill="#cde9d7"/>',f'<path d="{curve}" fill="none" stroke="#2f826a" stroke-width="5" stroke-linecap="round"/>',f'<line x1="{x0}" y1="{baseline}" x2="{x1}" y2="{baseline}" stroke="#9aada2" stroke-width="1.5"/>']
    for z in [-3,-2,-1,0,1,2,3]:
        x=xscale(z)
        v.append(f'<line x1="{x:.1f}" y1="{baseline}" x2="{x:.1f}" y2="{baseline+7}" stroke="#9aada2"/><text x="{x:.1f}" y="{baseline+26}" text-anchor="middle" font-size="14" fill="#60756f">{z:+d}</text>')
    v+=['<text x="280" y="98" font-size="28" font-weight="800" text-anchor="middle" fill="#27624f">≈68%</text>','<text x="280" y="268" font-size="13" text-anchor="middle" fill="#60756f">標準化分數 Z</text>','</svg>']
    return ''.join(v)

def interval_chart():
    # p in percent 45 to 75 horizontally; CI 55.2 - 64.8
    W,H=560,200;x0=60;w=450
    pos=lambda v:x0+(v-45)/30*w
    c=['<svg viewBox="0 0 560 200" role="img" aria-label="自編示範比例估計60%，95%信賴區間55.2%到64.8%">',f'<line x1="{x0}" y1="110" x2="{x0+w}" y2="110" stroke="#cbdad2" stroke-width="8" stroke-linecap="round"/>']
    for t in [45,50,55,60,65,70,75]:
        p=pos(t);c.append(f'<text x="{p:.1f}" y="155" text-anchor="middle" fill="#6b7d74" font-size="14">{t}%</text>')
    c += [f'<line x1="{pos(55.2):.1f}" y1="110" x2="{pos(64.8):.1f}" y2="110" stroke="#2c8069" stroke-width="18" stroke-linecap="round"/>',f'<circle cx="{pos(60):.1f}" cy="110" r="13" fill="#fff" stroke="#2c8069" stroke-width="5"/>',f'<text x="{pos(55.2):.1f}" y="79" text-anchor="middle" fill="#27624f" font-weight="750" font-size="17">55.2%</text>',f'<text x="{pos(64.8):.1f}" y="79" text-anchor="middle" fill="#27624f" font-weight="750" font-size="17">64.8%</text>',f'<text x="{pos(60):.1f}" y="40" text-anchor="middle" fill="#173f34" font-size="25" font-weight="850">60%</text>','</svg>']
    return ''.join(c)

def dot_population():
    s=['<svg viewBox="0 0 560 260" role="img" aria-label="母體由很多點構成；右方樣本選中一小部分點，強調抽樣代表性">']
    for row in range(5):
        for col in range(9):
            x=38+col*27;y=33+row*38
            active=((col+row*9)%6==0)
            s.append(f'<circle cx="{x}" cy="{y}" r="8" fill="{("#3f9276" if active else "#d2e2d9")}"/>')
    s += ['<path d="M290 100 L337 100" stroke="#91a9a0" stroke-width="3" stroke-linecap="round"/><path d="M329 93 L337 100 L329 107" fill="none" stroke="#91a9a0" stroke-width="3"/>']
    for idx,(x,y) in enumerate([(375,34),(413,34),(451,34),(489,34),(375,78),(413,78),(451,78),(489,78),(375,122),(413,122),(451,122),(489,122)]):
        s.append(f'<circle cx="{x}" cy="{y}" r="12" fill="{("#3f9276" if idx%3==0 else "#89c8ad")}"/>')
    s += ['<text x="140" y="244" fill="#60756f" font-size="18" text-anchor="middle">母體 Population</text>','<text x="437" y="190" fill="#60756f" font-size="18" text-anchor="middle">樣本 Sample</text>','</svg>']
    return ''.join(s)

def data_matrix():
    heads=['學生','系所','每週咖啡杯數','上週買過咖啡？']
    rows=[['A','文學','2','是'],['B','理學','0','否'],['C','工學','4','是'],['D','醫學','1','是']]
    return '<div class="data-table"><div class="tbl-head">'+''.join(f'<span>{x}</span>' for x in heads)+'</div>'+''.join('<div class="tbl-row">'+''.join(f'<span>{E(x)}</span>' for x in r)+'</div>' for r in rows)+'</div>'

def source_refs(slide_id, extras=[]):
    claims=EV[str(slide_id).zfill(2)]['evidence'];refs=[]
    for e in claims:
        for c in e['citations']:
            t=(c['source_id'],c['pdf_page'])
            if t not in refs:refs.append(t)
    for r in extras:
        if r not in refs:refs.append(r)
    return refs

# Primary and support texts MUST be based on Wiki passages; any new figures are explicitly labeled pedagogical examples.
SLIDES=[
 dict(id='01', section='INTRO',title='從資料到結論',sub='統計學如何幫助我們做判斷？',kind='cover',eyebrow='STATISTICS 101 · INTERACTIVE LESSON',
      story='你看到的數字，真的能代表整個群體嗎？',take='觀察世界，先從「資料怎麼來」問起。',extra=[]),
 dict(id='02',section='01 · WHY STATS',title='為什麼我們需要統計？',sub='一份樣本，試著回答一個關於全校的問題',kind='question',
      story='研究問題：全校學生有多少比例上週買過咖啡？',take='樣本提供線索，不等於知道母體的真實答案。',extra=[('S05',10),('S05',21)]),
 dict(id='03',section='02 · DATA',title='每一列是誰？每一欄是什麼？',sub='先分清楚觀察值與變數，才開始分析',kind='data',
      story='四位學生的示意資料',take='列＝觀察值；欄＝變數。用數字表示的學號也未必是數值型資料。',extra=[('S01',6)]),
 dict(id='04',section='03 · SAMPLING',title='抽樣可能讓我們看錯',sub='選到誰，比問多少人更重要',kind='sampling',
      story='只在咖啡店門口發問，可能漏掉沒買咖啡的人。',take='隨機抽樣不能消除所有偏差；未回覆與涵蓋不足都要考慮。',extra=[('S01',14)]),
 dict(id='05',section='04 · VISUALISE',title='數據先畫出來',sub='用合適的圖表，看出資料分布的樣子',kind='hist',
      story='假設 12 位學生的一週咖啡杯數如下。',take='直方圖呈現數值區間的頻數；類別資料則常用長條圖。',extra=[('S02',20)]),
 dict(id='06',section='05 · SUMMARISE',title='平均數，可能不是典型值',sub='認識平均數與中位數的差異',kind='mean',
      story='六位同學的每週讀書時數：2、4、4、6、8、12。',take='極端值會拉動平均數；中位數相對穩健。',extra=[('S02',7)]),
 dict(id='07',section='06 · PROBABILITY',title='機率，關鍵在分母',sub='條件換了，問題就不是同一題',kind='conditional',
      story='課堂照片分類案例：同樣是 197 張，兩種比例卻不同。',take='P(A | B) 不等於 P(B | A)，先確認「已知什麼」。',extra=[('S03',18),('S03',20)]),
 dict(id='08',section='07 · RANDOM VARIABLE',title='期望值不是保證拿到的金額',sub='不確定的結果，可以用機率加權',kind='expected',
      story='講義購物例題：可能收入 970、800 或 0 元。',take='期望值是長期的機率加權中心，不一定是任何一次的實際結果。',extra=[('S03',26)]),
 dict(id='09',section='08 · DISTRIBUTION',title='用常態分配找相對位置',sub='Z 分數把不同尺度的數字放在同一把尺上',kind='normal',
      story='以距離平均數幾個標準差，描述個別分數。',take='68–95–99.7 法則只適用於近似常態分配的資料。',extra=[('S04',13),('S04',14)]),
 dict(id='10',section='09 · INTERVAL',title='從樣本推估整個群體',sub='用信賴區間呈現估計的不確定性',kind='ci',
      story='自編案例：隨機抽 400 人，其中 240 人上週買過咖啡。',take='95% 指的是建構區間的方法在長期重複抽樣下的涵蓋率。',extra=[('S05',10),('S05',21)]),
 dict(id='11',section='10 · HYPOTHESIS TEST',title='一個結果，到底夠不夠不尋常？',sub='從零假設理解 p 值',kind='pvalue',
      story='講義案例：n＝1,000，觀察到 37% 支持，檢驗是否與 50% 不同。',take='p 值不是「零假設為真的機率」，也不是效果大小。',extra=[('S06',11),('S06',17),('S06',19)]),
 dict(id='12',section='WRAP UP',title='把統計學連成一條線',sub='研究問題 → 抽樣 → 描述 → 機率 → 推論',kind='summary',
      story='統計不只是算出一個數字，而是追問這個數字能說明什麼。',take='判斷前先問：資料從哪裡來？用了什麼假設？不確定性在哪裡？',extra=[('S02',5),('S03',20),('S04',22),('S05',22)]),
]
assert len(SLIDES)==12

def topic_content(s):
    kind=s['kind']
    if kind=='cover':
        return '''<div class="cover-layout"><div class="cover-left"><div class="large-step">從<span>一筆資料</span><br>走向有根據的決定。</div><p class="cover-p">從校園調查開始，理解抽樣、資料視覺化、條件機率、常態分配與統計推論。</p><div class="cover-tags"><span>12 個教學畫面</span><span>6 份課程來源</span><span>來源可追溯</span></div></div><div class="cover-right"><div class="cover-motif"><div class="motif-pill">資料 DATA</div><div class="motif-stem"></div><div class="motif-plot"><span style="height:46%"></span><span style="height:73%"></span><span style="height:59%"></span><span style="height:88%"></span><span style="height:62%"></span><span style="height:98%"></span></div><div class="motif-stem"></div><div class="motif-pill light">推論 INFERENCE</div></div></div></div>'''
    if kind=='question':
        return '''<div class="work-grid"><div class="narrative"><span class="overline">從一個校園問題開始</span><div class="big-query">「上週買過咖啡」的人，占全校多少？</div><p>不可能逐一訪問每位學生，統計學讓我們用<span class="em">樣本統計量</span>估計未知的<span class="em">母體參數</span>。</p><div class="mini-note">換一批隨機抽中的人，結果可能不同：這是<strong>抽樣誤差</strong>。</div></div><div class="graphic-side"><div class="split-figure"><div class="symbol-box"><div class="stat-symbol">p</div><b>母體參數</b><span>未知的真實比例</span></div><div class="flow-forward">➜</div><div class="symbol-box pale"><div class="stat-symbol">p̂</div><b>樣本統計量</b><span>從蒐集到的資料計算</span></div></div><div class="micro-label">例子僅用於說明研究問題，並非真實校園調查</div></div></div>'''
    if kind=='data':
        return f'''<div class="work-grid"><div class="narrative"><span class="overline">第一步，讓資料有結構</span><div class="big-query">一個對象 = 一筆觀察值</div><p>每個學生各占一列；「系所」「杯數」「是否購買」是不同變數。</p><div class="mini-note">資料類型：<strong>系所、是否購買</strong>是類別；<strong>杯數</strong>是數值。</div></div><div class="graphic-side"><div class="panel"><div class="panel-title">示意資料矩陣 <small>（自編四筆，非真實調查）</small></div>{data_matrix()}</div></div></div>'''
    if kind=='sampling':
        return f'''<div class="work-grid"><div class="narrative"><span class="overline">抽樣不是人數競賽</span><div class="big-query">「在哪裡問」會影響「問到誰」</div><p>如果只在咖啡店門口調查，就可能漏掉平常不進咖啡店的學生。</p><div class="mini-note"><b>兩種風險</b><br>涵蓋偏差：有些人根本不在抽樣名單中。<br>未回覆偏差：被抽到但不回覆的人可能有不同特徵。</div></div><div class="graphic-side"><div class="panel"><div class="panel-title">母體與樣本</div>{dot_population()}<div class="micro-label">圖中點數僅用於說明概念，不代表實際樣本比例</div></div></div></div>'''
    if kind=='hist':
        return f'''<div class="work-grid"><div class="narrative"><span class="overline">第二步，先看分布</span><div class="big-query">資料集中在哪裡？有沒有長尾？</div><p>直方圖把數值分成區間，觀察每個區間有幾個人。</p><div class="mini-note">這組自編杯數是：0、1、1、2、2、2、3、4、4、6、8、12。<br><strong>12 杯</strong>使分布出現右側長尾。</div></div><div class="graphic-side"><div class="panel"><div class="panel-title">每週咖啡杯數 · 分組頻數 <small>（自編示範）</small></div>{histogram()}</div></div></div>'''
    if kind=='mean':
        return f'''<div class="work-grid"><div class="narrative"><span class="overline">同一筆資料，兩種中心</span><div class="two-stats"><div><span>平均數 mean</span><strong>6 <small>小時</small></strong></div><div><span>中位數 median</span><strong>5 <small>小時</small></strong></div></div><p>若最後一人的讀書時間從 12 變成 30 小時，平均會變成 <b>9</b>，但中位數仍是 <b>5</b>。</p><div class="mini-note">平均：把六人的值加總後除以 6。中位數：排序後取中間兩人的平均。</div></div><div class="graphic-side"><div class="panel"><div class="panel-title">每週讀書時數 <small>（Wiki 中的自編例題）</small></div>{mean_chart()}</div></div></div>'''
    if kind=='conditional':
        return '''<div class="work-grid"><div class="narrative"><span class="overline">注意「給定」哪個條件</span><div class="big-query">同一個 197，分母不同。</div><p>講義照片分類表中，219 張被預測為 fashion，其中 197 張確實是 fashion；真正屬於 fashion 的照片共有 309 張。</p><div class="mini-note">條件機率的分母，是<strong>條件事件</strong>所包含的總數。</div></div><div class="graphic-side"><div class="panel contrast-panel"><div class="comparison"><div><div class="ratio-label">在「預測 fashion」中有多少真的？</div><div class="ratio">197 / 219</div><div class="ratio-result">≈ 90.0%</div><div class="meter"><i style="width:90%"></i></div></div><div><div class="ratio-label">在「真的 fashion」中有多少被預測到？</div><div class="ratio">197 / 309</div><div class="ratio-result">≈ 63.8%</div><div class="meter"><i style="width:63.8%"></i></div></div></div><div class="micro-label">講義交叉表的兩種條件機率，非另外蒐集的調查數據</div></div></div></div>'''
    if kind=='expected':
        return f'''<div class="work-grid"><div class="narrative"><span class="overline">把機率變成可計算的量</span><div class="big-query">E(X) = Σ x · P(X = x)</div><p>講義購物情境：以機率加權收入，得到</p><div class="math-line">970×0.6 + 800×0.3 + 0×0.1</div><div class="highlight-num">= 822 <small>元</small></div><div class="mini-note">你不會真的收到 822 元，但它是此隨機模型的期望收入。</div></div><div class="graphic-side"><div class="panel"><div class="panel-title">三種結果的機率 <small>（講義案例）</small></div>{coin_chart()}</div></div></div>'''
    if kind=='normal':
        return f'''<div class="work-grid"><div class="narrative"><span class="overline">平均數之外，還有相對位置</span><div class="big-query">Z = (觀察值 − 平均) / 標準差</div><p>講義中的 TOEFL 例子：<b>70 分</b>，平均 <b>80 分</b>，標準差 <b>25 分</b>。</p><div class="math-line">Z = (70 − 80) / 25 = −0.4</div><div class="mini-note">表示低於平均 <strong>0.4 個標準差</strong>。不同考試不能只比較原始分數。</div></div><div class="graphic-side"><div class="panel"><div class="panel-title">標準常態分配 <small>（示意鐘形曲線）</small></div>{normal_chart()}</div></div></div>'''
    if kind=='ci':
        return f'''<div class="work-grid"><div class="narrative"><span class="overline">第三步，讓估計附帶不確定性</span><div class="big-query">樣本 400 人，240 人買咖啡</div><p>樣本比例 <b>p̂ = 240 / 400 = 0.60</b>，在隨機抽樣及適用條件下，使用常態近似：</p><div class="math-line">95% CI = 0.60 ± 1.96 × √(0.6×0.4 / 400)</div><div class="mini-note"><b>重要：</b>這是 Wiki 裡的自編計算，不是真實的學校調查。抽樣方式與模型條件會影響推論可靠度。</div></div><div class="graphic-side"><div class="panel"><div class="panel-title">95% 信賴區間 <small>（自編數據）</small></div>{interval_chart()}<div class="micro-label">反覆依相同方法建立區間，約 95% 的區間會涵蓋固定母體比例。</div></div></div></div>'''
    if kind=='pvalue':
        return '''<div class="work-grid"><div class="narrative"><span class="overline">第四步，檢驗一個主張</span><div class="big-query">假設 H₀：母體比例 p = 0.50</div><p>講義調查樣本 <b>n = 1,000</b>、觀察比例 <b>p̂ = 0.37</b>。如果 H₀ 為真，這樣的落差會有多罕見？</p><div class="math-line">Z = (0.37 − 0.50) / √(0.5×0.5 / 1,000) ≈ −8.22</div><div class="mini-note">講義先將標準誤近似成 0.016，得到 Z ≈ −8.13；兩者都在 5% 水準下拒絕 H₀。</div></div><div class="graphic-side"><div class="panel"><div class="panel-title">p 值的意義</div><div class="test-flow"><div><small>前提</small><b>先假定 H₀ 成立</b></div><div class="thin-arrow">↓</div><div><small>觀察</small><b>目前結果有多極端？</b></div><div class="thin-arrow">↓</div><div class="p-interpret"><small>p-value</small><b>發生至少同樣極端結果的機率</b></div></div></div></div></div>'''
    if kind=='summary':
        return '''<div class="summary-area"><div class="summary-intro">一個好的統計結論，不能只看最後一個數字。</div><div class="summary-track"><div><span>01</span><b>問問題</b><small>母體是誰？</small></div><i>→</i><div><span>02</span><b>取樣本</b><small>代表性夠嗎？</small></div><i>→</i><div><span>03</span><b>描述資料</b><small>分布怎麼樣？</small></div><i>→</i><div><span>04</span><b>量化不確定</b><small>機率與 SE</small></div><i>→</i><div><span>05</span><b>做推論</b><small>區間與檢定</small></div></div><div class="summary-questions"><div><span>Q1</span> 只在咖啡店門口調查，可能產生什麼偏差？<small>涵蓋偏差；樣本可能無法代表所有學生。</small></div><div><span>Q2</span> 95% 信賴區間是不是代表「參數有 95% 機率在裡面」？<small>不是；指建構方法在長期重複抽樣下的涵蓋率。</small></div></div></div>'''
    raise ValueError(kind)

def source_drawer_items(slide_id, refs):
    evidence=EV[slide_id]['evidence'];sourceids={id for id,p in refs}
    parts=[]
    for k,(sid,page) in enumerate(refs):
        fname=REG[sid]['filename']; related=next((e for e in evidence if e['entry'].endswith(REG[sid]['filename'])),None)
        # use all claims for a source, not file suffix
        match=next((e for e in evidence if any(c['source_id']==sid and c['pdf_page']==page for c in e['citations'])),None)
        if match:
            wiki=match['entry'];excerpt=match['teaching_excerpt']
        else:
            wiki=next((e['entry'] for e in evidence if any(c['source_id']==sid for c in e['citations'])), 'wiki/index.md')
            excerpt='此頁用於補充對應公式／案例；完整內容請查看 Wiki 的相關章節及來源清冊。'
        short=(excerpt[:145]+'…') if len(excerpt)>145 else excerpt
        href='../'+wiki
        parts.append(f'<div class="reference-item"><div class="ref-heading"><span class="source-pill">{sid} · PDF p.{page}</span><small>{E(fname)}</small></div><p>{E(short)}</p><a href="{E(href)}" target="_blank" rel="noopener">查看對應 Wiki</a></div>')
    return ''.join(parts)

def build_html():
    deck=[];refs_manifest={}
    for i,s in enumerate(SLIDES):
        refs=source_refs(s['id'],s['extra']);refs_manifest[s['id']]=refs
        citation_html=source_pills(refs)
        active=' active' if i==0 else ''
        deck.append(f'''<section class="slide{active}" id="slide-{s['id']}" data-slide="{i}" role="group" aria-label="第 {i+1} 頁：{E(s['title'])}">
          <header class="slide-top"><span class="topic-tag">{E(s['section'])}</span><span class="slide-sequence">{i+1:02d} <span>/</span> 12</span></header>
          <div class="slide-content"><div class="heading"><h1>{E(s['title'])}</h1><p>{E(s['sub'])}</p></div>{topic_content(s)}
          {'' if i==0 else f'<div class="takeaway"><span>TAKEAWAY</span><b>{E(s["take"])}</b></div>'}
          </div>
          <footer class="source-footer"><div class="source-summary"><span>WIKI SOURCE</span> {citation_html if citation_html else '<span class="source-note">內容架構依據 S01–S06；下頁開始逐頁列來源</span>'}</div><button class="source-toggle" type="button" data-source-for="{i}" aria-label="開啟第{i+1}頁的來源對照">來源對照 <span>↗</span></button></footer>
        </section>''')
    panels=[]
    for i,s in enumerate(SLIDES):
        refs=refs_manifest[s['id']]
        panels.append(f'<section class="reference-panel" data-refs="{i}"><h3>第 {i+1} 頁 · {E(s["title"])}</h3><p class="ref-lede">來源 ID 對應原始課程講義的 PDF 實體頁碼。此公開版不包含講義 PDF；引用可在 Wiki 找到原始對照。</p>{source_drawer_items(s["id"],refs) if refs else "<p>封面無單獨統計主張。</p>"}</section>')
    css=CSS
    js=JS
    page=f'''<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"/><meta name="theme-color" content="#edf1e9"/><meta name="description" content="從資料到結論：以六份課程講義建立的 LLM Wiki 製作統計學入門教學 HTML 簡報"/><title>統計學入門｜從資料到結論 · Study Journal</title><style>{css}</style></head><body><div class="app-shell"><div class="presentation" id="deck"><div class="deck-accent"><span class="brand-dot"></span> <span>STUDY JOURNAL</span><span class="small-brand"> / STATISTICS GUIDE</span></div>{''.join(deck)}<nav class="bottom-nav" aria-label="簡報導覽"><div class="nav-left"><button type="button" id="menuBtn" aria-label="開啟頁面目錄" title="頁面目錄">☷</button><span class="key-hint">方向鍵切換 · 按 F 全螢幕</span></div><div class="nav-middle"><div class="track" id="progress-track"><span id="progress-bar"></span></div><small id="progress-label">01 / 12</small></div><div class="nav-right"><button type="button" id="prevBtn" aria-label="上一頁">←</button><button type="button" id="nextBtn" aria-label="下一頁">→</button><button type="button" id="fullBtn" title="全螢幕" aria-label="全螢幕">⛶</button></div></nav></div><div class="credit-line">教學內容整理自 Statistics LLM Wiki · 所有自編數據均已標明 · 非官方課程簡報</div></div>
    <div class="overlay" id="overlay" aria-hidden="true"><div class="overlay-shade" id="overlayShade"></div><div class="drawer" role="dialog" aria-modal="true" aria-labelledby="drawerTitle"><div class="drawer-head"><div><small id="drawerEyebrow">SOURCE NOTES</small><h2 id="drawerTitle">來源對照</h2></div><button type="button" id="drawerClose" aria-label="關閉視窗">×</button></div><div class="drawer-body" id="drawerBody"><div id="tocPanel" class="toc-panel"></div>{''.join(panels)}</div></div></div>
    <script>{js}</script></body></html>'''
    (ROOT/'slides/statistics-teaching.html').write_text(page,encoding='utf-8')
    (ROOT/'index.html').write_text('''<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0; url=slides/statistics-teaching.html"><title>統計學入門教學簡報</title></head><body><p>正在前往 <a href="slides/statistics-teaching.html">統計學入門教學簡報</a>…</p></body></html>''',encoding='utf-8')
    (ROOT/'workflow/artifacts/final_slide_refs.json').write_text(json.dumps({k:[{'source_id':a,'pdf_page':b} for a,b in v] for k,v in refs_manifest.items()},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return refs_manifest
CSS=r'''
:root{--bg:#eef1eb;--paper:#fbfaf5;--ink:#1d3932;--muted:#61766d;--deep:#153c31;--green:#2d8469;--lime:#d9ebd4;--stroke:#dce5dc;--shadow:0 30px 90px rgba(25,61,48,.12)}
*{box-sizing:border-box}html,body{margin:0;min-height:100%;font-family:ui-sans-serif,-apple-system,BlinkMacSystemFont,"Noto Sans TC","Microsoft JhengHei",system-ui,sans-serif;color:var(--ink);background:var(--bg)}body{overscroll-behavior:none}
button{font:inherit;cursor:pointer}button:focus-visible,a:focus-visible{outline:3px solid #e6ae5c;outline-offset:3px}a{color:#166a53}
.app-shell{width:100%;height:100dvh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:10px 12px}.presentation{position:relative;background:var(--paper);width:min(1320px,100%);height:min(750px,calc(100dvh - 40px));min-height:570px;border:1px solid #dce4da;border-radius:22px;overflow:hidden;box-shadow:var(--shadow)}
.deck-accent{position:absolute;top:0;left:0;width:100%;height:40px;display:flex;align-items:center;gap:9px;z-index:2;padding:0 44px;background:linear-gradient(90deg,#183e31,#2b6854);color:#e9f6eb;font-size:11px;font-weight:800;letter-spacing:2px}.brand-dot{width:9px;height:9px;background:#cae98b;border-radius:50%}.small-brand{font-weight:500;letter-spacing:1.3px;opacity:.7}
.slide{position:absolute;display:none;top:40px;left:0;right:0;bottom:58px;padding:27px 54px 0;overflow-y:auto;overflow-x:hidden;scrollbar-color:#b6ccbf transparent}.slide.active{display:flex;flex-direction:column;animation:fadeUp .24s ease both}
@keyframes fadeUp{0%{opacity:.3;transform:translateY(9px)}100%{opacity:1;transform:translateY(0)}}
.slide-top{display:flex;justify-content:space-between;align-items:center;min-height:23px;flex:none}.topic-tag{display:inline-flex;align-items:center;font-size:11px;font-weight:900;letter-spacing:1.2px;color:#28775e;text-transform:uppercase}.slide-sequence{font-size:16px;font-weight:900;color:#264e40;font-variant-numeric:tabular-nums}.slide-sequence span{font-weight:500;color:#a1b5aa}
.slide-content{flex:1;min-height:0;display:flex;flex-direction:column}.heading{flex:none;padding-top:5px}.heading h1{font-size:clamp(30px,3.15vw,49px);font-weight:900;letter-spacing:-1.6px;line-height:1.14;margin:3px 0 5px}.heading p{font-size:clamp(14px,1.37vw,18px);color:var(--muted);margin:0 0 12px;line-height:1.5}
.work-grid{display:grid;grid-template-columns:46% 54%;gap:20px;align-items:stretch;flex:1;min-height:310px;max-height:390px;margin:5px 0 12px}.narrative{background:#f2f5ed;border:1px solid #e0e8dc;border-radius:18px;padding:22px 23px;display:flex;flex-direction:column;min-width:0;justify-content:center}.overline{font-size:10px;font-weight:900;letter-spacing:1.4px;color:#2e7d62}.big-query{font-weight:900;line-height:1.28;letter-spacing:-.35px;font-size:clamp(21px,2.13vw,31px);margin:12px 0 10px;color:#1c4436}.narrative p{line-height:1.65;color:#435d50;font-size:clamp(14px,1.18vw,16px);margin:0 0 10px}.narrative .em{font-weight:850;color:#2c775d}.mini-note{background:#fff;border-radius:11px;border-left:3px solid #5aa989;color:#41564c;font-size:13px;line-height:1.56;padding:10px 13px;margin-top:auto}.mini-note strong,.mini-note b{color:#17624d}
.graphic-side{min-width:0;display:flex;align-items:stretch}.panel{background:#fff;border:1px solid #e3eae1;border-radius:18px;padding:18px 20px;width:100%;min-height:270px;box-shadow:0 10px 24px #244a3709;display:flex;flex-direction:column;justify-content:center}.panel svg{width:100%;max-height:270px;flex:1}.panel-title{font-size:15px;font-weight:850;color:#254e3f;margin-bottom:8px;display:flex;flex-wrap:wrap;gap:4px}.panel-title small{font-size:11px;font-weight:500;color:#829488}.micro-label{font-size:11px;color:#72887c;line-height:1.45;margin-top:4px;text-align:center}
.takeaway{flex:none;display:flex;align-items:center;gap:13px;margin:3px 0 8px;padding:11px 15px;border-radius:12px;background:#dcebdd;color:#224c3b;line-height:1.35;font-size:13px}.takeaway span{font-size:10px;font-weight:900;letter-spacing:1.1px;opacity:.7;flex:none}.takeaway b{font-weight:750}
.source-footer{flex:none;min-height:46px;border-top:1px solid var(--stroke);display:flex;align-items:center;justify-content:space-between;gap:10px;color:var(--muted);font-size:11px;padding:6px 0}.source-summary{display:flex;align-items:center;flex-wrap:wrap;gap:5px;min-width:0}.source-summary>span:first-child{font-size:9px;font-weight:900;letter-spacing:1px;color:#779083;margin-right:6px}.source-pill{border-radius:40px;background:#edf3eb;border:1px solid #dbe7dd;color:#357258;display:inline-flex;align-items:center;white-space:nowrap;font-size:10px;padding:3px 7px;font-weight:650}.source-note{color:#738a7f}.source-toggle{border:0;background:transparent;color:#2c795d;font-size:12px;white-space:nowrap;font-weight:800;padding:6px}.source-toggle span{font-size:17px}
.bottom-nav{position:absolute;bottom:0;left:0;right:0;height:58px;background:#eff3eb;border-top:1px solid #e0e6dc;display:grid;grid-template-columns:1fr 1.15fr 1fr;align-items:center;padding:0 24px;z-index:5;gap:12px}.nav-left,.nav-middle,.nav-right{display:flex;align-items:center;gap:12px}.nav-middle{justify-content:center}.nav-right{justify-content:flex-end}.nav-left button,.nav-right button{height:37px;min-width:40px;background:#fff;border:1px solid #dae6da;border-radius:11px;color:#2b6c54;font-weight:900;font-size:21px}.nav-right button#nextBtn{background:#245e49;color:#fff;border-color:#245e49}.nav-left button:hover,.nav-right button:hover{filter:brightness(.95)}.key-hint{font-size:10px;color:#71867b}.track{height:6px;background:#d4dfd3;border-radius:5px;overflow:hidden;width:min(280px,18vw)}#progress-bar{display:block;width:8.333%;height:100%;background:#328c6e;border-radius:5px;transition:width .2s}#progress-label{font-size:12px;white-space:nowrap;font-variant-numeric:tabular-nums;color:#3a6652;font-weight:800}.credit-line{height:18px;line-height:18px;font-size:10px;text-align:center;color:#7b897f}
.cover-layout{display:grid;grid-template-columns:58% 42%;align-items:center;min-height:360px;flex:1;max-height:410px}.heading:has(+.cover-layout) h1{font-size:clamp(35px,4.1vw,57px);margin-bottom:8px}.cover-left{padding:4px 8px 8px 0}.large-step{font-size:clamp(26px,3.0vw,43px);line-height:1.28;letter-spacing:-1px;font-weight:920}.large-step span{color:#3b9a75}.cover-p{font-size:17px;color:#5c7266;line-height:1.7;max-width:540px}.cover-tags{display:flex;flex-wrap:wrap;gap:8px;margin-top:20px}.cover-tags span{font-size:11px;border:1px solid #cadec8;border-radius:30px;padding:8px 12px;background:#ecf3e8;color:#36664e;font-weight:800}.cover-right{display:flex;align-items:center;justify-content:center;height:100%}.cover-motif{width:90%;max-width:370px;border-radius:26px;padding:24px;min-height:310px;background:linear-gradient(150deg,#215e48,#4f997d);box-shadow:0 20px 35px #1c6d4826;display:flex;align-items:center;justify-content:center;flex-direction:column}.motif-pill{background:#e6f1d9;color:#225b43;padding:11px 26px;border-radius:999px;font-size:15px;font-weight:900;letter-spacing:1px}.motif-pill.light{background:transparent;border:1.5px solid #c8e4cb;color:#fff}.motif-stem{width:2px;height:23px;background:#bce2c5}.motif-plot{height:135px;width:240px;background:#f9fcf8;border-radius:19px;padding:17px 18px;display:flex;align-items:flex-end;gap:12px;box-shadow:0 10px 35px #17493240}.motif-plot span{flex:1;display:block;border-radius:7px 7px 2px 2px;background:#62aa8e}
.split-figure{display:flex;align-items:center;justify-content:space-evenly;gap:12px;width:100%}.symbol-box{display:flex;min-width:0;flex:1;align-items:center;justify-content:center;flex-direction:column;background:#e3efe8;border-radius:16px;padding:15px 7px;height:210px}.symbol-box.pale{background:#f4eedf}.stat-symbol{font-family:Georgia,serif;font-size:60px;color:#276c57;font-style:italic;font-weight:800}.symbol-box b{font-size:16px}.symbol-box span{font-size:12px;color:#708078;margin-top:7px}.flow-forward{font-size:30px;color:#569b7c}.two-stats{display:flex;gap:10px;margin:14px 0}.two-stats>div{flex:1;background:#fff;border-radius:12px;padding:11px 12px}.two-stats span{display:block;color:#698375;font-size:12px}.two-stats strong{font-size:36px;color:#287659;font-weight:900}.two-stats small{font-size:13px}
.data-table{font-size:13px;display:flex;flex-direction:column;gap:0;overflow:hidden;border:1px solid #dbe6dc;border-radius:12px}.tbl-head,.tbl-row{display:grid;grid-template-columns:.6fr .7fr 1.2fr 1.3fr;align-items:center}.tbl-head{background:#dcebe0;color:#285740;font-weight:900}.tbl-row:nth-child(odd){background:#f4f7f2}.tbl-row span,.tbl-head span{padding:12px 10px;white-space:nowrap;text-align:center}.tbl-row span:first-child{font-weight:900;color:#318765}
.prob-bars{display:flex;align-items:flex-end;justify-content:space-around;gap:20px;flex:1;min-height:210px}.prob-col{height:100%;display:flex;align-items:center;flex-direction:column;justify-content:flex-end;gap:10px;min-width:75px}.prob-col b{font-size:24px;color:#24654f}.prob-track{height:155px;width:62px;display:flex;align-items:flex-end;background:#eef4ed;border-radius:12px;padding:5px}.prob-track>span{display:block;width:100%;border-radius:9px 9px 4px 4px}.prob-col small{font-size:15px;color:#6b8075;font-weight:700}.math-line{font-size:clamp(14px,1.28vw,18px);font-family:Georgia,"Noto Serif TC",serif;font-weight:700;padding:12px 10px;color:#246d51;background:#fff;border-radius:10px;line-height:1.4}.highlight-num{font-size:33px;font-weight:920;color:#26765a}.highlight-num small{font-size:16px}
.comparison{display:grid;grid-template-columns:1fr 1fr;gap:14px}.comparison>div{background:#f3f7f0;padding:18px 14px;border-radius:14px;display:flex;flex-direction:column;gap:10px}.ratio-label{font-size:13px;line-height:1.5;min-height:43px;color:#4e655a}.ratio{font-size:23px;font-weight:900;color:#254b3e;font-variant-numeric:tabular-nums}.ratio-result{font-size:26px;color:#258267;font-weight:900}.meter{height:11px;background:#e0e8df;border-radius:9px;overflow:hidden}.meter i{display:block;height:100%;border-radius:9px;background:#68b594}
.test-flow{display:flex;flex-direction:column;align-items:center;justify-content:center;flex:1;gap:4px}.test-flow>div:not(.thin-arrow){width:100%;border-radius:13px;padding:12px 18px;background:#f1f6ef;display:flex;flex-direction:column;align-items:center;gap:4px}.test-flow small{font-size:10px;letter-spacing:1px;color:#719082}.test-flow b{font-size:15px;color:#275640}.test-flow .p-interpret{background:#dceddd!important}.thin-arrow{color:#66a388;font-size:20px}
.summary-area{flex:1;display:flex;flex-direction:column;justify-content:center;gap:24px}.summary-intro{font-size:clamp(21px,2.2vw,29px);font-weight:900;color:#27614b}.summary-track{display:flex;gap:6px;align-items:center}.summary-track>div{flex:1;background:#eff4ec;border-radius:15px;padding:17px 8px;text-align:center;display:flex;flex-direction:column;gap:7px;min-width:0}.summary-track>div span{font-weight:900;color:#398265;font-size:13px}.summary-track>div b{font-size:16px}.summary-track>div small{font-size:11px;color:#728679}.summary-track>i{font-size:25px;font-style:normal;color:#7eb69d}.summary-questions{display:grid;grid-template-columns:1fr 1fr;gap:13px}.summary-questions>div{border:1px solid #dfebe0;border-radius:15px;padding:16px;font-weight:760;font-size:14px;line-height:1.6}.summary-questions span{font-weight:900;color:#288665;margin-right:6px}.summary-questions small{display:block;font-weight:500;color:#657e70;font-size:12px;margin-top:9px}
.overlay{position:fixed;inset:0;z-index:20;display:none}.overlay.open{display:block}.overlay-shade{position:absolute;inset:0;background:#0b221aa0}.drawer{position:absolute;right:0;top:0;bottom:0;overflow:hidden;width:min(540px,100vw);background:#fbfcf9;box-shadow:-20px 0 80px #122c2039;display:flex;flex-direction:column}.drawer-head{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:26px 30px;border-bottom:1px solid #e0e9e1}.drawer-head small{font-size:10px;letter-spacing:1.3px;color:#599479;font-weight:900}.drawer-head h2{margin:4px 0 0;font-size:23px}.drawer-head button{width:39px;height:39px;border-radius:12px;border:1px solid #dee8df;background:white;font-size:28px;color:#315e47}.drawer-body{overflow-y:auto;flex:1;padding:22px 30px}.reference-panel{display:none}.reference-panel.visible{display:block}.reference-panel h3{margin:0 0 8px;font-size:21px}.ref-lede{font-size:13px;line-height:1.7;color:#708377;margin:0 0 20px}.reference-item{padding:17px 0;border-bottom:1px solid #e4ece5}.ref-heading{display:flex;align-items:center;flex-wrap:wrap;gap:10px}.ref-heading small{font-size:11px;color:#697e73;word-break:break-all}.reference-item p{font-size:13px;line-height:1.65;color:#40594c}.reference-item a{font-weight:800;font-size:13px}.toc-panel{display:none}.toc-panel.visible{display:block}.toc-entry{width:100%;display:flex;justify-content:space-between;gap:15px;align-items:center;background:#fff;border:1px solid #e4eae0;border-radius:10px;padding:11px 14px;text-align:left;margin:0 0 9px;font-size:14px;color:#284837}.toc-entry:hover{background:#f2f8ef}.toc-entry span{font-weight:900;color:#3a9772;font-size:11px}
@media (max-width:980px){.presentation{height:min(780px,calc(100dvh - 30px))}.slide{padding:20px 26px 0}.heading h1{font-size:36px}.work-grid{grid-template-columns:47% 53%;gap:10px}.narrative{padding:16px}.big-query{font-size:22px}.narrative p{font-size:14px}.panel{padding:12px}.cover-motif{min-height:280px}.summary-track>div b{font-size:13px}}
@media (max-width:650px){.app-shell{padding:0}.presentation{width:100%;height:100dvh;min-height:0;border-radius:0;border:0}.deck-accent{height:38px;padding:0 17px}.slide{top:38px;bottom:65px;padding:13px 16px 0}.slide-top{min-height:21px}.heading h1{font-size:clamp(26px,7.3vw,34px);line-height:1.15;letter-spacing:-.7px}.heading p{font-size:13px;margin-bottom:8px}.work-grid{display:flex;flex-direction:column;max-height:none;min-height:0;gap:10px;flex:0;margin:5px 0 12px}.narrative{padding:14px;min-height:0}.big-query{font-size:23px;margin:6px 0}.narrative p{font-size:13px;line-height:1.45}.mini-note{font-size:11px;padding:9px 10px;margin-top:6px}.graphic-side{min-height:190px}.panel{padding:12px;min-height:210px}.panel svg{max-height:190px}.panel-title{font-size:13px}.source-footer{margin-top:auto;align-items:flex-start;gap:4px}.source-summary{max-width:76%}.source-pill{font-size:9px;padding:3px 5px}.source-summary>span:first-child{font-size:8px}.source-toggle{font-size:11px}.takeaway{font-size:12px;padding:9px 10px;gap:8px;flex-wrap:wrap}.bottom-nav{height:65px;padding:0 13px;grid-template-columns:43px 1fr auto}.nav-left .key-hint{display:none}.nav-middle{gap:7px}.track{width:24vw}.nav-left button,.nav-right button{min-width:37px;height:40px}.nav-right{gap:5px}.credit-line{display:none}.cover-layout{display:flex;flex-direction:column;max-height:none;gap:5px;align-items:stretch}.cover-left{padding:0}.large-step{font-size:clamp(26px,6.8vw,34px);margin-top:8px}.cover-p{font-size:13px;line-height:1.55;margin:12px 0}.cover-tags{margin-top:8px}.cover-tags span{font-size:10px;padding:6px 9px}.cover-right{height:210px;flex:0}.cover-motif{min-height:180px;width:100%;max-width:none;padding:12px;flex-direction:row;gap:14px}.motif-pill{font-size:10px;padding:7px}.motif-stem{height:2px;width:14px}.motif-plot{height:115px;width:115px;gap:5px;padding:10px}.two-stats strong{font-size:27px}.data-table{font-size:10px}.tbl-row span,.tbl-head span{padding:10px 4px}.comparison{gap:7px}.comparison>div{padding:10px 8px}.ratio-label{font-size:11px;min-height:52px}.ratio{font-size:17px}.ratio-result{font-size:19px}.prob-track{height:130px}.math-line{font-size:13px}.summary-area{gap:13px}.summary-intro{font-size:19px}.summary-track{flex-direction:column;align-items:stretch;gap:3px}.summary-track>div{flex-direction:row;justify-content:space-around;align-items:center;padding:7px 9px}.summary-track>i{transform:rotate(90deg);font-size:15px;text-align:center}.summary-track>div b{font-size:13px}.summary-track>div small{font-size:10px}.summary-questions{grid-template-columns:1fr;gap:7px}.summary-questions>div{font-size:11px;padding:9px 12px}.summary-questions small{font-size:10px;margin-top:5px}.drawer-head{padding:17px 19px}.drawer-body{padding:16px 19px}}
@media (max-height:700px) and (min-width:651px){.presentation{min-height:0}.slide{padding-top:12px}.heading h1{font-size:32px}.work-grid{min-height:0;max-height:320px}.narrative{padding:13px}.big-query{font-size:24px}.panel{min-height:245px;padding:12px}.panel svg{max-height:235px}.takeaway{padding:7px 12px}.cover-layout{max-height:300px}.cover-motif{min-height:260px}}
@media print{html,body{background:#fff!important;height:auto}.app-shell{display:block;height:auto;padding:0}.presentation{height:auto;width:100%;border:none;box-shadow:none;overflow:visible}.deck-accent,.bottom-nav,.overlay,.credit-line{display:none!important}.slide{position:relative;display:flex!important;height:180mm;top:auto;bottom:auto;left:auto;right:auto;overflow:hidden;break-after:page;padding:10mm 12mm 8mm;border-bottom:1px solid #ddd}.slide-content{min-height:0}.work-grid{max-height:110mm}.source-toggle{display:none}}
'''
JS=r'''(()=>{const slides=[...document.querySelectorAll('.slide')],total=slides.length,progress=document.getElementById('progress-bar'),lab=document.getElementById('progress-label');let current=0,lastFocus=null;const overlay=document.getElementById('overlay'),toc=document.getElementById('tocPanel');const refs=[...document.querySelectorAll('.reference-panel')];const drawerTitle=document.getElementById('drawerTitle'),eye=document.getElementById('drawerEyebrow');const tocLinks=slides.map((s,i)=>`<button type="button" class="toc-entry" data-target="${i}"><span>${String(i+1).padStart(2,'0')}</span>${s.querySelector('h1').textContent}</button>`).join('');toc.innerHTML=tocLinks;function show(i){current=Math.max(0,Math.min(total-1,i));slides.forEach((s,n)=>{s.classList.toggle('active',n===current);s.setAttribute('aria-hidden',n===current?'false':'true');if(n===current)s.scrollTop=0});progress.style.width=`${(current+1)/total*100}%`;lab.textContent=`${String(current+1).padStart(2,'0')} / ${total}`;document.getElementById('prevBtn').disabled=current===0;document.getElementById('nextBtn').disabled=current===total-1;history.replaceState(null,'',`#slide-${String(current+1).padStart(2,'0')}`)}function closeDrawer(){overlay.classList.remove('open');overlay.setAttribute('aria-hidden','true');document.body.style.overflow='';lastFocus?.focus()}function openDrawer(which){lastFocus=document.activeElement;overlay.classList.add('open');overlay.setAttribute('aria-hidden','false');toc.classList.toggle('visible',which==='toc');refs.forEach((p,n)=>p.classList.toggle('visible',which===n));drawerTitle.textContent=which==='toc'?'簡報目錄':'來源對照';eye.textContent=which==='toc'?'CONTENTS':'SOURCE NOTES';document.getElementById('drawerBody').scrollTop=0;document.getElementById('drawerClose').focus()}
document.getElementById('prevBtn').addEventListener('click',()=>show(current-1));document.getElementById('nextBtn').addEventListener('click',()=>show(current+1));document.getElementById('menuBtn').addEventListener('click',()=>openDrawer('toc'));document.querySelectorAll('[data-source-for]').forEach(b=>b.addEventListener('click',()=>openDrawer(Number(b.dataset.sourceFor))));toc.addEventListener('click',e=>{const b=e.target.closest('[data-target]');if(b){closeDrawer();show(Number(b.dataset.target))}});document.getElementById('drawerClose').addEventListener('click',closeDrawer);document.getElementById('overlayShade').addEventListener('click',closeDrawer);document.getElementById('fullBtn').addEventListener('click',()=>{const el=document.getElementById('deck');if(document.fullscreenElement){document.exitFullscreen?.()}else{el.requestFullscreen?.()}});document.addEventListener('keydown',e=>{if(overlay.classList.contains('open')){if(e.key==='Escape')closeDrawer();return}if(['ArrowRight','PageDown',' '].includes(e.key)){if(e.target.matches('button,input,textarea'))return;e.preventDefault();show(current+1)}else if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();show(current-1)}else if(e.key==='Home'){e.preventDefault();show(0)}else if(e.key==='End'){e.preventDefault();show(total-1)}else if(e.key.toLowerCase()==='f'&&!e.ctrlKey&&!e.altKey&&!e.metaKey){document.getElementById('fullBtn').click()}});let xStart=null;document.querySelector('.presentation').addEventListener('touchstart',e=>{if(e.touches.length===1)xStart=e.touches[0].clientX},{passive:true});document.querySelector('.presentation').addEventListener('touchend',e=>{if(xStart===null||overlay.classList.contains('open'))return;const diff=e.changedTouches[0].clientX-xStart;xStart=null;if(Math.abs(diff)>90){show(current+(diff<0?1:-1))}},{passive:true});const m=location.hash.match(/slide-(\d+)/);show(m?Number(m[1])-1:0)})();'''

CSS += r'''
@media(max-width:650px){
 .slide{height:auto;display:none;overflow-y:auto;overscroll-behavior:contain}
 .slide.active{display:block}
 .slide-content{flex:none;min-height:auto;display:block}
 .heading{display:block}
 .work-grid{display:flex;flex-direction:column;flex:none;min-height:0;max-height:none;height:auto}
 .work-grid>.narrative,.work-grid>.graphic-side{flex:0 0 auto;min-height:0}
 .narrative{display:block}
 .panel{height:auto;min-height:220px}
 .takeaway{margin-top:12px}
 .cover-layout{display:block;min-height:0;height:auto;max-height:none}
 .cover-right{height:200px;margin-top:12px}
 .summary-area{display:block}
 .summary-track,.summary-questions{margin-top:15px}
 .source-footer{margin-top:15px}
}
'''

if __name__=='__main__':
    refs=build_html()
    print('Built slides/statistics-teaching.html', (ROOT/'slides/statistics-teaching.html').stat().st_size, 'bytes')
    print('Reference count',sum(len(v) for v in refs.values()), 'unique sources',len({sid for v in refs.values() for sid,p in v}))
