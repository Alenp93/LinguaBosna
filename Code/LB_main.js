
//Header//
   fetch('/Code/LB_header.html')
        .then(response => response.text())
        .then(html => {
            // Suchen Sie einen Platzhalter im aktuellen HTML-Dokument
            const headerPlaceholder = document.getElementById('header');
            if (headerPlaceholder) {
                headerPlaceholder.innerHTML = html;
            } else {
                // Alternativ: Fügen Sie den Header am Anfang des Body-Bereichs ein
                document.body.insertAdjacentHTML('afterbegin', html);
            }
        // ── Hamburger-Menü ──────────────────────────────────────────
        // Erst HIER initialisieren, weil der Header jetzt im DOM ist
        const hamburger = document.getElementById('hamburger');
        const navMenu   = document.getElementById('nav-menu');

        if (hamburger && navMenu) {

            // Klick auf den Hamburger-Button öffnet/schließt das Menü
            hamburger.addEventListener('click', function () {
                navMenu.classList.toggle('open');
                hamburger.classList.toggle('open');

                // aria-expanded für Barrierefreiheit aktualisieren
                const isOpen = navMenu.classList.contains('open');
                hamburger.setAttribute('aria-expanded', isOpen);
            });

            // Menü automatisch schließen, wenn ein Link angeklickt wird
            navMenu.querySelectorAll('a').forEach(function (link) {
                link.addEventListener('click', function () {
                    navMenu.classList.remove('open');
                    hamburger.classList.remove('open');
                    hamburger.setAttribute('aria-expanded', false);
                });
            });
        }
        // ────────────────────────────────────────────────────────────

        // ── Wörterbuch-Suche (Header-Overlay) ───────────────────────
        // Läuft hier drin, weil der Header (und damit das Such-Icon +
        // das Overlay) erst JETZT im DOM steht – vorher gäbe es die
        // Elemente noch nicht.
        initWoerterbuchSuche();
        // ────────────────────────────────────────────────────────────
    });

