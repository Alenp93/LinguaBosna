

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
// gebraucht wird (Vokabel-Tabelle UND Vokabeltrainer). So gibt es
// nur EINE Stelle, die gepflegt werden muss.
//
// HINTERGRUND ZUR AUSSPRACHE:
// Eine echte BOSNISCHE Computerstimme ("bs-BA") gibt es fast nirgends.
// Bosnisch klingt aber wie Kroatisch/Serbisch und wird lateinisch
// "wie geschrieben" gelesen → wir suchen eine kroatische/serbische
// Stimme. Zwei typische Stolpersteine, die hier abgefangen werden:
//   1) Die Stimmenliste ist anfangs LEER und füllt sich erst verzögert.
//   2) In Edge gibt es kroatische ONLINE-Stimmen, die oft erst NACH
//      dem ersten Sprechversuch auftauchen ("Aufwärm"-Trick unten).
(function () {

  let verfuegbareStimmen = [];   // gemerkte Stimmenliste
  let aufgewaermt        = false; // wurde der Edge-Aufwärmruf schon gemacht?

  function stimmenLaden() {
    if ('speechSynthesis' in window) {
      verfuegbareStimmen = window.speechSynthesis.getVoices() || [];
    }
  }

  if ('speechSynthesis' in window) {
    stimmenLaden();
    // Feuert, sobald (mehr) Stimmen bereitstehen
    window.speechSynthesis.onvoiceschanged = stimmenLaden;
    // Online-Stimmen laden manchmal sekundenlang → mehrmals nachfragen
    let versuche = 0;
    const poll = setInterval(() => {
      stimmenLaden();
      if (versuche++ > 12) clearInterval(poll);
    }, 500);
  }

  // Sucht die beste Stimme. Für Bosnisch in der Reihenfolge der
  // Sprachverwandtschaft: bosnisch → kroatisch → serbisch →
  // slowenisch → mazedonisch (alle näher an Bosnisch als Deutsch).
  function findeStimme(sprache) {
    stimmenLaden();
    if (sprache === 'de') {
      return verfuegbareStimmen.find(s => s.lang.toLowerCase().startsWith('de')) || null;
    }
    for (const code of ['bs', 'hr', 'sr', 'sl', 'mk']) {
      const treffer = verfuegbareStimmen.find(s => s.lang.toLowerCase().startsWith(code));
      if (treffer) return treffer;
    }
    return null;
  }

  // Spricht das Wort tatsächlich aus.
  function aussprechen(text, sprache) {
    window.speechSynthesis.cancel(); // evtl. laufende Ausgabe stoppen

    const u      = new SpeechSynthesisUtterance(text);
    const stimme = findeStimme(sprache);

    if (stimme) {
      u.voice = stimme;
      u.lang  = stimme.lang;
    } else {
      // Keine Stimme gelistet → trotzdem die Sprache angeben. Edge nutzt
      // dann ggf. eine Online-Stimme. Klappt das nicht, fängt onerror es ab.
      u.lang = (sprache === 'de') ? 'de-DE' : 'hr-HR';
    }
    u.rate = 0.9; // etwas langsamer = besser zum Mitlernen

    // Schlägt die Ausgabe fehl (z. B. keine passende Stimme vorhanden),
    // zeigen wir einen kurzen Hinweis statt einfach stumm zu bleiben.
    u.onerror = (e) => {
      if (e.error && e.error !== 'interrupted' && e.error !== 'canceled') {
        hinweisZeigen();
      }
    };

    window.speechSynthesis.speak(u);
  }

  // Kleine, unaufdringliche Einblendung am unteren Bildschirmrand.
  function hinweisZeigen() {
    let t = document.getElementById('lb-speak-hint');
    if (!t) {
      t = document.createElement('div');
      t.id = 'lb-speak-hint';
      t.style.cssText =
        'position:fixed;left:50%;bottom:24px;transform:translateX(-50%);' +
        'background:#0A3D62;color:#fff;padding:10px 16px;border-radius:8px;' +
        'font:14px/1.4 "Open Sans",system-ui,sans-serif;z-index:9999;' +
        'max-width:90%;box-shadow:0 6px 20px rgba(0,0,0,.25);transition:opacity .4s';
      document.body.appendChild(t);
    }
    t.textContent = '🔇 Auf diesem Gerät ist keine passende Stimme installiert – Aussprache nicht verfügbar.';
    t.style.opacity = '1';
    clearTimeout(t._timer);
    t._timer = setTimeout(() => { t.style.opacity = '0'; }, 3500);
  }

  // Öffentliche Funktion: auf jeder Seite als LB_speak(...) aufrufbar.
  //   text    = Wort MIT Sonderzeichen (č, ć, š, ž, đ)
  //   sprache = 'bos' (Standard) oder 'de'
  window.LB_speak = function (text, sprache) {
    if (!text) return;
    if (!('speechSynthesis' in window)) { hinweisZeigen(); return; }
    sprache = sprache || 'bos';

    // EDGE-AUFWÄRM-TRICK: Beim allerersten Klick einen unhörbaren
    // Mini-Ruf abgeben. Das bewegt Edge dazu, seine Online-Stimmen zu
    // laden. Das echte Wort kommt 300 ms später – dann ist die kroatische
    // Stimme meist verfügbar. Ab dem 2. Klick direkt sprechen.
    if (!aufgewaermt) {
      aufgewaermt = true;
      try {
        const warm = new SpeechSynthesisUtterance(' ');
        warm.volume = 0; // unhörbar
        window.speechSynthesis.speak(warm);
      } catch (e) { /* egal */ }
      setTimeout(() => aussprechen(text, sprache), 300);
      return;
    }

    aussprechen(text, sprache);
  };

})();
// ────────────────────────────────────────────────────────────
