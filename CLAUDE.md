# LinguaBosna – Projektkontext für Claude Code

## Über das Projekt

LinguaBosna (linguabosna.com) ist eine kostenlose Lernwebseite für die bosnische Sprache und Kultur,
primär für deutschsprachige Lerner und die bosnische Diaspora im DACH-Raum. Sprachniveau A1–C2.

**Wichtigste Prämisse: Kosten sehr gering halten.** Kein Backend, keine Paid-Services.
Reines HTML/CSS/JavaScript, kein Framework. Statisches Hosting über GitHub Pages.

**Kommunikationssprache:** Deutsch (auch in dieser Datei und in allen Sessions).

## Kenntnisstand des Projektinhabers

Alen hat nur Grundkenntnisse in Webdesign/Programmierung.
- Code ausreichend kommentieren.
- Lösungen verständlich erklären, nicht nur Ergebnisse liefern.
- Bei Dateiersatz: **denselben Dateinamen wie die alte Datei übernehmen.**
- Vor jedem Git-Commit/Push die Änderungen zeigen und explizit bestätigen lassen –
  besonders bei sprachlichen Inhalten (siehe unten).

## Tech-Stack & Repository

- Repository: github.com/Alenp93/LinguaBosna
- Lokal unter: `C:\Website\LinguaBosna`
- Hosting: GitHub Pages
- Analytics: GoatCounter (privacy-safe, DSGVO-konform, cookielos) – injiziert via `createElement`/`appendChild`
- Domain & E-Mail-Weiterleitung: Namecheap (WhoisGuard aktiv)
- Header/Footer werden dynamisch per JS eingebunden (`LB_main.js`), nicht statisch pro Seite kopiert
- **Alle Fetch-Pfade und Asset-Referenzen sind absolute Pfade** (z. B. `/Code/LB_header.html`),
  da relative Pfade bei verschachtelten Unterordnern brechen. Absolute Pfade benötigen einen
  Webserver-Kontext (kein `file://`-Testen im Browser ohne lokalen Server).

## Zielgruppe & Sprachliche Ausrichtung

- Diaspora, Deutschsprachige, Kinder/Jugendliche/Erwachsene, Fortgeschrittene
- **Bosnisch-Standard:** konsequent ijekavisch, bosnisch-spezifische Varianten statt
  kroatischer/serbischer Alternativen. Turzismen werden als authentische Sprachmarker behandelt,
  nicht vermieden.
- BKS-Grammatik (Bosnisch/Kroatisch/Serbisch) wird als gemeinsame Basis betrachtet –
  kroatische und serbische Grammatikquellen dürfen als Referenz herangezogen werden, wo sinnvoll.
- **Diaspora-first-Vokabular:** Registerpaare, Bosnismen, Verwaltungs-/Rechtsbegriffe sind bei
  B1–C2 bewusst eingewoben.
- ⚠️ Sprachliche Inhalte (Grammatikerklärungen, Übersetzungen, Vokabeln) sind fehleranfällig
  bei ijekavischer Form und Register. Erstentwürfe sind ok, aber vor Veröffentlichung
  gemeinsam mit Alen prüfen, nicht automatisch committen.

## Design-System (verbindlich für jede Seite)

**Farben:**
- Dunkelblau `#0A3D62` (Primär – Header, Buttons, Überschriften)
- Goldgelb `#F4C542` (Akzent – Highlights, Icons, CTAs)
- Dunkelgrün `#2E5E2E` (Sekundär – Slogan, Untertitel, Zitate)
- Hintergrund hell `#F8F5F0`
- Neutral Grau `#E6E6E6` (Linien, Rahmen, Boxen)

**Typografie:**
- Überschriften: Montserrat SemiBold/700, Großbuchstaben bei Haupttiteln, `letter-spacing: 0.5px`
- Fließtext: Open Sans Regular
- Zentrale CTAs: Montserrat Bold
- Google Fonts Pflichtblock im `<head>` jeder Seite (Montserrat 400/600/700 + Open Sans 400/600)

