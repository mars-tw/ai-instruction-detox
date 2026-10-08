# Zwölf Bereinigungsprüfungen: vollständige Kriterien

Jede Frage für jede Regel beantworten. Ziel ist nicht, Löschgründe zu finden, sondern **die passende Ebene und Form für die Regel zu bestimmen**.

---

## 1. Standardverhalten prüfen

> Tut das Modell dies auch ohne ausdrückliche Anweisung garantiert?

Drei Kategorien unterscheiden:

| Kategorie | Bedeutung | Maßnahme |
|---|---|---|
| **A** | Von Plattform/Werkzeug **ausdrücklich garantiertes** Verhalten | Ohne besondere Projektbedeutung → bevorzugter Löschkandidat |
| **B** | Übliches Modellverhalten, aber **ohne Garantie** | Behalten und seine Bedeutung erklären |
| **C** | Projektspezifisch | Behalten |

**Wichtige Regeln nicht allein deshalb löschen, weil das Modell sich üblicherweise so verhält.** Standardverhalten ändert sich zwischen Versionen; die heutige Kategorie B kann morgen nicht mehr gelten.

Beispiele zur Einordnung:

- „Wahrheitsgemäß antworten“ → ohne Beleg einer technisch durchsetzbaren Plattformgarantie Kategorie B; eine Richtlinienerwartung ist keine Verhaltensgarantie
- „Keine API-Endpunkte in Antworten erfinden“ → B (üblicherweise vermieden, aber nicht garantiert) → sinnvoll zu behalten
- „Jede Preisaussage muss einem Feld der Spezifikationstabelle entsprechen“ → C → muss bleiben

---

## 2. Konflikte prüfen

> Widerspricht diese Regel anderen Regeln?

Häufige Konfliktmuster:

- Immer zuerst fragen ⟷ ohne Rückfragen ausführen
- Automatisch ändern ⟷ vor Änderungen Genehmigung benötigen
- Automatisch deployen ⟷ Deployment verboten
- Knapp bleiben ⟷ äußerst vollständig sein
- Nur einen Agenten verwenden ⟷ stets Multi-Agent-Debatte
- Kein Netzwerk verwenden ⟷ aktuelle Informationen recherchieren
- Immer das neueste Modell verwenden ⟷ reproduzierbare Version festschreiben
- Bestehende Struktur erhalten ⟷ vollständig refaktorieren
- Geschwindigkeit priorisieren ⟷ jeden Schritt mehrfach prüfen
- Alles automatisch ausführen ⟷ hohe Risiken erfordern menschliche Bestätigung

Angeben: beide Regeln, jeweilige Quellen und Geltungsbereiche, **ob tatsächlich ein Konflikt besteht**, ob nur unterschiedliche Geltungsbereiche vorliegen, empfohlene Priorität und Umformulierung.

⚠️ **Berechtigte Unterschiede zwischen Verzeichnissen, Aufgaben und Rollen nicht als Konflikt einstufen.** „In der Entwicklungsumgebung direkt ändern, in Produktion Genehmigung einholen“ ist eine korrekte Trennung der Geltungsbereiche.

---

## 3. Duplikate prüfen

> Wiederholt diese Regel Inhalte anderer Dateien?

Fünf Stufen unterscheiden:

| Stufe | Beschreibung |
|---|---|
| Identisches Duplikat | Wortgleich |
| Sinngleiches Duplikat | Andere Formulierung, gleiche Bedeutung |
| Teilweise Überschneidung | Gemeinsame und jeweils eigene Inhalte |
| Sonderfall | Eine Regel ist ein Sonderfall der anderen |
| **Versionsaufspaltung** | Kopien entwickeln sich bereits getrennt weiter; am gefährlichsten |

Die **geeignetste einzige maßgebliche Quelle** bestimmen. Andere Stellen löschen, durch Verweise ersetzen, auf einen agentenspezifischen Adapter kürzen oder einer Synchronisationsprüfung unterziehen.

Praktischer Hinweis: Steht dieselbe Regel an mindestens vier Stellen, ist ihre Version nahezu sicher bereits aufgespalten.

---

## 4. Vorfall-Patches prüfen

> Wurde diese Regel wegen einer einzelnen schlechten Ausgabe ergänzt?

Typische Merkmale:

- Der letzte Titel war zu lang → alle Titel dauerhaft begrenzen
- Zu viele Rückfragen → Rückfragen dauerhaft verbieten
- Ein Test wurde vergessen → vollständige Tests für jede Aufgabe
- Ein Modell scheiterte → drei Modelle für jede Aufgabe debattieren lassen
- Eine Datei wurde versehentlich gelöscht → sämtliche Dateiänderungen verbieten
- Ein Bild war falsch → Spezifikationen einer einzelnen SKU auf sämtliche Produkte anwenden

