# Overseerr MCP

MCP server for searching Overseerr media, retrieving TMDB-backed details, and submitting movie or TV requests from Claude, Codex, or any MCP client.

## What this repository ships

- `overseerr_mcp/`: FastMCP server and Overseerr API client
- `.claude-plugin/`, `.codex-plugin/`, `gemini-extension.json`: client manifests
- `skills/overseerr/`: Claude-facing skill docs
- `docker-compose.yml`, `Dockerfile`, `entrypoint.sh`: container deployment
- `docs/overseerr-api.yaml`: bundled Overseerr API reference
- `scripts/`: linting, Docker, and smoke-test helpers

## Runtime model

The server talks to an existing Overseerr instance via its REST API and exposes these MCP tools:

| Tool | Purpose |
| --- | --- |
| `search_media` | Search movies or TV shows |
| `get_movie_details` | Fetch movie details by TMDB ID |
| `get_tv_show_details` | Fetch show details by TMDB ID |
| `request_movie` | Submit a movie request |
| `request_tv_show` | Submit a TV request, optionally scoped to seasons |
| `list_failed_requests` | List failed requests |
| `overseerr_help` | Return built-in tool help |

The server also exposes `GET /health` for liveness checks.

## Installation

### Marketplace

```bash
/plugin marketplace add jmagar/claude-homelab
/plugin install overseerr-mcp @jmagar-claude-homelab
```

### Local development

```bash
uv sync --dev
uv run overseerr-mcp-server
```

Alternative entrypoint:

```bash
uv run python -m overseerr_mcp
```

## Configuration

Create `.env` from `.env.example` and set, at minimum:

```bash
OVERSEERR_URL=https://your-overseerr-instance.example.com
OVERSEERR_API_KEY=your_overseerr_api_key
OVERSEERR_MCP_TRANSPORT=streamable-http
OVERSEERR_MCP_HOST=0.0.0.0
OVERSEERR_MCP_PORT=9151
OVERSEERR_MCP_TOKEN=...
OVERSEERR_MCP_NO_AUTH=false
OVERSEERR_MCP_ALLOW_DESTRUCTIVE=false
OVERSEERR_MCP_ALLOW_YOLO=false
OVERSEERR_LOG_LEVEL=INFO
```

Notes:

- `OVERSEERR_URL` and `OVERSEERR_API_KEY` are required or the server exits at startup.
- `OVERSEERR_MCP_TRANSPORT` supports `streamable-http`, `http`, `stdio`, and `sse`.
- For HTTP transports, use Bearer auth unless `OVERSEERR_MCP_NO_AUTH=true`.
- Set `OVERSEERR_MCP_PORT` explicitly. `.env.example` recommends `9151`; if unset, the current server fallback in code is `6975`.

## Typical usage

1. Search:

```text
search_media(query="Dune")
```

2. Inspect details:

```text
get_movie_details(tmdb_id=438631)
```

3. Request:

```text
request_movie(tmdb_id=438631)
```

4. Review failures:

```text
list_failed_requests(count=20)
```

## Development commands

```bash
just dev
just lint
just fmt
just typecheck
just test
just up
just logs
just health
```

Key recipes from `Justfile`:

- `just dev`: `uv run python -m overseerr_mcp`
- `just test`: run tests
- `just check-contract`: run plugin contract lint
- `just gen-token`: generate a Bearer token with `openssl rand -hex 32`

## Verification

Recommended verification after changes:

```bash
just lint
just typecheck
just test
just health
```

If you need a live end-to-end check:

```bash
just test-live
```

## Related files

- `overseerr_mcp/server.py`: MCP server and tool definitions
- `overseerr_mcp/client.py`: Overseerr HTTP client
- `docs/overseerr-api.yaml`: upstream API contract
- `skills/overseerr/`: skill docs for Claude clients
- `CHANGELOG.md`: release history

## License

MIT
