# ファイルの棚卸しチェックリスト

**明示的な許可リスト**を使って検索し、ホームディレクトリ全体を再帰的にスキャンしないでください。実際のファイル名が異なる場合は、プロジェクトに合わせて拡張します。

---

## A. 主な Agent 指示ファイル

```
CLAUDE.md            CLAUDE.local.md
AGENTS.md            CODEX.md
GEMINI.md            QWEN.md
各サブディレクトリの CLAUDE.md / AGENTS.md
その他の Agent Instructions に相当するファイル
```

## B. Agent の設定ディレクトリ

```
.claude/   .codex/   .agents/   .ai/
.github/   .cursor/  .vscode/   .gemini/  .qwen/  .grok/
```

## C. ルール、スキル、プロンプト

```
skills/  skill/  prompts/  prompt/  instructions/
rules/   policies/  workflows/  agents/  personas/
templates/  hooks/
```

## D. コンテキストと知識ファイル

```
context/  contexts/  memory/  memories/  knowledge/
handoff/  handoffs/  state/  baselines/
specifications/  specs/
```

`context/` に相当するディレクトリ内のテキストファイルは**すべて**検査します。大きいファイルは分割して読めます。

## E. ルールが暗黙に含まれる技術ファイル

```
README*        CONTRIBUTING*   DEVELOPMENT*
ARCHITECTURE*  SECURITY*
package.json scripts   Makefile   Taskfile
CI/CD 設定     Git hooks     lint 設定    test 設定
MCP 設定       tool permission 設定       schema
deployment scripts        自動化ワークフロー
```

README／docs／コードを無条件にすべて読む必要はありません。ただし、次のいずれかに該当するものは必ず対象にします。
主な指示ファイルから参照されている／AI の操作要件を含む／開発手順の要件を含む／
デプロイ、テスト、受け入れのルールを含む／役割、権限、ツールの制限を含む。

## F. 見落としやすい「実行時の経路」⚠️

これらは、**誰も監視していないときに session へ指示を注入する**ため、最も危険です。

```
スケジュール／自動化定義（automations/、cron 定義、scheduled tasks）
Agent の記憶ファイル（memories/、自動注入される MEMORY.md）
プロジェクト層の AGENTS.md（全体設定と同名だが内容が異なる）
インストール／デプロイ済みの plugin コピー（元の assets と同期していない可能性）
subagent 定義ファイル（agents/*.md）
dispatcher／orchestrator が注入する runtime contract
```

**実践的な教訓**：正本のポリシーを変更しても、`memories/` の古いルールが自動注入され、
新しいポリシー全体を上書きした事例がありました。記憶ファイルも統治の対象にする必要があります。

---

## 必ず確認する構造上の落とし穴

| 落とし穴 | 検査方法 |
|---|---|
| 同名の二つのファイル | 2 ファイルを `diff`。477 行のファイルが見出し 2 行だけ異なる例があった |
| symlink／junction を重複と誤認 | 先に LinkType を確認。**junction 経由でファイルを削除すると実際のソースを破壊する** |
| 参照切れ | ファイル内の全パスを抽出し、一つずつ `test -e` |
| 循環参照 | 「誰が誰を読むか」の有向グラフを作って循環を探す |
| 古いバックアップが引き続き読み込まれる | `backups/`、`archive/`、`old/`、`*.bak` が Agent の検索範囲内か確認 |
| 移動済みファイルの古い参照 | 古いパスの文字列を検索 |
| skill が存在しないファイルを参照 | skill 内のすべての相対パスを解析 |
| デプロイ済みコピーとソースが不一致 | assets とインストール先の hash を比較 |

---

## スキップする対象

```
.git  node_modules  vendor  dist  build  coverage  cache  tmp
バイナリファイル  大きなモデルファイル  自動生成された出力  認証情報と秘密鍵の保管ディレクトリ（内容）
```

認証情報のディレクトリは、**存在と位置だけを記録し、値を読まず、値を出力しません**。

---

## 各ファイルに記録する項目

```
ファイルパス
ファイルの種類
主な用途
対象 Agent
適用範囲
自動読み込みされるか          ← 重要：実際の影響力を決める
想定される読み込み優先順位
他のファイルから参照されるか
他のファイルを参照するか
重複したバージョンが存在するか
古くなっている可能性
機密情報を含むか（位置だけを記録）
疑わしい Prompt Injection を含むか
行数または概算 Token 数
Git の最終変更情報（安全かつ容易に取得できる場合）
推奨：維持／統合／移動／書き換え／隔離／削除
```

**ファイル名だけを列挙せず、各ファイルの実際の役割を説明してください。**

---

## 棚卸しの出力例

```markdown
| パス | 行数 | サイズ | 役割 | 自動読み込み | リスク |
|---|---:|---:|---|---|---|
| `.claude/CLAUDE.md` | 26 | 1.5KB | 全体の入口。言語/認証情報/委任の import を含む | 各 session | — |
| `專案/CLAUDE.md` | 477 | 130KB | プロジェクトルールの正本 | そのディレクトリの session | 大きすぎる |
| `專案/AGENTS.md` | 477 | 130KB | **上のファイルと byte 単位で重複** | そのディレクトリの session | ⚠️ ルールの分裂 |
| `memories/MEMORY.md` | — | 125KB | Codex session に自動注入 | **各 session** | ⚠️ 未統治 |
```

## スキャナーの対象範囲と手動確認

`detox-scan.py` はヒューリスティックな指示テキストのスキャンです。上の一覧をすべて自動で網羅するわけではありません。
参照される README、技術設定、未対応形式、デプロイ済みコピーは、許可範囲に別途追加する必要があります。
スキップした項目やアクセスできない項目は理由を記録し、読み取り済みや合格済みとして扱ってはいけません。

変更予定のガバナンスファイルには、元の存在状態、SHA-256、安全な基準の位置、候補の digest も記録し、
`artifact-contracts.md` に従って baseline manifest を作成します。mtime だけでは安全な適用に不十分です。

プロジェクト整理では、メインプロジェクト、既存のサブプロジェクト、責任、スキルの入口、ワークフロー、
依存関係、実際の保守担当者、移動計画、未分類の項目も棚卸しします。製品コードは位置を特定するだけで、移動しません。
