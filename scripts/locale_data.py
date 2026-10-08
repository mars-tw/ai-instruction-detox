"""Shared, fixed language catalog; source projects never provide translations."""
import argparse
import json
import os
from pathlib import Path
import re
import stat
import sys


LANGUAGES = ("zh-TW", "en", "de", "ja")
TEXT = {
    "language": ("顯示語言", "Display language", "Anzeigesprache", "表示言語"),
    "help": ("顯示說明並結束", "Show help and exit", "Hilfe anzeigen und beenden", "ヘルプを表示して終了"),
    "usage": ("用法", "usage", "Aufruf", "使用方法"),
    "options": ("選項", "options", "Optionen", "オプション"),
    "arguments": ("位置參數", "positional arguments", "Positionsargumente", "位置引数"),
    "invalid_arguments": ("命令參數無效；請見 --help。", "Invalid command arguments; see --help.", "Ungültige Argumente; siehe --help.", "引数が無効です。--help を確認してください。"),
    "scan_description": ("AI 指令排毒唯讀掃描器；只輸出位置與分類", "Read-only AI instruction scanner; locations and categories only", "Nur lesender Scanner für KI-Anweisungen; nur Fundorte und Kategorien", "AI 指示の読み取り専用スキャナー。位置と分類のみを出力"),
    "scan_title": ("AI 指令排毒掃描結果", "AI instruction scan results", "Ergebnisse der KI-Anweisungsprüfung", "AI 指示のスキャン結果"),
    "scan_root": ("明確的專案根目錄；不接受家目錄或磁碟根目錄", "Explicit project root; home and filesystem roots are refused", "Explizite Projektwurzel; Home- und Dateisystemwurzel sind ausgeschlossen", "明示したプロジェクトルート。ホームとファイルシステムのルートは不可"),
    "scan_files": ("明確指定檔案；不遞迴讀取引用", "Explicit files; referenced contents are not loaded", "Explizite Dateien; referenzierte Inhalte werden nicht geladen", "明示したファイル。参照先の内容は読み込まない"),
    "scan_json": ("新的 JSON 報告；不覆寫既有檔案、不建立父目錄", "New JSON report; no overwriting or parent-directory creation", "Neuer JSON-Bericht; kein Überschreiben oder Erstellen von Elternverzeichnissen", "新規 JSON レポート。上書きや親ディレクトリ作成は行わない"),
    "scan_depth": ("根目錄深度為 0；預設 6", "Root depth is 0; default 6", "Wurzeltiefe ist 0; Standard 6", "ルートの深さは 0。既定値 6"),
    "scan_bytes": ("單檔大小上限；預設 1048576", "Maximum file bytes; default 1048576", "Maximale Dateigröße in Bytes; Standard 1048576", "ファイルごとの上限バイト数。既定値 1048576"),
    "scan_counts": ("掃描檔案數：{scanned} / {selected}｜覆蓋狀態：{status}", "Files scanned: {scanned} / {selected} | Coverage: {status}", "Gelesene Dateien: {scanned} / {selected} | Abdeckung: {status}", "スキャン済みファイル：{scanned} / {selected}｜読み取り状況：{status}"),
    "scan_complete": ("完成選定檔案讀取", "selected files read successfully", "ausgewählte Dateien vollständig gelesen", "選択したファイルの読み取り完了"),
    "scan_partial": ("部分掃描，需處理錯誤", "partial scan; resolve coverage errors", "unvollständige Prüfung; Abdeckungsfehler beheben", "一部のみスキャン。読み取りの問題を解消してください"),
    "scan_totals": ("總行數：{lines}｜約略 Token：{tokens}", "Total lines: {lines} | Approximate tokens: {tokens}", "Zeilen insgesamt: {lines} | Geschätzte Tokens: {tokens}", "総行数：{lines}｜概算トークン数：{tokens}"),
    "errors": ("覆蓋錯誤", "Coverage errors", "Abdeckungsfehler", "読み取り範囲のエラー"),
    "secrets": ("疑似秘密", "Possible secrets", "Mögliche Geheimnisse", "秘密情報の可能性"),
    "injections": ("可疑注入", "Possible prompt injection", "Mögliche Prompt Injection", "プロンプトインジェクションの可能性"),
    "dangling_refs": ("懸空引用", "Dangling references", "Nicht auflösbare Referenzen", "参照先が存在しない参照"),
    "boundary_refs": ("引用範圍／政策邊界", "Reference scope or policy boundaries", "Referenzen außerhalb von Bereich oder Richtlinie", "参照範囲またはポリシーの境界"),
    "circular_refs": ("候選循環引用元件", "Candidate cyclic reference components", "Komponenten mit möglichen Referenzzyklen", "循環参照の候補コンポーネント"),
    "duplicate_blocks": ("跨檔重複區塊", "Duplicate blocks across files", "Dateiübergreifend doppelte Blöcke", "ファイル間の重複ブロック"),
    "vague_rules": ("模糊規則", "Vague rules", "Unklare Regeln", "曖昧なルール"),
    "absolute_terms": ("絕對詞", "Absolute terms", "Absolute Formulierungen", "絶対的な表現"),
    "block": ("區塊 {id}（{characters} 字元）：{locations}", "Block {id} ({characters} characters): {locations}", "Block {id} ({characters} Zeichen): {locations}", "ブロック {id}（{characters} 文字）：{locations}"),
    "more": ("另有 {count} 筆", "{count} more findings", "{count} weitere Befunde", "ほか {count} 件"),
    "excluded": ("政策排除：{count}；不輸出來源段落、秘密值或引用字串。", "Excluded by policy: {count}; no source excerpts, secret values or raw reference strings are emitted.", "Durch Richtlinien ausgeschlossen: {count}; keine Quellauszüge, Geheimniswerte oder rohen Referenztexte werden ausgegeben.", "ポリシーによる除外：{count}。原文の抜粋、秘密の値、参照文字列は出力しません。"),
    "heuristic": ("樣式命中需人工判讀；完整治理須依 SKILL.md 執行語意檢查。", "Pattern matches require review; use SKILL.md for semantic governance checks.", "Mustertreffer müssen bewertet werden; semantische Governance-Prüfungen stehen in SKILL.md.", "パターン一致は判断が必要です。意味上のガバナンス確認は SKILL.md に従ってください。"),
    "limitations": ("導航回鏈可能形成循環；秘密偵測不保證找出所有秘密。", "Navigation backlinks may form cycles; detection cannot guarantee finding every secret.", "Navigationsrückverweise können Zyklen bilden; die Erkennung findet nicht garantiert jedes Geheimnis.", "戻りリンクも循環になり得ます。すべての秘密情報を検出できる保証はありません。"),
    "scan_invalid": ("輸入範圍或報告輸出無效；需安全範圍與全新的報告檔。", "Invalid input scope or report output; choose a safe scope and a new report file.", "Ungültiger Eingabebereich oder Berichtspfad; sicheren Bereich und neue Berichtsdatei wählen.", "入力範囲またはレポート出力先が無効です。安全な範囲と新規ファイルを指定してください。"),
    "scan_empty": ("未找到 AI 指令檔。", "No AI instruction files found.", "Keine KI-Anweisungsdateien gefunden.", "AI 指示ファイルが見つかりません。"),
    "scan_limits_error": ("max-depth 必須 >= 0；max-bytes 必須 > 0", "max-depth must be >= 0; max-bytes must be > 0", "max-depth muss >= 0 sein; max-bytes muss > 0 sein", "max-depth は 0 以上、max-bytes は 0 より大きい値が必要です"),
    "map_description": ("驗證明確的專案路由並建立新的導航檔案", "Validate explicit project routes and create new navigation files", "Explizite Projektrouten prüfen und neue Navigationsdateien erstellen", "明示したプロジェクトの経路を検証し、新規ナビゲーションを生成"),
    "map_check": ("唯讀 check 的別名", "Alias for the read-only check command", "Alias für den nur lesenden check-Befehl", "読み取り専用 check コマンドの別名"),
    "map_root": ("明確允許的專案目錄", "Explicit allowed project directory", "Explizit freigegebenes Projektverzeichnis", "明示した許可済みのプロジェクトディレクトリ"),
    "map_manifest": ("相對於專案的 manifest 路徑", "Project-relative manifest path", "Projektbezogener Manifestpfad", "プロジェクトからの相対 manifest パス"),
    "map_require": ("要求所有技能／流程檔案存在", "Require all skill and workflow files to exist", "Alle Skill- und Workflow-Dateien müssen vorhanden sein", "すべてのスキルとワークフローファイルの存在を要求"),
    "map_output": ("新的專案相對目錄；render 必填", "New project-relative directory; required for render", "Neues projektbezogenes Verzeichnis; für render erforderlich", "新規のプロジェクト相対ディレクトリ。render では必須"),
    "map_valid": ("VALID: {nodes} nodes；尚未建立的候選治理路徑：{missing}", "VALID: {nodes} nodes; {missing} candidate governance paths missing", "VALID: {nodes} Knoten; {missing} vorgesehene Governance-Pfade fehlen", "VALID: {nodes} ノード。未作成のガバナンス候補パス：{missing}"),
    "map_rendered": ("RENDERED: {files} 份新導航檔；尚未建立的候選路徑：{missing}", "RENDERED: {files} new navigation files; {missing} candidate governance paths missing", "RENDERED: {files} neue Navigationsdateien; {missing} vorgesehene Governance-Pfade fehlen", "RENDERED: 新規ナビゲーション {files} ファイル。未作成の候補パス：{missing}"),
    "navigation": ("專案導航", "Project navigation", "Projektnavigation", "プロジェクトナビゲーション"),
    "nav_intro": ("此頁由 project-map.json 的明確路由產生。連結只供導航，不要求沿返回連結重讀所有技能。", "Generated from explicit routes in project-map.json. Links provide navigation; backlinks do not require reloading every skill.", "Aus den expliziten Routen in project-map.json erzeugt. Links dienen der Navigation; Rückverweise erfordern kein erneutes Laden aller Skills.", "project-map.json の明示的な経路から生成しています。リンクは移動用であり、戻りリンクによる全スキルの再読み込みは不要です。"),
    "nav_status": ("治理檔案狀態：{status}", "Governance file status: {status}", "Status der Governance-Dateien: {status}", "ガバナンスファイルの状態：{status}"),
    "nav_all": ("全部路徑存在。", "All paths exist.", "Alle Pfade vorhanden.", "すべてのパスが存在します。"),
    "nav_missing": ("有 {count} 個候選路徑尚未建立，尚未可用。", "{count} candidate paths have not been created and are not ready for use.", "{count} vorgesehene Pfade sind noch nicht angelegt und nicht einsatzbereit.", "候補パス {count} 件は未作成で、まだ使用できません。"),
    "route_index": ("路由索引", "Route index", "Routenindex", "経路一覧"),
    "path": ("路徑", "Path", "Pfad", "パス"),
    "owner": ("負責人", "Owner", "Verantwortliche Person", "担当者"),
    "purpose": ("用途", "Purpose", "Zweck", "目的"),
    "skill": ("技能", "Skill", "Skill", "スキル"),
    "workflow": ("工作流程", "Workflow", "Workflow", "ワークフロー"),
    "not_created": ("（尚未建立）", " (not created yet)", " (noch nicht angelegt)", "（未作成）"),
    "dependencies": ("依賴", "Dependencies", "Abhängigkeiten", "依存関係"),
    "none_declared": ("未宣告。", "None declared.", "Keine angegeben.", "未宣言。"),
    "sources": ("盤點來源", "Inventory sources", "Bestandsquellen", "棚卸しの参照元"),
    "maintenance": ("閱讀與維護", "Reading and maintenance", "Lesen und Pflege", "読み方と保守"),
    "nav_loading": ("依任務路由載入主技能與相關子技能。跨子專案才讀共同流程及明確依賴；麵包屑返回不新增強制載入依賴。", "Load the main skill and relevant child skills for the task. Read shared workflows and explicit dependencies for cross-project work only; breadcrumb backlinks add no mandatory loading dependency.", "Haupt-Skill und relevante Teilprojekt-Skills für die Aufgabe laden. Gemeinsame Workflows und explizite Abhängigkeiten nur für projektübergreifende Arbeit lesen; Breadcrumb-Rückverweise erzeugen keine verpflichtenden Ladeabhängigkeiten.", "タスクに対応するメインスキルと子スキルを読み込みます。共通フローと明示した依存先は複数のサブプロジェクトにまたがる場合のみ確認し、パンくずの戻りリンクを強制読み込みの依存にしません。"),
    "nav_derivation": ("樹狀圖、心智圖與依賴圖都由同一份 manifest 產生。箭頭由依賴指向使用者節點；不補猜測的任務或依賴。", "The tree, mindmap and dependency graph derive from one manifest. Arrows point from a dependency to the node using it; no inferred tasks or dependencies are added.", "Baum, Mindmap und Abhängigkeitsgraph stammen aus einem Manifest. Pfeile zeigen von der Abhängigkeit zum nutzenden Knoten; keine vermuteten Aufgaben oder Abhängigkeiten werden ergänzt.", "ツリー、マインドマップ、依存関係図は同一 manifest から生成します。矢印は依存先から利用側へ向き、推測したタスクや依存は追加しません。"),
    "tree": ("專案樹", "Project tree", "Projektbaum", "プロジェクトツリー"),
    "mindmap": ("心智圖", "Mindmap", "Mindmap", "マインドマップ"),
    "dependency_graph": ("依賴圖", "Dependency graph", "Abhängigkeitsgraph", "依存関係図"),
}


