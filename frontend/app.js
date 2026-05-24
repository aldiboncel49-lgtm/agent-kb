/* agent-kb: app.js — client-side with embedded seed data */
(function () {
  "use strict";

  // --- Embedded seed knowledge base (survives page reload, no backend needed) ---
  var SEED_DOCS = [
    {
      id: 1, title: "Introduction to Machine Learning", source_type: "manual", url: "",
      content: "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. The primary aim is to allow computers to learn automatically without human intervention.\n\nSupervised learning algorithms are trained using labeled examples. The algorithm receives inputs with known correct outputs, compares its actual output with correct outputs, and modifies the model.\n\nUnsupervised learning algorithms work without labeled data. The system tries to learn patterns without a teacher. The most common method is cluster analysis.\n\nReinforcement learning rewards desired behaviors and punishes undesired ones. The agent learns from consequences of its actions."
    },
    {
      id: 2, title: "Understanding Distributed Systems", source_type: "manual", url: "",
      content: "A distributed system is a model where components on networked computers communicate by passing messages. Components interact to achieve a common goal.\n\nKey properties include concurrency, lack of a global clock, and independent failure of components. Design must handle partial failure gracefully.\n\nCAP theorem states that any distributed data store can provide only two of three guarantees: Consistency, Availability, and Partition tolerance. Systems must choose between consistency and availability during network partitions.\n\nConsensus algorithms like Raft and Paxos enable multiple nodes to agree on a single value despite failures. These are fundamental to distributed databases and coordination services."
    },
    {
      id: 3, title: "Python Best Practices", source_type: "manual", url: "",
      content: "Python is a high-level, interpreted programming language emphasizing code readability through significant indentation.\n\nKey best practices: follow PEP 8 style guide, use type hints, write docstrings, use virtual environments. List comprehensions and generator expressions offer efficient iteration.\n\nError handling should use specific exception types, not bare except clauses. Context managers (with statement) ensure proper resource cleanup.\n\nFor performance, use built-in functions, avoid premature optimization, and profile before optimizing. NumPy and Pandas provide efficient data structures.\n\nPackage management with pip and venv isolates dependencies. pyproject.toml is the modern standard."
    },
    {
      id: 4, title: "Web Security Fundamentals", source_type: "manual", url: "",
      content: "Cross-Site Scripting (XSS) allows attackers to inject malicious scripts into web pages viewed by other users. Three main types: stored, reflected, and DOM-based XSS.\n\nSQL injection inserts malicious SQL code into application queries. Using parameterized queries and ORM libraries prevents most injection attacks.\n\nCross-Site Request Forgery (CSRF) tricks authenticated users into unintended actions. Anti-CSRF tokens are the primary defense.\n\nHTTPS ensures encrypted communication. TLS 1.3 provides improved security. Content Security Policy headers mitigate XSS.\n\nAuthentication should use established libraries, never store plaintext passwords, and implement rate limiting. OAuth 2.0 and JWT are common patterns."
    },
    {
      id: 5, title: "CLI Application Design", source_type: "manual", url: "",
      content: "Command-line interfaces provide efficient interaction with software. Well-designed CLIs follow conventions: positional arguments for required inputs, flags for optional parameters, subcommands for distinct operations.\n\nKey principles: sensible defaults, clear error messages, help text for every command, consistent naming. The --help flag should provide comprehensive usage.\n\nOutput formatting supports both human-readable and machine-parseable formats. JSON output is useful for scripting.\n\nConfiguration follows XDG Base Directory Specification. Environment variables override config files, which override defaults.\n\nTerminal colors and progress indicators improve UX. Libraries like Rich (Python), Ink (Node), and clap (Rust) provide high-level CLI abstractions."
    },
    {
      id: 6, title: "How AI Agents Work", source_type: "manual", url: "",
      content: "An AI agent is a system that perceives its environment, makes decisions, and takes actions to achieve goals. Unlike simple chatbots, agents can use tools, maintain state, and execute multi-step workflows.\n\nThe core loop: perceive → reason → act → observe → repeat. The agent receives input, plans a sequence of actions, executes them using available tools, and processes the results.\n\nTool use is what makes agents powerful. Tools include web search, code execution, file operations, API calls, and browser automation. The agent selects the right tool for each subtask.\n\nMulti-agent systems coordinate multiple specialized agents. One agent might research, another writes, a third reviews. This mirrors how human teams work.\n\nMemory — both short-term (conversation context) and long-term (stored facts) — enables agents to maintain continuity across sessions."
    },
    {
      id: 7, title: "Introduction to Rust", source_type: "manual", url: "",
      content: "Rust is a systems programming language focused on safety, speed, and concurrency. It achieves memory safety without garbage collection through its ownership system.\n\nThe ownership model: each value has a single owner. When the owner goes out of scope, the value is dropped. Borrowing allows references without transferring ownership. The borrow checker enforces rules at compile time.\n\nZero-cost abstractions mean high-level features compile to efficient machine code. Iterators, closures, and pattern matching have no runtime overhead.\n\nCargo is Rust's build system and package manager. crates.io hosts thousands of libraries. The type system prevents null pointer dereferences and data races.\n\nRust is used in operating systems, web assembly, blockchain infrastructure, and performance-critical services. Major projects include the Linux kernel (Rust modules), Firefox's CSS engine, and the Deno runtime."
    },
    {
      id: 8, title: "Database Indexing Explained", source_type: "manual", url: "",
      content: "A database index is a data structure that improves the speed of data retrieval operations. Without an index, the database must scan every row in a table (full table scan). With an index, it can jump directly to relevant rows.\n\nB-tree indexes are the most common type. They maintain sorted data and allow logarithmic-time lookups, insertions, and deletions. Most relational databases use B-trees by default.\n\nHash indexes provide O(1) lookups for equality comparisons but don't support range queries. They're useful for exact-match lookups.\n\nComposite indexes cover multiple columns. Column order matters — the index can efficiently query on the prefix of columns. Put the most selective column first.\n\nIndexes speed up reads but slow down writes (inserts, updates, deletes must also update the index). Over-indexing can hurt write performance. Use EXPLAIN to analyze query plans."
    }
  ];

  // --- Simple TF-IDF + Cosine Similarity (client-side) ---
  var STOPWORDS = {};
  ["the","and","for","are","but","not","you","all","can","had","her","was","one","our","out","has","have","been","were","they","their","what","when","where","which","this","that","with","from","will","would","there","these","than","then","them","into","some","could","other","about","more","very","just","also","only","such","each","make","like","over","time","here","well","know","does","dont","using","used","via","per","its","any","may","most","many","much","get","got","how","why","who","whom","whose","both","few","being","did","doing","done","come","came","give","given","take","takes","took","within","without","org","com","www","http","https","html","pdf"].forEach(function(w) { STOPWORDS[w] = true; });

  function tokenize(text) {
    return text.toLowerCase().match(/[a-z]{2,}/g) || [];
  }

  function removeStopwords(tokens) {
    return tokens.filter(function(t) { return !STOPWORDS[t]; });
  }

  function computeTFIDF(documents) {
    var n = documents.length;
    var df = {};
    documents.forEach(function(tokens) {
      var unique = {};
      tokens.forEach(function(t) { unique[t] = true; });
      Object.keys(unique).forEach(function(t) { df[t] = (df[t] || 0) + 1; });
    });
    var idf = {};
    Object.keys(df).forEach(function(t) {
      idf[t] = Math.log((n + 1) / (df[t] + 1)) + 1;
    });
    var vectors = documents.map(function(tokens) {
      var tf = {};
      tokens.forEach(function(t) { tf[t] = (tf[t] || 0) + 1; });
      var tfVals = [];
      for (var k in tf) tfVals.push(tf[k]);
      var maxTF = Math.max.apply(null, tfVals.concat([1]));
      var vec = {};
      Object.keys(tf).forEach(function(t) {
        if (idf[t]) vec[t] = (tf[t] / maxTF) * idf[t];
      });
      var normSq = 0;
      for (var vk in vec) normSq += vec[vk] * vec[vk];
      var norm = Math.sqrt(normSq);
      if (norm > 0) Object.keys(vec).forEach(function(t) { vec[t] /= norm; });
      return vec;
    });
    return { vectors: vectors, idf: idf };
  }

  function cosineSim(a, b) {
    var dot = 0;
    Object.keys(a).forEach(function(k) { if (b[k]) dot += a[k] * b[k]; });
    return dot;
  }

  // Pre-compute document vectors
  var docTokens = SEED_DOCS.map(function(d) { return removeStopwords(tokenize(d.content)); });
  var tfidf = computeTFIDF(docTokens);

  function searchDocs(query, limit) {
    limit = limit || 10;
    var qTokens = removeStopwords(tokenize(query));
    if (qTokens.length === 0) return [];

    var qTF = {};
    qTokens.forEach(function(t) { qTF[t] = (qTF[t] || 0) + 1; });
    var qTfVals = [];
    for (var qk in qTF) qTfVals.push(qTF[qk]);
    var maxQTF = Math.max.apply(null, qTfVals.concat([1]));
    var qVec = {};
    Object.keys(qTF).forEach(function(t) {
      if (tfidf.idf[t]) qVec[t] = (qTF[t] / maxQTF) * tfidf.idf[t];
    });
    var qNormSq = 0;
    for (var qvk in qVec) qNormSq += qVec[qvk] * qVec[qvk];
    var qNorm = Math.sqrt(qNormSq);
    if (qNorm > 0) Object.keys(qVec).forEach(function(t) { qVec[t] /= qNorm; });

    var scored = tfidf.vectors.map(function(vec, i) {
      return { doc: SEED_DOCS[i], score: cosineSim(qVec, vec), index: i };
    });
    scored = scored.filter(function(s) { return s.score > 0.01; });
    scored.sort(function(a, b) { return b.score - a.score; });
    return scored.slice(0, limit);
  }

  // --- Navigation ---
  function showView(name) {
    document.querySelectorAll(".view").forEach(function(v) { v.classList.remove("active"); });
    document.querySelectorAll(".nav-item").forEach(function(n) { n.classList.remove("active"); });
    var view = document.getElementById("view-" + name);
    if (view) view.classList.add("active");
    var nav = document.querySelector('[data-view="' + name + '"]');
    if (nav) nav.classList.add("active");
  }

  document.querySelectorAll(".nav-item").forEach(function(item) {
    item.addEventListener("click", function(e) {
      e.preventDefault();
      showView(this.dataset.view);
    });
  });

  // --- Search ---
  var searchForm = document.getElementById("search-form");
  var searchInput = document.getElementById("search-input");
  var resultsDiv = document.getElementById("results");

  if (searchForm) {
    searchForm.addEventListener("submit", function(e) {
      e.preventDefault();
      var q = searchInput.value.trim();
      if (!q) return;
      resultsDiv.innerHTML = '<p style="color:var(--text2);padding:16px;">Searching...</p>';
      // Small delay for UX
      setTimeout(function() {
        var results = searchDocs(q, 10);
        if (results.length === 0) {
          resultsDiv.innerHTML = '<p style="color:var(--text2);padding:16px;">No results found. Try different keywords.</p>';
          return;
        }
        resultsDiv.innerHTML = results.map(function(r) {
          var snippet = r.doc.content.substring(0, 280).replace(/\n/g, " ") + "...";
          var badgeClass = "badge-" + (r.doc.source_type || "manual");
          return '<div class="result-card">' +
            '<div class="result-title"><span class="badge ' + badgeClass + '">' + esc(r.doc.source_type) + '</span> ' + esc(r.doc.title) + '</div>' +
            '<div class="result-snippet">' + esc(snippet) + '</div>' +
            '<div class="result-meta">Relevance: ' + (r.score * 100).toFixed(1) + '%</div>' +
            '</div>';
        }).join("");
      }, 150);
    });
  }

  // --- Browse ---
  function loadDocs() {
    var list = document.getElementById("doc-list");
    if (!list) return;
    list.innerHTML = SEED_DOCS.map(function(d) {
      var badgeClass = "badge-" + (d.source_type || "manual");
      return '<div class="doc-card">' +
        '<div class="doc-card-title"><span class="badge ' + badgeClass + '">' + esc(d.source_type) + '</span> ' + esc(d.title) + '</div>' +
        '<div class="doc-card-meta">' + esc(d.content.substring(0, 120)) + '...</div>' +
        '</div>';
    }).join("");
  }

  document.querySelector('[data-view="browse"]') && document.querySelector('[data-view="browse"]').addEventListener("click", loadDocs);

  // --- Stats ---
  function loadStats() {
    var grid = document.getElementById("stats-grid");
    if (!grid) return;
    grid.innerHTML = [
      { val: SEED_DOCS.length, label: "Documents" },
      { val: SEED_DOCS.reduce(function(s,d) { return s + d.content.split(/\s+/).length; }, 0).toLocaleString(), label: "Total Words" },
      { val: "8", label: "Topics" },
      { val: "TF-IDF", label: "Search Method" },
    ].map(function(c) {
      return '<div class="stat-card"><div class="stat-value">' + esc(String(c.val)) + '</div><div class="stat-label">' + esc(c.label) + '</div></div>';
    }).join("");
  }

  document.querySelector('[data-view="stats"]') && document.querySelector('[data-view="stats"]').addEventListener("click", loadStats);

  // --- Add Source (demo — adds to session only) ---
  var ingestForm = document.getElementById("ingest-form");
  var ingestResult = document.getElementById("ingest-result");

  if (ingestForm) {
    ingestForm.addEventListener("submit", function(e) {
      e.preventDefault();
      var title = document.getElementById("ingest-title").value.trim() || "Untitled";
      var content = document.getElementById("ingest-url").value.trim();
      if (!content) return;

      var newDoc = {
        id: SEED_DOCS.length + 1,
        title: title,
        source_type: "manual",
        url: "",
        content: content,
      };
      SEED_DOCS.push(newDoc);
      // Re-index
      docTokens.push(removeStopwords(tokenize(content)));
      var newTfidf = computeTFIDF(docTokens);
      tfidf.vectors = newTfidf.vectors;
      tfidf.idf = newTfidf.idf;

      ingestResult.innerHTML = '<p class="result-msg ok"> Added "' + esc(title) + '" to the knowledge base. Re-indexed ' + SEED_DOCS.length + ' documents.</p>';
      ingestForm.reset();
    });
  }

  // --- Utilities ---
  function esc(s) {
    if (!s) return "";
    return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
  }

  // Show browse on load for demo
  // showView('search');
})();
