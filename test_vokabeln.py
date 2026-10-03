#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_vokabeln.py — Regelprüfung für vokabeln_flat.json.

Aufruf (im Repo-Root):
    python test_vokabeln.py           # volle Prüfung
    python test_vokabeln.py --quiet   # nur Fehler und Hinweise, keine ✓-Zeilen

WARUM DIESES SKRIPT?
--------------------
vokabeln_flat.json ist die größte handgepflegte Datei des Projekts (rund 4.000
Einträge) und die mit den meisten ungeschriebenen Regeln. Die Build-Pipeline,
die sie früher erzeugt hat (build_a1.py … build_parid.py), liegt nicht mehr im
Repo — seit August 2026 wird die Datei direkt bearbeitet. Bis September 2026
stand in CLAUDE.md dazu: „Ein Validierungsskript dafür fehlt bisher."

Das war die einzige Stelle im Projekt, an der eine bindende Regel nur in Prosa
existierte. Wer ein Kapitel anlegt, muss sonst zwölf Regeln aus einer
574-Zeilen-Datei korrekt im Kopf haben. Dieses Skript prüft sie nach.

HARTE FEHLER (Exit 1) — technisch bindend, brechen eine konsumierende Seite
--------------------------------------------------------------------------
  [1] Pflichtfelder Niveau/Bosnisch/Deutsch vorhanden und nicht leer
  [2] Wortart-Konvention: GENAU EINES der Felder "Wortart (Genus)"
      (Substantive) oder "Wortart" (alle anderen) — nie beide, nie keines
  [3] Kapitel = genau ein Niveau. LB_2_Vokabeln.html gruppiert nach
      Niveau → Kapitel; ein gemischtes Kapitel erscheint in zwei Niveau-Tabs
      gleichzeitig, jeweils mit einer Teilzählung
  [4] Kapitelgröße ≤ 35 Einträge
  [5] Kapitelnummer ↔ Kapitelname eindeutig in beide Richtungen,
      kategorie == "Kapitel {Nummer}"
  [6] nur_woerterbuch-Einträge OHNE kategorie/Kapitel/Kapitelname — sonst
      baut LB_2_Vokabeln.html eine leere Geisterkarte
  [7] Aspektpaare: jede par_id genau zwei Einträge, davon genau ein
      "nesvršeni" und ein "svršeni", beide auf demselben Niveau.
      lernen-aspektpaare.html nimmt Bedeutung UND Niveau vom nesvršeni-
      Partner; ein Paar über zwei Niveaus landet im falschen Übungsset
  [8] Datei nach Kapitelnummer sortiert (die Kapitelreihenfolge innerhalb
      eines Niveaus ergibt sich aus dem ersten Auftreten in der JSON)

