#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_sitemap.py — erzeugt sitemap.xml automatisch aus allen HTML-Seiten.

Aufruf (im Repo-Root):
    python3 build_sitemap.py          # schreibt sitemap.xml neu
    python3 build_sitemap.py --check  # nur prüfen, ob sitemap.xml aktuell ist
                                      # (Exit 1, wenn veraltet — für CI/Kontrolle)

Warum ein Skript?
    Die Sitemap muss bei JEDER neuen Seite aktualisiert werden. Von Hand wird
    das vergessen. Dieses Skript sammelt alle indexierbaren Seiten selbst ein.

Was ist "indexierbar"? Aufgenommen wird jede *.html mit <head> und <title>,
AUSSER:
  - Fragmenten ohne eigenen <head> (LB_header.html, LB_footer.html, Blog-Platzhalter)
  - der Vorlage TEMPLATE_Grammatik_Detailseite.html
  - Seiten mit <meta name="robots" content="noindex..."> (z.B. Impressum,
    Datenschutz, 404) — die gehören bewusst NICHT in die Sitemap.

lastmod = Datum des letzten Git-Commits der jeweiligen Datei (fällt auf das
heutige Datum zurück, falls Git nicht verfügbar ist).
"""

import os
import re
import sys
import subprocess
import datetime
import pathlib

if sys.platform == "win32":  # UTF-8-Ausgabe wie in test_seo.py
    # Ohne diese Zeilen bricht das Skript unter Windows beim ABSCHLIESSENDEN
    # print() mit einem UnicodeEncodeError ab ("✓" gibt es in cp1252 nicht) –
    # die sitemap.xml war da längst geschrieben, es sah nur nach Fehlschlag aus.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

DOMAIN = "https://linguabosna.com"
TODAY = datetime.date.today().isoformat()

# Dateien, die nie in die Sitemap gehören (zusätzlich zur noindex-Erkennung).
# Die Header/Footer-Fragmente haben zwar einen <head> mit <title>Document</title>,
# sind aber keine eigenständigen Seiten, sondern werden per JS eingebunden.
EXCLUDE_NAMES = {
    "TEMPLATE_Grammatik_Detailseite.html",
    "LB_header.html",
    "LB_footer.html",
}


def find_repo_root(start, max_levels=6):
    """Sucht aufwärts nach dem Repo-Root (erkennbar an Code/Style.css)."""
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


def rel_html_files():
    """Alle *.html relativ zum Repo-Root, sortiert, ohne versteckte Ordner.

    Übersprungen wird JEDES Verzeichnis, dessen Name mit einem Punkt beginnt –
    nicht nur .git. Grund: Unter .claude/worktrees/ kann eine vollständige
    Arbeitskopie des Repos liegen (git worktree). Die wurde vorher mitgelesen
    und hat rund 50 Phantom-URLs der Form
    /.claude/worktrees/<branch>/Code/... in die Sitemap geschrieben – Adressen,
    die es auf linguabosna.com gar nicht gibt und die Google als doppelten
    Inhalt zur echten Seite gewertet hätte.

    Das Filtern geschieht über die dirs-Liste von os.walk: Wer sie an Ort und
    Stelle kürzt (dirs[:] = ...), verhindert, dass os.walk dort überhaupt
    hinabsteigt.
    """
    out = []
    for dp, dirs, fns in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fn in fns:
            if fn.endswith(".html"):
                rel = os.path.relpath(os.path.join(dp, fn), REPO_ROOT)
                out.append(rel.replace(os.sep, "/"))
    return sorted(out)


def git_lastmod(rel):
    """Datum des letzten Commits einer Datei (YYYY-MM-DD) oder heute."""
    try:
        res = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "log", "-1", "--format=%cs", "--", rel],
            capture_output=True, text=True, timeout=10)
        date = res.stdout.strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            return date
    except Exception:
        pass
    return TODAY


def url_for(rel):
    if rel == "index.html":
        return DOMAIN + "/"
    return DOMAIN + "/" + rel


def priority_for(rel):
    # Reihenfolge wie im ursprünglichen Sitemap-Generator (bewusst beibehalten)
    if rel == "index.html":
        return "1.0"
    if rel == "Code/1_Startseite/LB_3_Grammatik.html":
        return "0.9"
    if (rel.startswith("Code/3_Grammatik/") or rel.startswith("Code/4_Lernen/")
            or "Vokabeln" in rel or "vokabeltrainer" in rel):
        return "0.8"
    return "0.5"


def collect_entries():
    """(url, lastmod, priority)-Tupel für alle indexierbaren Seiten."""
    entries = []
    for rel in rel_html_files():
        if pathlib.PurePosixPath(rel).name in EXCLUDE_NAMES:
            continue
        doc = (REPO_ROOT / rel).read_text(encoding="utf-8", errors="replace")
        # Fragmente ohne echten Kopf überspringen
        if "<head>" not in doc or "<title>" not in doc:
            continue
        # noindex-Seiten gehören nicht in die Sitemap
        if re.search(r'name="robots"[^>]*content="[^"]*noindex', doc):
            continue
        entries.append((url_for(rel), git_lastmod(rel), priority_for(rel)))
    return entries


def render(entries):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, lastmod, prio in entries:
        lines += ['  <url>',
                  f'    <loc>{url}</loc>',
                  f'    <lastmod>{lastmod}</lastmod>',
                  f'    <priority>{prio}</priority>',
                  '  </url>']
    lines.append('</urlset>')
    return "\n".join(lines) + "\n"


def main():
    check_only = "--check" in sys.argv[1:]
    entries = collect_entries()
    xml = render(entries)
    target = REPO_ROOT / "sitemap.xml"

    if check_only:
        current = target.read_text(encoding="utf-8") if target.exists() else ""
        if current == xml:
            print(f"✓ sitemap.xml ist aktuell ({len(entries)} URLs).")
            sys.exit(0)
        print("✗ sitemap.xml ist VERALTET — bitte `python3 build_sitemap.py` "
              "ausführen und committen.")
        sys.exit(1)

    target.write_text(xml, encoding="utf-8")
    print(f"✓ sitemap.xml geschrieben: {len(entries)} URLs "
          f"(Repo-Root: {REPO_ROOT})")


if __name__ == "__main__":
    main()
