# W7_D5 — Multi-Agent Orchestration & Capstone Deployment · STARTER

The capstone `agent-svc`, with each topic's core left for you to implement. All the
infrastructure — the mock backend, the fakes, the graph engine, the fan-out/fan-in
wiring — is in place, so the project boots and `run_demo.py` runs immediately. Each
topic's payoff shows a **placeholder** result until you fill in its `TODO`.

## Run it — one topic at a time

Python is pinned to **3.12** by `.devcontainer/devcontainer.json`.

```bash
pip install -r requirements.txt
python run_demo.py            # shows only the topics in ENABLED_TOPICS (starts at [1])
python run_demo.py 3          # run a single topic's payoff
pytest -q                     # graded checks — each is skipped until you implement it
```

**Add topics one at a time.** Implement a topic's `TODO`, then either add its number to
`ENABLED_TOPICS` at the top of `run_demo.py` or run `python run_demo.py <n>`, and watch
that payoff switch from a placeholder to the real output. Remove the matching
`pytestmark = pytest.mark.skip(...)` line to grade it.

## Your job, topic by topic

| # | Topic | Implement in |
| --- | --- | --- |
| 1 | State reducers (merge, don't clobber) | `agent_svc/state.py` |
| 2 | Supervisor routing (fan-out) | `agent_svc/graph.py` (`supervisor`) |
| 3 | Per-node deadline decorator | `agent_svc/nodes/_deadline.py` |
| 4 | API agent tool-use loop + idempotency | `agent_svc/nodes/api.py` |
| 5 | Synthesis: structured, grounded answer | `agent_svc/nodes/synthesis.py` |
| 6 | SSE event-stream bridge | `agent_svc/sse.py` (`event_stream`) |
| 7 | Retrieval: hybrid + rerank + fallback | `agent_svc/nodes/retrieval.py` |
| 8 | Capture + surface the trace id | `agent_svc/tracing.py` |
| 9 | Cost tagging + RAGAS drift | `agent_svc/monitoring.py` |
| 10 | Reconcile loop + budget deny | `agent_svc/reconcile.py` |

No API keys or network needed — every external service is faked in-repo (`agent_svc/fakes/`
+ `mock_backend.py`). The real deploy manifests are under `deploy/` for reference (Topic 10).

Tip: implement Topic 1 (reducers) and Topic 2 (supervisor) first — the parallel graph in
`run_agent_graph` only merges both agents' results once the reducers exist.
