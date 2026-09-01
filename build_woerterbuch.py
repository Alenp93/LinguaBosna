#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_woerterbuch.py — erzeugt die statischen Buchstabenseiten des Wörterbuchs.

Aufruf (im Repo-Root):
    python3 build_woerterbuch.py          # schreibt alle Seiten neu
    python3 build_woerterbuch.py --check  # nur prüfen, ob sie aktuell sind
                                          # (Exit 1, wenn veraltet)

WARUM DIESES SKRIPT?
--------------------
/Code/2_Vokabeln/LB_2-2_Woerterbuch.html ist die komfortable Seite: suchen,
filtern, blättern. Für Google ist sie trotzdem fast wertlos — ihr <body> ist
leer, bis JavaScript die Einträge nachlädt, und die Adresse ?q=kuca entsteht
erst, wenn ein Mensch etwas eintippt. Ein Crawler tippt nicht in Suchfelder,
also gibt es keinen Link, dem er folgen könnte.

Dieses Skript erzeugt deshalb zusätzlich ~30 ganz normale HTML-Seiten — eine
je Buchstabe der bosnischen Abeceda — in denen alle Wörter fertig im Quelltext
stehen. Sie sind untereinander und über eine Übersichtsseite verlinkt und
dadurch für Suchmaschinen erreichbar.

Bewusst NICHT eine Seite pro Wort (2.895 Stück): Solche Massen an
Kleinstseiten wertet Google als "Thin Content" ab und sie würden die
wenigen guten Seiten der Domain mit verwässern.

WAS ENTSTEHT?
-------------
    Code/2_Vokabeln/woerterbuch/index.html            (Übersicht aller Buchstaben)
    Code/2_Vokabeln/woerterbuch/woerterbuch-a.html
    Code/2_Vokabeln/woerterbuch/woerterbuch-b.html
    …

Die Seiten benutzen dieselben CSS-Klassen wie die dynamische Seite
(.wb-liste / .wb-eintrag aus Style_2-2_Woerterbuch.css) — sie sehen deshalb
identisch aus und brauchen kein eigenes Stylesheet.

