"""Service settings. In prod these come from env / secrets (pydantic-settings);
here they carry safe defaults so the whole thing runs with zero configuration.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

TENANTS = ("tenant-a", "tenant-b", "tenant-c")


@dataclass(frozen=True)
class Settings:
    project_name: str = "acme-agent-svc-dev"
    tenants: tuple[str, ...] = TENANTS
    # Per-node deadlines (seconds), chosen ~2x p99 from the lesson's measurements.
    retrieval_deadline_s: float = 3.0
    api_deadline_s: float = 5.0
    # Reranker: 'bge' (local, default) or 'cohere' (exercises the 503 -> bge fallback).
    reranker: str = field(default_factory=lambda: os.environ.get("RERANKER", "bge"))
    # Cost SLI: alarm if synthesis $/request p99 exceeds this (today's budget).
    synthesis_cost_ceiling_usd: float = 0.015
    # RAGAS faithfulness floor for the nightly drift alarm.
    faithfulness_floor: float = 0.80


settings = Settings()
