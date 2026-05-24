import json
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.db import get_db, search, keyword_search, get_stats
from lib.ingest import ingest_url

# Use /tmp for serverless writable storage
DB_PATH = "/tmp/kb.sqlite"


def handler(request):
    """Vercel serverless function entry point."""
    method = request.method
    path = request.path or ""

    # CORS
    cors = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    if method == "OPTIONS":
        return Response(status=204, headers=cors)

    try:
        if path == "/api/stats":
            stats = get_stats(path=DB_PATH)
            return Response(json.dumps(stats), headers={**cors, "Content-Type": "application/json"})

        elif path == "/api/search":
            query = request.args.get("q", "")
            limit = int(request.args.get("limit", "10"))
            if not query:
                return Response(json.dumps({"error": "Missing q parameter"}), status=400,
                                headers={**cors, "Content-Type": "application/json"})
            results = search(query, limit=limit, path=DB_PATH)
            if not results:
                results = keyword_search(query, limit=limit, path=DB_PATH)
            return Response(json.dumps({"results": results, "query": query}),
                            headers={**cors, "Content-Type": "application/json"})

        elif path == "/api/ingest" and method == "POST":
            body = request.json()
            url = body.get("url", "")
            title = body.get("title", "")
            tags = body.get("tags", [])
            if not url:
                return Response(json.dumps({"error": "Missing url"}), status=400,
                                headers={**cors, "Content-Type": "application/json"})
            doc_id = ingest_url(url, title=title, tags=tags)
            return Response(json.dumps({"doc_id": doc_id, "status": "ok"}),
                            headers={**cors, "Content-Type": "application/json"})

        else:
            return Response(json.dumps({"error": "Not found"}), status=404,
                            headers={**cors, "Content-Type": "application/json"})

    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500,
                        headers={**cors, "Content-Type": "application/json"})


# Vercel Python runtime compatibility
class Response:
    def __init__(self, body="", status=200, headers=None):
        self.body = body
        self.status_code = status
        self.headers = headers or {}
