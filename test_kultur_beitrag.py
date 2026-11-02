#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_kultur_beitrag.py — Struktur-/Mobil-Validierung für den Kultur-Bereich

Analog zu test_grammatikseite.py und test_lernen_uebung.py, aber für
Code/5_Kultur/*.html. Die Regeln, die hier geprüft werden, stehen in
WORKFLOW_Kultur.md (Quelle der Wahrheit).

Aufruf (Windows: PYTHONUTF8=1 python …):
    python test_kultur_beitrag.py kultur-[thema].html
    python test_kultur_beitrag.py kultur-uebersicht.html     # Übersichtsseite
    python test_kultur_beitrag.py Code/5_Kultur/kultur-[thema].html

Geprüft bei einem BEITRAG:
  [1] Struktur: die 8 Blöcke (Kopf, Auf einen Blick, Abschnitte, Wörter,
      Quiz, Weiter geht's, Quellen), Rubrikname, Tetka-Fata-Box
  [2] Text: Wortzahl gesamt und je Abschnitt, Lesezeit-Angabe
  [3] Quiz-Daten: gültiges JSON, 4–6 Fragen à 3 Optionen, gestreute Lösung
  [4] Links: Wörterbuch-Links (Wort steht in vokabeln_flat.json?),
      keine ?kapitel=-Links, keine relativen Pfade, Ziele existieren
  [5] Bilder: alt-Text, Datei vorhanden, Größe, Bildnachweis in figcaption
  [6] Head-Pflichten + SEO (delegiert an test_seo.py)
  [7] Übersicht: Ist der Beitrag dort verlinkt?
  [8] Mobiltest (Playwright, lokaler Server) bei 900/628/480/360/320 px:
      Grundzustand, alle <details> aufgeklappt, interaktives Element
      durchgeklickt, Quiz bis zum Ergebnis – jeweils Überlauf und
      Touch-Targets (≥44px)

Bei der ÜBERSICHT: Head + SEO, alle Karten-Links existieren, jeder Beitrag
im Ordner hat eine Karte, Mobiltest.

Exit-Code 0 = alles bestanden, 1 = mindestens ein FEHLER.
Hinweise (⚠) sind keine Fehler, nur zum Draufschauen.
"""

import re
import sys
import json
import math
import html as htmllib
import pathlib
import subprocess
import urllib.parse

# Gemeinsame Bausteine — siehe lb_testlib.py. errors/warnings hier NICHT neu
# zuweisen, sonst schreibt fail() in eine andere Liste als der Schluss ausliest.
from lb_testlib import (utf8_ausgabe, repo_root, LocalServer, overflow_js,
                        playwright_oder_fehler, VIEWPORTS, MIN_TOUCH,
                        ok, fail, warn, errors, warnings)

utf8_ausgabe()

REPO_ROOT = repo_root()
KULTUR_DIR = REPO_ROOT / "Code" / "5_Kultur"

# Feste Rubriknamen laut WORKFLOW_Kultur.md, Abschnitt 2
RUBRIKEN = {
    "familie":    "Familie & Zusammenleben",
    "essen":      "Essen & Trinken",
    "musik":      "Musik & Tanz",
    "tracht":     "Tracht & Handwerk",
    "geschichte": "Geschichte & Schrift",
    "feste":      "Feste & Bräuche",
    "diaspora":   "Diaspora & Humor",
}

# Richtwerte laut WORKFLOW_Kultur.md, Abschnitt 4
WORTE_GESAMT = (400, 900)
WORTE_ABSCHNITT_MAX = 120
WOERTER_ANZAHL = (5, 10)
QUIZ_ANZAHL = (4, 6)
WEITER_ANZAHL = (2, 4)
BILD_MAX_KB = 250


# ── Datei einlesen ───────────────────────────────────────────────
if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(1)

arg = sys.argv[1]
page_path = pathlib.Path(arg)
if not page_path.exists():
    cand = KULTUR_DIR / pathlib.Path(arg).name
    if cand.exists():
        page_path = cand
    else:
        print(f"✗ Datei nicht gefunden: {arg}")
        sys.exit(1)

page_path = page_path.resolve()
try:
    rel_path = page_path.relative_to(REPO_ROOT).as_posix()
except ValueError:
    print(f"✗ Datei liegt außerhalb des Repos ({REPO_ROOT}): {page_path}")
    sys.exit(1)

doc = page_path.read_text(encoding="utf-8", errors="replace")
IST_UEBERSICHT = page_path.name == "kultur-uebersicht.html"

print(f"\n══ Validierung: {page_path.name} "
      f"({'Übersicht' if IST_UEBERSICHT else 'Beitrag'}) ══════════════\n")
print(f"  (Repo-Root: {REPO_ROOT})\n")


# ── Hilfsfunktionen ──────────────────────────────────────────────

def text_von(fragment):
    """HTML-Fragment → reiner Text (Tags weg, Entities aufgelöst)."""
    fragment = re.sub(r"<script\b.*?</script>", " ", fragment, flags=re.S)
    fragment = re.sub(r"<!--.*?-->", " ", fragment, flags=re.S)
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", htmllib.unescape(fragment)).strip()


def woerter_zaehlen(text):
    return len(re.findall(r"\w+", text))


def bloecke(klasse, tag="section"):
    """Alle <tag class="… klasse …">…</tag>-Blöcke (nicht verschachtelt)."""
    muster = (rf'<{tag}\b[^>]*class="[^"]*\b{re.escape(klasse)}\b[^"]*"[^>]*>'
              rf'(.*?)</{tag}>')
    return re.findall(muster, doc, flags=re.S)


def lokaler_pfad(href):
    """Absoluter Seitenpfad (/Code/…) → Datei im Repo, sonst None."""
    pfad = urllib.parse.urlsplit(href).path
    if not pfad.startswith("/"):
        return None
    return REPO_ROOT / urllib.parse.unquote(pfad).lstrip("/")


def vokabel_formen():
    """Alle bosnischen Formen aus vokabeln_flat.json (klein geschrieben).
    „amidžinica / strina" zählt als zwei Formen."""
    datei = REPO_ROOT / "Code" / "2_Vokabeln" / "vokabeln_flat.json"
    try:
        daten = json.loads(datei.read_text(encoding="utf-8"))
    except Exception as e:
        warn(f"vokabeln_flat.json nicht lesbar ({e}) — Wortabgleich übersprungen")
        return None
    formen = set()
    for e in daten:
        b = (e.get("Bosnisch") or "").strip().lower()
        formen.add(b)
        for teil in b.split("/"):
            formen.add(teil.strip())
    return formen


# ── [Head] Pflichten (gilt für Beitrag UND Übersicht) ────────────
def pruefe_head():
    print("[Head] Pflichten")
    pflicht = {
        "Google Fonts": "fonts.googleapis.com/css2",
        "FontAwesome 6.5.0": "font-awesome/6.5.0",
        "meta description": 'name="description"',
        "meta viewport": 'name="viewport"',
        "Style.css": 'href="/Code/Style.css"',
        "Style_5_Kultur.css": 'href="/Code/5_Kultur/Style_5_Kultur.css"',
    }
    for label, needle in pflicht.items():
        (ok if needle in doc else fail)(
            f"{label} vorhanden" if needle in doc else f"{label} FEHLT")

    for skript in ("/Code/LB_main.js", "/Code/5_Kultur/kultur.js"):
        if re.search(rf'src="{re.escape(skript)}"\s+defer', doc):
            ok(f"{skript} mit defer eingebunden")
        elif f'src="{skript}"' in doc:
            fail(f"{skript} OHNE defer eingebunden")
        else:
            fail(f"{skript} FEHLT")

    n_favicon = doc.count("favicon")
    (ok if n_favicon >= 5 else fail)(
        f"Favicon-Block: {n_favicon} Treffer" if n_favicon >= 5
        else f"Favicon-Block unvollständig ({n_favicon} Treffer, soll ≥5)")

    erwartet = "kultur-uebersicht" if IST_UEBERSICHT else "kultur-beitrag"
    if re.search(rf'<body[^>]*class="[^"]*\b{erwartet}\b', doc):
        ok(f'<body class="{erwartet}">')
    else:
        fail(f'<body> braucht class="{erwartet}" (steuert Lesebreite im CSS)')

    if re.search(r'(href|src)="\.\./', doc):
        fail("Relative Pfade (../) gefunden — absolute Pfade verwenden!")
    else:
        ok("Keine relativen Pfade (../)")


# ── [SEO] delegiert an test_seo.py ───────────────────────────────
def pruefe_seo():
    print("\n[SEO] via test_seo.py")
    seo_script = REPO_ROOT / "test_seo.py"
    if not seo_script.exists():
        warn("test_seo.py nicht gefunden — SEO-Prüfung übersprungen")
        return
    proc = subprocess.run(
        [sys.executable, str(seo_script), str(page_path)],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
        encoding="utf-8", errors="replace")
    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.returncode != 0:
        fail("test_seo.py hat Fehler gemeldet (siehe Ausgabe oben)")
    else:
        ok("test_seo.py: keine Fehler")


# ── Beitrag: [1] Struktur ────────────────────────────────────────
def pruefe_struktur():
    print("\n[1] Struktur (8 Blöcke)")

    if 'class="breadcrumb"' in doc and "kultur-uebersicht.html" in doc:
        ok("Breadcrumb mit Link zur Kultur-Übersicht")
    else:
        fail("Breadcrumb mit Link auf /Code/5_Kultur/kultur-uebersicht.html FEHLT")

    m = re.search(r'class="kultur-rubrik">(.*?)<', doc, re.S)
    rubrik = htmllib.unescape(m.group(1)).strip() if m else ""
    if not rubrik:
        fail("Rubrik (span.kultur-rubrik) FEHLT")
    elif rubrik in RUBRIKEN.values():
        ok(f"Rubrik: „{rubrik}“")
    else:
        fail(f"Unbekannte Rubrik „{rubrik}“ — erlaubt: "
             + ", ".join(RUBRIKEN.values()))

    n_h1 = len(re.findall(r"<h1\b", doc))
    (ok if n_h1 == 1 else fail)(
        "genau ein <h1>" if n_h1 == 1 else f"{n_h1}× <h1> (soll genau 1)")

    for label, needle in {"Unterzeile": 'class="kultur-unterzeile"',
                          "Lesezeit": 'class="kultur-meta"'}.items():
        (ok if needle in doc else fail)(
            f"{label} vorhanden" if needle in doc else f"{label} FEHLT")

    blick = bloecke("kultur-blick")
    if not blick:
        fail("„Auf einen Blick“ (section.kultur-blick) FEHLT")
    else:
        n = len(re.findall(r"<li\b", blick[0]))
        (ok if n == 3 else fail)(
            "„Auf einen Blick“: 3 Stichpunkte" if n == 3
            else f"„Auf einen Blick“: {n} Stichpunkte (soll genau 3)")

    abschnitte = bloecke("kultur-abschnitt")
    if 2 <= len(abschnitte) <= 4:
        ok(f"{len(abschnitte)} Abschnitte")
    else:
        fail(f"{len(abschnitte)} Abschnitte (soll 2–4)")
    for i, a in enumerate(abschnitte, 1):
        h2 = re.search(r"<h2[^>]*>(.*?)</h2>", a, re.S)
        if not h2:
            fail(f"Abschnitt {i}: Überschrift <h2> FEHLT")
        elif not text_von(h2.group(1)).endswith("?"):
            warn(f"Abschnitt {i}: Überschrift ist keine Frage "
                 f"(„{text_von(h2.group(1))}“)")

    n_tetka = doc.count('class="kultur-tetka"')
    if n_tetka == 0:
        warn("Keine „Tetka Fata meint“-Box (empfohlen: 1–2 pro Beitrag)")
    elif n_tetka > 2:
        warn(f"{n_tetka} Tetka-Fata-Boxen (empfohlen: höchstens 2)")
    else:
        ok(f"{n_tetka}× Tetka Fata")

    for label, klasse in {"Wörter aus diesem Beitrag": "kultur-woerter",
                          "Mini-Quiz": "kultur-quiz",
                          "Weiter geht's": "kultur-weiter",
                          "Quellen & Bildnachweis": "kultur-quellen"}.items():
        (ok if bloecke(klasse) else fail)(
            f"Block „{label}“ vorhanden" if bloecke(klasse)
            else f"Block „{label}“ (section.{klasse}) FEHLT")

    quiz_ids = ["quizContainer", "quizProgress", "quizBarFill", "quizQuestion",
                "quizOptions", "quizFeedback", "quizNextBtn", "quizResult",
                "resultScore", "resultText", "quizRetryBtn"]
    fehlend = [i for i in quiz_ids if f'id="{i}"' not in doc]
    (ok if not fehlend else fail)(
        "alle Quiz-IDs vorhanden" if not fehlend
        else "Quiz-IDs fehlen: " + ", ".join(fehlend))

    if re.search(r"\[[A-ZÄÖÜ][A-ZÄÖÜ0-9 \-–]{2,}", doc):
        fail("Offene [PLATZHALTER] aus der Vorlage gefunden")
    else:
        ok("Keine offenen [PLATZHALTER]")

    return abschnitte, blick


# ── Beitrag: [2] Textlänge & Lesezeit ────────────────────────────
def pruefe_text(abschnitte, blick):
    print("\n[2] Textlänge & Lesezeit")

    gesamt = 0
    for i, a in enumerate(abschnitte, 1):
        # Begriffslisten zählen nicht als Fließtext, Boxen schon
        ohne_liste = re.sub(r'<dl class="kultur-begriffe".*?</dl>', " ", a, flags=re.S)
        n = woerter_zaehlen(text_von(ohne_liste))
        gesamt += n
        # Richtwert gilt für den Fließtext; Boxen (Wusstest du / Tetka)
        # dürfen dazukommen, deshalb nur der reine <p>-Text ohne Boxen
        kern = re.sub(r'<(div|aside) class="kultur-(wusstest|tetka)".*?</\1>',
                      " ", ohne_liste, flags=re.S)
        n_kern = woerter_zaehlen(text_von(kern))
        if n_kern > WORTE_ABSCHNITT_MAX:
            warn(f"Abschnitt {i}: {n_kern} Wörter Fließtext "
                 f"(Richtwert ≤{WORTE_ABSCHNITT_MAX})")
        else:
            ok(f"Abschnitt {i}: {n_kern} Wörter Fließtext (+ Boxen: {n - n_kern})")

    for b in blick:
        gesamt += woerter_zaehlen(text_von(b))
    for b in bloecke("kultur-interaktiv"):
        # Nur Überschrift + Hinweis zählen, nicht Tabellen/Buttons
        hinweis = re.search(r'class="kultur-interaktiv-hinweis">(.*?)</p>', b, re.S)
        if hinweis:
            gesamt += woerter_zaehlen(text_von(hinweis.group(1)))

    lo, hi = WORTE_GESAMT
    if lo <= gesamt <= hi:
        ok(f"Gesamt: {gesamt} Wörter (Richtwert {lo}–{hi})")
    else:
        warn(f"Gesamt: {gesamt} Wörter (Richtwert {lo}–{hi})")

    erwartet = max(1, math.ceil(gesamt / 200))
    m = re.search(r'class="kultur-meta".*?(\d+)\s*Min', doc, re.S)
    if not m:
        fail("Lesezeit-Angabe „N Min.“ nicht gefunden")
    else:
        angabe = int(m.group(1))
        if abs(angabe - erwartet) <= 1:
            ok(f"Lesezeit „{angabe} Min.“ passt (gerechnet: {erwartet})")
        else:
            warn(f"Lesezeit „{angabe} Min.“, gerechnet {erwartet} Min. "
                 f"({gesamt} Wörter ÷ 200)")
        return angabe
    return None


# ── Beitrag: [3] Quiz-Daten ──────────────────────────────────────
def pruefe_quiz():
    print("\n[3] Quiz-Daten (JSON)")
    m = re.search(r'<script type="application/json" id="kulturQuizDaten">(.*?)</script>',
                  doc, re.S)
    if not m:
        fail('Quiz-Daten (<script type="application/json" id="kulturQuizDaten">) FEHLEN')
        return
    try:
        daten = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        fail(f"Quiz-JSON ungültig: {e} (gerades \" im Text? → „ “ verwenden)")
        return
    ok("Quiz-JSON gültig")

    fragen = daten.get("fragen") or []
    lo, hi = QUIZ_ANZAHL
    (ok if lo <= len(fragen) <= hi else fail)(
        f"{len(fragen)} Fragen" if lo <= len(fragen) <= hi
        else f"{len(fragen)} Fragen (soll {lo}–{hi})")

    loesungen = []
    for i, f in enumerate(fragen, 1):
        fehlt = [k for k in ("frage", "optionen", "richtig", "erklaerung") if k not in f]
        if fehlt:
            fail(f"Frage {i}: Felder fehlen: {', '.join(fehlt)}")
            continue
        if len(f["optionen"]) != 3:
            fail(f"Frage {i}: {len(f['optionen'])} Optionen (soll genau 3)")
        if not isinstance(f["richtig"], int) or not 0 <= f["richtig"] < len(f["optionen"]):
            fail(f"Frage {i}: „richtig“ = {f['richtig']} liegt außerhalb der Optionen")
        if len(set(f["optionen"])) != len(f["optionen"]):
            fail(f"Frage {i}: doppelte Antwortoption")
        loesungen.append(f["richtig"])

    if loesungen and len(set(loesungen)) == 1:
        warn(f"Die richtige Antwort steht immer an Stelle {loesungen[0]} — streuen!")
    elif loesungen:
        ok(f"Lösungen gestreut: {loesungen}")

    texte = daten.get("ergebnis") or {}
    fehlt = [k for k in ("top", "gut", "rest") if not texte.get(k)]
    (ok if not fehlt else fail)(
        "Ergebnistexte top/gut/rest vorhanden" if not fehlt
        else "Ergebnistexte fehlen: " + ", ".join(fehlt))


# ── Beitrag: [4] Links ───────────────────────────────────────────
def pruefe_links():
    print("\n[4] Links")

    if "?kapitel=" in doc or "&kapitel=" in doc:
        fail("?kapitel=N-Link gefunden — Kapitelnummern können sich ändern, "
             "stattdessen Wörterbuch-Suche ?q=wort verlinken")
    else:
        ok("Keine ?kapitel=-Links")

    # Wörterbuch-Links: steht das Wort so in vokabeln_flat.json?
    formen = vokabel_formen()
    woerter = bloecke("kultur-woerter")
    if woerter:
        # Nur die Wortkarten (<li><a …>), nicht der Hinweis-Link darunter
        links = re.findall(r'<li>\s*<a href="/Code/2_Vokabeln/LB_2-2_Woerterbuch\.html\?q=([^"]+)"',
                           woerter[0])
        lo, hi = WOERTER_ANZAHL
        (ok if lo <= len(links) <= hi else fail)(
            f"{len(links)} Wörter verlinkt" if lo <= len(links) <= hi
            else f"{len(links)} Wörter in „Wörter aus diesem Beitrag“ (soll {lo}–{hi})")
        n_bs = len(re.findall(r'class="wort" lang="bs"', woerter[0]))
        if n_bs != len(links):
            fail(f"{len(links) - n_bs} Wörter ohne lang=\"bs\" (span.wort)")
        if formen is not None:
            for q in links:
                wort = urllib.parse.unquote(htmllib.unescape(q)).strip().lower()
                if wort in formen:
                    ok(f"„{wort}“ steht in vokabeln_flat.json")
                else:
                    warn(f"„{wort}“ steht NICHT so in vokabeln_flat.json — "
                         f"Wortform prüfen (Suche liefert evtl. nichts)")

    # Weiter geht's: 2–4 Links, mindestens einer zur Sprache
    weiter = bloecke("kultur-weiter")
    if weiter:
        hrefs = re.findall(r'<a\b[^>]*href="([^"]+)"', weiter[0])
        lo, hi = WEITER_ANZAHL
        (ok if lo <= len(hrefs) <= hi else fail)(
            f"„Weiter geht's“: {len(hrefs)} Links" if lo <= len(hrefs) <= hi
            else f"„Weiter geht's“: {len(hrefs)} Links (soll {lo}–{hi})")
        sprache = [h for h in hrefs if any(s in h for s in
                   ("/Code/3_Grammatik/", "/Code/4_Lernen/", "/Code/2_Vokabeln/",
                    "LB_3_Grammatik.html"))]
        (ok if sprache else fail)(
            "mindestens ein Link zu Grammatik/Lernen/Vokabeln" if sprache
            else "„Weiter geht's“ braucht mindestens einen Link zu Grammatik, "
                 "Lernen oder Vokabeln")

    # Alle internen Ziele existieren?
    tot = []
    for href in set(re.findall(r'<a\b[^>]*href="(/[^"#]*)', doc)):
        ziel = lokaler_pfad(href)
        if ziel is not None and not ziel.exists():
            tot.append(href)
    if tot:
        for t in sorted(tot):
            fail(f"Link-Ziel existiert nicht: {t}")
    else:
        ok("Alle internen Link-Ziele existieren")


# ── Beitrag: [5] Bilder ──────────────────────────────────────────
def pruefe_bilder():
    print("\n[5] Bilder & Bildnachweis")
    main = re.search(r"<main\b.*?</main>", doc, re.S)
    main = main.group(0) if main else ""

    imgs = re.findall(r"<img\b[^>]*>", main)
    for tag in imgs:
        src = re.search(r'src="([^"]+)"', tag)
        src = src.group(1) if src else ""
        alt = re.search(r'alt="([^"]*)"', tag)
        if not alt or not alt.group(1).strip():
            fail(f"Bild ohne alt-Text: {src}")
        if not re.search(r'\bwidth="\d+"', tag) or not re.search(r'\bheight="\d+"', tag):
            warn(f"Bild ohne width/height (Seite springt beim Laden): {src}")
        datei = lokaler_pfad(src)
        if datei is None:
            fail(f"Bild nicht lokal unter /Bilder/ abgelegt: {src}")
        elif not datei.exists():
            fail(f"Bilddatei fehlt: {src}")
        else:
            kb = datei.stat().st_size / 1024
            if kb > BILD_MAX_KB:
                warn(f"Bild {src}: {kb:.0f} KB (Richtwert < {BILD_MAX_KB} KB)")
            if datei.suffix.lower() != ".webp":
                warn(f"Bild {src}: kein WebP (Richtwert laut WORKFLOW_Kultur.md)")
            if datei.exists() and kb <= BILD_MAX_KB:
                ok(f"Bild {src} ({kb:.0f} KB)")

    figuren = re.findall(r"<figure\b.*?</figure>", main, re.S)
    for i, fig in enumerate(figuren, 1):
        cap = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", fig, re.S)
        cap = text_von(cap.group(1)) if cap else ""
        if re.search(r"\b(Foto|Bild|Illustration):", cap):
            ok(f"Abbildung {i}: Bildnachweis vorhanden")
        else:
            fail(f"Abbildung {i}: Bildnachweis fehlt — figcaption braucht "
                 f"„Foto: …“, „Bild: KI-generiert (…)“ oder „Illustration: …“")

    # Bilder außerhalb einer <figure> (z. B. Tetka-Fata-Avatar) brauchen
    # keinen sichtbaren Nachweis am Bild, aber einen in den Quellen
    if not imgs and not figuren:
        ok("Keine Bilder (Bildblock ist optional)")


# ── Beitrag: [7] Verlinkung auf der Übersicht ────────────────────
def pruefe_uebersicht_eintrag():
    print("\n[7] Übersicht")
    uebersicht = KULTUR_DIR / "kultur-uebersicht.html"
    if not uebersicht.exists():
        fail("kultur-uebersicht.html fehlt")
        return
    u = uebersicht.read_text(encoding="utf-8", errors="replace")
    if f'href="/Code/5_Kultur/{page_path.name}"' in u:
        ok("Beitrag ist auf der Kultur-Übersicht verlinkt")
    else:
        warn("Beitrag ist auf kultur-uebersicht.html (noch) nicht verlinkt "
             "— Karte von „Demnächst“ auf aktiven Link umstellen")


# ── Übersicht: Karten ────────────────────────────────────────────
def pruefe_uebersicht_karten():
    print("\n[1] Karten")
    # Kommentare entfernen – der Kopfkommentar zeigt Beispiel-Karten mit „…"
    ohne_kommentare = re.sub(r"<!--.*?-->", " ", doc, flags=re.S)
    aktive = re.findall(r'<a\s+href="([^"]+)"\s+class="kultur-card"[^>]*>', ohne_kommentare)
    aktive += re.findall(r'<a\s+class="kultur-card"[^>]*href="([^"]+)"', ohne_kommentare)
    karten = re.findall(r'class="kultur-card[^"]*"[^>]*data-rubrik="([^"]*)"', ohne_kommentare)
    ok(f"{len(aktive)} aktive Karte(n), "
       f"{ohne_kommentare.count('kultur-card demnaechst')} „Demnächst“")

    for r in karten:
        if r not in RUBRIKEN:
            fail(f'Unbekannte data-rubrik="{r}" — erlaubt: ' + ", ".join(RUBRIKEN))
    for href in aktive:
        ziel = lokaler_pfad(href)
        if ziel is None or not ziel.exists():
            fail(f"Karte verlinkt auf nicht vorhandene Seite: {href}")
        else:
            ok(f"Karte → {href}")

    verlinkt = {pathlib.Path(h).name for h in aktive}
    for datei in sorted(KULTUR_DIR.glob("kultur-*.html")):
        if datei.name != "kultur-uebersicht.html" and datei.name not in verlinkt:
            warn(f"{datei.name} hat keine aktive Karte auf der Übersicht")


# ── [8] Mobiltest (Playwright) ───────────────────────────────────
OVERFLOW_JS = overflow_js("main")

# Alles Klickbare in main: Buttons, Links mit Kartencharakter, <summary>.
# Fließtext-Links (z. B. „Wörterbuch“ mitten im Satz) sind ausgenommen –
# für Inline-Links gilt die 44px-Regel nach WCAG nicht.
TOUCH_JS = """() => {
    const sel = 'main button, main summary, main a.kultur-card, '
              + 'main .kultur-woerter li > a, main .kultur-weiter-grid a';
    const els = [...document.querySelectorAll(sel)].filter(b => {
        if (b.disabled) return false;
        const cs = getComputedStyle(b);
        return cs.display !== 'none' && cs.visibility !== 'hidden' && b.offsetParent !== null;
    });
    return els.map(b => {
        const r = b.getBoundingClientRect();
        return { w: Math.round(r.width), h: Math.round(r.height), tag: b.tagName,
                 text: (b.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 30) };
    });
}"""


def check_overflow(page, label, width):
    r = page.evaluate(OVERFLOW_JS)
    if r["ov"] <= 0:
        ok(f"{width}px [{label}]: kein Überlauf")
    else:
        fail(f"{width}px [{label}]: ÜBERLAUF {r['ov']}px")
        for c in r["culprits"]:
            cls = f".{c['cls']}" if c["cls"] else ""
            print(f"      → Verursacher-Kandidat: <{c['tag'].lower()}{cls}> "
                  f"(−{c['drop']}px) „{c['text']}…“")


def check_touch(page, label, width):
    els = page.evaluate(TOUCH_JS)
    zu_klein = [b for b in els if b["w"] < MIN_TOUCH or b["h"] < MIN_TOUCH]
    if not els:
        return
    if not zu_klein:
        ok(f"{width}px [{label}]: alle {len(els)} Bedienelemente ≥{MIN_TOUCH}px")
    for b in zu_klein[:5]:
        fail(f"{width}px [{label}]: Touch-Target zu klein ({b['w']}x{b['h']}px) "
             f"<{b['tag'].lower()}> „{b['text']}…“")


def interaktiv_durchklicken(page):
    """Klickt im interaktiven Element bis zu 4× – jeweils in der LETZTEN
    sichtbaren Button-Gruppe (.kultur-wahl) den ersten noch nicht gewählten
    Button. So arbeitet sich der Test bei mehrstufigen Elementen
    (Schritt 1 → Schritt 2 → Ergebnis) automatisch bis zum Ende durch.
    Gibt True zurück, wenn mindestens ein Klick möglich war."""
    geklickt = False
    for _ in range(4):
        btn = page.evaluate_handle("""() => {
            const gruppen = [...document.querySelectorAll('.kultur-interaktiv .kultur-wahl')]
                .filter(g => g.offsetParent !== null);
            const letzte = gruppen[gruppen.length - 1];
            return letzte ? letzte.querySelector(
                "button:not([disabled]):not([aria-pressed='true'])") : null;
        }""").as_element()
        if not btn:
            break
        btn.click()
        page.wait_for_timeout(60)
        geklickt = True
    return geklickt


def quiz_durchklicken(page):
    """Beantwortet alle Fragen (immer Option 1) bis zum Ergebnis."""
    for _ in range(QUIZ_ANZAHL[1] + 1):
        opt = page.query_selector("#quizOptions button:not([disabled])")
        if not opt:
            break
        opt.click()
        page.wait_for_timeout(50)
        weiter = page.query_selector("#quizNextBtn")
        if weiter and weiter.is_visible():
            weiter.click()
            page.wait_for_timeout(50)
        else:
            # letzte Frage: Ergebnis erscheint nach 1,2 s
            page.wait_for_selector("#quizResult:not(.hidden)", timeout=4000)
            return True
    return False


def run_playwright():
    print("\n[8] Mobiltest & Touch-Targets (Playwright, lokaler Server)")
    sync_playwright = playwright_oder_fehler()
    if sync_playwright is None:
        return
    server = LocalServer(REPO_ROOT).start()
    url = server.url_for(rel_path)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for width in VIEWPORTS:
                page = browser.new_page(viewport={"width": width, "height": 900})
                try:
                    page.goto(url)
                    page.wait_for_load_state("networkidle")

                    check_overflow(page, "Grundzustand", width)
                    check_touch(page, "Grundzustand", width)

                    if page.query_selector("main details"):
                        page.evaluate("() => document.querySelectorAll('main details')"
                                      ".forEach(d => d.open = true)")
                        check_overflow(page, "Tabellen aufgeklappt", width)

                    if not IST_UEBERSICHT:
                        if interaktiv_durchklicken(page):
                            check_overflow(page, "Interaktiv", width)
                            check_touch(page, "Interaktiv", width)

                        opt = page.query_selector("#quizOptions button")
                        if opt:
                            opt.click()
                            page.wait_for_timeout(50)
                            check_overflow(page, "Quiz-Feedback", width)
                            check_touch(page, "Quiz-Feedback", width)
                            weiter = page.query_selector("#quizNextBtn")
                            if weiter and weiter.is_visible():
                                weiter.click()
                            if quiz_durchklicken(page):
                                check_overflow(page, "Quiz-Ergebnis", width)
                                check_touch(page, "Quiz-Ergebnis", width)
                            else:
                                warn(f"{width}px: Quiz-Ergebnis nicht erreicht")
                        else:
                            fail(f"{width}px: Quiz zeigt keine Antwortbuttons "
                                 f"(kultur.js geladen? JSON gültig?)")
                    else:
                        btns = page.query_selector_all(".kultur-filter button")
                        if len(btns) > 1:
                            btns[1].click()
                            page.wait_for_timeout(50)
                            check_overflow(page, "Filter aktiv", width)
                except Exception as e:
                    fail(f"{width}px: Mobiltest fehlgeschlagen: {e}")
                finally:
                    page.close()
            browser.close()
    finally:
        server.stop()


# ── Ablauf ───────────────────────────────────────────────────────
pruefe_head()
pruefe_seo()

if IST_UEBERSICHT:
    pruefe_uebersicht_karten()
else:
    abschnitte, blick = pruefe_struktur()
    pruefe_text(abschnitte, blick)
    pruefe_quiz()
    pruefe_links()
    pruefe_bilder()
    pruefe_uebersicht_eintrag()

run_playwright()

print("\n══ Ergebnis ═══════════════════════════════════════════════")
if errors:
    print(f"✗ {len(errors)} FEHLER — Seite NICHT auslieferungsbereit:")
    for e in errors:
        print(f"   - {e}")
    sys.exit(1)
extra = f" ({len(warnings)} Hinweis(e), siehe oben)" if warnings else ""
print(f"✓ Alle Prüfungen bestanden{extra} — Seite ist auslieferungsbereit.")
sys.exit(0)
