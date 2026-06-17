
   

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