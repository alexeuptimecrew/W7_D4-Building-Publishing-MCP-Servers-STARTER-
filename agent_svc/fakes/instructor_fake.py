"""Local stand-in for Instructor — returns a *validated* instance of the requested
Pydantic `response_model`, grounded in the docs/tool-results text it is given.

This mirrors the real contract: you pass `response_model=FinalAnswer`, you get a
`FinalAnswer` back (validated by Pydantic), never a raw string. Grounding/refusal is
decided from the context so Topic 5's payoff is deterministic.
"""
from __future__ import annotations

import re
from typing import Any


def _text_of(messages: list[dict]) -> str:
    parts: list[str] = []
    for m in messages:
        c = m.get("content", "")
        if isinstance(c, str):
            parts.append(c)
        elif isinstance(c, list):
            for blk in c:
                if isinstance(blk, dict) and blk.get("type") == "text":
                    parts.append(blk.get("text", ""))
    return "\n".join(parts)


class _Messages:
    def create(self, response_model: Any, messages: list[dict],
               max_retries: int = 0, **_kw: Any) -> Any:
        text = _text_of(messages)
        doc_ids = re.findall(r"\[(doc-[a-z0-9-]+)\]", text)
        has_docs = "(no docs retrieved)" not in text
        has_tools = "(no tools called)" not in text

        if not has_docs and not has_tools:
            # Empty context -> refuse with low confidence (the Air Canada rule).
            return response_model(
                text="I don't have enough grounded context to answer that safely.",
                citations=[],
                confidence=0.2,
            )

        citations = [{"doc_id": d, "quote": "supporting text from the retrieved policy chunk"}
                     for d in dict.fromkeys(doc_ids)][:3]
        body = ("Based on the retrieved policy and the order data, here is the grounded "
                "answer for your request.")
        return response_model(text=body, citations=citations,
                              confidence=0.88 if citations else 0.55)


class _Client:
    def __init__(self) -> None:
        self.messages = _Messages()


def from_anthropic(_client: Any) -> _Client:
    return _Client()
