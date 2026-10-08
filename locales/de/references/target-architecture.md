# Zielarchitektur: die Struktur nach der Bereinigung

---

## Vier verbindliche Grundsätze

### 1. Eine einzige maßgebliche Quelle

Jede Regel hat genau **eine** primäre maßgebliche Quelle. Andere Dateien dürfen nur darauf verweisen, einen agentenspezifischen Adapter bereitstellen oder einen tatsächlich anderen Geltungsbereich ergänzen.

Dieselbe Regel **nicht** in Einstiegsdateien, Skills und Kontext kopieren.

### 2. Einstiegsdateien enthalten nur langfristige übergreifende Regeln

Geeignete Inhalte:

- Projektmission und Umfang
- Unverletzliche Kernbeschränkungen
- Wesentliche Architekturprinzipien
- Sicherheit und Datenschutz
- Zentrale Entwicklungsbefehle
- Mindestanforderungen für Tests und Abnahme
- Grenzen für Änderungen und Deployment
- Anweisungspriorität
- Laden relevanter Skills und Kontexte
- Definition of Done

Ungeeignet sind umfangreiche Historien, einzelne Vorfälle, vollständige Abläufe einzelner Aufgaben, zahlreiche Beispiele, Details abgeschlossener Phasen, nicht für jede Aufgabe benötigter Hintergrund und häufig wechselnde Personal- oder Versionsinformationen.

Unverbindlicher Richtwert: **80–200 Zeilen**. Bei Überschreitung den Grund erklären; **keine wichtigen Inhalte nur zur Einhaltung des Richtwerts löschen**.

### 3. Skills enthalten nur wiederverwendbare Workflows

Jeder Skill soll enthalten: Name, Zweck, Auslöser, Situationen ohne Auslösung, erforderliche Eingaben, verfügbare Werkzeuge, Schritte, Risiken und Grenzen, Ausgabeformat, Abnahmekriterien, Stoppbedingungen, Fehlerbehandlung und Beziehungen zu anderen Skills.

**Nicht alle Skills bei jeder Aufgabe automatisch laden**, sondern nur unmittelbar relevante Skills.

### 4. Kontext enthält nur Fakten und Zustand

Aufbewahren: verifizierte Fakten, Architekturzustand, Projektbasis, aktuelle Versionen, abgeschlossene/offene Punkte, Glossar, Rollen und Ressourcen, Entscheidungsgrundlagen, Quellen und Daten.

Keine umfangreichen dauerhaften Verhaltensregeln hineinpacken.

Veränderliche Informationen benötigen:

```yaml
verified_at: 2026-08-27
source: <Prüfmethode oder Quelle>
owner: <Verantwortlicher>
expires_at / recheck_condition: <Bedingung für erneute Prüfung>
```

---

## Gemeinsame Architektur für mehrere Agenten

**Problem:** Agenten verwenden unterschiedliche Einstiegsdateien und unterstützen nicht unbedingt dieselbe Verweissyntax.

**Lösung**, ohne Unterstützung einer bestimmten Verweissyntax vorauszusetzen:

```
<共用目錄>/core-rules.md          ← Klartext, von jedem Agenten lesbar
├── Regelpriorität
├── Sprache
├── Zugangsdaten
├── Richtlinie für externe Texte
├── Delegation zwischen CLIs
└── Keine Behauptungen über nicht erfolgte Handlungen

Agenten-Einstiegsdateien (nur tatsächliche Unterschiede des jeweiligen Agenten)
├── Claude:  unterstützte und überprüfte import-Syntax des Werkzeugs
├── Codex:   ausdrückliche Ladeanweisung mit Pfad („<path> laden und befolgen“)
├── Qwen:    ebenso
└── Grok:    ebenso
```

**Entscheidend:**

1. Zuerst **die aktuelle Umgebung und tatsächliche Projektnutzung prüfen**; Syntaxunterstützung nicht voraussetzen.
2. Ohne Verweisunterstützung nur das **unvermeidbare Minimum** wiederholen.
3. Für wiederholte Inhalte **Synchronisationsprüfungen einrichten** (siehe unten).
4. Jede Einstiegsdatei mit `VERSION` kennzeichnen, damit Versionsaufspaltungen erkennbar sind.

---

## Wohin einmalige Vorfälle gehören

