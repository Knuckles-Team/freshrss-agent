# CONN-FRESHRSS-AGENT-SDK-CENTRALIZATION — Requirements

Governing specification: [spec.md](spec.md).

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-FRESHRSS-AGENT-SDK-CENTRALIZATION-R001` | **Governed HTTP.** The connector must reach FreshRSS only through the SDK governed HTTP client in `freshrss_agent/api/api_client_base.py`. It must not import `requests`. | `tests/test_sdk_centralization.py::test_api_client_uses_sdk_http_client` must observe an SDK client and no `requests` import. |