// ── Wörterbuch-Suche: gesamte Logik ─────────────────────────────
// Als eigene Funktion ausgelagert, damit der obige .then()-Block
// übersichtlich bleibt. Wird von dort aufgerufen, sobald der Header
// im DOM ist.
function initWoerterbuchSuche() {

    // Die Bausteine aus LB_header.html einsammeln
    var toggleBtn = document.getElementById('search-toggle');   // Lupe im Header
    var overlay   = document.getElementById('search-overlay');  // ganzes Overlay
    var panel     = overlay ? overlay.querySelector('.search-panel') : null; // das Panel
    var input     = document.getElementById('search-input');    // Eingabefeld
    var closeBtn  = document.getElementById('search-close');    // X-Button
    var results   = document.getElementById('search-results');  // Ergebnis-Container
    var dictcc    = document.getElementById('search-dictcc');   // dict.cc-Link

    // Wenn eines der Kernelemente fehlt (z. B. Header nicht geladen),
    // brechen wir sauber ab, statt einen Fehler zu werfen.
    if (!toggleBtn || !overlay || !panel || !input || !closeBtn || !results || !dictcc) {
        return;
    }

    // -- Zustands-Variablen ---------------------------------------
    var vokabelDaten  = null;   // hier landet das geladene JSON (Cache)
    var wirdGeladen   = false;  // true, während der fetch() läuft
    var debounceTimer = null;   // Timer-ID für das Entprellen der Eingabe

    // -- Hilfsfunktion: Text für den Vergleich vereinheitlichen ----
    // Entfernt Diakritika (č, ć, š, ž, đ → c, s, z, d) und macht alles
    // klein. So findet "cetiri" auch "četiri" und umgekehrt.
    // normalize('NFD') zerlegt Buchstaben in Grundzeichen + Akzent,
    // die Regex löscht dann alle Akzentzeichen (U+0300 bis U+036F).
    function normalisieren(text) {
        return (text || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase();
    }

    // -- Hilfsfunktion: HTML-Sonderzeichen entschärfen -------------
    // Sicherheitsnetz, falls in den Daten mal <, > oder & vorkommt,
    // damit beim Einfügen per innerHTML nichts kaputtgeht.
    function escapeHtml(text) {
        return (text || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    // -- JSON einmalig laden und cachen ---------------------------
    // Wird beim ersten Öffnen des Overlays aufgerufen. Danach liegt
    // alles im Speicher (vokabelDaten) – kein erneuter Netzabruf.
    function datenLaden() {
        if (vokabelDaten || wirdGeladen) return;   // schon da oder gerade dabei
        wirdGeladen = true;

        fetch('/Code/2_Vokabeln/vokabeln_flat.json')
            .then(function (antwort) { return antwort.json(); })
            .then(function (daten) {
                vokabelDaten = daten;
                wirdGeladen  = false;
                // Falls der Nutzer schon getippt hat, während geladen
                // wurde: jetzt die Suche mit dem aktuellen Wert nachholen.
                if (input.value.trim()) {
                    sucheAusfuehren(input.value);
                }
            })
            .catch(function () {
                wirdGeladen = false;
                results.innerHTML =
                    '<p class="search-hint">Wörterbuch konnte nicht geladen ' +
                    'werden. Bitte später erneut versuchen.</p>';
            });
    }

    // -- Suche ausführen und Ergebnisse anzeigen ------------------
    function sucheAusfuehren(begriff) {
        var roh = begriff.trim();               // Original (für dict.cc-Link)
        var q   = normalisieren(roh);           // normalisiert (für Vergleich)

        // dict.cc-Link IMMER aktualisieren (auch bei leerer Eingabe egal).
        dictcc.href = 'https://m.dict.cc/deutsch-bosnisch/' +
                      encodeURIComponent(roh) + '.html';

        // Leere Eingabe → Ergebnisliste leeren, nichts weiter tun.
        if (!q) {
            results.innerHTML = '';
            return;
        }

        // Daten noch nicht da? Kurzer Hinweis, Suche folgt automatisch,
        // sobald datenLaden() fertig ist (siehe .then() oben).
        if (!vokabelDaten) {
            results.innerHTML = '<p class="search-hint">Wörterbuch wird geladen …</p>';
            return;
        }

        // Durchsuchen: gegen Deutsch UND Bosnisch, max. 8 Treffer.
        var treffer = [];
        for (var i = 0; i < vokabelDaten.length && treffer.length < 8; i++) {
            var e = vokabelDaten[i];
            if (normalisieren(e.Deutsch).indexOf(q) !== -1 ||
                normalisieren(e.Bosnisch).indexOf(q) !== -1) {
                treffer.push(e);
            }
        }

        // Keine Treffer → Hinweistext.
        if (treffer.length === 0) {
            results.innerHTML = '<p class="search-hint">Keine Treffer in LinguaBosna</p>';
            return;
        }

        // Treffer in HTML umwandeln und einsetzen.
        results.innerHTML = treffer.map(function (e) {
            // Wortart steht je nach Eintrag mal unter "Wortart (Genus)"
            // (Substantive), mal unter "Wortart" (alles andere) – beide prüfen.
            var wortart = e['Wortart (Genus)'] || e['Wortart'] || '';
            var niveau  = e.Niveau || '';

            // Meta-Zeile (Wortart + Niveau-Pill) nur bauen, wenn es was gibt.
            var metaHtml = '';
            if (wortart || niveau) {
                metaHtml = '<div class="search-result-meta">';
                if (wortart) {
                    metaHtml += '<span class="search-result-wortart">' +
                                escapeHtml(wortart) + '</span>';
                }
                if (niveau) {
                    metaHtml += '<span class="search-result-niveau">' +
                                escapeHtml(niveau) + '</span>';
                }
                metaHtml += '</div>';
            }

            return '' +
                '<div class="search-result">' +
                    '<div class="search-result-main">' +
                        '<span class="search-result-de">' + escapeHtml(e.Deutsch) + '</span>' +
                        '<span class="search-result-sep"> – </span>' +
                        '<span class="search-result-bs">' + escapeHtml(e.Bosnisch) + '</span>' +
                    '</div>' +
                    metaHtml +
                '</div>';
        }).join('');
    }

    // -- Overlay öffnen -------------------------------------------
    function overlayOeffnen() {
        overlay.hidden = false;                          // sichtbar machen
        toggleBtn.setAttribute('aria-expanded', 'true'); // Zustand melden

        // Auf Mobil: falls das Hamburger-Menü offen war, zuklappen,
        // damit das Overlay allein im Vordergrund steht.
        var navMenu   = document.getElementById('nav-menu');
        var hamburger = document.getElementById('hamburger');
        if (navMenu)   navMenu.classList.remove('open');
        if (hamburger) {
            hamburger.classList.remove('open');
            hamburger.setAttribute('aria-expanded', false);
        }

        // Eingabefeld fokussieren (kleiner Timeout, damit das Element
        // sicher sichtbar ist, bevor der Fokus gesetzt wird).
        setTimeout(function () { input.focus(); }, 0);
    }

    // -- Overlay schließen ----------------------------------------
    function overlaySchliessen() {
        overlay.hidden = true;                            // ausblenden
        toggleBtn.setAttribute('aria-expanded', 'false'); // Zustand melden
        toggleBtn.focus();                                // Fokus zurück auf Lupe
    }

    // -- Ereignisse verdrahten ------------------------------------

    // Klick auf die Lupe: auf/zu umschalten.
    toggleBtn.addEventListener('click', function () {
        if (overlay.hidden) {
            overlayOeffnen();
            datenLaden();          // JSON beim ersten Öffnen laden (danach gecacht)
        } else {
            overlaySchliessen();
        }
    });

    // Klick auf das X: schließen.
    closeBtn.addEventListener('click', overlaySchliessen);

    // Klick auf die dunkle Fläche AUSSERHALB des Panels: schließen.
    // (e.target === overlay heißt: es wurde der Hintergrund getroffen,
    // nicht das Panel oder ein Element darin.)
    overlay.addEventListener('click', function (e) {
        if (e.target === overlay) {
            overlaySchliessen();
        }
    });

    // Escape-Taste: schließen (nur wenn das Overlay offen ist).
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && !overlay.hidden) {
            overlaySchliessen();
        }
    });

    // Live-Suche mit ~150 ms Entprellung (Debounce): Es wird erst
    // gesucht, wenn der Nutzer kurz aufhört zu tippen – das spart
    // unnötige Durchläufe bei jedem einzelnen Tastenanschlag.
    input.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        var wert = input.value;
        debounceTimer = setTimeout(function () {
            sucheAusfuehren(wert);
        }, 150);
    });
}
// ────────────────────────────────────────────────────────────

