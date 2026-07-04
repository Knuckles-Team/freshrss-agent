---
name: freshrss-subscription-management
description: >-
  Curate FreshRSS feeds, categories, and item tags over the Google Reader
  (GReader) API via the freshrss-agent MCP server — list subscriptions and
  categories, subscribe/unsubscribe to feeds, label a feed into a category, and
  tag items (mark-read / star). Use when the agent must manage which feeds are
  followed, organize them into folders, or change item read/starred state. Do
  NOT use to read stream contents or item bodies (use freshrss-feed-reader) or
  to push feeds into the knowledge graph (use freshrss-knowledge-ingestion).
license: MIT
tags: [freshrss, rss, greader, subscriptions, curation, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# FreshRSS Subscription Management

Write-side curation of FreshRSS through the Google Reader compatible API. These
tools transparently fetch the short-lived GReader POST token required by write
actions, so callers never manage it.

## When to use
- List current subscriptions or categories/folders.
- Subscribe to a new feed (optionally with a title and category).
- Unsubscribe from a feed.
- Label an existing feed into a category.
- Mark items read, or star / unstar an item.

## When NOT to use
- Read stream contents, item bodies, or unread counts → `freshrss-feed-reader`.
- Ingest feeds/items into the knowledge graph → `freshrss-knowledge-ingestion`.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`freshrss-agent`** MCP server.

| Variable | Required | Notes |
|----------|----------|-------|
| `FRESHRSS_URL` | ✅ | Base URL of the FreshRSS instance |
| `FRESHRSS_USER` | ✅ | GReader account username |
| `FRESHRSS_API_PASSWORD` | ✅ | GReader API password |
| `FRESHRSS_SSL_VERIFY` | optional | TLS verification toggle |

`MCP_TOOL_MODE` (`condensed`|`verbose`|`both`) selects the condensed surface vs.
the one-to-one verbose tools.

## Tools & actions
Prefer the **condensed** tool; it takes `action` + a `params_json` **JSON string**.

| Condensed tool | Actions |
|----------------|---------|
| `freshrss_subscriptions` | `list`, `categories`, `subscribe`, `unsubscribe`, `label`, `mark_read`, `star` |

### Key parameters
- `feed_url` — a feed URL, or a `feed/<url>` stream id (subscribe/unsubscribe/label).
- `title` — optional feed title on `subscribe`.
- `category` — category label to assign (`subscribe` / `label`).
- `item_ids` — one id or a list of ids (`mark_read`).
- `item_id` + `starred` — id and boolean for `star` (True to star, False to unstar).

## Recipes (`params_json`)
List all subscriptions:
```json
{}
```
Subscribe to a feed under a category:
```json
{"feed_url":"https://example.com/rss.xml","title":"Example","category":"News"}
```
Label an existing feed into a category:
```json
{"feed_url":"feed/https://example.com/rss.xml","category":"Research"}
```
Mark items read:
```json
{"item_ids":["tag:google.com,2005:reader/item/00000000abcd"]}
```
Star an item:
```json
{"item_id":"tag:google.com,2005:reader/item/00000000abcd","starred":true}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- Categories are GReader labels (`user/-/label/<cat>`); pass the bare `category`
  name — the tool wraps it.
- `subscribe`/`unsubscribe`/`label` accept either a raw feed URL or a `feed/<url>`
  stream id; the client normalizes to the `feed/` form.
- Write actions need the POST token — it is fetched automatically, but a stale auth
  session triggers one silent re-login/retry.

## Related
- Read what those feeds contain → `freshrss-feed-reader`.
- Map subscriptions/items into the KG → `freshrss-knowledge-ingestion`.
