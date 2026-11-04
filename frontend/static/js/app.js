/* Client-side behaviour: accessibility settings, format tabs, quiz submission,
   text-to-speech, speech-to-text and the tutor widget. */
(function () {
  "use strict";

  const KEY = "adaptivelearn-a11y";
  const DEFAULTS = {
    dyslexia_font: false, font_scale: 1.0, high_contrast: false, reduced_motion: false,
    focus_mode: false, tts_enabled: false, preferred_format: "text",
  };
  const body = document.body;
  const loggedIn = body.dataset.loggedIn === "true";

  // Let learners narrow the library without a page reload.
  const libraryCards = Array.from(document.querySelectorAll("[data-topic-card]"));
  if (libraryCards.length) {
    const search = document.getElementById("library-search");
    const subjectFilter = document.getElementById("subject-filter");
    const statusFilter = document.getElementById("status-filter");
    const resultCount = document.getElementById("library-result-count");
    const emptyState = document.getElementById("library-empty");
    const sections = Array.from(document.querySelectorAll(".library-subject"));

    function filterLibrary() {
      const query = search.value.trim().toLowerCase();
      const subject = subjectFilter.value;
      const status = statusFilter.value;
      let visible = 0;
      libraryCards.forEach(function (card) {
        const show = card.dataset.search.includes(query)
          && (!subject || card.dataset.subject === subject)
          && (!status || card.dataset.status === status);
        card.hidden = !show;
        if (show) visible += 1;
      });
      sections.forEach(function (section) {
        section.hidden = !section.querySelector("[data-topic-card]:not([hidden])");
      });
      resultCount.textContent = visible + (visible === 1 ? " topic found" : " topics found");
      emptyState.hidden = visible !== 0;
    }

    search.addEventListener("input", filterLibrary);
    subjectFilter.addEventListener("change", filterLibrary);
    statusFilter.addEventListener("change", filterLibrary);
    filterLibrary();
  }

  function loadLocal() {
    try {
      return Object.assign({}, DEFAULTS, JSON.parse(localStorage.getItem(KEY) || "{}"));
    } catch (e) {
      return Object.assign({}, DEFAULTS);
    }
  }

  function applySettings(s) {
    body.classList.toggle("dyslexia-font", !!s.dyslexia_font);
    body.classList.toggle("high-contrast", !!s.high_contrast);
    body.classList.toggle("reduced-motion", !!s.reduced_motion);
    body.classList.toggle("focus-mode", !!s.focus_mode);
    document.documentElement.style.fontSize = (Number(s.font_scale) || 1) * 100 + "%";
  }

  function readForm() {
    const s = Object.assign({}, DEFAULTS);
    document.querySelectorAll("[data-setting]").forEach(function (el) {
      s[el.dataset.setting] = el.type === "checkbox" ? el.checked : el.value;
    });
    s.font_scale = parseFloat(s.font_scale) || 1.0;
    return s;
  }

  function fillForm(s) {
    document.querySelectorAll("[data-setting]").forEach(function (el) {
      const v = s[el.dataset.setting];
      if (el.type === "checkbox") el.checked = !!v; else el.value = String(v);
    });
  }

  function saveSettings(s) {
    localStorage.setItem(KEY, JSON.stringify(s));
    applySettings(s);
    if (loggedIn) {
      fetch("/api/accessibility", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(s),
      }).catch(function () { /* offline: the browser copy still applies */ });
    }
  }

  // Anonymous visitors: apply saved browser settings. Logged-in users get server-rendered classes.
  if (!loggedIn) applySettings(loadLocal());

  // Settings page wiring
  if (document.querySelector("[data-setting]")) {
    if (!loggedIn) fillForm(loadLocal());
    document.querySelectorAll("[data-setting]").forEach(function (el) {
      el.addEventListener("change", function () { saveSettings(readForm()); });
    });
    const reset = document.querySelector("[data-reset]");
    if (reset) reset.addEventListener("click", function () {
      fillForm(DEFAULTS);
      saveSettings(Object.assign({}, DEFAULTS));
    });
  }

  // Text-to-speech (Web Speech API)
  function speak(text) {
    if (!("speechSynthesis" in window)) {
      alert("Text-to-speech is not supported in this browser.");
      return;
    }
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 0.95;
    window.speechSynthesis.speak(u);
  }
  document.addEventListener("click", function (e) {
    const btn = e.target.closest("[data-speak-target]");
    if (!btn) return;
    const target = document.querySelector(btn.dataset.speakTarget);
    if (target) speak(target.textContent.trim());
  });

  // Speech-to-text (where supported)
  document.querySelectorAll("[data-stt]").forEach(function (btn) {
    const Rec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Rec) {
      btn.disabled = true;
      btn.title = "Speech input is not supported in this browser";
      return;
    }
    btn.addEventListener("click", function () {
      const rec = new Rec();
      rec.lang = "en-US";
      rec.onresult = function (ev) {
        document.getElementById(btn.dataset.stt).value = ev.results[0][0].transcript;
      };
      rec.start();
    });
  });

  // Format tabs (text / audio / visual)
  const activeTab = document.querySelector("[data-format-tab].active");
  let currentFormat = activeTab ? activeTab.dataset.formatTab : "text";
  document.querySelectorAll("[data-format-tab]").forEach(function (tab) {
    tab.addEventListener("click", function () {
      currentFormat = tab.dataset.formatTab;
      document.querySelectorAll("[data-format-tab]").forEach(function (t) {
        const on = t === tab;
        t.classList.toggle("active", on);
        t.setAttribute("aria-pressed", on ? "true" : "false");
      });
      document.querySelectorAll("[data-format-panel]").forEach(function (p) {
        p.hidden = p.dataset.formatPanel !== currentFormat;
      });
    });
  });

  // Quiz submission
  document.querySelectorAll(".quiz-q").forEach(function (q) { q.dataset.start = Date.now(); });
  let answeredQuestions = 0;
  let correctQuestions = 0;
  const quizSection = document.getElementById("quiz-section");
  const quizTotal = quizSection ? Number(quizSection.dataset.totalQuestions) : 0;
  document.querySelectorAll(".quiz-option").forEach(function (btn) {
    btn.addEventListener("click", async function () {
      const card = btn.closest(".quiz-q");
      if (card.dataset.answered === "true" || card.dataset.submitting === "true") return;
      const feedback = card.querySelector(".quiz-feedback");
      const timeTaken = (Date.now() - Number(card.dataset.start)) / 1000;
      card.dataset.submitting = "true";
      card.querySelectorAll(".quiz-option").forEach(function (option) { option.disabled = true; });
      try {
        const res = await fetch("/api/quiz/" + card.dataset.qid + "/submit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ selected: btn.dataset.answer, time_taken: timeTaken, format_used: currentFormat }),
        });
        if (res.status === 401) {
          feedback.textContent = "Please log in to save your progress.";
          card.dataset.submitting = "false";
          card.querySelectorAll(".quiz-option").forEach(function (option) { option.disabled = false; });
          return;
        }
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Request failed");

        card.dataset.answered = "true";
        card.dataset.submitting = "false";
        answeredQuestions += 1;
        if (data.correct) correctQuestions += 1;
        card.querySelectorAll(".quiz-option").forEach(function (b) {
          if (b.dataset.answer === data.correct_answer) b.classList.add("btn-success");
          else if (b === btn) b.classList.add("btn-danger");
        });
        feedback.textContent = (data.correct ? "Correct. " : "Not quite. The correct answer is: " + data.correct_answer + ". ")
          + (data.explanation || "");
        const status = document.getElementById("topic-status");
        if (status) {
          status.textContent = "Topic status: " + String(data.status).replace(/_/g, " ")
            + " · mastery " + Math.round(data.mastery * 100) + "%";
        }
        const progress = document.getElementById("quiz-progress-bar");
        const progressTrack = progress && progress.parentElement;
        if (progress && progressTrack) {
          progress.style.width = (answeredQuestions / quizTotal * 100) + "%";
          progressTrack.setAttribute("aria-valuenow", String(answeredQuestions));
          document.getElementById("quiz-progress-label").textContent =
            answeredQuestions + " of " + quizTotal + " answered";
          document.getElementById("quiz-score").textContent = "Score: " + correctQuestions;
        }
        if (answeredQuestions === quizTotal && quizTotal > 0) {
          const complete = document.getElementById("quiz-complete");
          complete.textContent = "Practice complete: " + correctQuestions + " of " + quizTotal + " correct.";
          complete.hidden = false;
        }
      } catch (err) {
        feedback.textContent = "Something went wrong. Please try again. (" + err.message + ")";
        card.dataset.submitting = "false";
        card.querySelectorAll(".quiz-option").forEach(function (option) { option.disabled = false; });
      }
    });
  });

  // Tutor widget
  const tutorForm = document.getElementById("tutor-form");
  if (tutorForm) {
    tutorForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      const input = document.getElementById("tutor-input");
      const out = document.getElementById("tutor-reply");
      const question = input.value.trim();
      if (!question) return;
      out.textContent = "Looking that up…";
      try {
        const res = await fetch("/api/tutor", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: question }),
        });
        const data = await res.json();
        out.textContent = data.reply || data.error || "No answer available.";
      } catch (err) {
        out.textContent = "The assistant is unavailable right now.";
      }
    });
  }
})();
