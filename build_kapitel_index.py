#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_kapitel_index.py — erzeugt kapitel_index.json aus vokabeln_flat.json.

Aufruf (im Repo-Root):
    python3 build_kapitel_index.py          # schreibt kapitel_index.json neu
    python3 build_kapitel_index.py --check  # nur prüfen, ob der Index aktuell
                                             # ist (Exit 1, wenn veraltet)

Warum ein eigener Index?
    vokabeln_flat.json enthält alle ~2.900 Vokabeln (mehrere hundert KB) und
    wird von der Vokabel-Übersicht (LB_2_Vokabeln.html) bisher komplett
    geladen, obwohl die Seite dort nur Kapitelnummer, -name, Niveau und
    Anzahl pro Kapitel braucht (97 Zeilen). kapitel_index.json enthält genau
    diese Metadaten und ist dadurch um ein Vielfaches kleiner.

    Einträge mit "nur_woerterbuch": true gehören zu keinem Kapitel (siehe
    CLAUDE.md) und werden hier bewusst ausgeschlossen — sonst entstünde eine
    leere "Kapitel undefined"-Karte.

Kapitelnummern werden NICHT fest verdrahtet, nur aus der JSON übernommen —
das ist Bedingung dafür, dass eine künftige Neunummerierung (wie im August
2026) weiterhin ohne Codeänderung funktioniert.

Nach JEDER Änderung an vokabeln_flat.json ausführen und kapitel_index.json
mitcommitten (analog zu build_sitemap.py / sitemap.xml).
"""

import json
import pathlib
import sys

if sys.platform == "win32":  # UTF-8-Ausgabe wie in test_seo.py
    # Ohne diese Zeilen bricht das Skript unter Windows beim abschließenden
    # print() mit einem UnicodeEncodeError ab ("✓" gibt es in cp1252 nicht) –
    # die Arbeit war da längst getan, es sah nur nach Fehlschlag aus.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

VOKABELN_REL = pathlib.Path("Code/2_Vokabeln/vokabeln_flat.json")
INDEX_REL    = pathlib.Path("Code/2_Vokabeln/kapitel_index.json")


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


def build_index():
    """Liest vokabeln_flat.json und baut die Kapitelliste (Reihenfolge nach
    erstem Auftreten in der Datei = Kapitelnummer-Sortierung laut Projektregel)."""
    path = REPO_ROOT / VOKABELN_REL
    data = json.loads(path.read_text(encoding="utf-8"))

    chapters = {}
    order = []
    for entry in data:
        if entry.get("nur_woerterbuch"):
            continue
        kap = entry["Kapitel"]
        if kap not in chapters:
            chapters[kap] = {
                "Kapitel":     kap,
                "Kapitelname": entry["Kapitelname"],
                "Niveau":      entry["Niveau"],
                "Anzahl":      0,
            }
            order.append(kap)
        chapters[kap]["Anzahl"] += 1

    return [chapters[k] for k in order]


def render(index):
    return json.dumps(index, ensure_ascii=False, indent=2) + "\n"


def main():
    check_only = "--check" in sys.argv[1:]
    index = build_index()
    text = render(index)
    target = REPO_ROOT / INDEX_REL

    if check_only:
        current = target.read_text(encoding="utf-8") if target.exists() else ""
        if current == text:
            print(f"✓ kapitel_index.json ist aktuell ({len(index)} Kapitel).")
            sys.exit(0)
        print("✗ kapitel_index.json ist VERALTET — bitte "
              "`python3 build_kapitel_index.py` ausführen und committen.")
        sys.exit(1)

    target.write_text(text, encoding="utf-8")
    print(f"✓ kapitel_index.json geschrieben: {len(index)} Kapitel "
          f"(Repo-Root: {REPO_ROOT})")


if __name__ == "__main__":
    main()