**Button-System (einheitlich):**
- `.btn-hero` – Goldgelb, Hero-Bereiche
- `.btn-outline` – nur Umrandung, sekundäre Aktionen
- `.btn-primary` – Dunkelblau, Hauptaktionen
- Alle: `border-radius: 6px`, Montserrat Bold, Hover-Effekt Goldgelb → Dunkelblau mit weißer Schrift

**Section-Intro-Block:**
```html
<div class="section-intro">
  <h2>Titel</h2>
  <p>Untertitel</p>
</div>
```

**Karten-Hover (Feature/Blog/Vokabel/Grammatik-Karten):**
```css
transition: transform 0.3s ease, box-shadow 0.3s ease;
/* Hover: */
transform: translateY(-6px);
box-shadow: 0 12px 30px rgba(0,0,0,0.13);
```

**Abstände (Padding):**
- Desktop: `70px 5%`
- Tablet (≤900px): Schriftgrößen reduzieren
- Mobile (≤768px): `50px 5%`, 1-spaltige Layouts
- Sehr klein (≤480px): `40px 4%`
- Button-Stacking-Breakpoint bei 900px (nicht 768px), 44px Mindest-Touch-Targets

**FontAwesome:** 6.5.0 via cdnjs — `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css`
(NICHT den alten Kit-Link verwenden)

**SEO-Pflicht pro Seite:**
- `<meta name="description" content="...">` (~150 Zeichen)
- `<title>LinguaBosna – [Seitenname]</title>`

**Favicon-Pflicht (B1+ Seiten, mandatory 6-Einträge-Block):** `/Bilder/favicon/`

## Referenzseite

`LB_1_Startseite.html` + `Style_1_Startseite.css` sind die fertige Designreferenz für alle weiteren Seiten.

## Grammatikseiten erstellen – IMMER zuerst diese Dateien lesen

Für Grammatikseiten gibt es eine vollständige, verbindliche Arbeitsgrundlage im Repo selbst.
**Bevor du eine neue Grammatikseite erstellst oder änderst, lies zuerst:**

1. `WORKFLOW_Grammatikseiten.md` – enthält alle festen Regeln (Dateinamen, 6-Block-Struktur,
   exakte Quiz-IDs, Antwortverteilung, Pfade, Kapitel-Taxonomie A1–C2, Didaktik-Checkliste,
   Ablageorte im Repo, Antwortformat der Auslieferung)
2. `TEMPLATE_Grammatik_Detailseite.html` – Boilerplate mit `[ECKIGE KLAMMERN]`-Platzhaltern
3. `test_grammatikseite.py` – Pflicht-Validierung nach jeder neuen/geänderten Seite
   (Aufruf: `python3 test_grammatikseite.py grammatik-[thema].html`; findet Repo-Root und
   CSS-Dateien automatisch, prüft Mobile-Overflow, Struktur, Quiz-IDs und mehr)
4. `.claude/agents/bosnisch-pruefer.md` – Subagent für die unabhängige sprachliche
   Zweitprüfung (ijekavisch, Bosnisch vs. kroatisch/serbisch, Turzismen, Register,
   Konsistenz mit `vokabeln_flat.json`). MUSS nach jeder neuen/geänderten Grammatikseite
   aufgerufen werden, zusätzlich zu `test_grammatikseite.py` – prüft Sprache, nicht Struktur.
   Nur Leserechte (Read/Grep/Glob/WebSearch), korrigiert nichts selbst, liefert nur eine
   ✓/⚠-Liste zur Entscheidung durch Alen.

Diese Datei hier dupliziert diese Regeln bewusst **nicht** – WORKFLOW_Grammatikseiten.md ist
die Quelle der Wahrheit, damit nichts auseinanderdriftet. Nach jeder neuen Seite: entsprechende
Karte in `LB_3_Grammatik.html` von „Demnächst" auf aktiven Link umstellen (siehe Workflow-Doku).

## Lernen-Bereich erstellen – IMMER zuerst diese Datei lesen

Für den „Lernen"-Bereich (Übungsaufgaben zu Grammatik + Vokabeln, ergänzend zu den
Grammatik-Erklärseiten und dem Vokabeltrainer) gibt es eine eigene Arbeitsgrundlage,
analog zu WORKFLOW_Grammatikseiten.md:

