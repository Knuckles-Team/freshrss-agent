"""Native epistemic-graph ingestion — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_documents`` seam plus the FreshRSS
domain mappers with a fake engine client (no engine required), asserting the txn
add_node/commit + edge calls and the item -> :Document / subscription ->
:FeedSubscription mappings. CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from freshrss_agent.kg_ingest import (
    ingest_documents,
    ingest_entities,
    ingest_feed_items,
    ingest_subscriptions,
    maybe_ingest_items,
)


class _FakeTxn:
    def __init__(self):
        self.nodes = {}
        self.committed = False
        self.graph = None

    def begin(self, graph=None):
        self.graph = graph
        return "txn-1"

    def add_node(self, txn, node_id, props):
        self.nodes[node_id] = props

    def commit(self, txn):
        self.committed = True
        return True


class _FakeEdges:
    def __init__(self):
        self.edges = []

    def add(self, src, dst, props):
        self.edges.append((src, dst, props))


class _FakeClient:
    def __init__(self):
        self.txn = _FakeTxn()
        self.edges = _FakeEdges()


def test_ingest_entities_writes_nodes_and_edges():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "type": "FeedSubscription", "name": "p"},
            {"id": "b", "type": "FeedCategory"},
        ],
        [{"source": "a", "target": "b", "type": "inCategory"}],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 2, "edges": 1}
    assert c.txn.committed is True
    assert set(c.txn.nodes) == {"a", "b"}
    # provenance is stamped
    assert c.txn.nodes["a"]["source"] == "freshrss-agent"
    assert c.txn.nodes["a"]["domain"] == "freshrss"
    assert c.edges.edges == [("a", "b", {"type": "inCategory"})]


def test_ingest_documents_forces_type_and_text():
    c = _FakeClient()
    res = ingest_documents(
        [{"id": "d1", "text": "hello world", "title": "T"}],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 1, "edges": 0}
    node = c.txn.nodes["d1"]
    assert node["type"] == "Document"
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
    res = ingest_feed_items(items, client=c, graph="__commons__")
    assert res == {"nodes": 1, "edges": 0}
    node = c.txn.nodes["freshrss:item:00000000abcd"]
    assert node["type"] == "Document"
    assert node["text"] == "the body"
    assert node["title"] == "Big News"
    assert node["source_uri"] == "https://example.com/a"
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
    res = ingest_subscriptions(subs, client=c, graph="__commons__")
    assert res == {"nodes": 2, "edges": 1}
    # Subscription/category ids slugify the FULL stream id (tails collide).
    sub_nodes = [n for n in c.txn.nodes if n.startswith("freshrss:subscription:")]
    cat_nodes = [n for n in c.txn.nodes if n.startswith("freshrss:category:")]
    assert len(sub_nodes) == 1
    assert len(cat_nodes) == 1
    assert c.txn.nodes[sub_nodes[0]]["type"] == "FeedSubscription"
    assert c.txn.nodes[cat_nodes[0]]["type"] == "FeedCategory"
    assert c.txn.nodes[cat_nodes[0]]["name"] == "News"
    src, dst, props = c.edges.edges[0]
    assert src == sub_nodes[0]
    assert dst == cat_nodes[0]
    assert props == {"type": "inCategory"}
    assert "example.com" in sub_nodes[0]  # full stream id is preserved in the slug


def test_ingest_subscriptions_accepts_wrapped_payload():
    c = _FakeClient()
    payload = {"subscriptions": [{"id": "feed/https://x/rss", "title": "X"}]}
    res = ingest_subscriptions(payload, client=c)
    assert res == {"nodes": 1, "edges": 0}


def test_ingest_noops_without_engine():
    # No injected client + no reachable engine -> clean no-op.
    assert ingest_entities([{"id": "a", "type": "FeedSubscription"}]) is None
    assert ingest_documents([{"id": "d", "text": "x"}]) is None


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
