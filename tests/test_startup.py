import importlib


def test_mcp_server_module_importable():
    assert importlib.import_module("freshrss_agent.mcp_server") is not None
