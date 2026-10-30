# freshrss-agent — Concept Overview

> Built on [`scion-sdk`](https://github.com/Knuckles-Team/scion-sdk) — the unified AGI Harness.

## Description

`freshrss-agent` wraps a self-hosted **FreshRSS** RSS reader through its
**Google Reader compatible API** (GReader, served at
`{FRESHRSS_URL}/api/greader.php`). It exposes two action-routed MCP tool domains —
`freshrss_reader` (stream contents, item bodies, unread counts) and
`freshrss_subscriptions` (subscribe/unsubscribe/label feeds, browse categories,
`stream_contents` action is consumed directly by the scion-sdk Knowledge
Graph connector preset to ingest feed items.

## Architecture

This project follows the standardized agent-package pattern:

- **Modular Design**: split into `api/` (client mixins) and `mcp/` (action-routed
  tool modules) for cleaner organization.
- **Dynamic Tool Registration**: action-routed dynamic tool tags, strictly
  lowercase, each togglable with a `*TOOL` environment flag.

## Concept Registry

This project implements or inherits the following ecosystem concepts:

| Concept ID | Description | Source |
|:-----------|:------------|:-------|
| ECO-4.1 | MCP & Universal Skills | `scion-sdk` (inherited) |

> 📖 **Full Registry**: See [`scion-sdk/docs/overview.md`](https://github.com/Knuckles-Team/scion-sdk/blob/main/docs/overview.md) for the complete 5-Pillar concept index.
