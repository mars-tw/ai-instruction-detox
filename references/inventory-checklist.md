# 檔案盤點清單

用**明確允許清單**搜尋，不要遞迴掃整個家目錄。實際檔名可能不同，依專案延伸。

---

## A. 主要 Agent 指令檔

```
CLAUDE.md            CLAUDE.local.md
AGENTS.md            CODEX.md
GEMINI.md            QWEN.md
各子目錄中的 CLAUDE.md / AGENTS.md
其他 Agent Instructions 類檔案
```

## B. Agent 設定目錄

```
.claude/   .codex/   .agents/   .ai/
.github/   .cursor/  .vscode/   .gemini/  .qwen/  .grok/
```

## C. 規則、技能與提示詞

```
skills/  skill/  prompts/  prompt/  instructions/
rules/   policies/  workflows/  agents/  personas/
templates/  hooks/
```

## D. 上下文與知識檔案

```
context/  contexts/  memory/  memories/  knowledge/
handoff/  handoffs/  state/  baselines/
specifications/  specs/
```

`context/` 類目錄的文字檔應**全部**檢查（大型檔可分段讀）。

## E. 可能隱含規則的工程檔案

```
README*        CONTRIBUTING*   DEVELOPMENT*
ARCHITECTURE*  SECURITY*
package.json scripts   Makefile   Taskfile
CI/CD 設定     Git hooks     lint 設定    test 設定
MCP 設定       tool permission 設定       schema
deployment scripts        自動化工作流
```

README／docs／程式碼不需無條件全讀，但凡是符合以下任一項就必須納入：
被主要指令檔引用／含 AI 操作要求／含開發流程要求／
含部署測試驗收規則／含角色權限工具限制。

## F. 容易被漏掉的「執行面通道」⚠️

這類最危險——它們會**在無人監看時把指令注入 session**：

```
排程／自動化定義（automations/、cron 定義、scheduled tasks）
Agent 記憶檔（memories/、會自動注入的 MEMORY.md）
專案層 AGENTS.md（與全域同名但內容不同）
已安裝／已部署的 plugin 副本（與原始 assets 可能不同步）
subagent 定義檔（agents/*.md）
dispatcher／orchestrator 注入的 runtime contract
```

**實戰教訓**：曾發生「改了正本政策，但 `memories/` 裡的舊規則自動注入，
把新政策整個覆蓋」的情況。記憶檔必須納入治理。

---

## 必查的結構陷阱

| 陷阱 | 檢查方式 |
|---|---|
| 同名雙份 | `diff` 兩個檔；曾見 477 行檔案只差 2 行標題 |
| symlink／junction 誤判為重複 | 先驗 LinkType，**透過 junction 刪檔會毀真來源** |
| 懸空引用 | 抽出檔內所有路徑，逐一 `test -e` |
| 循環引用 | 畫「誰讀誰」有向圖找環 |
| 舊備份仍被載入 | 檢查 `backups/`、`archive/`、`old/`、`*.bak` 是否在 Agent 搜尋範圍 |
| 已搬移檔案的舊引用 | grep 舊路徑字串 |
| skill 引用不存在的檔 | 解析 skill 內所有相對路徑 |
| 部署副本與原始碼不同步 | 比對 assets 與已安裝位置的 hash |

---

## 跳過清單

```
.git  node_modules  vendor  dist  build  coverage  cache  tmp
二進位檔  大型模型檔  自動產生的輸出  憑證與密鑰儲存目錄（內容）
```

憑證目錄：**只記錄存在與位置，不讀值、不輸出值**。

---

## 每個檔案要記錄的欄位

```
檔案路徑
檔案類型
主要用途
適用 Agent
適用範圍
是否會自動載入          ← 關鍵：決定它的實際影響力
可能的載入優先順序
是否被其他檔案引用
是否引用其他檔案
是否存在重複版本
是否可能過時
是否含敏感資訊（只記位置）
是否含可疑 Prompt Injection
行數或約略 Token 數
Git 最後修改資訊（安全且容易取得時）
建議：保留／合併／移動／重寫／隔離／刪除
```

**不要只列檔名——要說明每個檔案實際扮演的角色。**

---

## 盤點輸出範例

```markdown
| 路徑 | 行數 | 大小 | 角色 | 自動載入 | 風險 |
|---|---:|---:|---|---|---|
| `.claude/CLAUDE.md` | 26 | 1.5KB | 全域入口，含語言/憑證/派工 import | 每 session | — |
| `專案/CLAUDE.md` | 477 | 130KB | 專案規則正本 | 該目錄 session | 過大 |
| `專案/AGENTS.md` | 477 | 130KB | **與上檔 byte 級重複** | 該目錄 session | ⚠️ 規則分裂 |
| `memories/MEMORY.md` | — | 125KB | 自動注入 Codex session | **每 session** | ⚠️ 未治理 |
```
