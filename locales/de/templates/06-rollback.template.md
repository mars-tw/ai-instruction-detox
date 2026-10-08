# 06 — Rollback

## Aktueller Modus

Dokumentieren, ob nur Entwürfe erstellt oder Änderungen angewendet wurden. Bei reinen Entwürfen ist keine Wiederherstellung produktiver Dateien nötig; Audit-Belege erhalten. Nicht annehmen, dass sämtliche Dateien unter .ai-detox aus diesem Durchlauf stammen; vorhandene Berichte nicht pauschal löschen.

## Voraussetzungen pro Datei

| Pfad | Aktion | Zuvor vorhanden | Basis-SHA-256 | Angewendeter SHA-256 | Sichere Sicherung | Rollback |
|---|---|---|---|---|---|---|

Mit baseline-manifest.json abgleichen. Vor Rollback aktuellen Digest prüfen. Weicht er von der angewendeten Version ab, spätere Änderungen erhalten und Drei-Wege-Vergleich durchführen oder Bestätigung ausstehend markieren. Keine direkte Überschreibung mit alter Sicherung.

## Rollback nach Aktion

- UPDATE: sichere Sicherung wiederherstellen und ursprünglichen Digest zurücklesen.
- CREATE: nur in diesem Durchlauf neue und seitdem unveränderte Dateien zurücknehmen; keine automatisch geladenen Einstiege zurücklassen.
- MOVE/ARCHIVE: beide Enden prüfen, Quelle und Verweise wiederherstellen, Zielkopie dieses Durchlaufs zurücknehmen.
- Nicht angewendet: keine Wiederherstellung produktiver Dateien nötig; nur Entwurfspositionen erfassen.

Jeden Punkt mit geprüften tatsächlichen Pfaden und plattformgerechten Befehlen ausfüllen. Kein pauschales reset/clean oder rekursives Löschen vorgeben. Unter Windows LiteralPath verwenden und absolute Pfade vorab innerhalb des genehmigten Umfangs bestätigen. Quellen nicht über Links bearbeiten.

## Rollback-Validierung

Prüfbefehle, Exitcodes und zurückgelesene Ergebnisse für Verweise, Haupt-/Teilprojekt-Skill-Routing, Workflows und Projektindex dokumentieren. Einstiegseinstellungen prüfen, die eine neue Session verlangen; Manifest auf ROLLED_BACK aktualisieren.
