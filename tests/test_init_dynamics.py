import importlib


def test_package_imports():
    module = importlib.import_module("freshrss_agent")
    assert hasattr(module, "__all__")