| Eigenschaft | Ziel |
|---|---|
| Automatisch prüfbares Verhalten | regression test |
| Vor Auslieferung zwingend prüfen | acceptance checklist |
| Architekturentscheidung | ADR (Architecture Decision Record) |
| Ablauf und Ursache eines Vorfalls | incident report |
| Begründung einer Entscheidung | decision log |
| Reine Historie | archive, nicht mehr laden |
| Nur in einem Verzeichnis gültig | Regeldatei dieses Verzeichnisses |

**Nicht sämtliche Vorfälle dauerhaft in globale Agentenanweisungen aufnehmen.**

---

## Regeln formulieren

Jede Regel möglichst mit **Aktion, Geltungsbereich, Auslöser, Ausnahme, Prüfmethode und Fehlerbehandlung** formulieren.

Wörter ohne Bewertungskriterien sparsam verwenden: beste, perfekt, hohe Qualität, natürlich, angemessen, situationsabhängig, neueste, bevorzugt, vollständig.

`MUST`, `NEVER` und `ALWAYS` **besonders prüfen**. Absolute Wörter gehören nur zu tatsächlich unverletzlichen Anforderungen für Sicherheit, Datenintegrität, Recht oder zentrale Abnahme.

---

## Erneute Regelanhäufung verhindern

1. Das **Prinzip der einzigen maßgeblichen Quelle** in die Einstiegsdatei aufnehmen.
2. **Unverbindliche Zeilenobergrenzen**: Benutzerebene ≤ 40, Projektebene ≤ 200 Zeilen.
3. **Synchronisationsprüfung automatisieren** und prüfen:
   - Alle Einstiegsdateien verweisen auf die gemeinsame Quelle.
   - `VERSION` stimmt überein.
   - Wesentliche Regelzeichenfolgen stehen nur in der maßgeblichen Quelle, ohne Duplikate.
   - Alle referenzierten Pfade existieren; keine verwaisten Verweise.
4. **Vor jeder neuen Regel drei Fragen stellen:**
   - Wo ist die maßgebliche Quelle; wurde dies schon beschrieben?
   - Automatisch prüfbar? Dann als Test umsetzen.
   - Allgemeines Prinzip oder einzelner Vorfall? Bei Letzterem den Umfang begrenzen.
5. **Erinnerungen und Zeitpläne vierteljährlich prüfen**; beide injizieren automatisch und sammeln leicht veraltete Regeln an.

---

## Anforderungen an das Synchronisationsprüfskript

```
[ ] Gemeinsame maßgebliche Quelle existiert und ist nicht leer
[ ] Sie enthält alle erforderlichen Abschnitte
[ ] Jede Einstiegsdatei verweist auf sie
[ ] Einstiegsdateien kopieren keine Inhalte der Quelle (keine doppelten Schlüsselzeichenfolgen)
[ ] Sämtliche referenzierten Pfade existieren
[ ] Keine zyklischen Verweise
[ ] Skill-Links/junctions zeigen auf das richtige Ziel
[ ] Bereitgestellte Kopien und ursprüngliche assets sind synchron (Hashvergleich)
```

⚠️ **Auch Prüfskripte veralten.** Prüfen sie Einstiegsdateien nur anhand wörtlicher Inhalte, können verschobene Regeln falsche Fehler auslösen. Vor einer Korrektur feststellen, **ob die Assertion veraltet oder die Verknüpfung tatsächlich unterbrochen ist**. Assertions sollen vorzugsweise die **Funktion** prüfen (Verweis auf die maßgebliche Quelle), nicht den **Wortlaut** (Vorhandensein eines Satzes).

## Haupt-Skill und Teilprojekt-Skills

Bei Gesamtorganisation des Projekts nach dem [Projektorganisationsprozess](project-organization.md) Haupt-Skill und Workflow erstellen und Teilprojekt-Skills in ihren Teilprojekten ablegen. project-map.json ist der einzige Hierarchie- und Pfadindex; Navigation, Breadcrumbs und Mindmap werden daraus erzeugt. Gemeinsame Quelle und Haupt-Skill teilen sich die Verantwortung: Die Quelle regelt aufgabenübergreifende Grenzen, der Haupt-Skill Routing und Übergaben. Er kopiert keine gemeinsamen Regeln und erzwingt nicht das Laden aller Teilprojekt-Skills.
