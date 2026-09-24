"""TLS-profile coverage for ``freshrss_agent`` guarding against a regression
back to a bare ``FRESHRSS_SSL_VERIFY`` boolean or a ``urllib3.disable_warnings``
call: TLS verification must stay on by default and a configured profile must
be honoured end-to-end (base client + auth.py + the OIDC delegation path).
"""

import os
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from agent_connector_sdk.auth.delegation import DelegationSettings
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

import freshrss_agent.auth as auth_module
from freshrss_agent.api import FreshRSSApi
from freshrss_agent.auth import get_client

_DELEGATION_SETTINGS = DelegationSettings(
    enabled=True,
    token_endpoint="https://idp.example/token",
    client_id="freshrss-agent",
    client_secret_ref="env://FRESHRSS_OIDC_CLIENT_SECRET",
    audience="https://freshrss.internal",
    scopes="api",
)


def _self_signed_ca_pem(common_name: str) -> str:
    now = datetime.now(UTC)
    key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    certificate = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), True)
        .sign(key, hashes.SHA256())
    )
    return certificate.public_bytes(serialization.Encoding.PEM).decode("ascii")


def test_client_verifies_by_default():
    """No TLS env vars configured -> the resolved profile still verifies."""
    with patch.dict(os.environ, {}, clear=True):
        client = FreshRSSApi(
            base_url="http://freshrss.local", username="admin", api_password="pw"
        )
        assert client.tls_profile.verify_enabled is True
        assert client.session.verify is True


def test_client_honors_ca_bundle_profile(tmp_path):
    """A configured CA bundle (the standard SSL_CERT_FILE override) is
    resolved and applied to the session — proving a private-PKI instance is
    configured with its CA rather than by disabling verification."""
    ca_bundle = tmp_path / "freshrss-ca.pem"
    ca_bundle.write_text(_self_signed_ca_pem("Synthetic FreshRSS Test Root"))
    with patch.dict(os.environ, {"SSL_CERT_FILE": str(ca_bundle)}, clear=True):
        client = FreshRSSApi(
            base_url="https://freshrss.internal", username="admin", api_password="pw"
        )
        assert client.tls_profile.verify_enabled is True
        assert client.tls_profile.ca_bundle_path == ca_bundle
        assert client.session.verify == str(ca_bundle)


def test_client_honors_named_tls_profile():
    """``FRESHRSS_TLS_PROFILE`` selects a named profile from the catalog —
    proving the documented env var is actually wired end-to-end."""
    catalog = (
        '{"profiles": {"private-pki": {"system_trust": false, '
        '"ca_directory": "/etc/ssl/certs"}}}'
    )
    auth_module._client = None
    with patch.dict(
        os.environ,
        {
            "FRESHRSS_URL": "https://freshrss.internal",
            "FRESHRSS_API_PASSWORD": "pw",
            "FRESHRSS_TLS_PROFILE": "private-pki",
            "TLS_PROFILES": catalog,
        },
        clear=True,
    ):
        client = get_client()
        assert client.tls_profile.verify_enabled is True
        assert client.tls_profile.name == "private-pki"
        assert client.tls_profile.system_trust is False
    auth_module._client = None


@pytest.mark.concept("FR-OS.identity.frss")
def test_delegation_path_never_passes_verify_kwarg():
    """The OIDC delegation path must call the SDK's ``delegated_token()``
    wrapper (which owns its own httpx transport, never a bare ``verify=``
    kwarg) and must construct the client with a resolved TLS profile, never a
    bare boolean."""
    auth_module._client = None
    with patch.dict(
        os.environ,
        {"FRESHRSS_URL": "https://freshrss.internal"},
        clear=True,
    ):
        with patch.object(
            DelegationSettings, "from_settings", return_value=_DELEGATION_SETTINGS
        ):
            with patch(
                "freshrss_agent.auth.delegated_token", return_value="delegated-token"
            ) as mock_delegated:
                with patch(
                    "freshrss_agent.auth.current_user_identity",
                    return_value="actor:test",
                ):
                    with patch("freshrss_agent.auth.ApiClientSystem") as mock_cls:
                        client = get_client()
                        assert client is not None
                        mock_delegated.assert_called_once_with(_DELEGATION_SETTINGS)
                        _, client_kwargs = mock_cls.call_args
                        assert client_kwargs["api_password"] == "delegated-token"
                        assert client_kwargs["tls_profile"].verify_enabled is True
    auth_module._client = None
