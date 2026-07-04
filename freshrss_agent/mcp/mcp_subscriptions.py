#!/usr/bin/python
"""MCP tools for FreshRSS subscription, category and tagging operations."""

import json

from agent_utilities.mcp_utilities import resolve_action, run_blocking
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ..auth import get_client


def register_subscriptions_tools(mcp: FastMCP):
    """Register subscriptions tag dynamic tools."""

    @mcp.tool(tags={"subscriptions"})
    async def freshrss_subscriptions(
        action: str = Field(
            description="Action to perform. Must be one of: "
            "'list', 'subscribe', 'unsubscribe', 'label', 'categories', "
            "'mark_read', 'star'."
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Curate FreshRSS feeds, categories and item tags. CONCEPT:FR-OS.governance.frss

        Manage subscriptions (``subscribe``/``unsubscribe``/``label``), browse
        ``list``/``categories``, and tag items (``mark_read``/``star``). Write
        actions transparently fetch the GReader POST token.
        """
        if ctx:
            await ctx.info("Executing subscriptions tool...")

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # Action-router trio: resolve_action validates/canonicalizes (and serves the
        # discovery payload), run_blocking runs the sync client call off the event loop.
        resolved = resolve_action(
            action,
            {
                "list",
                "subscribe",
                "unsubscribe",
                "label",
                "categories",
                "mark_read",
                "star",
            },
            service="freshrss-agent",
        )
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "list":
            return await run_blocking(client.subscription_list, **kwargs)
        if action == "subscribe":
            return await run_blocking(client.subscribe, **kwargs)
        if action == "unsubscribe":
            return await run_blocking(client.unsubscribe, **kwargs)
        if action == "label":
            return await run_blocking(client.label, **kwargs)
        if action == "categories":
            return await run_blocking(client.categories, **kwargs)
        if action == "mark_read":
            return await run_blocking(client.mark_read, **kwargs)
        if action == "star":
            return await run_blocking(client.star, **kwargs)
        raise ValueError(f"Unknown action: {action}")
