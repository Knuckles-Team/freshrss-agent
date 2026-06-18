import asyncio

from freshrss_agent.mcp_server import get_mcp_instance


def test_mcp_instance_registers_reader_and_subscriptions(monkeypatch):
    monkeypatch.setattr("sys.argv", ["freshrss-mcp"])
    mcp, args, middlewares = get_mcp_instance()
    assert mcp is not None

    tools = asyncio.run(mcp.get_tools())
    tool_names = set(tools.keys())
    assert "freshrss_reader" in tool_names
    assert "freshrss_subscriptions" in tool_names
