# 統計學學習知識庫｜LLM Wiki 索引

> Step 3 完成：已從 **六份真實課程講義**逐篇建立來源卡與 Wiki 條目；已完成檔案、引用格式／頁次及部分數值驗證。STEP 5 已製作正式 12 頁 HTML 教學簡報；本機來源／算術／瀏覽器檢查已執行，獨立學術審查及公開網站部署仍待完成。

## 五大主題與六篇 Wiki 條目

1. **[資料與抽樣](entries/data-and-sampling.md)** — 資料分類、抽樣與實驗設計。來源：[S01 來源卡](sources/cards/S01.md)。
2. **[敘述統計](entries/summarizing-data.md)** — 平均與變異、圖表、偏態與離群。來源：[S02 來源卡](sources/cards/S02.md)。
3. **[機率](entries/probability-and-random-variables.md)** — 機率規則、條件機率、隨機變數與相關。來源：[S03 來源卡](sources/cards/S03.md)。
4. **[隨機變數與分配](entries/random-variable-distributions.md)** — 常態與伯努利、二項、幾何、卜瓦松。來源：[S04 來源卡](sources/cards/S04.md)。
5. **[統計推論：估計](entries/inference-estimation.md)** — CLT、估計量與信賴區間。來源：[S05 來源卡](sources/cards/S05.md)。
6. **[統計推論：假設檢定](entries/inference-hypothesis-testing.md)** — H0/HA、p值、兩類錯誤與Z檢定。來源：[S06 來源卡](sources/cards/S06.md)。

## 從哪裡開始讀？

若是完全沒有統計基礎，可以按本頁的順序閱讀：資料與抽樣 → 敘述統計 → 機率 → 隨機變數與分配 → 統計推論。

若是準備考試，請依照授課章節查詢相對應條目。公式、例題與重要主張旁均盡量註明 `[Sxx, PDF p.n]`。

## 可追溯的研究及來源

- [六份原始講義來源總清冊](sources/source_registry.csv)：檔名、SHA-256、實際 PDF 頁數與 ingest 狀態。
- [課程文件核對報告](sources/source_audit.md)：總共 23 份統計學資料的核對及排除理由。
- [主題與來源覆蓋矩陣](sources/coverage_matrix.csv)。
- [來源分頁地圖](sources/page_maps/)：一共 177 個 PDF 實體頁的逐頁標題索引。
- [來源差異及處理](conflicts.md)：四捨五入、條件及後續待查證項目。
- [程式化檢查結果](../reports/audit_wiki.json)。

## 認識本專案的「ingest」

這裡的 ingest 不只是存檔：每份講義都已被讀取，擷取主題及頁面定位點、建立來源卡，再寫成新的中文知識筆記並通過基礎檢查。

**注意：**本專案只公開自編整理；原始老師講義仍保留在私人 `raw/`，不會包含於公開版壓縮檔。外部統計教材目前是候選，尚未納入完成 ingest 的六份來源。

## 對應教學簡報

- [從資料到結論：統計學如何幫助我們做判斷？（HTML 簡報）](../slides/statistics-teaching.html)
- [簡報逐頁來源 ID 及頁次對照](../workflow/artifacts/final_slide_refs.json)
- [STEP 5 Graph 執行與修正](../reports/step5/run_final_graph.md)
