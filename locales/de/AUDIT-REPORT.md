# AI Instruction Detox 1.1.0: Update-Validierung

Datum: 2026-10-08 (Asia/Taipei). Ursprüngliche Quelle: [mars-tw/ai-instruction-detox](https://github.com/mars-tw/ai-instruction-detox), Basis-commit: `0b4ce515f209f3fb5cf82522d904f15999b69a1d`.

Das lokale Skill-Paket wurde aktualisiert: Scanner und Governance-Verträge korrigiert und die Gesamtorganisation von Projekten ergänzt. Vollständige Prüfungen und Regressionstests bestanden. Heuristische Scans und begrenzte Simulationen gelten nicht als umfassende Sicherheitsgarantie. Während des 1.1.0-Basisaudits erfolgten weder commit, push noch Deployment; die spätere Veröffentlichung von 1.2.0 auf GitHub folgt ausdrücklicher Benutzerautorisierung. Ursprünglicher Autor und MIT-Lizenz bleiben erhalten.

## Behobene Probleme

Die Positionen beziehen sich auf Zeilen des ursprünglichen Basis-commits; die neuen Dateien wurden neu gegliedert.

| ID / Schweregrad | Ursprünglicher Beleg | Problem und Wirkung | Korrektur |
|---|---|---|---|
| S01 / Hoch | `scripts/detox-scan.py:157–159,166,174,194` | Injection, unklare Regeln, absolute Wörter und Duplikate enthielten Originalauszüge und konnten Geheimnisse derselben Zeile nach stdout/JSON übertragen | Befunde auf Position/Kategorie umgestellt; alle Felder und Pfadmetadaten gegen Weitergabe erkannter Geheimnisse geschützt |
| S02 / Hoch | `scripts/detox-scan.py:86–97` | symlinks/Windows junctions/sensitive Verzeichnisse waren nicht isoliert; auch ausdrückliche Eingaben konnten über Links lesen | lstat-/reparse-Prüfung jeder Vorfahrenebene; sensitive Verzeichnisse, Dateien sowie Quell-/Ausgabepositionen ausgeschlossen |
| S03 / Mittel | `scripts/detox-scan.py:100–105` | Lesefehler wurden zu leerem Text; ausgelassene/abgeschnittene Scans konnten als Erfolg gelten | selected/scanned getrennt, errors/skipped erhalten, Teilscan mit Exitcode 3 und Ressourcenlimits |
| S04 / Mittel | `scripts/detox-scan.py:177–183` | Nur gegenseitige Zwei-Knoten-Verweise gefunden; längere und Selbstzyklen übersehen | Nicht rekursive stark zusammenhängende Komponenten; Zyklus mit 1.200 Knoten ohne Call-Stack-Überlauf geprüft |
| S05 / Mittel | `scripts/detox-scan.py:74–78,134–144` | Übliche references-Pfade, Markdown-/Leerzeichenpfade fehlten; Parsing und Grenzen unklar | URLs, Anker und lokale Pfade getrennt; nur gewählten Umfang prüfen, keine Erweiterung des Inhaltslesens durch Verweise |
| S06 / Mittel | `scripts/detox-scan.py:191` | Erste 200 Zeichen als Duplikatidentität fassten unterschiedliche Regeln mit gleichem Anfang falsch zusammen | Vollständige normalisierte Absätze vergleichen; nur Quellpositionen ausgeben |
| S07 / Hoch | `scripts/detox-scan.py:266–268` | JSON-Schreibmodus w überschrieb Quellen oder vorhandene Berichte | exclusive create, Ziel-/Vorfahrenprüfung, Überschreiben und sensitive Zieldateien abgelehnt; CLI-Modi schließen einander aus |
| G01 / Hoch | `SKILL.md:93` | Ledger verlangte Originaltext ohne Schutz vor eingemischten Geheimnissen; CSV konnte Formeln ausführen | Einheitlicher Maskierungsvertrag für abgeleitete Ausgaben, CSV-Formelschutz und Empfehlung zum JSON-Austausch |
| G02 / Hoch | `references/apply-phase.md:45–59,85` | Geheimnisprüfung erst nach Sicherung; ungeprüfte Ausführung auditierter Projektskripte möglich | Vor Sicherung prüfen; ohne sichere Aufbewahrung Punkt zurückstellen; Skripte/hooks zuerst prüfen und dann nach Aufgabenautorisierung ausführen |
| G03 / Hoch | `references/apply-phase.md:26–30`, `templates/06-rollback.template.md:16` | Kein Basissnapshot-Vertrag; Rollback konnte spätere Änderungen überschreiben, CREATE/MOVE fehlten | Existenz, SHA-256 sowie Entwurfs-/Anwendungs-Digests ergänzt; Drei-Wege-Vergleich pro Punkt, neue Dateien zurücknehmen und Verschiebungen wiederherstellen |
| G04 / Mittel | `SKILL.md:93–94,189–201` | Verbindlichkeit, Ausnahmen und Abhängigkeiten fehlten im Ledger; Vorlagen 02–05 fehlten | Ursprüngliche 25 Spalten erhalten und drei ergänzt; Vorlagen 00–06 und baseline vervollständigt |
| G05 / Mittel | `README.md:38,99`, `SKILL.md` frontmatter | Einzelner Haupt-Skill verlor Abhängigkeiten; „keine Schreibvorgänge“ widersprach Berichten; metadata entsprach nicht dem aktuellen Validator | Vollständige Paketnutzung erläutert, schreibgeschützte Quellen von Artefaktschreiben getrennt, version/author nach metadata verschoben |
| G06 / Mittel | `references/12-checks.md:23,215–218`, `references/multi-agent-review.md:85` | Ehrlichkeit als Plattformgarantie behandelt, Zeitplanung pauschal unmöglich genannt, Aufspaltung maßgeblicher Quellen über Sessions hinweg übersehen | Fähigkeiten anhand offizieller/tatsächlicher Belege bewerten, Navigation/Laden unterscheiden, Kopien über Agenten hinweg weiter auf Versionsaufspaltung prüfen |

Technische Grundlage der Sicherheitskorrekturen sind [Pythons Regeln zum Dateidurchlauf](https://docs.python.org/3.8/library/os.html#os.walk), [Windows reparse attributes](https://docs.python.org/3.12/library/stat.html#stat.FILE_ATTRIBUTE_REPARSE_POINT) und [OWASP CSV Injection](https://community.owasp.org/attacks/CSV_Injection). Dieses Projekt ist eine Standardbibliothek-CLI; keine sachfremde Webframework-Checkliste wurde angewendet.

## Ergänzung: Gesamtorganisation von Projekten

Der Haupt-Skill erhält das Routing `ORGANIZE_PROJECT`. Einzelheiten stehen in [project-organization.md](references/project-organization.md).

1. Haupt- und Teilprojekte anhand vorhandener Verantwortung, Pfade, Arbeitsdokumente und Abnahmequellen inventarisieren.
2. Haupt-Skill und gemeinsamen Workflow erstellen; Teilprojekt-Skills und lokale Abläufe in ihren Teilprojekten ablegen.
3. Knoten, Eltern-Kind-Beziehungen, Skills, Workflows, owner, Quellen und Abhängigkeiten in einer einzigen `project-map.json` speichern.
4. Nach Prüfung durch `project-map.py` Breadcrumb-Markdown, Verzeichnisbaum, Mermaid-Mindmap und Abhängigkeitsdiagramm erzeugen.
5. Entwürfe im isolierten run prüfen und nach produktiver Anwendung Routen strikt kontrollieren, ohne Produktcode zu verschieben.

Das Werkzeug lehnt falsche Schemas/Typen, doppelte IDs/Pfade, unbekannte Eltern/Abhängigkeiten, Grenzüberschreitungen, sensitive Positionen, Links und Abhängigkeitszyklen ab. Sämtliche Navigation stammt aus einem Index; Rücklinks verlangen kein wiederholtes Laden. Haupt-/Teilprojekt-Skill- und Workflow-Vorlagen enthalten Anforderungen für Ein-/Ausgaben, Verantwortung, Abnahme, Stopp, Übergabe und Rollback.

## Tatsächliche Validierung

Umgebung: Windows, Python 3.12.10, Git 2.53.0.windows.3.

| Prüfung | Ergebnis | Beleg |
|---|---|---|
| `python -W error scripts/verify-package.py` | PASS | 80 tests, 0 failures, 0 skipped |
| Scanner | PASS | 38 tests, einschließlich Geheimnisausgaben, echter symlinks/Windows junctions, CLI, Abdeckungsfehler und langer Zyklen |
| Project map | PASS | 39 tests, einschließlich dreistufiger fixture, striktem Routing, schreibgeschütztem Zugriff, Überschreibschutz, Escaping und falschen Eingaben |
| Package contracts | PASS | 3 tests, einschließlich aller Ressourcenlinks von Haupt-Skill/references, vollständiger Vorlagen und Migration auf 28 Spalten |
| Python 3.8 grammar | PASS | ast.parse prüft kompatible Syntax in scripts/tests; kein tatsächlicher Python-3.8-runtime-Lauf |
| Offizielles lokales skill-creator quick_validate | PASS | `Skill is valid!`; kompatibles frontmatter und Haupteinstieg |
| `git diff --check` | PASS | Keine whitespace errors; Git-Hinweise zu LF/CRLF ändern dieses Ergebnis nicht |
| Unabhängige Vorwärtsvalidierung | PASS (Governance-Entwurf) | frontend/backend-fixture erzeugt vollständige Haupt-/Teilprojekt-Skills, Workflows, 28-Spalten-Ledger, 00–06, baseline und patch |
| Erhaltung der Vorwärtsvalidierungsquellen | PASS | Digests von 11 Originaldateien und Git status unverändert; zwei vorhandene nicht committete Produktänderungen erhalten |
| Entwurfs-Routing und Navigation | PASS | Isoliertes Overlay besteht strikte Prüfung; vier Navigationen nach zweimaliger Erzeugung byte-identisch, Markdown-Links auflösbar |
| Entwurfs-patch | PASS | `git apply --check` in isolierter fixture bestanden; keine tatsächliche Anwendung |
| Echte Produkttests/produktive Anwendung/Rollback | NOT_RUN | Nur Skill-Paket aktualisiert; keine Governance oder Änderungen anderer Produktprojekte des Benutzers |

Ausführung, Dokumentreview und Vorwärtsbewertung verwendeten unabhängige Agentenkontexte innerhalb des Hosts mit getrennten Arbeitsbereichen. Danach las der Supervisor Ergebnisse zurück und führte tatsächliche Validierungen aus. Dies ist keine Validierung durch unterschiedliche Modelle. Kein externer Modell-Roundtrip wurde als Auditbeleg verwendet.

## Korrekturen aus dem Gegenreview der neuen Module

- Die Mermaid-ID end kollidiert mit [offizieller reservierter Syntax](https://mermaid.js.org/syntax/flowchart.html). Sicheres Präfix node_ ergänzt; Manifest-ID und Navigationsanker bleiben erhalten.
- Ausschlüsse für .envrc und credentials.* ergänzt; gleiche Grenzen für Quelle, Manifest, root und Ausgabepfade.
- Markdown-Navigation enthält direkt Baum, Mindmap und Abhängigkeitsdiagramm aus derselben Quelle; die .mmd-Dateien müssen nicht separat gesucht werden.

## Versionskompatibilität und Grenzen

- JSON schema v2 entfernt raw snippet/text/ref; Zyklen und Duplikate verwenden ebenfalls Positionsstrukturen. Konsumenten müssen aktualisiert werden.
- Ledger von 25 auf 28 Spalten; alte Dateien können `strength`, `exceptions`, `dependencies` ergänzen. Keine Ausnahmen erfinden.
- Geheimnis-/Injection-Erkennung und Pfadparsing sind heuristisch und decken nicht jedes Format ab; Treffer im Kontext beurteilen.
- `complete` bezeichnet vollständiges Lesen des gewählten Umfangs, kein vollständiges Projektinventar oder Sicherheitsnachweis.
- Das Navigationswerkzeug schreibt keine Skill-Inhalte und prüft keine tatsächlichen owner, geschäftliche Vollständigkeit oder unbekannten Geheimnisse im Manifest.
- Andere Python-Versionen/Betriebssysteme, echte Anfängernutzung sowie Governance-Anwendung und Rollback wurden noch nicht tatsächlich geprüft und gelten nicht als bestanden.
- Pfadprüfungen sind keine Betriebssystem-Sandbox; kein garantierter Schutz gegen bösartige parallele Ersetzung übergeordneter Verzeichnisse.

## Protokoll der chinesischen Textkorrekturen

| Ursprünglicher Satz/Ansatz | Grund | Ersatz |
|---|---|---|
| Keine Schreibvorgänge während des Audits | Widerspricht neuen Berichten/Entwurfsdateien | Audit ändert keine Quellen; neue isolierte Artefakte nur im angegebenen Modus |
| SKILL.md an den AI-Agenten geben | Referenzierte Kriterien und Skripte fehlen | Vollständiges Skill-Paket und relative Pfade erhalten |
| Ehrlich antworten → Plattform garantiert es → löschbar | Richtlinienerwartung als technisch durchsetzbare Verhaltensgarantie behandelt | Ohne Garantiebeleg Kategorie B behalten |
| Duplikat nur bei gleichzeitigem Laden in einer Session | Aufspaltung maßgeblicher Regeln zwischen Agenten übersehen | Nach Umfang und maßgeblicher Quelle beurteilen; auch Kopien über Sessions hinweg prüfen |

Die übrigen wesentlichen Änderungen betreffen technische Verträge und neue Funktionen. Ursprünglicher Autor, Daten, Lizenz und englische Kennungen bleiben erhalten.
