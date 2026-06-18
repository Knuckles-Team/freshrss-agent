#!/usr/bin/python

import logging
import os
import sys
from typing import Any

from agent_utilities.base_utilities import get_logger, to_boolean
from agent_utilities.mcp_utilities import create_mcp_server
from dotenv import find_dotenv, load_dotenv

from .mcp import register_reader_tools, register_subscriptions_tools

__version__ = "0.1.0"

logger = get_logger(name="MCP_Server")
logger.setLevel(logging.INFO)


def get_mcp_instance() -> tuple[Any, Any, Any]:
    """Initialize and return the FreshRSS MCP instance, args, and middlewares."""
    load_dotenv(find_dotenv())

    args, mcp, middlewares = create_mcp_server(
        name="FreshRSS MCP",
        version=__version__,
        instructions="FreshRSS MCP Server — Condensed Action-Routed Tools.",
    )

    DEFAULT_READERTOOL = to_boolean(os.getenv("READERTOOL", "True"))
    if DEFAULT_READERTOOL:
        register_reader_tools(mcp)

    DEFAULT_SUBSCRIPTIONSTOOL = to_boolean(os.getenv("SUBSCRIPTIONSTOOL", "True"))
    if DEFAULT_SUBSCRIPTIONSTOOL:
        register_subscriptions_tools(mcp)

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
