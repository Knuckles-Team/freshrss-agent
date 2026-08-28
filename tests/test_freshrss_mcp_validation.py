import asyncio
import json
from pathlib import Path

import pytest
from agent_utilities.protocols.source_connectors.tool_schema import (
    canonical_input_schema,
    compatibility_fingerprint,
)

from freshrss_agent.mcp_server import get_mcp_instance

CONNECTORS = Path(__file__).resolve().parents[1] / "freshrss_agent" / "connectors"


@pytest.mark.concept("FR-OS.identity.frss")
@pytest.mark.concept("FR-OS.governance.frss")
def test_mcp_instance_registers_reader_and_subscriptions(monkeypatch):
    """CONCEPT:FR-OS.identity.frss CONCEPT:FR-OS.governance.frss Both action-routed tool domains register."""
    monkeypatch.setattr("sys.argv", ["freshrss-mcp"])
    mcp, args, middlewares = get_mcp_instance()
    assert mcp is not None

    tools = asyncio.run(mcp.list_tools())
    tool_names = {tool.name for tool in tools}
    assert "freshrss_reader" in tool_names
    assert "freshrss_subscriptions" in tool_names


@pytest.mark.concept("FR-OS.governance.frss")
def test_source_preset_is_provider_owned_and_matches_live_reader_schema(monkeypatch):
    """The source contract and schema pin describe the real FreshRSS reader."""
    preset_document = json.loads(
        (CONNECTORS / "mcp_source_presets.json").read_text(encoding="utf-8")
    )
    assert set(key for key in preset_document if not key.startswith("_")) == {
        "freshrss"
    }
    preset = preset_document["freshrss"]
    assert preset == {
        "server": "freshrss-mcp",
        "tool": "freshrss_reader",
        "action": "stream_contents",
        "params_style": "json",
        "params": {"count": 100, "order": "o"},
        "records_path": "items",
        "id_field": "id",
        "title_field": "title",
        "text_field": "text",
        "updated_field": "published",
        "updated_since_param": "newer_than",
        "pagination": "cursor",
        "cursor_param": "continuation",
        "cursor_path": "continuation",
        "doc_type": "news_article",
    }

    monkeypatch.setattr("sys.argv", ["freshrss-mcp"])
    mcp, _args, _middlewares = get_mcp_instance()
    tools = asyncio.run(mcp.list_tools())
    reader = next(tool for tool in tools if tool.name == "freshrss_reader")
    expected = compatibility_fingerprint(
        reader.name,
        canonical_input_schema(reader, include_presentation=False),
    )
    sidecar = json.loads(
        (CONNECTORS / "tool_schema_fingerprints.json").read_text(encoding="utf-8")
    )
    assert sidecar == {
        "algorithm": "agent-utilities:mcp-tool-schema-compat:v1",
        "connector": "freshrss-agent",
        "schema_version": "1",
        "tools": {"freshrss_reader": expected},
    }


@pytest.mark.concept("FR-OS.governance.frss")
def test_reader_dispatch_has_no_dead_unknown_action_fallback():
    """BUG-CX-045: `resolve_action(action, {"stream_contents", "item_contents",
    "unread_count"}, ...)` runs BEFORE the if-chain in `freshrss_reader` and
    either raises its own rich did-you-mean `ValueError` for anything outside
    that exact 3-member set, or returns one of those 3 members -- the if-chain
    below covers all 3, so the trailing `raise ValueError(f"Unknown action:
    {action}")` can never execute. It is dead code that the complexity gate
    still counts as a branch. Structural proof it is gone."""
    import inspect

    from freshrss_agent.mcp import mcp_reader

    src = inspect.getsource(mcp_reader.register_reader_tools)
    assert 'raise ValueError(f"Unknown action: {action}")' not in src, (
        "the trailing Unknown-action raise after the if-chain is unreachable "
        "(resolve_action already raised or canonicalized above it) -- BUG-CX-045"
    )


@pytest.mark.concept("FR-OS.governance.frss")
def test_reader_invalid_action_still_raises_resolve_action_error(monkeypatch):
    """Removing the dead fallback must not change observable behaviour: an
    unknown action still raises resolve_action's rich, did-you-mean ValueError
    -- never an unhandled error from a missing branch."""
    from unittest.mock import MagicMock

    monkeypatch.setattr("sys.argv", ["freshrss-mcp"])
    mcp, _args, _middlewares = get_mcp_instance()
    tools = asyncio.run(mcp.list_tools())
    reader = next(tool for tool in tools if tool.name == "freshrss_reader")

    with pytest.raises(ValueError, match="Unknown action"):
        asyncio.run(
            reader.fn(
                action="totally_bogus_action",
                params_json="{}",
                client=MagicMock(),
                ctx=None,
            )
        )
