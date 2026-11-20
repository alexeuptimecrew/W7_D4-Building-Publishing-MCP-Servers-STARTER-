"""Local stand-in for LangSmith — no API key, no network.

`@traceable` builds a real run tree using contextvars (exactly how the real SDK
nests sub-runs under a parent), records the tree in memory, and exposes
`get_current_run_tree()` + a `Client` so Topics 8 and 9 work offline.
"""
from __future__ import annotations

import contextvars
import functools
import inspect
from typing import Any, Callable

_counter = {"n": 0}
_TRACES: list["Run"] = []                      # every root run, in order
_current: contextvars.ContextVar["Run | None"] = contextvars.ContextVar(
    "current_run", default=None)


class Run:
    def __init__(self, name: str, run_type: str | None, parent: "Run | None") -> None:
        _counter["n"] += 1
        self.id = f"run-{_counter['n']:04d}"
        self.name = name
        self.run_type = run_type
        self.parent = parent
        self.child_runs: list["Run"] = []
        self.metadata: dict[str, Any] = {}
        self.extra: dict[str, Any] = {}
        self.inputs: dict[str, Any] = {}
        self.outputs: Any = None

    def add_metadata(self, md: dict[str, Any]) -> None:
        self.metadata.update(md)

    def as_tree(self, indent: int = 0) -> str:
        pad = "  " * indent
        tag = f" [{self.run_type}]" if self.run_type else ""
        md = f"  {self.metadata}" if self.metadata else ""
        lines = [f"{pad}- {self.name}{tag} ({self.id}){md}"]
        for c in self.child_runs:
            lines.append(c.as_tree(indent + 1))
        return "\n".join(lines)


def get_current_run_tree() -> "Run | None":
    return _current.get()


def traceable(name: str | None = None, run_type: str | None = None,
              project_name: str | None = None, **_kw: Any):
    """Decorate a sync or async function so each call becomes a nested run."""
    def deco(fn: Callable) -> Callable:
        run_name = name or fn.__name__

        def _open() -> Run:
            parent = _current.get()
            run = Run(run_name, run_type, parent)
            (parent.child_runs if parent else _TRACES).append(run)
            return run

        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def awrap(*a: Any, **k: Any) -> Any:
                run = _open()
                token = _current.set(run)
                try:
                    run.outputs = await fn(*a, **k)
                    return run.outputs
                finally:
                    _current.reset(token)
            return awrap

        @functools.wraps(fn)
        def wrap(*a: Any, **k: Any) -> Any:
            run = _open()
            token = _current.set(run)
            try:
                run.outputs = fn(*a, **k)
                return run.outputs
            finally:
                _current.reset(token)
        return wrap
    return deco


def reset_runs() -> None:
    _TRACES.clear()
    _counter["n"] = 0


def all_runs() -> list[Run]:
    """Flatten the whole forest (roots + descendants), in creation order."""
    out: list[Run] = []

    def walk(r: Run) -> None:
        out.append(r)
        for c in r.child_runs:
            walk(c)

    for root in _TRACES:
        walk(root)
    return out


def list_runs(name: str | None = None) -> list[Run]:
    return [r for r in all_runs() if name is None or r.name == name]


class Client:
    """The subset of langsmith.Client that Topics 8-9 touch."""

    def list_runs(self, project_name: str | None = None, run_type: str | None = None,
                  filter: str | None = None, parent_run_id: str | None = None,
                  limit: int | None = None) -> list[Run]:
        runs = all_runs()
        if run_type is not None:
            runs = [r for r in runs if r.run_type == run_type]
        if parent_run_id is not None:
            runs = [r for r in runs if r.parent is not None and r.parent.id == parent_run_id]
        if filter and filter.startswith('eq(name,'):
            wanted = filter.split('"')[1]
            runs = [r for r in runs if r.name == wanted]
        return runs[: limit] if limit else runs

    def update_run(self, run_id: str, extra: dict[str, Any] | None = None, **_kw: Any) -> None:
        for r in all_runs():
            if r.id == run_id and extra:
                r.extra.update(extra)
