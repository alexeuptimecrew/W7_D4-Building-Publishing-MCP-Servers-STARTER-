"""Local stand-in for the W7D3 hybrid retriever + pgvector store — no models, no DB.

Embeddings are deterministic hashed bag-of-tokens vectors (so cosine is meaningful
and reproducible without downloading a model). Provides a dense retriever, a BM25-ish
lexical retriever, an RRF fusion, and a local cross-encoder-ish reranker — enough to
demonstrate Topic 7 offline.
"""
from __future__ import annotations

import hashlib
from typing import Any

import numpy as np

_DIM = 256

# Tiny per-tenant policy corpus. doc_id, text.
_CORPUS: dict[str, list[dict[str, str]]] = {
    "tenant-a": [
        {"doc_id": "doc-a-refund", "text": "Refunds for tenant-a are issued via the orders-svc portal within 30 days of purchase."},
        {"doc_id": "doc-a-ship", "text": "Standard shipping for tenant-a takes three to five business days."},
        {"doc_id": "doc-a-warranty", "text": "Hardware sold to tenant-a carries a one year limited warranty."},
        {"doc_id": "doc-a-return", "text": "To return an item, tenant-a customers start a request in the orders portal and print the label."},
    ],
    "tenant-b": [
        {"doc_id": "doc-b-refund", "text": "Tenant-b refunds require manager approval and post within 45 days."},
        {"doc_id": "doc-b-sla", "text": "Billing-svc commits to 99.9 percent monthly availability for tenant-b."},
    ],
    "tenant-c": [
        {"doc_id": "doc-c-refund", "text": "Tenant-c operates on store credit only; cash refunds are not offered."},
    ],
}


def _stem(tok: str) -> str:
    # Tiny deterministic stemmer so refund/refunds and order/orders match.
    if len(tok) > 4 and tok.endswith("s") and not tok.endswith("ss"):
        return tok[:-1]
    return tok


def _tokens(text: str) -> list[str]:
    raw = "".join(c.lower() if c.isalnum() else " " for c in text).split()
    return [_stem(t) for t in raw if t]


def embed(text: str) -> np.ndarray:
    """Deterministic hashed bag-of-tokens embedding, L2-normalized."""
    v = np.zeros(_DIM, dtype=np.float32)
    for tok in _tokens(text):
        h = int(hashlib.sha256(tok.encode()).hexdigest(), 16)
        v[h % _DIM] += 1.0
    n = np.linalg.norm(v)
    return v / n if n else v


def corpus_texts(tenant_id: str) -> list[str]:
    return [d["text"] for d in _CORPUS.get(tenant_id, [])]


def dense_search(query: str, tenant_id: str, k: int = 20) -> list[dict[str, Any]]:
    docs = _CORPUS.get(tenant_id, [])
    q = embed(query)
    scored = [(d, float(embed(d["text"]) @ q)) for d in docs]
    scored.sort(key=lambda t: t[1], reverse=True)
    return [dict(d, _score=s) for d, s in scored[:k]]


def bm25_search(query: str, tenant_id: str, k: int = 20) -> list[dict[str, Any]]:
    docs = _CORPUS.get(tenant_id, [])
    q = set(_tokens(query))
    scored = [(d, len(q & set(_tokens(d["text"])))) for d in docs]
    scored.sort(key=lambda t: t[1], reverse=True)
    return [dict(d, _score=s) for d, s in scored[:k] if s > 0] or [dict(d, _score=0) for d in docs[:k]]


def rrf_fuse(lists: list[list[dict[str, Any]]], weights: list[float], k_const: int = 60) -> list[dict[str, Any]]:
    """Reciprocal Rank Fusion — combine ranked lists by 1/(k+rank), weighted."""
    scores: dict[str, float] = {}
    by_id: dict[str, dict[str, Any]] = {}
    for lst, w in zip(lists, weights):
        for rank, d in enumerate(lst):
            scores[d["doc_id"]] = scores.get(d["doc_id"], 0.0) + w / (k_const + rank)
            by_id[d["doc_id"]] = d
    ordered = sorted(scores.items(), key=lambda t: t[1], reverse=True)
    return [dict(by_id[doc_id], _rrf=s) for doc_id, s in ordered]


def bge_rerank(query: str, docs: list[dict[str, Any]], top_n: int = 8) -> list[dict[str, Any]]:
    """Local cross-encoder-ish reranker: joint lexical overlap + embedding cosine."""
    q_tokens = set(_tokens(query))
    q_vec = embed(query)
    def score(d: dict[str, Any]) -> float:
        lexical = len(q_tokens & set(_tokens(d["text"]))) / (len(q_tokens) or 1)
        cosine = float(embed(d["text"]) @ q_vec)
        return 0.5 * lexical + 0.5 * cosine
    return sorted(docs, key=score, reverse=True)[:top_n]
