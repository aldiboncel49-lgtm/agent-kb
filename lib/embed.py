"""
agent-kb: embed.py
Semantic embedding + similarity using TF-IDF (zero external dependencies)
"""
import math
import re
import sqlite3
from collections import Counter
from typing import Optional


def tokenize(text: str) -> list[str]:
    """Simple tokenizer — lowercase, alphabetic tokens, min 2 chars."""
    return [t for t in re.findall(r'[a-z]{2,}', text.lower()) if t not in STOPWORDS]


# Common English stopwords + tech noise
STOPWORDS = {
    'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
    'her', 'was', 'one', 'our', 'out', 'has', 'have', 'been', 'were', 'they',
    'their', 'what', 'when', 'where', 'which', 'this', 'that', 'with', 'from',
    'will', 'would', 'there', 'these', 'than', 'then', 'them', 'into', 'some',
    'could', 'other', 'about', 'more', 'very', 'just', 'also', 'only', 'such',
    'each', 'make', 'like', 'over', 'such', 'time', 'here', 'well', 'know',
    'does', 'dont', 'doing', 'done', 'come', 'came', 'give', 'given', 'take',
    'takes', 'took', 'using', 'used', 'via', 'per', 'within', 'without',
    'org', 'com', 'www', 'http', 'https', 'html', 'pdf', 'png', 'jpg',
    'github', 'repo', 'repository', 'readme', 'license', 'mit', 'apache',
}


def compute_tfidf(documents: list[list[str]]) -> tuple[list[Counter], list[str], dict[str, float]]:
    """
    Compute TF-IDF vectors for a list of tokenized documents.
    Returns (tfidf_vectors, vocabulary, idf_scores).
    """
    n_docs = len(documents)
    if n_docs == 0:
        return [], [], {}

    # Document frequency
    df: Counter = Counter()
    for tokens in documents:
        unique_terms = set(tokens)
        for t in unique_terms:
            df[t] += 1

    # IDF
    idf: dict[str, float] = {}
    vocab: list[str] = sorted(df.keys())
    for t in vocab:
        idf[t] = math.log((n_docs + 1) / (df[t] + 1)) + 1  # smoothed

    # TF-IDF vectors
    tfidf_vectors: list[Counter] = []
    for tokens in documents:
        tf = Counter(tokens)
        max_tf = max(tf.values()) if tf else 1
        vec: Counter = Counter()
        for t, count in tf.items():
            if t in idf:
                vec[t] = (count / max_tf) * idf[t]
        # L2 normalize
        norm = math.sqrt(sum(v ** 2 for v in vec.values()))
        if norm > 0:
            for t in vec:
                vec[t] /= norm
        tfidf_vectors.append(vec)

    return tfidf_vectors, vocab, idf


def cosine_similarity(vec_a: Counter, vec_b: Counter) -> float:
    """Cosine similarity between two sparse TF-IDF vectors."""
    common = set(vec_a.keys()) & set(vec_b.keys())
    if not common:
        return 0.0
    dot = sum(vec_a[t] * vec_b[t] for t in common)
    return dot  # already normalized


def embed_text(text: str, idf: dict[str, float], vocab: list[str]) -> Counter:
    """Embed a single text into TF-IDF vector using pre-computed IDF."""
    tokens = tokenize(text)
    tf = Counter(tokens)
    max_tf = max(tf.values()) if tf else 1
    vec: Counter = Counter()
    for t, count in tf.items():
        if t in idf:
            vec[t] = (count / max_tf) * idf[t]
    norm = math.sqrt(sum(v ** 2 for v in vec.values()))
    if norm > 0:
        for t in vec:
            vec[t] /= norm
    return vec
