"""Local stand-in for the Cohere rerank client.

By default it reranks by a simple lexical-overlap score. Set the env var
COHERE_FORCE_503=1 (the demo does this) to make it raise a service error, so the
retrieval agent's fallback to the local bge reranker (Topic 7) can be shown.
"""
from __future__ import annotations

import os
from typing import Any


class CohereError(Exception):
    """Simulated transient Cohere failure (like a 503)."""


class _Result:
    def __init__(self, index: int, score: float) -> None:
        self.index = index
        self.relevance_score = score


class _Reranked:
    def __init__(self, results: list[_Result]) -> None:
        self.results = results


class Client:
    def __init__(self, api_key: str | None = None, **_kw: Any) -> None:
        self.api_key = api_key

    def rerank(self, model: str, query: str, documents: list[str],
               top_n: int = 8, **_kw: Any) -> _Reranked:
        if os.environ.get("COHERE_FORCE_503") == "1":
            raise CohereError("503 Service Unavailable")
        q = set(query.lower().split())
        scored = sorted(
            ((i, len(q & set(d.lower().split())) / (len(q) or 1)) for i, d in enumerate(documents)),
            key=lambda t: t[1], reverse=True,
        )
        return _Reranked([_Result(i, s) for i, s in scored[:top_n]])
