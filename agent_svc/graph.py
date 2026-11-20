"""Topics 1-3 wiring — the orchestration engine.

The engine below (reducer lookup, apply_update, run_agent_graph, build_langgraph) is
given. Your Topic 2 job is `supervisor()`: route the question to the right agent(s).
"""
from __future__ import annotations

import asyncio
from typing import Callable

from .state import AgentState


def reducers_of(state_cls: type) -> dict:
    """Pull the reducer function out of each Annotated field's metadata."""
    out: dict = {}
    for key, ann in getattr(state_cls, "__annotations__", {}).items():
        meta = getattr(ann, "__metadata__", None)
        if meta:
            out[key] = meta[0]
    return out


REDUCERS = reducers_of(AgentState)


def apply_update(state: dict, update: dict) -> dict:
    """Apply a node's partial update: reduced keys merge, bare keys overwrite."""
    for key, value in update.items():
        if key in REDUCERS and key in state:
            state[key] = REDUCERS[key](state[key], value)
        else:
            state[key] = value
    return state


def supervisor(state: AgentState) -> list:
    # TODO (Topic 2): return a list of targets — 'retrieval', 'api', or BOTH —
    #   based on keywords in state['question']. Default to ['retrieval'] when
    #   nothing matches. (A question that needs docs AND an order should fan out.)
    return ["retrieval"]          # placeholder: always retrieval, so the graph still runs


def _fresh_state(question: str, tenant_id: str, thread_id: str) -> dict:
    return {"question": question, "tenant_id": tenant_id, "thread_id": thread_id,
            "messages": [], "docs": [], "tool_results": {}, "answer": None}


async def run_agent_graph(question: str, tenant_id: str, thread_id: str = "t-demo") -> dict:
    """Supervisor -> parallel fan-out (with deadlines) -> reduce -> synthesis."""
    from .nodes import api_node, retrieval_node, synthesis_node

    state = _fresh_state(question, tenant_id, thread_id)
    targets = supervisor(state)

    node_by_name = {"retrieval": retrieval_node, "api": api_node}
    coros = [node_by_name[name](dict(state)) for name in targets if name in node_by_name]
    updates = await asyncio.gather(*coros)
    for update in updates:
        apply_update(state, update)

    apply_update(state, synthesis_node(state))
    return state


def build_langgraph():
    """The production wiring: a real compiled LangGraph. Returns (graph, note)."""
    try:
        from langgraph.checkpoint.memory import MemorySaver
        from langgraph.graph import END, START, StateGraph
        from .nodes import api_node, retrieval_node, synthesis_node

        sg = StateGraph(AgentState)
        sg.add_node("retrieval", retrieval_node)
        sg.add_node("api", api_node)
        sg.add_node("synthesis", synthesis_node)
        sg.add_conditional_edges(START, lambda s: supervisor(s), ["retrieval", "api"])
        sg.add_edge("retrieval", "synthesis")
        sg.add_edge("api", "synthesis")
        sg.add_edge("synthesis", END)
        return sg.compile(checkpointer=MemorySaver()), "compiled real LangGraph"
    except Exception as exc:
        return None, f"real LangGraph not wired here ({type(exc).__name__}); using the offline engine"
