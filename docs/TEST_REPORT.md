# FitForm Atlas — v1.0 驗收紀錄

日期：2026-11-10

## 單臂啞鈴划船新增驗收（2026-11-10）

本節為本次實測；下方原始 v1.0 紀錄保留為歷史結果，不代表本次全部重跑通過。

- 基準：`ee2afb83e976fbce9379b73517f8c5f0db3d361d`（main）。
- 新增 id：`one-arm-dumbbell-row`，既有 `back` 分類、中階；資料由 4 筆增加為 5 筆，分類仍為 4 個。
- `lastUpdated` 維持實際修改日期 `2026-11-10`，與當日原值相同。
- 逐筆比較：原有四筆動作內容、順序、categories 與 schemaVersion 完全相同；HTML、CSS、前端 JS、AGENTS.md、SPEC.md 均未修改。
- 修改檔案：`data/exercises.json`、新增 `assets/illustrations/one-arm-dumbbell-row.svg`、`README.md`、`tests/browser_smoke.py`、本報告。
- 教學來源已實際查閱：
  - [ACE Single-arm Row](https://www.acefitness.org/resources/everyone/exercise-library/126/single-arm-row/)：椅面支撐、步驟、呼吸與避免軀幹旋轉；難度依該頁標示為 intermediate。
  - [PureGym Single Arm Dumbbell Rows](https://www.puregym.com/exercises/back/rows/single-arm-dumbbell-row/)：肌群、支撐位置、拉向腰側與控制下放。文字重新整理，SVG 自行繪製，未複製來源圖片。

| 檢查 | 本次結果 | 範圍與限制 |
|---|---|---|
| 正式資料驗證 | PASS，exit 0 | `python tests/validate_content.py`：5 筆、4 類，欄位及資產路徑合約正確；驗證器不會驗證外站內容真偽 |
| 驗證器回歸 | PASS，7/7 | `python -m unittest discover -s tests -p 'test_validator.py' -v` |
| 原有資料與架構 | PASS | 對照基準，原有四筆資料、分類與前端檔案均保留 |
| JS 語法 | PASS，3/3 | `node --check`：common.js、app.js、exercise.js |
| Python 測試語法 | PASS | `python -m py_compile tests/browser_smoke.py` |
| 本機 HTTP 根路徑與子路徑 | PASS，16/16 | Python HTTP server + urllib：首頁、帶新 id 的詳細頁、CSS、三個 JS、JSON、划船 SVG，兩種路徑均 200 且內容非空 |
| SVG 解析與外觀 | PASS | XML 解析；Sharp 將原始 SVG 渲染為 PNG 並目視檢查，沿用 448 viewBox、墨綠底、格線、萊姆色器材與簡潔人物；不代表姿勢專業認證 |
| 本機瀏覽器功能與 RWD | BLOCKED | 已嘗試 `python tests/browser_smoke.py`；HTTP 部分成功，Chromium 啟動失敗，未執行 DOM/互動斷言 |
| GitHub Pages 新動作實測 | 待驗 | 提交後確認自動部署及公開頁面 |

本機瀏覽器限制：Playwright 預設 Chromium 未安裝；既有系統 Chromium fallback 因 `socket() failed: Operation not permitted` 無法啟動。另嘗試使用可用的雲端瀏覽器連線本機 HTTP，該環境無法存取本機站點。因此不將新增搜尋、背部分類、詳細頁點擊、返回連結、鍵盤、320/390/768/1440px 排版或 console 寫為本機通過。

`tests/browser_smoke.py` 已移除固定四筆的總數假設，加入新動作中文／別名／英文搜尋、分類交集、各欄位、來源安全屬性、SVG、原有 id 與新詳細頁 RWD 斷言。這些瀏覽器斷言目前僅完成語法檢查，需在可啟動 Chromium 的環境重跑；網站本身仍無新增依賴。可獨立重跑本機 HTTP 部分：

```bash
python -c "import sys; sys.path.insert(0, 'tests'); from browser_smoke import check_http_assets; check_http_assets()"
```

## 原始 v1.0 驗收（歷史紀錄）

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
