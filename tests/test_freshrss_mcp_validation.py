import asyncio
from pathlib import Path

import pytest

from scion_sdk.connector import build_server

CONNECTORS = Path(__file__).resolve().parents[1] / "freshrss_agent" / "connectors"


@pytest.mark.concept("FR-OS.identity.frss")
@pytest.mark.concept("FR-OS.governance.frss")
def test_mcp_instance_registers_reader_and_subscriptions(monkeypatch):
    """CONCEPT:FR-OS.identity.frss CONCEPT:FR-OS.governance.frss Both action-routed tool domains register."""
    monkeypatch.setattr("sys.argv", ["freshrss-mcp"])
    _, mcp = build_server("freshrss_agent", command_args=[])
    assert mcp is not None

    tools = asyncio.run(mcp.list_tools())
    tool_names = {tool.name for tool in tools}
    assert "freshrss_stream_contents" in tool_names
    assert "freshrss_reader" not in tool_names
    assert "freshrss_subscriptions" not in tool_names