1. `WORKFLOW_Lernen.md` – enthält feste Regeln je Übungstyp (Dateinamen, Ablageorte,
   Interaktionsmuster, Datenquellen-Prinzip, Pool-Größen-Richtwerte, Status-Übersicht
   aller Übungstypen, Validierungs- und Auslieferungs-Workflow)

**Bevor du eine neue Lernen-Übung erstellst oder änderst, lies zuerst
`WORKFLOW_Lernen.md`.** Diese Datei hier dupliziert die dortigen Regeln bewusst
nicht, aus denselben Gründen wie bei den Grammatikseiten. Nach jeder neuen/geänderten
Übung: Status-Tabelle in `WORKFLOW_Lernen.md` aktualisieren.

## Vokabular-System

- Kanonische Datei: `vokabeln_flat.json` – ca. 1.943 Einträge über 72 Kapitel (A1–C2)
- JSON-Schema: `"Wortart (Genus)"` für Substantive, `"Wortart"` für andere Wortarten –
  **diese Konvention darf nicht gebrochen werden**
- Verben: `aspekt`-Feld, 27 Aspektpaare über `par_id` (`ap01`–`ap27`) verlinkt
- **Kapitelgrößen-Regel (fix):** kein Kapitel über 35 Einträge. Größere Themen werden thematisch
  in nummerierte Teile gesplittet (z. B. "Umgangssprache & Bosnizismen 1 / 2")

**Build-Pipeline (sequentiell, Reihenfolge beachten):**
```
build_a1.py → build_a2.py → build_order.py → build_b1.py → build_b1_expand.py →
build_b1_split.py → build_b2.py → build_resplit.py → build_c1.py → build_c2.py → build_parid.py
```
`build_resplit.py` enthält die autoritative MASTER-Kapitelliste und globale Neunummerierung –
diese Datei ist am kritischsten für Konsistenz.

## Bekannte Lösungen / Fallstricke (nicht wiederholen)

- **Mobile Overflow (Grammatik-Tabellen) – aktuelle Lösung (Juli 2026):** Tabellen sollen
  auf schmalen Viewports **ganze Wörter behalten** und bei Bedarf **horizontal scrollen**
  (statt Wörter mitten im Wort umzubrechen – für Lernende schlecht lesbar). Verbindlich in
  `Style_3_Grammatik_Detail.css`, global für alle `.letter-table`:
  - `.letter-table { table-layout: auto }` + `overflow-wrap: normal; word-break: normal;
    hyphens: none` auf `th`/`td` → Spalten nach Inhalt, Wörter bleiben komplett.
  - `.letter-table-wrap { overflow-x: auto; max-width: 100% }` → der **Wrapper** scrollt,
    nicht die Seite; ein Rand-Fade (CSS-Gradient, kein JS) signalisiert den Überlauf.
  - **Schlüssel-Fix (ohne den scrollt der Wrapper NICHT):** `main { width: 100% }`. `main` ist
    ein Flex-Item (`body` ist `display:flex; flex-direction:column`, `main` hat `flex:1`).
    Ohne feste Breite schrumpft `main` auf **Inhaltsbreite** und wird von einer breiten Tabelle
    über den Viewport gebläht; `body { overflow-x:hidden }` klippt den Überlauf dann unsichtbar
    (weder Seite noch Wrapper scrollen). `width:100%` bindet `main` an die Viewport-Breite,
    erst dadurch greift `overflow-x:auto` am Wrapper. (`box-sizing:border-box` ist global.)
  - Empirisch mit `test_grammatikseite.py` (Playwright, 320–900 px) bestätigt: 0 Seiten-Überlauf,
    breite Tabellen scrollen intern. **Achtung:** `min-width:0` an `main` allein behebt das
    **nicht** – nur `width:100%` wirkt. Diese Regel gilt für **alle** Tabellen der Seite.
  - *Historie:* Bis Juli 2026 war der Fix `table-layout: fixed` + `overflow-wrap: break-word`
    (feste Spalten, lange Wörter brachen um). Das ist bewusst umgekehrt worden – nicht
    versehentlich auf `table-layout: fixed` zurücksetzen.
