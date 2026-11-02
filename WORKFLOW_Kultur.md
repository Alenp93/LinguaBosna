# WORKFLOW: Kultur-Beiträge – LinguaBosna

Verbindliche Arbeitsgrundlage für den Kultur-Bereich. Analog zu
`WORKFLOW_Grammatikseiten.md` und `WORKFLOW_Lernen.md`: **Diese Datei ist die
Quelle der Wahrheit** – CLAUDE.md verweist nur hierher.

Stand: November 2026 · Grundlage: Konzept vom 02.11.2026, Entscheidungen von Alen

---

## 1. Wozu der Bereich da ist

Kultur ist bei LinguaBosna **der Einstieg zur Sprache**, kein eigenständiger
Kulturblog. Ein Beitrag soll Interesse wecken, nicht alles erklären. Daraus
folgen drei Grundsätze:

1. **Kurz statt vollständig.** 3–5 Minuten Lesezeit. Wer mehr will, findet es
   in den Quellen.
2. **Unterhaltsam, nie verletzend.** Humor über Situationen, nie über Gruppen
   („mitlachen, nicht auslachen").
3. **Jeder Beitrag führt zurück zur Sprache.** Pflichtblöcke „Wörter aus diesem
   Beitrag" (mit Link ins Wörterbuch) und „Weiter geht's" (Grammatik/Lernen).

**Kulturverständnis:** offen **bosnisch-herzegowinisch** – das ganze Land mit
allen Volksgruppen und Konfessionen (Bošnjaci, Kroaten, Serben, Juden, Roma …).
Die *Sprache* bleibt Bosnisch-Standard (ijekavisch, siehe CLAUDE.md); die
*Kultur* gehört allen, die in Bosnien und Herzegowina leben oder von dort kommen.

**Erscheinungsrhythmus:** etwa **ein Beitrag pro Woche**. Lieber regelmäßig und
kurz als selten und lang.

---

## 2. Dateien & Ablageorte

| Was | Wo |
|---|---|
| Übersichtsseite | `Code/5_Kultur/kultur-uebersicht.html` |
| Beiträge | `Code/5_Kultur/kultur-[thema].html` (flach, **keine** Rubrik-Unterordner) |
| Gemeinsames CSS | `Code/5_Kultur/Style_5_Kultur.css` (Übersicht + Beiträge) |
| Gemeinsames JS | `Code/5_Kultur/kultur.js` (Rubrik-Filter + Mini-Quiz) |
| Bilder | `Bilder/kultur/[thema].webp` (bzw. `[thema]-2.webp` …) |
| Vorlage | `TEMPLATE_Kultur_Beitrag.html` (Repo-Root) |
| Prüfskript | `test_kultur_beitrag.py` (Repo-Root) |
| Inhaltsprüfung | Subagent `.claude/agents/kultur-pruefer.md` (Kopie: `kultur-pruefer.md` im Repo-Root) |

- **Dateinamen nur ASCII:** `kultur-cevapi.html`, nicht `kultur-ćevapi.html`
  (Umlaut-/Sonderzeichen-Dateinamen sind unter Windows/Git/GitHub Pages eine
  bekannte Fehlerquelle, siehe Wörterbuch-Slugs in CLAUDE.md).
- **Warum keine Rubrik-Ordner?** Die Rubrik steht nur auf der Karte und im
  Beitrag. Wird eine Rubrik später umbenannt oder ein Beitrag umsortiert, bleibt
  die Adresse gleich – sonst brächen bereits geteilte Links.
- **Ein Dateiname ist endgültig**, sobald der Beitrag online ist.
- Interaktive Logik, die es nur in **einem** Beitrag gibt, steht als eigenes
  `<script>` am Ende dieses Beitrags, nicht in `kultur.js`.

### Rubriken (feste Namen und Schlüssel)

| Rubrik (Anzeige) | `data-rubrik` | Themenbeispiele |
|---|---|---|
| Familie & Zusammenleben | `familie` | Stammbaum, komšiluk, „Kad ćeš se udati?" |
| Essen & Trinken | `essen` | Pita, Ćevapi, Kahva, Ramazan-Tisch |
| Musik & Tanz | `musik` | Sevdah, Saz, Kolo |
| Tracht & Handwerk | `tracht` | Dimije, Fes, Ćilim, Kazandžije |
| Geschichte & Schrift | `geschichte` | Bosančica, Stećci, Povelja Kulina bana |
| Feste & Bräuche | `feste` | Bajram, Božić, Teferič, Sijelo |
| Diaspora & Humor | `diaspora` | Sommerfahrt, „Švabo", Mujo & Haso |

- **Keine eigene Farbe pro Rubrik** (Entscheidung Alen, November 2026 – sonst
  wirkt es zu bunt). Die Rubrik steht als grüner Text über dem Titel.
- Der Filter auf der Übersicht wird **automatisch** aus den Karten erzeugt
  (`kultur.js`). Eine neue Rubrik erscheint dort, sobald es eine Karte dazu gibt.
- **Mythen-Check** ist keine Rubrik, sondern ein Beitragstyp (siehe Abschnitt 3).

---

## 3. Beitragstypen

| Typ | Kennzeichen | Beispiel |
|---|---|---|
| **Erklärstück** | Standard, 2–4 Abschnitte | „Was ist eigentlich Sevdah?" |
| **Duell** | zwei Dinge im Vergleich, augenzwinkernd | „Burek vs. Sirnica" |
| **Wer ist wer?** | interaktives Element im Mittelpunkt | Familien-Stammbaum |
| **Top 5** | kurze Liste, je Punkt 2–3 Sätze | „5 Dinge, die nur die Diaspora kennt" |
| **Unübersetzbar** | ein Wort, eine Geschichte, kurz | merak, ćejf, inat, rahatluk |
| **Mythen-Check** | populäre Behauptung → was stimmt wirklich? | „Waren die Stećci Gräber der Bogumilen?" |

---

## 4. Aufbau eines Beitrags (8 Blöcke, Reihenfolge fest)

| # | Block | Regel |
|---|---|---|
| 1 | **Kopf** | Breadcrumb, Rubrik, `<h1>`, Unterzeile (1 Satz), Lesezeit, Bild (optional) |
| 2 | **Auf einen Blick** | **genau 3** Stichpunkte, je 1 Satz |
| 3 | **Abschnitte** | 2–4, Überschrift als **Frage**, je **höchstens ~120 Wörter** |
| 4 | **Interaktiv** | optional; ganzer Block entfällt, wenn keiner |
| 5 | **Wörter aus diesem Beitrag** | **5–10** Wörter, jedes verlinkt auf `LB_2-2_Woerterbuch.html?q=…` |
| 6 | **Mini-Quiz** | **4–6** Fragen à 3 Optionen, als JSON (`id="kulturQuizDaten"`) |
| 7 | **Weiter geht's** | **2–4** Links, mindestens einer zu Grammatik, Lernen oder Vokabeln |
| 8 | **Quellen & Bildnachweis** | 1–4 Quellen, Bildnachweis zusätzlich am Bild |

**Gesamtlänge:** ca. **400–900 Wörter** Fließtext (ohne Quiz, Tabellen und
Wörterliste). Lesezeit = Wortzahl ÷ 200, aufgerundet.
`test_kultur_beitrag.py` zählt nach und meldet Abweichungen.

**Lange Übersichten** (z. B. alle Verwandtschaftswörter) stehen in einer
zugeklappten `<details class="kultur-aufklapp">`-Tabelle: für Google und ohne
JavaScript vollständig im HTML, aber ohne die Seite optisch zu verlängern.

### Bosnische Wörter im Text

- Jedes bosnische Wort im deutschen Fließtext: `<strong lang="bs">amidža</strong>`
  (Screenreader-Aussprache + einheitliche Optik).
- **Wortform aus `vokabeln_flat.json`** – projektweit gilt die Form aus der JSON
  (z. B. `daidža`, nicht `dajdža`; `nana`/`dedo` als Bosnismen). Steht ein Wort
  noch nicht im Bestand, ist die Form frei, dann aber überall gleich.
- **Der Kultur-Bereich soll natürlich klingen** (Entscheidung Alen, November 2026):
  In wörtlicher Rede, Zitaten und Tetka-Fata-Sprüchen sind gesprochene Alltagsformen
  ausdrücklich erwünscht, auch wenn die Norm oder die JSON eine andere Form führt –
  z. B. „Hajde, sjedi!“ (statt normgerecht „sjedni“) oder „Kad ćeš se udati?“ (statt
  „kada“). Für Lemmata (Wörterliste, Tabellen, Quizoptionen) gilt weiter die JSON-Form.
- Beim ersten Vorkommen kurz übersetzen. Kein Lehrbuch-Ton, aber auch keine
  Wörter ohne Erklärung.

### Verlinkung

- **Keine `?kapitel=N`-Links** auf Vokabelkapitel. Kapitelnummern können sich
  ändern (siehe Neunummerierung August 2026 in CLAUDE.md); nur die
  Vokabelseiten selbst erzeugen solche Links aus den Daten. Stattdessen:
  Wörterbuch-Suche `?q=wort` – die findet das Wort unabhängig von seiner Nummer.
- Alle Pfade absolut (`/Code/…`, `/Bilder/…`).

---

## 5. Tonalität & die Figur „Tetka Fata"

**Grundton:** warm, selbstironisch, mit einem Augenzwinkern für die Diaspora,
so wie die Tetka beim Kaffee erzählt. Duzen. Kurze Sätze.

**Tetka Fata** ist die wiederkehrende Figur des Bereichs (Box
`.kultur-tetka`, 1–2 pro Beitrag, je 1–3 Sätze).

- Sie ist herzlich, neugierig, ein bisschen zu neugierig („Kad ćeš se udati?"),
  kocht und füttert gern und kommentiert alles beim Kaffee.
- Sie spricht Deutsch mit einzelnen bosnischen Einsprengseln.
- Sie ist **nie** gemein, politisch, religiös spöttisch oder herablassend.
  Sie lacht über sich und ihre Familie, nicht über andere.
- Optik: runder Goldkreis mit Kaffeetassen-Icon. Wird später eine Illustration
  (z. B. KI-generiert) gewünscht: als `<img>` in `.kultur-tetka-bild`, überall
  dieselbe Datei `Bilder/kultur/tetka-fata.webp`.

---

## 6. Bilder

Grundsatz: **Nur Bilder mit eindeutig geklärter Lizenz.** In Deutschland sind
Abmahnungen wegen Bildrechten teuer (oft vierstellig), auch für private,
nicht-kommerzielle Seiten.

### Erlaubte Quellen

| Quelle | Bedingung |
|---|---|
| **Unsplash, Pexels, Pixabay** | Lizenz der Plattform; Nachweis trotzdem angeben (Fotograf + Plattform) |
| **Wikimedia Commons** | nur CC0, CC BY oder CC BY-SA – **Urheber, Lizenz und Link sind Pflicht**, genau wie auf der Dateiseite angegeben |
| **KI-generiert** | erlaubt, **immer gekennzeichnet** („Bild: KI-generiert (Werkzeug)"), siehe Einschränkungen unten |
| Eigene Fotos | erlaubt; erkennbare Personen nur mit deren Einverständnis |

**„Lizenzfrei" heißt nicht „im Internet gefunden".** Google-Bildersuche,
Instagram, Zeitungs- und Restaurantseiten, Pinterest: **nie**.

### KI-Bilder: wofür ja, wofür nicht

- ✅ Szenen und Stimmungen: Kaffeetisch, Familienfeier, Autofahrt in den Sommerferien
- ✅ Illustrationen, Figuren (Tetka Fata), Symbolbilder
- ❌ **Reale Orte, Bauwerke und historische Objekte** (Stari most, Stećci,
  Povelja Kulina bana): KI erfindet Details, das wäre eine falsche Abbildung
- ❌ **Echte Personen** (Sänger, historische Figuren)
- ⚠️ **Tracht und Speisen** nur, wenn die Details stimmen (Pita-Form, Dimije-Schnitt,
  Ćevapi im Somun). Im Zweifel ein echtes Foto nehmen – eine falsche Pita fällt der
  Zielgruppe sofort auf.

### Technik

- Format **WebP**, ca. **1200 px** breit, **unter 250 KB**
- `width` und `height` im `<img>` angeben (verhindert Springen beim Laden)
- `alt`-Text: was ist zu sehen (1 Satz), nicht „Bild von …"
- Bildnachweis in der `<figcaption>` direkt am Bild (Pflicht, wird geprüft)
- Ohne passendes Bild: Bildblock weglassen oder eine eigene SVG-Illustration
  (Nachweis: „Illustration: LinguaBosna"). Das ist besser als ein beliebiges Foto.
- Teilbild (`og:image`): sobald ein Beitragsbild existiert, als absolute URL
  eintragen; bis dahin bleibt das Logo.

---

## 7. NO-GOs

1. **Kein Humor über Krieg, Genozid, Vertreibung.** Wo ein Thema 1992–95 berührt
   (z. B. Stari most), dann kurz, sachlich, respektvoll, im Ton erkennbar anders.
2. **Kein „Wem gehört's?"-Streit.** Ćevapi, Burek, Sevdah werden nicht gegen
   Nachbarländer ausgespielt. Augenzwinkernde Rivalität ja („Burek ist NUR mit
   Fleisch"), Abwertung anderer Volksgruppen nie.
3. **Religion:** erklären, nicht bewerten. Bajram und Božić gleichermaßen.
   Keine Witze über religiöse Praxis selbst.
4. **Keine Tagespolitik**, keine Parteien, keine Politiker. Geschichte sachlich.
5. **Keine abwertenden Stereotype** – auch nicht „traditionell" verpackt
   (Mujo-&-Haso-Witze sorgfältig auswählen; Rollenbilder, Minderheiten, Roma).
6. **Keine Mythen als Fakten** (Visoko-„Pyramiden", Herkunftslegenden). Solche
   Themen nur als Mythen-Check.
7. **Restaurants, Cafés, Firmen nie namentlich** (Entscheidung Alen) – keine
   Ranglisten, keine Empfehlungen, keine Werbung, keine Affiliate-Links.
   Stattdessen: „Woran erkennst du gute Ćevapi?"
8. **Keine Liedtexte** moderner Lieder. Traditionelle Sevdalinke nur als eigene,
   kurze Inhaltsangabe oder Übersetzung einzelner Zeilen.
9. **Keine fremden Bilder** ohne geklärte Lizenz (Abschnitt 6).
10. **Keine Einbettungen** von YouTube, Spotify, Google Maps, Instagram –
    sie setzen Cookies und senden Daten an Dritte (DSGVO). Stattdessen ein
    normaler Link. (Eine Zwei-Klick-Lösung wäre möglich, müsste dann aber auch
    in die Datenschutzerklärung.)
11. **Keine Textwände:** höchstens ~120 Wörter pro Abschnitt.

---

## 8. Prüfung (vor jedem Commit)

1. **Struktur & Mobil:** `PYTHONUTF8=1 python test_kultur_beitrag.py kultur-[thema].html`
   (Blöcke, Wortzahlen, Lesezeit, Quiz-JSON, Bilder + Nachweis, Wörterbuch-Links,
   keine `?kapitel=`-Links, Verlinkung auf der Übersicht, SEO via `test_seo.py`,
   Überlauf und Touch-Targets bei 900/628/480/360/320 px)
2. **Sprache:** Subagent `bosnisch-pruefer` – alle bosnischen Wörter, Sätze und
   Quizoptionen (ijekavisch, Bosnisch-Standard, Abgleich mit `vokabeln_flat.json`).
3. **Inhalt, Fakten & Ton:** Subagent `kultur-pruefer` (`.claude/agents/kultur-pruefer.md`).
   Er prüft Fakten per Websuche, Mythen, die NO-GOs aus Abschnitt 7, die Ausgewogenheit
   (offen bosnisch-herzegowinisch), Tonalität und Tetka Fata sowie die Bildregeln.
   Jede Faktenaussage braucht eine Quelle (intern, nicht jede muss im Beitrag stehen).
   Die drei Prüfungen ersetzen sich nicht gegenseitig: Das Skript prüft Struktur,
   `bosnisch-pruefer` die Sprache, `kultur-pruefer` den Inhalt.
4. **Usability** (bei neuen Bausteinen): `PYTHONUTF8=1 python test_usability.py Code/5_Kultur/kultur-[thema].html`
5. `PYTHONUTF8=1 python build_sitemap.py` und `sitemap.xml` mitcommitten.

Alle Ergebnisse Alen zeigen, bevor committed wird.

---

## 9. Nach jedem neuen Beitrag

- Karte in `kultur-uebersicht.html` von „Demnächst" (`<div class="kultur-card demnaechst">`)
  auf aktiven Link (`<a class="kultur-card" href="…">`) umstellen bzw. neu anlegen.
  Neueste Beiträge stehen **vorn**.
- Status-Tabelle unten aktualisieren.
- Optional: Instagram-Karussell zum Beitrag (siehe `Instagram-Werkzeuge`).

---

## 10. Später (bewusst noch nicht umgesetzt)

- **Lernfortschritt** („gelesen"-Plakette auf den Kultur-Karten): `LB_fortschritt.js`
  reagiert bisher nur auf `/Code/3_Grammatik/`. Die Quiz-IDs der Kultur-Beiträge
  sind dieselben wie bei der Grammatik, eine Erweiterung um einen Schlüssel
  `kultur` ist also klein. Erst umsetzen, wenn es mehrere Beiträge gibt.
- **Generierte Übersicht** (`build_kultur_index.py` liest die Beiträge und baut
  die Karten), sobald die Handpflege der Karten lästig wird.

---

## 11. Status-Übersicht

| Beitrag | Datei | Rubrik | Typ | Status |
|---|---|---|---|---|
| Amidža, daidža, zet – wer ist hier eigentlich wer? | `kultur-familie-stammbaum.html` | Familie & Zusammenleben | Wer ist wer? | Entwurf (Nov. 2026): Struktur ✓, Sprache ✓ (bosnisch-pruefer), Inhalt: kultur-pruefer |
| Burek oder Sirnica? | – | Essen & Trinken | Duell | geplant |
| Ćevapi: Woran erkennst du gute? | – | Essen & Trinken | Erklärstück | geplant |
| Bosanska kahva | – | Essen & Trinken | Erklärstück | geplant |
| Was ist eigentlich Sevdah? | – | Musik & Tanz | Erklärstück | geplant |
| Stećci & Bosančica | – | Geschichte & Schrift | Erklärstück | geplant |
