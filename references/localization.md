# 語言版本與安裝

提供 `zh-TW`、`en`、`de`、`ja` 四種語言。中文根目錄是翻譯來源，語意與安全契約
透過相同版本維護；翻譯是閱讀／執行版本，不新增權限或與來源競爭正本。
不要讓宿主同時自動載入四份同名技能。

## 完整範圍

各語言有 README、SKILL、CHANGELOG、AUDIT-REPORT、全部 references 與 templates。
自然語言說明及模板標籤翻譯，程式碼、命令、檔名、JSON keys、schema version、CSV header、
狀態 enum、rule ID、模板變數與外部網址保持一致。
來源文件保留歷史測試結果，不能把有限實測說成所有語言／所有平台都已驗證。

原始碼中翻譯文件在 `locales/en`、`locales/de`、`locales/ja`；工具與測試只有一份，
維護於根目錄 `scripts/`、`tests/`。直接讀 locale 主技能時，命令需從 repo 根目錄執行。
只複製 locale 資料夾不能得到可執行的完整技能。

## 發布包

```powershell
python scripts/build-locales.py --output-dir release-packages-new
```

此建置命令僅適用完整原始碼 repo；發布 ZIP 只含選定語言與執行工具，不含建置器及其他語言來源。

輸出目錄必須全新；產生四個 ZIP、SHA256SUMS.txt 與 RELEASE-MANIFEST.json。
每個 ZIP 的頂層是 `ai-instruction-detox/`，包含該語言的文件、範本、共用工具、測試及
`package-language.json`。只打包明確的公開檔案，不含 Git、staging、備份、私人路徑或憑證。
包內語言切換連結指向 GitHub 對應版本，避免依賴其他未安裝的語言文件。

下載並確認 SHA-256 後，把完整資料夾放到宿主的技能目錄。沿用宿主自己的載入／刷新方式，
不假設所有產品的安裝目錄或自動載入語法相同。更新前保留既有技能修改與可回復副本。
不要同時安裝四個同名主技能；需要換語言時先核對來源版本，再換完整包。

## 工具語言

掃描器與導航工具接受 `--language zh-TW|en|de|ja`。未指定時，使用工具所在技能包的
`package-language.json`，原始碼預設繁中；不讀被審計目錄內的 metadata，也不依作業系統
環境猜測。CLI 顯示文字、摘要與產生的導航標籤改變，機器欄位、檔名與退出碼不變。

```powershell
python scripts/detox-scan.py --root . --language en
python scripts/project-map.py check --manifest project-map.json --language de
python scripts/project-map.py render --manifest project-map.json --output-dir map-preview-new --language ja
```

這些旗標不改變允許路徑、掃描範圍、寫入邊界或任何安全檢查。

## 維護與驗證

每次來源契約變更，同步相關翻譯、模板與版本；以測試比對完整文件清冊、相對連結、
模板變數、機器欄位、程式碼命令與語言選項。另做獨立上下文語意覆核，不能只檢查檔案存在。
CLI 每種語言都用臨時 fixture 實跑；發布 ZIP 解壓後驗證資源、工具與 metadata。
未實際執行的語言／平台檢查標記 NOT_RUN，不因翻譯已寫完就宣稱通過。
