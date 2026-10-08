# Sprachfassungen und Installation

Vier Sprachen stehen bereit: `zh-TW`, `en`, `de`, `ja`. Die chinesischen Dokumente im Stammverzeichnis bilden die Übersetzungsquelle. Bedeutung und Sicherheitsverträge werden mit derselben Version gepflegt. Übersetzungen dienen zum Lesen und Ausführen; sie vergeben keine zusätzlichen Berechtigungen und konkurrieren nicht als maßgebliche Quellen mit dem Original. Der Host darf nicht gleichzeitig alle vier gleichnamigen Skills automatisch laden.

## Vollständiger Umfang

Jede Sprache enthält README, SKILL, CHANGELOG, AUDIT-REPORT sowie sämtliche references und templates. Erklärungen in natürlicher Sprache und Vorlagenbeschriftungen werden übersetzt. Code, Befehle, Dateinamen, JSON keys, schema version, CSV header, Status-enums, rule IDs, Vorlagenvariablen und externe URLs bleiben identisch. Historische Testergebnisse der Quelldokumente bleiben erhalten; begrenzte tatsächliche Tests dürfen nicht als Validierung aller Sprachen und Plattformen dargestellt werden.

Im Quellcode liegen die Übersetzungen unter `locales/en`, `locales/de`, `locales/ja`; es gibt nur einen gemeinsamen Satz Werkzeuge und Tests im Stammverzeichnis `scripts/` und `tests/`. Wer einen locale-Haupt-Skill direkt liest, muss Befehle vom Repository-Stamm aus ausführen. Ein kopierter locale-Ordner allein ist kein vollständiger ausführbarer Skill.

## Veröffentlichungspakete

```powershell
python scripts/build-locales.py --output-dir release-packages-new
```

Den Build-Befehl vom vollständigen Quellrepository aus ausführen. Der Paket-Builder wird nur im Quellrepository benötigt und ist nicht in den veröffentlichten Sprach-ZIPs enthalten.

Das Ausgabeverzeichnis muss neu sein. Erzeugt werden vier ZIPs, SHA256SUMS.txt und RELEASE-MANIFEST.json. Jedes ZIP hat `ai-instruction-detox/` als obersten Ordner und enthält die Dokumente und Vorlagen der Sprache, gemeinsame Werkzeuge, Tests und `package-language.json`. Nur ausdrücklich ausgewählte öffentliche Dateien werden gepackt; kein Git, staging, Sicherungen, private Pfade oder Zugangsdaten. Sprachwechsel-Links im Paket verweisen auf die entsprechende GitHub-Version, damit sie keine nicht installierten Sprachdokumente voraussetzen.

Nach Download und SHA-256-Prüfung den vollständigen Ordner im Skill-Verzeichnis des Hosts ablegen. Den Lade-/Aktualisierungsprozess des Hosts verwenden; nicht identische Installationsverzeichnisse oder automatische Ladesyntax aller Produkte voraussetzen. Vor Updates bestehende Skill-Änderungen und wiederherstellbare Kopien erhalten. Nicht vier gleichnamige Haupt-Skills gleichzeitig installieren. Vor Sprachwechsel Quellversion prüfen und das vollständige Paket wechseln.

## Werkzeugsprache

Scanner und Navigationswerkzeug akzeptieren `--language zh-TW|en|de|ja`. Ohne Angabe verwenden sie `package-language.json` des Skill-Pakets, in dem die Werkzeuge liegen; im Quellcode ist traditionelles Chinesisch der Standard. Sie lesen keine Metadaten aus dem auditierten Verzeichnis und raten nicht anhand der Betriebssystemumgebung. CLI-Texte, Zusammenfassungen und erzeugte Navigationsbeschriftungen ändern sich; maschinenlesbare Felder, Dateinamen und Exitcodes bleiben gleich.

```powershell
python scripts/detox-scan.py --root . --language en
python scripts/project-map.py check --manifest project-map.json --language de
python scripts/project-map.py render --manifest project-map.json --output-dir map-preview-new --language ja
```

Diese Optionen ändern weder erlaubte Pfade, Scanumfang, Schreibgrenzen noch Sicherheitsprüfungen.

## Pflege und Validierung

Bei jeder Änderung des Quellvertrags relevante Übersetzungen, Vorlagen und Versionen synchronisieren. Tests vergleichen vollständiges Dokumentinventar, relative Links, Vorlagenvariablen, maschinenlesbare Felder, Codebefehle und Sprachoptionen. Zusätzlich ein semantisches Review in unabhängigem Kontext durchführen; Dateiexistenz allein reicht nicht. Jede CLI-Sprache mit temporären fixtures tatsächlich ausführen. Veröffentlichungs-ZIPs entpacken und Ressourcen, Werkzeuge und Metadaten prüfen. Nicht ausgeführte Sprach-/Plattformprüfungen als NOT_RUN kennzeichnen; fertige Übersetzungen belegen keinen Test-Erfolg.