NACH JEDER ÄNDERUNG AN vokabeln_flat.json AUSFÜHREN und die erzeugten
Dateien mitcommitten — genau wie build_kapitel_index.py. Danach noch
build_sitemap.py laufen lassen, damit die neuen Adressen in die Sitemap
kommen.
"""

import html
import json
import pathlib
import shutil
import sys
import unicodedata

if sys.platform == "win32":  # UTF-8-Ausgabe wie in test_seo.py
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

DOMAIN = "https://linguabosna.com"

VOKABELN_REL = pathlib.Path("Code/2_Vokabeln/vokabeln_flat.json")
ZIEL_REL     = pathlib.Path("Code/2_Vokabeln/woerterbuch")

# Adressen der bestehenden Seiten (absolute Pfade, Projektprinzip)
SUCHSEITE   = "/Code/2_Vokabeln/LB_2-2_Woerterbuch.html"
MASTER_PATH = "/Code/2_Vokabeln/LB_2-1_Vokabeln_Master.html"
UEBERSICHT  = "/Code/2_Vokabeln/woerterbuch/index.html"

# Bosnische Abeceda. Dž, Lj und Nj sind eigenständige Buchstaben und stehen
# an ihrer eigenen Stelle — dieselbe Reihenfolge wie in LB_2-2_Woerterbuch.html.
ABECEDA = ["A", "B", "C", "Č", "Ć", "D", "Dž", "Đ", "E", "F", "G", "H", "I",
           "J", "K", "L", "Lj", "M", "N", "Nj", "O", "P", "R", "S", "Š", "T",
           "U", "V", "Z", "Ž"]

# Dateinamen müssen reines ASCII sein: Umlaut-Dateinamen im Repo sind unter
# Windows/Git/GitHub Pages erfahrungsgemäß eine Fehlerquelle (Prozent-
# Kodierung in der Sitemap, unterschiedliche Unicode-Normalisierung je
# Betriebssystem). Deshalb diese feste, eindeutige Zuordnung. Sie darf sich
# NICHT mehr ändern — sonst brechen bereits indexierte Adressen.
SLUGS = {
    "Č": "c-caron",    # c mit Hatschek
    "Ć": "c-akut",     # c mit Akut
    "Đ": "d-strich",   # d mit Querstrich
    "Š": "s-caron",
    "Ž": "z-caron",
    "Dž": "dz",
    "Lj": "lj",
    "Nj": "nj",
}

# Aspekt-Kürzel für Verben (gleiche Abkürzungen wie auf allen anderen Seiten)
ASPEKT_KUERZEL = {
    "svršeni":   "svrš.",
    "nesvršeni": "nesvrš.",
    "dvovidni":  "dvov.",
}


# ══════════════════════════════════════════════════════════════
#  Repo-Root finden (gleiche Logik wie in den anderen Skripten)
# ══════════════════════════════════════════════════════════════
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


# ══════════════════════════════════════════════════════════════
#  Hilfsfunktionen
# ══════════════════════════════════════════════════════════════
def buchstabe_von(wort):
    """Anfangsbuchstabe mit Rücksicht auf die Digraphen.

    "džemper" → "Dž", "ljeto" → "Lj", "kuća" → "K".
    Gleiche Regel wie buchstabeVon() in LB_2-2_Woerterbuch.html — beide
    müssen dieselbe Einteilung ergeben, sonst zeigen dynamische und
    statische Seite unterschiedliche Wörter unter demselben Buchstaben.
    """
    w = (wort or "").strip()
    if not w:
        return ""
    zwei = w[:1].upper() + w[1:2].lower()
    if zwei in ("Dž", "Lj", "Nj"):
        return zwei
    return w[:1].upper()


def slug_von(buchstabe):
    """Dateiname-Baustein für einen Buchstaben ("Č" → "c-caron")."""
    if buchstabe in SLUGS:
        return SLUGS[buchstabe]
    return buchstabe.lower()


def datei_von(buchstabe):
    return f"woerterbuch-{slug_von(buchstabe)}.html"


def url_von(buchstabe):
    return f"/Code/2_Vokabeln/woerterbuch/{datei_von(buchstabe)}"


def sortier_schluessel(wort):
    """Alphabetische Sortierung für bosnische Wörter.

    Python kennt keine bosnische Kollation ohne Zusatzbibliothek. Deshalb
    wird hier von Hand einsortiert: Jeder Buchstabe bekommt seine Position
    in der Abeceda, Sonderzeichen landen dadurch an der richtigen Stelle
    (č nach c, š nach s …) statt hinter z, wo ein roher Unicode-Vergleich
    sie ablegen würde. Die dynamische Seite nutzt dafür Intl.Collator('bs'),
    das im Browser eingebaut ist.
    """
    # Reihenfolge der Einzelzeichen (Digraphen werden unten zerlegt)
    einzel = "abcčćdđefghijklmnoprsštuvzž"
    rang = {ch: i for i, ch in enumerate(einzel)}

    schluessel = []
    for ch in (wort or "").lower():
        if ch in rang:
            schluessel.append(rang[ch])
        elif ch.isspace() or ch == "-":
            schluessel.append(-1)          # Leerzeichen vor allen Buchstaben
        else:
            # Alles Übrige (Ziffern, w, x, y …) hinten anstellen, aber
            # untereinander stabil nach Codepoint.
            schluessel.append(100 + ord(ch))
    return (schluessel, wort or "")


def wortart_von(e):
    """JSON kennt zwei Feldnamen: "Wortart (Genus)" und "Wortart"."""
    return e.get("Wortart (Genus)") or e.get("Wortart") or ""


def genus_zusatz(e):
    """Aus "Substantiv (f)" wird "(f)"; bei anderen Wortarten leer."""
    wa = wortart_von(e)
    if not wa.startswith("Substantiv"):
        return ""
    if "(" in wa and ")" in wa:
        return "(" + wa[wa.index("(") + 1:wa.rindex(")")] + ")"
    return ""


def wort_anker(wort):
    """Leerzeichen → Bindestrich. Gleiche Regel wie LBSuche.wortAnker()."""
    return "-".join((wort or "").strip().split())


def esc(text):
    """HTML-Sonderzeichen entschärfen."""
    return html.escape(str(text or ""), quote=True)


def zahl(n):
    """1234 → "1.234" (deutsches Tausendertrennzeichen)."""
    return f"{n:,}".replace(",", ".")


# ══════════════════════════════════════════════════════════════
#  Bausteine der Seiten
# ══════════════════════════════════════════════════════════════
def kopf(titel, beschreibung, kanonisch, breadcrumb_name):
    """Der komplette <head> plus <body>-Anfang.

    Bewusst identisch aufgebaut wie bei den handgeschriebenen Seiten
    (Fonts, FontAwesome, Favicon-Block, Open Graph, Twitter Card, JSON-LD),
    damit test_seo.py auch hier durchläuft.
    """
    t, b = esc(titel), esc(beschreibung)
    jsonld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "LearningResource",
                "name": titel.replace("LinguaBosna – ", ""),
                "description": beschreibung,
                "url": kanonisch,
                "inLanguage": "de",
                "learningResourceType": "Wörterbuch",
                "teaches": "Bosnischer Wortschatz",
                "isAccessibleForFree": True,
                "isPartOf": {
                    "@type": "Course",
                    "name": "Bosnisch lernen",
                    "url": DOMAIN + "/",
                },
                "provider": {
                    "@type": "EducationalOrganization",
                    "name": "LinguaBosna",
                    "url": DOMAIN + "/",
                },
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Start",
                     "item": DOMAIN + "/"},
                    {"@type": "ListItem", "position": 2, "name": "Wörterbuch",
                     "item": DOMAIN + SUCHSEITE},
                    {"@type": "ListItem", "position": 3, "name": breadcrumb_name},
                ],
            },
        ],
    }

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{b}">
  <title>{t}</title>
  <link rel="canonical" href="{kanonisch}">

  <!-- ── Open Graph (Vorschau beim Teilen) ──────────────────────── -->
  <meta property="og:type"        content="website">
  <meta property="og:title"       content="{t}">
  <meta property="og:description" content="{b}">
  <meta property="og:url"         content="{kanonisch}">
  <meta property="og:image"       content="{DOMAIN}/Bilder/logo/Logo-Version2.png">
  <meta property="og:site_name"   content="LinguaBosna">
  <meta property="og:locale"      content="de_DE">

  <!-- ── Twitter Card ───────────────────────────────────────────── -->
  <meta name="twitter:card"        content="summary_large_image">
  <meta name="twitter:title"       content="{t}">
  <meta name="twitter:description" content="{b}">
  <meta name="twitter:image"       content="{DOMAIN}/Bilder/logo/Logo-Version2.png">

  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">

  <!-- FontAwesome -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">

  <!-- ── Favicon (LinguaBosna-Logo) ───────────────────────────── -->
  <link rel="icon" type="image/png" href="/Bilder/favicon/favicon-96x96.png" sizes="96x96" />
  <link rel="icon" type="image/svg+xml" href="/Bilder/favicon/favicon.svg" />
  <link rel="shortcut icon" href="/Bilder/favicon/favicon.ico" />
  <link rel="apple-touch-icon" sizes="180x180" href="/Bilder/favicon/apple-touch-icon.png" />
  <meta name="apple-mobile-web-app-title" content="LinguaBosna" />
  <link rel="manifest" href="/Bilder/favicon/site.webmanifest" />

  <!-- Stylesheets — dieselben wie auf der dynamischen Wörterbuch-Seite,
       deshalb sehen die Einträge hier genauso aus. -->
  <link rel="stylesheet" href="/Code/Style.css">
  <link rel="stylesheet" href="/Code/2_Vokabeln/Style_2-2_Woerterbuch.css">

  <!-- Shared Header/Footer JS -->
  <script src="/Code/LB_main.js" defer></script>

  <!-- ── Strukturierte Daten (schema.org) ─────────────────── -->
  <script type="application/ld+json">
{json.dumps(jsonld, ensure_ascii=False, indent=2)}
  </script>
</head>
<body>

  <!-- Header (dynamisch eingebunden per LB_main.js) -->
  <div id="header"></div>

  <main>
"""


