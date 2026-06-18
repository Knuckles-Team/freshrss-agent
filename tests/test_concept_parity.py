from pathlib import Path

import pytest

CONCEPTS_DOC = Path(__file__).resolve().parents[1] / "docs" / "concepts.md"


@pytest.mark.concept("FRSS-001")
def test_concepts_doc_exists():
    """CONCEPT:FRSS-001 The concept registry document is present."""
    assert CONCEPTS_DOC.is_file()


@pytest.mark.concept("FRSS-001")
def test_eco_bridge_present():
    """CONCEPT:FRSS-001 The ECO-4.0 ecosystem bridge concept is referenced."""
    assert "ECO-4.0" in CONCEPTS_DOC.read_text(encoding="utf-8")


@pytest.mark.concept("FRSS-001")
def test_prefix_registered():
    """CONCEPT:FRSS-001 The project-specific FRSS concept prefix is registered."""
    assert "CONCEPT:FRSS-" in CONCEPTS_DOC.read_text(encoding="utf-8")
