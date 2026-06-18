# FreshRSS
## CLI or API | MCP | Agent

![PyPI - Version](https://img.shields.io/pypi/v/freshrss-agent)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
![PyPI - Downloads](https://img.shields.io/pypi/dd/freshrss-agent)
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/freshrss-agent)
![PyPI - License](https://img.shields.io/pypi/l/freshrss-agent)
![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/freshrss-agent)

*Version: 0.1.0*

> **Documentation** — Installation, deployment, usage across the API, CLI, and MCP
> interfaces, the integrated A2A agent server, and guidance for provisioning the
> backing platform are maintained in the
> [official documentation](https://knuckles-team.github.io/freshrss-agent/).

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [MCP](#mcp)
  - [Available MCP Tools](#available-mcp-tools)
  - [Environment Variables](#environment-variables)
  - [Transport Configuration Examples](#stdio-transport-local-ides--cursor-claude-desktop-vs-code)
  - [Additional Deployment Options](#additional-deployment-options)
- [Usage](#usage)
- [Installation](#installation)
- [Documentation](#documentation)

---

## Overview

**FreshRSS MCP Server + A2A Agent**

A connector for the self-hosted [FreshRSS](https://freshrss.org/) RSS reader,
wrapping its **Google Reader compatible API** (GReader). It exposes two
action-routed MCP tool domains:

- **`freshrss_reader`** — `stream_contents` (feed items + continuation), `item_contents`, `unread_count`.
- **`freshrss_subscriptions`** — `list`, `subscribe`, `unsubscribe`, `label`, `categories`, `mark_read`, `star`.

This repository is actively maintained - Contributions are welcome!

---

## Key Features

- **Consolidated Action-Routed MCP Tools:** Two togglable tool domains group every
  GReader operation, minimizing token overhead and tool bloat in LLM contexts.
- **Google Reader Compatible:** Wraps the FreshRSS GReader API — `ClientLogin` auth,
  transparent re-authentication on `401`, and automatic write-token handling.
- **Enterprise-Grade Security:** OIDC token delegation (RFC 8693), Eunomia policy
  enforcement, and per-instance credential resolution.
- **Integrated A2A Agent:** Built-in Pydantic AI agent server alongside the MCP server.
- **Native Telemetry & Tracing:** Out-of-the-box OpenTelemetry exports and Langfuse tracing.

---

## MCP

### Available MCP Tools

This server uses dynamic Action-Routed tools to optimize token overhead and maximize
IDE compatibility. Each tool takes an `action` plus a `params_json` payload.

| Tool Module | Toggle Env Var | Enabled by Default | Description & Action-Routed Methods |
|-------------|----------------|--------------------|-------------------------------------|
| **Reader** | `READERTOOL` | `True` | Read FreshRSS streams via the GReader API. Action-routed methods: `stream_contents`, `item_contents`, `unread_count`. |
| **Subscriptions** | `SUBSCRIPTIONSTOOL` | `True` | Curate feeds, categories, and item tags. Action-routed methods: `list`, `subscribe`, `unsubscribe`, `label`, `categories`, `mark_read`, `star`. |

Detailed tool schemas, parameter shapes, and validation constraints are preserved in
[docs/usage.md](docs/usage.md).

### Environment Variables

The MCP Server can be run in `stdio` (local), `streamable-http` (networked), or
`sse` mode.

*   `FRESHRSS_URL`: The base URL of the FreshRSS instance (e.g. `http://freshrss.arpa`).
*   `FRESHRSS_USER`: The FreshRSS username (GReader `Email` field).
*   `FRESHRSS_API_PASSWORD`: The FreshRSS **API password** (Settings → Authentication).
*   `FRESHRSS_SSL_VERIFY`: Whether to verify TLS certificates (default `True`).

#### stdio Transport (local IDEs - Cursor, Claude Desktop, VS Code)

```json
{
  "mcpServers": {
    "freshrss-mcp": {
      "command": "uvx",
      "args": ["--from", "freshrss-agent", "freshrss-mcp"],
      "env": {
        "FRESHRSS_URL": "https://service.example.com",
        "FRESHRSS_USER": "admin",
        "FRESHRSS_API_PASSWORD": "your_api_password"
      }
    }
  }
}
```

#### Streamable-HTTP Transport (networked / production)

```json
{
  "mcpServers": {
    "freshrss-mcp": {
      "command": "uvx",
      "args": ["--from", "freshrss-agent", "freshrss-mcp", "--transport", "streamable-http", "--port", "8000"],
      "env": {
        "TRANSPORT": "streamable-http",
        "HOST": "0.0.0.0",
        "PORT": "8000",
        "FRESHRSS_URL": "https://service.example.com",
        "FRESHRSS_USER": "admin",
        "FRESHRSS_API_PASSWORD": "your_api_password"
      }
    }
  }
}
```

<!-- BEGIN GENERATED: additional-deployment-options -->
### Additional Deployment Options

`freshrss-agent` can also run as a **local container** (Docker / Podman / `uv`) or be
consumed from a **remote deployment**. The
[Deployment guide](https://knuckles-team.github.io/freshrss-agent/deployment/) has full,
copy-paste `mcp_config.json` for all four transports — **stdio**, **streamable-http**,
**local container / uv**, and **remote URL**:

- **Local container / uv** — launch the server from `mcp_config.json` via `uvx`,
  `docker run`, or `podman run`, or point at a local streamable-http container by `url`.
- **Remote URL** — connect to a server deployed behind Caddy at
  `http://freshrss-mcp.arpa/mcp` using the `"url"` key.
<!-- END GENERATED: additional-deployment-options -->

## Usage

Once configured, an LLM (or a direct caller) invokes a tool domain with an `action`
and a JSON `params_json` payload. Examples:

```jsonc
// Fetch the 50 most recent unread items, newest first
{
  "tool": "freshrss_reader",
  "action": "stream_contents",
  "params_json": "{\"count\": 50, \"order\": \"n\"}"
}

// Subscribe to a feed and file it under a category
{
  "tool": "freshrss_subscriptions",
  "action": "subscribe",
  "params_json": "{\"feed_url\": \"http://example.com/rss\", \"category\": \"News\"}"
}

// Mark items as read
{
  "tool": "freshrss_subscriptions",
  "action": "mark_read",
  "params_json": "{\"item_ids\": [\"tag:google.com,2005:reader/item/0001\"]}"
}
```

Invoking a tool with an unknown or omitted `action` returns the discovery payload
listing every valid action for that domain.

## Installation

```bash
# Using uv (recommended)
uv pip install freshrss-agent

# Using standard pip
python -m pip install freshrss-agent
```

After installation two console scripts are available:

```bash
freshrss-mcp      # run the MCP server
freshrss-agent    # run the A2A agent server
```

## Documentation

Full installation, deployment, usage, and platform-provisioning guides live in the
[`docs/`](docs/) directory and are published via mkdocs + GitHub Pages at the
[official documentation site](https://knuckles-team.github.io/freshrss-agent/):

- [Overview](docs/overview.md) · [Installation](docs/installation.md) ·
  [Usage](docs/usage.md) · [Deployment](docs/deployment.md) ·
  [Platform](docs/platform.md) · [Concepts](docs/concepts.md)
