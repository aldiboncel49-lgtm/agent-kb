"""
agent-kb: db.py
SQLite storage for documents + embeddings
"""
import json
import math
import re
import sqlite3
import time
from collections import Counter
from pathlib import Path
from typing import Optional

from lib.embed import tokenize, compute_tfidf, embed_text, cosine_similarity

DB_PATH = Path(__file__).parent.parent / "kb.sqlite"


def get_db(path: Optional[str] = None) -> sqlite3.Connection:
    p = Path(path) if path else DB_PATH
    conn = sqlite3.connect(str(p))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def init_db(path: Optional[str] = None):
    conn = get_db(path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            source_type TEXT NOT NULL DEFAULT 'url',
            title TEXT DEFAULT '',
            content TEXT NOT NULL,
            url TEXT DEFAULT '',
            tags TEXT DEFAULT '[]',
            created_at REAL DEFAULT (julianday('now'))
        );

        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id INTEGER NOT NULL,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            embedding TEXT NOT NULL,
            FOREIGN KEY (doc_id) REFERENCES documents(id) ON DELETE CASCADE
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(
            title, content, content=documents, content_rowid=id
        );

        CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks(doc_id);
        CREATE INDEX IF NOT EXISTS idx_documents_source ON documents(source);
        CREATE INDEX IF NOT EXISTS idx_documents_created ON documents(created_at);
    """)
    conn.commit()
    conn.close()


def add_document(source: str, source_type: str, title: str, content: str,
                 url: str = "", tags: list[str] | None = None,
                 path: Optional[str] = None) -> int:
    """Insert a document, chunk it, compute embeddings, return doc_id."""
    conn = get_db(path)
    cur = conn.execute(
        "INSERT INTO documents (source, source_type, title, content, url, tags) VALUES (?,?,?,?,?,?)",
        (source, source_type, title, content, url, json.dumps(tags or []))
    )
    doc_id = cur.lastrowid

    # FTS index
    conn.execute("INSERT INTO docs_fts(rowid, title, content) VALUES (?,?,?)",
                 (doc_id, title, content))

    # Chunk the content
    chunks = _chunk_text(content)
    all_tokens = [tokenize(c) for c in chunks]
    tfidf_vectors, vocab, idf = compute_tfidf(all_tokens)

    for i, (chunk_text, vec) in enumerate(zip(chunks, tfidf_vectors)):
        conn.execute(
            "INSERT INTO chunks (doc_id, chunk_index, content, embedding) VALUES (?,?,?,?)",
            (doc_id, i, chunk_text, json.dumps(dict(vec)))
        )

    # Store IDF + vocab for query-time embedding
    conn.execute(
        "CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)"
    )
    conn.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
        ("idf", json.dumps(idf))
    )
    conn.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
        ("vocab", json.dumps(vocab))
    )

    conn.commit()
    conn.close()
    return doc_id


def search(query: str, limit: int = 10, path: Optional[str] = None) -> list[dict]:
    """Semantic search: embed query, rank chunks by cosine similarity."""
    conn = get_db(path)

    # Load IDF + vocab
    idf_row = conn.execute("SELECT value FROM meta WHERE key='idf'").fetchone()
    vocab_row = conn.execute("SELECT value FROM meta WHERE key='vocab'").fetchone()
    if not idf_row or not vocab_row:
        conn.close()
        return []

    idf = json.loads(idf_row["value"])
    vocab = json.loads(vocab_row["value"])
    query_vec = embed_text(query, idf, vocab)

    # Load all chunk embeddings
    rows = conn.execute(
        "SELECT c.id, c.doc_id, c.chunk_index, c.content, c.embedding, "
        "d.title, d.source, d.source_type, d.url "
        "FROM chunks c JOIN documents d ON c.doc_id = d.id"
    ).fetchall()

    scored = []
    seen_chunks = set()
    for row in rows:
        chunk_id = row["id"]
        if chunk_id in seen_chunks:
            continue
        seen_chunks.add(chunk_id)
        vec = Counter(json.loads(row["embedding"]))
        sim = cosine_similarity(query_vec, vec)
        if sim > 0.01:
            scored.append({
                "chunk_id": chunk_id,
                "doc_id": row["doc_id"],
                "chunk_index": row["chunk_index"],
                "content": row["content"][:500],
                "score": round(sim, 4),
                "title": row["title"],
                "source": row["source"],
                "source_type": row["source_type"],
                "url": row["url"],
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    conn.close()
    return scored[:limit]


def keyword_search(query: str, limit: int = 10, path: Optional[str] = None) -> list[dict]:
    """Fallback FTS5 keyword search."""
    conn = get_db(path)
    try:
        rows = conn.execute(
            "SELECT d.id, d.title, d.source, d.source_type, d.url, d.content, "
            "snippet(docs_fts, 1, '<b>', '</b>', '...', 32) as snippet "
            "FROM docs_fts JOIN documents d ON docs_fts.rowid = d.id "
            "WHERE docs_fts MATCH ? ORDER BY rank LIMIT ?",
            (query, limit)
        ).fetchall()
    except Exception:
        conn.close()
        return []

    results = []
    for row in rows:
        results.append({
            "doc_id": row["id"],
            "title": row["title"],
            "source": row["source"],
            "source_type": row["source_type"],
            "url": row["url"],
            "snippet": row["snippet"],
            "score": 0.0,
        })
    conn.close()
    return results


def get_stats(path: Optional[str] = None) -> dict:
    conn = get_db(path)
    docs = conn.execute("SELECT COUNT(*) as c FROM documents").fetchone()["c"]
    chunks = conn.execute("SELECT COUNT(*) as c FROM chunks").fetchone()["c"]
    sources = conn.execute(
        "SELECT source_type, COUNT(*) as c FROM documents GROUP BY source_type"
    ).fetchall()
    conn.close()
    return {
        "total_documents": docs,
        "total_chunks": chunks,
        "sources": {r["source_type"]: r["c"] for r in sources},
    }


def get_document(doc_id: int, path: Optional[str] = None) -> Optional[dict]:
    conn = get_db(path)
    row = conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def _chunk_text(text: str, max_tokens: int = 200, overlap: int = 40) -> list[str]:
    """Split text into overlapping chunks by sentences, then truncate to max_tokens words."""
    # Split on sentence-ish boundaries
    sentences = re.split(r'(?<=[.!?])\s+|\n\s*\n', text)
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for sent in sentences:
        words = sent.split()
        if current_len + len(words) > max_tokens and current:
            chunks.append(" ".join(current))
            # overlap: keep last few words
            current = current[-overlap:]
            current_len = len(current)
        current.extend(words)
        current_len += len(words)

    if current:
        chunks.append(" ".join(current))

    # Filter tiny chunks
    chunks = [c for c in chunks if len(c.split()) >= 20]
    return chunks
