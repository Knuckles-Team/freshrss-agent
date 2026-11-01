# CONN-FRESHRSS-AGENT-SDK-CENTRALIZATION — Requirements

Governing specification: [spec.md](spec.md).

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-FRESHRSS-AGENT-SDK-CENTRALIZATION-R001` | **Governed HTTP.** The connector must reach FreshRSS only through the SDK governed HTTP client in `freshrss_agent/api/api_client_base.py`. It must not import `requests`. Caller chain: arbora fleet.call -> a FreshRSS MCP tool (freshrss_agent/mcp_server.py) -> freshrss_agent/auth.py::get_client -> freshrss_agent/api/api_client_base.py::FreshRSSClientBase, whose __init__ builds self.session with create_http_client. Shape: FreshRSSClientBase.__init__ uses scion_sdk.http.client.create_http_client with HttpClientOptions and resolve_tls_profile("freshrss"); FreshRSSApi subclasses it, and no module imports requests. | `tests/test_sdk_centralization.py::test_api_client_uses_sdk_http_client` must observe an SDK client and no `requests` import. |
