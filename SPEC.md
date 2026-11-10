# FitForm Atlas｜正式專案規格書 v1.0

- 專案名稱：FitForm Atlas 健身動作知識庫
- 專案類型：AI Agent 專案規則與可擴充靜態網站
- 版本：v1.0.0
- 日期：2026-11-10
- 語言：繁體中文（台灣）
- 預期部署：GitHub Pages

## 1. 背景、問題及目標

健身動作的訓練部位、操作步驟與錯誤提醒常分散於不同來源，不利於快速查找。本專案將資料轉成統一的動作卡片與教學頁，同時以 `AGENTS.md` 建立可重複使用的 AI 開發流程。

### 成功定義
1. 使用者能從首頁搜尋／分類找到動作，並在詳細頁閱讀步驟、錯誤與注意事項。
2. AI 能先讀 `AGENTS.md`，只新增資料與示意 SVG 即讓新動作出現在網站，而不重複建 HTML。
3. 全站可在 GitHub Pages 靜態託管，手機與電腦皆可使用。

## 2. 對象及使用情境
- 健身初學者：閱讀清楚、不過度承諾的操作說明。
- 有經驗的訓練者：快速查閱器材、肌群、提示。
- 維護者／AI Agent：以統一 schema 新增、修改內容。

## 3. 範圍
### P0（本次必做）
- 首頁英雄區、知識庫區塊、動作卡片。
- 4 個完整示範動作：槓鈴臥推、滑輪下拉、高腳杯深蹲、啞鈴肩推。
- 中文關鍵字搜尋；分類按鈕篩選；結果數量及空狀態。
- `exercise.html?id=<slug>` 共用動作頁：主要／次要肌群、器材、步驟、常見錯誤、安全提醒、參考來源。
- 清晰的 404 式未知動作提示；資料載入失敗回饋。
- AGENTS.md、README.md、資料驗證器、GitHub Pages 相對路徑。

### P1（可選，視時間）
- 動作難度篩選、進階搜尋、標籤化收藏、深色／淺色切換。

### 不包含
- 使用者註冊、個人健身紀錄、AI 動作評分、影片上傳、付費 API、運動處方與醫療診斷。

## 4. 資訊架構與頁面

### `index.html`
- Header：品牌、知識庫錨點、專案介紹。
- Hero：品牌口號、特色摘要、CTA。
- Category：依 `categories` 自動建立分類選項。
- Library：搜尋欄、動作數、可篩選卡片、無結果狀態。
- Process：告訴訪客網站由統一資料模型維護，展示可擴充特色。
- Footer：免責聲明、外部教學參考連結。

### `exercise.html?id=<id>`
- Header / Breadcrumb 返回知識庫。
- 動作標題（中英）、分類、難度、摘要、示意插畫。
- 器材、主要與次要肌群。
- 分步教學、常見錯誤、安全提醒。
- 參考來源外部連結，以及其他動作連結。
- 不存在的 id 顯示友善錯誤與返回按鈕。

## 5. 視覺設計
- 風格：premium fitness editorial、暗色、乾淨、高對比。
- 背景深色，螢光萊姆色 `#c7fa71` 作主要 CTA，暖灰與淡白作文字。
- 版心最大寬度約 1180px；卡片在桌機 3 欄、平板 2 欄、手機 1 欄。
- 版面斷點：<= 900px、<= 650px；手機最小 320px。
- 使用系統中文字型、無強制外部字型請求；純 SVG 原創插畫；保留明確 hover/focus。

## 6. 資料模型
資料唯一來源 `data/exercises.json`：

```json
{
  "schemaVersion": "1.0.0",
  "lastUpdated": "2026-11-10",
  "categories": [
    {"id":"chest","label":"胸部","description":"胸推與胸肌訓練"}
  ],
  "exercises": [
    {
      "id": "bench-press",
      "name": "槓鈴臥推",
      "nameEn": "Barbell Bench Press",
      "category": "chest",
      "level": "intermediate",
      "summary": "...",
      "intro": "...",
      "equipment": ["槓鈴", "臥推椅", "安全架"],
      "muscles": {"primary": ["胸大肌"], "secondary": ["肱三頭肌", "前三角肌"]},
      "steps": [{"title": "準備姿勢", "description": "..."}],
      "mistakes": [{"title": "...", "description": "..."}],
      "safetyTips": ["..."],
      "keywords": ["bench"],
      "illustration": "assets/illustrations/bench-press.svg",
      "sources": [{"title": "ACE Exercise Library", "url": "https://www.acefitness.org/resources/everyone/exercise-library/"}]
    }
  ]
}
```