FUSS = """
  </main>

  <!-- Footer (dynamisch eingebunden per LB_main.js) -->
  <div id="footer"></div>

</body>
</html>
"""


def abc_leiste(vorhandene, aktiv=None):
    """Die A–Ž-Leiste als echte Links.

    Das ist der Kern der ganzen Übung: Erst diese Links machen die
    Buchstabenseiten für einen Crawler erreichbar. Auf der dynamischen
    Seite sind die entsprechenden Elemente <button>s ohne Ziel.
    """
    teile = [
        '    <nav class="wb-abc" aria-label="Alphabetisch blättern">',
        f'      <a class="wb-abc-btn" href="{UEBERSICHT}">Alle</a>',
    ]
    for b in vorhandene:
        if b == aktiv:
            # Der aktuelle Buchstabe wird nicht auf sich selbst verlinkt.
            teile.append(
                f'      <span class="wb-abc-btn active" aria-current="page">{esc(b)}</span>')
        else:
            teile.append(
                f'      <a class="wb-abc-btn" href="{url_von(b)}" '
                f'aria-label="Wörter mit {esc(b)}">{esc(b)}</a>')
    teile.append("    </nav>")
    return "\n".join(teile)


def eintrag_html(e):
    """Eine Wort-Karte — gleiche Struktur wie karteHtml() im JS."""
    bs      = esc(e.get("Bosnisch", ""))
    de      = esc(e.get("Deutsch", ""))
    genus   = genus_zusatz(e)
    wa      = wortart_von(e)
    niveau  = esc(e.get("Niveau", ""))
    kuerzel = ASPEKT_KUERZEL.get(e.get("aspekt", ""))

    kopf_html = (
        '<div class="wb-kopf">'
        f'<span class="wb-bs" lang="bs">{bs}'
        + (f' <span class="wb-genus">{esc(genus)}</span>' if genus else "")
        + "</span>"
        + (f'<span class="wb-niveau">{niveau}</span>' if niveau else "")
        + "</div>"
        f'<div class="wb-de">{de}</div>'
    )

    if wa or kuerzel:
        kopf_html += (
            '<div class="wb-meta">'
            + (f"<span>{esc(wa)}</span>" if wa else "")
            + (f'<span class="wb-aspekt">[{esc(kuerzel)}]</span>' if kuerzel else "")
            + "</div>"
        )

    kapitel = e.get("Kapitel")
    if kapitel:
        kopf_html += (
            '<div class="wb-fuss">'
            '<i class="fa-solid fa-book-open" aria-hidden="true"></i>'
            f'Kapitel {kapitel}: {esc(e.get("Kapitelname", ""))}'
            "</div>"
        )
        ziel = (f'{MASTER_PATH}?kapitel={kapitel}'
                f'#{wort_anker(e.get("Bosnisch", ""))}')
        return (f'      <li><a class="wb-eintrag" href="{esc(ziel)}">'
                f"{kopf_html}</a></li>")

    kopf_html += (
        '<div class="wb-fuss">'
        '<i class="fa-solid fa-circle-info" aria-hidden="true"></i>'
        "Nur im Wörterbuch – zu keinem Kapitel"
        "</div>"
    )
    return (f'      <li><div class="wb-eintrag wb-eintrag-static">'
            f"{kopf_html}</div></li>")


