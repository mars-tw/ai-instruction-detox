# AI Instruction Detox 1.1.0 更新の検証

日付：2026-10-08（Asia/Taipei）。元のソース：[mars-tw/ai-instruction-detox](https://github.com/mars-tw/ai-instruction-detox)。
基準 commit：`0b4ce515f209f3fb5cf82522d904f15999b69a1d`。

今回、ローカルのスキルパッケージを更新し、スキャナーとガバナンスの契約を修正して、プロジェクト全体の標準化機能を追加しました。
完全な検査と回帰テストは合格しました。ただし、ヒューリスティックなスキャンや限られたシミュレーションを全面的な安全保証として扱いません。
1.1.0 の基準監査では commit、push、デプロイを行っていません。その後の 1.2.0 はユーザーの明示的な許可に基づき GitHub へ公開しました。原作者と MIT ライセンスを維持します。

## 修正した問題

以下の位置は、元の基準 commit の行番号です。新版のファイルは再編されています。

| ID／重大度 | 元版の証拠 | 問題と影響 | 修正 |
|---|---|---|---|
| S01／高 | `scripts/detox-scan.py:157–159,166,174,194` | インジェクション、曖昧なルール、絶対表現、重複ブロックに元の抜粋が含まれ、同じ行の秘密が stdout／JSON に出る可能性 | 検出を位置／分類に変更。全フィールドとパスの metadata による検出済み秘密の流出を防止 |
| S02／高 | `scripts/detox-scan.py:86–97` | symlink／Windows junction／機密ディレクトリが隔離されず、明示入力もリンク経由で読み取り可能 | 各 ancestor の lstat／reparse を検査。機密ディレクトリ、ファイル、ソース／出力位置を除外 |
| S03／中 | `scripts/detox-scan.py:100–105` | 読み取りエラーを空文字列に変え、未スキャン／打ち切りを成功とみなす可能性 | selected／scanned を分離し、errors／skipped を維持。部分スキャンは終了 3 とし、リソース上限を追加 |
| S04／中 | `scripts/detox-scan.py:177–183` | 2 ノードの相互参照だけを探し、長い循環と自己参照を見落とす | 非再帰の強連結成分を使用。1,200 ノードの循環で呼び出しスタックがあふれないことを検査 |
| S05／中 | `scripts/detox-scan.py:74–78,134–144` | 一般的な references パス、Markdown／空白を含むパスを見落とし、解析と範囲が不明確 | URL、アンカー、ローカルパスを区別。選択範囲だけを検査し、参照による内容の追加読み取りをしない |
| S06／中 | `scripts/detox-scan.py:191` | 先頭 200 文字を重複 identity として、同じ始まりの異なるルールを誤統合 | 正規化した段落全体を比較。段落を出力せず、ソース位置を報告 |
| S07／高 | `scripts/detox-scan.py:266–268` | JSON を w で上書きし、ソースや既存のレポートを破壊する可能性 | exclusive create、出力先／祖先検査、上書きと機密出力先の拒否。CLI モードを相互排他的にする |
| G01／高 | `SKILL.md:93` | ledger が原文を要求する一方、混在する秘密を保護せず、CSV が数式を実行する可能性 | 派生出力の統一マスキング契約、CSV の数式対策、JSON での交換を推奨 |
| G02／高 | `references/apply-phase.md:45–59,85` | バックアップ後に秘密を検査し、監査対象プロジェクトのスクリプトを無条件に実行できる | バックアップ前に検査。安全な保管方法がなければその項目を延期。スクリプト／hooks はレビュー後にタスクの許可に従って実行 |
| G03／高 | `references/apply-phase.md:26–30`、`templates/06-rollback.template.md:16` | 基準スナップショットの契約がなく、復元で後の変更を上書きする可能性。CREATE／MOVE の処理がない | 存在、SHA-256、候補と適用の digest を追加。各項目の三者比較、新規ファイルの回収、移動の復元を規定 |
| G04／中 | `SKILL.md:93–94,189–201` | ledger に強制の程度、例外、依存関係がなく、02–05 のテンプレートが不足 | 元の 25 列を維持して 3 列を追加。00–06 と baseline のテンプレートを補完 |
| G05／中 | `README.md:38,99`、`SKILL.md` frontmatter | 主ファイルだけでは依存物が失われ、「書き込みゼロ」とレポート作成が矛盾し、metadata が現在の validator に不適合 | 完全なパッケージの説明を追加。ソースの読み取り専用と成果物への書き込みを分離し、version／author を metadata に移動 |
| G06／中 | `references/12-checks.md:23,215–218`、`references/multi-agent-review.md:85` | 誠実さをプラットフォーム保証とみなし、スケジュールを一律不可能とし、session をまたぐ正本の分裂を見落とす | 公式／実測の証拠で能力を判断。ナビゲーションと読み込みを区別し、Agent 間のコピーもバージョン分裂を検査 |

安全上の技術的根拠には [Python のファイル走査仕様](https://docs.python.org/3.8/library/os.html#os.walk)、
[Windows reparse attributes](https://docs.python.org/3.12/library/stat.html#stat.FILE_ATTRIBUTE_REPARSE_POINT)、
[OWASP CSV Injection](https://community.owasp.org/attacks/CSV_Injection) を使用しました。
このプロジェクトは標準ライブラリの CLI であり、無関係な Web framework のチェックリストは適用していません。

## 追加：プロジェクト全体の標準化

メインスキルに `ORGANIZE_PROJECT` の振り分けを追加しました。詳しい手順は [project-organization.md](references/project-organization.md) を参照してください。

1. 既存の責任、パス、作業文書、受け入れの出典から、メインプロジェクト／サブプロジェクトを棚卸し。
2. メインスキルと共通ワークフローを作成し、サブスキルと局所ワークフローを各サブプロジェクト内に配置。
3. 一つの `project-map.json` にノード、親子関係、スキル、ワークフロー、owner、出典、依存関係を保存。
4. `project-map.py` で検証し、パンくずナビゲーションの Markdown、ディレクトリツリー、Mermaid のマインドマップ、依存関係図を出力。
5. 隔離した run 内で候補案をレビューし、正式適用後に経路を厳密に照合。製品コードは移動しない。

ツールは不正な schema／型、重複 ID／パス、未知の parent／依存先、範囲外、機密位置、
リンク、依存関係の循環を拒否します。すべてのナビゲーションは同じ索引に基づき、戻るリンクは繰り返しの読み込みを要求しません。
メイン／サブスキルとワークフローのテンプレートは、入力、出力、責任、受け入れ、停止、引き継ぎ、復元の要件を含みます。

## 実際の検証

環境：Windows、Python 3.12.10、Git 2.53.0.windows.3。

| 検証 | 結果 | 証拠 |
|---|---|---|
| `python -W error scripts/verify-package.py` | PASS | 80 tests、0 failures、0 skipped |
| Scanner | PASS | 38 tests。秘密出力、実際の symlink／Windows junction、CLI、網羅性エラー、長い循環を含む |
| Project map | PASS | 39 tests。3 階層 fixture、厳密な経路、読み取り専用、上書き拒否、エスケープ、不正入力を含む |
| Package contracts | PASS | 3 tests。メインスキル／reference の全リソースリンク、テンプレートの完備、28 列への移行を含む |
| Python 3.8 grammar | PASS | scripts／tests に ast.parse で互換構文を検査。Python 3.8 runtime の実行ではない |
| 公式ローカルの skill-creator quick_validate | PASS | `Skill is valid!`。frontmatter と主な入口の互換性 |
| `git diff --check` | PASS | whitespace error なし。Git の LF／CRLF の通知はこの結果に影響しない |
| 独立した前向き検証 | PASS（候補ガバナンス） | frontend／backend fixture で完全なメイン／サブスキル、ワークフロー、28 列 ledger、00–06、baseline、patch を生成 |
| 前向き検証でのソース維持 | PASS | 元の 11 ファイルの digest と Git status が同じで、既存の未コミットの製品変更 2 件を維持 |
| 候補の経路とナビゲーション | PASS | 隔離 overlay の厳密な検証に合格。4 つのナビゲーションを 2 回再生成し byte 単位で一致。Markdown リンクを解決可能 |
| 候補 patch | PASS | 隔離 fixture で `git apply --check` に合格。実際の適用はしていない |
| 実際の製品テスト／正式適用／復元 | NOT_RUN | 今回はスキルパッケージの更新で、ユーザーの他の製品プロジェクトを統治、変更していない |

実行担当、文書レビュー、前向き評価は、ホスト内蔵の独立した Agent コンテキストを使い、各自の範囲を維持しました。
その後、監督担当が成果を読み戻し、実際に検証しました。これは異なるモデルによる検証ではありません。
外部モデルとの往復を、この監査の検証証拠に使用していません。

## 新規モジュールの相互レビューによる修正

- Mermaid ID が end の場合に [公式の予約構文](https://mermaid.js.org/syntax/flowchart.html) に衝突するため、安全な node_ 接頭辞を使用。manifest ID とナビゲーションのアンカーを維持。
- .envrc と credentials.* を除外に追加し、ソース、manifest、root、出力パスに同じ制限を適用。
- Markdown のナビゲーション入口に、同じ出典のツリー、マインドマップ、依存関係図を直接含め、図を見るために .mmd を別途探す必要をなくした。

## バージョン互換性と制限

- JSON schema v2 は raw snippet／text／ref を削除し、循環と重複のフィールドも位置構造に変更。利用側の更新が必要。
- Ledger は 25 → 28 列。旧ファイルに `strength`、`exceptions`、`dependencies` を追加できるが、例外を捏造してはいけない。
- 秘密／インジェクションの検出とパス解析はヒューリスティックで、すべての形式を網羅できない。検出は文脈に応じて判断する必要がある。
- `complete` は選択範囲の読み取り完了を示し、プロジェクト全体の完全な一覧や安全の証明ではない。
- ナビゲーションツールはスキル本文を作成せず、実際の owner、事業の完全性、manifest に未知の秘密があるかを検証しない。
- 他の Python バージョン／OS、実際の初心者の操作、ガバナンスの適用と復元は未実行で、合格とは記録しない。
- パス検査は OS のサンドボックスではなく、悪意あるプロセスによる祖先ディレクトリの同時置き換えへの防御を保証できない。

## 繁体字中国語の文章の修正記録

| 元の文／方法 | 理由 | 変更後 |
|---|---|---|
| 監査段階は書き込みゼロ | 新しいレポート／候補ファイルの作成と矛盾 | 監査はソースを変更しない。指定モードでだけ、新しい隔離成果物を書き込む |
| SKILL.md を AI エージェントに渡す | 参照する判断基準とスクリプトが欠落する | 完全なスキルパッケージと相対パスを維持する |
| 正直な回答 → プラットフォームで保証済み → 削除可能 | ポリシー上の期待を実行可能な動作保証と誤認 | 保証の証拠がなければ B として維持する |
| 同じ session で同時に読み込む場合だけ重複 | 異なる Agent 間のルール正本の分裂を見落とす | 範囲と正本で判断し、session 間のコピーも検査する |

その他の主な変更は技術的な契約と機能の追加です。原作者、日付、ライセンス、英語の識別子を維持しています。
