# Live Smoke Testing (mcporter) — overseerr-mcp

End-to-end verification against a running server.

## Location

```
bin/smoke-test.sh
```

## Usage

```bash
bash bin/smoke-test.sh [--url http://host:9151/mcp]
bash bin/smoke-test.sh --config path/to/mcporter.json
```

## Requirements

- `mcporter` (installed via npm)
- `curl`
- `python3`
- Running overseerr-mcp server

## Test phases

### Phase 1: Pre-flight

- Health endpoint responds with `{"status":"ok"}`
- mcporter lists all 7 tools

### Phase 2: Tool tests (read-only)

| Tool | Test parameters |
| --- | --- |
| `overseerr_help` | No args — verifies non-empty response |
| `search_media` | `query=test` — verifies no error, non-empty results |
| `search_media` | `query=test, media_type=movie` — verifies filter works |
| `get_movie_details` | `tmdb_id=550` (Fight Club) — verifies details returned |
| `get_tv_show_details` | `tmdb_id=1396` (Breaking Bad) — verifies details returned |
| `list_failed_requests` | `count=5, skip=0` — verifies response |

### Skipped (destructive)

- `request_movie` — creates real request
- `request_tv_show` — creates real request

### Phase 3: Summary

Reports pass/fail/skip counts. Exit code 0 = all passed.

## Assertions

- `assert_no_error` — MCP response has `isError` absent or false
- `assert_non_empty_text` — response contains non-empty text content
- `assert_eq` — field equals expected value
- `assert_gte` — field is integer >= minimum
