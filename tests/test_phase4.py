"""Graded checks for Phase 4 — retrieval, tracing, monitoring, GitOps. Skipped until built."""
import asyncio

import pytest

from agent_svc import monitoring as mon
from agent_svc import reconcile as rc
from agent_svc.fakes import langsmith_fake as ls
from agent_svc.nodes.retrieval import retrieval_node
from agent_svc.nodes.synthesis import synthesis_node
from agent_svc.tracing import traced_request

pytestmark = pytest.mark.skip(reason="Implement the topic, then remove this skip to grade it.")


async def test_retrieval_surfaces_relevant_doc():
    out = await retrieval_node({"question": "how do I get a refund?",
                                "tenant_id": "tenant-a", "thread_id": "t"})
    assert out["docs"][0]["doc_id"] == "doc-a-refund"


async def test_one_trace_three_subruns():
    await traced_request("how do I refund order ord-synth-9001?", "tenant-a", "th")
    root = ls.list_runs("chat_request")[0]
    names = {c.name for c in root.child_runs}
    assert {"retrieval_agent", "api_agent", "synthesis_agent"} <= names


async def test_cost_tagging_is_concurrency_correct():
    async def work(agent, tenant):
        mon.set_agent(agent)
        await asyncio.sleep(0.01)
        mon.emit_cost(tenant, 0.001)
    await asyncio.gather(work("retrieval", "tenant-a"), work("api", "tenant-a"))
    costs = mon.costs_by_agent()
    assert costs[("retrieval", "tenant-a")] == 0.001
    assert costs[("api", "tenant-a")] == 0.001


def test_ragas_drift_alarm_fires():
    synthesis_node({"question": "q", "tenant_id": "tenant-a", "docs": [], "tool_results": {}})
    summary = mon.evaluate_sampled_runs(1.0)
    assert mon.drift_alarm(summary) is True


def test_reconcile_and_budget():
    desired, live = {"image": "sha-good"}, {"image": "sha-good"}
    rc.self_heal(desired, live, {"image": "sha-drift"})
    assert live["image"] == "sha-good"
    guard = rc.BudgetGuard(limit_usd=0.01)
    guard.record(0.006)
    assert guard.can_invoke_llm() is True
    guard.record(0.006)
    assert guard.can_invoke_llm() is False
