"""Topic 6 — bridge graph events to the Vercel AI SDK SSE protocol (STARTER).

`demo_event_source` (given) yields events shaped exactly like
`graph.astream_events(version='v2')`. Your job is `event_stream`: translate each event
into the prefixed SSE line the UI expects.
"""
from __future__ import annotations

import json  # noqa: F401
from typing import AsyncIterator


class _Chunk:
    def __init__(self, content: str) -> None:
        self.content = content


async def demo_event_source(final_answer: dict) -> AsyncIterator[dict]:
    """Yield events shaped like astream_events(version='v2'), deterministically."""
    for word in final_answer["text"].split():
        yield {"event": "on_chat_model_stream", "name": "synthesis_agent",
               "data": {"chunk": _Chunk(word + " ")}}
    yield {"event": "on_tool_start", "name": "orders.get_order",
           "data": {"input": {"order_id": "ord-synth-9001"}}}
    yield {"event": "on_tool_end", "name": "orders.get_order",
           "data": {"output": {"status": "PAID"}}}
    yield {"event": "on_chain_end", "name": "synthesis_agent",
           "data": {"output": {"answer": json.dumps(final_answer)}}}


async def event_stream(events: AsyncIterator[dict]) -> AsyncIterator[str]:
    # TODO (Topic 6): for each event, yield the matching SSE line:
    #   on_chat_model_stream -> f'0:{json.dumps(delta)}\n'   (delta = chunk.content)
    #   on_tool_start        -> f'9:{json.dumps({"toolName":name,"args":...})}\n'
    #   on_tool_end          -> f'a:{json.dumps({"toolName":name,"result":...})}\n'
    #   on_chain_end(synthesis) -> f'2:{json.dumps({"finalAnswer": ...})}\n'
    async for _ev in events:
        pass                                   # placeholder: nothing translated yet
    yield 'd:{"finishReason":"stop"}\n'        # keep the terminating line
