"""
Seed the local KB with some sample data for testing.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.db import init_db
from lib.ingest import ingest_text, ingest_rss

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kb.sqlite")

# Init
init_db(path=DB_PATH)
print("DB initialized.")

# Seed with a few useful sources
docs = [
    {
        "title": "Introduction to Machine Learning",
        "content": """
Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. The primary aim is to allow computers to learn automatically without human intervention or assistance and adjust actions accordingly.

Supervised learning algorithms are trained using labeled examples, such as an input where the desired output is known. The algorithm receives a set of inputs along with the corresponding correct outputs, and the algorithm learns by comparing its actual output with correct outputs to find errors. It then modifies the model accordingly.

Unsupervised learning algorithms are used when the training data consists of examples without a corresponding target label. The system tries to learn without a teacher. The most common unsupervised learning method is cluster analysis.

Reinforcement learning is inspired by behaviorist psychology. It works by rewarding desired behaviors and punishing undesired ones. A reinforcement agent learns from the consequences of its actions, rather than from being explicitly taught, and selects its actions on the basis of its past experiences and new choices.
        """,
        "tags": ["ml", "ai", "tutorial"],
    },
    {
        "title": "Understanding Distributed Systems",
        "content": """
A distributed system is a model in which components located on networked computers communicate and coordinate their actions by passing messages. The components interact with each other in order to achieve a common goal.

Key properties of distributed systems include concurrency, lack of a global clock, and independent failure of components. The design must handle partial failure gracefully.

CAP theorem states that any distributed data store can provide only two of the following three guarantees: Consistency, Availability, and Partition tolerance. In practice, distributed systems must choose between consistency and availability when a network partition occurs.

Consensus algorithms like Raft and Paxos enable multiple nodes to agree on a single value despite failure. These are fundamental to distributed databases and coordination services like ZooKeeper and etcd.
        """,
        "tags": ["distributed-systems", "architecture", "systems"],
    },
    {
        "title": "Python Best Practices",
        "content": """
Python is a high-level, interpreted, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation.

Key best practices include following PEP 8 style guide, using type hints, writing docstrings, and structuring projects with virtual environments. List comprehensions and generator expressions offer efficient iteration patterns.

Error handling should use specific exception types rather than bare except clauses. Context managers (with statement) ensure proper resource cleanup.

For performance, use built-in functions, avoid premature optimization, and profile before optimizing. Libraries like NumPy and Pandas provide efficient data structures for numerical computing.

Package management with pip and virtual environments (venv or conda) isolates dependencies. pyproject.toml is the modern standard for project configuration.
        """,
        "tags": ["python", "best-practices", "tutorial"],
    },
    {
        "title": "Web Security Fundamentals",
        "content": """
Cross-Site Scripting (XSS) is a security vulnerability that allows attackers to inject malicious scripts into web pages viewed by other users. There are three main types: stored XSS, reflected XSS, and DOM-based XSS.

SQL injection occurs when an attacker inserts malicious SQL code into application queries. Using parameterized queries and ORM libraries prevents most injection attacks.

Cross-Site Request Forgery (CSRF) tricks authenticated users into performing unintended actions. Anti-CSRF tokens are the primary defense mechanism.

HTTPS ensures encrypted communication between client and server. TLS 1.3 provides improved security and performance over earlier versions. Content Security Policy headers mitigate XSS by restricting content sources.

Authentication should use established libraries, never store plaintext passwords, and implement rate limiting on login endpoints. OAuth 2.0 and JWT are common authorization patterns.
        """,
        "tags": ["security", "web", "fundamentals"],
    },
    {
        "title": "CLI Application Design",
        "content": """
Command-line interfaces provide an efficient way to interact with software. Well-designed CLIs follow conventions: positional arguments for required inputs, flags for optional parameters, and subcommands for distinct operations.

Key principles include: sensible defaults, clear error messages, help text for every command, and consistent naming conventions. The --help flag should provide comprehensive usage information.

Output formatting supports both human-readable and machine-parseable formats. JSON output is useful for scripting and piping between tools.

Configuration should follow the XDG Base Directory Specification, with sensible fallbacks. Environment variables override config files, which override defaults.

Terminal colors and progress indicators improve user experience. Libraries like Rich (Python), Ink (Node), and lipglustic (Rust) provide high-level abstractions for CLI development.

Interactive prompts should support both TTY and piped input. Confirmation dialogs prevent destructive operations.
        """,
        "tags": ["cli", "design", "ux"],
    },
]

for doc in docs:
    doc_id = ingest_text(
        text=doc["content"],
        title=doc["title"],
        tags=doc.get("tags", []),
        path=DB_PATH,
    )
    print(f"Added: {doc_id} — {doc['title']}")

from lib.db import get_stats
stats = get_stats(path=DB_PATH)
print(f"\nTotal documents: {stats['total_documents']}")
print(f"Total chunks: {stats['total_chunks']}")
print(f"Sources: {stats['sources']}")
print("\nDone.")
