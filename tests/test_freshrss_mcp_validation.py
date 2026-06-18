import asyncio

import pytest

from freshrss_agent.mcp_server import get_mcp_instance


@pytest.mark.concept("FRSS-001")
@pytest.mark.concept("FRSS-002")
def test_mcp_instance_registers_reader_and_subscriptions(monkeypatch):
    """CONCEPT:FRSS-001 CONCEPT:FRSS-002 Both action-routed tool domains register."""
    monkeypatch.setattr("sys.argv", ["freshrss-mcp"])
    mcp, args, middlewares = get_mcp_instance()
    assert mcp is not None

    tools = asyncio.run(mcp.list_tools())
    tool_names = {tool.name for tool in tools}
    assert "freshrss_reader" in tool_names
    assert "freshrss_subscriptions" in tool_names
