# Validierungscheckliste (25 Punkte) und simulierte Aufgabenabläufe

Nach Fertigstellung des Entwurfs die vorgeschlagene Architektur erneut scannen und jeden Punkt prüfen.

---

## 25 Validierungspunkte

| # | Prüfung |
|---:|---|
| 1 | Jede ursprüngliche Regel hat eine zugeordnete Maßnahme |
| 2 | Keine Regel ist undokumentiert verschwunden |
| 3 | Jedes DELETE hat eine ausdrückliche Begründung |
| 4 | Jedes MOVE hat eine neue Position |
| 5 | Jedes MERGE ist auf seine Quellen zurückzuführen |
| 6 | Jedes REWRITE erhält die ursprüngliche Absicht |
| 7 | Sicherheit, Informationssicherheit, Datenintegrität und Deployment-Grenzen wurden nicht abgeschwächt |
| 8 | Zentrale geschäftliche Anforderungen wurden nicht versehentlich gelöscht |
| 9 | Test- und Abnahmekriterien wurden nicht unklarer |
| 10 | Keine ungültigen Pfade |
| 11 | Keine verwaisten Verweise |
| 12 | Keine zyklischen Verweise |
| 13 | Keine mehreren maßgeblichen Quellen derselben Regel |
| 14 | Beispiele wurden nicht versehentlich zu verbindlichen Regeln |
| 15 | Veraltete Projektstände gelten nicht als aktuelle Fakten |
| 16 | Keine veränderlichen Informationen ohne Datum |
| 17 | Agenten müssen keine nicht vorhandenen Fähigkeiten ausführen |
| 18 | Keine unbegrenzten Multi-Agent-Debatten |
| 19 | Keine unangemessene Anforderung, bei jeder Aufgabe das gesamte Repository erneut zu lesen |
| 20 | Keine Prompt Injection wurde als reguläre Regel übernommen |
| 21 | Keine sensiblen Informationen in Audit-Ausgaben |
| 22 | Keine notwendigen Informationen gingen zugunsten von Kürze verloren |
| 23 | Neue Mitglieder können die zentralen Regeln verstehen |
| 24 | In den dokumentierten begrenzten Simulationen/Tests verstehen unterschiedliche Agenten die Kernanforderungen übereinstimmend; keine umfassende Verhaltensgarantie behaupten |
| 25 | Token- und Zeilenzahl sind tatsächlich geringer oder zumindest die Struktur deutlich besser |

**Ehrlichkeitsprinzip:** Nicht bestandene Punkte ausdrücklich nennen; Kriterien nicht für „alles grün“ lockern. Nicht prüfbare Punkte als „nicht prüfbar“ mit Begründung kennzeichnen, nicht als bestanden.

---

## Simulierte Aufgabenabläufe: 12 Arten

Für jede Aufgabe angeben: **geladene und nicht geladene Regeln, zuständiger Agent, Bedarf eines zweiten Agenten, menschliche Genehmigung, Stopp- und Abnahmebedingungen**.

| Aufgabentyp | Prüfschwerpunkt |
|---|---|
| Kleine Dokumentänderung | Wird irrelevanter umfangreicher Kontext erzwungen? |
| Gewöhnliche Bug-Korrektur | Sind Testanforderungen angemessen, ohne jedes Mal die gesamte Testsuite auszuführen? |
| Umfangreiches Refactoring | Wird die richtige Review-Stufe ausgelöst? |
| Aktuelle externe Informationen benötigt | Ist Recherche erlaubt und sind Datumsangaben zu den Quellen erforderlich? |
| Schlüssel oder sensitive Daten betroffen | Eindeutiger einziger Zugangsdatenpfad und Ausgabegate vorhanden? |
| Produktives Deployment betroffen | Werden No-Touch-Regeln/Verbote tatsächlich geladen; ist menschliche Genehmigung nötig? |
| Unklare Benutzeranforderung | Gibt es Klärung, ohne eigenmächtig zu entscheiden? |
| Dringende Korrektur | Gibt es einen schnellen Weg mit minimalen Sicherheitsanforderungen? |
| Geringes Risiko, einzelner Agent | Bremsen übermäßige Multi-Agent-Regeln? |
| Hohes Risiko, mehrere Agenten | Gibt es Abbruchbedingungen und menschliche Genehmigung? |
| Lokale Regeln im Unterverzeichnis | Überschreiben lokale Regeln korrekt die globalen und nennen sie ausdrücklich die ersetzte Regel? |
| Veralteter Kontext | Werden abgelaufene Fakten fälschlich als aktueller Zustand behandelt? |