上例為欄位形狀示意；**正式資料必須符合 AGENTS.md 的最低數量要求**：steps 至少 3 筆、mistakes 至少 2 筆、安全提醒至少 2 筆。

## 7. 功能規格與邊界情境
| 編號 | 需求 | 行為及成功條件 |
|---|---|---|
| F01 | 載入資料 | 網頁以相對路徑讀取 JSON；錯誤顯示可見提示 |
| F02 | 動作卡片 | 顯示中英文名、分類、難度、器材、摘要 |
| F03 | 搜尋 | 不分大小寫；可搜尋名稱、英文、肌群、器材、keywords |
| F04 | 分類 | 點擊後更新列表與數量；「全部」恢復完整清單 |
| F05 | 詳細頁 | 以 `id` 找到唯一動作並完整呈現欄位 |
| F06 | 未知 ID | 顯示友善資訊及返回首頁連結，不顯示空白頁 |
| F07 | RWD | 320 / 390 / 768 / 1440px 不出現水平溢出 |
| F08 | 內容新增 | 加入單筆 JSON + SVG 無需改 HTML 或 CSS |
| F09 | 外部連結 | 有 `target="_blank"` 和安全 `rel`，文字來源可信 |
| F10 | 資料檢查 | Python validator 可發現缺欄、重複 id、錯分類或錯插畫路徑 |

## 8. AI 開發工作流程
讀 `AGENTS.md` → 確認既有 schema → 整理可信來源 → 加資料及 SVG → 跑驗證器 → 用 HTTP server 進行瀏覽器測試 → 回報修改與問題。

### 擴充演示
在不同的開發對話交辦：「新增單臂啞鈴划船」。AI 應依 `AGENTS.md` 找到資料位置、建立 JSON 及 SVG，不增加新頁面。新增前後比對資料筆數（4→5）、檢查搜尋／分類／詳細頁，並紀錄提交差異。

## 9. 驗收測試
| ID | 測試條件 | 預期結果 |
|---|---|---|
| T01 | 首頁由 HTTP server 載入 | 英雄區與卡片完整呈現 |
| T02 | 初始資料 | 4 筆有效資料、類別與欄位正確 |
| T03 | 搜尋「臥推」及「bench」 | 只出現槓鈴臥推 |
| T04 | 選「背部」 | 只出現滑輪下拉 |
| T05 | 點任一卡片 | 同一詳細頁依 id 呈現不同內容 |
| T06 | 輸入不存在的 id | 有錯誤提示及返回首頁連結 |
| T07 | 模擬手機版 320/390px | 不水平溢出、主要功能可用 |
| T08 | 新增第 5 筆動作 | 不複製 HTML，通過驗證並正常顯示 |
| T09 | 原有動作回歸測試 | 舊有 4 個 id 仍可進入 |
| T10 | GitHub Pages 正式網址 | 公開頁面可正常載入資源與導覽 |

## 10. 交付物
`AGENTS.md`、`SPEC.md`、`README.md`、網站程式與素材、資料 JSON、驗證器、測試紀錄、GitHub Repository URL、GitHub Pages URL（需發布後補上）。

## 11. 風險與改善
- **運動內容不應被當成個人化醫療建議**：提供安全提醒與可追溯來源。
- **示意圖非精密姿勢教學**：不以 SVG 評分動作正確與否。
- **網路來源可能更新**：新內容需複查引用網址、避免原文照抄。
- **GitHub Pages 是靜態主機**：無登入及後端功能；JSON 使用 fetch，需 HTTP server。
- **部署尚未完成前不能宣稱 T10 通過**：須實際開啟公開連結驗收。
