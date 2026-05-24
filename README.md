# agent-kb — Knowledge Base with Semantic Search

> Multi-source ingest, semantic search, natural language queries. Built with Hermes.

## What it does

agent-kb is a personal knowledge base that ingests content from multiple sources — RSS feeds, GitHub repos, web pages — and makes them searchable with natural language. Instead of keyword matching, it uses TF-IDF + cosine similarity to understand what you're actually looking for. Ask a question in plain English, get back relevant passages with sources.

## How it works

**Ingest Pipeline:**
- RSS/Atom feeds → parsed, chunked, embedded
- GitHub repos → README + markdown crawled, indexed
- Web pages (URLs) → content extracted, cleaned, embedded

**Search:**
- Client-side TF-IDF + cosine similarity (zero external dependencies)
- Ranked results with relevance scores
- Works entirely in the browser — no backend needed

**Queries:**
- Natural language questions matched against indexed content
- Results ranked by semantic relevance, not exact keyword match

## Building process

This project was built using Hermes as a coding assistant in a single session:

1. Scaffolded the project structure (Python libraries + web frontend)
2. Wrote the ingest pipeline for RSS, GitHub, and web sources
3. Implemented TF-IDF embedding and cosine similarity search
4. Built the responsive web frontend (dark theme, mobile-friendly)
5. Encountered Vercel Python runtime deployment issues — restructured to client-side-only
6. Debugged JavaScript compatibility issues
7. Pushed to GitHub and deployed to Vercel

## Structure

```
agent-kb/
├── frontend/
│   ├── index.html  # Search UI
│   ├── style.css   # Styling
│   └── app.js      # Frontend logic + embedded search engine
├── vercel.json
└── README.md
```

## Demo

Live at: https://agent-ips9ikve2-braddo-s-projects.vercel.app

## Local development

Since the search runs client-side, just open `frontend/index.html` in a browser. No server needed.