HINWEISE (⚠, kein Fehlschlag) — Ermessen oder Altbestand
--------------------------------------------------------
  [9]  Wortart-Monokultur in Kapiteln ab Nr. 98. Ältere Kapitel waren schon
       vor der Regel so geschnitten (CLAUDE.md: „Ausgenommen sind
       Altbestandskapitel") und werden deshalb nicht gemeldet
  [10] Progression: Grundwort auf höherem Niveau als das Kompositum.
       Legitime Ausnahmen sind dokumentiert (anderes Bedeutungsfeld wie
       `slava`/`krsna slava`, oder feste Formeln wie `vozačka dozvola`) —
       deshalb Hinweis, nicht Fehler
  [11] Gleiche bosnische Form mehrfach im Bestand. Echte Homonyme sind in
       Ordnung, solange das Deutsch-Feld sie unterscheidbar macht
       (`nana` = Oma / Minze) — deshalb Hinweis
  [12] par_id-Lücken in der Nummerierung (ap01 … apNNN)
  [13] nur_woerterbuch-Einträge stehen nicht geschlossen am Dateiende

NICHT geprüft: alles Sprachliche. Ob eine Form ijekavisch, bosnisch-standard
und im richtigen Register ist, entscheidet der `bosnisch-pruefer`-Subagent —
ein grüner Lauf hier heißt „strukturell sauber", nicht „sprachlich korrekt".
Genau wie test_grammatikseite.py bei den Grammatikseiten.

Exit-Code 0 = keine harten Fehler, 1 = mindestens einer.
"""

import re
import sys
import json
import collections

from lb_testlib import (utf8_ausgabe, repo_root, ok, fail, warn,
                        errors, warnings)

utf8_ausgabe()
REPO_ROOT = repo_root()
JSON_PFAD = REPO_ROOT / "Code" / "2_Vokabeln" / "vokabeln_flat.json"

MAX_KAPITELGROESSE = 35          # CLAUDE.md: „Kapitelgrößen-Regel (fix)"
NIVEAUS = ["A1", "A2", "B1", "B2", "C1", "C2"]
NIVEAU_RANG = {n: i for i, n in enumerate(NIVEAUS)}

# Die Wortart-Mischungsregel gilt seit dem Tiere-Block (September 2026).
# Kapitel davor waren teils schon als reine Substantiv-/Verbkapitel
# geschnitten und sollen nicht dauerhaft Hinweise erzeugen.
MISCHUNG_AB_KAPITEL = 98

# Erlaubte Werte im Feld "Wortart". Bewusst KEIN "Satz"/"Redewendung"/
# "Sprichwort"/"Nominalphrase" — alles Mehrteilige ist "Phrase".
WORTARTEN = {"Adjektiv", "Adverb", "Konjunktion", "Partikel", "Phrase",
             "Pronomen", "Präposition", "Verb", "Zahl"}
GENUS_MUSTER = re.compile(r"^Substantiv \((m|f|n)(, Pl\.)?\)$")

# Klitika und Präpositionen, die in Mehrwortlemmata stehen, ohne dass das
# Lemma ein Kompositum wäre. Ohne diese Liste meldet Prüfung [10] jedes
# reflexive Verb (`vratiti se` gegen `vratiti`) als Progressionsfehler.
FUELLWOERTER = {"se", "si", "li", "ne", "na", "za", "od", "do", "sa", "s",
                "po", "iz", "uz", "u", "o", "k", "bez", "pod", "nad", "pri",
                "kroz", "i", "a", "je", "su", "ali", "ovdje", "tamo"}


def wortart_von(e):
    """Grobe Wortart eines Eintrags ('Substantiv', 'Verb', …)."""
    if "Wortart (Genus)" in e:
        return "Substantiv"
    return e.get("Wortart", "")


def main():
    quiet = "--quiet" in sys.argv

    if not JSON_PFAD.exists():
        print(f"✗ Nicht gefunden: {JSON_PFAD}")
        return 1

    daten = json.loads(JSON_PFAD.read_text(encoding="utf-8"))
    kapitel_eintraege = [e for e in daten if not e.get("nur_woerterbuch")]
    nur_wb = [e for e in daten if e.get("nur_woerterbuch")]

    print(f"\n══ Prüfung: {JSON_PFAD.relative_to(REPO_ROOT).as_posix()} "
          f"═══════════════════\n")
    print(f"  {len(daten)} Einträge — {len(kapitel_eintraege)} in Kapiteln, "
          f"{len(nur_wb)} nur im Wörterbuch\n")

    def gut(msg):
        if not quiet:
            ok(msg)

    # ── [1] Pflichtfelder ────────────────────────────────────────────
    print("[1] Pflichtfelder")
    fehlend = []
    for i, e in enumerate(daten):
        for feld in ("Niveau", "Bosnisch", "Deutsch"):
            if not str(e.get(feld, "")).strip():
                fehlend.append(f"Eintrag #{i} ({e.get('Bosnisch', '?')}): "
                               f"{feld} fehlt/leer")
        if e.get("Niveau") not in NIVEAU_RANG:
            fehlend.append(f"Eintrag #{i} ({e.get('Bosnisch', '?')}): "
                           f"unbekanntes Niveau {e.get('Niveau')!r}")
    for m in fehlend[:15]:
        fail(m)
    if len(fehlend) > 15:
        fail(f"… und {len(fehlend) - 15} weitere Pflichtfeld-Verstöße")
    if not fehlend:
        gut(f"Alle {len(daten)} Einträge haben Niveau/Bosnisch/Deutsch")

    # ── [2] Wortart-Konvention ───────────────────────────────────────
    print("\n[2] Wortart-Konvention")
    verstoesse = []
    for e in daten:
        hat_genus = "Wortart (Genus)" in e
        hat_wortart = "Wortart" in e
        if hat_genus and hat_wortart:
            verstoesse.append(f"{e['Bosnisch']}: hat BEIDE Felder "
                              f"'Wortart' und 'Wortart (Genus)'")
        elif not hat_genus and not hat_wortart:
            verstoesse.append(f"{e['Bosnisch']}: hat KEINE Wortart-Angabe")
        elif hat_genus and not GENUS_MUSTER.match(e["Wortart (Genus)"]):
            verstoesse.append(f"{e['Bosnisch']}: 'Wortart (Genus)' = "
                              f"{e['Wortart (Genus)']!r} — erwartet "
                              f"'Substantiv (m|f|n)' ggf. mit ', Pl.'")
        elif hat_wortart and e["Wortart"] not in WORTARTEN:
            verstoesse.append(f"{e['Bosnisch']}: 'Wortart' = "
                              f"{e['Wortart']!r} — erlaubt: "
                              f"{', '.join(sorted(WORTARTEN))}")
    for m in verstoesse[:15]:
        fail(m)
    if len(verstoesse) > 15:
        fail(f"… und {len(verstoesse) - 15} weitere Wortart-Verstöße")
    if not verstoesse:
        gut("Substantive führen 'Wortart (Genus)', alle anderen 'Wortart'")

    # ── [3]–[5] Kapitel ──────────────────────────────────────────────
    print("\n[3] Kapitel: ein Kapitel = ein Niveau")
    nach_kapitel = collections.defaultdict(list)
    for e in kapitel_eintraege:
        nach_kapitel[e.get("Kapitel")].append(e)

    gemischt = {k: sorted(set(x["Niveau"] for x in v))
                for k, v in nach_kapitel.items()
                if len(set(x["Niveau"] for x in v)) > 1}
    for k, niv in gemischt.items():
        fail(f"Kapitel {k} „{nach_kapitel[k][0].get('Kapitelname')}“ mischt "
             f"{'/'.join(niv)} — erscheint dadurch in mehreren Niveau-Tabs")
    if not gemischt:
        gut(f"Alle {len(nach_kapitel)} Kapitel haben genau ein Niveau")

    print("\n[4] Kapitelgröße")
    zu_gross = {k: len(v) for k, v in nach_kapitel.items()
                if len(v) > MAX_KAPITELGROESSE}
    for k, n in sorted(zu_gross.items()):
        fail(f"Kapitel {k} „{nach_kapitel[k][0].get('Kapitelname')}“ hat "
             f"{n} Einträge (max. {MAX_KAPITELGROESSE}) — thematisch in "
             f"nummerierte Teile splitten")
    if not zu_gross:
        groesste = max((len(v) for v in nach_kapitel.values()), default=0)
        gut(f"Kein Kapitel über {MAX_KAPITELGROESSE} Einträgen "
            f"(größtes: {groesste})")

    print("\n[5] Kapitelnummer ↔ Kapitelname")
    nr2name = collections.defaultdict(set)
    name2nr = collections.defaultdict(set)
    kat_falsch = []
    for e in kapitel_eintraege:
        nr2name[e.get("Kapitel")].add(e.get("Kapitelname"))
        name2nr[e.get("Kapitelname")].add(e.get("Kapitel"))
        if e.get("kategorie") != f"Kapitel {e.get('Kapitel')}":
            kat_falsch.append(f"{e['Bosnisch']}: kategorie "
                              f"{e.get('kategorie')!r} passt nicht zu "
                              f"Kapitel {e.get('Kapitel')}")
    sauber = True
    for nr, namen in sorted(nr2name.items()):
        if len(namen) > 1:
            fail(f"Kapitel {nr} hat mehrere Namen: {sorted(namen)}")
            sauber = False
    for name, nrs in sorted(name2nr.items()):
        if len(nrs) > 1:
            fail(f"Kapitelname „{name}“ steht unter mehreren Nummern: "
                 f"{sorted(nrs)}")
            sauber = False
    for m in kat_falsch[:10]:
        fail(m)
        sauber = False
    if len(kat_falsch) > 10:
        fail(f"… und {len(kat_falsch) - 10} weitere kategorie-Abweichungen")
    if sauber:
        gut("Nummer und Name sind in beide Richtungen eindeutig, "
            "kategorie passt überall")

    # ── [6] nur_woerterbuch ──────────────────────────────────────────
    print("\n[6] nur_woerterbuch-Einträge")
    mit_kapitel = [e for e in nur_wb
                   if any(f in e for f in ("kategorie", "Kapitel",
                                           "Kapitelname"))]
    for e in mit_kapitel[:10]:
        fail(f"{e['Bosnisch']}: nur_woerterbuch, hat aber Kapitel-Felder — "
             f"erzeugt eine leere Geisterkarte in LB_2_Vokabeln.html")
    if len(mit_kapitel) > 10:
        fail(f"… und {len(mit_kapitel) - 10} weitere")
    if not mit_kapitel:
        gut(f"Alle {len(nur_wb)} nur_woerterbuch-Einträge sind kapitellos")

    # [13] Position am Dateiende (Hinweis)
    idx = [i for i, e in enumerate(daten) if e.get("nur_woerterbuch")]
    if idx and idx != list(range(len(daten) - len(idx), len(daten))):
        warn("nur_woerterbuch-Einträge stehen nicht geschlossen am "
             "Dateiende (CLAUDE.md: „stehen am Dateiende“)")
    elif idx:
        gut("Sie stehen geschlossen am Dateiende")

    # ── [7] Aspektpaare ──────────────────────────────────────────────
    print("\n[7] Aspektpaare (par_id)")
    paare = collections.defaultdict(list)
    for e in daten:
        if e.get("par_id"):
            paare[e["par_id"]].append(e)

    paar_fehler = False
    for pid in sorted(paare):
        v = paare[pid]
        if len(v) != 2:
            fail(f"{pid}: {len(v)} Einträge statt 2 "
                 f"({', '.join(x['Bosnisch'] for x in v)})")
            paar_fehler = True
            continue
        aspekte = sorted(str(x.get("aspekt")) for x in v)
        if aspekte != ["nesvršeni", "svršeni"]:
            fail(f"{pid} ({v[0]['Bosnisch']}/{v[1]['Bosnisch']}): Aspekte "
                 f"{aspekte} — erwartet genau ein nesvršeni + ein svršeni")
            paar_fehler = True
        niv = set(x["Niveau"] for x in v)
        if len(niv) > 1:
            fail(f"{pid} ({v[0]['Bosnisch']}/{v[1]['Bosnisch']}): Partner auf "
                 f"{'/'.join(sorted(niv))} — lernen-aspektpaare.html nimmt "
                 f"das Niveau vom nesvršeni-Partner, das Paar landet im "
                 f"falschen Übungsset")
            paar_fehler = True
    if not paar_fehler:
        gut(f"Alle {len(paare)} Paare: 2 Partner, ein Aspekt je Seite, "
            f"ein Niveau")

    # [12] Lückenlosigkeit (Hinweis)
    nummern = sorted(int(p[2:]) for p in paare if re.fullmatch(r"ap\d+", p))
    krumm = [p for p in paare if not re.fullmatch(r"ap\d+", p)]
    if krumm:
        warn(f"par_id ohne Muster ap<Zahl>: {sorted(krumm)[:5]}")
    if nummern:
        luecken = sorted(set(range(1, max(nummern) + 1)) - set(nummern))
        if luecken:
            warn(f"Lücken in der par_id-Nummerierung: "
                 f"{luecken[:20]}{' …' if len(luecken) > 20 else ''}")
        else:
            gut(f"ap01–ap{max(nummern)} lückenlos belegt")

    # ── [8] Sortierung ───────────────────────────────────────────────
    print("\n[8] Sortierung nach Kapitelnummer")
    nummern_folge = [e.get("Kapitel") for e in kapitel_eintraege]
    if nummern_folge != sorted(nummern_folge):
        erste = next(i for i in range(1, len(nummern_folge))
                     if nummern_folge[i] < nummern_folge[i - 1])
        fail(f"Datei ist nicht nach Kapitelnummer sortiert — erster Bruch bei "
             f"Eintrag #{erste} ({kapitel_eintraege[erste]['Bosnisch']}): "
             f"Kapitel {nummern_folge[erste]} nach "
             f"{nummern_folge[erste - 1]}")
    else:
        gut("Kapiteleinträge stehen aufsteigend nach Kapitelnummer")

    # ── [9] Wortart-Mischung (Hinweis) ───────────────────────────────
    print("\n[9] Wortart-Mischung je Kapitel (ab Kapitel "
          f"{MISCHUNG_AB_KAPITEL})")
    mono = []
    for k in sorted(x for x in nach_kapitel if isinstance(x, int)):
        if k < MISCHUNG_AB_KAPITEL:
            continue
        arten = set(wortart_von(e) for e in nach_kapitel[k])
        if len(arten) == 1:
            mono.append((k, nach_kapitel[k][0].get("Kapitelname"),
                         arten.pop(), len(nach_kapitel[k])))
    for k, name, art, n in mono:
        warn(f"Kapitel {k} „{name}“ besteht aus {n}× {art} — reine "
             f"Wortartkapitel lehren eine Liste, keinen benutzbaren Wortschatz")
    if not mono:
        gut("Keine Wortart-Monokultur in den neueren Kapiteln")

    # ── [10] Progression Grundwort/Kompositum (Hinweis) ──────────────
    print("\n[10] Progression: Grundwort nicht über dem Kompositum")
    einwort = {}
    for e in daten:
        w = e["Bosnisch"].strip()
        if " " not in w:
            einwort.setdefault(w.lower(), NIVEAU_RANG[e["Niveau"]])
    inversionen = []
    for e in daten:
        teile = e["Bosnisch"].strip().split()
        if len(teile) < 2:
            continue
        rang = NIVEAU_RANG[e["Niveau"]]
        for t in teile:
            t = t.lower().strip(".,!?„“\"")
            if len(t) < 3 or t in FUELLWOERTER:
                continue
            if t in einwort and einwort[t] > rang:
                inversionen.append(
                    (e["Bosnisch"], e["Niveau"], t, NIVEAUS[einwort[t]]))
    if inversionen:
        warn(f"{len(inversionen)} Mehrwortlemma(ta) stehen unter dem Niveau "
             f"ihres Bausteins. Legitim, wenn das Grundwort eine ANDERE "
             f"Bedeutung trägt oder das Lemma eine feste Formel ist "
             f"(siehe CLAUDE.md) — sonst prüfen:")
        for lemma, niv, teil, teil_niv in inversionen[:20]:
            print(f"      → „{lemma}“ ({niv}) enthält „{teil}“ ({teil_niv})")
        if len(inversionen) > 20:
            print(f"      … und {len(inversionen) - 20} weitere")
    else:
        gut("Kein Baustein steht über seinem Mehrwortlemma")

    # ── [11] Doppelte bosnische Formen (Hinweis) ─────────────────────
    print("\n[11] Mehrfach vergebene bosnische Formen")
    nach_form = collections.defaultdict(list)
    for e in daten:
        nach_form[e["Bosnisch"]].append(e)
    doppelt = {k: v for k, v in nach_form.items() if len(v) > 1}
    exakt = [k for k, v in doppelt.items()
             if len(set(x["Deutsch"] for x in v)) == 1]
    for k in exakt:
        fail(f"„{k}“ steht {len(doppelt[k])}× mit identischer Übersetzung "
             f"„{doppelt[k][0]['Deutsch']}“ — echte Dublette")
    homonyme = {k: v for k, v in doppelt.items() if k not in exakt}
    if homonyme:
        warn(f"{len(homonyme)} Form(en) mehrfach mit verschiedener Bedeutung "
             f"— als Homonym in Ordnung, wenn das Deutsch-Feld sie "
             f"unterscheidbar macht:")
        for k, v in sorted(homonyme.items()):
            paare_txt = " / ".join(f"„{x['Deutsch']}“ ({x['Niveau']})"
                                   for x in v)
            print(f"      → {k}: {paare_txt}")
    if not doppelt:
        gut("Jede bosnische Form kommt genau einmal vor")

    # ── Ergebnis ─────────────────────────────────────────────────────
    print("\n══ Ergebnis ═══════════════════════════════════════════════")
    if errors:
        print(f"✗ {len(errors)} FEHLER:")
        for e in errors:
            print(f"   – {e}")
        if warnings:
            print(f"  (dazu {len(warnings)} Hinweis(e))")
        print("\n  Nach der Korrektur nicht vergessen:")
        print("    python build_kapitel_index.py")
        print("    python build_woerterbuch.py")
        print("    python build_sitemap.py")
        return 1
    extra = f" ({len(warnings)} Hinweis(e) — bitte durchsehen)" if warnings else ""
    print(f"✓ Keine harten Fehler{extra}.")
    print("\n  Hinweis: geprüft ist die STRUKTUR, nicht die Sprache. "
          "Für ijekavische\n  Form, Register und Bosnisch-Standard bleibt der "
          "`bosnisch-pruefer`-Subagent\n  zuständig.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
