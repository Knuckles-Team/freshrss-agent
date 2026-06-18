import pytest
from unittest.mock import patch

import freshrss_agent.auth as auth_module
from freshrss_agent.auth import get_client


@pytest.mark.concept("FRSS-001")
def test_get_client_auth_error():
    """CONCEPT:FRSS-001 get_client raises a friendly RuntimeError on bad credentials."""
    auth_module._client = None
    with patch("freshrss_agent.auth.ApiClientSystem") as mock_client_cls:
        mock_client_cls.side_effect = Exception("Auth Failure")
        with pytest.raises(RuntimeError) as exc_info:
            get_client()
        assert "AUTHENTICATION ERROR" in str(exc_info.value)
    auth_module._client = None
