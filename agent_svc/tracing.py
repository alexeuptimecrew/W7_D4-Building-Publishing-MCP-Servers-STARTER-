"""Topic 8 — one trace per request (STARTER: capture + surface the trace id).

`traced_request` is already the root run (so the three agents nest under it). Your job:
capture the current run's id with `get_current_run_tree()` and return it, so the server
can put it on the X-LangSmith-Trace-Id header for the UI.
"""
from __future__ import annotations

from .config import settings
from .fakes import get_current_run_tree, traceable  # noqa: F401


@traceable(name="chat_request", project_name=settings.project_name)
async def traced_request(question: str, tenant_id: str, thread_id: str = "t-demo") -> dict:
    from .graph import run_agent_graph

    # TODO (Topic 8): capture the current run's id via get_current_run_tree()
    #   and return it as "trace_id" (empty string if there is no active run).
    trace_id = ""     # placeholder
    state = await run_agent_graph(question, tenant_id, thread_id)
    return {"trace_id": trace_id, "state": state}


def response_headers(trace_id: str) -> dict:
    return {"X-LangSmith-Trace-Id": trace_id, "X-Accel-Buffering": "no"}


def trace_url(trace_id: str) -> str:
    return f"https://smith.langchain.com/o/acme/runs/{trace_id}"
