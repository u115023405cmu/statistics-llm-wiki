# 教學 HTML 簡報大綱（由 Wiki 證據卡生成）

> 這是 Step 4 中間成果；來源是 `wiki/entries/`，不是重新讀取 PDF 或外部搜尋。

共 12 頁；對象：未接觸統計學的大學生。

## 01. 從資料到結論
- 教學定位：一份給統計學初學者的導覽

## 02. 為什麼要學統計？
- 教學定位：用樣本理解母體，而不是只憑直覺
- Wiki 證據：研究對象可能包含數百萬人，無法每個人都調查，因此從樣本推測母體的未知量。母體參數（parameter）是描述整體的數值，如母體支持率 p、母體平均 \mu；統計量（statistic）是從樣本計算的數值，如樣本比例 \hat p 和樣本平均 \bar X。統計推論用「樣本的統計量」估計「母體的參數」。（[S05, PDF p.2]；`wiki/entries/inference-estimation.md`）
- Wiki 證據：抽樣誤差（sampling error）：不同隨機樣本產生不同統計量。（[S05, PDF p.6] [S05, PDF p.7]；`wiki/entries/inference-estimation.md`）

## 03. 資料是怎麼組成的？
- 教學定位：看懂觀察值、變數與資料矩陣
- Wiki 證據：觀察值（observation/case）：研究的一個對象，例如一筆貸款、一位學生。變數（variable）：對每個觀察對象測量的屬性，如貸款金額、利率、居住州別。把每個觀察對象排成一列、各變數排成一欄，就形成資料矩陣（data matrix）。講義以貸款資料矩陣為例。（[S01, PDF p.3] [S01, PDF p.5]；`wiki/entries/data-and-sampling.md`）
- Wiki 證據：解釋變數（explanatory variable）通常是希望用來解釋或預測其他變數的 X；反應變數（response variable）是受關注的結果 Y。X 和 Y 的指定受研究問題影響；不能因為在圖中 X 擺左邊就證明 X 導致 Y。（[S01, PDF p.8]；`wiki/entries/data-and-sampling.md`）

## 04. 抽樣會讓我們看錯嗎？
- 教學定位：母體、樣本，以及偏差的來源
- Wiki 證據：母體（population）是研究欲推論的所有對象；樣本（sample）是實際取得資料的一部分。若要知道某校學生平均完成學位所需時間，觀察到兩名延畢學生的故事，不足以支持整體平均很高。這是把零星個案誤認為代表性資料的問題。（[S01, PDF p.12]；`wiki/entries/data-and-sampling.md`）
- Wiki 證據：未回覆偏差（non-response bias）：被抽到的人不回覆，而回覆與否又和研究特徵有關。（[S01, PDF p.13]；`wiki/entries/data-and-sampling.md`）

## 05. 先用圖表看資料
- 教學定位：先辨認資料種類，再選擇呈現方式
- Wiki 證據：散佈圖（scatterplot）：描述兩個數值變數的關係，例如個人總收入與貸款金額；它不直接證明因果。（[S02, PDF p.4] [S02, PDF p.5] [S02, PDF p.6] [S02, PDF p.10]；`wiki/entries/summarizing-data.md`）
- Wiki 證據：直方圖（histogram）：把數值資料切成區間（bins），觀察次數分布；講義使用貸款利率作例子。箱寬不同可能影響所觀察到的分布細節。（[S02, PDF p.4] [S02, PDF p.5] [S02, PDF p.6] [S02, PDF p.10]；`wiki/entries/summarizing-data.md`）

## 06. 平均與中位數不一樣
- 教學定位：一個極端值，可能讓平均數失真
- Wiki 證據：資料排序後，中位數（median）是中間位置；Q_1 與 Q_3 分別表示第一與第三四分位數，四分位距 IQR=Q_3-Q_1 表示中間 50% 資料的跨度。（[S02, PDF p.11]；`wiki/entries/summarizing-data.md`）
- Wiki 證據：為何同時報告平均與中位數？ 當資料非常右偏、少數值遠大於其他值，平均數容易被拉高，中位數則較能代表典型個案；講義以貸款利率的極端觀察值修改前後比較，展示中位數與 IQR 相對不受影響，平均數與標準差較敏感。（[S02, PDF p.15] [S02, PDF p.16]；`wiki/entries/summarizing-data.md`）

