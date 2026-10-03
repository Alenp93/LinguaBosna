#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lb_testlib.py — gemeinsame Bausteine für die LinguaBosna-Prüf- und Build-Skripte.

Dies ist KEIN eigenständiges Skript, sondern eine Sammelstelle. Aufgerufen wird
sie nicht direkt, sondern importiert von:

    test_grammatikseite.py   test_lernen_uebung.py   test_seo.py
    test_usability.py        test_vokabeln.py        build_sitemap.py

WARUM DIESE DATEI?
------------------
Bis September 2026 hatte jedes dieser Skripte seine eigene Kopie derselben fünf
Bausteine: Repo-Root suchen, ✓/✗/⚠ ausgeben, HTML-Dateien einsammeln, einen
lokalen Server starten, horizontalen Überlauf messen. Vier Kopien bedeuten vier
Stellen, an denen ein Fix vergessen werden kann — und genau das ist passiert:

    build_sitemap.py hat gefiltert, dass unter .claude/worktrees/ eine komplette
    zweite Arbeitskopie des Repos liegen kann (git worktree), und schrieb sonst
    ~50 Phantom-URLs in die Sitemap. test_usability.py hat den Filter ebenfalls
    bekommen. test_seo.py NICHT — es prüfte deshalb 172 statt 86 Seiten, jede
    Seite doppelt, die zweite Hälfte aus einem veralteten Klon.

Der Filter steht jetzt genau einmal, in html_dateien(). Wer ihn ändert, ändert
ihn für alle Skripte gleichzeitig.

KONVENTION FÜR DIE ERGEBNIS-SAMMLUNG
------------------------------------
`errors` und `warnings` sind Modul-Listen, die von fail()/warn() gefüllt werden.
Die Skripte importieren sie per Namen und lesen sie am Ende aus:

    from lb_testlib import ok, fail, warn, errors, warnings
    ...
    sys.exit(1 if errors else 0)

