import importlib

import pytest


@pytest.mark.concept("FR-OS.identity.frss")
def test_package_imports():
    """CONCEPT:FR-OS.identity.frss The package imports cleanly and exposes its public surface."""
    module = importlib.import_module("freshrss_agent")
    assert hasattr(module, "__all__")
