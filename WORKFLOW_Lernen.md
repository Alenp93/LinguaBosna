# WORKFLOW: Lernen-Bereich (Übungsaufgaben) erstellen

> Prozess-Referenz für LinguaBosna. Gehört ins Project Knowledge, analog zu
> `WORKFLOW_Grammatikseiten.md`.
>
> ✅ **Status dieser Datei:** Gegen den echten Repo-Stand von `Code/4_Lernen/`
> abgeglichen (Stand 2026-08-28). Die früheren 🔲-Platzhalter sind ausgefüllt.
> Die Struktur-Validierung (Abschnitt 6) ist seit 2026-08-28 mit
> `test_lernen_uebung.py` ebenfalls abgedeckt.

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
  ⚠️ Das gilt für die **Aufgaben**. Sobald eine solche Übung im *Feedback*
  ganze Sätze zeigen will, greift wieder die Regel darunter: Die
  Aspektpaar-Zuordnung zieht ihre Paare weiterhin komplett aus
  `vokabeln_flat.json` und hat trotzdem eine kleine Zusatzdatei
  `aspektpaare_data.json` für die Beispielsätze bekommen (2026-08-28).
  Zwei Dateien mit klarer Rollentrennung sind hier richtig – Sätze gehören
  nicht in die Wortliste.
- Übungen, die vollständige Beispielsätze brauchen (z. B. Lückentext,
  Satzbau-Puzzle), brauchen zwingend eine **eigene JSON-Datei**, da
  `vokabeln_flat.json` nur Einzelwörter enthält, keine Sätze.
- Neue Datendateien liegen unter `Code/4_Lernen/[typ]_data.json` (bestätigt,
  z. B. `Code/4_Lernen/luckentext_data.json`).

**Vokabellücken beim Übungsbau → `VOKABEL_BACKLOG.md` (nicht nebenbei einbauen).**
Beim Schreiben von Beispielsätzen fallen regelmäßig Wörter auf, die es im Bestand
noch nicht gibt – vor allem Funktionswörter (Zeitadverbien, Konjunktionen), weil
`vokabeln_flat.json` thematisch geschnitten ist. Solche Wörter werden **gesammelt,
nicht spontan in die Vokabel-JSON geschrieben**: Ein Einzeleintrag würde entweder
die 35er-Kapitelgrenze reißen oder in einem Kapitel mit falschem Niveau landen.
Deshalb nach jedem neuen Set die verwendeten Wörter gegen `vokabeln_flat.json`
abgleichen und die Fehlenden mit Niveau-Vorschlag in `VOKABEL_BACKLOG.md` eintragen.
Umgekehrt gilt weiterhin: Wo der Bestand eine Form **hat**, ist sie verbindlich
(`kahva` nicht `kafa`, `jučer` nicht `juče`, `sedmica` nicht `tjedan`).

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
| Aspektpaar-Zuordnung | ✅ fertig | `Code/4_Lernen/lernen-aspektpaare.html` | `vokabeln_flat.json` (`par_id`, `aspekt`) **+** `Code/4_Lernen/aspektpaare_data.json` (Beispielsätze fürs Feedback) | 92 Paare (`ap01`–`ap92`, lückenlos), 3 Sets: A1–A2 (54) / B1–C1 (38) / alle (92) |
| Satzbau-Puzzle (Enklitika/Wortstellung) | ✅ fertig (Enklitika, B2) | `Code/4_Lernen/lernen-satzbau.html` | eigene JSON (`Code/4_Lernen/satzbau_data.json`) | 63 Sätze, 4 Sets: Zweitstellung (20) / Die Kette (25) / Fragen & Betonung (18) / alle gemischt (63, in JS berechnet) |
| Aspektwahl (Verbalaspekt in der Anwendung) | ✅ Set 1–4 fertig | `Code/4_Lernen/lernen-aspektwahl.html` | eigene JSON (`Code/4_Lernen/aspektwahl_data.json`) | Set 1 „Signalwörter" (41 Einträge: 18 nesvršeni / 10 svršeni / 13 offen) · Set 2 „Aspektwahl im Satz" (64 Sätze über 9 Regelmuster) · Set 3 „Situation → Satz" (56 Aufgaben über 7 Bedeutungsmuster) · Set 4 „Erzähltext" (10 Texte à 5 Lücken) |

