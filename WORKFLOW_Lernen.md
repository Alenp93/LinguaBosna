# WORKFLOW: Lernen-Bereich (Übungsaufgaben) erstellen

> Prozess-Referenz für LinguaBosna. Gehört ins Project Knowledge, analog zu
> `WORKFLOW_Grammatikseiten.md`.
>
> ✅ **Status dieser Datei:** Gegen den echten Repo-Stand von `Code/4_Lernen/`
> abgeglichen (Stand 2026-07-17). Die früheren 🔲-Platzhalter sind ausgefüllt.
> Einzig offen: die Struktur-Validierung (Abschnitt 6) – dort ist noch eine
> Entscheidung durch Alen nötig.

---

## 1. Zweck des Lernen-Bereichs

Ergänzt die Grammatik-Erklärseiten (Verständnis) und den Vokabeltrainer
(Wortschatz-Abruf) um **wiederholtes, gezieltes Üben einzelner
Grammatikthemen unter Einbindung der Vokabel-JSON**. Anders als das
10-Fragen-Quiz auf jeder Grammatikseite (dient der einmaligen
Selbstkontrolle direkt nach dem Lesen) ist der Lernen-Bereich auf
**Wiederholung zur Festigung** ausgelegt – daher die größeren Sätze-/Item-Pools
(siehe Abschnitt 4).

---

## 2. Feste Regeln (für alle Übungstypen gemeinsam, nie abweichen)

| Regel | Wert |
|---|---|
| Dateiname Übungsseite | `lernen-[typ].html` (klein, Bindestriche) |
| Ablageort Übungsseiten | `Code/4_Lernen/` (bestätigt) |
| Übersichtsseite | `Code/4_Lernen/lernen-uebersicht.html` (existiert, fertig) – listet alle Übungen als Karten im Raster `.uebung-grid`; neue Übung = weitere `<a class="thema-card">`-Karte |
| Interaktionsmuster | **Klickbasierte Auswahl, kein Drag & Drop** (Mobiltauglichkeit) – gilt für alle Übungstypen, auch „Zuordnung" |
| Design-System | wie überall im Projekt (siehe CLAUDE.md) – hier nicht dupliziert |
| Pfade | immer absolut (`/Code/...`, `/Bilder/...`) |
| Favicon-Block | Pflicht auf jeder neuen Seite |
| SEO-Block | Pflicht wie bei Grammatikseiten: eindeutiger `<title>`, `description`, **Canonical**, Open Graph (og:title/description/url/image), Twitter Card. JSON-LD optional (`LearningResource`). `<meta charset>`+`viewport` als erstes im Head |
| Menüpunkt „Lernen" | **aktiv** in `LB_header.html` (Zeile 37): `<li><a href="/Code/4_Lernen/lernen-uebersicht.html">Lernen</a></li>`. Kultur/Blog bleiben weiter auskommentiert. ⚠️ Hinweis: CLAUDE.md („Pausierte Bereiche") beschreibt den Lernen-Menüpunkt noch als auskommentiert – dort ggf. nachziehen |
| JS-Einbindung | `/Code/LB_main.js` im head **mit `defer`**; Header/Footer via `<div id="header">` / `<div id="footer">` |

---

## 3. Datenquellen-Prinzip

**Grundsatz: vorhandene `vokabeln_flat.json` bevorzugen, eigene JSON nur wo nötig.**

- Übungen, die sich direkt aus vorhandenen Feldern ableiten lassen
  (z. B. Aspektpaare über `par_id` + `aspekt`, Genus über `Wortart (Genus)`),
  **brauchen keine neue Datendatei** – nur Filter-/Gruppierungslogik in JS.
- Übungen, die vollständige Beispielsätze brauchen (z. B. Lückentext,
  Satzbau-Puzzle), brauchen zwingend eine **eigene JSON-Datei**, da
  `vokabeln_flat.json` nur Einzelwörter enthält, keine Sätze.
- Neue Datendateien liegen unter `Code/4_Lernen/[typ]_data.json` (bestätigt,
  z. B. `Code/4_Lernen/luckentext_data.json`).

---

## 4. Pool-Größen-Richtwerte

