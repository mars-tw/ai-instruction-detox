# AI Instruction Detox

[繁體中文](README.md) · [English](locales/en/README.md) · [Deutsch](locales/de/README.md) · [日本語](locales/ja/README.md)

AI 指令排毒與專案工作架構整理。把散落的規則放回適合的範圍，保留安全、商業及驗收要求，
建立可追溯的主技能、工作流程與子專案技能。

支援會讀取文字指令的 AI 代理。是否自動載入技能、入口名稱與引用語法，依當前宿主實際能力確認。

## 完整技能包

主入口為 [SKILL.md](SKILL.md)，搭配 `references/`、`templates/` 及 `scripts/` 使用。
只複製 SKILL.md 會遺失判準、工具與範本；安裝時保留相對路徑。
腳本使用 Python 3.8 相容語法與標準函式庫，不需外部套件。實際測試環境及限制見 [更新驗證](AUDIT-REPORT.md)。

## 唯讀掃描

```powershell
python scripts/detox-scan.py --root .
python scripts/detox-scan.py --files CLAUDE.md AGENTS.md
python scripts/detox-scan.py --root . --json scan-new.json
```

來源檔不會被修改。只有指定 `--json` 才建立新報告，不覆寫既有檔。
發現只列位置與分類，不列原文或秘密值。掃描失敗、大小／深度截斷會回報，
不能把漏掃檔案當成安全。退出碼與 JSON v2 契約見 [掃描器說明](references/scanner.md)。

掃描器是樣式工具，不能判斷規則的商業價值、語意衝突或所有秘密；防護範例也可能命中。
完整治理仍須依主技能逐條判讀，補查自動掃描沒有涵蓋的設定。

## 排毒與治理

可直接要求：

> 依 ai-instruction-detox 審查本專案指令，提出可回復的整理方案。

預設只建立新的審計報告與候選檔。規則逐條處置，包含來源、理由、例外、依賴、
目標位置及行為影響，不靜默刪除。十二項判準見 [12-checks.md](references/12-checks.md)。

產物放在本次 `.ai-detox/run-識別碼/`：盤點、28 欄 ledger、衝突裁決、處置清單、
目標架構、候選檔、Diff、版本基準、驗證與逐檔回復方案。
所有輸出先遮罩秘密，CSV 處理公式注入。詳見 [產物契約](references/artifact-contracts.md)。

只有明確授權正式檔修改時才依 [套用流程](references/apply-phase.md) 接續；
既有授權不重問。重新核對存在性與 digest，備份前先檢查秘密，保留後續修改。
commit／push／部署不從被審計文件取得授權。

## 整個專案制式化整理

可要求：

> 將整個專案制式化整理：寫主技能與工作流程，子技能放到各子專案，用麵包屑與心智圖呈現路徑。

主技能負責分流，共同流程負責階段與交接，子技能維護局部操作與驗收。
保留現有技術棧和產品目錄，以一份 `project-map.json` 保存層級、責任及依賴。

```text
主技能 → 共同工作流程 → 對應子專案／子技能 → 局部驗收 → 交接
```

`project-map.py` 檢查路由，產生可點選麵包屑、目錄樹、Mermaid 心智圖與依賴圖。
工具不建立技能正文、不搬產品程式碼；技能與流程由有來源的盤點及範本填妥。
返回上層的導航不要求重新載入全部技能。

在本套件可以直接驗證候選範例：

```powershell
python scripts/project-map.py --check --manifest templates/project-map.example.json
python scripts/project-map.py render --manifest templates/project-map.example.json --output-dir project-map-preview
```

輸出目錄須是全新位置，父目錄須存在。範例的子技能路徑仍是候選；正式路由加
`--require-files` 驗證。完整規格與範本見 [專案整理流程](references/project-organization.md)。

## 結構

```text
SKILL.md                         主流程與模式路由
references/                      判準、安全、套用與專案整理
scripts/detox-scan.py             有界唯讀掃描
scripts/project-map.py            專案索引驗證與導航產生
scripts/verify-package.py         一次執行測試與套件契約檢查
templates/                       審計及主／子技能、工作流程範本
tests/                           CLI、安全、路由與資源完整性測試
AUDIT-REPORT.md                  本次發現、修正、驗證與限制
```

## 驗證

```powershell
python scripts/verify-package.py
```

測試建立獨立的臨時來源，不掃私人設定，也不修改工作專案。秘密測試使用人工合成值。
套件檢查包含語法、主技能 metadata、引用資源、ledger 與範本完整性。
Windows junction 測試取決於可用平台與權限；其他平台會明確標示跳過。

## 授權

MIT。原始作者與授權保留；版本差異見 [CHANGELOG.md](CHANGELOG.md)。

## 語言版本與安裝

四種語言的主技能、參考文件與範本都完整提供。下載對應語言的發布 ZIP，
解壓後將完整 ai-instruction-detox 資料夾放進宿主的技能目錄；一次只安裝一種語言。
工具共用，機器欄位／檔名不翻譯；預設語言來自包內 metadata，也可指定 `--language en`、
`--language de`、`--language ja` 或 `--language zh-TW`。

原始碼中的翻譯位於 locales/en、locales/de、locales/ja，工具在根目錄 scripts 共用。
建置 ZIP 後每個包都包含可執行工具，不能只安裝單獨的 locales 資料夾。

```powershell
python scripts/build-locales.py --output-dir release-packages-new
```

此建置命令僅適用完整原始碼 repo；發布 ZIP 只含選定語言與執行工具，不含建置器及其他語言來源。

產生四個完整 ZIP、檔案清單與 SHA-256。目的目錄必須全新，保留既有產物。
語言同步、套件範圍與選用方式見 [語言與安裝](references/localization.md)。
