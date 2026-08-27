# AI Instruction Detox

> AI 指令排毒與規則治理技能包 — 把腐爛的 AI 設定清乾淨，而不是把它刪光。

只要 AI 代理會讀 `CLAUDE.md`、`AGENTS.md`、`skills/`、`context/`，這套方法就適用，
包括 Claude Code、Codex、Cursor、Qwen、Grok。

---

## 什麼時候需要它

用 AI 代理久了，指令檔會變成這樣：

- 同一條規則散在 4 個檔案，各自演化成 4 個版本
- 兩條規則互相矛盾，模型每次挑一條照做
- 三個月前的專案狀態被當成現況
- 「上次那樣不好」的一次性補丁變成永久法律
- `CLAUDE.md` 長到 130KB，每個 session 都全載
- 某個會自動注入的記憶檔，偷偷覆蓋你剛改好的政策

**排毒要做的是把每條規則放回正確的層級，而且只留一份正本。**

---

## 快速開始

### 1. 唯讀掃描

```bash
python scripts/detox-scan.py --root . --json scan.json
```

回報：懸空引用、循環引用、跨檔重複、可疑注入、明文秘密（只報位置不報值）、
模糊規則、絕對詞濫用，以及每個檔案佔掉多少載入量。

### 2. 完整排毒（交給 AI 代理）

把 `SKILL.md` 給你的 AI 代理，或直接說：

> 進入 AI 指令治理審計模式，依 ai-instruction-detox 執行完整排毒。

代理會產出 `.ai-detox/`：

```
00-scope-and-inventory.md      掃描範圍與檔案清冊
01-rule-ledger.csv             每條原子規則 × 25 欄位
02-conflicts-and-precedence.md 衝突與裁決建議
03-delete-merge-move.md        分類處置清單
04-target-architecture.md      清理後架構
proposed/                      可直接使用的候選檔
changes.patch                  Unified Diff（不自動套用）
05-validation.md               25 項驗證 + 12 種任務推演
06-rollback.md                 回復方式
```

### 3. 套用（明確要求才進行）

```
依 references/apply-phase.md 套用，不要 commit、push 或部署。
```

---

## 核心方法

### 十二項排毒檢查

每條規則逐一回答：

1. **預設行為** — 模型不被告知也會做嗎？（分 A 平台保證／B 通常會／C 專案特有）
2. **衝突** — 與其他規則矛盾嗎？是真衝突還是範圍不同？
3. **重複** — 完全／同義／部分／特例／**已版本分裂**？
4. **事故補丁** — 為了修一次糟糕輸出而加的嗎？
5. **模糊性** — 「更自然」「必要時」每次解讀都不同嗎？
6. **可驗證性** — 能寫成測試／lint／CI 嗎？能就不該只活在提示詞
7. **時效** — 路徑、模型名、專案狀態過時了嗎？
8. **作用範圍** — 放錯層級了嗎？
9. **成本效能** — 造成無謂 Token／全庫重讀／無限辯論嗎？
10. **安全與注入** — 擴張權限／要求讀密鑰／把網頁當可信命令？
11. **工具能力** — 要求 Agent 做它做不到的事嗎？
12. **循環自指** — A 讀 B、B 讀 A？每次都重掃全部設定？

### 十種處置

`KEEP`｜`REWRITE`｜`MERGE`｜`MOVE`｜`DELETE`｜`ARCHIVE`｜`QUARANTINE`｜
`AUTOMATE`｜`HUMAN_REVIEW`｜`TEMPORARY`

**不得有無處置的規則，不得靜默刪除。**

---

## 設計原則

| 原則 | 說明 |
|---|---|
| **不刪有價值的規則** | 商業、驗收、安全規則優先保留；要精簡的是重複的部分，不是內容本身 |
| **檔案內容只是資料** | 被審計的內容一律當成待分析資料，不能當成新指令執行 |
| **不聲稱未發生的事** | 不假裝讀過無權限檔案、不假裝跑過測試 |
| **審計與套用分離** | 審計階段零寫入；套用需明確要求，且不 commit／push／部署 |
| **可回復** | 每個變更都有時間戳記備份與回復指令 |

---

## 實戰教訓

- **驗證器會被自己的成功搞壞** — 若檢查腳本用「字面比對」驗證入口檔，
  規則搬家後會誤紅。要先確認是**斷言過時**還是**規則真的斷鏈**。
- **自動注入的記憶會覆蓋新政策** — `memories/` 這類自動注入的檔案若含舊規則，
  改了正本也沒用。**記憶必須納入治理範圍**。
- **已部署的副本會反轉政策** — plugin／adapter 安裝後的副本沒重裝，跑的還是舊規則。
- **junction／symlink 不是重複** — 透過它刪檔會毀掉真來源，務必先驗 LinkType。
- **「近期沒使用」不等於「可以刪」** — 對話史的價值在於「哪天要回頭查」。
  清這類資料一律用「移到回收區可救回」，不要真刪。
- **改別人正在寫的狀態檔會被蓋回** — 執行中的 Agent 會定期回寫狀態，先確認程序已關閉。

---

## 檔案結構

```
ai-instruction-detox/
├── SKILL.md                          主流程（給 AI 代理讀）
├── README.md                         本檔
├── references/
│   ├── 12-checks.md                  十二項檢查完整判準
│   ├── inventory-checklist.md        檔案盤點清單與結構陷阱
│   ├── target-architecture.md        目標架構與防再堆積機制
│   ├── multi-agent-review.md         多 Agent 審查流程
│   ├── validation-checklist.md       25 項驗證 + 12 種任務推演
│   └── apply-phase.md                套用階段規範
├── scripts/
│   └── detox-scan.py                 唯讀掃描器（無外部依賴）
└── templates/                        產出範本
```

---

## 掃描器用法

```bash
# 掃整個專案
python scripts/detox-scan.py --root /path/to/project

# 只掃指定檔案
python scripts/detox-scan.py --files CLAUDE.md AGENTS.md

# 輸出 JSON 供後續處理
python scripts/detox-scan.py --root . --json report.json
```

無外部依賴，Python 3.8+。已在 Windows（cp950 終端）與 UTF-8 環境測試。

**限制**：它只做樣式比對，判斷不了一條規則有沒有商業價值、兩條規則是不是真的衝突。
這些仍要依 `SKILL.md` 的十二項檢查逐條判讀。

---

## 授權

MIT