Grundprinzip: 10 Items pro Übungsrunde sind richtig (Quiz-Standard), aber
der **Gesamt-Pool**, aus dem per `Math.random()` zufällig ausgewählt wird,
muss deutlich größer sein – sonst lernt der Nutzer die Antwortmuster statt
der Grammatikregel.

| Themenbreite | Beispiel | Pool-Größe |
|---|---|---|
| Schmal | Vokativ, Possessivpronomen | 25–35 |
| Mittel | Komparation, Konditional I | 35–50 |
| Breit | Akkusativ, Verbalaspekt | 50–80 |

Technische Umsetzung: `Math.random()`-basierte Auswahl von 10 Items ohne
Wiederholung aus dem Pool bei jedem Seitenaufruf/Neustart. Bei
Übungstypen ohne eigene Datendatei (z. B. Aspektpaare über `par_id`)
entspricht der „Pool" der Anzahl vorhandener `par_id`-Gruppen in
`vokabeln_flat.json` – dieser wächst automatisch mit, wenn neue
Aspektpaare in der Vokabel-JSON ergänzt werden.

---

## 5. Status-Übersicht der Übungstypen

> Diese Tabelle bitte nach jedem neuen/geänderten Übungstyp aktualisieren.

| Übungstyp | Status | Datei | Datenquelle | Pool |
|---|---|---|---|---|
| Übersicht „Lernen" | ✅ fertig | `Code/4_Lernen/lernen-uebersicht.html` | – (statische Kartenliste) | – |
| Vokabeltrainer | ✅ fertig | `Code/2_Vokabeln/vokabeltrainer.html` | `vokabeln_flat.json` (alle Kapitel) | – |
| Lückentext mit Wortbank | ✅ Pilot fertig (Akkusativ) | `Code/4_Lernen/lernen-luckentext.html` | eigene JSON (`Code/4_Lernen/luckentext_data.json`) | 80 Sätze (Thema `akkusativ`) |
| Aspektpaar-Zuordnung | ✅ fertig | `Code/4_Lernen/lernen-aspektpaare.html` | `vokabeln_flat.json` (`par_id`, `aspekt`) | 85 Paare (`ap01`–`ap85`, lückenlos), 3 Sets: A1–A2 (51) / B1–C1 (34) / alle (85) |
| Satzbau-Puzzle (Enklitika/Wortstellung) | 📋 geplant | – | eigene JSON nötig | – |

---

## 6. Validierung

- **Sprache:** `bosnisch-pruefer`-Subagent auch für Lernen-Inhalte aufrufen
  (Distraktoren eingeschlossen – auch falsche Optionen müssen sprachlich
  sauber sein, nicht nur die korrekte Lösung).
- **SEO:** `python3 test_seo.py <datei>` prüft die SEO-Grundausstattung auch für
  Lernen-Seiten (Canonical, Open Graph, Twitter, gültiges JSON-LD, Description-Länge,
  offene `[PLATZHALTER]`, `defer`). Nach einer neuen Übung zusätzlich
  `python3 build_sitemap.py` ausführen und die aktualisierte `sitemap.xml` mitcommitten.
- **Struktur (Mobile/Layout):** ⚠️ Weiterhin offen – es existiert **kein**
  `test_grammatikseite.py`-Äquivalent (Mobile-Overflow/Touch-Targets) für Lernen-Seiten.
  `test_seo.py` deckt nur die SEO-Metadaten ab, nicht das Layout. Bis ein eigenes
  Struktur-Skript existiert: neue/geänderte Übungen mindestens manuell auf Mobilgeräten
  (Overflow, Touch-Targets) prüfen.
- Wie bei Grammatikseiten: Vor jedem Commit Alen die Änderungen zeigen und
  explizit bestätigen lassen, besonders bei neuen Beispielsätzen/Distraktoren.

---

## 7. Antwortformat der Auslieferung

Analog zu Grammatikseiten:
- Kurzer didaktischer Vorspann vor der Dateierstellung (welches Thema,
  welche Untermuster werden abgedeckt)
- Nach Fertigstellung: Zusammenfassung (Aufbau, Datenquelle, Pool-Größe,
  sprachlicher Hinweis auf bewusst Weggelassenes)
- To-dos für Alen benennen (z. B. Übersichtskarte in `LB_4_Lernen.html`
  aktivieren, Menüpunkt-Reaktivierung, Verlinkung von der passenden
  Grammatikseite aus)
