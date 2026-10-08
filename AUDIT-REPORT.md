# AI Instruction Detox 1.1.0 更新驗證

日期：2026-10-08（Asia/Taipei）。原始來源：[mars-tw/ai-instruction-detox](https://github.com/mars-tw/ai-instruction-detox)，
基準 commit：`0b4ce515f209f3fb5cf82522d904f15999b69a1d`。

本次已更新本機技能包：修正掃描器與治理契約，新增全專案制式化整理能力。
完整檢查與迴歸測試通過；不把啟發式掃描或有限推演當成全面安全保證。
1.1.0 基準審計時未 commit、push 或部署；後續 1.2.0 依使用者明確授權發布至 GitHub。保留原作者與 MIT 授權。

## 已修正問題

以下位置指原版基準 commit 的行號；新版檔案已重新編排。

| ID／級別 | 原版證據 | 問題與影響 | 修正 |
|---|---|---|---|
| S01／高 | `scripts/detox-scan.py:157–159,166,174,194` | 注入、模糊規則、絕對詞與重複區塊含原始摘錄，可能把同行秘密帶進 stdout／JSON | 發現改為位置／分類；所有欄位及路徑 metadata 防止帶出已偵測秘密 |
| S02／高 | `scripts/detox-scan.py:86–97` | 未隔離 symlink／Windows junction／敏感目錄；明確輸入也可跨連結讀取 | 每層 ancestor 的 lstat／reparse 檢查；敏感目錄、檔案及來源／輸出位置排除 |
| S03／中 | `scripts/detox-scan.py:100–105` | 讀取錯誤吞成空文字，漏掃／截斷可能被當成功 | 分開 selected／scanned，保留 errors／skipped，部分掃描退出 3，加入資源上限 |
| S04／中 | `scripts/detox-scan.py:177–183` | 只找兩節點互指，漏長環與自指 | 非遞迴強連通元件，檢查 1,200 節點環不溢出呼叫堆疊 |
| S05／中 | `scripts/detox-scan.py:74–78,134–144` | 漏常見 references 路徑、Markdown／空白路徑，解析與範圍不明 | 區分 URL、錨點及本地路徑；只檢查選定範圍，不因引用展開內容讀取 |
| S06／中 | `scripts/detox-scan.py:191` | 用前 200 字作重複 identity，誤合併相同開頭的不同規則 | 比對完整正規化段落；回報來源位置，不輸出段落 |
| S07／高 | `scripts/detox-scan.py:266–268` | JSON 用 w 覆寫，可破壞來源或既有報告 | exclusive create、目的地／祖先檢查、拒絕覆寫與敏感目的檔；CLI 模式互斥 |
| G01／高 | `SKILL.md:93` | ledger 要求原文卻未保護混入的秘密，CSV 可能執行公式 | 統一衍生輸出遮罩契約、CSV 公式防護與 JSON 交換建議 |
| G02／高 | `references/apply-phase.md:45–59,85` | 備份後才查秘密，且可盲目執行被審計專案的腳本 | 備份前檢查；沒有安全保管方式就暫緩該項；腳本／hooks 先審查再按任務授權執行 |
| G03／高 | `references/apply-phase.md:26–30`、`templates/06-rollback.template.md:16` | 缺基準快照契約；回復可能覆寫後續變更，未處理 CREATE／MOVE | 加存在性、SHA-256、候選與套用 digest，逐項三方比較、回收新檔與還原移動 |
| G04／中 | `SKILL.md:93–94,189–201` | ledger 缺強制程度、例外、依賴，02–05 範本缺失 | 保留原 25 欄並追加三欄；補齊 00–06 與 baseline 範本 |
| G05／中 | `README.md:38,99`、`SKILL.md` frontmatter | 單給主檔會失去依賴；「零寫入」與報告寫入矛盾；metadata 不符合目前 validator | 完整包使用說明、來源唯讀／產物寫入分開，version／author 改放 metadata |
| G06／中 | `references/12-checks.md:23,215–218`、`references/multi-agent-review.md:85` | 誠實被視為平台保證、排程被一概視為不可能、漏跨 session 的正本分裂 | 以官方／實測證據判斷能力，區分導航／載入，跨 Agent 副本仍查版本分裂 |

安全重點採 [Python 的檔案走訪規格](https://docs.python.org/3.8/library/os.html#os.walk)、
[Windows reparse attributes](https://docs.python.org/3.12/library/stat.html#stat.FILE_ATTRIBUTE_REPARSE_POINT)
及 [OWASP CSV Injection](https://community.owasp.org/attacks/CSV_Injection) 作技術依據。
本專案是標準函式庫 CLI，未套用不相關的 Web framework 檢查清單。

## 新增：整個專案制式化整理

主技能新增 `ORGANIZE_PROJECT` 路由，詳細流程見 [project-organization.md](references/project-organization.md)。

1. 從既有責任、路徑、工作文件與驗收來源盤點主專案／子專案。
2. 建立主技能與共同工作流程，子技能及局部流程放在其子專案內。
3. 用單一 `project-map.json` 保存節點、主從關係、技能、流程、owner、來源與依賴。
4. `project-map.py` 驗證後產出麵包屑 Markdown、目錄樹、Mermaid 心智圖及依賴圖。
5. 候選方案在隔離 run 內檢閱，正式套用後嚴格核對路由，不移動產品程式碼。

工具拒絕錯誤 schema／型別、重複 ID／路徑、未知 parent／依賴、越界、敏感位置、
連結與依賴循環。所有導航來自同一索引；返回連結不要求反覆載入。
主／子技能與流程範本含輸入、輸出、責任、驗收、停止、交接與回復要求。

## 實際驗證

環境：Windows、Python 3.12.10、Git 2.53.0.windows.3。

| 驗證 | 結果 | 證據 |
|---|---|---|
| `python -W error scripts/verify-package.py` | PASS | 80 tests，0 failures，0 skipped |
| Scanner | PASS | 38 tests，含秘密輸出、真實 symlink／Windows junction、CLI、覆蓋錯誤及長環 |
| Project map | PASS | 39 tests，含三層 fixture、嚴格路由、唯讀、不可覆寫、跳脫與錯誤輸入 |
| Package contracts | PASS | 3 tests，含所有主技能／reference 資源連結、範本齊備、28 欄遷移 |
| Python 3.8 grammar | PASS | ast.parse 對 scripts／tests 做相容語法檢查；不是 Python 3.8 runtime 實跑 |
| 官方本機 skill-creator quick_validate | PASS | `Skill is valid!`；frontmatter 與主入口相容 |
| `git diff --check` | PASS | 無 whitespace error；Git 的 LF／CRLF 提示不影響此結果 |
| 獨立前向驗證 | PASS（候選治理） | frontend／backend fixture 產生完整主／子技能、流程、28 欄 ledger、00–06、baseline 及 patch |
| 前向驗證來源保留 | PASS | 11 個原始檔 digest 與 Git status 相同，兩個既有未提交產品修改保留 |
| 候選路由與導航 | PASS | 隔離 overlay 嚴格驗證通過，四份導航兩次重建逐位元相同，Markdown 連結可解析 |
| 候選 patch | PASS | 隔離 fixture 中 `git apply --check` 通過，未真正套用 |
| 真實產品測試／正式套用／回復 | NOT_RUN | 本次更新技能包，未治理或改動使用者其他產品專案 |

執行者、文件覆核與前向評測使用宿主內建的獨立 Agent 上下文，保留各自工作範圍，
再由主管讀回成果與實際驗證。這不是不同模型驗證。
未使用外部模型往返作為此審計的驗證證據。

## 新增模組的交叉覆核修正

- Mermaid ID 為 end 時會碰到 [官方保留語法](https://mermaid.js.org/syntax/flowchart.html)，改為安全 node_ 前綴，保留 manifest ID 與導航錨點。
- 補 .envrc 及 credentials.* 排除，來源、manifest、root 與輸出路徑採同一限制。
- Markdown 導航入口直接包含同源的樹狀圖、心智圖與依賴圖，不需另找 .mmd 檔才能看圖。

## 版本相容與限制

- JSON schema v2 移除 raw snippet／text／ref，循環與重複欄位也改為位置結構；消費者需更新。
- Ledger 25 → 28 欄，舊檔可補 `strength`、`exceptions`、`dependencies`；不可憑空補例外。
- 秘密／注入偵測及路徑解析是啟發式，不能涵蓋全部格式；命中須依語境判斷。
- `complete` 是選定範圍讀取完成，不是全專案完整清冊或安全證明。
- 導航工具不建立技能正文，不驗證真實 owner、商業完整性或 manifest 是否含未知秘密。
- 尚未實跑其他 Python 版本／作業系統、真實新手操作、治理套用與回復；不標記通過。
- 路徑檢查不是作業系統沙箱，不能保證防禦惡意程序同時替換祖先目錄。

## 繁中文案修正紀錄

| 原句／原做法 | 原因 | 改成什麼 |
|---|---|---|
| 審計階段零寫入 | 與新增報告／候選檔矛盾 | 審計不改來源；指定模式才寫新的隔離產物 |
| 把 SKILL.md 給 AI 代理 | 會漏掉引用判準及腳本 | 保留完整技能包及相對路徑 |
| 回答誠實 → 平台已保證 → 可刪 | 把政策期望當可執行行為保證 | 缺少保證證據時保留為 B 類 |
| 同一 session 同時載入才算重複 | 漏不同 Agent 的規則正本分裂 | 依範圍與正本判斷；跨 session 副本也檢查 |

其餘主要修改是技術契約與功能新增，原作者、日期、授權與英文識別字保留。
