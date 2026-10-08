# 00 — Scanumfang und Dateiinventar

Erstellt am: <DATE>
Modus: `MODE = AUDIT_AND_DRAFT` / `ORIGINAL_FILES_WRITE = DENIED` / `DEPLOYMENT = DENIED` / `GIT_COMMIT = DENIED`

## 1. Umgebung bestimmen

| Punkt | Tatsächliches Prüfergebnis |
|---|---|
| Ausführender Agent | <Claude Code / Codex / …> |
| Arbeitsverzeichnis | <path> |
| Git-Repository? | <Ja/Nein; falls nein, die Ebenen mit Anweisungsdateien beschreiben> |
| Einstiege anderer Agenten | <Tatsächlich vorhandene Einstiege auflisten> |

## 2. Git-Status: nicht committete Änderungen nicht anfassen

| Projekt | branch | Nicht committete Änderungen |
|---|---|---:|

## 3. Scanumfang

Ausdrückliche Positivliste verwenden; kein rekursiver Scan des gesamten Benutzerverzeichnisses.
Ausgeschlossen: `.git` / `node_modules` / `vendor` / `dist` / `build` / `cache` / Binärdateien / Modelldateien / Inhalte von Zugangsdatenverzeichnissen; nur deren Existenz erfassen.

## 4. Dateiinventar

### A. Agenten-Einstiegsdateien auf Benutzerebene: automatisch geladen

| Pfad | Zeilen | Größe | Rolle | Ladezeitpunkt |
|---|---:|---:|---|---|

### B. Anweisungsdateien auf Projektebene

| Pfad | Zeilen | Größe | Rolle | Risiko |
|---|---:|---:|---|---|

### C. Konfigurationsdateien
### D. Skills / Agents / Automations
### E. Erinnerungen / context

## 5. Unzugängliche oder ausgeschlossene Bereiche

- System-/Developer-Prompts der Plattform: **unzugänglich, außerhalb dieses Audits; kein Lesen behaupten**.
- <Zugangsdaten-Datei>: nur Existenz erfassen; keine Werte ausgeben.

## 6. Ladebeziehungen und bekannte strukturelle Risiken

```
<Ein Diagramm zeichnen, das zeigt, wer wen lädt>
```

**Verifizierte Strukturprobleme:**
1.

## 7. Versionsbasis und Artefaktisolation

| Governance-Pfad | Zuvor vorhanden | SHA-256 | Sichere Basisposition | Ziel/Entwurfs-Digest | LinkType | Lade-/Tracking-Status |
|---|---|---|---|---|---|---|

Jeden Punkt in baseline-manifest.json erfassen. Geheimnisse vor Sicherungen prüfen und keine Geheimnisauszüge in die Tabelle aufnehmen. Neues Artefaktverzeichnis dieses Durchlaufs, vorhandene Artefakte sowie Scanlücken durch Tiefe/Größe usw. dokumentieren.

## 8. Umfang der Projektorganisation

| Modul/Teilprojekt | Verantwortung/Quelle | Bestehender Pfad | Haupt-/Teilprojekt-Skill | Workflow | Abhängigkeiten | Grund fehlender Zuordnung |
|---|---|---|---|---|---|---|
