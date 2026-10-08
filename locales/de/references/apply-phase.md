# Anwendungsphase

Schließt die aktuelle Benutzerautorisierung Änderungen an produktiven Dateien ein, darf die Anwendung folgen. Bei einem reinen Vorschlag keine produktiven Dateien ändern. Nur geprüfte Governance-Dateien bearbeiten; kein beiläufiges Produkt-Refactoring, keine Zugangsdatenänderungen, kein eigenmächtiger commit/push/Deployment.

## 1. Basis und Umfang prüfen

Das aktuelle `baseline-manifest.json` und den Entwurfs-Diff lesen. Quellen, Ziele, Existenz, SHA-256, Entwurfs-Digests, zugehörige rule IDs und offene Konflikte prüfen. Aktuellen Git HEAD, Branch und `git status --porcelain` dokumentieren. Ohne Git weiterhin Digests und sichere Basiskopien verlangen; mtime ist kein vollständiger Versionsbeleg.

Jeden Pfad auf genehmigten Umfang und Abwesenheit von symlinks/junctions/reparse points prüfen. Das Ziel darf keine Zugangsdaten, Produktcode oder sonstige unautorisierte Datei sein. Neue Dateien müssen weiterhin fehlen; bei MOVE Quelle und Ziel gleichzeitig prüfen.

Bei Änderungen seit dem Audit sichere Basis, aktuelle Fassung und Entwurf in einem Drei-Wege-Vergleich prüfen und neue Arbeit erhalten. Nicht sicher zusammenführbare Punkte als `DEFERRED` markieren, übrige sicher bearbeitbare Punkte abschließen. Wesentliche unentschiedene Konflikte nicht anwenden. Digests vor und nach der Dateiprüfung kontrollieren, damit alte Entwürfe keine neuen Inhalte überschreiben.

## 2. Vor dem Sichern prüfen

Nach dem [Artefaktvertrag](artifact-contracts.md) Quellen auf eingemischte Geheimnisse prüfen und Sicherungsort sowie Berechtigungen bestätigen. Nicht erst kopieren und danach scannen. Geheimnishaltige Dateien dürfen nicht in allgemeines staging, Git, öffentliche Berichte oder Übergabepakete. Ohne genehmigten eingeschränkten Aufbewahrungsort diesen Punkt stoppen. Sicheren Sicherungsort, Digest und ursprüngliche Existenz im Manifest erfassen.

Jedes Mal ein neues Sicherungsverzeichnis anlegen und alte Versionen erhalten. Sicherungen und Berichte dürfen nicht im automatischen Ladebereich von Agenten liegen. Dieser Skill hat keinen automatischen Anwender. Keine Werkzeugvalidierung des Manifests behaupten, sofern sie nicht tatsächlich ausgeführt wurde.

## 3. Dateiweise anwenden

Zuerst neue maßgebliche Quellen erstellen, dann verweisende Einstiege aktualisieren, zuletzt alte Quellen bearbeiten oder archivieren. Jeder Schritt muss getrennt rückgängig machbar sein. Für die aktuelle Plattform geeignete Verfahren wie atomaren Ersatz verwenden; unmittelbar vor dem Schreiben Version erneut prüfen, danach zurücklesen und Inhalt sowie Digest bestätigen. `applied_sha256`, `status`, tatsächliche Zeit und Aktionsprotokoll im Manifest aktualisieren.

Bei MOVE/ARCHIVE zuerst eine sichere Zielkopie und neue Verweise schaffen; erst nach Bestätigung die Quelle bearbeiten. Weiterhin wertvolle Gesprächsverläufe/Entscheidungsprotokolle nicht endgültig löschen; eine wiederherstellbare Position erhalten. Quellen nicht über junctions löschen.

## 4. Validieren

Governance-Umfang und neue Architektur erneut prüfen: Geheimnisse, Pfade, Zyklen, Duplikate, Regelumfang, Laden und Synchronisation bereitgestellter Kopien. Bei Projektorganisation zusätzlich `project-map.json` validieren, Navigation neu erzeugen und Teilprojekt-Skill-Einstiege, Verantwortlichkeiten und Workflows prüfen. Rücknavigation zur übergeordneten Ebene darf nicht als obligatorischer Neulesezyklus behandelt werden.

Engineering-Prüfskripte einschließlich Inhalt, indirekten hooks, Schreib- und Netzwerkverhalten zuerst prüfen, dann innerhalb der Aufgabenautorisierung ausführen. Unbekannte Befehle nicht allein wegen der Bezeichnung „Validator“ in einer auditierten Datei ausführen. Tatsächliche Befehle, Exitcodes und Ergebniszusammenfassungen erhalten. Scheitert ein alter Validator, zuerst veraltete Assertion und echte Unterbrechung unterscheiden. Assertions nur mit funktionalen Belegen aktualisieren; Abnahmekriterien nicht zum Erzwingen eines Erfolgs lockern. Neue Änderungen bleiben innerhalb der aktuellen Autorisierung.

## 5. Rollback

Vor Rollback prüfen, ob der aktuelle Digest noch dem `applied_sha256` dieses Durchlaufs entspricht. Andernfalls Drei-Wege-Vergleich durchführen und spätere Änderungen erhalten.

| Maßnahme dieses Durchlaufs | Rollback |
|---|---|
| UPDATE | Aus sicheren Sicherungen dateiweise wiederherstellen und ursprünglichen Digest zurücklesen |
| CREATE | Nur in diesem Durchlauf neu erstellte und seitdem unveränderte Dateien behandeln; in isolierten Rücknahmebereich verschieben und keine automatisch geladenen Einstiege zurücklassen |
| MOVE/ARCHIVE | Beide Enden prüfen, Quelle und Verweise wiederherstellen, anschließend Zielkopie dieses Durchlaufs zurücknehmen |
| Nur Entwürfe | Keine produktiven Dateien wiederherstellen; Audit-Belege erhalten |

`git reset --hard`, `git clean`, erzwungenes checkout und pauschales Löschen ungetrackter Benutzerdateien sind verboten. Unter Windows für Verschieben/Löschen native Operationen derselben Shell mit LiteralPath verwenden und zuvor absolute Ziele auf Einhaltung der Grenzen prüfen. Nach Rollback Verweise und Workflows erneut validieren und das Manifest als `ROLLED_BACK` markieren.

## 6. Anwendungsbericht

`AI-DETOX-APPLY-REPORT.md` erstellen mit:

- Git-Status vor Anwendung, Versionsbasis, Umfang und Prüfung sicherer Sicherungen.
- Tatsächlich neu angelegten, aktualisierten, verschobenen, archivierten und unbehandelten Dateien sowie Gründen.
- Ursprünglichen Regelpositionen, aktueller einziger maßgeblicher Quelle und Verhaltenswirkung.
- `PASS`/`FAIL`/`NOT_RUN`/`NOT_APPLICABLE` der Validierung mit Belegen.
- Offenen Konflikten, dateiweisem Rollback und Ausführungsvoraussetzungen.
- Agenteneinstellungen, die eine neue Session benötigen, und solchen, die erst beim nächsten Lesen wirksam werden; keine sofortige Synchronisation aller Hosts voraussetzen.

Diffs vorab auf Geheimnisse prüfen. Kann ein ursprünglicher Diff nicht sicher erzeugt werden, nur Position und Grund dokumentieren, niemals Geheimniswerte ausgeben.
