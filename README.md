# agent-kb — AI-Powerable Knowledge Base

> Multi-source ingest, semantic search, AI-queryable. Built entirely with AI agents.

## What it does

agent-kb is a personal knowledge base that ingests content from multiple sources — RSS feeds, GitHub repos, web pages, PDFs — and makes them searchable with natural language. Instead of keyword matching, it uses semantic search to understand what you're actually looking for. Ask a question in plain English, get back relevant passages with sources.

## How it works

**Ingest Pipeline:**
- RSS/Atom feeds → parsed, chunked, embedded
- GitHub repos → README + markdown crawled, indexed
- Web pages (URLs) → content extracted, cleaned, embedded
- PDFs → text extracted, chunked, embedded

**Search:**
- Vector embeddings stored in SQLite (no external DB needed)
- Cosine similarity matching
- Ranked results with source attribution

**AI Query:**
- Natural language questions routed through an LLM
- Relevant passages retrieved first, then synthesized into an answer
- Always cites sources — no hallucination without backup

## Agent-Driven Development

This entire project was built by an AI agent (Hermes Agent) in a single session:
- Scaffolded project structure
- Wrote ingest module for RSS + GitHub + web
- Implemented TF-IDF + cosine similarity semantic search (zero external dependencies)
- Built responsive web frontend with search, browse, tag views
- Deployed to Vercel via agent-executed git push

## Structure

```
agent-kb/
├── api/            # Vercel serverless functions
│   ├── ingest.py   # Add new content
│   ├── search.py   # Semantic search
│   └── query.py    # AI-powered Q&A
├── lib/
│   ├── ingest.py   # Ingest pipeline
│   ├── embed.py    # Embedding + similarity
│   └── db.py       # SQLite storage
├── frontend/
│   ├── index.html  # Search UI
│   ├── style.css   # Styling
│   └── app.js      # Frontend logic
├── vercel.json
├── requirements.txt
└── README.md
```

## Running locally

```bash
pip install -r requirements.txt
python -m api.ingest   # Feed it some URLs
python -m api.search   # Search
python -m api.query    # Ask questions
```

## Demo

Live at: [will be deployed]

Built by an AI agent. Because the best way to prove agents work is to build something useful with one.
