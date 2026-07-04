#!/usr/bin/python
"""Wire-First MCP tools: native ingestion of FreshRSS records into epistemic-graph."""

import json

from agent_utilities.mcp_utilities import run_blocking
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ..auth import get_client


def register_ingest_tools(mcp: FastMCP):
    """Register the freshrss KG ingestion tools."""

    @mcp.tool(tags={"misc", "kg"})
    async def freshrss_ingest_items(
        params_json: str = Field(
            default="{}",
            description="JSON string of stream_contents params (stream_id, count, "
            "order, newer_than, continuation).",
        ),
        client=Depends(get_client),
        ctx: Context | None = None,
    ) -> dict:
        """Natively ingest FreshRSS feed items into epistemic-graph as :Document nodes.

        Fetches a stream via the GReader API and pushes the items (title + body +
        source_uri + originating feed) into the knowledge graph via the fast engine
        client. Best-effort: returns ``{"ingested": None}`` when no engine is
        reachable. CONCEPT:AU-KG.ingest.enterprise-source-extractor.
        """
        from ..kg_ingest import ingest_feed_items

        try:
            kwargs = json.loads(params_json) if params_json else {}
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        if ctx:
            await ctx.info("Fetching stream for ingestion...")
        result = await run_blocking(client.stream_contents, **kwargs)
        items = result.get("items", []) if isinstance(result, dict) else []
        ingested = ingest_feed_items(items)
        return {"listed": len(items), "ingested": ingested}

    @mcp.tool(tags={"misc", "kg"})
    async def freshrss_ingest_subscriptions(
        params_json: str = Field(
            default="{}",
            description="JSON string of options (currently none; reserved).",
        ),
        client=Depends(get_client),
        ctx: Context | None = None,
    ) -> dict:
        """Natively ingest FreshRSS subscriptions into epistemic-graph as typed nodes.

        Lists feed subscriptions via the GReader API and pushes them as
        :FeedSubscription nodes with their :FeedCategory folders and :inCategory
        links. Best-effort: returns ``{"ingested": None}`` when no engine is
        reachable. CONCEPT:AU-KG.ingest.enterprise-source-extractor.
        """
        from ..kg_ingest import ingest_subscriptions

        if ctx:
            await ctx.info("Listing subscriptions for ingestion...")
        result = await run_blocking(client.subscription_list)
        subs = result.get("subscriptions", []) if isinstance(result, dict) else []
        ingested = ingest_subscriptions(subs)
        return {"listed": len(subs), "ingested": ingested}

    return None
