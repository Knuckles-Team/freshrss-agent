"""Native epistemic-graph ingestion — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_documents`` seam plus the FreshRSS
domain mappers against a fake transport boundary (no engine required), letting the
SDK's own ``agent_connector_sdk.ingest`` request builder run on top of it.
``freshrss_agent.kg_ingest`` is a **best-effort** surface (its MCP tools must never
raise when the KG stack is down), so it converts an unreachable engine
(``IngestUnavailableError``) or a malformed record (``IngestError``) into ``None``
rather than propagating it — those semantics are exercised explicitly below.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from agent_connector_sdk.ingest import KnowledgeIngest

from freshrss_agent.kg_ingest import (
    ingest_documents,
    ingest_entities,
    ingest_feed_items,
    ingest_subscriptions,
    maybe_ingest_items,
)


class _FakeTransport:
    def __init__(self) -> None:
        self.requests: list[Any] = []

    async def source_status(self, connector: str, stream: str) -> Any:
        return SimpleNamespace(accepted_checkpoint=None)

    async def submit(self, request: Any) -> Any:
        self.requests.append(request)
        return SimpleNamespace(
            affected_count=len(request.records),
            relationship_count=len(request.relationships),
            raw_admissions=[],
        )

    async def store_blob(self, data: bytes) -> str:
        raise AssertionError("this test does not exercise blob storage")


@pytest.fixture
def ingest():
    transport = _FakeTransport()
    return KnowledgeIngest(transport, loop=None), transport


@pytest.mark.asyncio
async def test_ingest_entities_writes_nodes_and_edges(ingest):
    service, transport = ingest
    res = await ingest_entities(
        [
            {"id": "a", "node_type": "FeedSubscription", "name": "p"},
            {"id": "b", "node_type": "FeedCategory"},
        ],
        [{"source": "a", "target": "b", "relationship": "inCategory"}],
        ingest=service,
    )
    assert res == {"nodes": 2, "edges": 1}
    assert {r.record_id for r in transport.requests[0].records} == {"a", "b"}
    assert transport.requests[0].relationships[0].relation_reference.endswith(
        "/relations/inCategory"
    )


@pytest.mark.asyncio
async def test_ingest_documents_forces_type_and_text(ingest):
    service, transport = ingest
    res = await ingest_documents(
        [{"id": "d1", "text": "hello world", "title": "T"}],
        ingest=service,
    )
    assert res == {"nodes": 1, "edges": 0}
    record = transport.requests[0].records[0]
    assert record.record_id == "d1"
    assert record.payload["text"] == "hello world"
    assert record.payload["title"] == "T"
    assert "content_hash" in record.payload


@pytest.mark.asyncio
async def test_ingest_documents_skips_bodyless(ingest):
    service, _ = ingest
    assert await ingest_documents([{"id": "d1", "text": ""}], ingest=service) is None


@pytest.mark.asyncio
async def test_ingest_feed_items_maps_to_documents(ingest):
    service, transport = ingest
    items = [
        {
            "id": "tag:google.com,2005:reader/item/00000000abcd",
            "title": "Big News",
            "text": "the body",
            "url": "https://example.com/a",
            "published": 1719792000,
            "updated": 1719792100,
            "origin": {
                "title": "Example Feed",
                "streamId": "feed/https://example.com/rss",
            },
        }
    ]
    res = await ingest_feed_items(items, ingest=service)
    assert res == {"nodes": 1, "edges": 0}
    record = transport.requests[0].records[0]
    assert record.record_id == "freshrss:item:00000000abcd"
    assert record.payload["text"] == "the body"
    assert record.payload["title"] == "Big News"
    # `source_uri` is one of the PersistencePrivacyGuard `_LOCATION_FIELDS` and is
    # blanket-redacted at persistence time regardless of content — same behavior as
    # the old agent_utilities guard; the real URL survives on the non-reserved
    # `itemUrl` field the mapper also stamps.
    assert record.payload["source_uri"] == "[REDACTED_LOCATION]"
    assert record.payload["itemUrl"] == "https://example.com/a"
    assert record.payload["feed_title"] == "Example Feed"
    assert record.payload["externalToolId"] == "00000000abcd"


@pytest.mark.asyncio
async def test_ingest_feed_items_skips_bodyless_and_idless(ingest):
    service, _ = ingest
    items = [
        {"id": "tag:.../item/x", "text": ""},  # no body
        {"title": "no id", "text": "body"},  # no id
    ]
    assert await ingest_feed_items(items, ingest=service) is None


@pytest.mark.asyncio
async def test_ingest_subscriptions_maps_feed_and_category(ingest):
    service, transport = ingest
    subs = [
        {
            "id": "feed/https://example.com/rss",
            "title": "Example",
            "url": "https://example.com/rss",
            "htmlUrl": "https://example.com",
            "categories": [{"id": "user/-/label/News", "label": "News"}],
        }
    ]
    res = await ingest_subscriptions(subs, ingest=service)
    assert res == {"nodes": 2, "edges": 1}
    records = {r.record_id: r for r in transport.requests[0].records}
    # Subscription/category ids slugify the FULL stream id (tails collide).
    sub_ids = [i for i in records if i.startswith("freshrss:subscription:")]
    cat_ids = [i for i in records if i.startswith("freshrss:category:")]
    assert len(sub_ids) == 1
    assert len(cat_ids) == 1
    assert records[cat_ids[0]].payload["name"] == "News"
    rel = transport.requests[0].relationships[0]
    assert rel.source.record_id == sub_ids[0]
    assert rel.target.record_id == cat_ids[0]
    assert "example.com" in sub_ids[0]  # full stream id is preserved in the slug


@pytest.mark.asyncio
async def test_ingest_subscriptions_accepts_wrapped_payload(ingest):
    service, _ = ingest
    payload = {"subscriptions": [{"id": "feed/https://x/rss", "title": "X"}]}
    res = await ingest_subscriptions(payload, ingest=service)
    assert res == {"nodes": 1, "edges": 0}


@pytest.mark.asyncio
async def test_ingest_noops_without_engine():
    # No injected service + no reachable engine -> clean no-op.
    assert await ingest_entities([{"id": "a", "node_type": "FeedSubscription"}]) is None
    assert await ingest_documents([{"id": "d", "text": "x"}]) is None


@pytest.mark.asyncio
async def test_ingest_rejects_missing_node_type_as_noop(ingest):
    # freshrss_agent's tool surface is best-effort (never raises): a malformed
    # record (missing the canonical ``node_type``) still reaches the SDK's own
    # validation, which this seam reports back as a clean no-op rather than
    # propagating IngestError.
    service, transport = ingest
    assert await ingest_entities([{"id": "a", "type": "FeedSubscription"}], ingest=service) is None
    assert transport.requests == []


@pytest.mark.asyncio
async def test_ingest_empty_is_noop(ingest):
    service, _ = ingest
    assert await ingest_entities([], ingest=service) is None
    assert await ingest_feed_items([], ingest=service) is None
    assert await ingest_subscriptions([], ingest=service) is None


def test_maybe_ingest_respects_disable_flag(monkeypatch):
    monkeypatch.setenv("FRESHRSS_KG_AUTO_INGEST", "0")
    # Even with items present, the disable flag short-circuits to None.
    assert maybe_ingest_items([{"id": "x", "text": "y"}]) is None


def test_maybe_ingest_noops_on_empty(monkeypatch):
    monkeypatch.setenv("FRESHRSS_KG_AUTO_INGEST", "1")
    assert maybe_ingest_items([]) is None
    assert maybe_ingest_items(None) is None


def test_maybe_ingest_noops_without_engine(monkeypatch):
    monkeypatch.setenv("FRESHRSS_KG_AUTO_INGEST", "1")
    # No engine configured -> the asyncio.run() bridge hits IngestUnavailableError,
    # caught by ingest_feed_items/ingest_documents's own best-effort handling.
    assert maybe_ingest_items([{"id": "tag:x/item/1", "text": "body"}]) is None
