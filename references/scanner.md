# 掃描器契約

`scripts/detox-scan.py` 使用 Python 3.8 相容語法及標準函式庫，不安裝套件、不執行來源內容、
不讀取引用目標內容。實際已驗證的 Python／平台版本見本次更新報告。

## 使用

```powershell
python scripts/detox-scan.py --root .
python scripts/detox-scan.py --files SKILL.md references/apply-phase.md
python scripts/detox-scan.py --root . --json scan-new.json
python scripts/detox-scan.py --root . --max-depth 8 --max-bytes 2097152
```

`--root` 與 `--files` 必選其一，不能同時使用。不允許以家目錄或檔案系統根目錄
做遞迴掃描。明確檔案清單也會拒絕敏感位置、連結與非一般檔案。
`--json` 只能建立新檔，父目錄須存在，不能覆寫來源、舊報告或連結。

預設深度 6（根為 0）、單檔 1 MiB、最多 5,000 檔、總讀取量 64 MiB。
UTF-8／UTF-8 BOM 可讀；錯誤編碼、不存在、無法讀取、變動中的檔案、深度及大小截斷
會記錄 coverage error，不能當作已掃描。

| 退出碼 | 意義 |
|---:|---|
| 0 | 選定範圍讀取完成，沒有風險樣式命中；不表示語意／安全全通過 |
| 1 | 有疑似秘密、注入、引用邊界、懸空、候選循環或跨檔重複 |
| 2 | CLI／範圍／輸出無效，或未找到可掃檔案 |
| 3 | 部分掃描；先處理缺口再判讀完整性 |

## 發現與限制

- 所有發現只含位置、分類及必要統計，不含來源摘錄、秘密值或原始引用字串。
- 支援具常見前綴的 key、GitHub fine-grained PAT、帶帳密 URL、私鑰標記與一般憑證賦值。
  無法保證辨識所有任意秘密，文件的防護範例或禁止語句也可能命中。
- 解析 Markdown／backtick／常見純文字檔案引用，忽略 URL 與純錨點。
  引用不能藉由 `..` 或連結越出掃描範圍；引用不會觸發新的內容讀取。
- 用有向圖的強連通元件找多節點、自指循環，提供每個元件的一條代表環，
  不是列出所有可能的環。導航返回連結與示例會命中，需判斷是否真正強制載入。
- 重複判斷使用整個正規化段落，不用截短的前綴，也不回傳段落內容。
- 檔案大小與 token 估計是掃描量，不代表宿主實際自動載入量。
- 自動盤點只涵蓋程式定義的入口名稱及規則目錄。README、工程設定、非支援格式、
  外部已安裝副本需按盤點清單另行補查；不能把自動清冊當全專案完整清冊。

## JSON 版本 2

`schema_version`、`files_selected`、`files_scanned`、`complete`、`errors`、`skipped`、`limits`、
`dangling_refs`、`boundary_refs`、`circular_refs`、`secrets`、`injections`、`vague_rules`、
`absolute_terms`、`duplicate_blocks`、`file_stats`。

`complete` 只表示設定範圍內的讀取成功；政策排除仍記在 `skipped`。
v1 的 `snippet`、`text`、raw `ref` 與兩節點 `pair` 不再輸出，消費報告的程式需更新。
循環改讀 `files` 與 `cycle`，重複改讀 `locations` 與 `characters`。

Python 呼叫介面保留 `find_files(root=None, explicit=None, max_depth=6)` 與
`scan(files, root=None, max_bytes=1048576)`；清冊是 list-compatible 的 `FileSelection`，
帶 `root`、`errors`、`skipped`。`read()` 失敗會拋出錯誤，不能再當成空檔案。

路徑安全檢查不是作業系統沙箱。執行時需避免其他程序惡意替換祖先目錄；
不要以本工具宣稱對並行路徑競爭有完整防護。