//Footer//
    fetch('/Code/LB_footer.html')
        .then(response => response.text())
        .then(html => {
            // Suchen Sie einen Platzhalter im aktuellen HTML-Dokument
            const footerPlaceholder = document.getElementById('footer');
            if (footerPlaceholder) {
                footerPlaceholder.innerHTML = html;
            } else {
                // Alternativ: Fügen Sie den Footer am Ende des Body-Bereichs ein
                document.body.insertAdjacentHTML('afterbegin', html);
            }
        });

// ── Tabellen-Scroll-Schatten ────────────────────────────────
// Setzt an jedem .letter-table-wrap die Klassen .lb-scroll-left /
// .lb-scroll-right – aber NUR, wenn man in diese Richtung noch scrollen
// kann. Das CSS (Style_3_Grammatik_Detail.css) zeigt den Schatten dann
// nur auf der jeweiligen Seite. Ergebnis:
//   • kein Überlauf            → keine Klasse → kein Schatten
//   • am Anschlag (links/rechts) → Schatten auf DER Seite verschwindet
// Läuft auf jeder Seite, weil LB_main.js überall eingebunden ist.
(function () {
    // Schatten-Klassen für EIN Wrap-Element anhand der Scroll-Position setzen
    function update(wrap) {
        var max = wrap.scrollWidth - wrap.clientWidth; // max. scrollbare Strecke
        var overflow = max > 1;                         // gibt es überhaupt Überlauf?
        var x = wrap.scrollLeft;
        // links scrollbar, wenn nicht am linken Anschlag (x > 0)
        wrap.classList.toggle('lb-scroll-left',  overflow && x > 1);
        // rechts scrollbar, wenn nicht am rechten Anschlag (x < max)
        wrap.classList.toggle('lb-scroll-right', overflow && x < max - 1);
    }

    function init() {
        var wraps = document.querySelectorAll('.letter-table-wrap');
        wraps.forEach(function (wrap) {
            var run = function () { update(wrap); };
            run();                                          // Anfangszustand
            wrap.addEventListener('scroll', run, { passive: true });
            // Neu berechnen, wenn sich die Wrap-Breite ändert (Drehen, Reflow)
            if (window.ResizeObserver) {
                new ResizeObserver(run).observe(wrap);
            }
        });
        // Fallback ohne ResizeObserver: bei Fensteränderung alle neu prüfen
        window.addEventListener('resize', function () {
            document.querySelectorAll('.letter-table-wrap').forEach(update);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    // Schriften können Spaltenbreiten nachträglich ändern → nach vollständigem
    // Laden noch einmal prüfen, damit der Anfangszustand stimmt.
    window.addEventListener('load', function () {
        document.querySelectorAll('.letter-table-wrap').forEach(update);
    });
})();
// ────────────────────────────────────────────────────────────

// ── GoatCounter Webanalyse ──────────────────────────────────
// Läuft auf JEDER Seite, weil LB_main.js überall eingebunden ist.
// Wir erzeugen das <script>-Element per JS und hängen es an den
// <body> an. Wichtig: Ein per innerHTML eingefügtes <script> würde
// NICHT ausgeführt – deshalb dieser Weg über createElement/appendChild.
(function () {
    var gc = document.createElement('script');          // neues <script> erzeugen
    gc.async = true;                                    // blockiert das Laden der Seite nicht
    gc.src = '//gc.zgo.at/count.js';                    // das Zähl-Script von GoatCounter

    gc.setAttribute('data-goatcounter',
                    'https://linguabosna.goatcounter.com/count');
    document.body.appendChild(gc);                      // ins DOM einfügen → wird ausgeführt
})();
// ────────────────────────────────────────────────────────────