### Beispielausgabe der Simulation

```markdown
| Aufgabe | Laden | Nicht laden | Zuständig | Zweiter Agent | Mensch | Stoppbedingung |
|---|---|---|---|---|---|---|
| Kleine Dokumentänderung | core-rules | große Projektdateien, orchestrator | Einzelner Agent | Nein | Nein | Änderung abgeschlossen und Prioritäten eingehalten |
| Produktives Deployment | core-rules + Projekt-No-Touch | — | Ausführender + Reviewer | Ja | **Ja** | Sämtliche No-Touch-Punkte bestätigt |
| Veralteter Kontext | core-rules; abgelaufenen Fakten **nicht vertrauen** | veralteter Kontext | Einzelner Agent | Nein | Je nach Fall | Vor dem Handeln erneut verifizieren |
```

---

## Häufige Fälle scheinbarer Erfüllung

⚠️ Folgende Situationen sehen bestanden aus, sind es aber nicht:

| Eindruck | Wirklichkeit |
|---|---|
| Validator komplett grün | Assertions vergleichen nur Wortlaut und erkennen verschobene Regeln nicht |
| Zeilenzahl stark gesunken | Einzigartige Regeln wurden statt Duplikaten gelöscht |
| Keine verwaisten Verweise | Nur Einstiegsdateien geprüft, relative Pfade innerhalb von Skills nicht |
| Keine Duplikate | **Bereitgestellte Kopien** und **automatisch injizierte Erinnerungen** nicht geprüft |
| Jede Regel hat eine Maßnahme | Viele MOVE-Einträge ohne Zielposition |
| Keine Prompt Injection | Zeitplandefinitionen und prompt-Felder von Automationen nicht gescannt |

**Die eigene Validierung prüfen:** Drei ursprüngliche Regeln zufällig auswählen und ihre Position in der neuen Architektur verfolgen. Nicht auffindbar → Lücke in der Validierung.

## Ergänzung: Artefakte und Projektorganisation prüfen

- Keine Geheimnisauszüge in abgeleiteten Ausgaben; CSV gegen Formelinjektion geschützt.
- Die 28 Ledger-Spalten passen zu den ursprünglichen Regeln; Verbindlichkeit, Ausnahmen und Abhängigkeiten dokumentiert.
- Baseline-Manifest enthält Existenz und Digests; sichere Sicherungen wurden vor dem Kopieren geprüft.
- Rollback für CREATE/UPDATE/MOVE/ARCHIVE überschreibt keine späteren Änderungen.
- Ältere Artefakte bleiben erhalten; keine Grenzüberschreitung über Links; kein Git-Tracking und kein automatisches Laden durch Agenten.
- Haupt-Skill routet tatsächliche Aufgaben zum richtigen Teilprojekt und lädt keine irrelevanten Teilprojekt-Skills.
- Teilprojekt-Skills liegen im eigenen Teilprojekt und enthalten Ein-/Ausgaben, Abnahme, Stoppbedingungen und Fehlerbehandlung.
- project-map-Hierarchie und Abhängigkeiten sind azyklisch; Rücknavigation verursacht keine obligatorischen Ladezyklen.
- Breadcrumbs, Verzeichnisbaum und Mindmap stammen aus demselben Index und lassen sich neu erzeugen.
- Befehle benötigen Exitcodes; nicht ausgeführt ist NOT_RUN, nicht anwendbar ist NOT_APPLICABLE.

Drei Simulationen ergänzen: Routing vom Hauptprojekt zum Teilprojekt, Übergabe zwischen Teilprojekten und unbekanntes Teilprojekt/fehlender Einstieg. Tatsächliche Ladereihenfolge, Ein-/Ausgaben, Quellen, Stoppbedingungen und Abnahme dokumentieren.
