#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_usability.py — seitentyp-unabhängige Usability-/A11y-Prüfung für LinguaBosna.

Ergänzt test_seo.py (SEO) und test_grammatikseite.py (Struktur einer
Grammatikseite): dieses Skript prüft messbare Usability-/Barrierefreiheits-
Grundwerte auf JEDER Seite — Startseite, Vokabeln, Lernen, Grammatik usw.
Es ersetzt keine dieser beiden Prüfungen, sondern kommt als dritte dazu.

Aufruf (im Repo-Root):
    python3 test_usability.py                      # alle Seiten (wie --all)
    python3 test_usability.py --all
    python3 test_usability.py index.html
    python3 test_usability.py Code/2_Vokabeln/LB_2_Vokabeln.html

Geprüft wird über einen selbst gestarteten lokalen Server (python -m
http.server auf einem freien Port), damit dynamisch nachgeladene Inhalte
(Header/Footer per fetch(), Vokabel-/Grammatik-Daten aus JSON) mitgeprüft
werden — nicht nur das statische HTML.

Pro Seite (Playwright, Chromium):
  1. HORIZONTALER ÜBERLAUF bei 900/628/480/360/320 px — HARTER FEHLER,
     genau wie in test_grammatikseite.py. Kein legitimer Grund dafür bekannt.
  2. KONTRAST (bei 360 px): sichtbarer Fließtext gegen seinen tatsächlichen
     Hintergrund, nach WCAG-Formel (4.5:1 normal, 3:1 ab 24px bzw. 18.66px+
     fett). Hinweis, kein harter Fehler — manche Fälle (z. B. bewusst
     dezente Sekundärtexte) sind Ermessenssache. Annäherung, keine exakte
     Messung: Text auf einem Foto (background-image statt background-color)
     oder auf einer stark transparenten Glasfläche darüber kann die Prüfung
     nicht zuverlässig auflösen (sie überspringt Hintergründe mit Alpha < 0.5
     und nimmt den nächsten deckenden Vorfahren) — solche Fälle im Zweifel
     manuell mit den Browser-DevTools nachprüfen.
  3. TAP-TARGETS (bei 360 px): interaktive Elemente (a/button/input/…)
     unter 44×44 px — CLAUDE.md schreibt „44px Mindest-Touch-Targets" fest
     vor. Hinweis, kein harter Fehler (Rundungen/Icon-Buttons mit groß-
     zügigem Padding sind ok).

