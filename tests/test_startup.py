import importlib

import pytest


@pytest.mark.concept("FRSS-001")
def test_mcp_server_module_importable():
    """CONCEPT:FRSS-001 The MCP server entry module imports without side effects."""
    assert importlib.import_module("freshrss_agent.mcp_server") is not None
