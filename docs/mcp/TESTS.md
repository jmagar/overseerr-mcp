# Testing — overseerr-mcp

## Test strategy

| Layer | Tool | Location | What it covers |
| --- | --- | --- | --- |
| Unit | pytest | `tests/` | (Planned) Individual function behavior |
| Integration | test_live.sh | `tests/test_live.sh` | Full MCP stack: auth, protocol, tools |
| Smoke | smoke-test.sh | `bin/smoke-test.sh` | Quick verification via mcporter |

## Running tests

```bash
just test         # pytest (unit tests)
just test-live    # integration tests against live server
just lint         # ruff check
just typecheck    # ty check
```

## Unit tests (pytest)

```bash
uv run pytest .cache/pytest
```

Currently minimal. CI accepts exit code 5 (no tests collected) as passing.

## Integration tests (test_live.sh)

Full end-to-end tests against a running server. Requires `OVERSEERR_URL` and `OVERSEERR_API_KEY`.

### Modes

| Mode | Command | Description |
| --- | --- | --- |
| `http` | `bash tests/test_live.sh --mode http` | Tests against running HTTP server |
| `docker` | `bash tests/test_live.sh --mode docker` | Builds image, starts container, tests, tears down |
| `stdio` | `bash tests/test_live.sh --mode stdio` | Tests via mcporter stdio with uvx |
| `all` | `bash tests/test_live.sh` | Docker then stdio (default) |

### Test phases

1. **Health** — `GET /health` returns 200 with `{"status":"ok"}`
2. **Auth** — No token returns 401, bad token returns 401, good token succeeds
3. **Protocol** — `initialize` returns `serverInfo`, `tools/list` returns all 7 tools
4. **Tools** — Calls `overseerr_help`, `search_media` (movie, tv, generic), `get_movie_details`, `get_tv_show_details`, `list_failed_requests`

### Destructive tools

`request_movie` and `request_tv_show` are skipped in all test modes because they create real requests in Overseerr.

### CI integration

The `mcp-integration` job in `ci.yml` runs `test_live.sh` with secrets:

```yaml
env:
  OVERSEERR_URL: ${{ secrets.OVERSEERR_URL }}
  OVERSEERR_API_KEY: ${{ secrets.OVERSEERR_API_KEY }}
```

Only runs on push to main or PRs from the same repository.

## Smoke test (mcporter)

Quick verification against a running server using mcporter:

```bash
bash bin/smoke-test.sh [--url http://host:9151/mcp]
```

Tests all 7 tools. Destructive tools are skipped.

## Adding new tests

1. Add pytest tests to `tests/` for unit-level behavior
2. Add new tool assertions to `tests/test_live.sh` for integration coverage
3. Ensure CI picks up new tests automatically
