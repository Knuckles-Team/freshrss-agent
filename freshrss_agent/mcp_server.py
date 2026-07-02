#!/usr/bin/python

import logging
import sys
from typing import Any

from agent_utilities.base_utilities import get_logger
from agent_utilities.mcp_utilities import (
    create_mcp_server,
    load_config,
    register_tool_surface,
)

from .api import ApiClientSystem
from .auth import get_client
from .mcp import register_reader_tools, register_subscriptions_tools  # noqa: F401

__version__ = "1.0.1"

logger = get_logger(name="MCP_Server")
logger.setLevel(logging.INFO)


def get_mcp_instance() -> tuple[Any, Any, Any]:
    """Initialize and return the FreshRSS MCP instance, args, and middlewares."""
    load_config()

    args, mcp, middlewares = create_mcp_server(
        name="FreshRSS MCP",
        version=__version__,
        instructions="FreshRSS MCP Server — Condensed Action-Routed Tools.",
    )

    register_tool_surface(
        mcp,
        client_cls=ApiClientSystem,
        get_client=get_client,
        service="freshrss-agent",
        tools_module=sys.modules[__name__],
    )

    for mw in middlewares:
        mcp.add_middleware(mw)

    return mcp, args, middlewares


def mcp_server():
    mcp, args, _ = get_mcp_instance()

    print(f"FreshRSS MCP v{__version__}", file=sys.stderr)
    print("\nStarting MCP Server", file=sys.stderr)
    print(f"  Transport: {args.transport.upper()}", file=sys.stderr)

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "streamable-http":
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    elif args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        logger.error(f"Invalid transport: {args.transport}")
        sys.exit(1)


if __name__ == "__main__":
    mcp_server()
