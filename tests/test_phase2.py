"""Graded checks for Phase 2 — state & reducers, coordination, deadlines.

Each test is SKIPPED until you implement its topic. Remove the matching skip line to
grade your work (or delete `pytestmark` to run them all).
"""
import asyncio

import pytest

from agent_svc.fakes import traceable
from agent_svc.graph import REDUCERS, apply_update, supervisor
from agent_svc.nodes._deadline import deadline

pytestmark = pytest.mark.skip(reason="Implement the topic, then remove this skip to grade it.")


def test_reducers_merge_not_clobber():
    assert {"docs", "tool_results", "messages"} <= set(REDUCERS)
    state = {"docs": [{"doc_id": "d1"}], "tool_results": {"a": 1}}
    apply_update(state, {"docs": [{"doc_id": "d2"}]})
    apply_update(state, {"tool_results": {"b": 2}})
    assert [d["doc_id"] for d in state["docs"]] == ["d1", "d2"]
    assert state["tool_results"] == {"a": 1, "b": 2}


def test_supervisor_routes():
    assert supervisor({"question": "how do I refund order ord-1?"}) == ["retrieval", "api"]
    assert supervisor({"question": "status of order ord-1"}) == ["api"]
    assert "retrieval" in supervisor({"question": "hello there"})


async def test_deadline_returns_sentinel():
    @deadline(0.02, {"docs": []})
    @traceable(name="slow")
    async def slow(_state):
        await asyncio.sleep(0.3)
        return {"docs": ["nope"]}

    assert await slow({}) == {"docs": []}
