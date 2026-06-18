# Usage — API / CLI / MCP

`freshrss-agent` exposes the same capability three ways: as **MCP tools** an agent
calls, as a **Python API** you import, and as a **CLI**.

## As an MCP server

Once [deployed](deployment.md), the server registers consolidated, action-routed
tool modules. Each module is independently togglable with a `*TOOL` environment
flag.

## As a Python API

```python
from freshrss_agent.auth import get_client

api = get_client()        # reads FRESHRSS_URL / FRESHRSS_API_PASSWORD from the environment / .env
status = api.get_system_status()
```

## As a CLI

```bash
export FRESHRSS_URL="http://localhost:8080"
export FRESHRSS_API_PASSWORD="your_token"
freshrss-mcp --transport stdio
```
