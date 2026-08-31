/* ============================================================
   LB_fortschritt.js — Lernfortschritt von LinguaBosna
   ------------------------------------------------------------
   Merkt sich LOKAL im Browser, welche Vokabelkapitel geübt und
   welche Grammatikthemen gelesen/abgeschlossen wurden.

   Grundsätze:
   • Kein Backend, kein Cookie — nur localStorage des Besuchers.
     Die Daten verlassen das Gerät nie und werden nirgends gesendet.
   • JEDER Zugriff steckt in try/catch. Im privaten Modus oder bei
     abgeschaltetem Speicher wirft localStorage eine Ausnahme — dann
     verhält sich die Seite exakt so wie vor diesem Modul.
   • Ohne gespeicherte Daten wird NICHTS angezeigt und NICHTS verändert.

   Eingebunden wird die Datei von LB_main.js, läuft also auf jeder Seite.

   ------------------------------------------------------------
   DATENMODELL (ein einziger localStorage-Key)

   Key: "linguabosna.fortschritt"

   {
     "version": 1,
     "vokabeln": {
       "12": {                        // Schlüssel = Kapitelnummer
         "name": "Zahlen & Mengen",   // Gegenprobe, s. u.
         "zuletzt": "2026-08-31",     // ISO-Datum, ohne Uhrzeit
         "durchgaenge": 3             // abgeschlossene Lerneinheiten
       }
     },
     "grammatik": {
       "grammatik-perfekt.html": {    // Schlüssel = Dateiname
         "gelesen": true,
         "zuletzt": "2026-08-31",
         "quiz": { "punkte": 8, "max": 10, "am": "2026-08-31" }
       }
     }
   }

   Warum steht bei den Vokabeln der Kapitelname mit drin?
   Kapitelnummern sind im Projekt schon einmal global verschoben
   worden (August 2026). Ohne Gegenprobe würde ein gespeichertes
   "Kapitel 12 geübt" nach so einer Verschiebung am falschen Kapitel
   kleben. Stimmt der Name nicht mehr, wird der Eintrag ignoriert —
   lieber ein stiller Reset als eine falsche Anzeige.

   Warum "max" beim Quiz und nicht fest 10?
   Die meisten Grammatikseiten haben 10 Fragen, grammatik-alphabet.html
   aber nur 5. Gespeichert wird das jeweils BESTE Ergebnis.

   Die Versionsnummer erlaubt spätere Schema-Änderungen: dann wird
   SCHEMA_VERSION erhöht und in migrieren() der Umbau ergänzt.
   ============================================================ */

