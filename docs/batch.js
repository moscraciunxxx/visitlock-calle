/**
 * VisitLock — client-side fixture batch loop (Gate A / Pages HUD).
 * No API key, no .env. Replays embedded board-data / board.json.
 */
(function () {
  "use strict";

  var BADGE = {
    yes: "ok",
    no: "bad",
    reschedule: "warn",
    no_answer: "mute",
    queued: "mute",
    calling: "mute",
    unknown: "mute",
  };

  var STEP_MS = 720;
  var CALLING_MS = 380;
  var board = null;
  var running = false;

  function $(id) {
    return document.getElementById(id);
  }

  function prefersReducedMotion() {
    return (
      window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    );
  }

  function sleep(ms) {
    if (prefersReducedMotion()) ms = Math.min(ms, 80);
    return new Promise(function (resolve) {
      setTimeout(resolve, ms);
    });
  }

  function setStatus(state, text) {
    var wrap = $("batch-status");
    var label = $("batch-status-text");
    if (wrap) wrap.setAttribute("data-state", state || "idle");
    if (label) label.textContent = text || "";
  }

  function tickMetric(el) {
    if (!el) return;
    el.classList.remove("tick");
    // force reflow for restart
    void el.offsetWidth;
    el.classList.add("tick");
    window.setTimeout(function () {
      el.classList.remove("tick");
    }, 220);
  }

  function badgeClass(status) {
    return BADGE[status] || "mute";
  }

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function parseEmbedded() {
    var el = $("board-data");
    if (!el) return null;
    try {
      return JSON.parse(el.textContent);
    } catch (err) {
      return null;
    }
  }

  function loadBoard() {
    return fetch("board.json", { cache: "no-store" })
      .then(function (res) {
        if (!res.ok) throw new Error("board.json " + res.status);
        return res.json();
      })
      .catch(function () {
        return parseEmbedded();
      });
  }

  function aggregate(results) {
    var called = results.length;
    var confirmed = 0;
    var reschedule = 0;
    for (var i = 0; i < results.length; i++) {
      var st = results[i].visit_status;
      if (st === "yes") confirmed += 1;
      if (st === "reschedule") reschedule += 1;
    }
    var rate = called ? Math.round((confirmed / called) * 1000) / 10 : 0;
    return {
      confirmed: confirmed,
      called: called,
      confirmation_rate: rate,
      reschedule_count: reschedule,
    };
  }

  function setMetrics(m, risk) {
    var cc = $("confirmed-called");
    var rate = $("confirmation-rate");
    var rs = $("reschedule-count");
    var nsr = $("no-show-risk");
    if (cc) {
      cc.textContent = m.confirmed + " / " + m.called;
      tickMetric(cc);
    }
    if (rate) {
      if (typeof m.confirmation_rate === "number") {
        var rv = m.confirmation_rate;
        rate.textContent =
          (Math.round(rv) === rv ? String(Math.round(rv)) : rv.toFixed(1)) + "%";
      } else {
        rate.textContent = String(m.confirmation_rate);
      }
      tickMetric(rate);
    }
    if (rs) {
      rs.textContent = String(m.reschedule_count);
      tickMetric(rs);
    }
    if (nsr && risk != null && risk !== "") {
      if (typeof risk === "number") {
        nsr.textContent =
          Math.round(risk) === risk ? String(Math.round(risk)) : risk.toFixed(1);
      } else {
        nsr.textContent = String(risk);
      }
      tickMetric(nsr);
    }
  }

  function rowCells(r, statusOverride) {
    var status = statusOverride || r.visit_status || "unknown";
    var slot = r.preferred_slot ? esc(r.preferred_slot) : "—";
    var notes = status === "queued" || status === "calling" ? "—" : esc(r.notes || "");
    if (status === "calling") notes = "Dialing…";
    if (status === "queued") notes = "Waiting in batch";
    return (
      "<td>" +
      esc(r.participant_id) +
      "</td>" +
      "<td>" +
      esc(r.name) +
      "</td>" +
      "<td>" +
      esc(r.visit_datetime) +
      "</td>" +
      "<td><span class='badge " +
      badgeClass(status) +
      "'>" +
      esc(status) +
      "</span></td>" +
      "<td>" +
      (status === "queued" || status === "calling" ? "—" : slot) +
      "</td>" +
      "<td>" +
      notes +
      "</td>"
    );
  }

  function ensureRows(results) {
    var body = $("ledger-body");
    if (!body) return;
    if (!results || !results.length) {
      body.innerHTML =
        '<tr><td class="ledger-empty" colspan="6">No participants in this fixture batch.</td></tr>';
      return;
    }
    var html = "";
    for (var i = 0; i < results.length; i++) {
      var r = results[i];
      html +=
        '<tr data-participant-id="' +
        esc(r.participant_id) +
        '">' +
        rowCells(r, r.visit_status) +
        "</tr>";
    }
    body.innerHTML = html;
  }

  function findRow(pid) {
    var body = $("ledger-body");
    if (!body) return null;
    return body.querySelector('[data-participant-id="' + pid + '"]');
  }

  function paintRow(r, status, settle) {
    var tr = findRow(r.participant_id);
    if (!tr) return;
    tr.classList.remove("calling", "just-settled", "vl-focus", "demo-hl");
    if (status === "calling") tr.classList.add("calling");
    tr.innerHTML = rowCells(r, status);
    if (settle) {
      tr.classList.add("just-settled");
      window.setTimeout(function () {
        tr.classList.remove("just-settled");
      }, 600);
    }
  }

  function resetQueued(results) {
    for (var i = 0; i < results.length; i++) {
      paintRow(results[i], "queued", false);
    }
    setMetrics(
      { confirmed: 0, called: 0, confirmation_rate: 0, reschedule_count: 0 },
      "—"
    );
  }

  function settleFinal(results) {
    var m = aggregate(results);
    var risk =
      board && board.matlab && board.matlab.no_show_risk != null
        ? board.matlab.no_show_risk
        : null;
    for (var i = 0; i < results.length; i++) {
      paintRow(results[i], results[i].visit_status, false);
    }
    setMetrics(m, risk);
  }

  function setRunning(isRunning) {
    running = isRunning;
    var btn = $("run-batch");
    if (!btn) return;
    btn.disabled = isRunning || !board;
    btn.setAttribute("aria-busy", isRunning ? "true" : "false");
    if (isRunning) {
      btn.textContent = "Running…";
    } else if (board) {
      btn.textContent = "Replay batch";
    }
  }

  function runBatch() {
    if (running || !board) return;
    var results = board.results || [];
    if (!results.length) {
      setStatus("error", "Empty fixture — nothing to confirm.");
      ensureRows([]);
      return;
    }

    setRunning(true);
    resetQueued(results);
    setStatus("running", "Starting batch…");

    var settled = [];

    (async function () {
      try {
        for (var i = 0; i < results.length; i++) {
          var r = results[i];
          var pid = r.participant_id || "P???";
          setStatus("running", "Calling " + pid + "…");
          paintRow(r, "calling", false);
          await sleep(CALLING_MS);

          settled.push(r);
          paintRow(r, r.visit_status, true);
          setMetrics(aggregate(settled), "—");
          setStatus(
            "running",
            "Logged " + pid + " → " + (r.visit_status || "unknown")
          );
          await sleep(STEP_MS);
        }

        settleFinal(results);
        var m = aggregate(results);
        setStatus(
          "done",
          "Batch complete — " +
            m.confirmed +
            "/" +
            m.called +
            " confirmed (" +
            m.confirmation_rate.toFixed(1) +
            "%). Ledger updated."
        );
      } catch (err) {
        setStatus("error", "Batch interrupted. Reload and try again.");
        settleFinal(results);
      } finally {
        setRunning(false);
      }
    })();
  }

  function wire() {
    var btn = $("run-batch");
    if (btn) {
      btn.addEventListener("click", function () {
        runBatch();
      });
    }
  }

  function boot() {
    wire();
    loadBoard().then(function (data) {
      board = data;
      var btn = $("run-batch");
      if (!board || !Array.isArray(board.results)) {
        setStatus(
          "error",
          "Could not load fixture board. Check board.json / embedded data."
        );
        if (btn) {
          btn.disabled = true;
          btn.textContent = "Run batch";
        }
        return;
      }
      // Keep SSR/static scoreboard; ensure rows have data attrs for replay.
      ensureRows(board.results);
      settleFinal(board.results);
      if (btn) {
        btn.disabled = false;
        btn.textContent = "Run batch";
      }
      setStatus(
        "idle",
        "Fixture ready — simulate confirmations without an API key."
      );
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
