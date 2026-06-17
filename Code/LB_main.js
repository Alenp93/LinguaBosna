
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


// ── Aussprache / Sprachausgabe (Text-to-Speech) ─────────────
// Liegt HIER in LB_main.js, weil die Funktion auf mehreren Seiten
// gebraucht wird (Vokabel-Tabelle UND Vokabeltrainer).
//
// Eine echte BOSNISCHE Stimme ("bs-BA") gibt es fast nirgends. Bosnisch
// klingt aber wie Kroatisch/Serbisch und wird lateinisch "wie geschrieben"
// gelesen. Darum sprechen wir mit kroatischer Sprache (hr-HR) und nehmen,
// falls vorhanden, eine kroatische/serbische Stimme des Geräts.
//
// WICHTIG (Handy): speak() MUSS direkt im Antippen laufen – ohne Timer,
// ohne Verzögerung, sonst blockieren mobile Browser den Ton.
(function () {

  // Manche Browser füllen die Stimmenliste verzögert – Laden anstoßen.
  if ('speechSynthesis' in window) {
    window.speechSynthesis.getVoices();
  }

  // Liefert – falls vorhanden – eine passende Stimme des Geräts zurück.
  function findeStimme(sprache) {
    const stimmen = window.speechSynthesis.getVoices() || [];
    if (sprache === 'de') {
      return stimmen.find(s => s.lang.toLowerCase().startsWith('de'));
    }
    // bosnisch → kroatisch → serbisch (gleiche Aussprache)
    return stimmen.find(s => /^(bs|hr|sr)/.test(s.lang.toLowerCase()));
  }

  // Öffentliche Funktion: LB_speak('riječ', 'bos')  oder  LB_speak('Wort', 'de')
  //   text = das Wort MIT Sonderzeichen (č, ć, š, ž, đ)
  window.LB_speak = function (text, sprache) {
    if (!text || !('speechSynthesis' in window)) return;
    sprache = sprache || 'bos';

    window.speechSynthesis.cancel();                 // evtl. Laufendes stoppen
    const u = new SpeechSynthesisUtterance(text);

    const stimme = findeStimme(sprache);
    if (stimme) u.voice = stimme;                    // passende Stimme, wenn vorhanden
    u.lang = stimme ? stimme.lang                    // sonst wenigstens die Sprache
                    : (sprache === 'de' ? 'de-DE' : 'hr-HR');
    u.rate = 0.9;                                    // etwas langsamer zum Mitlernen

    window.speechSynthesis.speak(u);
  };

})();
// ────────────────────────────────────────────────────────────