Einmalig (nicht pro Seite):
  4. Fokusring: `outline: none`/`outline: 0` in den CSS-Dateien ohne
     erkennbaren Ersatz (`:focus-visible`-Regel in derselben Datei).
  5. Skip-Link („Zum Inhalt springen" o. ä.) in LB_header.html.
  6. `prefers-reduced-motion` — Hinweis, falls in keiner CSS-Datei vorhanden.

Alle Punkte außer (1) sind Hinweise (⚠), keine harten Fehler — das Skript ist
neu und soll sichtbar machen, nicht sofort jeden bestehenden Commit blockieren.
Alen entscheidet von Fall zu Fall, was davon behoben wird.

Exit-Code 0 = keine harten Fehler, 1 = mindestens ein Überlauf-Fehler.
"""

import re
import sys
import json
import socket
import subprocess
import time
import pathlib
import contextlib
import urllib.request

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

VIEWPORTS = [900, 628, 480, 360, 320]
CONTRAST_WIDTH = 360  # Breite, bei der Kontrast/Tap-Targets geprüft werden

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


# ── Lokalen Server für die Testdauer starten ─────────────────────────
def free_port():
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class LocalServer:
    def __init__(self, root):
        self.root = root
        self.port = free_port()
        self.proc = None

    def __enter__(self):
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(self.port)],
            cwd=str(self.root),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        url = f"http://127.0.0.1:{self.port}/"
        for _ in range(50):
            try:
                urllib.request.urlopen(url, timeout=0.5)
                break
            except Exception:
                time.sleep(0.1)
        else:
            raise RuntimeError("Lokaler Testserver ist nicht hochgekommen.")
        return self

    def __exit__(self, *exc):
        if self.proc:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()

    def url_for(self, rel_path):
        return f"http://127.0.0.1:{self.port}/{rel_path}"


# ── Einmalige, seitenunabhängige Checks (CSS-Dateien, Header) ────────
def global_checks():
    print("\n══ Globale Checks (einmalig) ══")

    css_files = [p for p in sorted(REPO_ROOT.rglob("*.css"))
                 if ".git" not in p.parts and ".claude" not in p.parts]

    # outline: none/0 ohne :focus-visible in derselben Datei
    culprits = []
    for css in css_files:
        text = css.read_text(encoding="utf-8", errors="replace")
        if re.search(r"outline\s*:\s*(none|0)\s*;", text) and ":focus-visible" not in text:
            culprits.append(css.relative_to(REPO_ROOT).as_posix())
    if culprits:
        warn("outline:none/0 ohne :focus-visible-Ersatz in: " + ", ".join(culprits))
    else:
        ok("Kein entfernter Fokusring ohne erkennbaren Ersatz")

    # prefers-reduced-motion irgendwo vorhanden?
    if any("prefers-reduced-motion" in p.read_text(encoding="utf-8", errors="replace")
           for p in css_files):
        ok("prefers-reduced-motion wird mindestens einmal berücksichtigt")
    else:
        warn("Kein prefers-reduced-motion in den CSS-Dateien gefunden")

    # Skip-Link im Header
    header = REPO_ROOT / "Code" / "LB_header.html"
    if header.exists():
        h = header.read_text(encoding="utf-8", errors="replace")
        if re.search(r'href="#(main|content|inhalt)"', h, re.I) or "springen" in h.lower():
            ok("Skip-Link im Header gefunden")
        else:
            warn('Kein Skip-Link („Zum Inhalt springen") in LB_header.html gefunden')


# ── Kontrast- und Tap-Target-Messung (JS, läuft im Browser) ──────────
CONTRAST_JS = """() => {
    function lum(c) {
        const m = c.match(/\\d+(\\.\\d+)?/g).map(Number);
        const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92
                                                          : Math.pow((v + 0.055) / 1.055, 2.4); };
        return 0.2126 * f(m[0]) + 0.7152 * f(m[1]) + 0.0722 * f(m[2]);
    }
    function bg(el) {
        // Läuft die Vorfahren hoch und nimmt den ERSTEN weitgehend deckenden
        // Hintergrund (Alpha >= 0.5). Stark transparente Hintergründe (z.B.
        // Glass-Card-Effekte über einem Hero-Bild) werden übersprungen, weil
        // sie sonst einen bedeutungslosen Fast-1:1-Kontrast gegen sich selbst
        // ergeben würden (Text und "Hintergrund" beide nahe Weiß/halbtransparent).
        let e = el;
        while (e) {
            const c = getComputedStyle(e).backgroundColor;
            const m = c && c.match(/[\\d.]+/g);
            if (m) {
                const alpha = m.length >= 4 ? parseFloat(m[3]) : 1;
                if (alpha >= 0.5) return c;
            }
            e = e.parentElement;
        }
        return 'rgb(255,255,255)';
    }
    const out = [], seen = new Set();
    document.querySelectorAll('body *').forEach(el => {
        if (!el.offsetParent) return;
        const t = [...el.childNodes]
            .filter(n => n.nodeType === 3 && n.textContent.trim())
            .map(n => n.textContent.trim()).join(' ');
        if (!t) return;
        const cs = getComputedStyle(el);
        const fg = cs.color, b = bg(el);
        const l1 = lum(fg), l2 = lum(b);
        const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
        const size = parseFloat(cs.fontSize);
        const bold = parseInt(cs.fontWeight) >= 700;
        const need = (size >= 24 || (size >= 18.66 && bold)) ? 3 : 4.5;
        if (ratio < need) {
            const key = fg + '|' + b + '|' + Math.round(size);
            if (seen.has(key)) return;
            seen.add(key);
            out.push({ t: t.slice(0, 40), fg, b, ratio: +ratio.toFixed(2), need, size: Math.round(size) });
        }
    });
    return out.slice(0, 15);
}"""

TAPTARGET_JS = """() => {
    const out = [];
    document.querySelectorAll(
        'a,button,input,select,textarea,[role="button"],[onclick]'
    ).forEach(el => {
        if (!el.offsetParent) return;
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) return;
        if (r.width < 44 || r.height < 44) {
            out.push({
                tag: el.tagName.toLowerCase(),
                cls: (typeof el.className === 'string' ? el.className : ''),
                text: (el.textContent || el.value || el.getAttribute('aria-label') || '')
                    .replace(/\\s+/g, ' ').trim().slice(0, 30),
                w: Math.round(r.width), h: Math.round(r.height)
            });
        }
    });
    return out.slice(0, 15);
}"""

OVERFLOW_JS = """() => {
    const ov = document.documentElement.scrollWidth - window.innerWidth;
    let culprits = [];
    if (ov > 0) {
        const base = document.documentElement.scrollWidth;
        const cand = [];
        document.querySelectorAll('body *').forEach(e => {
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
}"""


def check_page(browser, server, path):
    rel = path.relative_to(REPO_ROOT).as_posix()
    doc = path.read_text(encoding="utf-8", errors="replace")

    if path.name in SKIP_NAMES or "<head>" not in doc or "<title>" not in doc:
        print(f"\n── {rel}: übersprungen (Fragment/Vorlage, keine eigene Seite)")
        return False

    print(f"\n══ {rel} ══")
    url = server.url_for(rel)

    # ── Überlauf bei mehreren Breiten (harter Fehler) ────────────────
    for width in VIEWPORTS:
        pg = browser.new_page(viewport={"width": width, "height": 900})
        try:
            pg.goto(url, wait_until="networkidle", timeout=15000)
            pg.wait_for_timeout(200)  # Nachladen von Header/Footer/JSON abwarten
            r = pg.evaluate(OVERFLOW_JS)
        finally:
            pg.close()

        if r["ov"] <= 0:
            ok(f"{width}px: kein horizontaler Überlauf")
        else:
            fail(f"{width}px: ÜBERLAUF {r['ov']}px")
            for c in r["culprits"]:
                cls = f".{c['cls']}" if c["cls"] else ""
                print(f"      → Verursacher-Kandidat: <{c['tag'].lower()}{cls}> "
                      f"(entfernt −{c['drop']}px Breite) „{c['text']}…\"")

    # ── Kontrast + Tap-Targets bei einer festen mobilen Breite ───────
    pg = browser.new_page(viewport={"width": CONTRAST_WIDTH, "height": 900})
    try:
        pg.goto(url, wait_until="networkidle", timeout=15000)
        pg.wait_for_timeout(200)
        low_contrast = pg.evaluate(CONTRAST_JS)
        small_targets = pg.evaluate(TAPTARGET_JS)
    finally:
        pg.close()

    if low_contrast:
        warn(f"{len(low_contrast)} Kontrast-Fall/Fälle unter dem WCAG-Mindestwert "
             f"(bei {CONTRAST_WIDTH}px):")
        for c in low_contrast:
            print(f"      → „{c['t']}…\" — {c['ratio']}:1 (nötig {c['need']}:1), "
                  f"{c['fg']} auf {c['b']}, {c['size']}px")
    else:
        ok(f"Kein Kontrast-Fall unter dem WCAG-Mindestwert (bei {CONTRAST_WIDTH}px)")

    if small_targets:
        warn(f"{len(small_targets)} interaktive/s Element/e unter 44×44px "
             f"(bei {CONTRAST_WIDTH}px):")
        for t in small_targets:
            cls = f".{t['cls']}" if t["cls"] else ""
            print(f"      → <{t['tag']}{cls}> „{t['text']}\" — {t['w']}×{t['h']}px")
    else:
        ok("Keine zu kleinen Tap-Targets (bei 44px-Mindestmaß)")

    return True


def all_html():
    out = []
    for p in sorted(REPO_ROOT.rglob("*.html")):
        if ".git" in p.parts or ".claude" in p.parts:
            continue
        out.append(p)
    return out


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("✗ Playwright nicht installiert "
              "(pip install playwright --break-system-packages && "
              "playwright install chromium)")
        sys.exit(1)

    global_checks()

    args = [a for a in sys.argv[1:] if a != "--all"]
    if not args:
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
    with LocalServer(REPO_ROOT) as server:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            try:
                for p in pages:
                    if check_page(browser, server, p):
                        checked += 1
            finally:
                browser.close()

    print("\n══ Ergebnis ═══════════════════════════════════════════════")
    print(f"  Geprüfte Seiten: {checked}")
    if errors:
        print(f"✗ {len(errors)} FEHLER (Überlauf):")
        for e in errors:
            print(f"   - {e}")
        sys.exit(1)
    extra = f" ({len(warnings)} Hinweis(e) — bitte durchsehen)" if warnings else ""
    print(f"✓ Keine harten Fehler{extra}.")
    sys.exit(0)


if __name__ == "__main__":
    main()