# ══════════════════════════════════════════════════════════════
#  Die einzelnen Seiten bauen
# ══════════════════════════════════════════════════════════════
def buchstabenseite(buchstabe, eintraege, vorhandene):
    """Eine komplette Buchstabenseite als HTML-String."""
    n     = len(eintraege)
    pos   = vorhandene.index(buchstabe)
    vor   = vorhandene[pos - 1] if pos > 0 else None
    nach  = vorhandene[pos + 1] if pos < len(vorhandene) - 1 else None

    titel = f"Bosnische Wörter mit {buchstabe} – Wörterbuch Bosnisch-Deutsch"

    # Ein paar Beispielwörter in die Description — dadurch steht in der
    # Google-Vorschau etwas Konkretes statt nur einer Zahl. Wie viele
    # hineinpassen, hängt von ihrer Länge ab: Google schneidet Snippets
    # bei rund 160 Zeichen ab, und test_seo.py mahnt alles über 170 an.
    # Deshalb von drei Beispielen abwärts probieren, bis es passt.
    def beschreibung_bauen(anzahl_beispiele):
        rumpf = (f"Alle {n} bosnischen Wörter mit {buchstabe} und ihre deutsche "
                 f"Übersetzung – mit Wortart, Genus und Sprachniveau A1 bis C2.")
        if anzahl_beispiele <= 0:
            return rumpf
        beispiele = ", ".join(e["Bosnisch"] for e in eintraege[:anzahl_beispiele])
        return f"{rumpf} Zum Beispiel: {beispiele}."

    for anzahl in (3, 2, 1, 0):
        beschreibung = beschreibung_bauen(anzahl)
        if len(beschreibung) <= 165:
            break
    kanonisch = DOMAIN + url_von(buchstabe)

    teile = [kopf(titel, beschreibung, kanonisch, f"Wörter mit {buchstabe}")]

    teile.append(f"""    <div class="section-intro">
      <h1>Bosnische Wörter mit {esc(buchstabe)}</h1>
      <p>{zahl(n)} {'Wort' if n == 1 else 'Wörter'} mit deutscher Übersetzung,
         Wortart und Sprachniveau</p>
    </div>

    <!-- Weg zur komfortablen Variante: Diese Seite ist zum Blättern und
         Verlinken da, die Suchseite kann zusätzlich filtern und suchen. -->
    <p class="wb-hinweis-suche">
      <i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i>
      Lieber gezielt suchen oder nach Niveau filtern?
      <a href="{SUCHSEITE}?buchstabe={esc(buchstabe)}">Zur Wörterbuch-Suche</a>
    </p>

{abc_leiste(vorhandene, aktiv=buchstabe)}

    <ul class="wb-liste">""")

    teile.extend(eintrag_html(e) for e in eintraege)
    teile.append("    </ul>")

    # Vorheriger / nächster Buchstabe
    nav = ['\n    <nav class="wb-blaettern" aria-label="Buchstaben-Navigation">']
    if vor:
        nav.append(f'      <a class="btn btn-outline" href="{url_von(vor)}">'
                   f'<i class="fa-solid fa-arrow-left" aria-hidden="true"></i>'
                   f" Wörter mit {esc(vor)}</a>")
    if nach:
        nav.append(f'      <a class="btn btn-outline" href="{url_von(nach)}">'
                   f"Wörter mit {esc(nach)} "
                   f'<i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a>')
    nav.append("    </nav>")
    teile.append("\n".join(nav))

    # Zurück zum Seitenanfang. Der Buchstabe P bringt es auf 430 Einträge und
    # damit auf rund 66.000 Pixel Seitenhöhe – wer unten ankommt, soll nicht
    # den ganzen Weg zurückwischen müssen, um die Alphabet-Leiste zu erreichen.
    teile.append("""
    <p class="wb-nach-oben">
      <a href="#main-content">
        <i class="fa-solid fa-arrow-up" aria-hidden="true"></i>
        Nach oben zur Buchstabenauswahl
      </a>
    </p>""")

    teile.append(FUSS)
    return "\n".join(teile)


