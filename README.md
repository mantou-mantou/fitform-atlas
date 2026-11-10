# FITFORM ATLAS｜健身動作知識庫

使用繁體中文的靜態健身動作知識網站，支援動作列表、關鍵字搜尋、分類篩選及詳細教學。此專案的另一個重點是利用 [`AGENTS.md`](./AGENTS.md) 定義可重複使用的 AI 網站開發規則。

## 現有內容
- 4 個示範動作：槓鈴臥推、滑輪下拉、高腳杯深蹲、啞鈴肩推。
- 首頁搜尋與分類、獨立動作詳細頁、來源、注意事項。
- 原生 HTML/CSS/JS/JSON，無付費 API、免建置。
- 可擴充內容資料格式、原創 SVG 示意圖、Python validator。

## 本機執行
1. 安裝 Python 3。
2. 在專案根目錄執行：

```bash
python -m http.server 8000
```

3. 瀏覽 `http://localhost:8000/`。
4. **不要直接以 `file://` 開啟**，瀏覽器可能禁止本地 `fetch()` 讀取 JSON。

## 資料驗證

```bash
python tests/validate_content.py
```

## 新增動作
1. 先閱讀 `AGENTS.md` 的第 4 與 5 節。
2. 在 `data/exercises.json` 新增符合 schema 的資料，放進既有 category。
3. 在 `assets/illustrations/` 新增相同 id 的 SVG。
4. 跑資料驗證；確認首頁、搜尋、分類和 `exercise.html?id=<id>`。
5. 不需要額外複製 HTML 頁面。

## GitHub Pages 部署
1. 在自己的 GitHub 建立新公開儲存庫（建議名稱 `fitform-atlas`）。
2. **將本專案根目錄內的檔案**上傳到 Repository 根目錄，確保 `index.html` 在根目錄，避免多一層 `fitform-atlas/fitform-atlas/`。
3. 前往 Repository `Settings → Pages → Build and deployment`。
4. `Source` 選 `Deploy from a branch`，`Branch` 選 `main`，資料夾選 `/(root)`，儲存。
5. 等 GitHub Pages 建置完成，實際開啟公開網址驗證首頁與詳細頁。

> 本專案使用相對路徑，可部署於 `https://<username>.github.io/<repo>/` 等專案子路徑。
> GitHub 官方說明：[建立 Pages 網站](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)。

## 主要檔案
| 路徑 | 用途 |
|---|---|
| `AGENTS.md` | AI 工作手冊，規定新增、修改、驗收方式 |
| `SPEC.md` | v1.0 規格書、資料結構與測試案例 |
| `data/exercises.json` | 動作內容唯一來源 |
| `index.html` | 網站首頁與動作列表 |
| `exercise.html` | 所有動作共用詳細頁 |
| `tests/validate_content.py` | 資料及資產驗證 |
| `docs/TEST_REPORT.md` | 已執行測試及待驗項目 |

## 注意事項
本站是一般運動知識整理，不提供醫療診斷或個人化運動處方；示意 SVG 僅為視覺輔助，無法保證姿勢正確。遇到疼痛、既有傷勢或無把握的技術動作，應請合格教練或醫療專業人員協助。

內容參考 [ACE Exercise Library](https://www.acefitness.org/resources/everyone/exercise-library/) 與 [NSCA](https://www.nsca.com/education/articles/ptq/time-efficient-training/)，文本為重新整理的概述，不直接複製圖文。
