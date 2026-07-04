# freshrss-agent — Concept Overview

> **Category**: Integration | **Ecosystem Role**: MCP Server + A2A Agent
> Built on [`agent-utilities`](https://github.com/Knuckles-Team/agent-utilities) — the unified AGI Harness.

## Description

`freshrss-agent` wraps a self-hosted **FreshRSS** RSS reader through its
**Google Reader compatible API** (GReader, served at
`{FRESHRSS_URL}/api/greader.php`). It exposes two action-routed MCP tool domains —
`freshrss_reader` (stream contents, item bodies, unread counts) and
`freshrss_subscriptions` (subscribe/unsubscribe/label feeds, browse categories,
mark items read or starred) — plus a Python API and an A2A agent. The reader's
`stream_contents` action is consumed directly by the agent-utilities Knowledge
Graph connector preset to ingest feed items.

## Architecture

This project follows the standardized agent-package pattern:

- **Modular Design**: split into `api/` (client mixins) and `mcp/` (action-routed
  tool modules) for cleaner organization.
- **Dynamic Tool Registration**: action-routed dynamic tool tags, strictly
  lowercase, each togglable with a `*TOOL` environment flag.
- **A2A Agent Server**: a Pydantic-AI graph agent (console script `freshrss-agent`)
  that calls the MCP tool surface and exposes an AG-UI web interface.

## Concept Registry

This project implements or inherits the following ecosystem concepts:

| Concept ID | Description | Source |
|:-----------|:------------|:-------|
| ECO-4.1 | MCP & Universal Skills | `agent-utilities` (inherited) |
| AU-ECO.toolkit.journey-map-narrative | A2A Network & Consensus | `agent-utilities` (inherited) |

> 📖 **Full Registry**: See [`agent-utilities/docs/overview.md`](https://github.com/Knuckles-Team/agent-utilities/blob/main/docs/overview.md) for the complete 5-Pillar concept index.
