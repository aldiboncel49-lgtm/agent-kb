/* agent-kb: app.js */
(function () {
  "use strict";

  // --- Navigation ---
  function showView(name) {
    document.querySelectorAll(".view").forEach(function (v) { v.classList.remove("active"); });
    document.querySelectorAll(".nav-item").forEach(function (n) { n.classList.remove("active"); });
    var view = document.getElementById("view-" + name);
    if (view) view.classList.add("active");
    var nav = document.querySelector('[data-view="' + name + '"]');
    if (nav) nav.classList.add("active");
    if (name === "stats") loadStats();
    if (name === "browse") loadDocs();
  }

  document.querySelectorAll(".nav-item").forEach(function (item) {
    item.addEventListener("click", function (e) {
      e.preventDefault();
      showView(this.dataset.view);
    });
  });

  // --- Search ---
  var searchForm = document.getElementById("search-form");
  var searchInput = document.getElementById("search-input");
  var resultsDiv = document.getElementById("results");

  if (searchForm) {
    searchForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var q = searchInput.value.trim();
      if (!q) return;
      resultsDiv.innerHTML = '<p style="color:var(--text2)">Searching...</p>';
      fetch("/api/search?q=" + encodeURIComponent(q) + "&limit=10")
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data.error) {
            resultsDiv.innerHTML = '<p class="result-msg err">' + esc(data.error) + '</p>';
            return;
          }
          if (!data.results || data.results.length === 0) {
            resultsDiv.innerHTML = '<p style="color:var(--text2)">No results found.</p>';
            return;
          }
          resultsDiv.innerHTML = data.results.map(function (r) {
            var title = r.title || "Untitled";
            var source = r.source || "";
            var snippet = r.content || r.snippet || "";
            var score = r.score ? "score: " + r.score : "";
            var type = r.source_type || "";
            var badge = '<span class="badge badge-' + type + '">' + type + '</span>';
            var link = r.url ? '<a href="' + esc(r.url) + '" target="_blank">' + esc(title) + '</a>' : esc(title);
            return '<div class="result-card">' +
              '<div class="result-title">' + badge + ' ' + link + '</div>' +
              '<div class="result-source">' + esc(source) + '</div>' +
              '<div class="result-snippet">' + esc(snippet.substring(0, 300)) + '...</div>' +
              '<div class="result-meta">' + score + '</div>' +
              '</div>';
          }).join("");
        })
        .catch(function (err) {
          resultsDiv.innerHTML = '<p class="result-msg err">Search failed: ' + esc(err.message) + '</p>';
        });
    });
  }

  // --- Ingest ---
  var ingestForm = document.getElementById("ingest-form");
  var ingestResult = document.getElementById("ingest-result");

  if (ingestForm) {
    ingestForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var url = document.getElementById("ingest-url").value.trim();
      var title = document.getElementById("ingest-title").value.trim();
      var tagsStr = document.getElementById("ingest-tags").value.trim();
      if (!url) return;

      var tags = tagsStr ? tagsStr.split(",").map(function (t) { return t.trim(); }).filter(Boolean) : [];
      var btn = ingestForm.querySelector("button");
      btn.textContent = "Ingesting...";
      btn.disabled = true;

      fetch("/api/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url, title: title, tags: tags }),
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data.error) {
            ingestResult.innerHTML = '<p class="result-msg err">' + esc(data.error) + '</p>';
          } else {
            ingestResult.innerHTML = '<p class="result-msg ok"> Ingested as doc #' + data.doc_id + '.</p>';
            ingestForm.reset();
          }
        })
        .catch(function (err) {
          ingestResult.innerHTML = '<p class="result-msg err">Failed: ' + esc(err.message) + '</p>';
        })
        .finally(function () {
          btn.textContent = "Ingest";
          btn.disabled = false;
        });
    });
  }

  // --- Stats ---
  function loadStats() {
    var grid = document.getElementById("stats-grid");
    if (!grid) return;
    grid.innerHTML = "<p>Loading...</p>";
    fetch("/api/stats")
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.error) { grid.innerHTML = "<p>Error loading stats</p>"; return; }
        var cards = [
          { val: data.total_documents || 0, label: "Documents" },
          { val: data.total_chunks || 0, label: "Chunks Indexed" },
        ];
        var sources = data.sources || {};
        Object.keys(sources).forEach(function (k) {
          cards.push({ val: sources[k], label: k + " sources" });
        });
        grid.innerHTML = cards.map(function (c) {
          return '<div class="stat-card"><div class="stat-value">' + c.val + '</div><div class="stat-label">' + esc(c.label) + '</div></div>';
        }).join("");
      })
      .catch(function () { grid.innerHTML = "<p>Error loading stats</p>"; });
  }

  // --- Browse ---
  function loadDocs() {
    var list = document.getElementById("doc-list");
    if (!list) return;
    list.innerHTML = '<p style="color:var(--text2)">Load docs via API (browse endpoint coming soon). Use search for now.</p>';
  }

  // --- Utilities ---
  function esc(s) {
    if (!s) return "";
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
})();
