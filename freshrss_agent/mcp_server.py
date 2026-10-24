#!/usr/bin/python


from .mcp import (  # noqa: F401
    register_ingest_tools,
    register_reader_tools,
    register_subscriptions_tools,
)

# SDK discovery registers the register_<tag>_tools functions bound in this module.
__all__ = [
    "register_ingest_tools",
    "register_reader_tools",
    "register_subscriptions_tools",
]