def text(key, language="zh-TW", **values):
    if language not in LANGUAGES:
        raise ValueError("unsupported display language")
    return TEXT[key][LANGUAGES.index(language)].format(**values)


def default_language():
    """Only read bounded, regular package metadata beside the installed scripts."""
    target = Path(__file__).resolve().parents[1] / "package-language.json"
    try:
        metadata = target.lstat()
        if (not stat.S_ISREG(metadata.st_mode) or metadata.st_size > 2048
                or getattr(metadata, "st_file_attributes", 0) & 0x400):
            return "zh-TW"
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
        with os.fdopen(os.open(str(target), flags), "rb") as stream:
            opened = os.fstat(stream.fileno())
            if (metadata.st_dev, metadata.st_ino) != (opened.st_dev, opened.st_ino):
                return "zh-TW"
            raw = stream.read(2049)
        if len(raw) > 2048:
            return "zh-TW"
        data = json.loads(raw.decode("utf-8"))
        return data.get("language") if isinstance(data, dict) and data.get("language") in LANGUAGES else "zh-TW"
    except (OSError, ValueError, UnicodeError):
        return "zh-TW"


def language_from_args(argv=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    selected = default_language()
    for index, value in enumerate(arguments):
        candidate = None
        if value == "--language" and index + 1 < len(arguments):
            candidate = arguments[index + 1]
        elif value.startswith("--language="):
            candidate = value.split("=", 1)[1]
        if candidate in LANGUAGES:
            selected = candidate
    return selected


class LocalizedParser(argparse.ArgumentParser):
    def __init__(self, language, **kwargs):
        self.language = language
        super().__init__(add_help=False, **kwargs)
        self._positionals.title = text("arguments", language)
        self._optionals.title = text("options", language)
        self.add_argument("-h", "--help", action="help", help=text("help", language))

    def format_usage(self):
        return super().format_usage().replace("usage:", text("usage", self.language) + ":", 1)

    def format_help(self):
        return super().format_help().replace("usage:", text("usage", self.language) + ":", 1)

    def error(self, message):
        # argparse messages may embed arbitrary argv, including secret values.
        # Keep diagnostics useful without echoing unrecognized input strings.
        known_limits = {text("scan_limits_error", code) for code in LANGUAGES}
        if message in FIXED_ERRORS:
            safe = translate_error(message, self.language)
        elif message in known_limits:
            safe = message
        else:
            # Never classify untrusted argv by a suffix resembling a validator
            # message: its prefix may contain a secret supplied on the CLI.
            safe = text("invalid_arguments", self.language)
        self.print_usage(sys.stderr)
        self.exit(2, "{}: ERROR: {}\n".format(self.prog, safe))


# Preserve machine field names and identifiers in diagnostics; never interpolate
# untrusted keys or source values. Validators continue raising English internally.
FIXED_ERRORS = {
    "--check cannot be combined with render": ("--check 不能與 render 同用", "--check kann nicht mit render kombiniert werden", "--check と render は併用できません"),
    "render requires --output-dir": ("render 需要 --output-dir", "render erfordert --output-dir", "render には --output-dir が必要です"),
    "--output-dir is valid only for render": ("--output-dir 僅供 render 使用", "--output-dir ist nur für render gültig", "--output-dir は render でのみ有効です"),
    "a required declared path does not exist": ("必要的宣告路徑不存在", "Ein erforderlicher deklarierter Pfad fehlt", "必須の宣言済みパスが存在しません"),
    "a declared path or its parent is a symlink, junction or reparse point": ("宣告路徑或上層是 symlink、junction 或 reparse point", "Ein deklarierter Pfad oder sein Elternpfad ist ein symlink, junction oder reparse point", "宣言したパスまたは親が symlink、junction、reparse point です"),
    "a declared path has a non-directory parent": ("宣告路徑的上層不是目錄", "Ein deklarierter Pfad hat einen Elternpfad, der kein Verzeichnis ist", "宣言したパスの親がディレクトリではありません"),
    "a declared file path is not a regular file": ("宣告檔案路徑不是一般檔案", "Ein deklarierter Dateipfad ist keine reguläre Datei", "宣言したファイルパスが通常のファイルではありません"),
    "a declared directory path is not a directory": ("宣告目錄路徑不是目錄", "Ein deklarierter Verzeichnispfad ist kein Verzeichnis", "宣言したディレクトリパスがディレクトリではありません"),
    "network-share roots are refused": ("不接受網路共用根目錄", "Netzwerkfreigaben als Wurzel sind ausgeschlossen", "ネットワーク共有のルートは使用できません"),
    "home and filesystem-root scopes are refused": ("不接受家目錄或磁碟根目錄", "Home- und Dateisystemwurzel sind ausgeschlossen", "ホームとファイルシステムのルートは使用できません"),
    "project root has an excluded or sensitive ancestor": ("專案根目錄位於排除或敏感位置", "Die Projektwurzel liegt unter einem ausgeschlossenen oder sensiblen Pfad", "プロジェクトルートが除外対象または機密領域の配下にあります"),
    "manifest contains duplicate JSON keys": ("manifest 有重複 JSON key", "Das Manifest enthält doppelte JSON-Schlüssel", "manifest に重複した JSON キーがあります"),
    "manifest is not a regular file": ("manifest 不是一般檔案", "Das Manifest ist keine reguläre Datei", "manifest が通常のファイルではありません"),
    "manifest exceeds 1 MiB": ("manifest 超過 1 MiB", "Das Manifest überschreitet 1 MiB", "manifest が 1 MiB を超えています"),
    "manifest must be valid UTF-8 JSON without excessive nesting": ("manifest 須為有效 UTF-8 JSON，且不能過度巢狀", "Das Manifest muss gültiges UTF-8-JSON ohne übermäßige Verschachtelung sein", "manifest は過度にネストしていない有効な UTF-8 JSON である必要があります"),
    "schema_version must be integer 1": ("schema_version 須為整數 1", "schema_version muss die Ganzzahl 1 sein", "schema_version は整数 1 である必要があります"),
    "project.root must be '.'; the CLI --root sets the allowed directory": ("project.root 須為 '.'；用 --root 指定允許目錄", "project.root muss '.' sein; --root legt das freigegebene Verzeichnis fest", "project.root は '.' とし、許可ディレクトリを --root で指定してください"),
    "node IDs must be unique": ("node ID 不得重複", "Knoten-IDs müssen eindeutig sein", "ノード ID は一意である必要があります"),
    "node paths must be unique, including case-insensitive matches": ("node 路徑不得重複，含大小寫差異", "Knotenpfade müssen auch ohne Beachtung der Groß-/Kleinschreibung eindeutig sein", "ノードパスは大文字と小文字の違いも含めて重複できません"),
    "skill and workflow paths must be within their owning node": ("skill 與 workflow 路徑須在所屬節點內", "Skill- und Workflow-Pfade müssen im zuständigen Knoten liegen", "skill と workflow のパスは所属ノードの範囲内に置いてください"),
    "skill and workflow file paths must be unique": ("skill 與 workflow 檔案路徑不得重複", "Skill- und Workflow-Dateipfade müssen eindeutig sein", "skill と workflow のファイルパスは重複できません"),
    "node.sources must be a nonempty array with at most 100 paths": ("node.sources 須為非空陣列，最多 100 個路徑", "node.sources muss ein nicht leeres Array mit höchstens 100 Pfaden sein", "node.sources は最大 100 パスの空でない配列である必要があります"),
    "source paths must be within their owning node": ("source 路徑須在所屬節點內", "Quellpfade müssen im zuständigen Knoten liegen", "参照元パスは所属ノードの範囲内に置いてください"),
    "source paths must not repeat within a node": ("node 內的 source 路徑不得重複", "Quellpfade dürfen sich innerhalb eines Knotens nicht wiederholen", "ノード内で参照元パスを重複させないでください"),
    "node.dependencies must be an array of node IDs": ("node.dependencies 須為 node ID 陣列", "node.dependencies muss ein Array von Knoten-IDs sein", "node.dependencies はノード ID の配列である必要があります"),
    "node dependencies must not repeat": ("node 依賴不得重複", "Knotenabhängigkeiten dürfen sich nicht wiederholen", "ノードの依存関係を重複させないでください"),
    "every subproject must declare a parent ID": ("每個子專案都須宣告 parent ID", "Jedes Teilprojekt muss eine Eltern-ID angeben", "すべてのサブプロジェクトは親 ID を宣言してください"),
    "node.parent refers to an unknown ID": ("node.parent 指向未知 ID", "node.parent verweist auf eine unbekannte ID", "node.parent が不明な ID を参照しています"),
    "child paths must be strictly inside their parent path": ("子節點路徑須在 parent 路徑之內", "Untergeordnete Pfade müssen strikt innerhalb ihres Elternpfads liegen", "子のパスは親パスの内側に置いてください"),
    "parent relationships contain a cycle": ("parent 關係有循環", "Elternbeziehungen enthalten einen Zyklus", "親子関係に循環があります"),
    "every node must descend from the project root": ("每個 node 都須隸屬專案根節點", "Jeder Knoten muss von der Projektwurzel abstammen", "すべてのノードはプロジェクトルートの配下である必要があります"),
    "dependencies must name known IDs other than the node itself": ("依賴須為已知 ID，且不能是自己", "Abhängigkeiten müssen bekannte IDs außer der eigenen angeben", "依存先には自身以外の既知の ID を指定してください"),
    "workflow dependencies contain a cycle": ("workflow 依賴有循環", "Workflow-Abhängigkeiten enthalten einen Zyklus", "ワークフローの依存関係に循環があります"),
    "output directory already exists; choose a new explicit destination": ("輸出目錄已存在；請指定全新位置", "Das Ausgabeverzeichnis existiert bereits; ein neues Ziel angeben", "出力ディレクトリがすでに存在します。新規の出力先を指定してください"),
}
SUFFIX_ERRORS = {
    " must be an object": (" 須為物件", " muss ein Objekt sein", " はオブジェクトである必要があります"),
    " has missing or unknown fields": (" 有缺少或未知欄位", " hat fehlende oder unbekannte Felder", " に不足または不明なフィールドがあります"),
    " contains control, surrogate or formatting characters": (" 含控制、surrogate 或格式字元", " enthält Steuer-, Surrogat- oder Formatierungszeichen", " に制御文字、サロゲート、書式制御文字が含まれています"),
    " must match [a-z][a-z0-9-]{0,63}": (" 須符合 [a-z][a-z0-9-]{0,63}", " muss [a-z][a-z0-9-]{0,63} entsprechen", " は [a-z][a-z0-9-]{0,63} に一致する必要があります"),
    " must be a plain project-relative POSIX path": (" 須為單純的專案相對 POSIX 路徑", " muss ein einfacher projektbezogener POSIX-Pfad sein", " は単純なプロジェクト相対 POSIX パスである必要があります"),
    " contains an empty, traversal or ambiguous segment": (" 含空白、越界或模糊路徑段", " enthält ein leeres, ausbrechendes oder mehrdeutiges Segment", " に空、範囲外移動、曖昧なパス要素が含まれています"),
    " contains a reserved device name": (" 含保留的裝置名稱", " enthält einen reservierten Gerätenamen", " に予約済みデバイス名が含まれています"),
    " points to an excluded or sensitive path": (" 指向排除或敏感位置", " verweist auf einen ausgeschlossenen oder sensiblen Pfad", " が除外対象または機密領域を指しています"),
}


def translate_error(message, language):
    if language == "en":
        return message
    index = {"zh-TW": 0, "de": 1, "ja": 2}[language]
    if message in FIXED_ERRORS:
        return FIXED_ERRORS[message][index]
    for suffix, translations in SUFFIX_ERRORS.items():
        if message.endswith(suffix):
            return message[:-len(suffix)] + translations[index]
    match = re.fullmatch(r"(.+) must be a nonempty string \(at most (\d+) characters\)", message)
    if match:
        templates = ("{field} 須為非空字串，最多 {limit} 字元", "{field} muss eine nicht leere Zeichenkette mit höchstens {limit} Zeichen sein", "{field} は最大 {limit} 文字の空でない文字列である必要があります")
        return templates[index].format(field=match.group(1), limit=match.group(2))
    match = re.fullmatch(r"subprojects must be an array with fewer than (\d+) items", message)
    if match:
        templates = ("subprojects 須為少於 {limit} 項的陣列", "subprojects muss ein Array mit weniger als {limit} Einträgen sein", "subprojects は {limit} 項目未満の配列である必要があります")
        return templates[index].format(limit=match.group(1))
    match = re.fullmatch(r"filesystem error \(errno (\d+)\)", message)
    if match:
        templates = ("檔案系統錯誤（errno {code}）", "Dateisystemfehler (errno {code})", "ファイルシステムエラー（errno {code}）")
        return templates[index].format(code=match.group(1))
    return message
