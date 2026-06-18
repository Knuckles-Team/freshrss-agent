# FreshRSS
## CLI or API | MCP | Agent

![PyPI - Version](https://img.shields.io/pypi/v/freshrss-agent)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
![PyPI - Downloads](https://img.shields.io/pypi/dd/freshrss-agent)
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/freshrss-agent)
![PyPI - License](https://img.shields.io/pypi/l/freshrss-agent)
![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/freshrss-agent)

*Version: 0.1.0*

> **Documentation** — Installation, deployment, usage across the API, CLI, and MCP
> interfaces, the integrated A2A agent server, and guidance for provisioning the
> backing platform are maintained in the
> [official documentation](https://knuckles-team.github.io/freshrss-agent/).

---

## Overview

**FreshRSS MCP Server + A2A Agent**

FreshRSS API + MCP Server + A2A Server

This repository is actively maintained - Contributions are welcome!

## MCP

### Using as an MCP Server

The MCP Server can be run in `stdio` (local), `streamable-http` (networked), or
`sse` mode.

#### Environment Variables

*   `FRESHRSS_URL`: The URL of the target service.
*   `FRESHRSS_API_PASSWORD`: The API token or access token.

#### stdio Transport (local IDEs — Cursor, Claude Desktop, VS Code)

```json
{
  "mcpServers": {
    "freshrss-mcp": {
      "command": "uvx",
      "args": ["--from", "freshrss-agent", "freshrss-mcp"],
      "env": {
        "FRESHRSS_URL": "https://service.example.com",
        "FRESHRSS_API_PASSWORD": "your_token"
      }
    }
  }
}
```

#### Streamable-HTTP Transport (networked / production)

```json
{
  "mcpServers": {
    "freshrss-mcp": {
      "command": "uvx",
      "args": ["--from", "freshrss-agent", "freshrss-mcp", "--transport", "streamable-http", "--port", "8000"],
      "env": {
        "TRANSPORT": "streamable-http",
        "HOST": "0.0.0.0",
        "PORT": "8000",
        "FRESHRSS_URL": "https://service.example.com",
        "FRESHRSS_API_PASSWORD": "your_token"
      }
    }
  }
}
```

<!-- BEGIN GENERATED: additional-deployment-options -->
### Additional Deployment Options

`freshrss-agent` can also run as a **local container** (Docker / Podman / `uv`) or be
consumed from a **remote deployment**. The
[Deployment guide](https://knuckles-team.github.io/freshrss-agent/deployment/) has full,
copy-paste `mcp_config.json` for all four transports — **stdio**, **streamable-http**,
**local container / uv**, and **remote URL**:

- **Local container / uv** — launch the server from `mcp_config.json` via `uvx`,
  `docker run`, or `podman run`, or point at a local streamable-http container by `url`.
- **Remote URL** — connect to a server deployed behind Caddy at
  `http://freshrss-mcp.arpa/mcp` using the `"url"` key.
<!-- END GENERATED: additional-deployment-options -->

## Install Python Package

```bash
python -m pip install freshrss-agent
```
