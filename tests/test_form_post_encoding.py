"""Write calls post form fields as httpx accepts them (list-of-tuples raised TypeError)."""

import httpx
import pytest

from freshrss_agent.api import FreshRSSApi
from freshrss_agent.api.api_client_base import _form_fields


def test_form_fields_merges_repeated_keys():
    assert _form_fields([("a", "1"), ("i", "x"), ("i", "y"), ("i", "z")]) == {
        "a": "1",
        "i": ["x", "y", "z"],
    }
    assert _form_fields(None) is None
    assert _form_fields({"k": "v"}) == {"k": "v"}


@pytest.mark.parametrize("op", ["subscribe", "unsubscribe", "mark_read"])
def test_write_calls_encode_through_httpx(op):
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("token"):
            return httpx.Response(200, text="WTOKEN")
        seen["body"] = request.content.decode()
        return httpx.Response(200, text="OK")

    client = FreshRSSApi(base_url="http://freshrss.local", username="a", api_password="p")
    client._auth_token = "TKN"
    client.session = httpx.Client(transport=httpx.MockTransport(handler))
    if op == "mark_read":
        client.mark_read(["i1", "i2"])
        assert seen["body"].count("i=") == 2
    else:
        getattr(client, op)("http://example.org/feed.xml")
        assert "T=WTOKEN" in seen["body"]
