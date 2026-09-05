# Status: Qualitätsprüfung Grammatikseiten (Sprache & Lerneffekt)

> Fahrplan für die nachträgliche Zweitprüfung aller 37 bestehenden Grammatikseiten.
> Anders als beim Neubau (siehe `WORKFLOW_Grammatikseiten.md`) geht es hier nicht um
> Struktur (die ist mit `test_grammatikseite.py` schon abgedeckt), sondern um zwei
> Dinge, die bisher nur beim jeweiligen Erstbau geprüft wurden: **Sprache** und
> **Lerneffekt/Didaktik**. Diese Datei ist der Tracker über viele Sessions hinweg –
> **eine Seite pro Session**, siehe `CLAUDE.md` Abschnitt „Arbeitsweise".

---

## Ablauf pro Session (1 Seite)

1. Seite lesen (`Code/3_Grammatik/Grammatik_[Niveau]/grammatik-[thema].html`).
2. **Sprachprüfung:** `bosnisch-pruefer`-Subagent aufrufen (wie beim Neubau,
   Prüfpunkte siehe `.claude/agents/bosnisch-pruefer.md`).
3. **Lerneffekt-Prüfung** (neu, manuell anhand der Didaktik-Checkliste aus
   `WORKFLOW_Grammatikseiten.md` Abschnitt 4, aber rückwärts angewendet –
   also "ist das noch da?", nicht "was wähle ich"):
   - Hook/Aha-Moment am Anfang noch klar erkennbar?
   - Callbacks zu Kapiteln, die es bei Erstellung dieser Seite noch nicht gab
     (spätere Seiten können Konzepte nachliefern, die hier fehlen)?
   - Stolperfallen-Hinweise für Deutschsprachige vorhanden und noch zutreffend?
   - Beispielsätze/Quizfragen: nutzen sie Wortschatz, der laut
     `vokabeln_flat.json` erst auf einem höheren Niveau eingeführt wird?
   - Progression stimmig mit allen inzwischen dazugekommenen Seiten (z. B.
     verweist eine A2-Seite nicht auf einen B1-Begriff, der erst nach ihr kam)?
4. Beide Ergebnisse (✓/⚠-Listen) Alen zeigen.
5. Nur nach Freigabe: Korrektur einbauen, `test_grammatikseite.py` erneut laufen
   lassen (Struktur darf durch Textänderungen nicht brechen), committen.
6. Zeile unten aktualisieren: Status, Datum, Kurzbefund.

**Status-Werte:** `offen` · `geprüft – ok` · `geprüft – Korrektur nötig` ·
`korrigiert & bestätigt`

**Verdacht-Werte** (aus dem Grob-Scan vom 05.09.2026, siehe Abschnitt „Grob-Scan"
weiter unten): `unauffällig` · `leicht` · `deutlich`. Das ist **nur** eine
Voreinschätzung zur Priorisierung – „unauffällig" heißt „im Grep-/Stichprobenscan
nichts gefunden", nicht „geprüft". Die Spalte wird durch die Tiefenprüfung nicht
überschrieben, damit man später sieht, wie gut der Scan getroffen hat.

---

## A1 (6 Seiten)

| # | Titel | Datei | Verdacht (Scan) | Status | Datum | Kurzbefund |
|---|---|---|---|---|---|---|
| 1 | Alphabet & Aussprache | `Grammatik_A1/grammatik-alphabet.html` | leicht | offen | | |
| 2 | Geschlecht der Substantive | `Grammatik_A1/grammatik-geschlecht.html` | leicht | offen | | |
| 3 | Das Verb „biti" & Verneinung | `Grammatik_A1/grammatik-biti.html` | unauffällig | offen | | |
| 4 | Fragen & Fragewörter | `Grammatik_A1/grammatik-fragen.html` | unauffällig | offen | | |
| 5 | Regelmäßiges Präsens | `Grammatik_A1/grammatik-praesens.html` | unauffällig | offen | | |
| 6 | Die 7 Fälle – Überblick | `Grammatik_A1/grammatik-faelle.html` | unauffällig | offen | | |

## A2 (7 Seiten)

