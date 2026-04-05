# Project Memory — overseerr-mcp

## Key decisions

- **Flat tool pattern:** 7 individual tools instead of a single action-router tool. Appropriate for the small, well-defined API surface.
- **No MCP resources:** All data access through tools. Resources may be added later for read-only endpoints.
- **Multi-transport:** Supports streamable-http (default), http, stdio, and sse. Dockerfile defaults to http on port 9151.
- **Bearer auth middleware:** Custom Starlette middleware with timing-safe comparison. `/health` exempted.
- **PyPI + GHCR + MCP Registry:** Triple-published on tag push via GitHub Actions.
- **DNS-based MCP Registry auth:** Uses `tootie.tv` domain with `MCP_PRIVATE_KEY` secret.

## Known issues

- Port default mismatch: Python code defaults to `6975`, Dockerfile defaults to `9151`. All deployments should set `OVERSEERR_MCP_PORT` explicitly.
- `OVERSEERR_MCP_ALLOW_DESTRUCTIVE` and `OVERSEERR_MCP_ALLOW_YOLO` are defined in `.env.example` but not yet implemented in tool logic.
- `.app.json` version is `1.0.0` while all other manifests are at `1.0.1`.

## Version history

- **1.0.1** (2026-04-03): Fixed OAuth discovery 401 cascade; added BearerAuthMiddleware WellKnownMiddleware; added authentication docs.
- **1.0.0**: Initial release with 7 tools, dual transport, pagination, destructive ops gate.
