# Concept Registry — freshrss-agent

> **Prefix**: `CONCEPT:FRSS-*`
> **Version**: 0.1.0
> **Bridge**: [`CONCEPT:AU-ECO.messaging.native-backend-abstraction`](https://github.com/Knuckles-Team/agent-connector-sdk/blob/main/docs/concepts.md) (Unified Toolkit Ingestion)

---

## Project-Specific Concepts

| Concept ID | Name | Description |
|------------|------|-------------|
| `CONCEPT:FR-OS.identity.frss` | Reader Operations | MCP tool domain `reader` — action-routed stream contents, item bodies, and unread counts via the GReader API |
| `CONCEPT:FR-OS.governance.frss` | Subscription Curation | MCP tool domain `subscriptions` — action-routed feed subscribe/unsubscribe/label, categories, and item tagging (read/star) |

## Cross-Project References (from agent-connector-sdk)

| Concept ID | Name | Origin |
|------------|------|--------|
| `CONCEPT:AU-ECO.messaging.native-backend-abstraction` | Unified Toolkit Ingestion | agent-connector-sdk |
| `CONCEPT:AU-ORCH.adapter.hot-cache-invalidation` | Confidence-Gated Router | agent-connector-sdk |
| `CONCEPT:AU-OS.config.secrets-authentication` | Prompt Injection Defense | agent-connector-sdk |
