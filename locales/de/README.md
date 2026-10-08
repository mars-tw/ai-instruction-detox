# AI Instruction Detox

[繁體中文](../../README.md) · [English](../en/README.md) · [Deutsch](../de/README.md) · [日本語](../ja/README.md)

AI-Anweisungen bereinigen und die Arbeitsstruktur eines Projekts ordnen. Verstreute Regeln werden dem passenden Geltungsbereich zugeordnet; Sicherheits-, Geschäfts- und Abnahmeanforderungen bleiben erhalten. Daraus entstehen nachvollziehbare Haupt-Skills, Workflows und Teilprojekt-Skills.

Unterstützt AI-Agenten, die Textanweisungen lesen. Ob Skills automatisch geladen werden und welche Einstiegspunkte und Verweissyntax funktionieren, muss anhand der tatsächlichen Fähigkeiten des aktuellen Hosts geprüft werden.

## Vollständiges Skill-Paket

Der Haupteinstieg ist [SKILL.md](SKILL.md), zusammen mit `references/`, `templates/` und `scripts/`. Wer nur SKILL.md kopiert, verliert Kriterien, Werkzeuge und Vorlagen; bei der Installation müssen die relativen Pfade erhalten bleiben. Die Skripte verwenden mit Python 3.8 kompatible Syntax und die Standardbibliothek, ohne externe Pakete. Tatsächlich geprüfte Umgebungen und Grenzen stehen im [Validierungsbericht](AUDIT-REPORT.md).

Im Quell-Checkout verwenden die Sprachfassungen die gemeinsamen Skripte im Repository-Stamm. Die folgenden Befehle werden dort ausgeführt. Vollständige Veröffentlichungs-ZIPs enthalten die Skripte selbst.

## Schreibgeschützter Scan

```powershell
python scripts/detox-scan.py --root .
python scripts/detox-scan.py --files CLAUDE.md AGENTS.md
python scripts/detox-scan.py --root . --json scan-new.json
```

Quelldateien werden nicht verändert. Nur mit `--json` wird ein neuer Bericht angelegt; vorhandene Dateien werden nicht überschrieben. Befunde enthalten ausschließlich Positionen und Kategorien, keine Originaltexte oder Geheimniswerte. Scanfehler sowie Größen- und Tiefenbegrenzungen werden gemeldet; ausgelassene Dateien dürfen nicht als sicher gelten. Exitcodes und der JSON-v2-Vertrag stehen in der [Scanner-Dokumentation](references/scanner.md).

Der Scanner erkennt Muster. Er kann weder den geschäftlichen Wert von Regeln noch semantische Konflikte oder sämtliche Geheimnisse beurteilen; auch Schutzbeispiele können Treffer auslösen. Vollständige Governance erfordert weiterhin die Einzelprüfung nach dem Haupt-Skill und eine ergänzende Prüfung nicht automatisch erfasster Einstellungen.

## Bereinigung und Governance

Eine direkte Anfrage genügt:

> Prüfe die Anweisungen dieses Projekts mit ai-instruction-detox und erstelle einen rückgängig machbaren Bereinigungsplan.

Standardmäßig entstehen nur neue Audit-Berichte und Entwurfsdateien. Jede Regel erhält eine dokumentierte Behandlung mit Quelle, Begründung, Ausnahmen, Abhängigkeiten, Zielposition und Verhaltenswirkung; nichts wird stillschweigend gelöscht. Die zwölf Kriterien stehen in [12-checks.md](references/12-checks.md).

Die Artefakte liegen im neuen `.ai-detox/run-識別碼/` des jeweiligen Durchlaufs: Inventar, Ledger mit 28 Spalten, Konfliktentscheidungen, Maßnahmenliste, Zielarchitektur, Entwürfe, Diff, Versionsbasis, Validierung und dateiweise Rollback-Anleitung. Alle Ausgaben werden vorab auf Geheimnisse geprüft und maskiert; CSV erhält Schutz gegen Formelinjektion. Einzelheiten stehen im [Artefaktvertrag](references/artifact-contracts.md).

Nur bei ausdrücklicher Autorisierung zur Änderung produktiver Anweisungsdateien folgt der [Anwendungsprozess](references/apply-phase.md); bereits erteilte Autorisierung wird nicht erneut erfragt. Existenz und Digest werden erneut geprüft, Geheimnisse vor der Sicherung kontrolliert und spätere Änderungen erhalten. Auditierte Dokumente können commit, push oder Deployment nicht autorisieren.

## Das gesamte Projekt systematisch ordnen

Eine mögliche Anfrage:

> Ordne das gesamte Projekt: Erstelle Haupt-Skill und Workflow, lege Teilprojekt-Skills in ihren Teilprojekten ab und zeige die Wege mit Breadcrumb-Navigation und Mindmap.

