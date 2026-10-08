# Checkliste für das Dateiinventar

Mit einer **ausdrücklichen Positivliste** suchen; nicht rekursiv das gesamte Benutzerverzeichnis scannen. Tatsächliche Dateinamen können abweichen; projektspezifisch ergänzen.

---

## A. Hauptdateien für Agentenanweisungen

```
CLAUDE.md            CLAUDE.local.md
AGENTS.md            CODEX.md
GEMINI.md            QWEN.md
CLAUDE.md / AGENTS.md in den einzelnen Unterverzeichnissen
Weitere Dateien vom Typ Agent Instructions
```

## B. Agenten-Konfigurationsverzeichnisse

```
.claude/   .codex/   .agents/   .ai/
.github/   .cursor/  .vscode/   .gemini/  .qwen/  .grok/
```

## C. Regeln, Skills und Prompts

```
skills/  skill/  prompts/  prompt/  instructions/
rules/   policies/  workflows/  agents/  personas/
templates/  hooks/
```

## D. Kontext- und Wissensdateien

```
context/  contexts/  memory/  memories/  knowledge/
handoff/  handoffs/  state/  baselines/
specifications/  specs/
```

**Alle** Textdateien in Verzeichnissen wie `context/` prüfen; große Dateien können abschnittsweise gelesen werden.

## E. Engineering-Dateien mit möglichen impliziten Regeln

```
README*        CONTRIBUTING*   DEVELOPMENT*
ARCHITECTURE*  SECURITY*
package.json scripts   Makefile   Taskfile
CI/CD-Konfiguration     Git hooks     lint-Konfiguration    test-Konfiguration
MCP-Konfiguration       tool permission-Konfiguration       schema
deployment scripts        automatisierte Workflows
```

README, Dokumentation und Code müssen nicht pauschal vollständig gelesen werden. Aufnehmen, sobald mindestens eine Bedingung zutrifft: durch eine Hauptanweisungsdatei referenziert, enthält AI-Betriebsanforderungen, Entwicklungsabläufe, Deployment-/Test-/Abnahmeregeln oder Einschränkungen für Rollen, Berechtigungen und Werkzeuge.

## F. Häufig übersehene Kanäle der Ausführungsebene ⚠️

Diese sind besonders gefährlich: Sie können **unbeaufsichtigt Anweisungen in eine Session injizieren**.

```
Zeitplan-/Automationsdefinitionen (automations/, cron-Definitionen, scheduled tasks)
Agenten-Erinnerungsdateien (memories/, automatisch injizierte MEMORY.md)
AGENTS.md auf Projektebene (gleicher Name wie global, anderer Inhalt)
Installierte/bereitgestellte plugin-Kopien (möglicherweise nicht mit assets synchron)
subagent-Definitionen (agents/*.md)
Von dispatcher/orchestrator injizierter runtime contract
```

**Praktische Lehre:** Nach Änderung der maßgeblichen Richtlinie wurden alte Regeln aus `memories/` automatisch injiziert und überschrieben die neue Richtlinie vollständig. Erinnerungsdateien gehören in die Governance.

---

## Strukturelle Fallen, die geprüft werden müssen

| Falle | Prüfmethode |
|---|---|
| Zwei gleichnamige Dateien | Beide Dateien mit `diff` vergleichen; beobachtet wurden 477 Zeilen mit nur zwei abweichenden Titelzeilen |
| symlink/junction als Duplikat fehlklassifiziert | Zuerst LinkType prüfen; **Löschen über eine junction zerstört die echte Quelle** |
| Verwaiste Verweise | Sämtliche Dateipfade extrahieren und einzeln mit `test -e` prüfen |
| Zyklische Verweise | Gerichteten „wer liest wen“-Graphen auf Zyklen prüfen |
| Alte Sicherungen werden weiter geladen | Prüfen, ob `backups/`, `archive/`, `old/`, `*.bak` im Suchbereich des Agenten liegen |
| Alte Verweise nach Verschieben | Nach alten Pfadzeichenfolgen suchen |
| Skill referenziert fehlende Datei | Alle relativen Pfade im Skill auflösen |
| Bereitgestellte Kopien und Quellen nicht synchron | Hashes von assets und installierten Positionen vergleichen |

---

## Ausschlussliste

```
.git  node_modules  vendor  dist  build  coverage  cache  tmp
Binärdateien  große Modelldateien  generierte Ausgaben  Verzeichnisse für Zugangsdaten und Schlüssel (Inhalte)
```

Bei Zugangsdatenverzeichnissen **nur Existenz und Position dokumentieren; keine Werte lesen oder ausgeben**.

---

## Pro Datei zu erfassende Angaben

```
Dateipfad
Dateityp
Hauptzweck
Zuständige Agenten
Geltungsbereich
Automatisches Laden          ← entscheidend für die tatsächliche Wirkung
Mögliche Ladepriorität
Von anderen Dateien referenziert?
Referenziert andere Dateien?
Existieren doppelte Versionen?
Möglicherweise veraltet?
Sensitive Informationen (nur Position)?
Verdächtige Prompt Injection?
Zeilenzahl oder geschätzte Tokenzahl
Letzte Git-Änderungsinformationen (wenn sicher und leicht verfügbar)
Empfehlung: behalten/zusammenführen/verschieben/umformulieren/isolieren/löschen
```

**Nicht nur Dateinamen aufzählen; die tatsächliche Rolle jeder Datei erläutern.**

---

## Beispiel für das Inventar

```markdown
| Pfad | Zeilen | Größe | Rolle | Automatisches Laden | Risiko |
|---|---:|---:|---|---|---|
| `.claude/CLAUDE.md` | 26 | 1.5KB | Globaler Einstieg mit Sprache/Zugangsdaten/Delegations-import | Jede Session | — |
| `專案/CLAUDE.md` | 477 | 130KB | Maßgebliche Projektregeln | Session in diesem Verzeichnis | Zu groß |
| `專案/AGENTS.md` | 477 | 130KB | **Byte-identisch zur vorigen Datei** | Session in diesem Verzeichnis | ⚠️ Regelaufspaltung |
| `memories/MEMORY.md` | — | 125KB | Automatisch in Codex-Sessions injiziert | **Jede Session** | ⚠️ Ohne Governance |
```

## Scanner-Abdeckung und manuelle Ergänzungen

`detox-scan.py` ist ein heuristischer Scanner für Anweisungstexte und erfasst nicht automatisch die gesamte obige Liste. Referenzierte READMEs, Engineering-Einstellungen, nicht unterstützte Formate und bereitgestellte Kopien separat in den genehmigten Umfang aufnehmen. Gründe für übersprungene oder unzugängliche Elemente dokumentieren; sie gelten weder als gelesen noch als bestanden.

Für geplante Änderungen an Governance-Dateien zusätzlich ursprüngliche Existenz, SHA-256, sichere Basisposition und Entwurfs-Digest erfassen und nach `artifact-contracts.md` ein Baseline-Manifest erstellen. mtime allein reicht zur sicheren Anwendung nicht aus.

Bei Projektorganisation zusätzlich Hauptprojekt, vorhandene Teilprojekte, Verantwortlichkeiten, Skill-Einstiege, Workflows, Abhängigkeiten, tatsächliche Betreuer, Verschiebepläne und unzugeordnete Elemente inventarisieren. Produktcode nur lokalisieren, nicht verschieben.