Entscheiden: **zu einem angemessenen allgemeinen Prinzip verallgemeinern**, **auf einen bestimmten Geltungsbereich begrenzen**, in einen regression test, eine Abnahmecheckliste, ADR/decision log verschieben oder direkt löschen.

⚠️ Vorfall-Patches **sind oft inhaltlich richtig**; ihr Geltungsbereich wurde zu weit ausgedehnt. Die Maßnahme soll den richtigen Umfang wiederherstellen, nicht die Erfahrung verwerfen.

---

## 5. Unklarheit prüfen

> Wird diese Regel jedes Mal anders verstanden?

Warnsignale: professioneller machen, natürlicher, guter Ton, vollständig sein, möglichst knapp, sehr hohe Qualität, bestes Modell, rechtzeitig recherchieren, bei Bedarf fragen, keine Token verschwenden, situationsabhängig Multi-Agent, korrekte Ergebnisse sicherstellen, wesentliche Änderungen, angemessen behandeln.

Umformulieren mit **Aktion + Geltungsbereich + Auslöser + Ausnahme + Prüfmethode**.

Beispiel:

❌ „Die Ausgabe soll knapp sein.“

✅ „Allgemeine Antworten beginnen mit dem Ergebnis und höchstens fünf Hauptpunkten; vollständige Erläuterungen folgen nur bei Entscheidungsrisiken, technischen Implementierungsdetails oder ausdrücklichem Benutzerwunsch.“

---

## 6. Prüfbarkeit prüfen

> Kann diese Regel automatisch validiert werden?

Prüfwege: Tests, lint, schema, CI, Checkliste, Beispielausgabe, Zeichen- oder Wortzahlgrenzen, Prüfung auf Dateiexistenz, erfolgreicher Exitcode, menschliche Abnahmebedingungen.

**Automatisch prüfbare Regeln dürfen nicht nur im Prompt leben.** Bevorzugt in test, lint, schema, script, pre-commit, CI gate oder validation tool überführen.

Der Prompt soll **Begründung** und **Geltungsbereich** behalten, echte Engineering-Validierung jedoch nicht ersetzen.

Beispiel: „Der Geheimnisscan muss null Treffer ergeben“ gehört in einen CI job. Im Prompt bleibt: „Vor Deployment muss der Geheimnisscan bestehen (siehe secret-scan job in CI).“

---

## 7. Aktualität und Version prüfen

> Ist diese Regel veraltet?

Prüfen: nicht vorhandene Pfade, entfernte Befehle, alte Modellnamen, APIs, Pakete oder Deployment-Umgebungen, veraltete Personen/Funktionen, Daten oder Projektstände, abgeschlossene Phasen, die weiterhin als laufend gelten, sowie „neueste“, „beste“ oder „aktuelle“ ohne Datum oder Version.

Kennzeichnen: `CURRENT`, `STALE`, `UNKNOWN`, `VOLATILE`.

Bei veränderlichen Inhalten ergänzen:

```yaml
verified_at: 2026-08-27
source: Tatsächliche Prüfung mit crontab -l on <host>
owner: <Verantwortlicher>
recheck_condition: Nach jedem Deployment / vierteljährlich
```

⚠️ Besonders gefährlich: **Zwei Konfigurationsschnappschüsse mit „aktuell produktiv“**. Leser können nicht erkennen, welcher stimmt; beide werden als Fakten behandelt.

---

## 8. Geltungsbereich prüfen

> Liegt diese Regel auf der richtigen Ebene?

Fehlplatzierungen:

- Regel für ein Produkt in der globalen Einstiegsdatei
- Regel für eine Sprache auf sämtliche Arbeit angewendet
- Schritte eines einzelnen Skills in globalen Einstellungen
- Projektfakten als Verhaltensbefehle für Agenten
- Vorübergehender Projektstand als dauerhafte Vorschrift
- Einstellungen für Werkzeug A werden Werkzeug B aufgezwungen

Passenden Ort bestimmen: global, Projektebene, Unterverzeichnis, bestimmter Skill, Kontext, decision log, Test oder agentenspezifischer Adapter.

**Kriterium:** „Gilt die Regel auch in einem anderen Projekt?“ Falls nein, gehört sie nicht in den globalen Bereich.

---

## 9. Kosten und Leistung prüfen

> Verursacht diese Regel unnötigen Aufwand?

