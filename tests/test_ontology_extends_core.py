"""The pack extends only the core ontology (CONN-FRESHRSS-AGENT-CONNECTOR-CONTENT-R002)."""

import re
from pathlib import Path

import pytest

ONTOLOGY_DIR = Path(__file__).resolve().parents[1] / "freshrss_agent" / "ontology"
CORE_TERMS = {
    "FeedItem",
    "FeedSource",
    "FeedSubscription",
}


@pytest.mark.spec("CONN-FRESHRSS-AGENT-CONNECTOR-CONTENT-R002")
def test_pack_declares_no_core_term():
    declared = set()
    for ttl in ONTOLOGY_DIR.glob("*.ttl"):
        declared |= set(
            re.findall(r"^:([A-Za-z0-9_]+)\s+(?:a|rdf:type)\s", ttl.read_text(), re.M)
        )
    assert declared.isdisjoint(CORE_TERMS), sorted(declared & CORE_TERMS)
