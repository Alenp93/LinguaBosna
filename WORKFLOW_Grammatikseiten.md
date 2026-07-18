# WORKFLOW: Grammatik-Erklärseiten erstellen

> Prozess-Referenz für LinguaBosna. Gehört ins Project Knowledge.
> Zusammen mit `TEMPLATE_Grammatik_Detailseite.html` ist dies die
> vollständige Arbeitsgrundlage für jede neue Grammatikseite.

---

## 1. Standard-Prompt (Kurzform)

Für eine neue Seite genügt künftig:

> „Erstelle grammatik-[thema].html auf Basis des Templates.
> Niveau [X], zurück: [Vorgänger], weiter: [Nachfolger]."

Claude übernimmt: Hook/Didaktik-Konzept, Beispielauswahl, Regel-Gruppen,
Quiz, Validierung, Mobiltest, Datei-Auslieferung.

---

## 2. Feste Regeln (nie abweichen)

| Regel | Wert |
|---|---|
| Dateiname | `grammatik-[thema].html` (klein, Bindestriche) |
| Struktur | 6 Blöcke: Einstieg → Beispiele → Regel → Vergleich → Üben → Spickzettel |
| Beispiele (Block 2) | genau 6 example-cards, Kernstelle mit `<span class="highlight">` |
| Regel (Block 3) | 2–4 Gruppen, je Tabelle + mini-note(s) |
| Spickzettel | genau 6 cheatsheet-items |
| Quiz | genau 10 Fragen, 3 Optionen |
| Quiz-Antwortverteilung | ca. 3/4/3 über die Indizes 0/1/2 streuen (nie gameable) |
| Quiz-Strings | KEINE ASCII-Apostrophe (') — nur typografische Zeichen („ " ' –) |
| Quiz-Ergebnisschwellen | >=9 / >=7 / >=5 / else — Texte themenspezifisch |
| Quiz-IDs | quizContainer, quizProgress, quizBarFill, quizQuestion, quizOptions, quizFeedback, quizNextBtn, quizResult, resultScore, resultText, quizRetryBtn — nie ändern |
| Tabellenköpfe/-zellen (Block 3) | kurz halten, möglichst 1 Wort pro `<th>`/`<td>` — lange Köpfe wie „Form (Nominativ)" können bei 320px zu Seitenüberlauf führen. Zusatzinfo lieber in `group-desc` oder `mini-note` statt in die Zelle |
| Pfade | immer absolut (`/Code/...`, `/Bilder/...`) — relative Pfade brechen in Unterordnern |
| Favicon-Block | Pflicht auf jeder neuen Seite (6 Zeilen, `/Bilder/favicon/...`) |
| CSS | `/Code/Style.css` + `/Code/3_Grammatik/Style_3_Grammatik_Detail.css` |
| JS-Einbindung | `/Code/LB_main.js` im head; Header/Footer via `<div id="header">` / `<div id="footer">` |

### Breadcrumb-Level-Labels (exakter Wortlaut)

- A1 – Grundlagen
- A2 – Aufbau
- B1 – Mittelstufe
- B2 – Fortgeschritten
- C1 – Oberstufe
- C2 – Profi

### Ablageorte im Repository

- Seiten: `Code/3_Grammatik/Grammatik_[LEVEL]/` (z. B. `Grammatik_B1/`)
- Übersichtsseite: `Code/1_Startseite/LB_3_Grammatik.html`
- Nach jeder neuen Seite: entsprechende Karte in der Übersicht von
  „Demnächst" (`div.coming-soon`) auf aktiven Link (`a.grammar-card`) umstellen.

### Seiten-Navigation (Vor/Zurück) – Konvention

- **Zurück-Link:** zeigt auf das vorige Kapitel. Innerhalb desselben Ordners relativ
  (`grammatik-[thema].html`); über Niveau-/Ordnergrenzen hinweg **absolut**
  (`/Code/3_Grammatik/Grammatik_[LEVEL]/grammatik-[thema].html`).
- **Weiter-Link (Grenzseite):** Existiert das nächste Kapitel noch nicht, zeigt „weiter"
  auf die Übersicht (`/Code/1_Startseite/LB_3_Grammatik.html`), Label = Titel des geplanten
  nächsten Kapitels.
- **Nachziehen:** Beim Anlegen des Folgekapitels den Weiter-Link der Vorgängerseite von der
  Übersicht auf die neue Seite umbiegen (sonst endet die Kette in der Übersicht).

---

## 3. Kapitel-Taxonomie (37 Kapitel, Stand: C1 komplett)

**A1 (1–6):** 1 Alphabet & Aussprache · 2 Geschlecht der Substantive ·
3 biti & Verneinung · 4 Fragen & Fragewörter · 5 Regelmäßiges Präsens ·
6 Die 7 Fälle – Überblick

