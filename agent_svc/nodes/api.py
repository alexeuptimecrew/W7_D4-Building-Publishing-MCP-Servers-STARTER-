"""Topic 4 — the api agent (STARTER: implement the tool-use loop + idempotency).

Available to you: `open_session()` gives an MCP session with `list_tools()` and
`call_tool(name, args, headers=...)`; `Anthropic()` is the (faked) model client.
Your job: discover tools, run a BOUNDED tool-use loop, and attach an X-Tenant header
plus a DETERMINISTIC Idempotency-Key to each call so a retried refund happens once.
"""
from __future__ import annotations

import hashlib  # noqa: F401
import json     # noqa: F401
import uuid     # noqa: F401

from ..config import settings
from ..fakes import open_session, traceable  # noqa: F401
from ..fakes.anthropic_fake import Anthropic
from ._deadline import deadline

_anthropic = Anthropic()


def _idempotency_key(thread_id: str, tool: str, args: dict) -> str:
    # TODO (Topic 4): return a DETERMINISTIC key — hash of thread_id + tool + sorted
    #   args — so a retry of the SAME call reproduces the SAME key and the server
    #   dedupes it. (A random uuid4 here would double-refund.)
    return ""     # placeholder


@deadline(settings.api_deadline_s, {"tool_results": {}})
@traceable(name="api_agent", project_name=settings.project_name)
async def api_node(state: dict) -> dict:
    # TODO (Topic 4): session = open_session(); catalogue = await session.list_tools()
    #   Build the tools list for the model, run a bounded `for _ in range(5)` loop:
    #   call the model, if stop_reason == 'tool_use' dispatch each tool via
    #   session.call_tool(name, input, headers={X-Tenant, Idempotency-Key}), collect
    #   results, append the assistant turn, else break. Return {"tool_results": {...}}.
    return {"tool_results": {}}     # placeholder so the graph still runs
