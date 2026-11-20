"""Topic 7 — the retrieval agent (STARTER: implement hybrid retrieve + rerank).

Available to you (all offline):
  from ..fakes import vectorstore_fake as vs
    vs.bm25_search(query, tenant, k)   vs.dense_search(query, tenant, k)
    vs.rrf_fuse([listA, listB], weights=[0.4, 0.6])   vs.bge_rerank(query, docs, top_n)
  from ..fakes import cohere_fake   # cohere_fake.Client(...).rerank(...) may raise CohereError
  Anthropic() for the query rewrite.
Your job: rewrite the query, fuse BM25 + dense, rerank the top set (fall back to bge if
Cohere is down), and return {"docs": [...]}.
"""
from __future__ import annotations

from ..config import settings
from ..fakes import traceable
from ._deadline import deadline


@deadline(settings.retrieval_deadline_s, {"docs": []})
@traceable(name="retrieval_agent", project_name=settings.project_name)
async def retrieval_node(state: dict) -> dict:
    # TODO (Topic 7): rewrite the query, run hybrid search (bm25 + dense) over each
    #   variant, RRF-fuse and dedup by doc_id, then rerank to the top docs (with a
    #   fallback to the local bge reranker if Cohere errors). Return {"docs": [...]}.
    return {"docs": []}     # placeholder so the graph still runs
