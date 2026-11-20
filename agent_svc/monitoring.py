"""Topic 9 — per-agent cost SLIs + RAGAS drift (STARTER).

The ContextVar and the metric sink are set up. Your job: (a) make `emit_cost` tag the
spend with the *current agent* from the ContextVar so attribution stays correct under
concurrency, and (b) implement `evaluate_sampled_runs` to score sampled synthesis runs.
"""
from __future__ import annotations

import contextvars
import json  # noqa: F401
from typing import Optional

from .config import settings
from .fakes import Client  # noqa: F401

_current_agent: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "current_agent", default=None)
_METRICS: list = []


def set_agent(name: str) -> None:
    _current_agent.set(name)


def emit_cost(tenant: str, usd: float) -> None:
    # TODO (Topic 9): append (the current agent from the ContextVar, tenant, usd)
    #   to _METRICS — read the agent with _current_agent.get().
    _METRICS.append((None, tenant, usd))     # placeholder: agent not tagged yet


def costs_by_agent() -> dict:
    agg: dict = {}
    for agent, tenant, usd in _METRICS:
        agg[(agent, tenant)] = round(agg.get((agent, tenant), 0.0) + usd, 6)
    return agg


def reset_metrics() -> None:
    _METRICS.clear()


def evaluate_sampled_runs(sample_rate: float = 1.0) -> dict:
    # TODO (Topic 9): use Client().list_runs(filter='eq(name,"synthesis_agent")'),
    #   sample sample_rate of them, score each (faithfulness/relevancy/recall),
    #   write scores back with update_run, and return the mean summary.
    return {"n": 0}     # placeholder


def drift_alarm(summary: dict) -> bool:
    return summary.get("faithfulness", 1.0) < settings.faithfulness_floor
