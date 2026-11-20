import pytest

from agent_svc import mock_backend as mb
from agent_svc import monitoring as mon
from agent_svc.fakes import langsmith_fake as ls


@pytest.fixture(autouse=True)
def _clean_state():
    """Reset all in-memory state before each test so they're deterministic + isolated."""
    mb.reset()
    ls.reset_runs()
    mon.reset_metrics()
    yield
