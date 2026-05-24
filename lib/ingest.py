"""
agent-kb: ingest.py
Multi-source content ingestion pipeline
"""
import re
import time
import urllib.request
import urllib.error
import json
from typing import Optional

from lib.db import add_document


def _fetch_url(url: str, timeout: int = 15) -> Optional[str]:
    """Fetch URL content with basic error handling."""
    try:
        headers = {"User-Agent": "agent-kb/1.0"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            charset = "utf-8"
            ct = resp.headers.get("Content-Type", "")
            if "charset=" in ct:
                charset = ct.split("charset=")[-1].strip()
            return resp.read().decode(charset, errors="replace")
    except Exception as e:
        print(f"[ingest] fetch failed for {url}: {e}")
        return None


def _clean_html(html: str) -> str:
    """Strip HTML tags, decode entities, normalize whitespace."""
    # Remove scripts and styles
    html = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', ' ', html, flags=re.DOTALL)
    # Remove tags
    text = re.sub(r'<[^>]+>', ' ', html)
    # Decode basic entities
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def ingest_url(url: str, title: str = "", tags: list[str] | None = None,
               path: Optional[str] = None) -> Optional[int]:
    """Ingest a web page by URL."""
    html = _fetch_url(url)
    if not html:
        return None

    content = _clean_html(html)
    if len(content) < 100:
        print(f"[ingest] Content too short for {url}, skipping.")
        return None

    if not title:
        m = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL)
        title = _clean_html(m.group(1)) if m else url

    doc_id = add_document(
        source=url,
        source_type="url",
        title=title[:200],
        content=content,
        url=url,
        tags=tags or [],
        path=path,
    )
    print(f"[ingest] URL → doc {doc_id}: {title[:80]}")
    return doc_id


def ingest_rss(feed_url: str, max_entries: int = 10, tags: list[str] | None = None) -> list[int]:
    """Ingest entries from an RSS/Atom feed."""
    raw = _fetch_url(feed_url)
    if not raw:
        return []

    doc_ids = []
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(raw)

        # Detect RSS vs Atom
        items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
        ns = {'atom': 'http://www.w3.org/2005/Atom'}

        for item in items[:max_entries]:
            title_el = item.find('title') or item.find('atom:title', ns)
            link_el = item.find('link') or item.find('atom:link', ns)
            desc_el = item.find('description') or item.find('atom:summary', ns) or item.find('atom:content', ns)

            title = title_el.text.strip() if title_el is not None and title_el.text else "Untitled"
            link = ""
            if link_el is not None:
                link = link_el.text.strip() if link_el.text else link_el.get("href", "")
            desc = ""
            if desc_el is not None and desc_el.text:
                desc = _clean_html(desc_el.text)

            full_content = f"{title}\n\n{desc}"
            if len(full_content) < 50:
                continue

            doc_id = add_document(
                source=feed_url,
                source_type="rss",
                title=title[:200],
                content=full_content,
                url=link,
                tags=tags or [],
            )
            doc_ids.append(doc_id)
            print(f"[ingest] RSS → doc {doc_id}: {title[:80]}")
            time.sleep(0.3)

    except Exception as e:
        print(f"[ingest] RSS parse error for {feed_url}: {e}")

    return doc_ids


def ingest_github_readme(repo: str, tags: list[str] | None = None) -> Optional[int]:
    """Ingest a GitHub repo's README."""
    repo = repo.rstrip("/")
    if not repo.startswith("http"):
        repo = f"https://raw.githubusercontent.com/{repo}/main/README.md"
        # Try main, then master
        raw = _fetch_url(repo)
        if not raw:
            repo = repo.replace("/main/", "/master/")
            raw = _fetch_url(repo)
    else:
        raw = _fetch_url(repo)

    if not raw:
        return None

    title = repo.split("/")[-3] if "/" in repo else repo
    doc_id = add_document(
        source=repo,
        source_type="github",
        title=f"README: {title}",
        content=raw,
        url=repo,
        tags=tags or ["github", "readme"],
    )
    print(f"[ingest] GitHub → doc {doc_id}: {title}")
    return doc_id


def ingest_text(text: str, title: str, source: str = "manual",
                tags: list[str] | None = None, path: Optional[str] = None) -> int:
    """Ingest raw text directly."""
    return add_document(
        source=source,
        source_type="manual",
        title=title[:200],
        content=text,
        tags=tags or [],
        path=path,
    )
