/* ======================================================
   kultur.js — gemeinsame Logik des Kultur-Bereichs
   LinguaBosna

   Wird von der Übersicht UND von jedem Beitrag eingebunden:
     <script src="/Code/5_Kultur/kultur.js" defer></script>

   Enthält zwei unabhängige Bausteine. Jeder prüft zuerst, ob
   seine Elemente auf der Seite stehen, und tut sonst nichts:

   1. Rubrik-Filter   (nur Übersicht: .kultur-filter + .kultur-grid)
   2. Mini-Quiz       (nur Beiträge: #kulturQuizDaten)

   Interaktive Elemente, die es nur in EINEM Beitrag gibt
   (z. B. der Stammbaum-Rechner), stehen NICHT hier, sondern
   als eigenes <script> im jeweiligen Beitrag.

   Wegen "defer" läuft diese Datei erst, wenn das HTML fertig
   eingelesen ist – alle Elemente existieren dann schon.
   ====================================================== */

(function () {
  'use strict';


  /* ────────────────────────────────────────────────────
     1. RUBRIK-FILTER (Übersichtsseite)

     Die Buttons werden aus den Karten selbst erzeugt: Jede
     Karte trägt data-rubrik="familie" und zeigt den Namen
     der Rubrik in .kultur-card-rubrik. Dadurch erscheint eine
     neue Rubrik automatisch im Filter, sobald es die erste
     Karte dazu gibt – im HTML muss dafür nichts gepflegt werden.

     Die Auswahl steht als ?rubrik=familie in der Adresszeile,
     damit man eine gefilterte Ansicht verlinken kann.
     ──────────────────────────────────────────────────── */
  function initFilter() {
    var leiste = document.querySelector('.kultur-filter');
    var karten = document.querySelectorAll('.kultur-grid .kultur-card');
    if (!leiste || !karten.length) return;

    // Rubriken in der Reihenfolge ihres ersten Auftretens einsammeln
    var rubriken = [];
    var namen = {};
    karten.forEach(function (karte) {
      var schluessel = karte.getAttribute('data-rubrik');
      var label = karte.querySelector('.kultur-card-rubrik');
      if (schluessel && !namen[schluessel]) {
        namen[schluessel] = label ? label.textContent.trim() : schluessel;
        rubriken.push(schluessel);
      }
    });

    // Bei nur einer Rubrik ist ein Filter sinnlos
    if (rubriken.length < 2) return;

    function knopf(schluessel, text) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'level-btn';
      btn.textContent = text;
      btn.setAttribute('data-rubrik', schluessel);
      btn.setAttribute('aria-pressed', 'false');
      btn.addEventListener('click', function () { anzeigen(schluessel, true); });
      leiste.appendChild(btn);
    }

    knopf('', 'Alle');
    rubriken.forEach(function (r) { knopf(r, namen[r]); });

    function anzeigen(rubrik, adresseMerken) {
      karten.forEach(function (karte) {
        var passt = !rubrik || karte.getAttribute('data-rubrik') === rubrik;
        karte.classList.toggle('hidden', !passt);
      });
      leiste.querySelectorAll('button').forEach(function (btn) {
        var aktiv = btn.getAttribute('data-rubrik') === rubrik;
        btn.classList.toggle('active', aktiv);
        btn.setAttribute('aria-pressed', aktiv ? 'true' : 'false');
      });
      if (adresseMerken && window.history && history.replaceState) {
        var url = new URL(window.location.href);
        if (rubrik) url.searchParams.set('rubrik', rubrik);
        else url.searchParams.delete('rubrik');
        history.replaceState(null, '', url);
      }
    }

    // Beim Laden: ?rubrik= aus der Adresszeile übernehmen (unbekannte
    // Werte verwerfen, statt eine leere Seite zu zeigen)
    var start = new URLSearchParams(window.location.search).get('rubrik') || '';
    if (rubriken.indexOf(start) === -1) start = '';
    leiste.classList.remove('hidden');
    anzeigen(start, false);
  }


  /* ────────────────────────────────────────────────────
     2. MINI-QUIZ (Beiträge)

     Die Fragen stehen im Beitrag als JSON:
       <script type="application/json" id="kulturQuizDaten">
         { "fragen": [ { "frage": "…", "optionen": ["…","…","…"],
                         "richtig": 1, "erklaerung": "…" }, … ],
           "ergebnis": { "top": "…", "gut": "…", "rest": "…" } }
       </script>

     Warum JSON und nicht wie bei der Grammatik ein JS-Array?
     In JSON sind Apostrophe (') unproblematisch, und ein Tippfehler
     zerstört nicht das ganze Skript – test_kultur_beitrag.py prüft
     die Daten vorab.

     Die IDs (quizContainer, quizQuestion, …) sind dieselben wie im
     Grammatik-Quiz. So kann LB_fortschritt.js die Kultur-Quizze
     später ohne Umbau mitzählen (siehe WORKFLOW_Kultur.md).
     ──────────────────────────────────────────────────── */
  function initQuiz() {
    var datenEl = document.getElementById('kulturQuizDaten');
    var box = document.getElementById('quizContainer');
    if (!datenEl || !box) return;

    var daten;
    try {
      daten = JSON.parse(datenEl.textContent);
    } catch (e) {
      // Kaputte Daten: Quiz-Bereich lieber ausblenden als halb anzeigen
      var bereich = box.closest('section');
      if (bereich) bereich.classList.add('hidden');
      return;
    }

    var fragen = daten.fragen || [];
    var texte = daten.ergebnis || {};
    if (!fragen.length) return;

    var el = {
      fortschritt: document.getElementById('quizProgress'),
      balken:      document.getElementById('quizBarFill'),
      frage:       document.getElementById('quizQuestion'),
      optionen:    document.getElementById('quizOptions'),
      feedback:    document.getElementById('quizFeedback'),
      weiter:      document.getElementById('quizNextBtn'),
      ergebnis:    document.getElementById('quizResult'),
      punkte:      document.getElementById('resultScore'),
      text:        document.getElementById('resultText'),
      nochmal:     document.getElementById('quizRetryBtn')
    };

    var aktuell = 0;
    var punkte = 0;
    var beantwortet = false;

    function frageZeigen() {
      var f = fragen[aktuell];
      el.fortschritt.textContent = 'Frage ' + (aktuell + 1) + ' von ' + fragen.length;
      el.balken.style.width = ((aktuell / fragen.length) * 100) + '%';
      el.frage.textContent = f.frage;

      el.optionen.innerHTML = '';
      f.optionen.forEach(function (text, i) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'quiz-option-btn';
        btn.textContent = text;
        btn.addEventListener('click', function () { pruefen(i); });
        el.optionen.appendChild(btn);
      });

      el.feedback.classList.add('hidden');
      el.weiter.classList.add('hidden');
      beantwortet = false;
    }

    function pruefen(gewaehlt) {
      if (beantwortet) return;          // Doppelklick verhindern
      beantwortet = true;

      var f = fragen[aktuell];
      var knoepfe = el.optionen.querySelectorAll('.quiz-option-btn');
      var richtig = gewaehlt === f.richtig;
      knoepfe[f.richtig].classList.add('correct');
      if (!richtig) knoepfe[gewaehlt].classList.add('wrong');
      if (richtig) punkte++;
      knoepfe.forEach(function (b) { b.disabled = true; });

      // Feedback per textContent zusammenbauen (kein innerHTML mit Text)
      el.feedback.innerHTML = '';
      var icon = document.createElement('i');
      icon.className = richtig ? 'fas fa-check-circle' : 'fas fa-times-circle';
      icon.setAttribute('aria-hidden', 'true');
      el.feedback.appendChild(icon);
      el.feedback.appendChild(document.createTextNode(
        (richtig ? 'Richtig! ' : 'Leider falsch. ') + f.erklaerung));
      el.feedback.className = 'quiz-feedback ' + (richtig ? 'feedback-correct' : 'feedback-wrong');

      if (aktuell < fragen.length - 1) {
        el.weiter.classList.remove('hidden');
        el.weiter.focus();
      } else {
        setTimeout(ergebnisZeigen, 1200);
      }
    }

    function ergebnisZeigen() {
      box.classList.add('hidden');
      el.ergebnis.classList.remove('hidden');
      el.punkte.textContent = punkte + ' von ' + fragen.length + ' richtig';

      // Grenzen relativ zur Fragenzahl, damit 4, 5 oder 6 Fragen gleich funktionieren
      var anteil = punkte / fragen.length;
      var text = anteil === 1 ? texte.top
               : anteil >= 0.6 ? texte.gut
               : texte.rest;
      el.text.textContent = text || '';
    }

    el.weiter.addEventListener('click', function () {
      aktuell++;
      frageZeigen();
      var erster = el.optionen.querySelector('button');
      if (erster) erster.focus();
    });

    el.nochmal.addEventListener('click', function () {
      aktuell = 0;
      punkte = 0;
      el.ergebnis.classList.add('hidden');
      box.classList.remove('hidden');
      frageZeigen();
    });

    frageZeigen();
  }


  initFilter();
  initQuiz();
})();
