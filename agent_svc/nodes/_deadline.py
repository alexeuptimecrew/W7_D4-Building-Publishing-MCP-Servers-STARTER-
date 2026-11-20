"""Topic 3 — per-node deadline decorator (STARTER: implement the timeout).

Right now the wrapper just runs the node with NO deadline, so a slow agent would hang
the whole graph. Your job: run it under a timeout and, on expiry, tag the trace and
return the `sentinel` instead of hanging.
"""
from __future__ import annotations

import asyncio  # noqa: F401  (you'll use asyncio.wait_for / asyncio.TimeoutError)
import functools

from ..fakes import get_current_run_tree  # noqa: F401  (tag the run on timeout)


def deadline(seconds: float, sentinel: dict):
    def deco(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs) -> dict:
            # TODO (Topic 3): run fn under asyncio.wait_for(timeout=seconds).
            #   On asyncio.TimeoutError: tag the current run (get_current_run_tree)
            #   with {"deadline_exceeded": True} and return `sentinel`.
            return await fn(*args, **kwargs)     # placeholder: no deadline yet
        return wrapper
    return deco
