# FitForm Atlas — v1.0 驗收紀錄

日期：2026-11-10

## 執行環境與測試方式
- Python 3 + 標準函式庫；Node.js 22 的 `--check`；Playwright + Chromium。
- 本執行環境阻擋 Chromium 對 URL 進行直接導覽（`ERR_BLOCKED_BY_ADMINISTRATOR`）。為避免誤稱真實瀏覽器端到端測試成功，改以以下方式拆開驗證：
  1. 啟動本機 Python HTTP server，使用 Python `urllib` 真正存取 `http://127.0.0.1:<port>/fitform-atlas/...` 下的八種檔案，確認狀態 200。
  2. 將**實際 HTML、CSS、JS 原始碼**注入 Chromium，將 `fetch` 以原始 `data/exercises.json` 回應模擬，進行互動、DOM 及 RWD 排版測試；SVG 插畫也從原始檔轉為 data URL 注入。
  3. 因瀏覽器限制，尚未能在本環境完成「瀏覽器直接連結至 HTTP server，並透過真實 fetch 請求 JSON」的完整端到端測試。
- GitHub Pages 正式部署和公開網址存取**尚未執行**。

## 測試結果
| 編號 | 測試項目 | 實測狀態 | 說明 |
|---|---|---|---|
| T01 | 首頁載入 | 通過（分拆測試） | HTTP 檔案 200；Chromium 注入後顯示 4 卡片 |
| T02 | 原始資料 | 通過 | 4 動作／4 分類，正式 JSON validator PASS |
| T03 | 關鍵字搜尋 | 通過 | `bench` 命中臥推；無結果提示、重置正常 |
| T04 | 分類篩選 | 通過 | 背部分類只顯示滑輪下拉 |
| T05 | 詳細頁 | 通過 | 同一模板依 id 顯示 3 步驟、2 錯誤、來源 |
| T06 | 未知 id | 通過 | 顯示「找不到這個動作」與返回連結 |
| T07 | RWD | 通過（Chromium DOM） | 320、390、768、1440px，首頁與詳細頁均無水平溢出 |
| T08a | 資料擴充模擬 | 通過 | 在隔離測試資料增加第 5 筆，驗證器成功，卡片、搜尋與詳細頁正常 |
| T08b | 全新 AI 對話遵循 AGENTS | 待驗 | 需實際於新對話執行並保存修改紀錄 |
| T09 | 基本回歸 | 通過（模擬） | 未修改既有頁面模板，原始 4 筆資料仍有效 |
| T10 | 正式公開網站 | 待驗 | GitHub Repository 建立、Pages 發布及外部實測尚未完成 |

## 自動化指令

```bash
python tests/validate_content.py
python -m unittest discover -s tests -p 'test_validator.py' -v
python tests/browser_smoke.py
node --check js/common.js
node --check js/app.js
node --check js/exercise.js
```

`browser_smoke.py` 需要 Playwright、Chromium；不影響網站本身運作。

## 結果摘要
- JSON 驗證：PASS（四筆、四類）。
- Validator 負面案例：7 項單元測試通過。
- JS 語法檢查：3 檔通過。
- HTTP 子路徑檔案：8 個路徑均回傳 200。
- Chromium：搜尋、篩選、詳細頁、錯誤頁、4 種寬度、資料擴充模擬均通過。
- 已知未完成：真實 HTTP browser E2E、全新 Agent 的操作實驗、GitHub Pages 正式部署。

## 截圖
- `docs/screenshots/desktop.png`：桌機首頁（Chromium DOM 模擬內容載入）。
- `docs/screenshots/mobile-home.png`：390px 首頁；`docs/screenshots/mobile.png`：390px 動作詳細頁（Chromium DOM 模擬內容載入）。

## 發布後建議人工實測
1. 從 GitHub Pages 公開 URL 開啟首頁，確定沒有 JSON `fetch`、CSS、SVG 404。
2. 搜尋中文「臥推」與英文 `bench`，確認結果。
3. 分類按鈕與詳細頁導覽正常，手機也可點擊。
4. 用全新 AI 開發對話先讀 `AGENTS.md`，新增一筆完整動作（附 SVG 與參考來源）。
5. 保留 Git commit diff 與修改前／後截圖，作為「可以重複擴充」的作業證據。
