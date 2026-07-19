
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
    });

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

