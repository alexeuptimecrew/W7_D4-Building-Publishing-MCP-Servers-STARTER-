"""Local stand-in for the Anthropic client — deterministic, no API key, no network.

Enough of the Messages API shape for the api agent's tool-use loop (Topic 4) and the
retrieval agent's query rewrite (Topic 7). Behaviour is decided from the message text
so the demo is reproducible.
"""
from __future__ import annotations

import re
from typing import Any


class _Block:
    def __init__(self, **kw: Any) -> None:
        self.__dict__.update(kw)


class _Response:
    def __init__(self, stop_reason: str, content: list[_Block]) -> None:
        self.stop_reason = stop_reason
        self.content = content


def _last_user_text(messages: list[dict]) -> str:
    for m in reversed(messages):
        if m.get("role") == "user":
            c = m.get("content", "")
            return c if isinstance(c, str) else str(c)
    return ""


def _tenant(text: str) -> str:
    m = re.search(r"tenant-[abc]", text)
    return m.group(0) if m else "tenant-a"


def _order_id(text: str) -> str:
    m = re.search(r"ord-[a-z0-9-]+", text)
    return m.group(0) if m else "ord-synth-9001"


class _Messages:
    def create(self, model: str, max_tokens: int, messages: list[dict],
               tools: list[dict] | None = None, **_kw: Any) -> _Response:
        text = _last_user_text(messages)
        last_role = messages[-1]["role"] if messages else "user"

        # Query-rewrite call (retrieval agent): no tools, asks for paraphrases.
        if not tools and "rewrite" in text.lower():
            base = text.split("\n")[-1].strip() or text
            return _Response("end_turn", [_Block(
                type="text",
                text=f"{base}\nWhat is the {base.rstrip('?')}?\nExplain: {base}")])

        # Tool-use loop: only emit a tool call when the model is being *asked*
        # (last turn is the user). After we append the assistant turn, it ends.
        if tools and last_role == "user":
            names = [t["name"] for t in tools]
            want = "orders.create_refund" if ("refund" in text.lower()
                                              and "orders.create_refund" in names) else None
            if want is None:
                want = "orders.get_order" if "orders.get_order" in names else names[0]
            args = {"order_id": _order_id(text), "tenant_id": _tenant(text)}
            if want.endswith("create_refund"):
                args["reason"] = "duplicate charge"
            return _Response("tool_use", [_Block(
                type="tool_use", id="toolu_synth_1", name=want, input=args)])

        return _Response("end_turn", [_Block(
            type="text", text="Done — I used the tools and have what I need.")])


class Anthropic:
    def __init__(self, *_a: Any, **_kw: Any) -> None:
        self.messages = _Messages()
