# Scanner-Vertrag

`scripts/detox-scan.py` verwendet mit Python 3.8 kompatible Syntax und die Standardbibliothek. Es installiert keine Pakete, führt keine Quellinhalte aus und liest keine Inhalte referenzierter Ziele. Tatsächlich geprüfte Python-/Plattformversionen stehen im Update-Bericht.

Im Quell-Checkout werden die gemeinsamen Skripte im Repository-Stamm verwendet; Befehle dort ausführen. Vollständige Sprach-ZIPs enthalten diese Skripte.

## Verwendung

```powershell
python scripts/detox-scan.py --root .
python scripts/detox-scan.py --files SKILL.md references/apply-phase.md
python scripts/detox-scan.py --root . --json scan-new.json
python scripts/detox-scan.py --root . --max-depth 8 --max-bytes 2097152
```

Genau eine Option aus `--root` und `--files` ist erforderlich; beide gemeinsam sind unzulässig. Rekursive Scans des Benutzerverzeichnisses oder eines Dateisystem-Stammverzeichnisses sind verboten. Ausdrückliche Dateilisten lehnen ebenfalls sensible Positionen, Links und nicht reguläre Dateien ab. `--json` darf nur neue Dateien erzeugen; das übergeordnete Verzeichnis muss existieren. Quellen, alte Berichte und Links dürfen nicht überschrieben werden.

Standards: Tiefe 6, Stamm auf 0; 1 MiB je Datei; höchstens 5.000 Dateien; insgesamt 64 MiB gelesene Daten. UTF-8 und UTF-8 BOM werden gelesen. Falsche Kodierung, fehlende/unlesbare oder sich verändernde Dateien sowie Tiefen- und Größenabschneidungen werden als coverage error dokumentiert und gelten nicht als gescannt.

| Exitcode | Bedeutung |
|---:|---|
| 0 | Gewählter Umfang vollständig gelesen, keine Risikomuster; keine vollständige semantische/Sicherheitsfreigabe |
| 1 | Verdacht auf Geheimnisse, Injection, Verweisgrenzen, verwaiste Verweise, mögliche Zyklen oder dateiübergreifende Duplikate |
| 2 | CLI, Umfang oder Ausgabe ungültig bzw. keine scanbaren Dateien gefunden |
| 3 | Teilscan; Lücken vor Bewertung der Vollständigkeit beheben |

## Befunde und Grenzen

- Alle Befunde enthalten nur Position, Kategorie und erforderliche Statistiken, keine Quellauszüge, Geheimniswerte oder ursprünglichen Verweiszeichenfolgen.
- Unterstützt Schlüssel mit üblichen Präfixen, GitHub fine-grained PATs, URLs mit Zugangsdaten, private Schlüsselmarker und allgemeine Zugangsdatenzuweisungen. Beliebige Geheimnisse werden nicht garantiert erkannt; Schutzbeispiele und Verbotsaussagen können ebenfalls Treffer auslösen.
- Analysiert Markdown-, Backtick- und übliche Klartext-Dateiverweise; URLs und reine Anker werden ignoriert. Verweise dürfen den Scanumfang nicht über `..` oder Links verlassen und lösen kein zusätzliches Lesen von Inhalten aus.
- Stark zusammenhängende Komponenten eines gerichteten Graphen finden Mehrknoten- und Selbstzyklen. Je Komponente wird ein repräsentativer Zyklus ausgegeben, nicht jeder mögliche Zyklus. Navigationsrücklinks und Beispiele können Treffer auslösen; obligatorisches Laden muss gesondert beurteilt werden.
- Duplikaterkennung verwendet vollständige normalisierte Absätze statt gekürzter Präfixe und gibt keinen Absatzinhalt zurück.
- Dateigröße und Tokenschätzung beschreiben das Scanvolumen, nicht das tatsächliche automatische Ladevolumen des Hosts.
- Automatisches Inventar umfasst nur im Programm definierte Einstiegsnamen und Regelverzeichnisse. READMEs, Engineering-Konfigurationen, nicht unterstützte Formate und extern installierte Kopien nach Inventarcheckliste ergänzen; das automatische Inventar ist kein vollständiges Projektinventar.

## JSON-Version 2

`schema_version`, `files_selected`, `files_scanned`, `complete`, `errors`, `skipped`, `limits`, `dangling_refs`, `boundary_refs`, `circular_refs`, `secrets`, `injections`, `vague_rules`, `absolute_terms`, `duplicate_blocks`, `file_stats`.

`complete` bedeutet nur erfolgreiches Lesen innerhalb des eingestellten Umfangs; richtlinienbedingte Ausschlüsse bleiben unter `skipped`. `snippet`, `text`, raw `ref` und das Zwei-Knoten-`pair` aus v1 werden nicht mehr ausgegeben; Berichtskonsumenten müssen aktualisiert werden. Für Zyklen `files` und `cycle`, für Duplikate `locations` und `characters` lesen.

Die Python-Schnittstelle behält `find_files(root=None, explicit=None, max_depth=6)` und `scan(files, root=None, max_bytes=1048576)`. Das Inventar ist eine list-kompatible `FileSelection` mit `root`, `errors` und `skipped`. Fehlgeschlagenes `read()` löst einen Fehler aus und darf nicht mehr wie eine leere Datei behandelt werden.

Pfadprüfungen sind keine Betriebssystem-Sandbox. Während der Ausführung verhindern, dass andere Prozesse übergeordnete Verzeichnisse bösartig austauschen; keinen vollständigen Schutz gegen parallele Pfadrennen behaupten.
