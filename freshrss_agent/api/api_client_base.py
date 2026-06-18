#!/usr/bin/python
"""GReader (Google Reader compatible) HTTP base client for FreshRSS."""

import logging
from typing import Any

import requests
import urllib3
from agent_utilities.base_utilities import get_logger
from agent_utilities.core.exceptions import AuthError, UnauthorizedError

logger = get_logger(__name__)


class FreshRSSClientBase:
    """Base client for the FreshRSS Google Reader compatible API (GReader).

    Implements the GReader auth flow:
      1. ``ClientLogin`` exchanges ``Email``/``Passwd`` for an ``Auth`` token.
      2. Authenticated requests send ``Authorization: GoogleLogin auth=<token>``.
      3. Write actions require a short-lived POST token (``T`` form field) fetched
         from the ``token`` endpoint.
      4. On HTTP 401 the client re-runs ClientLogin once and retries.
    """

    def __init__(
        self,
        base_url: str | None,
        username: str | None,
        api_password: str | None,
        verify: bool = True,
    ):
        self.base_url = (base_url or "").rstrip("/")
        self.username = username or ""
        self.api_password = api_password or ""
        self.verify = verify
        self.session = requests.Session()
        self._auth_token: str | None = None

        if self.verify is False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # -- internals -----------------------------------------------------------

    def _greader_url(self, path: str) -> str:
        return f"{self.base_url}/api/greader.php/{path.lstrip('/')}"

    def _login(self) -> str:
        """Run ClientLogin and cache the ``Auth`` token."""
        url = self._greader_url("accounts/ClientLogin")
        response = self.session.post(
            url,
            data={"Email": self.username, "Passwd": self.api_password},
            verify=self.verify,
            timeout=30,
        )
        if response.status_code in (401, 403):
            logger.error("FreshRSS ClientLogin failed: %s", response.status_code)
            raise AuthError if response.status_code == 401 else UnauthorizedError
        response.raise_for_status()
        token: str | None = None
        for line in response.text.splitlines():
            if line.startswith("Auth="):
                token = line[len("Auth=") :].strip()
                break
        if not token:
            raise AuthError
        self._auth_token = token
        return token

    def _auth_headers(self) -> dict[str, str]:
        if not self._auth_token:
            self._login()
        return {"Authorization": f"GoogleLogin auth={self._auth_token}"}

    def _get_write_token(self) -> str:
        """Fetch a short-lived POST token required by write actions."""
        response = self.session.get(
            self._greader_url("reader/api/0/token"),
            headers=self._auth_headers(),
            verify=self.verify,
            timeout=30,
        )
        if response.status_code == 401:
            self._login()
            response = self.session.get(
                self._greader_url("reader/api/0/token"),
                headers=self._auth_headers(),
                verify=self.verify,
                timeout=30,
            )
        response.raise_for_status()
        return response.text.strip()

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        data: Any | None = None,
    ) -> Any:
        """Issue an authenticated GReader request, retrying once on 401.

        ``output=json`` is always injected so JSON responses are returned. The
        JSON body is decoded when possible; otherwise the raw text is returned.
        """
        params = dict(params or {})
        params.setdefault("output", "json")
        url = self._greader_url(path)

        def _send() -> requests.Response:
            return self.session.request(
                method,
                url,
                params=params,
                data=data,
                headers=self._auth_headers(),
                verify=self.verify,
                timeout=60,
            )

        response = _send()
        if response.status_code == 401:
            # Token expired — re-login once and retry.
            self._auth_token = None
            response = _send()
        if response.status_code == 401:
            logger.error("FreshRSS request unauthorized after re-login: %s", url)
            raise AuthError
        response.raise_for_status()
        try:
            return response.json()
        except ValueError:
            return {"status": response.status_code, "text": response.text}

    def set_debug(self, debug: bool = False) -> None:
        logger.setLevel(logging.DEBUG if debug else logging.ERROR)