| # | Titel | Datei | Verdacht (Scan) | Status | Datum | Kurzbefund |
|---|---|---|---|---|---|---|
| 7 | Satzbau & Wortstellung | `Grammatik_A2/grammatik-satzbau.html` | leicht | offen | | |
| 8 | Nominativ | `Grammatik_A2/grammatik-nominativ.html` | unauffällig | offen | | |
| 9 | Akkusativ | `Grammatik_A2/grammatik-akkusativ.html` | unauffällig | offen | | |
| 10 | Lokativ | `Grammatik_A2/grammatik-lokativ.html` | leicht | offen | | |
| 11 | Personalpronomen | `Grammatik_A2/grammatik-personalpronomen.html` | unauffällig | offen | | |
| 12 | Modalverben & Imperativ | `Grammatik_A2/grammatik-modalverben.html` | **deutlich** | offen | | |
| 13 | Adjektive & Angleichung | `Grammatik_A2/grammatik-adjektive.html` | unauffällig | offen | | |

## B1 (10 Seiten)

| # | Titel | Datei | Verdacht (Scan) | Status | Datum | Kurzbefund |
|---|---|---|---|---|---|---|
| 14 | Perfekt | `Grammatik_B1/grammatik-perfekt.html` | unauffällig | offen | | |
| 15 | Futur I | `Grammatik_B1/grammatik-futur.html` | **deutlich** | offen | | |
| 16 | Reflexive Verben | `Grammatik_B1/grammatik-reflexive-verben.html` | leicht | offen | | |
| 17 | Genitiv | `Grammatik_B1/grammatik-genitiv.html` | unauffällig | offen | | |
| 18 | Dativ | `Grammatik_B1/grammatik-dativ.html` | leicht | offen | | |
| 19 | Instrumental | `Grammatik_B1/grammatik-instrumental.html` | **deutlich** | offen | | |
| 20 | Possessivpronomen | `Grammatik_B1/grammatik-possessivpronomen.html` | unauffällig | offen | | |
| 21 | Demonstrativpronomen | `Grammatik_B1/grammatik-demonstrativpronomen.html` | unauffällig | offen | | |
| 22 | Komparation | `Grammatik_B1/grammatik-komparation.html` | unauffällig | offen | | |
| 23 | Der Vokativ | `Grammatik_B1/grammatik-vokativ.html` | unauffällig | offen | | |

## B2 (6 Seiten)

| # | Titel | Datei | Verdacht (Scan) | Status | Datum | Kurzbefund |
|---|---|---|---|---|---|---|
| 24 | Verbalaspekt | `Grammatik_B2/grammatik-verbalaspekt.html` | unauffällig | offen | | |
| 25 | Zahlen & Numeralia | `Grammatik_B2/grammatik-zahlen.html` | unauffällig | offen | | |
| 26 | Konditional I | `Grammatik_B2/grammatik-konditional-1.html` | unauffällig | offen | | |
| 27 | Passiv | `Grammatik_B2/grammatik-passiv.html` | unauffällig | offen | | |
| 28 | Nebensätze & Konjunktionen | `Grammatik_B2/grammatik-nebensaetze.html` | leicht | offen | | |
| 29 | Enklitika & Wortstellung | `Grammatik_B2/grammatik-enklitika.html` | unauffällig | offen | | |

## C1 (4 Seiten)

| # | Titel | Datei | Verdacht (Scan) | Status | Datum | Kurzbefund |
|---|---|---|---|---|---|---|
| 30 | Konditional II & Futur II | `Grammatik_C1/grammatik-konditional-2-futur-2.html` | unauffällig | offen | | |
| 31 | Adverbiale Partizipien | `Grammatik_C1/grammatik-adverbiale-partizipien.html` | unauffällig | offen | | |
| 32 | Kasusfeinheiten & Wortbildung | `Grammatik_C1/grammatik-kasusfeinheiten-wortbildung.html` | unauffällig | offen | | |
| 33 | Formelle Sprache & Stilistik | `Grammatik_C1/grammatik-formelle-sprache-stilistik.html` | unauffällig | offen | | |

## C2 (4 Seiten)

| # | Titel | Datei | Verdacht (Scan) | Status | Datum | Kurzbefund |
|---|---|---|---|---|---|---|
| 34 | Aorist & Imperfekt | `Grammatik_C2/grammatik-aorist-imperfekt.html` | unauffällig | offen | | |
| 35 | Plusquamperfekt | `Grammatik_C2/grammatik-plusquamperfekt.html` | unauffällig | offen | | |
| 36 | Inversion, Emphase & Ellipsen | `Grammatik_C2/grammatik-inversion-emphase-ellipsen.html` | unauffällig | offen | | |
| 37 | Dialekte & Bosnisch im Vergleich (BKS) | `Grammatik_C2/grammatik-dialekte-vergleich.html` | leicht | offen | | |

---

## Reihenfolge-Empfehlung

