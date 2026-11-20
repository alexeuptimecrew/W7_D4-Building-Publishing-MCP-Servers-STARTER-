"""The capstone exit criteria — the whole three-agent graph. Skipped until you build it."""
import json

import pytest

from agent_svc import mock_backend as mb
from agent_svc.graph import run_agent_graph

pytestmark = pytest.mark.skip(reason="Implement the topics, then remove this skip to grade the capstone.")


async def test_full_graph_answers_grounded_and_acts():
    state = await run_agent_graph(
        "how do I get a refund on order ord-synth-9001?", "tenant-a", "smoke")
    assert state["docs"], "retrieval leg produced no docs"
    assert state["tool_results"], "api leg produced no tool results"
    answer = json.loads(state["answer"])
    assert answer["citations"] and answer["confidence"] >= 0.8
    assert len(mb.refunds()) == 1


async def test_tenant_isolation():
    state = await run_agent_graph("status of order ord-synth-9001", "tenant-b", "iso")
    results = state["tool_results"].get("orders.get_order", {})
    assert not (isinstance(results, dict) and results.get("status") == "PAID")
