import importlib

import pytest


@pytest.mark.concept("FR-OS.identity.frss")
def test_mcp_server_module_importable():
    """CONCEPT:FR-OS.identity.frss The MCP server entry module imports without side effects."""
    assert importlib.import_module("freshrss_agent.mcp_server") is not None
