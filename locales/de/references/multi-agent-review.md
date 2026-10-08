# Review-Prozess mit mehreren Agenten

---

## Bei mindestens zwei **tatsächlich unabhängigen** Modellen

### Runde 1: Blindreview

| Rolle | Aufgabe | Grenze |
|---|---|---|
| Auditor A | Dateiinventar, Regelatomisierung, Konflikt- und Duplikatanalyse | **Die Schlussfolgerungen von B nicht vorher lesen** |
| Auditor B | Dasselbe Audit unabhängig durchführen | **Die Löschvorschläge von A nicht vorher lesen** |

### Runde 2: Gegenseitiges Review

Die Ergebnisse vergleichen und finden:

- Regeln, die A löschen und B behalten möchte
- Regeln, die A als Konflikt und B als unterschiedlichen Geltungsbereich beurteilt
- **Von beiden übersehene Regeln**, die wertvollsten Befunde
- Abweichende Bewertungen zu Sicherheit, Deployment und Datenintegrität
- Unterschiede bei der Einordnung als einmaliger Patch oder allgemeine Regel

### Runde 3: Governance-Entscheidung

Die integrierende Instanz erstellt den endgültigen Vorschlag. **Bei wesentlichen Differenzen beide Begründungen erhalten; keinen Konsens vortäuschen.**

---

## Bei nur einem Agenten, dem häufigen Fall

Zwei Prüfungen mit unterschiedlichen Schwerpunkten durchführen:

| Runde | Schwerpunkt | Haltung |
|---|---|---|
| Erste | Vollständigkeit und Erhaltung | Im Zweifel mehr behalten; zunächst keine Regeln übersehen |
| Zweite | Vereinfachung, Konflikte und Kosten | Duplikate, Widersprüche, veraltete Inhalte und Aufblähung gezielt suchen |

**Ausdrücklich kennzeichnen:**

> Dies sind zwei Prüfungen eines einzigen Modells mit unterschiedlichen Schwerpunkten, **kein Blindreview zweier unabhängiger Modelle**.

### Strikt untersagt

**Zwei Selbstprüfungen eines Agenten dürfen nicht als unabhängige Prüfung durch Dritte beschrieben werden.**

Das ist eine grundlegende Ehrlichkeitsanforderung. Zwei Selbstprüfungen sind nützlich; die zweite kann Übersehenes entdecken. Sie teilen aber dieselben Verzerrungen und sind keine unabhängige Validierung.

---

## Praktischer Ansatz: paralleles Audit nach Bereichen

Bei Hunderten Regeln kann die Ausgabe eines Agenten die Grenzen überschreiten. Empfohlene Aufteilung:

```
Bereich A: Einstiegsdateien auf Benutzerebene + Einstellungen
Bereich B: größte Projektanweisungsdatei, ggf. weiter unterteilen
Bereich C: weitere Projektdateien + Erinnerungsdateien
Bereich D: dateiübergreifende Konflikte und Duplikate zwischen A/B/C
Bereich E: Sicherheit, Injection, Fähigkeiten und Zyklen; gefährliche Kategorien
Bereich F: completeness critic; von allen übersehene Positionen suchen
```

**Bereich F wird leicht weggelassen, entdeckt aber oft die wichtigsten Punkte.** Beispielsweise prüfen alle `CLAUDE.md`, während die ebenso große `AGENTS.md` daneben unbeachtet bleibt.

### Zu große Ausgaben behandeln

Wenn die Regeln eines Bereichs zu einer abgeschnittenen Ausgabe führen:

1. **Keine Fertigstellung vortäuschen.**
2. Abschnittsweise vorgehen, beispielsweise drei Teile nach Kapiteln.
3. Im Bericht ehrlich angeben: „Bereich noch nicht abgeschlossen; ergänzende Bearbeitung in Abschnitten läuft.“
4. Nach Abschluss Ergebnisse ergänzen und Validierungspunkte aktualisieren.

---

## Entscheidungsgrundsätze bei gegenseitigem Review

Bei unterschiedlichen Audit-Schlussfolgerungen:

| Situation | Entscheidung |
|---|---|
| Eine Seite hat tatsächliche Belege, die andere Vermutungen | **Belegte Bewertung** |
| Eine Seite sagt „sicher“, die andere „riskant“ | **Strengere Bewertung**, sofern keine Belege die Risikofreiheit zeigen |
| Eine Seite sagt „Duplikat“, die andere „anderer Geltungsbereich“ | Geltungsbereich und maßgebliche Quelle prüfen; gleichzeitiges Laden verursacht Duplikatkosten. Kopien derselben Regel in unterschiedlichen Sessions ebenfalls auf Versionsaufspaltung prüfen. Nur tatsächlich unterschiedliche Bereiche rechtfertigen Erhaltung. |
| Eine Seite will löschen, die andere behalten | Standardmäßig **behalten**, außer die löschende Seite zeigt eine Ersatzregel |

Jede Entscheidung dokumentiert Konfliktinhalt, übernommene Regel, Begründung, Umgang mit der ersetzten Regel und Bedarf an menschlicher Bestätigung.

## Unabhängige Kontexte und unterschiedliche Modelle

Unabhängige Kontexte desselben Modells können Reviews durchführen, gelten aber nicht als Validierung durch unterschiedliche Modelle. Nur notwendige, maskierte Daten delegieren und ausschließlich tatsächlich verfügbare, autorisierte Mechanismen verwenden. Keine unbekannten Werkzeuge starten, nicht rekursiv delegieren und keine unbegrenzten gegenseitigen Reviews. Reviewer lesen Dateien und Testbelege zurück; Fertigstellungsbehauptungen der ausführenden Instanz nicht ungeprüft übernehmen.