## 07. 機率不是憑感覺
- 教學定位：條件不一樣，分母就不一樣
- Wiki 證據：課堂照片分類的混淆表顯示：在 1,822 張照片中，219 張被系統預測為 fashion，其中 197 張真的屬於 fashion。（[S03, PDF p.18]；`wiki/entries/probability-and-random-variables.md`）
- Wiki 證據：這兩個條件機率不一樣；不能把 P(A\mid B) 和 P(B\mid A) 對調。這些比率由講義的交叉表計算，而非講義明示為同一個指標。（[S03, PDF p.18] [S03, PDF p.20]；`wiki/entries/probability-and-random-variables.md`）

## 08. 隨機變數與期望值
- 教學定位：用數值整理不確定的結果
- Wiki 證據：隨機變數（random variable, RV）是把隨機實驗的可能結果映射成數值的規則。例如講義中顧客可能購買 iPhone+AirPods、只買 iPhone 或什麼都不買，對應收入 X=970,800,0，機率分別是 0.6,0.3,0.1。（[S03, PDF p.24] [S03, PDF p.25]；`wiki/entries/probability-and-random-variables.md`）
- Wiki 證據：因此講義收入期望值是：970(0.6)+800(0.3)+0(0.1)=822。期望值不一定是一筆真實會發生的交易，而是重複過程的機率加權中心。（[S03, PDF p.26]；`wiki/entries/probability-and-random-variables.md`）

## 09. 看懂常態分配
- 教學定位：用 Z 分數比較不同尺度的資料
- Wiki 證據：Z 的意思是：觀察值距離均值幾個標準差。大於 0 代表高於平均；小於 0 代表低於平均。（[S04, PDF p.12]；`wiki/entries/random-variable-distributions.md`）
- Wiki 證據：68–95–99.7 法則：常態分配約 68%、95%、99.7% 的觀察值，分別落在均值正負 1、2、3 個 SD 範圍內。這是常態分配的近似性質，不可直接套在任何偏態分布。（[S04, PDF p.22]；`wiki/entries/random-variable-distributions.md`）

## 10. 從樣本推到母體
- 教學定位：信賴區間代表估計的不確定性
- Wiki 證據：點估計只給一個值；信賴區間（CI）給一段可能涵蓋未知母體參數的範圍。（[S05, PDF p.21] [S05, PDF p.23]；`wiki/entries/inference-estimation.md`）
- Wiki 證據：95% 的正確解讀：在同樣抽樣方式下反覆抽樣、每次用同一程序建立信賴區間，大約 95% 的區間會包含固定的母體參數。不是說某次已經算好的區間「母體參數有 95% 機率在裡面」。（[S05, PDF p.22]；`wiki/entries/inference-estimation.md`）

## 11. 如何檢驗一個主張？
- 教學定位：假設檢定與 p 值的直覺
- Wiki 證據：若有關於母體的主張，統計檢定先假定零假設（null hypothesis） H_0 成立，再問：「如果 H_0 真的正確，取得目前這麼極端的數據有多不尋常？」若很不尋常，就考慮拒絕 H_0。老師借用「無罪推定」幫助理解：不能證明有罪，不等於證明無罪；同樣地，不拒絕 H_0 不等於證明 H_0 為真。（[S06, PDF p.5] [S06, PDF p.6]；`wiki/entries/inference-hypothesis-testing.md`）
- Wiki 證據：p 值（p-value）是在 H₀ 為真的前提下，取得「至少與目前一樣極端」的觀察結果的機率。（[S06, PDF p.20]；`wiki/entries/inference-hypothesis-testing.md`）

## 12. 重點回顧
- 教學定位：資料 → 抽樣 → 描述 → 機率 → 推論
- Wiki 證據：母體（population）是研究欲推論的所有對象；樣本（sample）是實際取得資料的一部分。若要知道某校學生平均完成學位所需時間，觀察到兩名延畢學生的故事，不足以支持整體平均很高。這是把零星個案誤認為代表性資料的問題。（[S01, PDF p.12]；`wiki/entries/data-and-sampling.md`）
- Wiki 證據：p 值（p-value）是在 H₀ 為真的前提下，取得「至少與目前一樣極端」的觀察結果的機率。（[S06, PDF p.20]；`wiki/entries/inference-hypothesis-testing.md`）

