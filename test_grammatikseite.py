#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_grammatikseite.py — Pflicht-Validierung für LinguaBosna-Grammatikseiten

Aufruf:
    python3 test_grammatikseite.py grammatik-[thema].html
    python3 test_grammatikseite.py /voller/pfad/grammatik-[thema].html

Prüft (siehe WORKFLOW_Grammatikseiten.md, Abschnitt 5):
  1. Mobiltest via Playwright bei 900/628/480/360/320 px (kein Seitenüberlauf)
  2. Strukturzählungen: 10 Quizfragen, 6 Blöcke, 6 example-cards, 6 cheatsheet-items
  3. Head-Pflichten (Fonts, FontAwesome, description, viewport) + Favicon-Block
  4. Antwortverteilung der correct-Indizes (sollte ~3/4/3 sein)
  5. Alle Pflicht-Quiz-IDs vorhanden
  6. Vor/Zurück-Navigation (Linkziele werden angezeigt)
  7. Keine ASCII-Apostrophe in JS-Strings

Exit-Code 0 = alles bestanden, 1 = mindestens ein FEHLER.
Hinweise (⚠) sind keine Fehler, nur zum Draufschauen.
"""

import re
import sys
import pathlib
import tempfile

# ── Konfiguration ────────────────────────────────────────────────
VIEWPORTS = [900, 628, 480, 360, 320]


def find_repo_root(start, max_levels=6):
    """
    Sucht ausgehend von `start` aufwärts nach dem Repo-Root, erkennbar
    am Ordner Code/Style.css. Funktioniert unabhängig davon, in welchem
    Unterordner des Repos dieses Skript selbst liegt oder von wo aus
    es aufgerufen wird (lokal via Claude Code).
    """
    current = pathlib.Path(start).resolve()
    for _ in range(max_levels):
        if (current / "Code" / "Style.css").exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    return None


# Repo-Root zuerst vom Skript-Speicherort aus suchen, dann vom
# aktuellen Arbeitsverzeichnis aus (falls das Skript kopiert/verschoben wurde)
REPO_ROOT = (find_repo_root(pathlib.Path(__file__).resolve().parent)
             or find_repo_root(pathlib.Path.cwd()))

# CSS: bevorzugt lokale Repo-Struktur (Claude Code), sonst Fallback auf
# Projektwissen bzw. die gefixten Versionen in outputs (claude.ai-Chat;
# enthalten den kritischen main{width:100%}-Fix)
CSS_BASE_CANDIDATES = []
CSS_DETAIL_CANDIDATES = []
if REPO_ROOT:
    CSS_BASE_CANDIDATES.append(REPO_ROOT / "Code" / "Style.css")
    CSS_DETAIL_CANDIDATES.append(
        REPO_ROOT / "Code" / "3_Grammatik" / "Style_3_Grammatik_Detail.css")
CSS_BASE_CANDIDATES += [
    "/mnt/project/Style.css",
    "/mnt/user-data/outputs/Style.css",
]
CSS_DETAIL_CANDIDATES += [
    "/mnt/project/Style_3_Grammatik_Detail.css",
    "/mnt/user-data/outputs/Style_3_Grammatik_Detail.css",
]

QUIZ_IDS = [
    "quizContainer", "quizProgress", "quizBarFill", "quizQuestion",
    "quizOptions", "quizFeedback", "quizNextBtn", "quizResult",
    "resultScore", "resultText", "quizRetryBtn",
]

errors = []    # harte Fehler → Exit-Code 1
warnings = []  # Hinweise → nur Ausgabe


def find_first(paths):
    """Gibt den ersten existierenden Pfad aus einer Kandidatenliste zurück."""
    for p in paths:
        if pathlib.Path(p).exists():
            return p
    return None


def ok(msg):
    print(f"  ✓ {msg}")


def fail(msg):
    errors.append(msg)
    print(f"  ✗ FEHLER: {msg}")


def warn(msg):
    warnings.append(msg)
    print(f"  ⚠ Hinweis: {msg}")


# ── Datei einlesen ───────────────────────────────────────────────
if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(1)

arg = sys.argv[1]
page_path = pathlib.Path(arg)
if not page_path.exists():
    # Komfort: auch im outputs-Ordner suchen (claude.ai-Chat)
    alt = pathlib.Path("/mnt/user-data/outputs") / arg
    if alt.exists():
        page_path = alt
    elif REPO_ROOT and (REPO_ROOT / "Code" / "3_Grammatik").exists():
        # Komfort: in der lokalen Repo-Struktur suchen, z.B.
        # Code/3_Grammatik/Grammatik_B2/grammatik-verbalaspekt.html,
        # falls nur der Dateiname ohne Pfad übergeben wurde
        hits = list((REPO_ROOT / "Code" / "3_Grammatik").glob(
            f"Grammatik_*/{pathlib.Path(arg).name}"))
        if hits:
            page_path = hits[0]
        else:
            print(f"✗ Datei nicht gefunden: {arg}")
            sys.exit(1)
    else:
        print(f"✗ Datei nicht gefunden: {arg}")
        sys.exit(1)

html = page_path.read_text(encoding="utf-8", errors="replace")
print(f"\n══ Validierung: {page_path.name} ══════════════════════════\n")
if REPO_ROOT:
    print(f"  (Repo-Root erkannt: {REPO_ROOT})\n")
else:
    print("  (Kein lokales Repo-Root gefunden — nutze Sandbox-Fallback-Pfade)\n")

# ── 1. Strukturzählungen ─────────────────────────────────────────
print("[1] Struktur")

n_questions = len(re.findall(r"question:\s*'", html))
(ok if n_questions == 10 else fail)(
    f"Quizfragen: {n_questions} (soll 10)" if n_questions != 10
    else "Quizfragen: 10")

n_blocks = html.count('id="block-')
(ok if n_blocks == 6 else fail)(
    f"Blöcke: {n_blocks} (soll 6)" if n_blocks != 6 else "Blöcke: 6")

n_examples = html.count('class="example-card"')
(ok if n_examples == 6 else fail)(
    f"example-cards: {n_examples} (soll 6)" if n_examples != 6
    else "example-cards: 6")

n_cheats = html.count('class="cheatsheet-item"')
(ok if n_cheats == 6 else fail)(
    f"cheatsheet-items: {n_cheats} (soll 6)" if n_cheats != 6
    else "cheatsheet-items: 6")

# ── 2. Head-Pflichten & Favicon ──────────────────────────────────
print("\n[2] Head & Favicon")

head_checks = {
    "Google Fonts": "fonts.googleapis.com/css2",
    "FontAwesome 6.5.0": "font-awesome/6.5.0",
    "meta description": 'name="description"',
    "meta viewport": 'name="viewport"',
}
for label, needle in head_checks.items():
    (ok if needle in html else fail)(
        f"{label} vorhanden" if needle in html else f"{label} FEHLT")

n_favicon = html.count("favicon")
(ok if n_favicon >= 5 else fail)(
    f"Favicon-Block: {n_favicon} Treffer" if n_favicon >= 5
    else f"Favicon-Block unvollständig ({n_favicon} Treffer, soll >=5)")

# Absolute Pfade: relative CSS/JS-Verweise wären ein Fehler
if re.search(r'href="\.\./', html) or re.search(r'src="\.\./', html):
    fail("Relative Pfade (../) gefunden — absolute Pfade verwenden!")
else:
    ok("Keine relativen Pfade (../)")

# ── 3. Quiz: IDs, Verteilung, Apostrophe ─────────────────────────
print("\n[3] Quiz")

for qid in QUIZ_IDS:
    if qid not in html:
        fail(f"Quiz-ID fehlt: {qid}")
missing = [q for q in QUIZ_IDS if q not in html]
if not missing:
    ok(f"Alle {len(QUIZ_IDS)} Quiz-IDs vorhanden")

dist = {}
for m in re.findall(r"correct:\s*(\d)", html):
    dist[m] = dist.get(m, 0) + 1
dist_str = " / ".join(f"{k}:{v}" for k, v in sorted(dist.items()))
total = sum(dist.values())
if total != 10:
    fail(f"correct-Einträge: {total} (soll 10) — Verteilung {dist_str}")
elif max(dist.values()) > 5 or len(dist) < 3:
    warn(f"Antwortverteilung unausgewogen: {dist_str} (Ziel ~3/4/3)")
else:
    ok(f"Antwortverteilung: {dist_str}")

# ASCII-Apostrophe: im Script-Bereich escaped \' suchen
script_match = re.search(r"<script>(.*?)</script>", html, re.S)
if script_match:
    js = script_match.group(1)
    n_escaped = js.count("\\'")
    (ok if n_escaped == 0 else fail)(
        "Keine ASCII-Apostrophe in JS-Strings" if n_escaped == 0
        else f"{n_escaped}x escaped ASCII-Apostroph (\\') gefunden — "
             f"typografische Zeichen verwenden!")
else:
    fail("Kein Inline-Script-Block gefunden")

# ── 4. Navigation ────────────────────────────────────────────────
print("\n[4] Navigation")

nav_links = re.findall(r'href="(grammatik-[a-z0-9-]+\.html)"', html)
if len(nav_links) >= 2:
    ok(f"Seiten-Navigation: zurück → {nav_links[0]}, weiter → {nav_links[-1]}")
else:
    warn(f"Nur {len(nav_links)} grammatik-*.html-Link(s) gefunden "
         f"(erste/letzte Seite eines Niveaus kann das korrekt sein)")

breadcrumb_ok = 'class="breadcrumb"' in html and "LB_3_Grammatik.html" in html
(ok if breadcrumb_ok else fail)(
    "Breadcrumb mit Link zur Übersicht" if breadcrumb_ok
    else "Breadcrumb fehlt oder verlinkt nicht zur Übersicht")

# ── 5. Mobiltest (Playwright) ────────────────────────────────────
print("\n[5] Mobiltest (Playwright)")

base_css_path = find_first(CSS_BASE_CANDIDATES)
detail_css_path = find_first(CSS_DETAIL_CANDIDATES)

if not base_css_path or not detail_css_path:
    fail(f"CSS nicht gefunden (base: {base_css_path}, detail: {detail_css_path})")
else:
    print(f"  CSS: {base_css_path} + {detail_css_path}")
    try:
        from playwright.sync_api import sync_playwright

        base_css = pathlib.Path(base_css_path).read_text(
            encoding="utf-8", errors="replace")
        detail_css = pathlib.Path(detail_css_path).read_text(
            encoding="utf-8", errors="replace")

        body = re.search(r"<body>(.*)</body>", html, re.S).group(1)
        body = re.sub(r"<script>.*?</script>", "", body, flags=re.S)
        test_html = (f"<!DOCTYPE html><html lang=de><head><meta charset=UTF-8>"
                     f"<style>{base_css}\n{detail_css}</style></head>"
                     f"<body>{body}</body></html>")
        tmp = pathlib.Path(tempfile.gettempdir()) / "_grammatik_mobiltest.html"
        tmp.write_text(test_html, encoding="utf-8")

        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for width in VIEWPORTS:
                pg = browser.new_page(viewport={"width": width, "height": 900})
                pg.goto(tmp.resolve().as_uri())
                pg.wait_for_timeout(150)
                r = pg.evaluate("""() => {
                    const ov = document.documentElement.scrollWidth
                               - window.innerWidth;
                    const wraps = [...document.querySelectorAll(
                        '.letter-table-wrap')].map(
                        e => e.scrollWidth > e.clientWidth + 1);
                    return {ov: Math.round(ov), wraps};
                }""")
                intern = ("Tabellen scrollen intern: " + str(r["wraps"]))
                if r["ov"] <= 0:
                    ok(f"{width}px: kein Überlauf | {intern}")
                else:
                    fail(f"{width}px: ÜBERLAUF {r['ov']}px | {intern}")
                pg.close()
            browser.close()
    except ImportError:
        fail("Playwright nicht installiert "
             "(pip install playwright --break-system-packages && "
             "playwright install chromium)")
    except Exception as e:
        fail(f"Mobiltest fehlgeschlagen: {e}")

# ── Ergebnis ─────────────────────────────────────────────────────
print("\n══ Ergebnis ═══════════════════════════════════════════════")
if errors:
    print(f"✗ {len(errors)} FEHLER — Seite NICHT auslieferungsbereit:")
    for e in errors:
        print(f"   - {e}")
    sys.exit(1)
else:
    extra = f" ({len(warnings)} Hinweis(e), siehe oben)" if warnings else ""
    print(f"✓ Alle Prüfungen bestanden{extra} — Seite ist auslieferungsbereit.")
    sys.exit(0)
