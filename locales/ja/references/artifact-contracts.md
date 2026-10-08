# 監査成果物の契約

監査対象の内容には秘密やコマンドが含まれる場合があります。ここでは派生出力を規定し、追加の認証情報の読み取りを許可しません。

## 隔離とバージョン基準

毎回新しいディレクトリ `.ai-detox/run-識別碼/` を使用します。出力先と祖先ディレクトリのリンク／junction を検査し、
許可範囲内であることを確認します。既存のレポートを維持し、staging、バックアップ、引き継ぎデータが Agent に自動読み込みされないようにします。
Git ignore と `git ls-files` を確認します。追跡済みのファイルは、ignore により自動的に除外されません。

`baseline-manifest.json` は `schema_version: 1` を使用し、各変更を次のように記録します。

| フィールド | 契約 |
|---|---|
| `source_path`／`target_path` | 許可されたルート内の相対パス。範囲外、機密位置、リンクは禁止 |
| `action` | `CREATE`／`UPDATE`／`MOVE`／`ARCHIVE`。削除には別途復元可能な計画が必要 |
| `source_exists`／`target_exists` | 監査時の存在。新規ファイルと更新を区別 |
| `source_sha256`／`target_sha256` | 既存ファイルの digest。元々存在しなければ null |
| `proposed_path`／`proposed_sha256` | 候補の位置と digest |
| `baseline_copy` | 機密検査を通過した基準コピー。安全に保存できなければ null |
| `backup_path` | 適用前の安全なバックアップ先。未適用なら null |
| `applied_sha256` | 適用後の実際の digest。未適用なら null |
| `rule_ids` | 対応する ledger ID |
| `status` | `PROPOSED`／`APPLIED`／`DEFERRED`／`ROLLED_BACK` |

ルート、Git HEAD（存在する場合）、監査時刻、適用時刻も記録します。mtime は補助情報です。digest と存在が、
書き込み前の条件になります。MOVE はソースと出力先の両方を検査し、CREATE は現在も存在しないことを確認します。
原始の秘密や、秘密の値専用の hash を保存しません。ファイル全体の digest はバージョン比較だけに使用します。
manifest は操作記録です。このスキルには自動適用ツールがなく、プログラムによる検証や適用が済んだと主張してはいけません。

## 秘密と抜粋

1. スキャン前に認証情報のディレクトリとファイルを除外します。
2. 許可された指示ファイルに秘密鍵、token、パスワード、認証情報付き URL が混在する場合は、ファイル、行番号、種類だけを報告します。
   `original_text` などのフィールドでは秘密を `[REDACTED]` に置き換え、完全な原文を再引用しません。
3. 確実にマスキングできない部分は、出典の位置と「機密情報を含むため抜粋していません」に置き換えます。
   Diff が元の値を公開する場合は raw patch を作成せず、その項目を `HUMAN_REVIEW` とします。
4. バックアップ前に検査します。秘密を含むファイルを一般的な staging にコピーしてはいけません。許可済みでアクセスを制限した
   保管場所だけに、そのポリシーに従って保存できます。安全にバックアップできなければその項目を停止し、他の項目は遅らせません。
5. 秘密の検出はヒューリスティックです。検出がゼロでも秘密がないとは保証できません。納品予定の成果物をすべて検査します。

## Ledger：固定順序の 28 列

[header](../templates/01-rule-ledger-header.csv) を使用します。先頭 25 列は v1.0 の名称を維持し、
`strength`、`exceptions`、`dependencies` を追加します。新規ファイルは 28 列です。

| フィールド群 | 定義 |
|---|---|
| `rule_id`、`source_file`、`source_location` | 一意の ID、ソースの相対パス、行番号または節 |
| `original_text`、`normalized_rule` | マスキング済み原文と正規化したルール。有効な意図を維持 |
| `category`、`scope`、`agent` | 種類、適用範囲、実際の Agent または UNKNOWN |
| `severity` | `LOW`／`MEDIUM`／`HIGH`／`CRITICAL`。リスクであり、強制の程度ではない |
| `default_behavior` | `A`（出典のあるツール保証）／`B`（保証なし）／`C`（プロジェクト固有）／`UNKNOWN` |
| `conflict`、`duplicate`、`incident_patch`、`ambiguity` | 結論、関連 ID、証拠。なければ NONE |
| `testability`、`stale_status`、`scope_problem`、`cost_problem` | 検証方法、鮮度、範囲とコストの問題 |
| `security_status`、`capability_mismatch`、`circularity` | 安全評価、能力の差、読み込み循環の証拠 |
| `recommendation`、`target_location`、`reason`、`confidence` | 10 種類の処置のいずれか、移行先、理由、0–1 の確信度 |
| `strength` | `REQUIRED`／`RECOMMENDED`／`OPTIONAL`／`INFORMATIONAL`／`UNKNOWN` |
| `exceptions`、`dependencies` | 明示的な例外、依存する rule ID／ファイル／ツール。なければ NONE |

ルールの種類：security、legal、data-integrity、business-brand、architecture、test-acceptance、
workflow、tool-usage、multi-agent-dispatch、output-format、language-tone、persona、
factual-context、project-state、example、history、one-off-exception、incident-patch、
temporary、possible-prompt-injection。

各ルールには ID と処置をそれぞれ一つ割り当てます。MERGE／MOVE は新しい位置まで追跡可能にします。CSV writer でカンマ、
引用符、改行を処理します。Excel 用のレビューコピーでは、セルの最初の有効文字が `=`、`+`、`-`、`@`、
または先頭が tab／CR／LF の場合、先頭に一重引用符を追加します。再オープンや再保存後の安全を保証するものではありません。逐語的な保存と構造化した
交換にはマスキング済みの JSON を使用し、表計算による実行を避けます。[OWASP CSV Injection](https://community.owasp.org/attacks/CSV_Injection) を参照してください。

## 検証状態

`PASS` には実際のコマンド、成功結果、またはファイルの証拠が必要です。`FAIL` には反例、`NOT_RUN` には未実行の理由、
`NOT_APPLICABLE` には適用されない理由を記録します。シミュレーションは設計検査であり、実際のテストと同じではありません。
ナビゲーションリンクは強制読み込みではありません。テストスクリプトが存在しても、実行済みとは限りません。
