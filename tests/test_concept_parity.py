from pathlib import Path

import pytest

CONCEPTS_DOC = Path(__file__).resolve().parents[1] / "docs" / "concepts.md"


@pytest.mark.concept("FR-OS.identity.frss")
def test_concepts_doc_exists():
    """CONCEPT:FR-OS.identity.frss The concept registry document is present."""
    assert CONCEPTS_DOC.is_file()


@pytest.mark.concept("FR-OS.identity.frss")
def test_eco_bridge_present():
    """CONCEPT:FR-OS.identity.frss The ECO-4.0 ecosystem bridge concept is referenced."""
    assert "AU-ECO.messaging.native-backend-abstraction" in CONCEPTS_DOC.read_text(encoding="utf-8")


@pytest.mark.concept("FR-OS.identity.frss")
def test_prefix_registered():
    """CONCEPT:FR-OS.identity.frss The project-specific FRSS concept prefix is registered."""
    assert "CONCEPT:FRSS-" in CONCEPTS_DOC.read_text(encoding="utf-8")
