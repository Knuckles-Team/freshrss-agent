---
name: freshrss-subscription-management
skill_type: skill
description: >-
  Curate FreshRSS feeds, categories, and item tags over the Google Reader (GReader) API via the freshrss-agent MCP server — list subscriptions and categories, subscribe/unsubscribe to feeds, label a feed into a category, and tag items (mark-read / star). Use when the agent must manage which feeds are followed, organize them into folders, or change item read/starred state.
license: MIT
tags: [freshrss, rss, greader, subscriptions, curation, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---
# FreshRSS Subscription Management

Scope: Curate FreshRSS feeds, categories, and item tags over the Google Reader (GReader) API via the freshrss-agent MCP server — list subscriptions and categories, subscribe/unsubscribe to feeds, label a feed into a category, and tag items (mark-read / star). Use when the agent must manage which feeds are followed, organize them into folders, or change item read/starred state. Do NOT use to read stream contents or item bodies (use freshrss-feed-reader) or to push feeds into the knowledge graph (use freshrss-knowledge-ingestion).

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
| `FRESHRSS_TLS_PROFILE` / `FRESHRSS_TLS_PROFILE_REF` | optional | Named outbound TLS policy (verification is mandatory) |

`MCP_TOOL_MODE` (`condensed`|`verbose`|`both`) selects the condensed surface vs.
the one-to-one verbose tools.

## Steps

1. Inspect current state with `freshrss_subscription_list` and `freshrss_categories`, and verify the feed or category you will change appears or is absent as expected.
2. Subscribe with `freshrss_subscribe`(`feed_url`, optionally `title`, `category`), and verify the result is a subscription or `already_subscribed`.
3. Move a feed with `freshrss_label`(`feed_url`, `category`) using the bare category name, and verify with `freshrss_subscription_list` that the category changed.
4. Remove a feed only when asked: call `freshrss_unsubscribe`(`feed_url`), and verify the feed no longer appears in `freshrss_subscription_list`.
5. Change item state with `freshrss_mark_read`(`item_ids`) or `freshrss_star`(`item_id`, `starred`), and verify the call reports success.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Subscribe fails with HTTP 400 | FreshRSS refuses feed URLs resolving to private addresses | Use a publicly resolvable `feed_url` |
| Result `not_subscribed` | Unknown feed on unsubscribe | List with `freshrss_subscription_list` and pass the exact URL or `feed/<n>` id |
| Authentication error | `FRESHRSS_URL`, `FRESHRSS_USER` or `FRESHRSS_API_PASSWORD` missing or wrong | Set all three variables and call `freshrss_subscription_list` to confirm access |

## Tools
One typed tool per operation. Parameters are passed as normal tool arguments.

| Tool | Use |
|------|-----|
| `freshrss_subscription_list` | list feeds with their ids and categories |
| `freshrss_categories` | list categories and tags |
| `freshrss_subscribe` | subscribe to `feed_url` with optional `title` and `category`; a repeat returns `already_subscribed` |
| `freshrss_unsubscribe` | remove a feed by URL or `feed/<n>` id; an unknown feed returns `not_subscribed` |
| `freshrss_label` | add a category to a feed |

FreshRSS fetches the feed before it answers, so a subscribe can take a minute. The client confirms the
result against the subscription list. FreshRSS refuses feed URLs that resolve to private addresses (HTTP 400).

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
