"""Make `import agent_svc` resolve when pytest is run from the project root."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
