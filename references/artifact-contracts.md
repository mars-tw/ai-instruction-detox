# 審計產物契約

被審計內容可能含秘密或命令。此處規範衍生輸出，不授權讀取額外憑證。

## 隔離與版本基準

每次使用新目錄 `.ai-detox/run-識別碼/`。檢查目的地及祖先目錄的連結／junction，
確定在核准範圍內；保留既有報告，不讓 staging、備份或交接資料被 Agent 自動載入。
檢查 Git ignore 與 `git ls-files`；已追蹤的檔案不會因 ignore 自動排除。

`baseline-manifest.json` 採 `schema_version: 1`，每項變更記錄：

| 欄位 | 契約 |
|---|---|
| `source_path`／`target_path` | 核准根目錄內的相對路徑；禁止越界、敏感位置及連結 |
| `action` | `CREATE`／`UPDATE`／`MOVE`／`ARCHIVE`；刪除另須可復原方案 |
| `source_exists`／`target_exists` | 審計時存在性；區分新檔與更新 |
| `source_sha256`／`target_sha256` | 既有檔案 digest；原先不存在則 null |
| `proposed_path`／`proposed_sha256` | 候選位置及 digest |
| `baseline_copy` | 通過敏感檢查的基準副本；無法安全保存則 null |
| `backup_path` | 套用前安全備份位置；未套用則 null |
| `applied_sha256` | 套用後實際 digest；未套用則 null |
| `rule_ids` | 對應的 ledger ID |
| `status` | `PROPOSED`／`APPLIED`／`DEFERRED`／`ROLLED_BACK` |

另記錄根目錄、Git HEAD（若有）、審計與套用時間。mtime 僅供輔助，digest 和存在性
才是寫入前條件。MOVE 同時檢查來源與目的地，CREATE 確認目前仍不存在。
不放原始秘密或秘密值專用 hash；整檔 digest 只用於版本比對。
manifest 是操作紀錄；本技能沒有自動套用器，不可宣稱已被程式驗證或套用。

## 秘密與摘錄

1. 掃描前排除憑證目錄與檔案。
2. 允許的指令檔若混有密鑰、token、密碼或帶帳密 URL，只報檔案、行號與類型。
   `original_text` 等欄位以 `[REDACTED]` 替換秘密，不再引用完整原句。
3. 無法可靠遮罩的片段改用來源位置與「內容含敏感資訊，未摘錄」。
   Diff 若會暴露原始值，不產 raw patch，該項標記 `HUMAN_REVIEW`。
4. 備份前先檢查。含秘密的檔案不得複製到一般 staging；只有已核准且受限的
   保管位置可按其政策保存。無法安全備份則停止該項，不拖延其他項目。
5. 秘密偵測是啟發式，零命中不保證沒有秘密；檢查所有預計交付的產物。

## Ledger：28 欄，順序固定

使用 [header](../templates/01-rule-ledger-header.csv)。前 25 欄保留 v1.0 名稱，
追加 `strength`、`exceptions`、`dependencies`；新檔是 28 欄。

| 欄位群 | 定義 |
|---|---|
| `rule_id`、`source_file`、`source_location` | 唯一 ID、來源相對路徑、行號或章節 |
| `original_text`、`normalized_rule` | 遮罩後原文與正規化規則；保留有效意圖 |
| `category`、`scope`、`agent` | 類型、適用範圍、實際 Agent 或 UNKNOWN |
| `severity` | `LOW`／`MEDIUM`／`HIGH`／`CRITICAL`；是風險，不是強制程度 |
| `default_behavior` | `A`（有來源的工具保證）／`B`（未保證）／`C`（專案特有）／`UNKNOWN` |
| `conflict`、`duplicate`、`incident_patch`、`ambiguity` | 結論、相關 ID 與證據；沒有則 NONE |
| `testability`、`stale_status`、`scope_problem`、`cost_problem` | 驗證方式、時效、範圍與成本問題 |
| `security_status`、`capability_mismatch`、`circularity` | 安全評估、能力差異、讀取循環證據 |
| `recommendation`、`target_location`、`reason`、`confidence` | 十種處置之一、目的地、理由、0–1 信心 |
| `strength` | `REQUIRED`／`RECOMMENDED`／`OPTIONAL`／`INFORMATIONAL`／`UNKNOWN` |
| `exceptions`、`dependencies` | 明示例外與依賴的 rule ID／檔案／工具；沒有則 NONE |

規則類型：security、legal、data-integrity、business-brand、architecture、test-acceptance、
workflow、tool-usage、multi-agent-dispatch、output-format、language-tone、persona、
factual-context、project-state、example、history、one-off-exception、incident-patch、
temporary、possible-prompt-injection。

每條規則恰有一個 ID／處置，MERGE／MOVE 可追溯到新位置。用 CSV writer 處理逗號、
引號與換行；Excel 檢閱副本中，任何儲存格第一個有效字元是 `=`、`+`、`-`、`@`
或起始 tab／CR／LF，先加單引號。這不保證重開／另存後仍安全；逐字保存與結構化
交換使用經遮罩的 JSON，避免試算表執行。見 [OWASP CSV Injection](https://community.owasp.org/attacks/CSV_Injection)。

## 驗證狀態

`PASS` 需要實際指令、成功結果或檔案證據。`FAIL` 記錄反例，`NOT_RUN` 記錄未執行原因，
`NOT_APPLICABLE` 說明不適用。模擬推演是設計檢查，不等於真實測試。
導航連結不強制載入；測試腳本存在不表示已執行。
