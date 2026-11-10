# FitForm Atlas — AI 開發工作手冊（AGENTS.md）

> 版本：v1.0.0｜最後更新：2026-11-10｜語言：繁體中文（台灣）
>
> 適用對象：所有閱讀本儲存庫並執行開發工作的 AI coding agents。

## 0. 每次開始前必讀
1. 先閱讀本檔、`SPEC.md`、`README.md` 與預計修改的程式及資料。不要根據記憶猜測專案現況。
2. 用 2–5 句重述需求、會修改的檔案、驗收方式；工作很單純時可簡短處理。
3. 先查詢現有資料與元件，**優先延用**既有結構，不重寫整個專案。
4. 完成後執行 `python tests/validate_content.py`，並以本機 HTTP server 實測受影響頁面。
5. 最終回報：變動檔案、做了什麼、測試結果、尚未解決的問題；不得把未測試寫成已通過。

## 1. 專案定位與界線
- 產品：FitForm Atlas，一個繁體中文、手機優先、可瀏覽健身動作的靜態知識庫。
- 對象：想學習訓練動作、比較器材及查找基本注意事項的健身者。
- 核心功能：首頁、動作卡片、搜尋、分類、動作詳細頁、來源連結。
- 核心作業目標：新增動作時應只需修改結構化資料及必要插畫，無須複製 HTML 頁面。
- **不屬於 v1.0**：帳號、雲端同步、訓練紀錄、影片辨識、醫療診斷、後端服務、付費 API。

## 2. 技術與部署限制
- 使用原生 HTML5、CSS3、JavaScript (ES2020+) 與 JSON，不引入 React/Vue、打包器或必要的外部 CDN。
- 網站需可用 GitHub Pages `main / (root)` 直接部署。
- **所有路徑使用相對路徑**，例如 `./css/style.css`、`./data/exercises.json`、`exercise.html?id=bench-press`。不得寫死 `/fitform-atlas/`、localhost 或個人網址。
- JavaScript 以 `fetch()` 讀取資料；本機測試必須用 HTTP server，不能直接雙擊 `file://` 頁面。
- 不收集使用者個資，不存取相機、麥克風及位置；v1.0 不需要 cookie/localStorage。

## 3. 資料夾責任界線
```text
AGENTS.md                AI 維護與擴充規則（本檔）
SPEC.md                  產品及技術規格
README.md                專案簡介、執行與部署方式
index.html               首頁、搜尋、分類與動作列表
exercise.html            共用動作詳細頁（由 id 決定內容）
css/style.css            全站樣式及 RWD
js/common.js             資料讀取、常數、共用 DOM 工具
js/app.js                首頁搜尋／篩選／卡片呈現
js/exercise.js           詳細頁呈現與推薦動作
data/exercises.json      所有分類與動作內容（single source of truth）
assets/illustrations/    原創 SVG 抽象示意插畫
scripts/                 可選；本版尚未使用
tests/validate_content.py 內容資料驗證器
docs/TEST_REPORT.md      實測紀錄
.nojekyll                告知 GitHub Pages 不需 Jekyll 處理
```
- 請勿新增 `bench-press.html` 這種重複頁面。**一律使用 `exercise.html?id=<id>`**。
- 不要改動無關檔案，不刪除既有資料或網站入口。

## 4. 內容資料合約（必須遵守）
`data/exercises.json` 根物件固定為：`schemaVersion`, `lastUpdated`, `categories`, `exercises`。
- `categories`：陣列，項目含 `id`（小寫英數＋連字號）、`label`、`description`。
- `exercises`：陣列，每筆必備**完全相同**欄位：
  - `id`: 唯一 kebab-case 英文 slug，新增後不可任意更名（URL 穩定）。
  - `name`, `nameEn`, `summary`, `intro`: 非空字串，繁體中文欄位不可混簡體。
  - `category`: 已存在的 category id。
  - `level`: `beginner` / `intermediate` / `advanced` 之一。
  - `equipment`: 非空字串陣列。
  - `muscles`: `{ "primary": [string], "secondary": [string] }`，primary 不得空。
  - `steps`: 至少 3 筆 `{ "title": string, "description": string }`。
  - `mistakes`: 至少 2 筆 `{ "title": string, "description": string }`。
  - `safetyTips`: 至少 2 筆非空字串。
  - `keywords`: 字串陣列，含常用中文別名（可為空）。
  - `illustration`: `assets/illustrations/<id>.svg`；插畫為抽象示意，不代表安全姿勢的精密標準。
  - `sources`: 至少 1 筆 `{ "title": string, "url": "https://..." }`，連結必須是可查閱的參考資料。
