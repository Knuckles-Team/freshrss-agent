"""Native epistemic-graph ingestion for FreshRSS records.

CONCEPT:AU-KG.ingest.enterprise-source-extractor. The freshrss-agent connector
natively pushes its data into the ONE epistemic-graph knowledge graph in the two
modalities that apply to a feed reader:

* **documents** — feed items (stream-contents entries) → ``:Document`` nodes carrying
  the article body + ``source_uri`` (``ingest_feed_items``); hub-side enrichment
  chunks/embeds them for semantic search.
* **typed nodes** — feed subscriptions → ``:FeedSubscription`` (a ``:FeedSource``
  specialization) + their ``:FeedCategory`` folders and ``:inCategory`` links
  (``ingest_subscriptions``).

This is a **thin mapper** over the shared ``agent_connector_sdk.ingest`` knowledge-ingest
facade — the one connector write path; there is no self-contained fallback transaction
here. The MCP tool surface must never raise when the KG stack is down, so every entry
point stays **best-effort**: it returns ``None`` (never raises) for empty input or when
the facade reports :class:`IngestUnavailableError`/:class:`IngestError` (no reachable
engine, or a malformed record). Node ids follow ``freshrss:<class>:<externalId>`` and
each ``node_type`` matches a class the package's ``ontology_providers`` ``feed.ttl``
federates.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any

from agent_connector_sdk.ingest import (
    ChangeSet,
    Document,
    Entity,
    IngestBinding,
    IngestError,
    IngestUnavailableError,
    KnowledgeIngest,
    Relationship,
    current_ingest,
)

logger = logging.getLogger("freshrss_agent.kg")

_SOURCE = "freshrss-agent"
_DOMAIN = "freshrss"

_BINDING = IngestBinding(connector="freshrss-agent", stream=_DOMAIN)


def _to_entity(record: dict[str, Any]) -> Entity:
    return Entity(
        id=record.get("id"),
        node_type=record.get("node_type"),
        properties={k: v for k, v in record.items() if k not in ("id", "node_type")},
    )


def _to_relationship(record: dict[str, Any]) -> Relationship:
    props = {
        k: v
        for k, v in record.items()
        if k not in ("source", "target", "relationship")
    }
    return Relationship(
        source=record["source"],
        target=record["target"],
        relationship=record["relationship"],
        properties=props or None,
    )


def _to_document(record: dict[str, Any]) -> Document:
    return Document(
        id=record["id"],
        text=record["text"],
        title=record.get("title"),
        source_uri=record.get("source_uri"),
        properties={
            k: v
            for k, v in record.items()
            if k not in ("id", "text", "title", "source_uri")
        },
    )


async def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int] | None:
    """Write typed OWL nodes (+ edges) into epistemic-graph. Best-effort, never raises.

    ``entities``: ``[{"id":..., "node_type":<owl:Class>, ...props}]``.
    ``relationships``: ``[{"source":id, "target":id, "relationship":<link>}]``.
    Returns ``{"nodes":n, "edges":m}`` or ``None`` (empty input / no reachable engine /
    malformed record). ``ingest`` may be injected (tests); otherwise the process-wide
    facade is resolved on demand.
    """
    if not entities:
        return None
    change_set = ChangeSet(
        entities=tuple(_to_entity(e) for e in entities),
        relationships=tuple(_to_relationship(r) for r in relationships or ()),
    )
    try:
        service = ingest or current_ingest()
        receipt = await service.submit(_BINDING, change_set)
    except (IngestUnavailableError, IngestError) as exc:
        logger.debug("KG ingest unavailable/failed: %s", exc)
        return None
    return {"nodes": receipt.affected_count, "edges": receipt.relationship_count}


async def ingest_documents(
    documents: list[dict[str, Any]],
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int] | None:
    """Write text records as ``:Document`` nodes (semantic-search fodder). Best-effort.

    Each doc: ``{"id":..., "text":..., "title"?:..., "source_uri"?:..., ...props}``.
    Returns ``{"nodes":n, "edges":0}`` or ``None``.
    """
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    docs: list[dict[str, Any]] = []
    for doc in documents or []:
        did = doc.get("id")
        text = doc.get("text") or doc.get("content")
        if not did or not text:
            continue
        node = {k: v for k, v in doc.items() if k != "content" and v is not None}
        node["id"] = did
        node["text"] = text
        node.setdefault("created_at", now)
        docs.append(node)
    if not docs:
        return None
    change_set = ChangeSet(documents=tuple(_to_document(d) for d in docs))
    try:
        service = ingest or current_ingest()
        receipt = await service.submit(_BINDING, change_set)
    except (IngestUnavailableError, IngestError) as exc:
        logger.debug("KG ingest unavailable/failed: %s", exc)
        return None
    return {"nodes": receipt.affected_count, "edges": receipt.relationship_count}


# --- domain mappers (records -> entity/document dicts) ---------------------------


def _ext_id(raw: str) -> str:
    """Derive a compact external id from a GReader long-form *item* id.

    Item ids look like ``tag:google.com,2005:reader/item/00000000abcd``; the stable
    unique part is the trailing hex segment.
    """
    if not raw:
        return ""
    tail = raw.rsplit("/", 1)[-1]
    return re.sub(r"[^0-9A-Za-z._:-]", "_", tail)


def _slug(raw: str) -> str:
    """Sanitize a whole stream/label id into a collision-safe node-id segment.

    Feed/category ids (``feed/https://host/path``, ``user/-/label/News``) are only
    unique in full — unlike item ids, their trailing segment collides — so the entire
    string is slugified.
    """
    if not raw:
        return ""
    return re.sub(r"[^0-9A-Za-z._:-]", "_", raw)


async def ingest_feed_items(
    items: list[dict[str, Any]],
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int] | None:
    """Map FreshRSS stream-contents items → ``:Document`` nodes and ingest.

    Each item's flattened ``text``/``url`` (produced by ``ReaderMixin.stream_contents``)
    plus its title, timestamps and originating feed become a searchable Document.
    """
    docs: list[dict[str, Any]] = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        raw_id = item.get("id") or ""
        ext = _ext_id(raw_id)
        if not ext:
            continue
        body = item.get("text") or (item.get("summary") or {}).get("content") or ""
        if not body:
            continue
        origin = item.get("origin") or {}
        canonical = item.get("canonical") or []
        url = item.get("url") or (canonical[0].get("href", "") if canonical else "")
        docs.append(
            {
                "id": f"freshrss:item:{ext}",
                "text": body,
                "title": item.get("title"),
                "source_uri": url or None,
                "itemUrl": url or None,
                "published": item.get("published"),
                "updated": item.get("updated"),
                "feed_title": origin.get("title"),
                "feed_stream_id": origin.get("streamId"),
                "externalToolId": ext,
            }
        )
    return await ingest_documents(docs, ingest=ingest)


async def ingest_subscriptions(
    subscriptions: list[dict[str, Any]] | dict[str, Any],
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int] | None:
    """Map FreshRSS subscription records → ``:FeedSubscription`` (+ ``:FeedCategory``).

    Accepts either the raw ``{"subscriptions": [...]}`` payload or a bare list of
    subscription dicts. Emits a typed FeedSubscription per feed, a FeedCategory per
    label, and an ``:inCategory`` edge linking them.
    """
    if isinstance(subscriptions, dict):
        subscriptions = subscriptions.get("subscriptions") or []
    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    seen_cats: set[str] = set()
    for sub in subscriptions or []:
        if not isinstance(sub, dict):
            continue
        stream_id = sub.get("id") or sub.get("url")
        if not stream_id:
            continue
        ext = _slug(stream_id)
        sub_node_id = f"freshrss:subscription:{ext}"
        entities.append(
            {
                "id": sub_node_id,
                "node_type": "FeedSubscription",
                "name": sub.get("title"),
                "title": sub.get("title"),
                "url": sub.get("url"),
                "htmlUrl": sub.get("htmlUrl"),
                "stream_id": stream_id,
                "externalToolId": ext,
            }
        )
        for cat in sub.get("categories") or []:
            if not isinstance(cat, dict):
                continue
            cat_id = cat.get("id") or cat.get("label")
            if not cat_id:
                continue
            cat_ext = _slug(cat_id)
            cat_node_id = f"freshrss:category:{cat_ext}"
            if cat_node_id not in seen_cats:
                seen_cats.add(cat_node_id)
                entities.append(
                    {
                        "id": cat_node_id,
                        "node_type": "FeedCategory",
                        "name": cat.get("label") or cat_id.rsplit("/", 1)[-1],
                        "label_id": cat_id,
                        "externalToolId": cat_ext,
                    }
                )
            relationships.append(
                {
                    "source": sub_node_id,
                    "target": cat_node_id,
                    "relationship": "inCategory",
                }
            )
    return await ingest_entities(entities, relationships, ingest=ingest)


def maybe_ingest_items(items: Any) -> dict[str, int] | None:
    """Best-effort, default-on hook for the fetch flow (never raises).

    Called from ``ReaderMixin.stream_contents``, a plain synchronous method that
    itself runs off the engine's event loop (invoked through
    ``agent_connector_sdk.mcp.concurrency.run_blocking``'s worker thread), so this
    bridges into the async ``ingest_feed_items`` with its own short-lived event loop
    rather than requiring every caller up the stack to turn async. Controlled by the
    ``FRESHRSS_KG_AUTO_INGEST`` env flag (default on); no-ops on any failure or when
    no engine is reachable.
    """
    import asyncio
    import os

    if os.environ.get("FRESHRSS_KG_AUTO_INGEST", "1").lower() in ("0", "false", "no"):
        return None
    if not isinstance(items, list) or not items:
        return None
    try:
        return asyncio.run(ingest_feed_items(items))
    except Exception as e:  # noqa: BLE001 — fetch flow must never break on KG
        logger.debug("KG auto-ingest skipped: %s", e)
        return None
