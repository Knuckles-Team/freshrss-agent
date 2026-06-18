# Usage — API / CLI / MCP

`freshrss-agent` exposes the same capability three ways: as **MCP tools** an agent
calls, as a **Python API** you import, and as a **CLI**.

## As an MCP server

Once [deployed](deployment.md), the server registers consolidated, action-routed
tool modules. Each module is independently togglable with a `*TOOL` environment
flag.

The MCP surface is split into two action-routed tools:

- **`freshrss_reader`** (toggle `READERTOOL`) — actions `stream_contents`,
  `item_contents`, `unread_count`. `stream_contents` returns the raw
  `{"items": [...], "continuation": "..."}` payload with full item bodies, and
  accepts `stream_id`, `count`, `order`, `newer_than` (a unix-seconds delta
  watermark) and `continuation`.
- **`freshrss_subscriptions`** (toggle `SUBSCRIPTIONSTOOL`) — actions `list`,
  `subscribe`, `unsubscribe`, `label`, `categories`, `mark_read`, `star`.

## As a Python API

```python
from freshrss_agent.auth import get_client

# reads FRESHRSS_URL / FRESHRSS_USER / FRESHRSS_API_PASSWORD from the environment / .env
api = get_client()
page = api.stream_contents(count=50)          # {"items": [...], "continuation": "..."}
subs = api.subscription_list()
api.mark_read([item["id"] for item in page["items"]])
```

## As a CLI

```bash
export FRESHRSS_URL="http://freshrss.arpa"
export FRESHRSS_USER="admin"
export FRESHRSS_API_PASSWORD="your_api_password"
freshrss-mcp --transport stdio
```
