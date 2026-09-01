
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

        // ── Skip-Link-Ziel ───────────────────────────────────────────
        // Der Skip-Link in LB_header.html springt zu "#main-content".
        // Die ID steht in keiner einzelnen Seite fest im HTML, deshalb
        // wird sie hier zentral gesetzt – wirkt dadurch auf jeder Seite,
        // ohne <main> überall einzeln anpassen zu müssen. tabindex="-1"
        // macht <main> fokussierbar, obwohl es normalerweise kein
        // interaktives Element ist – sonst würde der Sprung zwar scrollen,
        // der Tastaturfokus aber auf der Seite hängen bleiben.
        const mainEl = document.querySelector('main');
        if (mainEl) {
            if (!mainEl.id) mainEl.id = 'main-content';
            mainEl.setAttribute('tabindex', '-1');
        }
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
    var vokabelDaten       = null;  // hier landet das geladene JSON (Cache)
    var wirdGeladen        = false; // true, während der fetch() läuft
    var debounceTimer      = null;  // Timer-ID für das Entprellen der Eingabe
    var aktiverIndex       = -1;    // per Pfeiltaste markierter Treffer (-1 = keiner)
    var vorherigerFokus    = null;  // Element, das vor dem Öffnen fokussiert war
    var vorherigerOverflow = '';    // body-Overflow vor dem Sperren des Seiten-Scrolls

    // Absoluter Pfad zur Vokabel-Kapitelseite – Ziel der Ergebnis-Links.
    var MASTER_PATH = '/Code/2_Vokabeln/LB_2-1_Vokabeln_Master.html';

    // Reihenfolge der Niveaus für die Sortierung bei Gleichstand
    // (A1 zuerst). Fehlt ein Niveau (sollte nicht vorkommen), landet
    // der Treffer über "?? 99" ganz hinten statt die Sortierung zu brechen.
    var NIVEAU_REIHENFOLGE = { 'A1': 0, 'A2': 1, 'B1': 2, 'B2': 3, 'C1': 4, 'C2': 5 };

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

    // -- Hilfsfunktion: bosnisches Wort in einen URL-Anker verwandeln --
    // Leerzeichen (bei Mehrwortlemmata wie "biti bolestan") werden zu
    // Bindestrichen, Diakritika bleiben erhalten. Dieselbe Funktion
    // steht (bewusst dupliziert, wie im Projekt üblich) auch in
    // LB_2-1_Vokabeln_Master.html – nur wenn beide Seiten denselben
    // Anker berechnen, springt der Link auch wirklich zum richtigen Wort.
    function wortAnker(wort) {
        return (wort || '').trim().replace(/\s+/g, '-');
    }

    // -- Relevanz EINES Feldes (Deutsch ODER Bosnisch) ermitteln ---
    // Rückgabe: 0 = exakte Übereinstimmung, 1 = Feld beginnt mit q,
    // 2 = eines der Wörter in einem Mehrwortlemma beginnt mit q,
    // 3 = q steckt nur irgendwo als Teilstring drin, -1 = kein Treffer.
    function feldRang(feldWert, q) {
        var norm = normalisieren(feldWert);
        var pos  = norm.indexOf(q);
        if (pos === -1) return -1;
        if (norm === q) return 0;
        if (pos === 0)  return 1;

        // Erstes Wort ist durch den obigen pos===0-Test schon abgedeckt,
        // deshalb hier erst ab dem zweiten Wort prüfen.
        var woerter = norm.split(' ');
        for (var i = 1; i < woerter.length; i++) {
            if (woerter[i].indexOf(q) === 0) return 2;
        }
        return 3;
    }

    // -- Besten (niedrigsten) Rang eines Eintrags über beide Felder --
    function eintragRang(e, q) {
        var rBs = feldRang(e.Bosnisch, q);
        var rDe = feldRang(e.Deutsch, q);
        if (rBs === -1) return rDe;   // nur Deutsch trifft (oder gar keins: -1)
        if (rDe === -1) return rBs;   // nur Bosnisch trifft
        return Math.min(rBs, rDe);    // beide treffen: besserer Rang zählt
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
            aktiverIndex = -1;
            return;
        }

        // Daten noch nicht da? Kurzer Hinweis, Suche folgt automatisch,
        // sobald datenLaden() fertig ist (siehe .then() oben).
        if (!vokabelDaten) {
            results.innerHTML = '<p class="search-hint">Wörterbuch wird geladen …</p>';
            aktiverIndex = -1;
            return;
        }

        // Durchsuchen: gegen Deutsch UND Bosnisch, jeden Treffer mit
        // seinem Relevanz-Rang sammeln (noch OHNE Obergrenze – die
        // Gesamtzahl brauchen wir für die "X von Y Treffern"-Anzeige).
        var alleTreffer = [];
        for (var i = 0; i < vokabelDaten.length; i++) {
            var e    = vokabelDaten[i];
            var rang = eintragRang(e, q);
            if (rang !== -1) {
                alleTreffer.push({ eintrag: e, rang: rang });
            }
        }

        // Keine Treffer → Hinweistext, Ergebnisliste war zuvor schon
        // vom letzten Suchlauf befüllt, also aktiverIndex zurücksetzen.
        aktiverIndex = -1;
        if (alleTreffer.length === 0) {
            results.innerHTML = '<p class="search-hint">Keine Treffer in LinguaBosna</p>';
            return;
        }

        // Sortieren: erst nach Relevanz-Rang (0 = am besten), bei
        // Gleichstand nach Niveau (A1 zuerst). Array.sort() ist in
        // modernen Browsern stabil – gleiche Treffer behalten sonst
        // ihre ursprüngliche Reihenfolge aus der JSON-Datei.
        alleTreffer.sort(function (a, b) {
            if (a.rang !== b.rang) return a.rang - b.rang;
            var na = NIVEAU_REIHENFOLGE[a.eintrag.Niveau];
            var nb = NIVEAU_REIHENFOLGE[b.eintrag.Niveau];
            if (na === undefined) na = 99;
            if (nb === undefined) nb = 99;
            return na - nb;
        });

        var gesamtzahl = alleTreffer.length;
        var treffer    = alleTreffer.slice(0, 8).map(function (t) { return t.eintrag; });

        // Trefferzahl-Zeile: macht die Begrenzung auf 8 sichtbar,
        // z. B. "8 von 23 Treffern" (oder einfach "3 Treffer", wenn
        // ohnehin alle angezeigt werden).
        var zahlHtml = '<p class="search-result-count">' +
            (gesamtzahl > treffer.length
                ? treffer.length + ' von ' + gesamtzahl + ' Treffern'
                : gesamtzahl + ' Treffer') +
            '</p>';

        // Treffer in HTML umwandeln und einsetzen.
        var trefferHtml = treffer.map(function (e) {
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

            var innerHtml =
                '<div class="search-result-main">' +
                    '<span class="search-result-de">' + escapeHtml(e.Deutsch) + '</span>' +
                    '<span class="search-result-sep"> – </span>' +
                    '<span class="search-result-bs">' + escapeHtml(e.Bosnisch) + '</span>' +
                '</div>' +
                metaHtml;

            // Einträge mit eigenem Kapitel verlinken direkt dorthin
            // (samt Anker aufs Wort). Reine Wörterbuch-Einträge
            // ("nur_woerterbuch": true) haben kein Kapitel und bleiben
            // deshalb sichtbar, aber ohne Link (keine Sackgasse mehr
            // vortäuschen, wo keine gibt).
            if (e.Kapitel) {
                var href = MASTER_PATH + '?kapitel=' + e.Kapitel +
                           '#' + encodeURIComponent(wortAnker(e.Bosnisch));
                return '<a class="search-result" href="' + href + '">' + innerHtml + '</a>';
            }
            return '<div class="search-result search-result-static">' + innerHtml + '</div>';
        }).join('');

        results.innerHTML = zahlHtml + trefferHtml;
    }

    // -- Aktiven (per Pfeiltaste markierten) Treffer setzen --------
    // index wird auf die gültigen Grenzen begrenzt. Ohne Treffer
    // passiert nichts. Der markierte Treffer bekommt die Klasse
    // "is-active" (Styling wie :hover) und wird ins Bild gescrollt.
    function aktivenTrefferSetzen(index) {
        var elemente = results.querySelectorAll('.search-result');
        if (!elemente.length) {
            aktiverIndex = -1;
            return;
        }
        if (index < 0) index = 0;
        if (index > elemente.length - 1) index = elemente.length - 1;

        elemente.forEach(function (el, i) {
            el.classList.toggle('is-active', i === index);
        });
        elemente[index].scrollIntoView({ block: 'nearest' });
        aktiverIndex = index;
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

        // Seiten-Scroll sperren, solange das Overlay offen ist – sonst
        // könnte man den Hintergrund hinter dem Panel weiterscrollen.
        vorherigerOverflow = document.body.style.overflow;
        document.body.style.overflow = 'hidden';

        // Merken, welches Element vorher fokussiert war (z. B. relevant,
        // wenn das Overlay per "/" mitten auf der Seite geöffnet wurde),
        // damit overlaySchliessen() den Fokus dorthin zurückgeben kann.
        vorherigerFokus = document.activeElement;

        // Eingabefeld fokussieren (kleiner Timeout, damit das Element
        // sicher sichtbar ist, bevor der Fokus gesetzt wird).
        setTimeout(function () { input.focus(); }, 0);
    }

    // -- Overlay schließen ----------------------------------------
    function overlaySchliessen() {
        overlay.hidden = true;                            // ausblenden
        toggleBtn.setAttribute('aria-expanded', 'false'); // Zustand melden

        // Seiten-Scroll wieder freigeben.
        document.body.style.overflow = vorherigerOverflow;

        // Fokus zurückgeben: bevorzugt an das Element, das vor dem
        // Öffnen fokussiert war, sonst zurück auf die Lupe.
        if (vorherigerFokus && typeof vorherigerFokus.focus === 'function') {
            vorherigerFokus.focus();
        } else {
            toggleBtn.focus();
        }
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

    // Escape schließt das offene Overlay; "/" oder Strg+K (Cmd+K auf dem
    // Mac) öffnet es von JEDER Seite aus.
    document.addEventListener('keydown', function (e) {
        if (!overlay.hidden) {
            if (e.key === 'Escape') {
                overlaySchliessen();
            }
            return;
        }

        var istCtrlK = (e.key === 'k' || e.key === 'K') && (e.ctrlKey || e.metaKey);
        var istSlash = e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey;
        if (!istCtrlK && !istSlash) return;

        // "/" nicht abfangen, wenn der Nutzer gerade in einem ANDEREN
        // Eingabefeld tippt (z. B. im Vokabeltrainer oder in einem Quiz) –
        // sonst könnte man dort kein "/" mehr eintippen. Strg+K bleibt
        // bewusst immer aktiv, das ist ein reines Tastenkürzel.
        var ziel = e.target;
        var tipptGerade = ziel && (
            ziel.tagName === 'INPUT' || ziel.tagName === 'TEXTAREA' || ziel.isContentEditable
        );
        if (istSlash && tipptGerade) return;

        e.preventDefault();
        overlayOeffnen();
        datenLaden();          // JSON beim ersten Öffnen laden (danach gecacht)
    });

    // Fokus-Trap: solange das Overlay offen ist, bleibt Tab/Shift+Tab
    // innerhalb des Panels (Eingabefeld, Treffer-Links, X-Button,
    // dict.cc-Link) – man kann sich nicht "aus Versehen" auf den Rest
    // der Seite hinaus-tabben.
    document.addEventListener('keydown', function (e) {
        if (overlay.hidden || e.key !== 'Tab') return;

        var fokussierbar = panel.querySelectorAll(
            'a[href], button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );
        if (!fokussierbar.length) return;

        var erstes  = fokussierbar[0];
        var letztes = fokussierbar[fokussierbar.length - 1];

        if (e.shiftKey && document.activeElement === erstes) {
            e.preventDefault();
            letztes.focus();
        } else if (!e.shiftKey && document.activeElement === letztes) {
            e.preventDefault();
            erstes.focus();
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

    // Pfeiltasten wandern durch die Treffer, Enter öffnet den markierten
    // Treffer (nur wenn er ein echter Link ist – unverlinkte reine
    // Wörterbuch-Einträge lassen sich per Enter nicht "öffnen").
    input.addEventListener('keydown', function (e) {
        var elemente = results.querySelectorAll('.search-result');

        if (e.key === 'ArrowDown') {
            if (!elemente.length) return;
            e.preventDefault();
            aktivenTrefferSetzen(aktiverIndex + 1);
        } else if (e.key === 'ArrowUp') {
            if (!elemente.length) return;
            e.preventDefault();
            aktivenTrefferSetzen(aktiverIndex - 1);
        } else if (e.key === 'Enter') {
            if (aktiverIndex === -1 || !elemente[aktiverIndex]) return;
            var el = elemente[aktiverIndex];
            if (el.tagName === 'A') {
                e.preventDefault();
                el.click();
            }
        }
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

// ── Fortschrittsleiste (Grammatikseiten): Scrollspy ─────────
// Die 6 Schritte in .progress-steps sind Anker-Links (<a href="#block-N">)
// auf die 6 .grammar-section-Blöcke der Seite (siehe
// TEMPLATE_Grammatik_Detailseite.html). Dieses Modul markiert beim
// Scrollen den gerade sichtbaren Block mit der Klasse "active" an
// seinem Link (Styling in Style_3_Grammatik_Detail.css). Läuft auf
// JEDER Seite, weil LB_main.js überall eingebunden ist – bricht aber
// sofort ab, wenn .progress-steps fehlt (bisher nur Grammatikseiten).
(function () {
    function init() {
        var steps = document.querySelectorAll('.progress-steps .step');
        if (!steps.length || !window.IntersectionObserver) return;

        // Nur Links mit einem echten #block-N-Ziel berücksichtigen.
        var sections = [];
        steps.forEach(function (step) {
            var hash = step.getAttribute('href');
            if (!hash || hash.charAt(0) !== '#') return;
            var section = document.querySelector(hash);
            if (section) sections.push(section);
        });
        if (!sections.length) return;

        function setActive(hash) {
            steps.forEach(function (step) {
                step.classList.toggle('active', step.getAttribute('href') === hash);
            });
        }

        // rootMargin zieht den "aktiven Streifen" auf einen schmalen Bereich
        // knapp unter dem fixen Header + der sticky Fortschrittsleiste
        // (zusammen ca. 140px): der Block, dessen Oberkante dort gerade
        // durchläuft, gilt als aktueller Abschnitt. -60% unten sorgt dafür,
        // dass immer nur ein Block gleichzeitig als "aktiv" zählt, auch
        // wenn Blöcke unterschiedlich lang sind.
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    setActive('#' + entry.target.id);
                }
            });
        }, { rootMargin: '-140px 0px -60% 0px', threshold: 0 });

        sections.forEach(function (section) { observer.observe(section); });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
// ────────────────────────────────────────────────────────────

// ── Lernfortschritt-Modul nachladen ─────────────────────────
// LB_fortschritt.js merkt sich im localStorage des Besuchers, welche
// Vokabelkapitel geübt und welche Grammatikthemen gelesen wurden.
// Es steckt in einer eigenen Datei, damit LB_main.js übersichtlich
// bleibt — wird aber von hier aus geladen und läuft dadurch auf JEDER
// Seite. Wie bei GoatCounter über createElement/appendChild, weil ein
// per innerHTML eingefügtes <script> nicht ausgeführt würde.
(function () {
    var fs = document.createElement('script');
    fs.src = '/Code/LB_fortschritt.js';   // absoluter Pfad (Projektprinzip)
    // Per JS eingefügte <script>-Elemente laden ohnehin asynchron und
    // blockieren den Seitenaufbau nicht. Das Modul wartet selbst darauf,
    // dass das DOM fertig ist.
    document.head.appendChild(fs);
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

