"""Root conftest.py — pytest session configuration.

Adds tools/mcp-server to sys.path so that ``import server`` (and
``from server import ...``) works in test_mcp_server.py without needing a
Python-legal package name for the hyphenated directory.
"""

import sys
from pathlib import Path

# Make tools/mcp-server importable as the top-level ``mcp_server`` package
_MCP_SERVER_DIR = Path(__file__).parent / "tools" / "mcp-server"
if str(_MCP_SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(_MCP_SERVER_DIR))
