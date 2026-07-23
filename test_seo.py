#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_seo.py — seitentyp-unabhängige SEO-Prüfung für LinguaBosna.

Ergänzt test_grammatikseite.py (das nur Grammatikseiten prüft): dieses Skript
prüft die SEO-Grundausstattung JEDER Seite — Startseite, Vokabeln, Lernen,
künftiger Blog usw.

Aufruf (im Repo-Root):
    python3 test_seo.py                      # alle Seiten (wie --all)
    python3 test_seo.py --all                # alle indexierbaren Seiten
    python3 test_seo.py index.html           # eine einzelne Seite
    python3 test_seo.py Code/2_Vokabeln/LB_2_Vokabeln.html

Geprüft pro Seite:
  - <meta charset> + viewport, aussagekräftiger <title> (nicht "Document"/leer)
  - meta description (Länge grob 110–170 Zeichen → sonst Hinweis)
  - Canonical (absolut, https://linguabosna.com)
  - Open Graph (og:title/description/url/image) + Twitter Card
  - JSON-LD vorhanden (Hinweis, wenn nicht) UND valide (Fehler, wenn kaputt)
  - keine offenen [PLATZHALTER]
  - LB_main.js mit defer

Sonderfälle:
  - Fragmente (LB_header/LB_footer), Blog-Platzhalter, TEMPLATE → übersprungen
  - noindex-Seiten (Impressum, Datenschutz, 404) → nur Basis-Checks
    (kein OG/JSON-LD/Canonical nötig)

Exit-Code 0 = keine Fehler, 1 = mindestens ein FEHLER.
"""

import re
import sys
import json
import pathlib

if sys.platform == "win32":  # UTF-8-Ausgabe wie in test_grammatikseite.py
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

DOMAIN = "https://linguabosna.com"

# Fragmente/Vorlagen, die keine eigenständigen Seiten sind
SKIP_NAMES = {
    "LB_header.html", "LB_footer.html",
    "TEMPLATE_Grammatik_Detailseite.html",
}

errors = []
warnings = []


def find_repo_root(start, max_levels=6):
    current = pathlib.Path(start).resolve()
    for _ in range(max_levels):
        if (current / "Code" / "Style.css").exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    return None


REPO_ROOT = (find_repo_root(pathlib.Path(__file__).resolve().parent)
             or find_repo_root(pathlib.Path.cwd()))
if REPO_ROOT is None:
    print("✗ Repo-Root nicht gefunden (kein Code/Style.css).")
    sys.exit(1)


def ok(msg):
    print(f"  ✓ {msg}")


def fail(msg):
    errors.append(msg)
    print(f"  ✗ FEHLER: {msg}")


def warn(msg):
    warnings.append(msg)
    print(f"  ⚠ Hinweis: {msg}")


def check_page(path):
    """Prüft eine einzelne Datei. Gibt True zurück, wenn geprüft wurde."""
    rel = path.relative_to(REPO_ROOT).as_posix()
    doc = path.read_text(encoding="utf-8", errors="replace")

    # Fragmente/Vorlagen überspringen
    if path.name in SKIP_NAMES or "<head>" not in doc or "<title>" not in doc:
        print(f"\n── {rel}: übersprungen (Fragment/Vorlage, keine eigene Seite)")
        return False

    is_noindex = bool(re.search(r'name="robots"[^>]*content="[^"]*noindex', doc))
    tag = " [noindex – nur Basis-Checks]" if is_noindex else ""
    print(f"\n══ {rel}{tag} ══")

    # ── Basis-Checks (für jede echte Seite) ──────────────────────────
    (ok if "charset" in doc else fail)(
        "charset vorhanden" if "charset" in doc else "meta charset FEHLT")
    (ok if 'name="viewport"' in doc else fail)(
        "viewport vorhanden" if 'name="viewport"' in doc else "viewport FEHLT")

    title = re.search(r"<title>(.*?)</title>", doc, re.S)
    ttext = title.group(1).strip() if title else ""
    if not ttext or ttext.lower() == "document":
        fail(f"Titel unbrauchbar: „{ttext}“ (aussagekräftigen <title> setzen)")
    else:
        ok(f"Titel: „{ttext}“")

    dm = re.search(r'name="description"\s+content="(.*?)"', doc, re.S)
    if not dm:
        fail("meta description FEHLT")
    else:
        dlen = len(dm.group(1).strip())
        if 110 <= dlen <= 170:
            ok(f"Description-Länge: {dlen} Zeichen")
        else:
            warn(f"Description-Länge: {dlen} Zeichen (ideal ~120–160)")

    # LB_main.js sollte defer haben (Ladeperformance)
    if 'src="/Code/LB_main.js"' in doc:
        (ok if 'LB_main.js" defer' in doc else warn)(
            "LB_main.js mit defer" if 'LB_main.js" defer' in doc
            else "LB_main.js ohne defer (Render-Blocking)")

    # ── JSON-LD-Validität (auch auf noindex-Seiten prüfen, falls vorhanden) ──
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                        doc, re.S)
    for i, block in enumerate(blocks, 1):
        try:
            json.loads(block)
        except Exception as e:
            fail(f"JSON-LD-Block {i} ist ungültiges JSON: {e}")

    # ── Erweiterte Checks nur für indexierbare Seiten ────────────────
    if is_noindex:
        return True

    # Canonical
    cm = re.search(r'rel="canonical"\s+href="(.*?)"', doc)
    if not cm:
        fail("Canonical-Link FEHLT")
    elif not cm.group(1).startswith(DOMAIN):
        fail(f"Canonical nicht absolut auf {DOMAIN}: {cm.group(1)}")
    else:
        ok("Canonical (absolut) vorhanden")

    for label, needle in [
        ("og:title", 'property="og:title"'),
        ("og:description", 'property="og:description"'),
        ("og:url", 'property="og:url"'),
        ("og:image", 'property="og:image"'),
        ("Twitter Card", 'name="twitter:card"'),
    ]:
        (ok if needle in doc else fail)(
            f"{label} vorhanden" if needle in doc else f"{label} FEHLT")

    if blocks:
        ok(f"JSON-LD vorhanden ({len(blocks)} Block/Blöcke, valide)")
    else:
        warn("Kein JSON-LD (schema.org) — für Rich Results empfohlen")

    # Offene Template-Platzhalter
    leftovers = re.findall(
        r"\[(?:THEMA|NIVEAU[^\]]*|SEO-BESCHREIBUNG[^\]]*|UNTERTITEL[^\]]*)\]", doc)
    if leftovers:
        fail(f"{len(leftovers)} offene [PLATZHALTER]: "
             f"{', '.join(sorted(set(leftovers))[:5])}")
    else:
        ok("Keine offenen [PLATZHALTER]")

    return True


def all_html():
    out = []
    for p in sorted(REPO_ROOT.rglob("*.html")):
        if ".git" in p.parts:
            continue
        out.append(p)
    return out


def main():
    args = [a for a in sys.argv[1:] if a != "--all"]
    if not args:  # ohne Argument oder mit --all: alle Seiten
        pages = all_html()
    else:
        pages = []
        for a in args:
            p = pathlib.Path(a)
            if not p.is_absolute():
                cand = REPO_ROOT / a
                p = cand if cand.exists() else p
            if not p.exists():
                print(f"✗ Datei nicht gefunden: {a}")
                sys.exit(1)
            pages.append(p.resolve())

    checked = 0
    for p in pages:
        if check_page(p):
            checked += 1

    print("\n══ Ergebnis ═══════════════════════════════════════════════")
    print(f"  Geprüfte Seiten: {checked}")
    if errors:
        print(f"✗ {len(errors)} FEHLER:")
        for e in errors:
            print(f"   - {e}")
        sys.exit(1)
    extra = f" ({len(warnings)} Hinweis(e))" if warnings else ""
    print(f"✓ Keine Fehler{extra}.")
    sys.exit(0)


if __name__ == "__main__":
    main()
