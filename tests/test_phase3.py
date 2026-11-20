"""Graded checks for Phase 3 — api agent, synthesis, SSE. Skipped until implemented."""
import json

import pytest

from agent_svc import mock_backend as mb
from agent_svc.nodes.api import _idempotency_key, api_node
from agent_svc.nodes.synthesis import synthesis_node
from agent_svc.sse import demo_event_source, event_stream

pytestmark = pytest.mark.skip(reason="Implement the topic, then remove this skip to grade it.")


def test_idempotency_key_is_deterministic():
    a = _idempotency_key("t1", "orders.create_refund", {"order_id": "o1"})
    b = _idempotency_key("t1", "orders.create_refund", {"order_id": "o1"})
    c = _idempotency_key("t2", "orders.create_refund", {"order_id": "o1"})
    assert a == b and a != c and a != ""


async def test_api_agent_refund_is_idempotent():
    st = {"question": "refund order ord-synth-9001", "tenant_id": "tenant-a", "thread_id": "x"}
    await api_node(dict(st))
    await api_node(dict(st))
    assert len(mb.refunds()) == 1


def test_synthesis_grounds_and_refuses():
    grounded = json.loads(synthesis_node({
        "question": "q", "tenant_id": "tenant-a",
        "docs": [{"doc_id": "doc-a-refund", "text": "Refunds within 30 days."}],
        "tool_results": {}})["answer"])
    assert grounded["confidence"] >= 0.8 and grounded["citations"]
    empty = json.loads(synthesis_node({
        "question": "q", "tenant_id": "tenant-a", "docs": [], "tool_results": {}})["answer"])
    assert empty["confidence"] < 0.3


async def test_sse_bridge_prefixes():
    final = {"text": "two words", "citations": [], "confidence": 0.9}
    lines = [ln async for ln in event_stream(demo_event_source(final))]
    prefixes = [ln[0] for ln in lines]
    assert prefixes[0] == "0" and "9" in prefixes and "a" in prefixes
    assert prefixes[-2] == "2" and prefixes[-1] == "d"
