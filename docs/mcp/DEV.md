# Development — overseerr-mcp

## Local setup

```bash
git clone https://github.com/jmagar/overseerr-mcp.git
cd overseerr-mcp
uv sync --dev
cp .env.example .env
# Edit .env with your Overseerr credentials
```

## Daily workflow

```bash
just dev          # start server locally (streamable-http on port 6975 or .env override)
just lint         # ruff check
just fmt          # ruff format
just typecheck    # ty check
just test         # pytest
just health       # curl /health
```

## Project structure

```
overseerr-mcp/
├── overseerr_mcp/
│   ├── __init__.py        # Package docstring
│   ├── server.py          # FastMCP server, tools, middleware, entrypoint
│   └── client.py          # OverseerrApiClient (async httpx)
├── skills/overseerr/
│   └── SKILL.md           # Claude-facing skill definition
├── hooks/
│   └── scripts/           # sync-uv.sh, , ensure-*.sh
├── scripts/               # Linting, security, smoke tests
├── tests/
│   ├── test_live.sh       # Integration test suite
│   └── TEST_COVERAGE.md   # Coverage notes
├── .claude-plugin/        # Claude Code manifest
├── .codex-plugin/         # Codex manifest
├── docs/                  # This documentation
├── Dockerfile             # Multi-stage Docker build
├── docker-compose.yml     # Compose deployment
├── entrypoint.sh          # Container entrypoint
├── pyproject.toml         # Python project config
├── Justfile               # Task runner recipes
└── server.json            # MCP Registry manifest
```

## Key modules

server.py

- Loads environment with `python-dotenv`
- Initializes `OverseerrApiClient`
- Defines 7 MCP tools via `@mcp.tool()` decorators
- `BearerAuthMiddleware` for HTTP auth
- `health_check` custom route
- `main()` dispatches by transport mode

client.py

- `OverseerrApiClient` wraps `httpx.AsyncClient`
- Base URL: `{OVERSEERR_URL}/api/v1`
- Auth via `X-Api-Key` header
- URL-encodes string parameters with `quote_plus`
- Handles HTTP errors, connection errors, and empty responses
- Returns structured data on success, error strings on failure

## Adding a new tool

1. Add the function to `server.py` with `@mcp.tool()` decorator
2. Use `ctx: Context` as first parameter to access `overseerr_client`
3. Return `dict | str` or `list[dict] | str` (error strings start with `"Error:"`)
4. Update the `_HELP_TEXT` string
5. Update `SKILL.md` tool reference
6. Update `README.md` tool table
7. Add test cases to `tests/test_live.sh`
8. Run `just lint && just typecheck`

## Code style

- Line length: 100 (ruff)
- Target: Python 3.12 (ruff), requires 3.10+ (pyproject.toml)
- Lint rules: E, F, I, UP (pycodestyle errors, pyflakes, isort, pyupgrade)
- Type hints on all functions
- Async/await for all I/O
- Google-style docstrings with Args/Returns sections

## Debugging

```bash
# Debug logging
OVERSEERR_LOG_LEVEL=DEBUG just dev

# Test a single tool
curl -X POST http://localhost:9151/mcp \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"search_media","arguments":{"query":"test"}}}'
```
