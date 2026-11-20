"""Interactive walkthrough — STARTER. Add topics ONE AT A TIME as you implement them.

The default run shows only the topic(s) in ENABLED_TOPICS below (starts at [1]). As you
finish a topic, add its number to ENABLED_TOPICS and re-run — or run a single topic
directly. You'll watch each payoff switch from a placeholder to the real output.

    python run_demo.py            # runs the ENABLED_TOPICS set below (one at a time)
    python run_demo.py 3          # run just topic 3
    python run_demo.py 1 2 3      # run a few
    python run_demo.py all        # run everything (mostly placeholders until you build it)
    pytest -q                     # graded checks (each is skipped until you implement it)
"""
from __future__ import annotations

import asyncio
import json
import sys
import time

# Add topic numbers here as you implement them, then re-run. Start with just topic 1.
ENABLED_TOPICS = [1]

TITLES = {
    1: "LangGraph state & reducers",
    2: "Coordination — the supervisor routes",
    3: "Parallel execution + per-node deadlines",
    4: "The API agent — tool-use loop + idempotency",
    5: "The synthesis agent — structured, grounded output",
    6: "Streaming to the UI over SSE",
    7: "The retrieval agent — hybrid + rerank + fallback",
    8: "End-to-end tracing — one trace, three sub-runs",
    9: "Monitoring — per-agent cost + RAGAS drift",
    10: "GitOps deploy — reconcile + budget hard-cap",
}


def banner(n: int) -> None:
    print(f"\n{'=' * 74}\n  TOPIC {n}: {TITLES[n]}\n{'=' * 74}")


def ok(msg: str) -> None:
    print(f"  ✓ {msg}")


async def topic1() -> None:
    from agent_svc.graph import REDUCERS, apply_update
    ok(f"fields with a reducer: {sorted(REDUCERS)}   (empty until you add them)")
    state = {"docs": [{"doc_id": "doc-a-refund"}], "tool_results": {"api": "x"}}
    apply_update(state, {"docs": [{"doc_id": "doc-a-return"}]})
    apply_update(state, {"tool_results": {"orders.get_order": "ok"}})
    ok(f"docs after two writes -> {[d['doc_id'] for d in state['docs']]}  (should MERGE to two)")
    ok(f"tool_results -> {state['tool_results']}")


async def topic2() -> None:
    from agent_svc.graph import supervisor
    for q in ["how do I get a refund on order ord-synth-9001?",
              "what's the status of order ord-synth-9001?",
              "what is the refund policy?"]:
        ok(f"{q!r} -> {supervisor({'question': q})}")


async def topic3() -> None:
    from agent_svc.fakes import reset_runs, traceable
    from agent_svc.nodes._deadline import deadline
    reset_runs()

    @deadline(0.05, {"docs": []})
    @traceable(name="slow_retrieval", run_type="retriever")
    async def slow(_state: dict) -> dict:
        await asyncio.sleep(0.5)
        return {"docs": ["never-reached"]}

    start = time.perf_counter()
    out = await slow({})
    ok(f"slow node under a 0.05s deadline -> {out} in {time.perf_counter()-start:.2f}s "
       f"(should be the sentinel, fast)")


async def topic4() -> None:
    from agent_svc import mock_backend as mb
    from agent_svc.nodes.api import api_node
    mb.reset()
    st = {"question": "refund order ord-synth-9001", "tenant_id": "tenant-a", "thread_id": "th-idem"}
    r1 = await api_node(dict(st))
    await api_node(dict(st))
    ok(f"tools used -> {list(r1['tool_results'])}   (empty until you build the loop)")
    ok(f"two identical refund calls -> {len(mb.refunds())} refund(s) (should be exactly 1)")


async def topic5() -> None:
    from agent_svc.nodes.synthesis import synthesis_node
    grounded = json.loads(synthesis_node({
        "question": "how do I get a refund?", "tenant_id": "tenant-a",
        "docs": [{"doc_id": "doc-a-refund", "text": "Refunds are issued within 30 days."}],
        "tool_results": {}})["answer"])
    ok(f"grounded -> confidence {grounded['confidence']} citing {[c['doc_id'] for c in grounded['citations']]}")
    empty = json.loads(synthesis_node({
        "question": "did my refund go through?", "tenant_id": "tenant-a",
        "docs": [], "tool_results": {}})["answer"])
    ok(f"empty context -> confidence {empty['confidence']} (should refuse, < 0.3)")


