"""Native epistemic-graph ingestion — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_documents`` seam plus the FreshRSS
domain mappers with a fake ChangeEnvelope-capable engine client (no engine
required), asserting the committed nodes/edges and the item -> :Document /
subscription -> :FeedSubscription mappings. CONCEPT:AU-KG.ingest.enterprise-source-extractor.

The fake client mirrors agent-utilities' own sanctioned test double
(``agent-utilities/tests/knowledge_graph/test_native_ingest.py``) — the ``txn``-only
fake is retired; ``native_ingest`` now hard-requires an injected client exposing
``.changes``/``.nodes``/``.rdf``/``.supports()``. ``freshrss_agent.kg_ingest`` is a
**best-effort** surface (its MCP tools must never raise when the KG stack is down),
so it converts ``NativeIngestError`` into ``None`` rather than propagating it — those
semantics are exercised explicitly below.
"""

from __future__ import annotations

from typing import Any

import msgpack
import pytest
from agent_utilities.knowledge_graph.core.session import GraphSession, use_session
from agent_utilities.security.actor_identity import ActorType
from agent_utilities.security.brain_context import ActorContext, use_actor

from freshrss_agent.kg_ingest import (
    ingest_documents,
    ingest_entities,
    ingest_feed_items,
    ingest_subscriptions,
    maybe_ingest_items,
)


@pytest.fixture(autouse=True)
def _governed_session():
    actor = ActorContext(
        actor_id="subject:opaque:synthetic",
        actor_type=ActorType.AUTOMATED_SERVICE,
        roles=(),
        tenant_id="tenant:opaque:synthetic",
        authenticated=True,
    )
    session = GraphSession(
        actor=actor,
        tenant=actor.tenant_id,
        scopes=frozenset({"kg:write"}),
        graph="graph:opaque:synthetic",
        policy_version="policy:opaque:synthetic",
        audience="epistemic-graph",
    )
    with use_actor(actor), use_session(session):
        yield


class _FakeNodes:
    def __init__(self) -> None:
        self.values: dict[str, dict[str, Any]] = {}

    def properties(self, node_id: str) -> dict[str, Any] | None:
        return self.values.get(node_id)

    def list(self) -> list[tuple[str, dict[str, Any]]]:
        return list(self.values.items())


class _FakeChanges:
    def __init__(self, nodes: _FakeNodes) -> None:
        self.nodes = nodes
        self.edges: list[tuple[str, str, dict[str, Any]]] = []
        self.applied: list[dict[str, Any]] = []
        self.records: dict[str, dict[str, Any]] = {}
        self.versions: dict[str, dict[str, Any]] = {}

    def get(self, envelope_id: str) -> dict[str, Any] | None:
        return self.records.get(envelope_id)

    def content_version(self, object_id: str) -> dict[str, Any] | None:
        return self.versions.get(object_id)

    def cursor(self, _source: str, _partition: str = "") -> None:
        return None

    def apply(self, envelope: dict[str, Any]) -> dict[str, Any]:
        self.applied.append(envelope)
        mutation = envelope["mutation"]
        for operation in mutation["operations"]:
            method = operation["method"]
            params = method["params"]
            properties = msgpack.unpackb(params["properties_msgpack"], raw=False)
            if method["method"] == "AddNode":
                self.nodes.values[params["node_id"]] = properties
            elif method["method"] == "AddEdge":
                self.edges.append(
                    (params["source_id"], params["target_id"], properties)
                )
        version = envelope["content_version"]
        self.versions[version["object_id"]] = version
        self.records[envelope["envelope_id"]] = envelope
        return {
            "batch_id": mutation["batch_id"],
            "replayed": False,
            "projection_pending": False,
        }


class _FakeRdf:
    def validate_shacl(self, _shapes: str, _data_graph: str) -> dict[str, Any]:
        return {"conforms": True, "results": []}


class _FakeClient:
    def __init__(self) -> None:
        self.nodes = _FakeNodes()
        self.changes = _FakeChanges(self.nodes)
        self.rdf = _FakeRdf()

    @staticmethod
    def supports(operation: str) -> bool:
        return operation == "ApplyChangeEnvelope"


def test_ingest_entities_writes_nodes_and_edges():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "node_type": "FeedSubscription", "name": "p"},
            {"id": "b", "node_type": "FeedCategory"},
        ],
        [{"source": "a", "target": "b", "relationship": "inCategory"}],
        client=c,
    )
    assert res == {"nodes": 2, "edges": 1}
    assert len(c.changes.applied) == 1
    assert set(c.nodes.values) == {"a", "b"}
    # provenance is stamped
    assert c.nodes.values["a"]["source"] == "freshrss-agent"
    assert c.nodes.values["a"]["domain"] == "freshrss"
    assert c.changes.edges == [("a", "b", {"relationship": "inCategory"})]


