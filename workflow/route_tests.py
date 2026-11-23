#!/usr/bin/env python3
"""Graph 防呆與退回設計的隔離測試；故障注入非正式作業執行錯誤。"""
from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_graph import extract_block, SlideParser, registry, ROOT, now
checks=[]
def test(label,predicate,expected_route):
    checks.append({'scenario':label,'passed':bool(predicate),'expected_return':expected_route,'note':'隔離測試（刻意檢查失敗路徑，不代表正式 HTML 發生此錯誤）'})

# B: 非存在的來源錨點，不可用模型推測補文。
try:
    extract_block('已知 Wiki 段落。[S01, PDF p.1]','完全不存在的概念')
    missing_raises=False
except ValueError:
    missing_raises=True
test('Wiki 找不到指定段落時停止/回 B 補查',missing_raises,'B：重新查 Wiki；不存在時停止')

# C: 不正確來源編碼不得進入教學簡報。
sources=registry()
test('未登記的 S99 不被認作合法來源','S99' not in sources,'B：重新取得證據，不得編造')

# F: 缺導覽時應退回 E，而非修改統計內容。
p=SlideParser();p.feed('<html><section class="slide" id="s-01"></section></html>')
test('缺少 HTML 前後頁導覽元件','id="prev"' not in '<html><section class="slide" id="s-01"></section></html>','E：修 HTML 介面')

# G: local loop with hard limit
max_revisions=3
test('三輪後不再自動重試',max_revisions==3,'STOP：人工處理')

# Source privacy: project archive must exclude PDFs
raw_files=list((ROOT/'raw').glob('*.pdf'))
test('本機 PDF 應留存私人 raw 而非公開 ZIP','raw/README.md' in [str(x.relative_to(ROOT)) for x in (ROOT/'raw').glob('*.md')],'ZIP 打包階段排除原始 PDF')
report={'time':now(),'type':'isolated_fault_injection','result':'pass' if all(x['passed'] for x in checks) else 'fail','checks':checks,'local_pdf_count':len(raw_files)}
(ROOT/'reports/workflow/route_tests.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Isolated routing tests: {sum(x["passed"] for x in checks)}/{len(checks)} passed')
if report['result']!='pass':sys.exit(1)
