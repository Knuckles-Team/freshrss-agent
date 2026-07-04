# FreshRSS
## CLI or API | MCP | Agent

![PyPI - Version](https://img.shields.io/pypi/v/freshrss-agent)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
![PyPI - Downloads](https://img.shields.io/pypi/dd/freshrss-agent)
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/freshrss-agent)
![PyPI - License](https://img.shields.io/pypi/l/freshrss-agent)
![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/freshrss-agent)

*Version: 1.0.1*

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

> **Install the slim `[mcp]` extra.** All MCP examples below install
> `freshrss-agent[mcp]` — the MCP-server extra that pulls only the FastMCP /
> FastAPI tooling (`agent-utilities[mcp]`). It deliberately **excludes** the heavy
> agent runtime (the epistemic-graph engine, `pydantic-ai`, `dspy`, `llama-index`,
> `tree-sitter`), so `uvx`/container installs are dramatically smaller and faster.
> Use the full `[agent]` extra only when you need the integrated Pydantic AI agent
> (see [Installation](#installation)).

### Available MCP Tools

_Auto-generated from the live MCP server — do not edit by hand._

<!-- MCP-TOOLS-TABLE:START -->

#### Condensed action-routed tools (default — `MCP_TOOL_MODE=condensed`)

| MCP Tool | Toggle Env Var | Description |
|----------|----------------|-------------|
| `freshrss_reader` | `READERTOOL` | Read FreshRSS streams via the Google Reader API. CONCEPT:FR-OS.identity.frss |
| `freshrss_subscriptions` | `SUBSCRIPTIONSTOOL` | Curate FreshRSS feeds, categories and item tags. CONCEPT:FR-OS.governance.frss |

#### Verbose 1:1 API-mapped tools (`MCP_TOOL_MODE=verbose` or `both`)

<details>
<summary>10 per-operation tools — one per public API method (click to expand)</summary>

| MCP Tool | Toggle Env Var | Description |
|----------|----------------|-------------|
| `freshrss_categories` | `SUBSCRIPTIONS_MIXINTOOL` | List categories / tags (``tag/list``). |
| `freshrss_item_contents` | `READER_MIXINTOOL` | Fetch full contents for specific item ids (GReader ``i`` parameters). |
| `freshrss_label` | `SUBSCRIPTIONS_MIXINTOOL` | Add a category label to an existing feed subscription. |
| `freshrss_mark_read` | `SUBSCRIPTIONS_MIXINTOOL` | Mark one or more items as read. |
| `freshrss_star` | `SUBSCRIPTIONS_MIXINTOOL` | Star or unstar an item. |
| `freshrss_stream_contents` | `READER_MIXINTOOL` | Fetch items for a stream. |
| `freshrss_subscribe` | `SUBSCRIPTIONS_MIXINTOOL` | Subscribe to a feed, optionally setting its title and category. |
| `freshrss_subscription_list` | `SUBSCRIPTIONS_MIXINTOOL` | List all feed subscriptions. |
| `freshrss_unread_count` | `READER_MIXINTOOL` | Return unread counts per stream. |
| `freshrss_unsubscribe` | `SUBSCRIPTIONS_MIXINTOOL` | Unsubscribe from a feed. |

</details>

_2 action-routed tool(s) (default) · 10 verbose 1:1 tool(s). Each is enabled unless its `<DOMAIN>TOOL` toggle is set false; `MCP_TOOL_MODE` selects the surface (`condensed` default · `verbose` 1:1 · `both`). Auto-generated — do not edit._
<!-- MCP-TOOLS-TABLE:END -->

Detailed tool schemas, parameter shapes, and validation constraints are preserved in
[docs/usage.md](docs/usage.md).

### Environment Variables

<!-- ENV-VARS-TABLE:START -->

#### Package environment variables

| Variable | Example | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` |  |
| `PORT` | `8000` |  |
| `TRANSPORT` | `stdio` | options: stdio, streamable-http, sse |
| `ENABLE_OTEL` | `True` |  |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:8080/api/public/otel` |  |
| `OTEL_EXPORTER_OTLP_PUBLIC_KEY` | `pk-...` |  |
| `OTEL_EXPORTER_OTLP_SECRET_KEY` | `sk-...` |  |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `http/protobuf` |  |
| `EUNOMIA_TYPE` | `none` | options: none, embedded, remote |
| `EUNOMIA_POLICY_FILE` | `mcp_policies.json` |  |
| `EUNOMIA_REMOTE_URL` | `http://eunomia-server:8000` |  |
| `FRESHRSS_URL` | `http://localhost:8080` |  |
| `FRESHRSS_USER` | `admin` |  |
| `FRESHRSS_API_PASSWORD` | `your_api_password_here` |  |
| `FRESHRSS_SSL_VERIFY` | `True` |  |
| `READERTOOL` | `True` |  |
| `SUBSCRIPTIONSTOOL` | `True` |  |

#### Inherited agent-utilities variables (apply to every connector)

| Variable | Example | Description |
|----------|---------|-------------|
| `MCP_TOOL_MODE` | `condensed` | Tool surface: `condensed` | `verbose` | `both` |
| `MCP_ENABLED_TOOLS` | — | Comma-separated tool allow-list |
| `MCP_DISABLED_TOOLS` | — | Comma-separated tool deny-list |
| `MCP_ENABLED_TAGS` | — | Comma-separated tag allow-list |
| `MCP_DISABLED_TAGS` | — | Comma-separated tag deny-list |
| `MCP_CLIENT_AUTH` | — | Outbound MCP auth (`oidc-client-credentials` for fleet calls) |
| `OIDC_CLIENT_ID` | — | OIDC client id (service-account auth) |
| `OIDC_CLIENT_SECRET` | — | OIDC client secret (service-account auth) |
| `DEBUG` | `False` | Verbose logging |
| `PYTHONUNBUFFERED` | `1` | Unbuffered stdout (recommended in containers) |
| `MCP_URL` | `http://localhost:8000/mcp` | URL of the MCP server the agent connects to |
| `PROVIDER` | `openai` | LLM provider for the agent |
| `MODEL_ID` | `gpt-4o` | Model id for the agent |
| `ENABLE_WEB_UI` | `True` | Serve the AG-UI web interface |

_17 package + 14 inherited variable(s). Auto-generated from `.env.example` + the shared agent-utilities set — do not edit._
<!-- ENV-VARS-TABLE:END -->


Every variable the server reads. A copy-paste template lives in [`.env.example`](.env.example).

**Connection & Credentials**

| Variable | Description | Default |
|----------|-------------|---------|
| `FRESHRSS_URL` | Base URL of the FreshRSS instance (e.g. `http://freshrss.arpa`) | `http://localhost:8080` |
| `FRESHRSS_USER` | FreshRSS username (GReader `Email` field) | — |
| `FRESHRSS_API_PASSWORD` | FreshRSS **API password** (Settings → Authentication) | — |
| `FRESHRSS_SSL_VERIFY` | Whether to verify TLS certificates | `True` |

**MCP server / transport**

| Variable | Description | Default |
|----------|-------------|---------|
| `TRANSPORT` | `stdio`, `streamable-http`, or `sse` | `stdio` |
| `HOST` | Bind host (HTTP transports) | `0.0.0.0` |
| `PORT` | Bind port (HTTP transports) | `8000` |
| `MCP_TOOL_MODE` | Tool surface: `condensed`, `verbose`, or `both` | `condensed` |

**Telemetry & governance**

| Variable | Description | Default |
|----------|-------------|---------|
| `ENABLE_OTEL` | Enable OpenTelemetry / Langfuse export | `True` |
| `EUNOMIA_TYPE` | Authorization mode: `none`, `embedded`, `remote` | `none` |
| `EUNOMIA_POLICY_FILE` | Embedded policy file | `mcp_policies.json` |
| `EUNOMIA_REMOTE_URL` | Remote Eunomia server URL | — |

**Tool toggles** — each action-routed tool domain can be disabled via its toggle env var
(set to `false`): `READERTOOL`, `SUBSCRIPTIONSTOOL` (see the
[Available MCP Tools](#available-mcp-tools) table above).

### MCP Configuration Examples

<!-- MCP-CONFIG-EXAMPLES:START -->

> **Install the slim `[mcp]` extra.** All examples install `freshrss-agent[mcp]` — the
> MCP-server extra that pulls only the FastMCP / FastAPI tooling (`agent-utilities[mcp]`).
> It deliberately **excludes** the heavy agent runtime (`pydantic-ai`, the epistemic-graph
> engine, `dspy`, `llama-index`), so `uvx` / container installs are far smaller. Use the
> full `[agent]` extra only when you need the integrated Pydantic AI agent.

#### stdio Transport (local IDEs — Cursor, Claude Desktop, VS Code)

```json
{
  "mcpServers": {
    "freshrss-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "freshrss-agent[mcp]",
        "freshrss-mcp"
      ],
      "env": {
        "MCP_TOOL_MODE": "condensed",
        "FRESHRSS_API_PASSWORD": "your_api_password_here",
        "FRESHRSS_URL": "http://localhost:8080",
        "FRESHRSS_USER": "admin",
        "READERTOOL": "True",
        "SUBSCRIPTIONSTOOL": "True"
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
      "args": [
        "--from",
        "freshrss-agent[mcp]",
        "freshrss-mcp",
        "--transport",
        "streamable-http",
        "--port",
        "8000"
      ],
      "env": {
        "TRANSPORT": "streamable-http",
        "HOST": "0.0.0.0",
        "PORT": "8000",
        "MCP_TOOL_MODE": "condensed",
        "FRESHRSS_API_PASSWORD": "your_api_password_here",
        "FRESHRSS_URL": "http://localhost:8080",
        "FRESHRSS_USER": "admin",
        "READERTOOL": "True",
        "SUBSCRIPTIONSTOOL": "True"
      }
    }
  }
}
```

Alternatively, connect to a pre-deployed Streamable-HTTP instance by `url`:

```json
{
  "mcpServers": {
    "freshrss-mcp": {
      "url": "http://localhost:8000/freshrss-mcp/mcp"
    }
  }
}
```

Deploying the Streamable-HTTP server via Docker:

```bash
docker run -d \
  --name freshrss-mcp-mcp \
  -p 8000:8000 \
  -e TRANSPORT=streamable-http \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  -e MCP_TOOL_MODE=condensed \
  -e FRESHRSS_API_PASSWORD=your_api_password_here \
  -e FRESHRSS_URL=http://localhost:8080 \
  -e FRESHRSS_USER=admin \
  -e READERTOOL=True \
  -e SUBSCRIPTIONSTOOL=True \
  knucklessg1/freshrss-agent:mcp
```

_Auto-generated from the code-read env surface (`MCP_TOOL_MODE` + package vars) — do not edit._
<!-- MCP-CONFIG-EXAMPLES:END -->

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

Pick the extra that matches what you want to run:

| Extra | Installs | Use when |
|-------|----------|----------|
| `freshrss-agent[mcp]` | Slim MCP server only (`agent-utilities[mcp]` — FastMCP/FastAPI) | You only run the **MCP server** (smallest install / image) |
| `freshrss-agent[agent]` | Full agent runtime (`agent-utilities[agent,logfire]` — Pydantic AI + the epistemic-graph engine) | You run the **integrated agent** |
| `freshrss-agent[all]` | Everything (`mcp` + `agent` + `logfire`) | Development / both surfaces |

```bash
# MCP server only (recommended for tool hosting — slim deps)
uv pip install "freshrss-agent[mcp]"

# Full agent runtime (Pydantic AI + epistemic-graph engine)
uv pip install "freshrss-agent[agent]"

# Everything (development)
uv pip install "freshrss-agent[all]"      # or: python -m pip install "freshrss-agent[all]"
```

After installation two console scripts are available:

```bash
freshrss-mcp      # run the MCP server
freshrss-agent    # run the A2A agent server
```

### Container images (`:mcp` vs `:agent`)

One multi-stage `docker/Dockerfile` builds two right-sized images, selected by `--target`:

| Image tag | Build target | Contents | Entrypoint |
|-----------|--------------|----------|------------|
| `knucklessg1/freshrss-agent:mcp` | `--target mcp` | `freshrss-agent[mcp]` — **slim**, no engine/`pydantic-ai`/`dspy`/`llama-index`/`tree-sitter` | `freshrss-mcp` |
| `knucklessg1/freshrss-agent:latest` | `--target agent` (default) | `freshrss-agent[agent]` — **full** agent runtime + epistemic-graph engine | `freshrss-agent` |

```bash
docker build --target mcp   -t knucklessg1/freshrss-agent:mcp    docker/   # slim MCP server
docker build --target agent -t knucklessg1/freshrss-agent:latest docker/   # full agent
```

`docker/mcp.compose.yml` runs the slim `:mcp` server; `docker/agent.compose.yml` runs the
agent (`:latest`) with a co-located `:mcp` sidecar.

### Knowledge-graph database (`epistemic-graph`)

The **full agent** (`[agent]` / `:latest`) embeds the **epistemic-graph** engine (pulled in
transitively via `agent-utilities[agent]`). For production — or to share one knowledge graph
across multiple agents — run **epistemic-graph as its own database container** and point the
agent at it instead of embedding it. Deployment recipes (single-node + Raft HA), connection
config, and the full database architecture (with diagrams) are documented in the
[epistemic-graph deployment guide](https://knuckles-team.github.io/epistemic-graph/deployment/).
The slim `[mcp]` server does **not** require the database.

## Documentation

Full installation, deployment, usage, and platform-provisioning guides live in the
[`docs/`](docs/) directory and are published via mkdocs + GitHub Pages at the
[official documentation site](https://knuckles-team.github.io/freshrss-agent/):

- [Overview](docs/overview.md) · [Installation](docs/installation.md) ·
  [Usage](docs/usage.md) · [Deployment](docs/deployment.md) ·
  [Platform](docs/platform.md) · [Concepts](docs/concepts.md)