Von A1 nach C2, in obiger Tabellenreihenfolge (= Lernpfad-Reihenfolge auf
`LB_3_Grammatik.html`). Das hat einen konkreten Vorteil gegenüber
niveau-durchmischter Prüfung: Callback-Bezüge lassen sich nur beurteilen, wenn
klar ist, was der Lernende zu diesem Zeitpunkt schon kennt – das ist bei
aufsteigender Reihenfolge am einfachsten nachvollziehbar.

---

## Grob-Scan 05.09.2026 (Triage, keine Tiefenprüfung)

Automatisierter Scan über alle 37 Seiten nach den fünf Kriterien aus
`TEMPLATE_Scan_Sprachfehler_Alle.md` (Ekavismen, kroat./serb. Sondervarianten,
Abgleich gegen `vokabeln_flat.json` nach Schreibweise und Niveau, Aspektpaare
gegen `par_id`, Widersprüche zwischen Seiten), ergänzt um eine Sichtprüfung
aller Beispieltabellen und aller 370 Quiz-Antworten.

**Gesamtbild:** Die Substanz ist gut. Es wurde **kein einziger echter Ekavismus**
gefunden – die generative Jat-Gegenprobe (jedes „e" testweise zu „ije"/„je"
aufgefüllt und gegen die JSON-Lemmata gehalten) schlägt nur auf
`grammatik-dialekte-vergleich.html` an, wo ekavische Formen der erklärte Zweck
sind. Ebenso keine fehlenden Diakritika und keine falschen Aspektpaar-Verweise.
Die Treffer liegen fast alle in einer anderen Klasse: **Register- und
Varietäten-Aussagen**, also Stellen, an denen eine Seite eine serbische oder
kroatische Form als bosnisch ausgibt.

### Deutlicher Verdacht (3)

