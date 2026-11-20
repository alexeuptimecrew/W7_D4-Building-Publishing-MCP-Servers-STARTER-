"""agent-svc — the W7 capstone three-agent service.

A retrieval agent (hybrid RAG), an api agent (MCP tool-use loop), and a synthesis
agent (structured output), orchestrated over one shared LangGraph state. Everything
runs offline on the devbox: the keyed/networked services are faked in `fakes/` and
`mock_backend.py`; the deploy stack ships as reference manifests under `deploy/`.
"""
