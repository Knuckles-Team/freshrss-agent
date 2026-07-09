---
name: freshrss-knowledge-ingestion
skill_type: skill
description: >-
  Natively ingest FreshRSS data into the epistemic-graph knowledge graph via the
  freshrss-agent MCP server — push feed items as searchable :Document nodes
  (title + body + source_uri) and subscriptions as typed :FeedSubscription nodes
  with their :FeedCategory folders and :inCategory links. Use when the agent must
  build durable, queryable knowledge from feeds rather than just read them. Do
  NOT use for one-off reads (use freshrss-feed-reader) or feed curation (use
  freshrss-subscription-management).
license: MIT
tags: [freshrss, rss, knowledge-graph, ingestion, documents, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# FreshRSS Knowledge Ingestion

Push FreshRSS content into the ONE epistemic-graph knowledge graph so feed items
become semantically searchable documents and feeds become typed, linkable nodes.
Ingestion is best-effort and engine-guarded: with no reachable engine it cleanly
no-ops (`ingested: null`) and the fetch still returns.

## When to use
- Build a searchable corpus of feed items (`:Document` with body + source_uri).
- Materialize the feed topology (`:FeedSubscription` → `:FeedCategory`) in the KG.
- Run a delta sweep that both reads and persists what is new.

## When NOT to use
- Just reading/triaging a stream without persisting → `freshrss-feed-reader`.
- Managing which feeds are followed / their tags → `freshrss-subscription-management`.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`freshrss-agent`** MCP server.
A reachable epistemic-graph engine is required for a non-null result.

| Variable | Required | Notes |
|----------|----------|-------|
| `FRESHRSS_URL` / `FRESHRSS_USER` / `FRESHRSS_API_PASSWORD` | ✅ | GReader access |
| `FRESHRSS_KG_AUTO_INGEST` | optional | Default on; set `0` to disable auto-ingest on every fetch |

## Tools & actions
| Tool | Purpose |
|------|---------|
| `freshrss_ingest_items` | Fetch a stream, push its items → `:Document` nodes |
| `freshrss_ingest_subscriptions` | List subscriptions, push → `:FeedSubscription` + `:FeedCategory` (+ `:inCategory`) |

Node ids follow `freshrss:<class>:<externalId>` (`freshrss:item:<id>`,
`freshrss:subscription:<id>`, `freshrss:category:<id>`).

## Recipes (`params_json`)
Ingest the newest 200 items across everything:
```json
{"stream_id":"user/-/state/com.google/reading-list","count":200,"order":"n"}
```
Delta ingest since a watermark:
```json
{"stream_id":"user/-/state/com.google/reading-list","newer_than":1719792000,"count":500}
```
Ingest the whole subscription topology (no params):
```json
{}
```

## Gotchas
- Ingestion is **best-effort**: a `null` `ingested` means no engine was reachable,
  not a failure — the listing still succeeds.
- `freshrss_ingest_items` accepts the same params as `freshrss_reader`
  `stream_contents`; page with `continuation` for a full sweep.
- Feed items land as `:Document` (type-forced) carrying `text`, `title`,
  `source_uri`, `published`, and the originating `feed_title`/`feed_stream_id`.
- Fetching via `freshrss_reader` already auto-ingests items by default; call
  `freshrss_ingest_items` explicitly when you want an ingest without the read path,
  or `freshrss_ingest_subscriptions` for the feed topology.
- `type` on every node matches a class federated by the package's `feed.ttl`
  ontology leg (`:Document`, `:FeedSubscription`, `:FeedCategory`).

## Related
- Read streams first → `freshrss-feed-reader`.
- Curate the feeds you ingest → `freshrss-subscription-management`.