def uebersichtsseite(gruppen, vorhandene, gesamt):
    """Die Hub-Seite: verlinkt alle Buchstabenseiten mit Anzahl."""
    titel = "Wörterbuch von A bis Ž – alle bosnischen Wörter"
    beschreibung = (
        f"Alle {zahl(gesamt)} Wörter des LinguaBosna-Wörterbuchs, nach "
        f"bosnischem Alphabet sortiert – von A bis Ž, mit deutscher "
        f"Übersetzung, Wortart und Sprachniveau A1 bis C2."
    )
    kanonisch = DOMAIN + UEBERSICHT

    teile = [kopf(titel, beschreibung, kanonisch, "Von A bis Ž")]

    teile.append(f"""    <div class="section-intro">
      <h1>Wörterbuch von A bis Ž</h1>
      <p>{zahl(gesamt)} bosnische Wörter mit deutscher Übersetzung,
         nach Anfangsbuchstaben sortiert</p>
    </div>

    <p class="wb-hinweis-suche">
      <i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i>
      Du weißt schon, welches Wort du suchst?
      <a href="{SUCHSEITE}">Zur Wörterbuch-Suche</a>
    </p>

    <p class="wb-abc-hinweis">
      Nach bosnischer Alphabetordnung sind <strong>Dž</strong>,
      <strong>Lj</strong> und <strong>Nj</strong> eigene Buchstaben –
      <em lang="bs">ljeto</em> steht also unter „Lj“, nicht unter „L“.
    </p>

    <ul class="wb-buchstaben-grid">""")

    for b in vorhandene:
        n = len(gruppen[b])
        teile.append(
            f'      <li><a class="wb-buchstabe-karte" href="{url_von(b)}">'
            f'<span class="wb-buchstabe-gross" lang="bs">{esc(b)}</span>'
            f'<span class="wb-buchstabe-anzahl">{zahl(n)} '
            f"{'Wort' if n == 1 else 'Wörter'}</span></a></li>")

    teile.append("    </ul>")
    teile.append(FUSS)
    return "\n".join(teile)


