"""PIPE-CONNSPEC-R122.4: the FreshRSS development skill is packaged."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "freshrss_agent" / "skills" / "freshrss-agent-development" / "SKILL.md"

pytestmark = pytest.mark.spec("PIPE-CONNSPEC-R122.4")


def test_development_skill_has_rapid_contract_and_package_binding() -> None:
    text = SKILL.read_text(encoding="utf-8")
    frontmatter = text.split("---", 2)[1]
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert SKILL.is_file()
    assert re.search(r"^name:\s*freshrss-agent-development\s*$", frontmatter, re.M)
    assert re.search(r"^skill_type:\s*skill\s*$", frontmatter, re.M)
    assert "## Rapid delivery: the 5-minute contract" in text
    for term in (
        "freshrss_agent/__init__.py",
        "freshrss_agent/api_client.py",
        "freshrss_agent/api/",
        "freshrss_agent/auth.py",
        "freshrss_agent/mcp/",
        "freshrss_agent/mcp_server.py",
        "freshrss_agent/kg_ingest.py",
        "freshrss_agent/connector_sources.py",
        "FRESHRSS_URL",
        "FRESHRSS_USER",
        "FRESHRSS_API_PASSWORD",
        "FRESHRSS_TLS_PROFILE",
        "FRESHRSS_TLS_PROFILE_REF",
        "ENABLE_DELEGATION",
        "skills/**",
        "ontology/**",
        "uv run --locked --extra test pytest",
    ):
        assert term in text

    assert "verify=False" not in text
    assert "--no-verify" not in text
    package_data = project["tool"]["setuptools"]["package-data"]["freshrss_agent"]
    assert "skills/**" in package_data
    assert project["project"]["entry-points"]["agent_connector_sdk.connector"] == {
        "freshrss-mcp": "freshrss_agent:connector"
    }
