from unittest.mock import MagicMock, patch

import pytest

from freshrss_agent.api import FreshRSSApi


def _client():
    return FreshRSSApi(
        base_url="http://freshrss.local",
        username="admin",
        api_password="pw",
    )


@pytest.mark.concept("FRSS-001")
def test_client_login_parses_auth_token():
    """CONCEPT:FRSS-001 GReader ClientLogin parses the Auth token from the response."""
    client = _client()
    login_resp = MagicMock(status_code=200)
    login_resp.text = "SID=abc\nLSID=def\nAuth=THE_TOKEN\n"
    with patch.object(client.session, "post", return_value=login_resp) as post:
        token = client._login()
    assert token == "THE_TOKEN"
    assert client._auth_token == "THE_TOKEN"
    # ClientLogin posts Email/Passwd form fields.
    _, kwargs = post.call_args
    assert kwargs["data"] == {"Email": "admin", "Passwd": "pw"}


@pytest.mark.concept("FRSS-001")
def test_stream_contents_parses_items_and_continuation():
    """CONCEPT:FRSS-001 stream_contents maps GReader params and parses items."""
    client = _client()
    client._auth_token = "TKN"  # skip login
    payload = {
        "items": [
            {
                "id": "tag:google.com,2005:reader/item/0001",
                "title": "Hello",
                "published": 1700000000,
                "summary": {"content": "<p>body</p>"},
                "origin": {"streamId": "feed/http://example.com/rss", "title": "Ex"},
                "categories": ["user/-/state/com.google/reading-list"],
            }
        ],
        "continuation": "CONT123",
    }
    resp = MagicMock(status_code=200)
    resp.json.return_value = payload
    with patch.object(client.session, "request", return_value=resp) as req:
        result = client.stream_contents(count=50, newer_than=1699999999)

    assert result["continuation"] == "CONT123"
    assert result["items"][0]["title"] == "Hello"
    assert result["items"][0]["summary"]["content"] == "<p>body</p>"

    # Verify GReader param mapping: count -> n, newer_than -> ot, output=json injected.
    _, kwargs = req.call_args
    assert kwargs["params"]["n"] == 50
    assert kwargs["params"]["ot"] == 1699999999
    assert kwargs["params"]["output"] == "json"
    assert kwargs["headers"]["Authorization"] == "GoogleLogin auth=TKN"


@pytest.mark.concept("FRSS-001")
def test_request_reauths_once_on_401():
    """CONCEPT:FRSS-001 request re-runs ClientLogin once and retries on HTTP 401."""
    client = _client()
    client._auth_token = "STALE"
    unauthorized = MagicMock(status_code=401)
    ok = MagicMock(status_code=200)
    ok.json.return_value = {"items": [], "continuation": None}
    login_resp = MagicMock(status_code=200)
    login_resp.text = "Auth=FRESH\n"
    with (
        patch.object(client.session, "request", side_effect=[unauthorized, ok]),
        patch.object(client.session, "post", return_value=login_resp),
    ):
        result = client.unread_count()
    assert result == {"items": [], "continuation": None}
    assert client._auth_token == "FRESH"
