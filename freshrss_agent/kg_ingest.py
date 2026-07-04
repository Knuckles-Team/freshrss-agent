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

This is a **thin mapper** over the shared primitive
``agent_utilities.knowledge_graph.memory.native_ingest`` (the one txn write path).
The import is GUARDED: when the shared primitive is not present in the installed
``agent_utilities`` a self-contained txn fallback is used, and when no engine is
reachable every entry point **no-ops** (returns ``None``), so the connector runs with
zero KG infrastructure. Node ids follow ``freshrss:<class>:<externalId>`` and each
``type`` matches a class the package's ``ontology_providers`` ``feed.ttl`` federates.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any

logger = logging.getLogger("freshrss_agent.kg")

_SOURCE = "freshrss-agent"
_DOMAIN = "freshrss"

# --- shared-primitive import (guarded) with a self-contained txn fallback --------
try:  # pragma: no cover - exercised only when the primitive is installed
    from agent_utilities.knowledge_graph.memory.native_ingest import (
        ingest_documents as _shared_ingest_documents,
    )
    from agent_utilities.knowledge_graph.memory.native_ingest import (
        ingest_entities as _shared_ingest_entities,
    )

    _HAVE_SHARED = True
except Exception:  # noqa: BLE001 — primitive absent in installed agent_utilities
    _shared_ingest_entities = None
    _shared_ingest_documents = None
    _HAVE_SHARED = False


def _client() -> tuple[Any | None, str]:
    """Return ``(engine_client, graph_name)`` or ``(None, "")`` when unavailable."""
    try:
        from agent_utilities.knowledge_graph.core.graph_compute import (
            GraphComputeEngine,
        )
    except Exception as e:  # noqa: BLE001 — KG stack absent
        logger.debug("KG ingest unavailable (import): %s", e)
        return None, ""
    try:
        engine = GraphComputeEngine()
        client = getattr(engine, "_client", None)
        if client is None:
            return None, ""
        return client, (getattr(engine, "graph_name", None) or "__commons__")
    except Exception as e:  # noqa: BLE001 — engine unreachable
        logger.debug("KG ingest: engine unreachable: %s", e)
        return None, ""


def _write_nodes(
    client: Any,
    graph: str,
    nodes: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None,
) -> dict[str, int] | None:
    """Fallback: stamp provenance, MERGE nodes in one txn, then add edges."""
    nodes = [n for n in nodes if n.get("id")]
    if not nodes:
        return None
    try:
        txn = client.txn.begin(graph=graph)
        for node in nodes:
            props = {k: v for k, v in node.items() if k != "id" and v is not None}
            props.setdefault("source", _SOURCE)
            props.setdefault("domain", _DOMAIN)
            client.txn.add_node(txn, node["id"], props)
        committed = client.txn.commit(txn)
    except Exception as e:  # noqa: BLE001 — engine/txn failure is non-fatal
        logger.warning("KG ingest: txn failed: %s", e)
        return None
    if not committed:
        logger.warning("KG ingest: txn not committed (conflict)")
        return None

    edges = 0
    for rel in relationships or []:
        try:
            client.edges.add(
                rel["source"], rel["target"], {"type": rel.get("type", "RELATED")}
            )
            edges += 1
        except Exception as e:  # noqa: BLE001 — pure edge link, best-effort
            logger.debug("KG ingest: edge skipped: %s", e)

    logger.info("KG ingest: wrote %d nodes, %d edges", len(nodes), edges)
    return {"nodes": len(nodes), "edges": edges}


def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Write typed OWL nodes (+ edges) into epistemic-graph.

    ``entities``: ``[{"id":..., "type":<owl:Class>, ...props}]``.
    ``relationships``: ``[{"source":id, "target":id, "type":<link>}]``.
    Returns ``{"nodes":n, "edges":m}`` or ``None``. Delegates to the shared
    primitive when present; otherwise uses the self-contained txn fallback.
    ``client``/``graph`` may be injected (tests); otherwise resolved on demand.
    """
    entities = [e for e in (entities or []) if e.get("id")]
    if not entities:
        return None
    if _HAVE_SHARED and client is None:
        return _shared_ingest_entities(
            entities, relationships, source=_SOURCE, domain=_DOMAIN
        )
    if client is None:
        client, graph = _client()
    if client is None:
        return None
    return _write_nodes(client, graph or "__commons__", entities, relationships)


def ingest_documents(
    documents: list[dict[str, Any]],
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Write text records as ``:Document`` nodes (semantic-search fodder).

    Each doc: ``{"id":..., "text":..., "title"?:..., "source_uri"?:..., ...props}``.
    Returns ``{"nodes":n, "edges":0}`` or ``None``.
    """
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    nodes: list[dict[str, Any]] = []
    for doc in documents or []:
        did = doc.get("id")
        text = doc.get("text") or doc.get("content")
        if not did or not text:
            continue
        node = {k: v for k, v in doc.items() if k != "content" and v is not None}
        node["id"] = did
        node["type"] = "Document"
        node["text"] = text
        node.setdefault("created_at", now)
        nodes.append(node)
    if not nodes:
        return None
    if _HAVE_SHARED and client is None:
        return _shared_ingest_documents(nodes, source=_SOURCE, domain=_DOMAIN)
    if client is None:
        client, graph = _client()
    if client is None:
        return None
    return _write_nodes(client, graph or "__commons__", nodes, None)


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


def ingest_feed_items(
    items: list[dict[str, Any]],
    *,
    client: Any | None = None,
    graph: str | None = None,
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
                "published": item.get("published"),
                "updated": item.get("updated"),
                "feed_title": origin.get("title"),
                "feed_stream_id": origin.get("streamId"),
                "externalToolId": ext,
            }
        )
    return ingest_documents(docs, client=client, graph=graph)


def ingest_subscriptions(
    subscriptions: list[dict[str, Any]],
    *,
    client: Any | None = None,
    graph: str | None = None,
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
                "type": "FeedSubscription",
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
                        "type": "FeedCategory",
                        "name": cat.get("label") or cat_id.rsplit("/", 1)[-1],
                        "label_id": cat_id,
                        "externalToolId": cat_ext,
                    }
                )
            relationships.append(
                {
                    "source": sub_node_id,
                    "target": cat_node_id,
                    "type": "inCategory",
                }
            )
    return ingest_entities(entities, relationships, client=client, graph=graph)


def maybe_ingest_items(items: Any) -> dict[str, int] | None:
    """Best-effort, default-on hook for the fetch flow (never raises).

    Called from ``ReaderMixin.stream_contents`` after normalization. Controlled by
    the ``FRESHRSS_KG_AUTO_INGEST`` env flag (default on); no-ops on any failure or
    when no engine is reachable.
    """
    import os

    if os.environ.get("FRESHRSS_KG_AUTO_INGEST", "1").lower() in ("0", "false", "no"):
        return None
    if not isinstance(items, list) or not items:
        return None
    try:
        return ingest_feed_items(items)
    except Exception as e:  # noqa: BLE001 — fetch flow must never break on KG
        logger.debug("KG auto-ingest skipped: %s", e)
        return None
