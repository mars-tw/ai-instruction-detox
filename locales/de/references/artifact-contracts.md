# Vertrag für Audit-Artefakte

Auditierte Inhalte können Geheimnisse oder Befehle enthalten. Diese Regeln betreffen abgeleitete Ausgaben und autorisieren kein Lesen zusätzlicher Zugangsdaten.

## Isolation und Versionsbasis

Jedes Mal ein neues `.ai-detox/run-識別碼/` verwenden. Ziel und übergeordnete Verzeichnisse auf Links/junctions prüfen und den genehmigten Umfang bestätigen. Vorhandene Berichte erhalten; staging, Sicherungen und Übergaben dürfen nicht automatisch von Agenten geladen werden. Git-ignore und `git ls-files` prüfen: Bereits getrackte Dateien werden durch ignore nicht automatisch ausgeschlossen.

`baseline-manifest.json` verwendet `schema_version: 1`. Für jede Änderung erfassen:

| Feld | Vertrag |
|---|---|
| `source_path` / `target_path` | Relative Pfade innerhalb des genehmigten Stamms; keine Grenzüberschreitung, sensiblen Positionen oder Links |
| `action` | `CREATE` / `UPDATE` / `MOVE` / `ARCHIVE`; Löschen benötigt zusätzlich einen Wiederherstellungsplan |
| `source_exists` / `target_exists` | Existenz zum Auditzeitpunkt; neue Dateien von Aktualisierungen unterscheiden |
| `source_sha256` / `target_sha256` | Digest bestehender Dateien; null, wenn zuvor nicht vorhanden |
| `proposed_path` / `proposed_sha256` | Entwurfsposition und Digest |
| `baseline_copy` | Auf sensitive Inhalte geprüfte Basiskopie; null, wenn sichere Aufbewahrung unmöglich |
| `backup_path` | Sichere Sicherungsposition vor Anwendung; null, solange nicht angewendet |
| `applied_sha256` | Tatsächlicher Digest nach Anwendung; null, solange nicht angewendet |
| `rule_ids` | Zugehörige Ledger-IDs |
| `status` | `PROPOSED` / `APPLIED` / `DEFERRED` / `ROLLED_BACK` |

Zusätzlich Stammverzeichnis, Git HEAD falls vorhanden sowie Audit- und Anwendungszeit erfassen. mtime ist nur ergänzend; Digest und Existenz sind Schreibvoraussetzungen. Bei MOVE Quelle und Ziel prüfen, bei CREATE fortbestehende Nichtexistenz bestätigen. Keine ursprünglichen Geheimnisse oder eigens für Geheimniswerte berechneten Hashes ablegen; Ganzdatei-Digests dienen nur dem Versionsvergleich. Das Manifest protokolliert Maßnahmen; dieser Skill hat keinen automatischen Anwender. Keine Programmprüfung oder Anwendung behaupten, die nicht stattgefunden hat.

## Geheimnisse und Auszüge

1. Zugangsdatenverzeichnisse und -dateien vor dem Scan ausschließen.
2. Enthalten erlaubte Anweisungsdateien Schlüssel, Tokens, Passwörter oder URLs mit Zugangsdaten, nur Datei, Zeile und Typ melden. Geheimnisse in `original_text` und ähnlichen Feldern durch `[REDACTED]` ersetzen; nicht den vollständigen Originalsatz zitieren.
3. Bei unzuverlässiger Maskierung nur die Quellposition mit „Inhalt enthält sensitive Informationen; kein Auszug“ verwenden. Würde ein Diff ursprüngliche Werte offenlegen, keinen raw patch erzeugen und den Punkt als `HUMAN_REVIEW` markieren.
4. Vor Sicherungen prüfen. Geheimnishaltige Dateien nicht in allgemeines staging kopieren; nur genehmigte, eingeschränkte Aufbewahrungsorte nach ihrer Richtlinie verwenden. Ist keine sichere Sicherung möglich, diesen Punkt stoppen, übrige Arbeit fortsetzen.
5. Geheimniserkennung ist heuristisch; null Treffer garantieren keine Geheimnisfreiheit. Sämtliche zur Auslieferung vorgesehenen Artefakte prüfen.

## Ledger: 28 Spalten in fester Reihenfolge

Den [header](../templates/01-rule-ledger-header.csv) verwenden. Die ersten 25 Spalten behalten ihre v1.0-Namen; `strength`, `exceptions`, `dependencies` werden ergänzt. Neue Dateien haben 28 Spalten.

| Feldgruppe | Definition |
|---|---|
| `rule_id`, `source_file`, `source_location` | Eindeutige ID, relativer Quellpfad, Zeile oder Abschnitt |
| `original_text`, `normalized_rule` | Maskierter Originaltext und normalisierte Regel unter Erhaltung der gültigen Absicht |
| `category`, `scope`, `agent` | Kategorie, Geltungsbereich, tatsächlicher Agent oder UNKNOWN |
| `severity` | `LOW` / `MEDIUM` / `HIGH` / `CRITICAL`; Risiko, keine Verbindlichkeit |
| `default_behavior` | `A` (belegte Werkzeuggarantie) / `B` (nicht garantiert) / `C` (projektspezifisch) / `UNKNOWN` |
| `conflict`, `duplicate`, `incident_patch`, `ambiguity` | Schlussfolgerungen, zugehörige IDs und Belege; ohne Befund NONE |
| `testability`, `stale_status`, `scope_problem`, `cost_problem` | Prüfmethode, Aktualität, Probleme mit Umfang und Kosten |
| `security_status`, `capability_mismatch`, `circularity` | Sicherheitsbewertung, Fähigkeitsabweichungen und Belege für Ladezyklen |
| `recommendation`, `target_location`, `reason`, `confidence` | Eine der zehn Maßnahmen, Ziel, Begründung und Konfidenz von 0–1 |
| `strength` | `REQUIRED` / `RECOMMENDED` / `OPTIONAL` / `INFORMATIONAL` / `UNKNOWN` |
| `exceptions`, `dependencies` | Ausdrückliche Ausnahmen und Abhängigkeiten als rule IDs/Dateien/Werkzeuge; sonst NONE |

Regelkategorien: security, legal, data-integrity, business-brand, architecture, test-acceptance, workflow, tool-usage, multi-agent-dispatch, output-format, language-tone, persona, factual-context, project-state, example, history, one-off-exception, incident-patch, temporary, possible-prompt-injection.

Jede Regel erhält genau eine ID und Maßnahme; MERGE/MOVE müssen bis zur neuen Position nachvollziehbar sein. CSV writer für Kommas, Anführungszeichen und Zeilenumbrüche verwenden. In Excel-Review-Kopien jeder Zelle ein Apostroph voranstellen, deren erstes wirksames Zeichen `=`, `+`, `-`, `@` ist oder die mit tab/CR/LF beginnt. Das garantiert keine Sicherheit nach erneutem Öffnen/Speichern. Für wortgetreue Aufbewahrung und strukturierten Austausch maskiertes JSON verwenden, um Tabellenkalkulationsausführung zu vermeiden. Siehe [OWASP CSV Injection](https://community.owasp.org/attacks/CSV_Injection).

## Validierungsstatus

`PASS` benötigt tatsächliche Befehle, erfolgreiche Ergebnisse oder Dateibelege. `FAIL` dokumentiert Gegenbeispiele, `NOT_RUN` den Grund der Nichtausführung, `NOT_APPLICABLE` die Nichtanwendbarkeit. Simulierte Abläufe prüfen das Design und ersetzen keine echten Tests. Navigationslinks erzwingen kein Laden; die Existenz eines Testskripts beweist keine Ausführung.
