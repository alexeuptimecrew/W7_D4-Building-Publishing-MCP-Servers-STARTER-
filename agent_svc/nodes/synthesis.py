"""Topic 5 — the synthesis agent (STARTER: implement grounded structured output).

The FinalAnswer / Citation schema is given. Your job: build the prompt from the state's
docs + tool_results, call Instructor with `response_model=FinalAnswer` and a system
prompt that grounds the answer in the supplied context, cites by doc_id, and REFUSES
(confidence < 0.3) when the context is empty.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from ..config import settings
from ..fakes import from_anthropic, traceable
from ..fakes.anthropic_fake import Anthropic

_client = from_anthropic(Anthropic())


class Citation(BaseModel):
    doc_id: str
    quote: str = Field(min_length=10, max_length=240)


class FinalAnswer(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    citations: list[Citation] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


@traceable(name="synthesis_agent", project_name=settings.project_name)
def synthesis_node(state: dict) -> dict:
    # TODO (Topic 5): build docs_block from state['docs'] (as "[doc_id] text") and
    #   api_block from state['tool_results']; call _client.messages.create(
    #   response_model=FinalAnswer, max_retries=2, messages=[...system + user...]).
    #   Return {"answer": answer.model_dump_json()}.
    stub = FinalAnswer(text="TODO: synthesis not implemented yet",
                       citations=[], confidence=0.0)
    return {"answer": stub.model_dump_json()}     # placeholder valid shape