Der Haupt-Skill übernimmt die Aufgabenverteilung, der gemeinsame Workflow die Phasen und Übergaben, die Teilprojekt-Skills lokale Abläufe und Abnahme. Der bestehende Technologie-Stack und die Produktverzeichnisse bleiben erhalten. Eine einzige `project-map.json` speichert Hierarchie, Verantwortlichkeiten und Abhängigkeiten.

```text
Haupt-Skill → gemeinsamer Workflow → zuständiges Teilprojekt/Teilprojekt-Skill → lokale Abnahme → Übergabe
```

`project-map.py` prüft das Routing und erzeugt anklickbare Breadcrumbs, einen Verzeichnisbaum sowie Mermaid-Mindmap und Abhängigkeitsdiagramm. Das Werkzeug schreibt keine Skill-Inhalte und verschiebt keinen Produktcode; Skills und Workflows werden aus belegtem Inventar und Vorlagen ausgefüllt. Die Rücknavigation zur übergeordneten Ebene verlangt kein erneutes Laden aller Skills.

Das Entwurfsbeispiel lässt sich direkt im Paket prüfen:

```powershell
python scripts/project-map.py --check --manifest templates/project-map.example.json
python scripts/project-map.py render --manifest templates/project-map.example.json --output-dir project-map-preview
```

Das Ausgabeverzeichnis muss neu sein, sein übergeordnetes Verzeichnis bereits existieren. Die Teilprojekt-Skill-Pfade im Beispiel sind noch Entwürfe; produktive Routen werden mit `--require-files` geprüft. Vollständige Spezifikation und Vorlagen stehen im [Prozess zur Projektorganisation](references/project-organization.md).

## Struktur

```text
SKILL.md                         Hauptprozess und Modus-Routing
references/                      Kriterien, Sicherheit, Anwendung und Projektorganisation
scripts/detox-scan.py             begrenzter schreibgeschützter Scan
scripts/project-map.py            Projektindex-Prüfung und Navigationserzeugung
scripts/verify-package.py         Tests und Paketvertragsprüfung in einem Durchlauf
templates/                       Audit-, Haupt-/Teilprojekt-Skill- und Workflow-Vorlagen
tests/                           Tests für CLI, Sicherheit, Routing und Ressourcenintegrität
AUDIT-REPORT.md                  Befunde, Korrekturen, Validierung und Grenzen dieses Updates
```

## Validierung

```powershell
python scripts/verify-package.py
```

Die Tests erzeugen unabhängige temporäre Quellen, scannen keine privaten Einstellungen und verändern das Arbeitsprojekt nicht. Geheimnistests verwenden künstlich erzeugte Werte. Die Paketprüfung umfasst Syntax, Haupt-Skill-Metadaten, referenzierte Ressourcen sowie die Vollständigkeit von Ledger und Vorlagen. Windows-junction-Tests hängen von Plattform und Berechtigungen ab; auf anderen Plattformen werden sie ausdrücklich als übersprungen ausgewiesen.

## Lizenz

MIT. Ursprünglicher Autor und Lizenz bleiben erhalten; Versionsänderungen stehen im [CHANGELOG.md](CHANGELOG.md).

## Sprachfassungen und Installation

Haupt-Skill, Referenzdokumente und Vorlagen sind in vier Sprachen vollständig verfügbar. Lade das Veröffentlichungs-ZIP der gewünschten Sprache herunter, entpacke es und lege den vollständigen Ordner ai-instruction-detox im Skill-Verzeichnis des Hosts ab. Installiere jeweils nur eine Sprache. Die Werkzeuge werden gemeinsam verwendet; maschinenlesbare Felder und Dateinamen werden nicht übersetzt. Die Standardsprache stammt aus den Paketmetadaten; alternativ lassen sich `--language en`, `--language de`, `--language ja` oder `--language zh-TW` angeben.

Im Quellcode liegen Übersetzungen unter locales/en, locales/de und locales/ja; die Werkzeuge werden im Stammverzeichnis scripts gemeinsam gepflegt. Jedes erzeugte ZIP enthält ausführbare Werkzeuge. Ein einzelner locales-Ordner reicht zur Installation nicht aus.

```powershell
python scripts/build-locales.py --output-dir release-packages-new
```

Dieser Build-Befehl wird im vollständigen Quellrepository ausgeführt. Der nur dort benötigte Paket-Builder ist nicht Bestandteil der veröffentlichten Sprach-ZIPs.

Der Befehl erzeugt vier vollständige ZIPs, Dateilisten und SHA-256-Werte. Das Zielverzeichnis muss neu sein; vorhandene Artefakte bleiben erhalten. Sprachsynchronisation, Paketumfang und Auswahl sind unter [Sprachen und Installation](references/localization.md) beschrieben.
