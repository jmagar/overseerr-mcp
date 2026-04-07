# Component Inventory — overseerr-mcp

Complete listing of all plugin components.

## MCP tools

| Tool | Parameters | Description | Destructive |
| --- | --- | --- | --- |
| `search_media` | `query` (str, required), `media_type` (str, optional) | Search movies or TV shows by title | no |
| `get_movie_details` | `tmdb_id` (int, required) | Fetch full movie details by TMDB ID | no |
| `get_tv_show_details` | `tmdb_id` (int, required) | Fetch full TV show details by TMDB ID | no |
| `request_movie` | `tmdb_id` (int, required) | Submit a movie request to Overseerr | yes |
| `request_tv_show` | `tmdb_id` (int, required), `seasons` (list[int], optional) | Submit a TV request, optionally scoped to seasons | yes |
| `list_failed_requests` | `count` (int, default 10), `skip` (int, default 0) | List failed requests with pagination | no |
| `overseerr_help` | — | Return built-in markdown help for all tools | no |

## MCP resources

| URI | Description | MIME type |
| --- | --- | --- |
| — | No resources exposed | — |

## HTTP endpoints

| Path | Method | Auth | Description |
| --- | --- | --- | --- |
| `/health` | GET | none | Liveness check, returns `{"status": "ok"}` |
| `/mcp` | POST | Bearer | MCP JSON-RPC endpoint (http/streamable-http transport) |
| `/sse` | GET | Bearer | Server-Sent Events endpoint (sse transport) |

## Environment variables

| Variable | Required | Default | Sensitive |
| --- | --- | --- | --- |
| `OVERSEERR_URL` | yes | — | no |
| `OVERSEERR_API_KEY` | yes | — | yes |
| `OVERSEERR_MCP_HOST` | no | `0.0.0.0` | no |
| `OVERSEERR_MCP_PORT` | no | `6975` | no |
| `OVERSEERR_MCP_TOKEN` | yes* | — | yes |
| `OVERSEERR_MCP_TRANSPORT` | no | `streamable-http` | no |
| `OVERSEERR_MCP_NO_AUTH` | no | `false` | no |
| `OVERSEERR_MCP_ALLOW_DESTRUCTIVE` | no | `false` | no |
| `OVERSEERR_MCP_ALLOW_YOLO` | no | `false` | no |
| `OVERSEERR_LOG_LEVEL` | no | `INFO` | no |
| `LOG_LEVEL` | no | `INFO` | no |
| `PUID` | no | `1000` | no |
| `PGID` | no | `1000` | no |
| `DOCKER_NETWORK` | no | `mcp-net` | no |
| `APPDATA_PATH` | no | `/mnt/appdata` | no |

## Plugin surfaces

| Surface | Present | Path |
| --- | --- | --- |
| Skills | yes | `skills/overseerr/SKILL.md` |
| Agents | no | — |
| Commands | no | — |
| Hooks | yes | `hooks/hooks.json`, `hooks/scripts/` |
| Channels | no | — |
| Output styles | no | — |
| Schedules | no | — |

## Client manifests

| File | Client | Purpose |
| --- | --- | --- |
| `.claude-plugin/plugin.json` | Claude Code | Plugin metadata and userConfig |
| `.codex-plugin/plugin.json` | Codex | Plugin metadata and interface |
| `gemini-extension.json` | Gemini | Extension metadata and MCP server config |
| `.mcp.json` | MCP clients | Server connection config |
| `.app.json` | Generic | App metadata |
| `server.json` | MCP Registry | Publishing metadata (tv.tootie/overseerr-mcp) |

## Docker

| Component | Value |
| --- | --- |
| Image | `ghcr.io/jmagar/overseerr-mcp:latest` |
| Port | `9151` |
| Health endpoint | `GET /health` (unauthenticated) |
| Compose file | `docker-compose.yml` |
| Entrypoint | `entrypoint.sh` |
| User | `mcpuser` (1000:1000) |
| Memory limit | 1024 MB |
| CPU limit | 1 |

## CI/CD workflows

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `ci.yml` | push to main, PR | lint, typecheck, test, version-sync, contract-drift, docker-security, mcp-integration |
| `docker-publish.yml` | push to main, tag push, PR | Build and push Docker image to GHCR, Trivy scan |
| `publish-pypi.yml` | tag push (`v*.*.*`) | Build, publish to PyPI, create GitHub Release, publish to MCP Registry |

## Scripts

| Script | Purpose |
| --- | --- |
| `scripts/smoke-test.sh` | Live smoke test via mcporter against running server |
| `scripts/check-docker-security.sh` | Dockerfile security checks (multi-stage, non-root, no secrets, healthcheck) |
| `scripts/check-no-baked-env.sh` | Verify no env vars baked into Docker artifacts |
| `scripts/check-outdated-deps.sh` | Report outdated Python dependencies |
| `scripts/ensure-ignore-files.sh` | Ensure .gitignore and .dockerignore have required patterns |
| `scripts/setup-data-dirs.sh` | Create data directories with correct ownership |

## Dependencies

### Runtime

| Package | Purpose |
| --- | --- |
| `fastmcp` (>=2.3.4) | MCP server framework |
| `httpx` (>=0.28.1) | Async HTTP client for Overseerr API |
| `python-dotenv` (>=1.1.0) | .env file loading |

### Development

| Package | Purpose |
| --- | --- |
| `ruff` (>=0.9) | Linter and formatter |
| `ty` (>=0.0.1a3) | Type checker |
| `pytest` (>=8.0) | Test framework |
| `pytest-asyncio` (>=0.23) | Async test support |
