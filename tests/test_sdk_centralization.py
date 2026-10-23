"""CONN-FRESHRSS-AGENT-SDK-CENTRALIZATION-R001."""

from pathlib import Path

import httpx

from freshrss_agent.api import FreshRSSApi


def test_api_client_uses_sdk_http_client():
    client = FreshRSSApi(
        base_url="https://freshrss.example", username="u", api_password="p"
    )
    assert isinstance(client.session, httpx.Client)
    root = Path(__file__).resolve().parents[1] / "freshrss_agent"
    for source in root.rglob("*.py"):
        assert "import requests" not in source.read_text(), source
