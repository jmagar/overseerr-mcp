# Marketplace — overseerr-mcp

## Claude Code marketplace

overseerr-mcp is listed in the `jmagar/claude-homelab` marketplace.

### Installation

```bash
/plugin marketplace add jmagar/claude-homelab
/plugin install overseerr-mcp @jmagar-claude-homelab
```

### Marketplace entry

The plugin is listed as an external repo-sourced plugin in `.claude-plugin/marketplace.json` of the `claude-homelab` repo:

```json
{
  "name": "overseerr-mcp",
  "source": {
    "type": "repo",
    "url": "https://github.com/jmagar/overseerr-mcp"
  },
  "category": "media",
  "description": "Search movies and TV shows, submit requests, and monitor failed requests via Overseerr."
}
```

## PyPI

Published as `overseerr-mcp` on PyPI:

```bash
pip install overseerr-mcp
# or: uvx overseerr-mcp-server
```

https://pypi.org/project/overseerr-mcp/

## GHCR (Docker)

Published to GitHub Container Registry:

```bash
docker pull ghcr.io/jmagar/overseerr-mcp:latest
```

https://github.com/jmagar/overseerr-mcp/pkgs/container/overseerr-mcp

## MCP Registry

Published as `tv.tootie/overseerr-mcp`:

- DNS-authenticated via `tootie.tv` domain
- Package type: PyPI
- Runtime hint: `uvx`
- Transport: stdio