async def topic6() -> None:
    from agent_svc.sse import demo_event_source, event_stream
    final = {"text": "Your refund is confirmed", "citations": [], "confidence": 0.9}
    lines = [ln async for ln in event_stream(demo_event_source(final))]
    for ln in lines:
        print(f"    {ln.rstrip()}")
    ok(f"SSE prefixes -> {[ln[0] for ln in lines]}  (want 0.. then 9 a 2 d)")


async def topic7() -> None:
    from agent_svc.nodes.retrieval import retrieval_node
    st = {"question": "how do I get a refund?", "tenant_id": "tenant-a", "thread_id": "t"}
    out = await retrieval_node(dict(st))
    ok(f"top docs -> {[d['doc_id'] for d in out['docs'][:3]]}  (want doc-a-refund first)")


async def topic8() -> None:
    from agent_svc import mock_backend as mb
    from agent_svc.fakes import langsmith_fake as ls
    from agent_svc.tracing import trace_url, traced_request
    mb.reset(); ls.reset_runs()
    out = await traced_request("how do I refund order ord-synth-9001?", "tenant-a", "th-trace")
    roots = ls.list_runs("chat_request")
    if roots:
        print(roots[0].as_tree().replace("\n", "\n    "))
    ok(f"trace id -> {out['trace_id']!r} -> {trace_url(out['trace_id'])}  (should be non-empty)")


async def topic9() -> None:
    from agent_svc import monitoring as mon
    from agent_svc.fakes import langsmith_fake as ls
    from agent_svc.nodes.synthesis import synthesis_node
    mon.reset_metrics()

    async def work(agent: str, tenant: str) -> None:
        mon.set_agent(agent)
        await asyncio.sleep(0.01)
        mon.emit_cost(tenant, 0.004)
    await asyncio.gather(work("retrieval", "tenant-a"), work("api", "tenant-a"),
                         work("synthesis", "tenant-b"))
    ok(f"per-agent cost -> {mon.costs_by_agent()}  (agents should NOT be None)")
    ls.reset_runs()
    synthesis_node({"question": "q", "tenant_id": "tenant-a", "docs": [], "tool_results": {}})
    summary = mon.evaluate_sampled_runs(1.0)
    ok(f"RAGAS summary -> {summary};  drift alarm -> {mon.drift_alarm(summary)}")


async def topic10() -> None:
    from agent_svc import reconcile as rc
    desired, live = {"image": "sha-good"}, {"image": "sha-good"}
    ok(f"reconcile in sync -> {rc.reconcile(desired, live)}")
    ok(f"drift then self-heal -> {rc.self_heal(desired, live, {'image': 'sha-hand-edited'})} "
       f"(live now {live['image']}, should be sha-good)")
    guard = rc.BudgetGuard(limit_usd=0.01)
    guard.record(0.006); allowed = guard.can_invoke_llm()
    guard.record(0.006); denied = guard.can_invoke_llm()
    ok(f"budget -> invoke at 60%: {allowed}; at 120%: {denied}  (should be True then False)")


TOPICS = {1: topic1, 2: topic2, 3: topic3, 4: topic4, 5: topic5,
          6: topic6, 7: topic7, 8: topic8, 9: topic9, 10: topic10}


def _selected(argv: list[str]) -> list[int]:
    if not argv:
        return ENABLED_TOPICS
    if argv[0].lower() == "all":
        return sorted(TOPICS)
    picks = [int(a) for a in argv if a.isdigit() and int(a) in TOPICS]
    return picks or ENABLED_TOPICS


async def main() -> None:
    picks = _selected(sys.argv[1:])
    print(f"Running topics {picks}.  Add numbers to ENABLED_TOPICS (or pass them: "
          f"python run_demo.py <n>) as you implement each one.")
    for n in picks:
        banner(n)
        try:
            await TOPICS[n]()
        except Exception as exc:
            print(f"  ⚠ topic {n} hit {type(exc).__name__}: {exc}")
    print(f"\n{'=' * 74}\n  Implement a topic, add it to ENABLED_TOPICS, re-run to light it up."
          f"\n{'=' * 74}")


if __name__ == "__main__":
    asyncio.run(main())
