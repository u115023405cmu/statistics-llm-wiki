#!/usr/bin/env python3
"""STEP 5 總流程入口：Wiki → 證據 → 教學簡報 → 檢查 → 記錄。

可在 Python 3.10+ 重新執行。瀏覽器測試需 Playwright/Chromium；無安裝時明確標示。
來源／內容錯誤不靠無根據的自動重寫來「修好」，而會停止要求人工查核。
"""
from pathlib import Path
import subprocess, datetime, json, sys
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
REPORTS=ROOT/'reports/step5'
REPORTS.mkdir(exist_ok=True,parents=True)
steps=[
 ('A — 核對 Wiki','scripts/audit_wiki.py'),
 ('B/C/D/E — STEP4 證據卡及 HTML 原型','workflow/run_graph.py'),
 ('F — 正式教學 HTML 產生','workflow/build_final_deck.py'),
 ('G — 簡報靜態引用與數學驗證','workflow/check_final_deck.py'),
 ('H — Chromium 桌機／手機驗證','workflow/check_final_deck_browser.py'),
]
result=[]
for name,script in steps:
  r=subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT,capture_output=True,text=True,timeout=180)
  result.append({'node':name,'file':script,'return_code':r.returncode,'stdout':r.stdout[-3500:],'stderr':r.stderr[-1500:],'status':'PASS' if r.returncode==0 else 'NOT_RUN' if r.returncode==2 else 'FAIL'})
  print(name, result[-1]['status'])
  if r.returncode!=0: break
run={'time':datetime.datetime.now(ZoneInfo('Asia/Taipei')).isoformat(timespec='seconds'),
     'state':'ready_for_user_review' if len(result)==len(steps) and all(x['return_code']==0 for x in result) else 'stopped_or_browser_pending',
     'node_results':result,
     'limits':'每階段出錯都停止，不擅自更動來源。局部重試最多三輪的排版 Loop 在 workflow/run_graph.py；這次正式版修了手機版 CSS 一次。',
     'pending':'原始講義的獨立逐句學術審查與 GitHub Pages 公開部署，仍需要另外執行。'}
(REPORTS/'run_final_graph.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
log=['# STEP 5｜正式 Graph 執行結果','',f'- 執行時間：{run["time"]}',f'- 狀態：`{run["state"]}`','','| 節點 | 結果 |','|---|---|']
for s in result:log += [f'| {s["node"]} | {s["status"]} |']
log += ['','## 不得超出已驗證的結論','', '- 通過靜態／瀏覽器測試，不能推論每句解釋已完成另一位審查者的獨立學術查核。','- 原始教師講義不收錄於公開 ZIP，重新執行來源 SHA 驗證時會標註跳過私人檔案。','- 此次有真實手機排版問題與修正，詳見 `visual-iteration.md`。','- 第 10 週作業最終公開部署需使用者 GitHub 帳號操作。','']
(REPORTS/'run_final_graph.md').write_text('\n'.join(log),encoding='utf-8')
print('FINAL_STATE:',run['state'])
sys.exit(0 if run['state']=='ready_for_user_review' else 1)
