import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_api_client():
    client = MagicMock()
    client.stream_contents.return_value = {"items": [], "continuation": None}
    client.subscription_list.return_value = {"subscriptions": []}
    return client