> **Die Seite kennt vier Aufgabentypen**, gesteuert über das Feld `typ` im Set:
> `typ` fehlt (= „signal") zeigt einen Ausdruck mit drei Korb-Buttons; `typ: "satz"`
> zeigt einen Lückensatz mit zwei Verbformen; `typ: "situation"` zeigt eine deutsche
> Absichtsbeschreibung mit zwei vollständigen bosnischen Sätzen; `typ: "text"` zeigt
> einen Erzähltext, dessen fünf Lücken nacheinander gefüllt werden. Alle teilen sich
> Fortschritt, Feedback, Ergebnis und die Auswertung nach Regeltyp. Set 2 und 4 nutzen
> die vorhandenen Lückentext-Klassen (`.uebung-satz`, `.luecke`, `.wortbank`) aus
> `Style_4_Lernen.css`; neu sind nur `.signal-mark` (Set 2), `.satzwahl` und
> `.feedback-variante` (Set 3) sowie `.erzaehl-text` und die Lücken-Zustände (Set 4).
>
> **Stratifiziert gezogen wird in Set 1–3, nach unterschiedlichen Feldern:**
> Set 1 nach `korb` (sonst wäre der kleinste Korb kaum vertreten), Set 2 und 3 nach
> `kategorie` – bei 9 bzw. 7 Mustern und 10 Fragen deckt so jeder Durchgang alle
> Muster ab und liefert bei Wiederholung andere Aufgaben desselben Musters.
> **Set 4 zieht anders:** zwei ganze Texte (`TEXTE_PRO_RUNDE`), aus deren Lücken eine
> flache Liste gebaut wird – 2 × 5 = wieder 10 Aufgaben. Die Lücken bleiben dabei
> bewusst in Textreihenfolge, weil eine Geschichte nur der Reihe nach Sinn ergibt.
> Dadurch funktionieren Fortschritt, Statistik und Ergebnis unverändert weiter; nur
> die Beschriftungen wechseln („Lücke 3 von 10", „Nächster Text →").
>
> ⚠️ **Erzähltexte brauchen härtere Lücken als Einzelsätze (Befund zu Set 4):**
> Im Textformat gibt es **kein „entscheidet nicht"-Ventil** wie in Set 1 – jede Lücke
> muss eine eindeutige Lösung haben, sonst wertet die Übung gutes Bosnisch als Fehler.
> Der Erzählkontext allein reicht dafür oft nicht: Nach `dok` ist der Hauptsatz frei
> (beide Aspekte möglich), eine Gewohnheit lässt den habituellen svršeni zu, und
> `sačekati` verträgt sehr wohl Dauerangaben. Lücken werden deshalb **lexikalisch
> gehärtet** – mit einem Wort, das die Wahl erzwingt: `odjednom`, `odmah`, `ukratko`,
> `u jednom trenutku` für den svršeni; `po cijeli dan`, `od jutra do mraka`, `danima`
> für den nesvršeni. Faustregel: Wenn sich die Lösung nicht an einem Wort im Satz
> festmachen lässt, gehört die Lücke nicht in den Text.
>
> ⚠️ **Minimalkontrast im selben Text** (dasselbe Verbpaar zweimal, einmal je Aspekt)
> ist didaktisch stark – aber nur, wenn **beide** Vorkommen eindeutig sind. Ist das
> erste mehrdeutig, lernt der Nutzer das Gegenteil: Er wählt eine korrekte Form,
> bekommt ein Falsch, und liest sie zwei Zeilen später als richtige Lösung. Das lehrt
> „der Aspekt ist willkürlich". Mustergültig gelöst im Text „Majstor“
> (`dok` gegen `za dva sata`).
>
> ✅ **Infinitiv und `da` + Präsens stehen bewusst nebeneinander (entschieden
> 2026-08-28) – bitte nicht vereinheitlichen.** Die eigene B2-Seite
> `grammatik-nebensaetze.html` stellt fest, dass im gesprochenen Bosnisch
> `da` + Präsens dominiert; die Übung zeigt deshalb **beide** Konstruktionen, damit
> der Lernende sie wiedererkennt. Umgestellt sind in Set 2 die Aufgaben mit
> `prestati`, `početi` und `uspjeti`, in Set 4 vier Stellen (`počeo da radi`,
> `morao da ponovim`, `sjeli smo da jedemo`, `naučio da plivam`); die übrigen
> behalten den Infinitiv. Die Botschaft der Erklärungstexte ist dabei zentral:
> **Die Aspektregel hängt an der Konstruktion nicht** – nach
> `početi`/`prestati`/`nastaviti` steht der nesvršeni, ob als `da troši` oder als
> `trošiti`. ⚠️ Bei `da` + Präsens richtet sich die **Person nach dem Subjekt des
> Hauptverbs** (`Počeli smo da uređujemo`, `morao sam da ponovim`) – auch der
> Distraktor muss dann in Person und Numerus passen. Die vollständige Liste der
> umgestellten Stellen steht im Feld `_hinweis_infinitiv` der JSON.
>
> ⚠️ **Fallstrick beim Ergänzen weiterer Typen (einmal passiert):** Im Fehlerzweig von
> `pruefeAntwort` wurde die Beschriftung des richtigen Korbs über `aktivSet.koerbe`
> gesucht – ein Feld, das **nur Set 1 hat**. Bei Set 4 war es `undefined`, und die
> Funktion brach genau dann ab, wenn der Lernende **falsch** antwortete: Feedback und
> Weiter-Button blieben unsichtbar, die Übung hing. Die Bedingung fragt deshalb jetzt
> nach `typ === 'signal'`, statt die anderen Typen aufzuzählen. Wer einen fünften Typ
> ergänzt, sollte gezielt eine **falsche** Antwort testen – der Fehler ist bei
> richtigen Antworten unsichtbar.
>
> **Set 2 und Set 3 sind Spiegelbilder – das ist der Kern und darf nicht verwischen:**
> In Set 2 macht der bosnische Kontext die andere Aspektform unmöglich; gefragt ist
> die *grammatisch* richtige Form. In Set 3 sind **beide Sätze korrekt**, sie bedeuten
> nur Verschiedenes; gefragt ist die *gemeinte* Form. Deshalb zeigt das Feedback in
> Set 3 immer BEIDE Sätze mit ihrer Bedeutung (`loesung_de` / `distraktor_de`) – das
> ist dort die eigentliche Lektion, nicht „richtig oder falsch". Aufgaben, die in
> Set 2 an der Eindeutigkeit scheitern, gehören nach Set 3; Aufgaben, deren deutsche
> Beschreibung die Wahl nicht determiniert, gehören in keins von beiden.
>
> ⚠️ **Designregel für Set 2 (und alle künftigen Satz-Sets):** Aufgenommen werden nur
> Sätze mit **eindeutiger** Lösung – der Kontext muss die andere Aspektform
> unnatürlich oder ungrammatisch machen. Fälle, in denen beide Formen natürlich sind
> und nur Verschiedenes bedeuten, gehören in Set 3, nicht hierher; sonst wertet die
> Übung korrekte Antworten als falsch. Der `bosnisch-pruefer` hat daran 14 der
> ursprünglich 72 Aufgaben beanstandet. Folgen daraus: Die Kategorie `wiederholung`
> ist in Set 2 **entfallen** (von 7 Aufgaben hielt nur eine stand – der habituelle
> svršeni greift genau dort), und `hintergrund_ereignis` wurde auf Kontexte
> umgebaut, in denen der nesvršeni implausibel wird (`odjednom`, `u jednom trenutku`,
> „cijelu kuću **i legla**"). Grund: „dok + nesvršeni, Hauptsatz + nesvršeni" ist als
> zwei parallele Verläufe ein völlig regulärer Satztyp.

> ⚠️ **Warum es zwei Aspekt-Übungen gibt (nicht zusammenlegen):**
> `lernen-aspektpaare.html` prüft die **Wortform** (welches Verb ist der Partner von
> `čitati`?) und wird über den Wortstamm gelöst. `lernen-aspektwahl.html` prüft die
> **Anwendung** (wann verwende ich welchen?). Wer die erste Übung perfekt löst, weiß
> immer noch nicht, ob „Čitao sam knjigu" oder „Pročitao sam knjigu" richtig ist.
> Die beiden bilden einen Lernpfad: Stufe 1 Formen → Stufe 2 Anwendung.
>
> **Die Brücke zwischen beiden Stufen liegt im Feedback von Stufe 1 (seit
> 2026-08-28):** Nach jeder Antwort stehen dort zwei Beispielsätze – der
> nesvršeni-Partner im **Präsens**, der svršeni-Partner im **Perfekt**
> („Čitam knjigu." / „Pročitao sam knjigu."), je mit deutscher Übersetzung, die
> den Unterschied sichtbar macht. Der Lernende sieht damit schon beim
> Formentraining, *wozu* die zweite Form gut ist, und trifft die Frage in
> `lernen-aspektwahl.html` nicht unvorbereitet. Die Sätze stehen in
> `Code/4_Lernen/aspektpaare_data.json`, nach `par_id` geschlüsselt.
> ⚠️ **Nicht clientseitig generierbar** – das war die naheliegende Idee und sie
> trägt nicht: Das Perfekt braucht das l-Partizip, und das ist aus dem Infinitiv
> nicht regelhaft ableitbar (`doći` → `došao`, `peći` → `ispekao`, `uzeti` →
> `uzeo`, `prenijeti` → `prenio`). Deshalb sind alle 184 Sätze geschrieben.
> Die Form-Konvention (nes = Präsens, svr = Perfekt) ist im Feld `_konvention`
> der JSON festgehalten und gilt für neu ergänzte Paare weiter. Fehlt eine
> `par_id` in der Datei, zeigt die Übung einfach keine Sätze – neue Aspektpaare
> in `vokabeln_flat.json` brechen sie also nicht.
>
> **Regel für das Set „Signalwörter" (aus dem Bau gelernt):** Es gibt einen dritten
> Korb „entscheidet nicht", und er ist didaktisch der wichtigste. Ohne ihn lernt der
> Nutzer eine Adverbien-Liste auswendig, statt den Aspekt zu verstehen – und mehrere
> gängige „Signalwörter" halten der Prüfung ohnehin nicht stand (`upravo`, `jednom`,
> `tek`, `već`, `dok`). Welche Ausdrücke warum ausgeschlossen wurden, steht im Feld
> `_bewusst_weggelassen` am Anfang von `aspektwahl_data.json` – dort nachsehen, bevor
> ein „fehlendes" Signalwort ergänzt wird.
>
> ⚠️ **Wortwahl-Fallen, die der `bosnisch-pruefer` in den Aspekt-Sets gefunden hat
> (2026-08-26/27) – beim Schreiben neuer Beispielsätze beachten:**
> `pozvati` heißt **nicht „anrufen"**, sondern „herbeirufen / einladen“; die
> Vokabel-JSON führt für „anrufen“ ein eigenes Verb (`nazvati`). `poslušati` heißt
> nicht nur „zu Ende zuhören“, sondern vor allem **„auf jemanden hören, befolgen“**.
> `otputovati` bezeichnet die **Abreise**, nicht die Reise als Ganzes. `uraditi` ist
> nicht der Aspektpartner von `raditi` in der Bedeutung *arbeiten* (nur in *erledigen*).
> `gledati koga preko ramena` heißt **„auf jemanden herabsehen“**, nicht „ihm über die
> Schulter schauen“. Solche Fälle fallen bei einer reinen Aspekt-Prüfung durch, weil
> die Aspektzuordnung stimmt – falsch ist die Bedeutung.
>
> ⚠️ **Der habituelle svršeni-Präsens (Befund des `bosnisch-pruefer`, 2026-08-26) –
> gilt für ALLE künftigen Aspekt-Sets:** Die verbreitete Faustregel „Wiederholung =
> nesvršeni" ist eine Default-Erwartung, keine Grammatikregel. Wiederholte, jeweils
> abgeschlossene Einzelakte stehen im Bosnischen regulär im svršeni: „Svaki dan
> pogledam jednu epizodu.", „Uvijek zatvorim vrata za sobom.", „Svaki put platim
> karticom." Konsequenzen, die im Set 1 bereits umgesetzt sind und beibehalten werden
> müssen: (a) Die Fragestellung lautet „Welcher Aspekt ist die **normale Wahl**?"
> (Feld `frage`), nicht „Welcher ist erzwungen?"; (b) die Korb-Labels heißen „meist
> unvollendet"/„meist vollendet"; (c) Erklärungstexte formulieren „in der Regel" statt
> „immer"/„nie"/„verlässlich". **Die einzige harte Regel im gesamten Set sind die
> Phasenverben** (`početi`/`prestati`/`nastaviti` + Infinitiv → zwingend
> nesvršeni-Infinitiv). Ebenfalls belastbar und ein guter Kandidat für Set 2:
> `ne` + synthetischer Imperativ („Ne čitaj to!", nicht *„Ne pročitaj to!") – anders
> als das oft gelehrte `nemoj`, das beide Aspekte verträgt.

> ⚠️ **Regel für Satzbau-/Umstell-Übungen (aus dem Satzbau-Puzzle gelernt):**
> Der **Satzanfang wird immer vorgegeben** und steht schon im Zielfeld. Grund: Die
> Wortstellung im Bosnischen ist außerhalb der Enklitika-Kette frei – ohne festen
> Anfang wären „Ja sam ti to rekao" und „Rekao sam ti to" beide richtig, und die Übung
> würde korrekte Antworten als falsch werten. Zusätzlich hat jede Aufgabe ein optionales
> Feld `alternativen` für weitere zulässige Reihenfolgen. Ein Baustein darf mehrere
> Wörter enthalten (`"u Njemačkoj"`), wenn deren Reihenfolge ohnehin feststeht – das
> nimmt weitere Mehrdeutigkeit heraus.

---

## 6. Validierung

- **Sprache:** `bosnisch-pruefer`-Subagent auch für Lernen-Inhalte aufrufen
  (Distraktoren eingeschlossen – auch falsche Optionen müssen sprachlich
  sauber sein, nicht nur die korrekte Lösung).
- **SEO:** `python3 test_seo.py <datei>` prüft die SEO-Grundausstattung auch für
  Lernen-Seiten (Canonical, Open Graph, Twitter, gültiges JSON-LD, Description-Länge,
  offene `[PLATZHALTER]`, `defer`). Nach einer neuen Übung zusätzlich
  `python3 build_sitemap.py` ausführen und die aktualisierte `sitemap.xml` mitcommitten.
- **Struktur (Mobile/Layout):** ✅ `test_lernen_uebung.py` (seit 2026-08-28, Repo-Root).
  Aufruf: `python3 test_lernen_uebung.py lernen-[typ].html` (Datei- oder Pfadangabe,
  wie bei `test_grammatikseite.py`; findet Repo-Root automatisch). Prüft:
  - Struktur: die drei Bildschirme (Start/Übung/Ergebnis), Set-Karten-Grid, Fortschritt,
    Feedback- und Ergebnis-Elemente
  - Head-Pflichten: Fonts, FontAwesome, Favicon-Block, `defer` bei `LB_main.js`,
    keine relativen (`../`) Pfade
  - SEO: ruft `test_seo.py` für dieselbe Datei mit auf (keine doppelte Prüflogik)
  - Mobiltest bei 900/628/480/360/320 px **mit echtem JavaScript**: anders als
    `test_grammatikseite.py` (das Scripts entfernt und nur HTML+CSS zusammenklebt)
    startet dieses Skript einen lokalen HTTP-Server auf dem Repo-Root, weil
    Lernen-Seiten ihren Inhalt per `fetch()` aus einer JSON-Datei nachladen –
    ohne echten Server und aktives JS blieben die Container leer. Geprüft werden
    Start-Bildschirm, erste Aufgabe, erstes Feedback und Ergebnis-Bildschirm.
  - Touch-Targets: alle sichtbaren, nicht deaktivierten `<button>` müssen
    mindestens 44×44px groß sein
  - Die Interaktion (Set-Karte anklicken, eine Aufgabe „lösen") ist **generisch**
    gehalten (Sofort-Auswertung bei Körben/Wortbank/Satzwahl; bei Puzzle-Typen wie
    Satzbau werden alle Bausteine geklickt und dann „Prüfen"), damit dasselbe
    Skript für künftige Übungstypen weiterfunktioniert, ohne je Typ Sondercode zu
    brauchen. Gelingt die generische Interaktion bei einem neuen Übungstyp nicht,
    gibt das Skript einen Hinweis (⚠) statt eines Fehlers aus – Struktur-/Head-Checks
    laufen trotzdem vollständig.
  - Exemplarisch getestet an `lernen-aspektwahl.html` (vier Aufgabentypen: signal/
    satz/situation/text) und `lernen-satzbau.html` (Puzzle-Typ) – beide fehlerfrei.
- Wie bei Grammatikseiten: Vor jedem Commit Alen die Änderungen zeigen und
  explizit bestätigen lassen, besonders bei neuen Beispielsätzen/Distraktoren.

---

## 7. Pflicht-Verlinkung von der Grammatikseite (nicht vergessen)

**Jede neue Lernen-Übung wird auf der zugehörigen Grammatik-Erklärseite verlinkt.**
Das ist kein optionaler Zusatz: Ohne diesen Button findet die Übung praktisch
niemand – die Übersichtsseite `lernen-uebersicht.html` allein reicht nicht, weil
Lernende beim Thema einsteigen, nicht bei der Übungsart.

- **Ort:** Block 5 („Üben") der Grammatikseite, direkt hinter dem Quiz-Ergebnis
  (`div.quiz-result`), noch innerhalb der `<section>`.
- **Baustein:** `div.uebung-cta-box` mit `a.uebung-cta` – die Klassen liegen bereits
  in `Style_3_Grammatik_Detail.css`, es ist kein neues CSS nötig. Exakter Wortlaut
  und Beispiel: `WORKFLOW_Grammatikseiten.md`, Abschnitt 2, „Übungs-Button am Ende
  von Block 5".
- **Deep-Link nur, wenn die Übung das Kapitel mit genau einem Thema/Set abdeckt**
  (z. B. `?thema=akkusativ` beim Lückentext) – der Parameter überspringt dann die
  Auswahlseite und startet direkt. Deckt die Übung das Kapitel mit **mehreren**
  Sets ab (Satzbau-Puzzle: Zweitstellung/Kette/Fragen; Aspektpaare: Sets nach
  Niveau statt nach Kapitel), verlinkt der Button **ohne** Parameter auf die
  Set-Auswahl – der Lernende soll selbst wählen. Jede neue Übung sollte trotzdem
  einen Parameter unterstützen, für den Fall, dass später von woanders direkt
  verlinkt wird – siehe die `URLSearchParams`-Auswertung in `lernen-satzbau.html`.
- **Gibt es noch keine passende Grammatikseite** (Übung kommt zuerst), wird das als
  To-do gemeldet und beim Anlegen der Grammatikseite nachgezogen.

Bereits verlinkt: `grammatik-akkusativ.html` → Lückentext,
`grammatik-enklitika.html` → Satzbau-Puzzle,
`grammatik-verbalaspekt.html` → Aspektpaare.

---

## 8. Antwortformat der Auslieferung

Analog zu Grammatikseiten:
- Kurzer didaktischer Vorspann vor der Dateierstellung (welches Thema,
  welche Untermuster werden abgedeckt)
- Nach Fertigstellung: Zusammenfassung (Aufbau, Datenquelle, Pool-Größe,
  sprachlicher Hinweis auf bewusst Weggelassenes)
- To-dos für Alen benennen (z. B. Übersichtskarte in `lernen-uebersicht.html`
  ergänzen, Menüpunkt-Reaktivierung, Verlinkung von der passenden
  Grammatikseite aus)
