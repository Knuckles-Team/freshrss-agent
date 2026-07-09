---
name: freshrss-feed-reader
skill_type: skill
description: >-
  Read FreshRSS streams over the Google Reader (GReader) API via the
  freshrss-agent MCP server — fetch stream contents for the reading-list, a
  single feed, or a category label, page through with a continuation cursor,
  pull full item bodies, and check per-stream unread counts. Use when the agent
  must triage what is new, fetch article bodies, or take a delta since a
  watermark. Do NOT use to subscribe/label/star feeds (use
  freshrss-subscription-management) or to push items into the knowledge graph
  (use freshrss-knowledge-ingestion).
license: MIT
tags: [freshrss, rss, greader, reader, feeds, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# FreshRSS Feed Reader

Read-side access to FreshRSS through the Google Reader compatible API. Prefer
these tools over raw HTTP — they normalize each item to a flat, transport-safe
`text` + `url` so downstream steps read the body directly.

## When to use
- Triage what is new in the reading-list or a specific feed/label.
- Fetch the full body of specific items.
- Take a delta since a known timestamp (only items newer than a watermark).
- Check unread counts per stream.

## When NOT to use
- Subscribe, unsubscribe, label, star, or mark-read → `freshrss-subscription-management`.
- Push feed items/sources into the knowledge graph → `freshrss-knowledge-ingestion`.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`freshrss-agent`** MCP server.

| Variable | Required | Notes |
|----------|----------|-------|
| `FRESHRSS_URL` | ✅ | Base URL of the FreshRSS instance |
| `FRESHRSS_USER` | ✅ | GReader account username |
| `FRESHRSS_API_PASSWORD` | ✅ | GReader API password (Settings → Profile → API) |
| `FRESHRSS_SSL_VERIFY` | optional | TLS verification toggle |

`MCP_TOOL_MODE` (`condensed`|`verbose`|`both`) selects the condensed surface
(used below) vs. the one-to-one verbose tools.

## Tools & actions
Prefer the **condensed** tool; it takes `action` + a `params_json` **JSON string**.

| Condensed tool | Actions |
|----------------|---------|
| `freshrss_reader` | `stream_contents`, `item_contents`, `unread_count` |

### Key parameters (`stream_contents`)
- `stream_id` — `user/-/state/com.google/reading-list` (all), `feed/<feedUrl>` (one
  feed), or `user/-/label/<category>` (a category). Defaults to the reading-list.
- `count` — max items (GReader `n`, default 100).
- `order` — `o` oldest-first or `n` newest-first (GReader `r`).
- `newer_than` — unix-seconds watermark; excludes items older than this (GReader `ot`).
- `continuation` — cursor from the previous page to resume.

## Recipes (`params_json`)
Newest 25 items across everything:
```json
{"stream_id":"user/-/state/com.google/reading-list","count":25,"order":"n"}
```
Delta since a watermark (only items newer than a unix timestamp):
```json
{"stream_id":"user/-/state/com.google/reading-list","newer_than":1719792000,"count":200}
```
Page 2 using the continuation returned by page 1:
```json
{"stream_id":"user/-/state/com.google/reading-list","count":200,"continuation":"<token>"}
```
Full bodies for specific item ids:
```json
{"item_ids":["tag:google.com,2005:reader/item/00000000abcd"]}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- `stream_contents` returns `{"items":[...],"continuation":"..."}`; when
  `continuation` is present there are more pages — loop until it is absent.
- Each item is normalized with a flat `text` (body) and `url` (canonical href)
  alongside the raw GReader fields — read those directly.
- `newer_than` is **unix seconds** (mapped to GReader `ot`), not milliseconds.
- Fetching a stream auto-ingests the items into the KG by default
  (`FRESHRSS_KG_AUTO_INGEST`); set it to `0` to disable that side-effect.

## Related
- Curate feeds and tags → `freshrss-subscription-management`.
- Build searchable knowledge from feeds → `freshrss-knowledge-ingestion`.
