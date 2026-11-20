"""Topic 1 — the shared graph state (STARTER: add the reducers).

Right now every field is a BARE type, so parallel writes to the same key clobber each
other (run `python run_demo.py 1` to see one branch's data vanish). Your job: give the
multi-writer fields a REDUCER via `Annotated[type, fn]` so concurrent writes MERGE.
"""
import operator  # noqa: F401  (you'll use operator.add)
from typing import Annotated, Optional, TypedDict  # noqa: F401


# TODO (Topic 1): write the merge function for tool_results (keys must never disappear).
# def merge_tool_results(old: dict, new: dict) -> dict: ...


class AgentState(TypedDict, total=False):
    question: str
    tenant_id: str
    thread_id: str
    # TODO (Topic 1): add reducers so these MERGE under parallel fan-out:
    #   messages     -> Annotated[list, operator.add]
    #   docs         -> Annotated[list, operator.add]
    #   tool_results -> Annotated[dict, merge_tool_results]
    messages: list          # bare -> clobbers (fix me)
    docs: list              # bare -> clobbers (fix me)
    tool_results: dict      # bare -> clobbers (fix me)
    answer: Optional[str]   # terminal, single writer: bare is correct here
