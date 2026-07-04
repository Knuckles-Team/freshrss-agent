#!/usr/bin/python
"""MCP tools for FreshRSS reader operations."""

import json

from agent_utilities.mcp_utilities import resolve_action, run_blocking
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ..auth import get_client


def register_reader_tools(mcp: FastMCP):
    """Register reader tag dynamic tools."""

    @mcp.tool(tags={"reader"})
    async def freshrss_reader(
        action: str = Field(
            description="Action to perform. Must be one of: "
            "'stream_contents', 'item_contents', 'unread_count'."
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Read FreshRSS streams via the Google Reader API. CONCEPT:FR-OS.identity.frss

        ``stream_contents`` accepts ``stream_id``, ``count``, ``order``,
        ``newer_than`` (a unix-seconds delta watermark mapped to GReader ``ot``)
        and ``continuation``, and returns the raw
        ``{"items": [...], "continuation": "..."}`` payload with full item bodies.
        """
        if ctx:
            await ctx.info("Executing reader tool...")

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # Action-router trio: resolve_action validates/canonicalizes (and serves the
        # discovery payload), run_blocking runs the sync client call off the event loop.
        resolved = resolve_action(
            action,
            {"stream_contents", "item_contents", "unread_count"},
            service="freshrss-agent",
        )
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "stream_contents":
            return await run_blocking(client.stream_contents, **kwargs)
        if action == "item_contents":
            return await run_blocking(client.item_contents, **kwargs)
        if action == "unread_count":
            return await run_blocking(client.unread_count, **kwargs)
        raise ValueError(f"Unknown action: {action}")