def test_ingest_documents_forces_type_and_text():
    c = _FakeClient()
    res = ingest_documents(
        [{"id": "d1", "text": "hello world", "title": "T"}],
        client=c,
    )
    assert res == {"nodes": 1, "edges": 0}
    node = c.nodes.values["d1"]
    assert node["node_type"] == "Document"
    assert node["text"] == "hello world"
    assert node["title"] == "T"
    assert "created_at" in node


def test_ingest_documents_skips_bodyless():
    c = _FakeClient()
    assert ingest_documents([{"id": "d1", "text": ""}], client=c) is None


def test_ingest_feed_items_maps_to_documents():
    c = _FakeClient()
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
    res = ingest_feed_items(items, client=c)
    assert res == {"nodes": 1, "edges": 0}
    node = c.nodes.values["freshrss:item:00000000abcd"]
    assert node["node_type"] == "Document"
    assert node["text"] == "the body"
    assert node["title"] == "Big News"
    # `source_uri` is one of agent-utilities' PersistencePrivacyGuard
    # `_LOCATION_FIELDS` (persistence_privacy.py) and is blanket-redacted at
    # persistence time regardless of content — the real URL survives on the
    # non-reserved `itemUrl` field the mapper also stamps.
    assert node["source_uri"] == "[REDACTED_LOCATION]"
    assert node["itemUrl"] == "https://example.com/a"
    assert node["feed_title"] == "Example Feed"
    assert node["externalToolId"] == "00000000abcd"


def test_ingest_feed_items_skips_bodyless_and_idless():
    c = _FakeClient()
    items = [
        {"id": "tag:.../item/x", "text": ""},  # no body
        {"title": "no id", "text": "body"},  # no id
    ]
    assert ingest_feed_items(items, client=c) is None


def test_ingest_subscriptions_maps_feed_and_category():
    c = _FakeClient()
    subs = [
        {
            "id": "feed/https://example.com/rss",
            "title": "Example",
            "url": "https://example.com/rss",
            "htmlUrl": "https://example.com",
            "categories": [{"id": "user/-/label/News", "label": "News"}],
        }
    ]
    res = ingest_subscriptions(subs, client=c)
    assert res == {"nodes": 2, "edges": 1}
    # Subscription/category ids slugify the FULL stream id (tails collide).
    sub_nodes = [n for n in c.nodes.values if n.startswith("freshrss:subscription:")]
    cat_nodes = [n for n in c.nodes.values if n.startswith("freshrss:category:")]
    assert len(sub_nodes) == 1
    assert len(cat_nodes) == 1
    assert c.nodes.values[sub_nodes[0]]["node_type"] == "FeedSubscription"
    assert c.nodes.values[cat_nodes[0]]["node_type"] == "FeedCategory"
    assert c.nodes.values[cat_nodes[0]]["name"] == "News"
    src, dst, props = c.changes.edges[0]
    assert src == sub_nodes[0]
    assert dst == cat_nodes[0]
    assert props == {"relationship": "inCategory"}
    assert "example.com" in sub_nodes[0]  # full stream id is preserved in the slug


def test_ingest_subscriptions_accepts_wrapped_payload():
    c = _FakeClient()
    payload = {"subscriptions": [{"id": "feed/https://x/rss", "title": "X"}]}
    res = ingest_subscriptions(payload, client=c)
    assert res == {"nodes": 1, "edges": 0}


def test_ingest_noops_without_engine():
    # No injected client + no reachable engine -> clean no-op.
    assert ingest_entities([{"id": "a", "node_type": "FeedSubscription"}]) is None
    assert ingest_documents([{"id": "d", "text": "x"}]) is None


def test_ingest_rejects_retired_structural_alias_as_noop():
    # freshrss_agent's tool surface is best-effort (never raises): a malformed
    # record (the retired ``type`` alias instead of canonical ``node_type``) is
    # reported back as a clean no-op rather than propagating NativeIngestError.
    c = _FakeClient()
    assert ingest_entities([{"id": "a", "type": "FeedSubscription"}], client=c) is None
    assert c.changes.applied == []


def test_ingest_empty_is_noop():
    assert ingest_entities([], client=_FakeClient()) is None
    assert ingest_feed_items([], client=_FakeClient()) is None
    assert ingest_subscriptions([], client=_FakeClient()) is None


def test_maybe_ingest_respects_disable_flag(monkeypatch):
    monkeypatch.setenv("FRESHRSS_KG_AUTO_INGEST", "0")
    # Even with items present, the disable flag short-circuits to None.
    assert maybe_ingest_items([{"id": "x", "text": "y"}]) is None


def test_maybe_ingest_noops_on_empty(monkeypatch):
    monkeypatch.setenv("FRESHRSS_KG_AUTO_INGEST", "1")
    assert maybe_ingest_items([]) is None
    assert maybe_ingest_items(None) is None