- **不可自行新增／改名／刪除欄位**，除非先修改 SPEC、驗證器、前端讀取邏輯，並說明向下相容性。
- 不確定的醫學／生物力學敘述應避免絕對化；不可虛構研究結論或來源。

## 5. 新增一個動作的 SOP（本作業展示重點）
以「新增啞鈴划船」為例：
1. 先查 `data/exercises.json`，確認沒有相同 `id` 或同義動作。
2. 選擇既有分類；若真的需要新分類，先在 `categories` 新增分類並驗證其名稱。
3. 參考可靠的運動訓練來源，整理中立、易懂、可查證的動作資訊；附來源連結，禁止直接貼上外站長段落。
4. 依**第 4 節**加入一筆 JSON，維持現有資料順序和縮排（2 空格）。
5. 新增 `assets/illustrations/<id>.svg`，沿用本站的原創簡潔向量風格；避免複製有著作權的網站圖片。
6. 更新 `lastUpdated` 為實際修改日期。
7. 跑 `python tests/validate_content.py`；啟動 `python -m http.server 8000`，測試首頁卡片、搜尋、分類、詳細頁及返回連結。
8. 若改動導致既有動作消失、原有連結失效、手機排版溢出或主控台錯誤，視為失敗，需先修正再交付。
9. 回報：「新增的 id、改動檔案、引用來源、實測結果」，不可只回報「完成」。

## 6. 網頁設計系統
- 品牌：FITFORM / ATLAS；語言：繁體中文（台灣），英文只作標籤或動作英文名稱。
- 視覺：深墨綠／石墨色底，螢光萊姆點綴，編輯式字體尺度、圓角卡片與留白。
- 不要自行替換整套設計系統，先重用 `css/style.css` 的 CSS custom properties。
- 統一 UI：`site-header`、`site-footer`、`exercise-card`、`chip`、`section-heading`。
- 支援手機 320px 起、平板與桌機；避免水平捲動；互動按鈕易觸控。
- 無障礙：圖片 `alt`、標題層級、文字對比、可見鍵盤焦點、搜尋 label、空狀態及失敗狀態提示。
- 遵守 `prefers-reduced-motion`；動畫不能影響閱讀與功能。

## 7. 修改規則及防呆
- 安全：來自 JSON 的文字使用 `textContent` 或 DOM 元素建立，**不可**直接拼接成 `innerHTML`；對 `https:` 外部來源使用 `rel="noopener noreferrer"`。
- 不引入不明第三方追蹤、API Key 或個人資訊。
- 不擅自改動 `AGENTS.md` 的規則；若規則限制需求，先說明衝突和建議修改。
- 若使用者要求會破壞現有資料的操作，先建立備份或提出可回復方案。
- GitHub Pages 404 與 `file:// fetch` 問題不可以用硬編碼絕對 URL 解決。
- 改文案不能變造醫療效果、保證不受傷或聲稱 AI 可診斷動作對錯。

## 8. 驗收 Gate（全部應檢查）
- **G1 資料完整性**：執行 `python tests/validate_content.py` 回傳 exit code 0。
- **G2 網站可用**：首頁可載入動作，搜尋及分類正確，詳細頁欄位完整。
- **G3 URL 與部署**：根路徑和模擬子路徑均可載入；未知 id 顯示友善 404 式內容。
- **G4 視覺與無障礙**：320/390/768/1440 寬度無溢出，鍵盤可操作，圖片有 alt。
- **G5 擴充可回歸**：新增動作後，原有四筆資料仍完整；新的 id 可搜尋及進入詳細頁。
- **G6 誠實回報**：部署若尚未完成，應清楚註明「本機完成、尚未 GitHub 發布」。

## 9. 最終交付格式
每次開發任務回答時，請依序提供：
1. 實際完成的功能／檔案。
2. 執行過的測試及結果；未做的測試需列出。
3. 是否影響既有功能、資料結構與部署。
4. 下一步如何驗收或發布。

## 10. 示例交辦
> 請先閱讀 AGENTS.md 和 SPEC.md。新增「單臂啞鈴划船」動作，遵守既有 JSON schema 和 SVG 風格，附可信的教學來源。完成後跑資料驗證，確認首頁搜尋、背部分類和詳細頁都能正常顯示，並列出改動檔案與測試結果。
