# Installation

`freshrss-agent` is a standard Python package and a prebuilt container image.

## Requirements

- **Python 3.11 – 3.14**.
- A reachable target service instance and access token.

## From PyPI (recommended)

```bash
pip install freshrss-agent
```

### Optional extras

| Extra | Install | Pulls in |
|---|---|---|
| `mcp` | `pip install "freshrss-agent[mcp]"` | FastMCP MCP-server runtime (`agent-utilities[mcp]`) |
| `agent` | `pip install "freshrss-agent[agent]"` | Pydantic-AI agent + Logfire tracing |
| `all` | `pip install "freshrss-agent[all]"` | Everything above |

## From source

```bash
git clone https://github.com/Knuckles-Team/freshrss-agent.git
cd freshrss-agent
pip install -e ".[all]"
```

## Docker

```bash
docker pull knucklessg1/freshrss-agent:latest
```
