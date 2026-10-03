#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_lernen_uebung.py — Struktur-/Mobil-Validierung für LinguaBosna-Lernen-Seiten

Analog zu test_grammatikseite.py (siehe dort), aber für Code/4_Lernen/*.html.

Aufruf:
    python3 test_lernen_uebung.py lernen-[typ].html
    python3 test_lernen_uebung.py /voller/pfad/lernen-[typ].html

Wichtigster Unterschied zu test_grammatikseite.py: Lernen-Seiten tragen ihren
Inhalt NICHT statisch im HTML, sondern laden ihn per fetch() aus einer eigenen
JSON-Datei (z. B. aspektwahl_data.json) nach. Ein Mobiltest, der nur HTML+CSS
zusammenklebt und Scripts entfernt (wie bei Grammatikseiten), würde nur leere
Container sehen. Dieses Skript startet deshalb einen lokalen HTTP-Server auf
dem Repo-Root und lässt Playwright die Seite mit aktivem JavaScript laden,
damit fetch() (absolute Pfade wie /Code/4_Lernen/...) tatsächlich greift.

Geprüft:
  [1] Struktur: die drei Bildschirme (Start/Übung/Ergebnis), Set-Karten-Grid
  [2] Head-Pflichten: Fonts, FontAwesome, Favicon-Block, defer bei LB_main.js,
      keine relativen Pfade (../)
  [2b] SEO — delegiert an test_seo.py (keine Duplizierung der Prüflogik)
  [3] Mobiltest (Playwright, echter Server, JS aktiv) bei 900/628/480/360/320 px:
      Start-Bildschirm, erste Aufgabe, erstes Feedback, Ergebnis-Bildschirm
  [4] Touch-Targets: alle sichtbaren, nicht deaktivierten <button> im Bereich
      main müssen mindestens 44x44px groß sein (Projektregel, siehe CLAUDE.md)

Exit-Code 0 = alles bestanden, 1 = mindestens ein FEHLER.
Hinweise (⚠) sind keine Fehler, nur zum Draufschauen.
"""

import re
import sys
import json
import pathlib
import subprocess

# Gemeinsame Bausteine — siehe lb_testlib.py. errors/warnings hier NICHT neu
# zuweisen, sonst schreibt fail() in eine andere Liste als der Schluss ausliest.
from lb_testlib import (utf8_ausgabe, repo_root, LocalServer, overflow_js,
                        playwright_oder_fehler, VIEWPORTS, MIN_TOUCH,
                        ok, fail, warn, errors, warnings)

utf8_ausgabe()

REPO_ROOT = repo_root()

# ── Datei einlesen ───────────────────────────────────────────────
if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(1)

arg = sys.argv[1]
page_path = pathlib.Path(arg)
if not page_path.exists():
    cand = REPO_ROOT / "Code" / "4_Lernen" / pathlib.Path(arg).name
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

html = page_path.read_text(encoding="utf-8", errors="replace")
print(f"\n══ Validierung: {page_path.name} ══════════════════════════\n")
print(f"  (Repo-Root: {REPO_ROOT})\n")

# ── [1] Struktur ─────────────────────────────────────────────────
print("[1] Struktur")

struct_checks = {
    "Startschirm (id=\"startScreen\")": 'id="startScreen"',
    "Übungsschirm (id=\"uebungScreen\")": 'id="uebungScreen"',
    "Ergebnisschirm (id=\"ergebnisScreen\")": 'id="ergebnisScreen"',
    "Set-Karten-Grid (id=\"themaGrid\")": 'id="themaGrid"',
    "Fortschrittsanzeige (id=\"uebungProgress\")": 'id="uebungProgress"',
    "Fortschrittsbalken (id=\"uebungBarFill\")": 'id="uebungBarFill"',
    "Feedback-Container (id=\"uebungFeedback\")": 'id="uebungFeedback"',
    "Weiter-Button (id=\"nextBtn\")": 'id="nextBtn"',
    "Ergebnis-Score (id=\"resultScore\")": 'id="resultScore"',
    "Wiederholen-Button (id=\"retryBtn\")": 'id="retryBtn"',
}
for label, needle in struct_checks.items():
    (ok if needle in html else fail)(
        f"{label} vorhanden" if needle in html else f"{label} FEHLT")

if 'class="hidden"' not in html:
    warn("Keine Klasse \"hidden\" im HTML gefunden — Übungs-/Ergebnisschirm "
         "normalerweise standardmäßig versteckt (section id=\"uebungScreen\" "
         "class=\"hidden\")")

# ── [2] Head-Pflichten ───────────────────────────────────────────
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

if 'src="/Code/LB_main.js" defer' in html or 'src="/Code/LB_main.js"defer' in html:
    ok("LB_main.js mit defer eingebunden")
elif 'src="/Code/LB_main.js"' in html:
    fail("LB_main.js OHNE defer eingebunden (Render-Blocking)")
else:
    fail("LB_main.js FEHLT (Header/Footer würden nicht geladen)")

n_favicon = html.count("favicon")
(ok if n_favicon >= 5 else fail)(
    f"Favicon-Block: {n_favicon} Treffer" if n_favicon >= 5
    else f"Favicon-Block unvollständig ({n_favicon} Treffer, soll >=5)")

if re.search(r'href="\.\./', html) or re.search(r'src="\.\./', html):
    fail("Relative Pfade (../) gefunden — absolute Pfade verwenden!")
else:
    ok("Keine relativen Pfade (../)")

if 'href="/Code' not in html and 'src="/Code' not in html:
    warn("Keine absoluten /Code/-Pfade gefunden — Seite prüfen")

# ── [2b] SEO (delegiert an test_seo.py) ──────────────────────────
print("\n[2b] SEO (via test_seo.py)")

seo_script = REPO_ROOT / "test_seo.py"
if not seo_script.exists():
    warn("test_seo.py nicht im Repo-Root gefunden — SEO-Prüfung übersprungen")
else:
    proc = subprocess.run(
        [sys.executable, str(seo_script), str(page_path)],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
        encoding="utf-8", errors="replace")
    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.stderr and proc.stderr.strip():
        print(proc.stderr.rstrip())
    if proc.returncode != 0:
        fail("test_seo.py hat Fehler gemeldet (siehe Ausgabe oben)")
    else:
        ok("test_seo.py: keine Fehler")

# ── [3]+[4] Mobiltest & Touch-Targets (Playwright, echter Server) ─
print("\n[3] Mobiltest & Touch-Targets (Playwright, lokaler Server)")

# Scope "main": Header/Footer sind auf allen Lernen-Seiten identisch und
# werden zentral von test_usability.py geprüft.
OVERFLOW_JS = overflow_js("main")

TOUCH_JS = """() => {
    const buttons = [...document.querySelectorAll('main button')].filter(b => {
        if (b.disabled) return false;
        const cs = getComputedStyle(b);
        return cs.display !== 'none' && cs.visibility !== 'hidden' && b.offsetParent !== null;
    });
    return buttons.map(b => {
        const r = b.getBoundingClientRect();
        return {
            w: Math.round(r.width), h: Math.round(r.height),
            cls: (typeof b.className === 'string' ? b.className : ''),
            text: (b.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 30)
        };
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
                  f"(entfernt −{c['drop']}px Breite) „{c['text']}…\"")


def check_touch_targets(page, label, width):
    buttons = page.evaluate(TOUCH_JS)
    zu_klein = [b for b in buttons if b["w"] < MIN_TOUCH or b["h"] < MIN_TOUCH]
    if not buttons:
        return
    if not zu_klein:
        ok(f"{width}px [{label}]: alle {len(buttons)} Buttons ≥{MIN_TOUCH}px")
    else:
        for b in zu_klein[:5]:
            cls = f".{b['cls']}" if b["cls"] else ""
            fail(f"{width}px [{label}]: Touch-Target zu klein "
                 f"({b['w']}x{b['h']}px) <button{cls}> „{b['text']}…\"")


def wait_hidden_off(page, selector, timeout=6000):
    page.wait_for_function(
        "sel => { const e = document.querySelector(sel); "
        "return e && !e.classList.contains('hidden'); }",
        arg=selector, timeout=timeout)


def try_interact(page):
    """Best-effort: löst eine Aufgabe generisch, egal welcher Aufgabentyp.
    Gibt True zurück, wenn eine Interaktion ausgelöst werden konnte."""
    # Sofort-Typen: ein Klick auf einen Antwort-Button wertet direkt aus
    # (Körbe, Wortbank-Formen, Satzwahl — je nach Übung).
    for container_id in ("korbGrid", "wortbank", "satzwahl"):
        el = page.query_selector(f"#{container_id}")
        if el and el.is_visible():
            btn = el.query_selector("button:not([disabled])")
            if btn:
                btn.click()
                return True

    # Puzzle-Typ (Satzbau): alle Bausteine der Reihe nach anklicken,
    # dann "Prüfen".
    vorrat = page.query_selector("#satzbauVorrat")
    if vorrat and vorrat.is_visible():
        for _ in range(20):
            btn = vorrat.query_selector("button:not([disabled])")
            if not btn:
                break
            btn.click()
            page.wait_for_timeout(30)
        pruefen = page.query_selector("#pruefenBtn")
        if pruefen and pruefen.is_visible() and not pruefen.is_disabled():
            pruefen.click()
            return True

    return False


def run_playwright_checks():
    sync_playwright = playwright_oder_fehler()
    if sync_playwright is None:
        return

    # Lokalen HTTP-Server auf dem Repo-Root starten, damit die
    # absoluten fetch()-Pfade (/Code/4_Lernen/...) funktionieren.
    server = LocalServer(REPO_ROOT).start()
    url = server.url_for(rel_path)

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for width in VIEWPORTS:
                page = browser.new_page(viewport={"width": width, "height": 900})
                try:
                    page.goto(url)
                    # Bei genau einem Thema/Set startet die Seite die Übung
                    # direkt (kein Auswahlbildschirm, siehe lernen-luckentext.html
                    # seit 2026-09-01) — #themaGrid bleibt dann leer und
                    # #uebungScreen ist schon beim Laden sichtbar. Beide Fälle
                    # generisch abfangen: warten, bis EINES von beidem eintritt.
                    page.wait_for_function(
                        "() => { const g = document.getElementById('themaGrid'); "
                        "const u = document.getElementById('uebungScreen'); "
                        "return (g && g.children.length > 0) || "
                        "(u && !u.classList.contains('hidden')); }", timeout=6000)

                    karte = page.query_selector("#themaGrid button.thema-card")
                    if karte:
                        # ── Start-Bildschirm ──
                        check_overflow(page, "Start", width)
                        check_touch_targets(page, "Start", width)

                        karte.click()
                        wait_hidden_off(page, "#uebungScreen")
                    else:
                        uebung = page.query_selector("#uebungScreen")
                        if not uebung or "hidden" in (uebung.get_attribute("class") or ""):
                            warn(f"{width}px: keine Set-Karte gefunden — "
                                 f"Übungs-/Ergebnisschirm nicht geprüft")
                            page.close()
                            continue
                        # Direktstart: kein Startbildschirm zu prüfen, die
                        # Übung läuft schon.

                    # ── Erste Aufgabe (vor Antwort) ──
                    check_overflow(page, "Aufgabe", width)
                    check_touch_targets(page, "Aufgabe", width)

                    # ── Bis zu 12 Aufgaben "lösen" (Inhalt egal, es geht
                    #    um Layout), Feedback nach der ersten Aufgabe
                    #    separat prüfen, danach bis zum Ergebnisschirm
                    #    durchklicken. ──
                    feedback_geprueft = False
                    fortschritt = True
                    for _ in range(12):
                        if not try_interact(page):
                            fortschritt = False
                            break
                        try:
                            wait_hidden_off(page, "#uebungFeedback", timeout=4000)
                        except Exception:
                            fortschritt = False
                            break

                        if not feedback_geprueft:
                            check_overflow(page, "Feedback", width)
                            check_touch_targets(page, "Feedback", width)
                            feedback_geprueft = True

                        next_btn = page.query_selector("#nextBtn")
                        if not next_btn or not next_btn.is_visible():
                            break
                        next_btn.click()

                        erg = page.query_selector("#ergebnisScreen")
                        if erg and "hidden" not in (erg.get_attribute("class") or ""):
                            break
                        page.wait_for_timeout(30)

                    if not feedback_geprueft:
                        warn(f"{width}px: Feedback-Zustand nicht geprüft "
                             f"(Interaktion für diesen Aufgabentyp nicht "
                             f"generisch auslösbar — ggf. manuell prüfen)")

                    erg = page.query_selector("#ergebnisScreen")
                    if erg and "hidden" not in (erg.get_attribute("class") or ""):
                        check_overflow(page, "Ergebnis", width)
                        check_touch_targets(page, "Ergebnis", width)
                    elif fortschritt:
                        warn(f"{width}px: Ergebnisschirm innerhalb von 12 "
                             f"Aufgaben nicht erreicht — nicht geprüft")

                except Exception as e:
                    fail(f"{width}px: Mobiltest fehlgeschlagen: {e}")
                finally:
                    page.close()
            browser.close()
    finally:
        server.stop()


run_playwright_checks()

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
