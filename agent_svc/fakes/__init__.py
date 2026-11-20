"""Local fakes for every keyed / networked service in the capstone.

Import these instead of the real SDKs so the whole thing runs offline on the devbox.
In a real deployment you would swap each import back to its real package.
"""
from . import cohere_fake, mcp_fake, vectorstore_fake
from .anthropic_fake import Anthropic
from .cohere_fake import CohereError
from .instructor_fake import from_anthropic
from .langsmith_fake import (
    Client,
    all_runs,
    get_current_run_tree,
    list_runs,
    reset_runs,
    traceable,
)
from .mcp_fake import ClientSession, open_session

__all__ = [
    "Anthropic", "from_anthropic", "traceable", "get_current_run_tree", "Client",
    "list_runs", "all_runs", "reset_runs", "ClientSession", "open_session",
    "CohereError", "cohere_fake", "mcp_fake", "vectorstore_fake",
]
