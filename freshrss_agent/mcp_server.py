#!/usr/bin/python


from .mcp import register_ingest_tools  # noqa: F401

# SDK discovery registers the register_<tag>_tools functions bound in this module.
# The reader and subscription tools are derived one per client method from the API class.
__all__ = ["register_ingest_tools"]
