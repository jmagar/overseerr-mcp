# Publishing — overseerr-mcp

## Registries

| Registry | Package name | URL |
| --- | --- | --- |
| PyPI | `overseerr-mcp` | https://pypi.org/project/overseerr-mcp/ |
| GHCR | `ghcr.io/jmagar/overseerr-mcp` | https://github.com/jmagar/overseerr-mcp/pkgs/container/overseerr-mcp |
| MCP Registry | `tv.tootie/overseerr-mcp` | https://registry.modelcontextprotocol.io |

## Version files

All must be in sync before publishing:

| File | Field |
| --- | --- |
| `pyproject.toml` | `version = "X.Y.Z"` |
| `.claude-plugin/plugin.json` | `"version": "X.Y.Z"` |
| `.codex-plugin/plugin.json` | `"version": "X.Y.Z"` |
| `gemini-extension.json` | `"version": "X.Y.Z"` |
| `server.json` | `"version": "X.Y.Z"` |

## Publishing with Justfile

```bash
just publish patch   # 1.0.1 → 1.0.2
just publish minor   # 1.0.1 → 1.1.0
just publish major   # 1.0.1 → 2.0.0
```

The `publish` recipe:
1. Verifies you are on `main` with a clean working tree
2. Pulls latest from origin
3. Reads current version from `pyproject.toml`
4. Computes new version based on bump type
5. Updates `pyproject.toml`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `gemini-extension.json`
6. Commits as `release: vX.Y.Z`
7. Tags as `vX.Y.Z`
8. Pushes to origin with tags

## Automated publishing

Tag push triggers two workflows:

### PyPI (publish-pypi.yml)

1. Verifies tag matches `pyproject.toml` version
2. Builds with `uv build`
3. Publishes to PyPI with `pypa/gh-action-pypi-publish` (OIDC, no API token)
4. Creates GitHub Release with auto-generated notes
5. Publishes to MCP Registry via `mcp-publisher`

### Docker (docker-publish.yml)

1. Builds multi-platform image (`linux/amd64`, `linux/arm64`)
2. Pushes to `ghcr.io/jmagar/overseerr-mcp` with semver tags
3. Runs Trivy vulnerability scan

## MCP Registry

### server.json

```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "tv.tootie/overseerr-mcp",
  "title": "Overseerr MCP",
  "description": "MCP server for Overseerr media requests and discovery.",
  "repository": {
    "url": "https://github.com/jmagar/overseerr-mcp",
    "source": "github"
  },
  "packages": [
    {
      "registryType": "pypi",
      "identifier": "overseerr-mcp",
      "runtimeHint": "uvx",
      "transport": { "type": "stdio" }
    }
  ]
}
```

### DNS authentication

The MCP Registry uses DNS-based authentication for the `tootie.tv` domain. The `MCP_PRIVATE_KEY` secret is used by `mcp-publisher login dns`.

## Manual publishing

If automated publishing fails:

```bash
# PyPI
uv build
twine upload dist/*

# Docker
docker build -t ghcr.io/jmagar/overseerr-mcp:latest .
docker push ghcr.io/jmagar/overseerr-mcp:latest

# MCP Registry
./mcp-publisher login dns --domain tootie.tv --private-key <key>
./mcp-publisher publish
```