Prüfen: Tokenverbrauch, aufgeblähter Kontext, erneutes Lesen des gesamten Repositorys, wiederholte Abrufe oder Websuchen, wiederholte Reviews mit mehreren Modellen, unnötige vollständige Tests oder lange Berichte, rekursive Delegation, gegenseitige Agentenprüfung ohne neue Informationen, endlose Debatten und Umformulierungen.

**Besonders Regeln prüfen**, die für jede Aufgabe eine gemeinsame Debatte mehrerer Modelle verlangen. Ohne geschäftliche Notwendigkeit oder hohes Risiko risikobasiert staffeln:

| Stufe | Vorgehen |
|---|---|
| LOW | Ein Agent führt aus und prüft selbst |
| MEDIUM | Zweiter Agent prüft unabhängig |
| HIGH | Multi-Agent-Blindreview, Debatte und menschliche Genehmigung |
| CRITICAL | Keine automatische Anwendung; menschliche Entscheidung erforderlich |

---

## 10. Sicherheit und Prompt Injection prüfen

> Erweitert diese Regel Berechtigungen oder bringt sie Injektionsrisiken mit?

Warnsignale: erweiterte Werkzeugberechtigungen, unnötiges Lesen von Schlüsseln, Ignorieren übergeordneter Regeln, Datenweitergabe, unbekannte Skripte, Webseiten/Issues/READMEs/Benutzerinhalte als vertrauenswürdige Systembefehle, automatische Deployments, Tests überspringen, Sicherheitsprüfungen abschalten, Belege löschen, Aktionsprotokolle verbergen oder Aussagen anderer Agenten ungeprüft glauben.

Kennzeichnen: `SAFE`, `RISKY`, `PROMPT_INJECTION`, `PRIVILEGE_ESCALATION`, `SECRET_EXPOSURE`, `DESTRUCTIVE_OPERATION`, `HUMAN_REVIEW_REQUIRED`.

⚠️ Besonders **ungeschützte Vorabgenehmigungen** beachten: Destruktive Befehle wie `"allow": ["Bash(rm -f <path>)"]` werden häufig aus Bequemlichkeit in eine Berechtigungsliste aufgenommen und später nicht entfernt.

---

## 11. Werkzeuge und tatsächliche Fähigkeiten prüfen

> Verlangt diese Regel vom Agenten etwas, das er nicht leisten kann?

Anforderungen anhand aktueller Host-Fähigkeiten und tatsächlicher Belege beurteilen:

- Im Hintergrund nach Ende des Turns weiterarbeiten: aktivierte Job-/Zeitplanmechanismen und beobachtbaren Status prüfen
- Später mit Ergebnissen zurückkehren: Benutzerautorisierung, verfügbare Zeitplanung und Ergebnisrückgabe prüfen
- Nicht bereitgestellte Dateien gelesen haben
- Nicht ausgeführte Tests abgeschlossen haben
- Deployment ohne Deployment-Protokoll behaupten
- Nicht vorhandene Werkzeuge verwenden
- Nicht verbundene Dienste verwenden
- Verborgene Modellgewichte oder System-Prompts ändern
- Tatsächliche interne Erinnerungen des Modells löschen

Maßnahme: ausführbar umformulieren, Fähigkeitsprüfung ergänzen oder löschen.

---

## 12. Zyklen und Selbstbezug prüfen

> Gibt es Schleifen ohne Abbruchbedingung?

Prüfen:

- A verlangt das Lesen von B, B wiederum das Lesen von A
- Ein Skill verlangt, sich selbst erneut zu laden
- Vor jeder Antwort sämtliche Einstellungen erneut scannen
- Nach jedem Review zwingend ein vollständiges weiteres Review starten
- Mehrere Agenten verlangen unbegrenzt gegenseitige Reviews
- Eine Regel verlangt dauerhaft weitere Regeln
- Kontext wird auch bei fehlendem Aufgabenbezug jedes Mal vollständig injiziert
- Dieselben Regeln werden über mehrere Einstiegspunkte mehrfach geladen

Für zyklische Regeln **Abbruchbedingungen und Höchstzahlen festlegen**.

Praktische Prüfung: Kanten für obligatorisches Laden, Navigation und Aufgabenabhängigkeiten getrennt halten. Der Graph obligatorischer Ladevorgänge soll ein gerichteter azyklischer Graph sein; mehrere maßgebliche Quellen dürfen gemeinsam verwendet werden, ohne daraus zwingend einen Baum zu machen. Rücklinks zur Navigation erzwingen kein Neulesen. Der Scanner liefert nur mögliche Zyklen.