Wichtig: Diese Listen dürfen im aufrufenden Skript nie neu zugewiesen werden
(`errors = []`), sonst zeigt der lokale Name auf eine andere Liste als die, in
die fail() schreibt. Leeren geht mit errors.clear().
"""

import os
import sys
import time
import socket
import pathlib
import subprocess
import contextlib
import urllib.request

# ── Ausgabe ──────────────────────────────────────────────────────────

# Windows-Konsolen nutzen oft cp1252. Das scheitert an ✓/✗/⚠/═ mit einem
# UnicodeEncodeError — und zwar oft erst beim ABSCHLIESSENDEN print(), wenn
# die eigentliche Arbeit längst erledigt ist. Sieht dann nach Fehlschlag aus,
# obwohl z. B. die sitemap.xml korrekt geschrieben wurde.
def utf8_ausgabe():
    """Erzwingt UTF-8 auf stdout/stderr (nur nötig unter Windows)."""
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")


errors = []    # harte Fehler → Exit-Code 1
warnings = []  # Hinweise → nur Ausgabe, kein Fehlschlag


def ok(msg):
    print(f"  ✓ {msg}")


def fail(msg):
    errors.append(msg)
    print(f"  ✗ FEHLER: {msg}")


def warn(msg):
    warnings.append(msg)
    print(f"  ⚠ Hinweis: {msg}")


def ergebnis(kopfzeile=True, hinweise_sind_ok=True):
    """
    Druckt den Ergebnisblock und gibt den Exit-Code zurück (0 = bestanden).

    hinweise_sind_ok=True bedeutet: ⚠-Hinweise lassen den Test bestehen.
    So verhalten sich alle bisherigen Skripte — Hinweise sind zum Draufschauen,
    nicht zum Blockieren.
    """
    if kopfzeile:
        print("\n══ Ergebnis ═══════════════════════════════════════════════")
    if errors:
        print(f"✗ {len(errors)} Fehler:")
        for e in errors:
            print(f"   – {e}")
        if warnings:
            print(f"  (dazu {len(warnings)} Hinweis(e))")
        return 1
    if warnings and not hinweise_sind_ok:
        return 1
    if warnings:
        print(f"✓ Keine Fehler ({len(warnings)} Hinweis(e)).")
    else:
        print("✓ Alle Prüfungen bestanden.")
    return 0


# ── Repo-Root ────────────────────────────────────────────────────────

def find_repo_root(start, max_levels=6):
    """
    Sucht ausgehend von `start` aufwärts nach dem Repo-Root, erkennbar am
    Ordner Code/Style.css. Funktioniert unabhängig davon, in welchem
    Unterordner des Repos das aufrufende Skript liegt oder von wo aus es
    gestartet wird.
    """
    current = pathlib.Path(start).resolve()
    for _ in range(max_levels):
        if (current / "Code" / "Style.css").exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    return None


def repo_root(pflicht=True):
    """
    Repo-Root ermitteln: zuerst vom Speicherort dieser Datei aus, dann vom
    aktuellen Arbeitsverzeichnis (falls ein Skript kopiert/verschoben wurde).

    pflicht=True beendet das Programm mit einer verständlichen Meldung, wenn
    kein Root gefunden wird; pflicht=False gibt None zurück.
    """
    root = (find_repo_root(pathlib.Path(__file__).resolve().parent)
            or find_repo_root(pathlib.Path.cwd()))
    if root is None and pflicht:
        print("✗ Repo-Root nicht gefunden (kein Code/Style.css). "
              "Skript innerhalb des LinguaBosna-Repos ausführen.")
        sys.exit(1)
    return root


# ── HTML-Dateien einsammeln ──────────────────────────────────────────

# Fragmente und Vorlagen, die keine eigenständigen Seiten sind: Header und
# Footer werden per JS eingebunden (haben zwar <head><title>Document</title>,
# sind aber keine Seite), die Grammatik-Vorlage ist Boilerplate mit
# [ECKIGEN KLAMMERN].
SKIP_NAMES = {
    "LB_header.html",
    "LB_footer.html",
    "TEMPLATE_Grammatik_Detailseite.html",
}


def html_dateien(root, als_relativ=False):
    """
    Alle *.html des Projekts, sortiert — die eine Wahrheit darüber, welche
    Dateien zur Webseite gehören.

    Übersprungen wird JEDES Verzeichnis, dessen Name mit einem Punkt beginnt,
    nicht nur .git. Grund: Unter .claude/worktrees/<name>/ kann eine
    vollständige zweite Arbeitskopie des Repos liegen (git worktree). Ohne
    diesen Filter taucht jede Seite doppelt auf — einmal echt, einmal aus dem
    Klon, dessen Stand beliebig alt sein kann.

    Das Filtern geschieht über die dirs-Liste von os.walk: Wer sie an Ort und
    Stelle kürzt (dirs[:] = ...), verhindert, dass os.walk dort überhaupt
    absteigt. Ein nachträgliches Aussortieren der Treffer wäre langsamer und
    würde bei 28 MB Worktree spürbar bremsen.

    Ebenso übersprungen wird alles, was laut .gitignore NICHT zum Repo gehört
    (siehe git_ignoriert() unten). Grund: Der Ordner Instagram-Vorlagen/ ist
    per `[Ii]nstagram*` ausgeschlossen, enthält aber *.dc.html-Vorlagen. Ohne
    diesen Filter schrieb build_sitemap.py sieben URLs dorthin in die Sitemap
    — auf GitHub Pages wären das 404-Seiten gewesen, die obendrein einen
    privaten Ordner verraten. Was nicht committet wird, wird nie veröffentlicht,
    gehört also auch nicht in Sitemap, SEO- oder Usability-Prüfung.

    SKIP_NAMES wird hier NICHT angewendet — die Aufrufer entscheiden selbst,
    ob sie Fragmente überspringen (test_seo.py meldet sie als "übersprungen",
    build_sitemap.py lässt sie stillschweigend weg).

    als_relativ=True liefert POSIX-Strings relativ zum Root (für build_sitemap),
    sonst absolute pathlib.Path-Objekte (für die Testskripte).
    """
    root = pathlib.Path(root)
    ignoriert = git_ignoriert(root)
    out = []
    for dp, dirs, fns in os.walk(root):
        # Relativer POSIX-Pfad des aktuellen Ordners mit "/" am Ende ("" für
        # den Root selbst), damit er sich mit der git-Ausgabe vergleichen lässt.
        rel_dp = pathlib.Path(dp).relative_to(root).as_posix()
        praefix = "" if rel_dp == "." else rel_dp + "/"
        dirs[:] = [d for d in dirs
                   if not d.startswith(".")
                   and praefix + d + "/" not in ignoriert]
        for fn in fns:
            if fn.endswith(".html") and praefix + fn not in ignoriert:
                voll = pathlib.Path(dp) / fn
                if als_relativ:
                    out.append(voll.relative_to(root).as_posix())
                else:
                    out.append(voll)
    return sorted(out)


def git_ignoriert(root):
    """
    Menge aller git-ignorierten Pfade unter root, relativ und in POSIX-Form.
    Ordner stehen mit abschließendem "/" darin ("Instagram-Vorlagen/"),
    Dateien ohne.

    Warum git fragen statt .gitignore selbst lesen? Die Muster-Syntax
    (Wildcards, Negation mit "!", verschachtelte .gitignore-Dateien,
    .git/info/exclude) korrekt nachzubauen wäre fehleranfällig. git kennt
    seine eigenen Regeln am besten — ein einziger Aufruf genügt:

        git ls-files --others --ignored --exclude-standard --directory -z

    --directory meldet einen komplett ignorierten Ordner als EINE Zeile statt
    jede Datei darin einzeln (wichtig für .claude/worktrees/ mit ~28 MB);
    -z trennt mit Nullbytes, damit git Umlaute/Leerzeichen nicht in
    Anführungszeichen setzt.

    Fallback: Ist git nicht installiert oder root kein Repo, kommt eine leere
    Menge zurück. Dann greift nur noch der Punkt-Ordner-Filter — also genau
    das Verhalten von vor dieser Erweiterung, kein Abbruch.
    """
    try:
        res = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--others", "--ignored",
             "--exclude-standard", "--directory", "-z"],
            capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return set()
    if res.returncode != 0:
        return set()
    return {p for p in res.stdout.decode("utf-8", "replace").split("\0") if p}


def ist_eigene_seite(doc, name):
    """
    True, wenn das HTML eine eigenständige Seite ist (kein Fragment, keine
    Vorlage). Dieselbe Regel in test_seo.py, test_usability.py und
    build_sitemap.py — deshalb hier gebündelt.
    """
    return (name not in SKIP_NAMES
            and "<head>" in doc
            and "<title>" in doc)


# ── Lokaler Testserver ───────────────────────────────────────────────

def freier_port():
    """Vom Betriebssystem einen freien Port zuteilen lassen."""
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class LocalServer:
    """
    Lokaler HTTP-Server auf dem Repo-Root, als Kontextmanager.

    Nötig, weil das Projekt durchgehend ABSOLUTE Pfade benutzt
    (/Code/LB_header.html, /Code/4_Lernen/luckentext_data.json). Über file://
    scheitert jeder fetch() — Header, Footer und alle JSON-Daten fehlen dann,
    und ein Mobiltest sähe nur leere Container.

        with LocalServer(root) as server:
            page.goto(server.url_for("index.html"))

    Wo ein `with`-Block nicht passt (etwa weil der Server einen bereits
    bestehenden try/finally-Block überspannen soll), geht auch:

        server = LocalServer(root).start()
        try:
            ...
        finally:
            server.stop()
    """

    def __init__(self, root):
        self.root = pathlib.Path(root)
        self.port = freier_port()
        self.proc = None

    def start(self):
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(self.port)],
            cwd=str(self.root),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        url = f"http://127.0.0.1:{self.port}/"
        # Bis zu 5 Sekunden warten, bis der Server antwortet
        for _ in range(50):
            try:
                urllib.request.urlopen(url, timeout=0.5)
                break
            except Exception:
                time.sleep(0.1)
        else:
            raise RuntimeError("Lokaler Testserver ist nicht hochgekommen.")
        return self

    def stop(self):
        if self.proc:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            self.proc = None

    def __enter__(self):
        return self.start()

    def __exit__(self, *exc):
        self.stop()

    def url_for(self, rel_path):
        return f"http://127.0.0.1:{self.port}/{rel_path}"


# ── Mobiltest ────────────────────────────────────────────────────────

VIEWPORTS = [900, 628, 480, 360, 320]
MIN_TOUCH = 44  # px, Mindest-Tap-Target laut Usability-Checkliste (CLAUDE.md)


def overflow_js(scope="body"):
    """
    Liefert die JS-Funktion, die horizontalen Überlauf misst und die
    Verursacher benennt.

    Vorgehen: Erst prüfen, ob scrollWidth > innerWidth. Wenn ja, jedes Element
    im `scope` kurz auf display:none setzen und schauen, ob die Seite dadurch
    schmaler wird. Elemente, bei denen das passiert, sind die Verursacher.
    Sortiert wird nach Tiefe (das innerste Element ist die eigentliche
    Ursache, nicht dessen Container) und danach nach Wirkung.

    scope="main"  → nur der Inhaltsbereich (Grammatik-/Lernen-Seiten, deren
                    Header/Footer identisch und separat geprüft sind)
    scope="body"  → die ganze Seite (test_usability.py prüft Header/Footer mit)
    """
    return """() => {
    const ov = document.documentElement.scrollWidth - window.innerWidth;
    let culprits = [];
    if (ov > 0) {
        const base = document.documentElement.scrollWidth;
        const cand = [];
        document.querySelectorAll('SCOPE *').forEach(e => {
            const prev = e.style.display;
            e.style.display = 'none';
            const drop = base - document.documentElement.scrollWidth;
            e.style.display = prev;
            if (drop > 0) {
                let depth = 0, p = e;
                while (p) { depth++; p = p.parentElement; }
                cand.push({
                    depth, drop, tag: e.tagName,
                    cls: (typeof e.className === 'string' ? e.className : ''),
                    text: (e.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 40)
                });
            }
        });
        cand.sort((a, b) => (b.depth - a.depth) || (b.drop - a.drop));
        culprits = cand.slice(0, 3);
    }
    return { ov: Math.round(ov), culprits };
}""".replace("SCOPE", scope)


def melde_overflow(res, label, width, melder=None):
    """
    Wertet das Ergebnis von overflow_js() aus und meldet es.

    Horizontaler Überlauf ist projektweit ein HARTER Fehler — es gibt keinen
    bekannten legitimen Grund dafür (breite Tabellen scrollen im Wrapper,
    siehe CLAUDE.md „Mobile Overflow"). Gibt True zurück, wenn Überlauf
    vorlag.
    """
    melder = melder or fail
    if res["ov"] > 0:
        details = "; ".join(
            f"<{c['tag'].lower()}"
            + (f" class=\"{c['cls']}\"" if c['cls'] else "")
            + f"> „{c['text']}“ (−{c['drop']}px)"
            for c in res["culprits"]) or "kein Einzelverursacher ermittelbar"
        melder(f"{width}px{label}: {res['ov']}px horizontaler Überlauf → {details}")
        return True
    return False


def playwright_oder_fehler():
    """
    Importiert Playwright und gibt sync_playwright zurück, oder None mit einer
    verständlichen Fehlermeldung. Die Installationsanweisung steht auch in
    CLAUDE.md („Einmalige lokale Einrichtung").
    """
    try:
        from playwright.sync_api import sync_playwright
        return sync_playwright
    except ImportError:
        fail("Playwright nicht installiert "
             "(pip install playwright --break-system-packages && "
             "playwright install chromium)")
        return None
