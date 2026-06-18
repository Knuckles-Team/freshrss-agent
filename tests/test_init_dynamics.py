import importlib

import pytest


@pytest.mark.concept("FRSS-001")
def test_package_imports():
    """CONCEPT:FRSS-001 The package imports cleanly and exposes its public surface."""
    module = importlib.import_module("freshrss_agent")
    assert hasattr(module, "__all__")