**A2 (7–13):** 7 Satzbau & Wortstellung · 8 Nominativ · 9 Akkusativ ·
10 Lokativ · 11 Personalpronomen · 12 Modalverben & Imperativ ·
13 Adjektive & Angleichung

**B1 (14–23):** 14 Perfekt · 15 Futur I · 16 Reflexive Verben ·
17 Genitiv · 18 Dativ · 19 Instrumental · 20 Possessivpronomen ·
21 Demonstrativpronomen · 22 Komparation · 23 Der Vokativ

**B2 (24–29):** 24 Verbalaspekt · 25 Zahlen & Numeralia ·
26 Konditional I · 27 Passiv · 28 Nebensätze & Konjunktionen ·
29 Enklitika & Wortstellung

**C1 (30–33):** 30 Konditional II & Futur II · 31 Adverbiale Partizipien ·
32 Kasusfeinheiten & Wortbildung · 33 Formelle Sprache & Stilistik

**C2 (34–37):** 34 Aorist & Imperfekt · 35 Plusquamperfekt ·
36 Inversion, Emphase & Ellipsen · 37 Dialekte & Bosnisch im Vergleich

Bewusste Taxonomie-Entscheidungen: Nominativ/Akkusativ getrennt ·
Dativ/Instrumental getrennt · Possessiv-/Demonstrativpronomen getrennt ·
Vokativ auf B1 (nicht C1) · Fälle decken Sg./Pl. intern ab
(keine eigene Pluralbildungs-Seite) · Aorist/Imperfekt erst auf C2.

---

## 4. Didaktik-Checkliste (pro Kapitel bewusst entscheiden)

1. **Hook:** Was ist der Aha-Moment? (bekannter Alltagssatz, Kontrast
   zum Deutschen, überraschendes Merkmal)
2. **Callbacks:** Welche früheren Kapitel zahlt dieses ein / greift es auf?
   (z. B. Klitika an 2. Stelle, Adjektiv-Angleichung, Genitiv nach od)
3. **Stolperfallen:** Wo machen Deutschsprachige typischerweise Fehler?
   → eigener mini-note oder Kontrasttabelle
4. **Bewusst weglassen:** Welche Feinheiten gehören in spätere Niveaus?
   Am Ende der Antwort kurz benennen (sprachlicher Hinweis).
5. **Zielgruppen-Bezug:** Wo passt Diaspora-/Kulturbezug natürlich rein?
   (Sarajevo, Familie, Grüße, Redewendungen)
6. **Bosnisch-Standard:** konsequent ijekavisch; BKS-Quellen sind valide.

---

## 5. Pflicht-Validierung nach jeder Seite

Testskript ausführen (liegt als `test_grammatikseite.py` bereit):

```
python3 test_grammatikseite.py grammatik-[thema].html
```

> **Windows:** `python` statt `python3` verwenden (`python3` startet dort den
> Microsoft-Store-Platzhalter). Die UTF-8-Konsolenausgabe stellt das Skript selbst ein.

Das Skript prüft automatisch:
- **Mobiltest** (Playwright/Chromium) bei 900/628/480/360/320 px:
  kein Seitenüberlauf; internes Scrollen von Tabellen ist OK
- 10 Quizfragen, 6 Blöcke, 6 example-cards, 6 cheatsheet-items
- Head-Pflichten (Fonts, FontAwesome, description, viewport) + Favicon
- Antwortverteilung der correct-Indizes
- Vorhandensein aller Quiz-IDs
- Vor/Zurück-Navigation (Linkziele werden angezeigt)
- ASCII-Apostrophe im Script-Bereich (muss 0 sein)

Bei Seitenüberlauf nennt das Skript zusätzlich bis zu 3 Verursacher-Kandidaten
(Tag/Klasse/Textanfang) direkt unter der Fehlermeldung — meist reicht das, um
das zu breite Element ohne weitere Handarbeit zu finden.

Danach: `present_files` mit der fertigen Datei.

CSS-Quelle für den Test: bevorzugt `/mnt/project/…`, sonst Fallback
auf die gefixten Versionen in `/mnt/user-data/outputs/`
(dort liegt der kritische `main { width: 100% }`-Fix).

---

Wenn die Prüfung erfolgreich durchgeführt wurde, dann die jeweilige Karte in LB_3_Grammatik.html von „Demnächst" auf aktiven Link umstellen

## 6. Antwortformat der Auslieferung

- Kurzer didaktischer Vorspann (Hook + Konzept) VOR der Dateierstellung
- Nach Validierung: Zusammenfassung mit didaktischer Gestaltung,
  Inhalt & Aufbau, sprachlichem Hinweis (was bewusst weggelassen wurde)
  und ggf. To-dos für Alen (Übersichtskarte aktivieren, Links anpassen)
- Erinnerung, in welchen Repo-Ordner die Datei gehört