| Seite | Fund |
|---|---|
| `grammatik-instrumental.html` (B1) | Beispielkarte „**Kafa** sa mlijekom" (Zeile ~205). `vokabeln_flat.json` führt **kahva** (A1), und alle anderen Seiten (A1 Fälle, B2 Konditional I, C2 Inversion) nutzen ebenfalls „kahva". `grammatik-dialekte-vergleich.html` kennzeichnet „kafa" ausdrücklich als **serbisch** – die Seite widerspricht also direkt einer anderen Seite und der JSON-Referenzregel aus `CLAUDE.md`. |
| `grammatik-futur.html` (B1) | Die mini-note (Zeile ~303) stellt die Zusammenschreibung „**radiću**", „**putovaćemo**" als „im Gespräch (und oft in der Schrift)" dar. Das ist serbische Orthographie; der bosnische Standard schreibt ausschließlich getrennt („radit ću") – so wie es die Tabelle direkt darüber auch tut. Die Seite widerspricht sich damit selbst. |
| `grammatik-modalverben.html` (A2) | „**da** + Präsens" wird an drei Stellen als „**Typisch Bosnisch**" etikettiert (Zeilen ~274, ~462 und die Quizfrage „Welche typisch bosnische Alternative zum Infinitiv gibt es?"). Die Konstruktion ist ein Balkanismus mit Schwerpunkt im Serbischen; der bosnische Standard bevorzugt den Infinitiv. Das ist eine Kernaussage der Seite, kein Randdetail – deshalb höchste Priorität. |

### Leichter Verdacht (8)

| Seite | Fund |
|---|---|
| `grammatik-lokativ.html` (A2) | Nominativ „**stol** → na stolu" (Zeile ~294). „stol" ist die kroatische Form, bosnischer Standard ist „**sto**" (Gen. stola) – die Instrumental- und die Zahlenseite verwenden dann auch „sto"/„stolom". Nur die Nominativform ist betroffen. |
| `grammatik-nebensaetze.html` (B2) | Dieselbe Aussage wie bei den Modalverben: „im gesprochenen Bosnisch **dominiert** die Konstruktion da + Präsens" (Zeilen ~260, ~482). In sich konsistent mit A2 – aber genau deshalb zusammen mit dieser Seite zu entscheiden. |
| `grammatik-dialekte-vergleich.html` (C2) | Die Aussage „Bosnisch behält den Laut h: **lahko, mehko, sahat**" ist stärker formuliert, als der eigene Vokabelbestand hergibt – die JSON führt `lako` (A1) und `sat` (A1), nicht die h-Formen. Als Marker beschreibbar, als Standardform fraglich. Sonst die sauberste kontrastive Seite (kahva/kava/kafa, hljeb/kruh/hleb, sedmica/tjedan/nedelja, historija/povijest/istorija alle korrekt zugeordnet). |
| `grammatik-geschlecht.html` (A1) | Nutzt „**sudija**" – laut JSON **B1** – als A1-Beispiel; dazu mehrere A2-Wörter (knjiga, škola, pismo, ljubav, kolega). Bei Grammatikbeispielen ist ein Niveau darüber normal, zwei Stufen nicht. |
| `grammatik-alphabet.html` (A1) | Nj-Beispiel „**njemačka** = Deutschland" (Zeile ~300) klein geschrieben. Als Eigenname müsste es „Njemačka" heißen – auf der Seite, auf der Lernende Schreibweisen zum ersten Mal sehen. |
| `grammatik-satzbau.html` (A2) | Verwendet „**jer**" – laut JSON **B1**. Möglicherweise eher ein zu hohes Niveau in der JSON als ein Fehler der Seite; bei der Tiefenprüfung in beide Richtungen offen entscheiden. |
| `grammatik-dativ.html` (B1) | Nennt „**pripadati**" – laut JSON **B2** – in der Liste der Dativ-Verben. |
| `grammatik-reflexive-verben.html` (B1) | Führt „**šetati se**" als reflexives Verb; im Bosnischen ist „šetati" ohne „se" mindestens ebenso üblich. Steht in keiner Form in der JSON, also ohne Referenz. |

### Am 05.09.2026 bereits behoben (Entscheidung Alen)

Diese Punkte sind **erledigt** – die Verdachtsstufe oben bleibt trotzdem stehen,
weil sie den Zustand *vor* der Korrektur dokumentiert. Die Tiefenprüfung findet
diese Stellen also schon korrigiert vor.

| Seite | Änderung |
|---|---|
| A1 Alphabet | `njemačka` → `Njemačka` (Eigenname) |
| A1 Geschlecht | `sudija` (B1) → `komšija` (A1) an 5 Stellen; in der Vergleichskarte `stol` → `prozor` (kroatische Form vermieden) |
| A2 Lokativ | `stol → na stolu` → `sto (Stamm stol-) → na stolu` |
| A2 Satzbau | Glosse „jer = weil" ergänzt (siehe offener Punkt unten) |
| B1 Futur | Zusammenschreibung „radiću" nun als **serbische Rechtschreibung** benannt, bosnisch immer getrennt „radit ću" |
| B1 Instrumental | `Kafa` → `Kahva`; Beispiel auf `sa šećerom` umgestellt, weil `sa mlijekom` der s/sa-Regel derselben Seite widersprach |
| B1 Dativ | `pripadati` (B2) → `nedostajati` (B1) mit Beispiel „Nedostaješ mi." |
| B1 Reflexive Verben | `šetati se` → `nadati se` (klareres Beispiel für „se ≠ sich", da `šetati` auch ohne `se` gebräuchlich ist) |
| B2 Nebensätze | „dominiert die da-Variante deutlich" → neutral: „beide wirst du in Bosnien häufig hören" |
| C2 Dialekte | h-Bewahrung differenziert: `kahva` = Standard, `lahko/mehko/sahat` = markierte Varianten neben `lako/meko/sat` |

**A2 Modalverben bleibt bewusst unverändert:** Die Einordnung von „da + Präsens"
als „typisch bosnisch" ist nach Alens Einschätzung dort passend formuliert.
Nur die stärkere Aussage auf der Nebensätze-Seite wurde entschärft.

**Offen (Entscheidung nötig, nicht am Seitentext lösbar):** `jer` steht in der
JSON auf **B1**, wird aber auf der A2-Satzbau-Seite gebraucht. Sachlich ist `jer`
A2-Wortschatz – der Fehler liegt eher im JSON-Niveau als auf der Seite. Eine
Korrektur dort ist aber nicht billig: Wegen der Regel „ein Kapitel = genau ein
Niveau" müsste `jer` in ein A2-Kapitel umziehen, nicht nur ein Feld ändern.
Vorerst wurde auf der Seite nur die Glosse „(jer = weil)" ergänzt.

### Was der Scan ausdrücklich NICHT ersetzt

Nicht geprüft wurden Rektion und Kongruenz in freien Fließtext-Beispielen,
Idiomatik, Registerfeinheiten und die Didaktik-Fragen aus dem Ablauf oben. Ein
„unauffällig" in der Tabelle bedeutet nur, dass die fünf Scan-Kriterien nichts
gefunden haben.