# ══════════════════════════════════════════════════════════════
#  Hauptprogramm
# ══════════════════════════════════════════════════════════════
def seiten_bauen():
    """Liefert {Dateiname: HTML-Inhalt} für alles, was erzeugt werden soll."""
    daten = json.loads((REPO_ROOT / VOKABELN_REL).read_text(encoding="utf-8"))

    # Nach Anfangsbuchstaben gruppieren
    gruppen = {}
    for e in daten:
        b = buchstabe_von(e.get("Bosnisch", ""))
        if not b:
            continue
        gruppen.setdefault(b, []).append(e)

    # Reihenfolge: erst die Abeceda, dann alles Übrige (im Bestand nur "W"
    # wegen "WC šolja") — so bleibt kein Wort unerreichbar.
    vorhandene = [b for b in ABECEDA if b in gruppen]
    vorhandene += sorted(b for b in gruppen if b not in ABECEDA)

    # Innerhalb eines Buchstabens alphabetisch sortieren
    for b in gruppen:
        gruppen[b].sort(key=lambda e: sortier_schluessel(e.get("Bosnisch", "")))

    seiten = {"index.html": uebersichtsseite(gruppen, vorhandene, len(daten))}
    for b in vorhandene:
        seiten[datei_von(b)] = buchstabenseite(b, gruppen[b], vorhandene)
    return seiten


def main():
    check_only = "--check" in sys.argv[1:]
    seiten = seiten_bauen()
    ziel   = REPO_ROOT / ZIEL_REL

    # Dateien, die es früher gab, deren Buchstabe aber leer geworden ist,
    # müssen weg — sonst bleiben tote Seiten in der Sitemap stehen.
    vorhanden_auf_platte = set()
    if ziel.exists():
        vorhanden_auf_platte = {p.name for p in ziel.glob("*.html")}
    veraltet = vorhanden_auf_platte - set(seiten)

    if check_only:
        aktuell = True
        for name, inhalt in seiten.items():
            pfad = ziel / name
            if not pfad.exists() or pfad.read_text(encoding="utf-8") != inhalt:
                aktuell = False
                break
        if aktuell and not veraltet:
            print(f"✓ Wörterbuch-Seiten sind aktuell ({len(seiten)} Dateien).")
            sys.exit(0)
        print("✗ Wörterbuch-Seiten sind VERALTET — bitte "
              "`python3 build_woerterbuch.py` ausführen und committen.")
        sys.exit(1)

    ziel.mkdir(parents=True, exist_ok=True)
    for name, inhalt in seiten.items():
        (ziel / name).write_text(inhalt, encoding="utf-8")
    for name in veraltet:
        (ziel / name).unlink()
        print(f"  – entfernt (kein Wort mehr mit diesem Buchstaben): {name}")

    woerter = sum(1 for _ in json.loads(
        (REPO_ROOT / VOKABELN_REL).read_text(encoding="utf-8")))
    print(f"✓ {len(seiten)} Seiten geschrieben in {ZIEL_REL.as_posix()}/ "
          f"({zahl(woerter)} Wörter)")
    print("  Nicht vergessen: python3 build_sitemap.py")


if __name__ == "__main__":
    main()
