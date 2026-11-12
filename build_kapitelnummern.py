#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_kapitelnummern.py — sortiert die Vokabelkapitel nach Niveau und
nummeriert sie lückenlos neu durch.

Aufruf (im Repo-Root):
    python build_kapitelnummern.py           # schreibt vokabeln_flat.json neu
    python build_kapitelnummern.py --check   # nur prüfen, Exit 1 wenn unsortiert

WARUM GIBT ES DAS?
------------------
Die Kapitelnummern müssen mit dem Niveau aufsteigen: erst alle A1-Kapitel,
dann A2, B1, B2, C1, C2. Die Buttons "Vorheriges/Nächstes Kapitel" (im
Vokabeltrainer und auf der Kapitelseite) gehen strikt nach Nummer. Wurden
neue Kapitel einfach hinten angehängt (so geschehen mit dem Tiere-Block
98–110 und dem Familien-Block 111–130), liegen A2-Kapitel hinter C2-
Kapiteln — "Weiter" sprang dann von A2 direkt nach B1 und ließ neun A2-
Kapitel aus, und nach dem letzten C2-Kapitel ging es zurück zu A2.

SO ARBEITEST DU MIT NEUEN KAPITELN
----------------------------------
1. Neue Kapitel hinten in vokabeln_flat.json anhängen, mit der nächsten
   freien Nummer (z. B. 131, 132 …) und ihrem richtigen Niveau.
2. `python build_kapitelnummern.py` ausführen. Das Skript sortiert stabil
   nach (Niveau, bisherige Nummer): Die Reihenfolge INNERHALB eines Niveaus
   bleibt, die neuen Kapitel landen am Ende ihres Niveaus, alle Nummern
   dahinter rücken nach.
3. Danach die drei üblichen Skripte (Reihenfolge beachten):
       python build_kapitel_index.py
       python build_woerterbuch.py
       python build_sitemap.py
4. `python test_vokabeln.py` — prüft, dass alles stimmt.

Das Verschieben von Nummern ist unkritisch, weil keine Datei Kapitelnummern
fest verdrahtet hat (siehe CLAUDE.md, „Globale Neunummerierung"). Einziger
Nebeneffekt: alte `?kapitel=N`-Links (Lesezeichen, Google) zeigen danach auf
ein anderes Kapitel, und gespeicherter Lernfortschritt zu verschobenen
Kapiteln wird zurückgesetzt (LB_fortschritt.js erkennt das am Kapitelnamen).

WAS DAS SKRIPT AN DER DATEI ÄNDERT
----------------------------------
Nur die Felder "Kapitel" und "kategorie" und die Reihenfolge der Einträge
(die Datei bleibt nach Kapitelnummer sortiert). `nur_woerterbuch`-Einträge
bleiben unberührt am Dateiende. Vor dem Schreiben prüft das Skript, dass es
die vorhandene Datei byte-genau reproduzieren kann — sonst bricht es ab,
statt die Formatierung der Datei zu verändern.
"""

import json
import pathlib
import sys

from lb_testlib import utf8_ausgabe, repo_root

utf8_ausgabe()

VOKABELN_REL = pathlib.Path("Code/2_Vokabeln/vokabeln_flat.json")
NIVEAUS = ["A1", "A2", "B1", "B2", "C1", "C2"]

REPO_ROOT = repo_root()


def serialisieren(daten, zeilenende):
    """Gleiches Format wie die vorhandene Datei: 2 Leerzeichen Einzug,
    Umlaute unverändert (ensure_ascii=False), Zeilenende wie in der Datei."""
    text = json.dumps(daten, ensure_ascii=False, indent=2)
    return text.replace("\n", zeilenende)


def neue_nummern(daten):
    """Liefert {alte Nummer: neue Nummer}. Sortiert wird nach
    (Niveau, bisherige Nummer) — stabil, also bleibt die Reihenfolge
    innerhalb eines Niveaus erhalten."""
    niveau_von = {}
    for e in daten:
        if not e.get("nur_woerterbuch"):
            niveau_von.setdefault(e["Kapitel"], e["Niveau"])
    reihenfolge = sorted(niveau_von,
                         key=lambda n: (NIVEAUS.index(niveau_von[n]), n))
    return {alt: neu for neu, alt in enumerate(reihenfolge, start=1)}


def main():
    nur_pruefen = "--check" in sys.argv[1:]
    pfad = REPO_ROOT / VOKABELN_REL
    roh = pfad.read_bytes().decode("utf-8")
    daten = json.loads(roh)

    # Zeilenende (Windows: \r\n) und abschließenden Umbruch der Datei merken,
    # damit das Neuschreiben sonst nichts verändert.
    zeilenende = "\r\n" if "\r\n" in roh else "\n"
    endumbruch = zeilenende if roh.endswith(zeilenende) else ""

    mapping = neue_nummern(daten)
    verschoben = {a: n for a, n in mapping.items() if a != n}

    if nur_pruefen:
        if not verschoben:
            print(f"✓ Kapitelnummern sind nach Niveau sortiert "
                  f"({len(mapping)} Kapitel).")
            sys.exit(0)
        print(f"✗ {len(verschoben)} von {len(mapping)} Kapiteln stehen nicht "
              f"in Niveau-Reihenfolge — bitte "
              f"`python build_kapitelnummern.py` ausführen.")
        sys.exit(1)

    if not verschoben:
        print(f"✓ Nichts zu tun: alle {len(mapping)} Kapitel sind schon "
              f"nach Niveau nummeriert.")
        return

    # Sicherung: Ohne Änderung muss exakt die vorhandene Datei herauskommen.
    if serialisieren(daten, zeilenende) + endumbruch != roh:
        print("✗ Abbruch: Die Datei lässt sich nicht byte-genau "
              "reproduzieren (anderes JSON-Format?). Nichts geschrieben.")
        sys.exit(1)

    kapitel_eintraege = [e for e in daten if not e.get("nur_woerterbuch")]
    nur_woerterbuch = [e for e in daten if e.get("nur_woerterbuch")]

    for e in kapitel_eintraege:
        neu = mapping[e["Kapitel"]]
        e["Kapitel"] = neu
        e["kategorie"] = f"Kapitel {neu}"

    # Datei bleibt nach Kapitelnummer sortiert (sort ist stabil: die
    # Reihenfolge der Einträge innerhalb eines Kapitels bleibt gleich).
    kapitel_eintraege.sort(key=lambda e: e["Kapitel"])
    ergebnis = kapitel_eintraege + nur_woerterbuch

    pfad.write_bytes((serialisieren(ergebnis, zeilenende) + endumbruch)
                     .encode("utf-8"))

    print(f"✓ {len(verschoben)} von {len(mapping)} Kapiteln neu nummeriert "
          f"(Repo-Root: {REPO_ROOT}):")
    for alt in sorted(verschoben):
        print(f"    {alt:>3} → {verschoben[alt]:>3}")
    print("\n  Nicht vergessen (in dieser Reihenfolge):")
    print("    python build_kapitel_index.py")
    print("    python build_woerterbuch.py")
    print("    python build_sitemap.py")


if __name__ == "__main__":
    main()
