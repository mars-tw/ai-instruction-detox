# Changelog

## 1.2.0 (2026-10-08)

- Vollständige Skills, Referenzdokumente, Vorlagen und Nutzungsanleitungen in Englisch, Deutsch und Japanisch ergänzt.
- Alle vier Sprachen verwenden gemeinsame Werkzeuge, maschinenlesbare Felder und Sicherheitsverträge bei identischer Version.
- Scanner und Navigation unterstützen --language; jedes veröffentlichte Sprachpaket verwendet standardmäßig seine eigene Sprache.
- Erzeugung der Sprachpakete sowie Prüfung von Vollständigkeit und sprachlicher Konsistenz ergänzt.

## 1.1.0 (2026-10-08)

- Gesamtorganisation von Projekten ergänzt: Haupt-Skill, gemeinsamer Workflow, Teilprojekt-Skills, einziger Index, Breadcrumbs, Baum und Mindmap.
- project-map.py zur Routing- und Abhängigkeitsprüfung ergänzt; überschreibt keine Quellen und führt keine Manifest-Inhalte aus.
- Geheimnislecks durch Berichtsauszüge, Beschränkung auf Zyklen mit zwei Knoten, falsche Duplikate durch gekürzte Präfixe, verschluckte Lesefehler und JSON-Überschreibung behoben.
- Sensitive Positionen, symlinks und junctions vom Scan isoliert; Abdeckungslücken und Ressourcenlimits ergänzt; JSON auf v2 angehoben.
- Audit-Vorlagen und Versionsbasis-/Rollback-Vertrag vervollständigt; Verbindlichkeit, Ausnahmen und Abhängigkeiten im Ledger ergänzt, von 25 auf 28 Spalten erweitert.
- Geheimnisse vor Sicherungen prüfen, nicht vertrauenswürdige Skriptausführung begrenzen und echte Tests, nicht ausgeführte Prüfungen und Simulationen unterscheiden.
- Haupt-Skill-Metadaten in das Standardfeld metadata verschoben; Hinweise zur Nutzung des vollständigen Pakets und zu schreibgeschütztem Zugriff korrigiert.
- Standardbibliothek-Tests und einen einzigen Einstieg zur Paketvalidierung ergänzt.

## 1.0.0 (2026-08-27)

Erstveröffentlichung. Die Methodik entstand aus einem tatsächlichen Governance-Audit sämtlicher AI-Anweisungen auf einem Rechner: 461 atomare Regeln, 88 Konflikte, 6 neu geordnete Einstiegsdateien.

- Zwölf Bereinigungsprüfungen mit vollständigen Kriterien
- Zehn Maßnahmenkategorien ohne stillschweigendes Löschen
- Trennung von Audit und Anwendung; das Audit verändert keine Originaldateien, isolierte Artefakte sind erlaubt
- Schreibgeschützter Scanner `detox-scan.py` ohne externe Abhängigkeiten; Geheimnisse werden nur mit Position, nie mit Wert gemeldet
- 25 Validierungsprüfungen und 12 Aufgabensimulationen
- Sechs Referenzen: Kriterien, Inventarcheckliste, Zielarchitektur, Multi-Agent-Review, Validierung und Anwendung
- Sechs praktische Lehren dokumentiert: falsche Validator-Fehler, Überschreiben von Richtlinien durch Erinnerungen, Umkehr durch bereitgestellte Kopien, junction-Fehlklassifikation, Löschen von Gesprächsverläufen und Zurückschreiben von Statusdateien