(function () {
  'use strict';

  // ── Konstanten ────────────────────────────────────────────
  var SPEICHER_KEY   = 'linguabosna.fortschritt';
  var SCHEMA_VERSION = 1;

  // Ab diesem Anteil richtiger Antworten gilt ein Grammatik-Quiz
  // als bestanden (0.7 = 70 %, also z. B. 7 von 10).
  var QUIZ_SCHWELLE = 0.7;


  /* ==========================================================
     1. SPEICHER-GRUNDLAGEN
     ========================================================== */

  // Frisches, leeres Modell — auch der Rückfallwert, wenn der
  // Speicher nicht lesbar ist. So arbeitet der Rest des Codes
  // immer mit einem gültigen Objekt und muss nie auf null prüfen.
  function leeresModell() {
    return { version: SCHEMA_VERSION, vokabeln: {}, grammatik: {} };
  }

  // Ist localStorage überhaupt benutzbar? (Privater Modus, iOS mit
  // gesperrtem Speicher, Browser-Einstellung …) Wir probieren es
  // einmal aus und merken uns das Ergebnis.
  var speicherOk = null;
  function verfuegbar() {
    if (speicherOk !== null) return speicherOk;
    try {
      var probe = '__lb_probe__';
      window.localStorage.setItem(probe, '1');
      window.localStorage.removeItem(probe);
      speicherOk = true;
    } catch (e) {
      speicherOk = false;
    }
    return speicherOk;
  }

  // Gespeicherten Stand lesen. Liefert IMMER ein gültiges Objekt.
  function laden() {
    if (!verfuegbar()) return leeresModell();
    try {
      var roh = window.localStorage.getItem(SPEICHER_KEY);
      if (!roh) return leeresModell();

      var daten = JSON.parse(roh);
      if (!daten || typeof daten !== 'object') return leeresModell();

      return migrieren(daten);
    } catch (e) {
      // Kaputtes JSON o. Ä. — lieber neu anfangen als abstürzen.
      return leeresModell();
    }
  }

  // Stand zurückschreiben. Gibt true/false zurück, damit Aufrufer
  // reagieren können (z. B. der Löschen-Button auf der Datenschutzseite).
  function speichern(daten) {
    if (!verfuegbar()) return false;
    try {
      daten.version = SCHEMA_VERSION;
      window.localStorage.setItem(SPEICHER_KEY, JSON.stringify(daten));
      return true;
    } catch (e) {
      // Kann auch bei vollem Speicher (QuotaExceeded) passieren.
      return false;
    }
  }

  // Alten Stand auf das aktuelle Schema bringen. Aktuell gibt es
  // nur Version 1 — die Funktion sorgt hier vor allem dafür, dass
  // die beiden Unterobjekte garantiert existieren. Kommt später
  // Version 2, wird hier von 1 nach 2 umgebaut.
  function migrieren(daten) {
    if (!daten.vokabeln  || typeof daten.vokabeln  !== 'object') daten.vokabeln  = {};
    if (!daten.grammatik || typeof daten.grammatik !== 'object') daten.grammatik = {};
    daten.version = SCHEMA_VERSION;
    return daten;
  }

  // Heutiges Datum als "YYYY-MM-DD" (lokale Zeit, ohne Uhrzeit).
  function heute() {
    var d = new Date();
    var m = String(d.getMonth() + 1).padStart(2, '0');
    var t = String(d.getDate()).padStart(2, '0');
    return d.getFullYear() + '-' + m + '-' + t;
  }

  // "2026-08-31" → "31.08.2026" (nur für Tooltips)
  function datumDE(iso) {
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || '');
    return m ? m[3] + '.' + m[2] + '.' + m[1] : '';
  }


  /* ==========================================================
     2. SCHREIBEN & LESEN (öffentliche Funktionen)
     ========================================================== */

  // Eine abgeschlossene Lerneinheit im Vokabeltrainer verbuchen.
  // kapitelname ist optional, sollte aber mitgegeben werden — er
  // dient als Gegenprobe gegen verschobene Kapitelnummern.
  function vokabelDurchgang(kapitel, kapitelname) {
    var key   = String(kapitel);
    var daten = laden();
    var alt   = daten.vokabeln[key];

    // Passt der gespeicherte Name nicht mehr zum Kapitel, wurde die
    // Nummer neu vergeben → alten Zählerstand verwerfen.
    if (alt && alt.name && kapitelname && alt.name !== kapitelname) {
      alt = null;
    }

    daten.vokabeln[key] = {
      name:        kapitelname || (alt && alt.name) || '',
      zuletzt:     heute(),
      durchgaenge: ((alt && alt.durchgaenge) || 0) + 1
    };
    return speichern(daten);
  }

  // Gespeicherten Stand eines Vokabelkapitels holen.
  // kapitelname optional: stimmt er nicht überein, wird null
  // geliefert (Kapitelnummer wurde offenbar neu vergeben).
  function vokabelStatus(kapitel, kapitelname) {
    var eintrag = laden().vokabeln[String(kapitel)];
    if (!eintrag) return null;
    if (eintrag.name && kapitelname && eintrag.name !== kapitelname) return null;
    return eintrag;
  }

  // Grammatikthema als gelesen markieren.
  function grammatikGelesen(datei) {
    var daten   = laden();
    var eintrag = daten.grammatik[datei] || {};
    eintrag.gelesen = true;
    eintrag.zuletzt = heute();
    daten.grammatik[datei] = eintrag;
    return speichern(daten);
  }

  // Quiz-Ergebnis eines Grammatikthemas verbuchen.
  // Gespeichert wird nur das BESTE Ergebnis (nach Prozentanteil),
  // damit eine misslungene Wiederholung nichts kaputtmacht.
  function grammatikQuiz(datei, punkte, max) {
    if (!max || max < 1) return false;

    var daten   = laden();
    var eintrag = daten.grammatik[datei] || {};
    var alt     = eintrag.quiz;
    var neuPct  = punkte / max;

    if (!alt || !alt.max || neuPct > (alt.punkte / alt.max)) {
      eintrag.quiz = { punkte: punkte, max: max, am: heute() };
    }
    eintrag.gelesen = true;      // wer das Quiz macht, hat die Seite gesehen
    eintrag.zuletzt = heute();
    daten.grammatik[datei] = eintrag;
    return speichern(daten);
  }

  function grammatikStatus(datei) {
    return laden().grammatik[datei] || null;
  }

  // Gilt das Quiz eines Themas als bestanden?
  function quizBestanden(eintrag) {
    return !!(eintrag && eintrag.quiz && eintrag.quiz.max &&
              (eintrag.quiz.punkte / eintrag.quiz.max) >= QUIZ_SCHWELLE);
  }

  // Kurzübersicht — für die Anzeige auf der Datenschutzseite.
  function zusammenfassung() {
    var daten = laden();
    var kapitel = Object.keys(daten.vokabeln);
    var themen  = Object.keys(daten.grammatik);
    var runden  = 0;
    var quizzes = 0;

    kapitel.forEach(function (k) {
      runden += daten.vokabeln[k].durchgaenge || 0;
    });
    themen.forEach(function (t) {
      if (quizBestanden(daten.grammatik[t])) quizzes++;
    });

    return {
      vokabelkapitel:  kapitel.length,
      durchgaenge:     runden,
      grammatikthemen: themen.length,
      quizBestanden:   quizzes,
      leer:            kapitel.length === 0 && themen.length === 0
    };
  }

  // Kompletten Fortschritt löschen (nur unser eigener Key).
  function alleLoeschen() {
    if (!verfuegbar()) return false;
    try {
      window.localStorage.removeItem(SPEICHER_KEY);
      return true;
    } catch (e) {
      return false;
    }
  }


  /* ==========================================================
     3. KLEINE HELFER
     ========================================================== */

  // "/Code/3_Grammatik/Grammatik_B1/grammatik-perfekt.html?x=1"
  //   → "grammatik-perfekt.html"
  function dateiname(pfad) {
    var ohneAnhang = (pfad || '').split('?')[0].split('#')[0];
    var stuecke    = ohneAnhang.split('/');
    try {
      return decodeURIComponent(stuecke[stuecke.length - 1] || '');
    } catch (e) {
      return stuecke[stuecke.length - 1] || '';
    }
  }

  // Kapitelnummer aus einem Link wie "…?kapitel=12" herausziehen.
  function kapitelAusHref(href) {
    var treffer = /[?&]kapitel=(\d+)/.exec(href || '');
    return treffer ? treffer[1] : null;
  }

  // Erst laufen lassen, wenn das DOM steht. Diese Datei wird von
  // LB_main.js nachgeladen und kann daher vor ODER nach dem
  // fertigen DOM ankommen — beide Fälle sind hier abgedeckt.
  function wennDomBereit(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else {
      fn();
    }
  }

  // Haken-Plakette bauen.
  //   art:   'gelesen' (grau) oder 'geuebt' (grün)
  //   kurz:  Text für Screenreader
  //   titel: Tooltip mit den Details
  // Bewusst ohne innerHTML zusammengesetzt, damit Texte aus dem
  // Speicher niemals als HTML interpretiert werden können.
  function hakenBadge(art, kurz, titel) {
    var span = document.createElement('span');
    span.className = 'lb-haken lb-haken-' + art;
    if (titel) span.setAttribute('title', titel);

    var icon = document.createElement('i');
    icon.className = 'fa-solid fa-check';
    icon.setAttribute('aria-hidden', 'true');

    var sr = document.createElement('span');
    sr.className   = 'lb-sr-only';
    sr.textContent = kurz;

    span.appendChild(icon);
    span.appendChild(sr);
    return span;
  }


  /* ==========================================================
     4. AUTOMATISCHE ERFASSUNG AUF GRAMMATIK-DETAILSEITEN

     Die 37 Grammatikseiten werden NICHT einzeln angefasst. Alle
     benutzen laut WORKFLOW_Grammatikseiten.md dieselben, fest
     eingefrorenen Quiz-IDs (quizContainer, quizResult, resultScore).
     Deshalb genügt dieser eine zentrale Block — und jede künftige
     Seite aus dem Template wird automatisch mit erfasst.
     ========================================================== */

  function initGrammatikSeite() {
    // Nur auf echten Grammatik-Detailseiten arbeiten.
    if (window.location.pathname.indexOf('/Code/3_Grammatik/') === -1) return;

    var datei = dateiname(window.location.pathname);
    if (!/^grammatik-.+\.html$/.test(datei)) return;

    // ── (a) "gelesen" ──────────────────────────────────────
    // Gesetzt, sobald der Übungsteil (Block 5 von 6) ins Bild
    // kommt — wer so weit gescrollt hat, hat die Lektion
    // durchgesehen. Das bloße Öffnen der Seite reicht nicht.
    var quizBox = document.getElementById('quizContainer');
    if (quizBox && window.IntersectionObserver) {
      var io = new IntersectionObserver(function (eintraege) {
        eintraege.forEach(function (e) {
          if (e.isIntersecting) {
            grammatikGelesen(datei);
            io.disconnect();          // einmal genügt
          }
        });
      }, { threshold: 0.2 });
      io.observe(quizBox);
    } else if (quizBox) {
      // Sehr alter Browser ohne IntersectionObserver: dann eben
      // direkt beim Laden markieren.
      grammatikGelesen(datei);
    }

    // ── (b) Quiz-Ergebnis ──────────────────────────────────
    // Die Seiten blenden das Ergebnis ein, indem sie die Klasse
    // "hidden" von #quizResult entfernen. Genau darauf hören wir.
    // Der Punktestand steht als "8 von 10 richtig" in #resultScore.
    var ergebnisBox = document.getElementById('quizResult');
    if (ergebnisBox && window.MutationObserver) {
      var mo = new MutationObserver(function () {
        if (ergebnisBox.classList.contains('hidden')) return;   // wieder versteckt
        var anzeige = document.getElementById('resultScore');
        if (!anzeige) return;
        var m = /(\d+)\s*von\s*(\d+)/.exec(anzeige.textContent || '');
        if (m) {
          grammatikQuiz(datei, parseInt(m[1], 10), parseInt(m[2], 10));
        }
      });
      mo.observe(ergebnisBox, { attributes: true, attributeFilter: ['class'] });
    }
  }


  /* ==========================================================
     5. MARKIERUNG DER KARTEN AUF DEN ÜBERSICHTSSEITEN

     Läuft ebenfalls zentral hier, damit LB_2_Vokabeln.html und
     LB_3_Grammatik.html unverändert bleiben. Ohne gespeicherten
     Fortschritt passiert hier gar nichts.
     ========================================================== */

  // ── Vokabel-Übersicht: Kapitelkarten ──────────────────────
  function markiereVokabelkarten() {
    var karten = document.querySelectorAll('a.vocab-card');
    if (!karten.length) return;

    var daten = laden();

    karten.forEach(function (karte) {
      if (karte.querySelector('.lb-haken')) return;      // schon markiert

      var kapitel = kapitelAusHref(karte.getAttribute('href'));
      if (!kapitel) return;

      var eintrag = daten.vokabeln[kapitel];
      if (!eintrag || !eintrag.durchgaenge) return;      // nie geübt → nichts tun

      // Gegenprobe: Steht hinter der Nummer noch dasselbe Kapitel?
      var titelEl = karte.querySelector('.vocab-card-title');
      var name    = titelEl ? titelEl.textContent.trim() : '';
      if (eintrag.name && name && eintrag.name !== name) return;

      var runden = eintrag.durchgaenge;
      var titel  = 'Zuletzt geübt am ' + datumDE(eintrag.zuletzt) +
                   ' · ' + runden + ' Lerneinheit' + (runden === 1 ? '' : 'en');

      karte.classList.add('lb-geuebt');
      var kreis = karte.querySelector('.vocab-card-icon') || karte;
      kreis.appendChild(hakenBadge('geuebt', 'bereits geübt', titel));
    });
  }

  // ── Grammatik-Übersicht: Themenkarten ─────────────────────
  function markiereGrammatikkarten() {
    var karten = document.querySelectorAll('a.grammar-card');
    if (!karten.length) return;

    var daten = laden();

    karten.forEach(function (karte) {
      if (karte.classList.contains('coming-soon')) return;   // noch nicht fertig
      if (karte.querySelector('.lb-haken')) return;          // schon markiert

      var datei   = dateiname(karte.getAttribute('href'));
      var eintrag = daten.grammatik[datei];
      if (!eintrag) return;

      if (quizBestanden(eintrag)) {
        // Grüner Haken: Quiz mit mindestens 70 % bestanden
        var titel = 'Quiz: ' + eintrag.quiz.punkte + ' von ' + eintrag.quiz.max +
                    ' richtig (' + datumDE(eintrag.quiz.am) + ')';
        karte.classList.add('lb-quiz-ok');
        karte.appendChild(hakenBadge('geuebt', 'Quiz bestanden', titel));

      } else if (eintrag.gelesen) {
        // Grauer Haken: gelesen, Quiz noch offen oder unter 70 %
        var hinweis = 'Zuletzt gelesen am ' + datumDE(eintrag.zuletzt);
        if (eintrag.quiz) {
          hinweis += ' · Quiz: ' + eintrag.quiz.punkte + ' von ' + eintrag.quiz.max;
        }
        karte.classList.add('lb-gelesen');
        karte.appendChild(hakenBadge('gelesen', 'bereits gelesen', hinweis));
      }
    });
  }

  // Beide Übersichten markieren.
  function markiereKarten() {
    markiereVokabelkarten();
    markiereGrammatikkarten();
  }


  /* ==========================================================
     6. START
     ========================================================== */

  wennDomBereit(function () {
    initGrammatikSeite();
    markiereKarten();

    // Die Vokabelkarten entstehen erst, nachdem vokabeln_flat.json
    // geladen ist — je nach Netz also VOR oder NACH dieser Datei.
    // Deshalb zusätzlich beobachten, ob im Kartenbereich etwas
    // Neues auftaucht, und dann erneut markieren. markiereKarten()
    // überspringt bereits markierte Karten, doppelt kann nichts werden.
    var gridWrap = document.getElementById('levelGrids');
    if (gridWrap && window.MutationObserver) {
      new MutationObserver(function () {
        markiereVokabelkarten();
      }).observe(gridWrap, { childList: true, subtree: true });
    }
  });


  /* ==========================================================
     7. ÖFFENTLICHE SCHNITTSTELLE

     Andere Seiten benutzen das Modul über window.LBFortschritt.
     Weil diese Datei von LB_main.js NACHGELADEN wird, kann sie
     beim Ausführen einer Seite noch fehlen. Zwei Muster:

     a) Reaktion auf einen Klick / späteres Ereignis:
          if (window.LBFortschritt) window.LBFortschritt.…

     b) Direkt beim Seitenaufbau (z. B. eine Übersicht anzeigen):
          function wennBereit(fn) {
            if (window.LBFortschritt) fn(window.LBFortschritt);
            else document.addEventListener('lb-fortschritt-bereit',
                   function () { fn(window.LBFortschritt); });
          }
     ========================================================== */

  window.LBFortschritt = {
    verfuegbar:       verfuegbar,
    laden:            laden,
    vokabelDurchgang: vokabelDurchgang,
    vokabelStatus:    vokabelStatus,
    grammatikGelesen: grammatikGelesen,
    grammatikQuiz:    grammatikQuiz,
    grammatikStatus:  grammatikStatus,
    quizBestanden:    quizBestanden,
    zusammenfassung:  zusammenfassung,
    alleLoeschen:     alleLoeschen,
    markiereKarten:   markiereKarten
  };

  // Signal für Seiten, die das Modul direkt beim Laden brauchen.
  try {
    document.dispatchEvent(new CustomEvent('lb-fortschritt-bereit'));
  } catch (e) {
    // Sehr alte Browser kennen CustomEvent nicht — window.LBFortschritt
    // steht trotzdem, nur das Ereignis entfällt.
  }

})();
