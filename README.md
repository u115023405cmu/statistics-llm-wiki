# Statistics Learning Wiki｜統計學入門 LLM Wiki

第 10 週生成式 AI 作業，目前已完成 **STEP 5：正式 12 頁教學型 HTML 簡報**。

## 立即開啟成果

- **[公開網站首頁入口](index.html)**：自動導向正式簡報。
- **[正式 HTML 教學簡報](slides/statistics-teaching.html)**：《從資料到結論：統計學如何幫助我們做判斷？》；可以用方向鍵或按鈕切換、查看來源對照；有圖表、計算與自編案例。
- [統計學 LLM Wiki](wiki/index.md)：六份來源講義、五大主題、六篇繁體中文條目。
- [Graph 工作流程](workflow/README.md)、[STEP 4 原型](slides/workflow-preview.html)。

## 本階段已實際執行的檢查

- Wiki 採用 S01–S06 **六份已 ingest 的課程講義**；教學簡報的全部來源皆可回查 `wiki/entries/` 中的引用標記。
- 靜態檢查：**187/187 項通過**，包含檔案、引用 ID 與頁碼範圍、連結、圖表存在與自編例題算術。
- Chromium 桌機（1280×800）和手機（390×844）檢查：**46/46 項通過**；手機允許個別較長頁垂直捲動。
- 使用者可查閱真正出現過的手機版文字重疊問題，以及一次 CSS 修正再驗證的紀錄：`reports/step5/visual-iteration.md`。
- **不能宣稱已完成獨立學術審查**：原始講義與 Wiki 每句的另一位審查者比對、公開網址驗證仍待完成。

## 可重複執行的 Graph 工作流程

從本專案根目錄執行：

```bash
python workflow/run_final_graph.py
```

執行階段：Wiki 稽核 → STEP 4 證據卡／12 頁大綱 → 正式 HTML → 靜態引用／算術驗證 → Chromium 雙尺寸測試 → 執行報告。若來源不合格或檢查失敗，會停止，而非自行補造統計敘述。

也能單獨執行：

```bash
python workflow/build_final_deck.py
python workflow/check_final_deck.py
python workflow/check_final_deck_browser.py
```

前兩項只需 Python（另需 bs4 才能執行靜態檢查），瀏覽器測試需 Playwright 與 Chromium。若缺少瀏覽器環境會標註未執行。程式採用相同 Wiki 證據與固定教學案例，更新 Wiki 後應重新核對案例，不得宣稱會無限制「自動創作」新統計內容。

## 專案主要檔案

- `AGENTS.md`：規則與可重複使用的來源／驗收標準。
- `wiki/entries/`：六篇正式 Wiki；`wiki/sources/`：來源卡、來源清冊、分頁地圖。
- `workflow/lesson_spec.json`、`workflow/artifacts/evidence_cards.json`：圖節點的教學主張與來源證據。
- `workflow/artifacts/final_slide_refs.json`：正式 12 頁簡報逐頁引用對照。
- `workflow/design.mmd`：STEP 4 Graph；`workflow/run_final_graph.py`：STEP 5 擴充執行入口。
- `reports/step5/`：靜態／瀏覽器測試、來源對照、版面修正紀錄與審查限制。
- `slides/statistics-teaching.html`：正式網頁；`index.html`：公開入口。

## GitHub Pages 公開部署（尚未操作）

建立新的公開 GitHub Repository（建議 `statistics-llm-wiki`），將**此 ZIP 解壓後根目錄中的檔案及資料夾**上傳，設定 `Settings → Pages → Deploy from a branch → main → /(root)`。公開後確認首頁和 12 頁操作正常，才能把網站網址填入作業。不要直接上傳 ZIP 或額外包一層資料夾。

## 隱私與來源界線

- **這份公開版 ZIP 不包含老師的六份原始 PDF**；原始講義請自行保存在私有的 `raw/`，不要上傳公開倉庫。
- 本專案 Wiki 使用老師提供的統計學課程講義，公式、概念和例題由使用者的個人學習專案重新整理。自編練習有標示，不當作原始講義內容。
- 外部教材尚未完成正式 ingest，**不要**將其誤寫成此次簡報已使用的來源。
- `AGENTS.md`、Graph 與可重跑的執行報告旨在讓老師看到「來源 → 整理 → 查核 → 生成 → 修正」的實際流程，分數由老師評定。