- **Scripts via innerHTML laufen nicht:** GoatCounter und Hamburger-Menü-Logik müssen über
  `createElement`/`appendChild` in `LB_main.js` eingebunden werden, nicht in
  `LB_header.html`/`LB_footer.html`.
- **Quiz-Antwortabgleich:** über Objektreferenzen (`btn._vocab === correctV`), nicht Textvergleich.
- **Flashcard-Flicker:** über `visibility: hidden` mit `.preparing`-Klasse + doppeltes
  `requestAnimationFrame`.
- **Mobile Audio:** `speak()` muss direkt innerhalb einer User-Geste aufgerufen werden –
  kein Warm-up/setTimeout-Wrapper (bricht Android-Audio).
- **Hamburger-Init:** muss innerhalb des `.then()`-Callbacks in `LB_main.js` laufen,
  nachdem der Header-HTML ins DOM injiziert wurde.
- **Audio-Feature:** aktuell pausiert, kompletter Audio-Code aus
  `LB_2-1_Vokabeln_Master.html` entfernt. Geplant: vorgenerierte MP3s (Google Cloud TTS)
  als primäre Lösung + Web Speech API als Fallback (Reihenfolge: `bs-BA` → `hr-HR` → `sr-RS` → `cnr-ME`).

## Validierungs-Workflow

Nach jeder neuen/geänderten Grammatikseite zwei getrennte Prüfungen durchführen, bevor
committed wird:

1. **Struktur:** `test_grammatikseite.py` ausführen (Details siehe
   `WORKFLOW_Grammatikseiten.md`, Abschnitt 5)
2. **Sprache:** `bosnisch-pruefer`-Subagent aufrufen (siehe oben)

Beide Ergebnisse Alen zeigen, bevor committed wird. Ein grüner Struktur-Test bedeutet nur
„technisch sauber", nicht „sprachlich korrekt" – beide Prüfungen sind nötig, keine ersetzt
die andere.

Für Lernen-Übungen gilt der Sprach-Check (bosnisch-pruefer) ebenso; die Struktur-Prüfung
ist dort noch offen (siehe `WORKFLOW_Lernen.md`, Abschnitt 6).

**Einmalige lokale Einrichtung (falls noch nicht geschehen):** Das Skript braucht Playwright.
Falls der Testlauf mit „Playwright nicht installiert" fehlschlägt, einmalig ausführen:
```
pip install playwright --break-system-packages
playwright install chromium
```

## Pausierte / auskommentierte Bereiche

Kultur- und Blog-Navigationslinks in `LB_header.html` sind bewusst auskommentiert
(Inhalte noch nicht fertig) – nicht versehentlich reaktivieren. Ebenso die
Kultur-Feature-Karte in `LB_1_Startseite.html`.

Der „Lernen"-Menüpunkt ist dagegen **aktiv** (`LB_header.html`, verlinkt auf
`/Code/4_Lernen/lernen-uebersicht.html`), seit die ersten Übungen (Lückentext,
Aspektpaare) fertig sind.

## Roadmap (zur Priorisierung, falls relevant)

- B2–C2 Grammatikkapitel (interne Kommentarnummern 24–37 in `LB_3_Grammatik.html`)
- Lernen-Bereich: weitere Übungstypen (siehe `WORKFLOW_Lernen.md`, Status-Übersicht)
- SEO: Google Search Console, sitemap.xml, robots.txt, schema.org, Long-Tail-Keywords
- Audio-Feature reaktivieren (Google Cloud TTS Free Tier)
- Mögliche zukünftige englische Version (nach Phase 3; JSON hat bereits English-Feldgrundlage)
- Kultur-/Blog-Sektionen aktivieren, sobald Grammatik weiter fortgeschritten ist

## Arbeitsweise

- Ein Thema/eine Seite pro Session (kein Vermischen mehrerer Grammatikkapitel in einem Auftrag)
- Vollständige Ersatzdateien bevorzugt gegenüber manuellen Patches – bei Claude Code heißt das:
  klare, überprüfbare Diffs statt vieler kleiner Einzeländerungen
- Mobile-first-Denken bei jeder CSS-Änderung
