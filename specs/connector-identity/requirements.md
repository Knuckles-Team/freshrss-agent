# CONN-FRESHRSS-AGENT-CONNECTOR-IDENTITY — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-FRESHRSS-AGENT-CONNECTOR-IDENTITY-R001` | **Fleet name.** `pyproject.toml` declares `freshrss-mcp` as the single `scion_sdk.connector` entry point. The content pack, the manifest `connector`, the fingerprints and the ingest binding all carry `freshrss-mcp`. Proving test: `tests/test_fleet_name.py::test_connector_name_is_the_fleet_name`. Caller chain: the `freshrss-mcp` console script (pyproject.toml, scion_sdk.cli:serve) loads `freshrss_agent:connector` (freshrss_agent/__init__.py) -> freshrss_agent/kg_ingest.py::_BINDING:49 (IngestBinding connector="freshrss-mcp") and freshrss_agent/connector_sources.py (server="freshrss-mcp"). Shape: tests/test_fleet_name.py checks the pyproject entry point and connector_name("freshrss_agent"); the name is set in pyproject.toml, kg_ingest.py::_BINDING and connector_sources.py, with no other literal. | Every connector name in the package is `freshrss-mcp`. |
