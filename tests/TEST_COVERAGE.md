# overseerr-mcp — Integration Test Coverage

**File:** `tests/test_live.sh`
**Last reviewed:** 2026-04-04

---

## 1. Overview

`tests/test_live.sh` is the canonical end-to-end integration test for the `overseerr-mcp` project. It exercises the MCP server at the HTTP protocol level (JSON-RPC 2.0 over HTTP POST) against a live Overseerr instance, verifying that:

- The MCP server's HTTP transport is reachable and healthy.
- Bearer token authentication is enforced correctly.
- The MCP `initialize` and `tools/list` protocol handshakes succeed.
- Every registered tool responds with valid, well-formed output from the live Overseerr backend.

**Service under test:** [Overseerr](https://overseerr.dev/) — a media request manager that integrates with Plex, Radarr, and Sonarr.

**MCP server under test:** `overseerr-mcp` — a Python FastMCP server (`overseerr_mcp/server.py`) that wraps the Overseerr REST API and exposes it as MCP tools over HTTP (streamable-http transport) or stdio.

**Test framework:** Pure Bash with `curl` for HTTP and `jq` for JSON assertion. No external test framework (e.g., pytest, bats) is used. Results are printed with `[PASS]`, `[FAIL]`, and `[SKIP]` prefixes, counters are accumulated, and the script exits `0` on full pass or `1` on any failure.

---

## 2. How to Run

### Required Environment Variables

| Variable | Purpose | Required |
|---|---|---|
| `OVERSEERR_URL` | Full URL of the live Overseerr instance (e.g., `https://overseerr.example.com`) | Yes |
| `OVERSEERR_API_KEY` | Overseerr API key with read access | Yes |
| `PORT` | Port for the MCP HTTP server (default: `9151`) | No |

If the variables are not set in the shell, the script automatically attempts to source them from `~/.claude-homelab/.env` before aborting.

### Modes

The script supports four modes selected via `--mode`:

| Mode | What it does | Command |
|---|---|---|
| `http` | Runs all four test phases against an already-running MCP server | `bash tests/test_live.sh --mode http --url http://localhost:9151` |
| `docker` | Builds the Docker image, starts a container, runs all four HTTP phases, tears down | `bash tests/test_live.sh --mode docker` |
| `stdio` | Runs a reduced test suite against the MCP server over stdio via `mcporter` + `uvx` | `bash tests/test_live.sh --mode stdio` |
| `all` | Runs `docker` then `stdio` (default when no `--mode` is specified) | `bash tests/test_live.sh` |

### Full Argument Reference

```bash
bash tests/test_live.sh \
  [--mode http|docker|stdio|all] \   # default: all
  [--url http://host:port]           \   # default: http://localhost:$PORT
  [--token <bearer-token>]           \   # default: ci-integration-token
  [--verbose]                           # prints full response bodies
```

### Exit Codes

| Code | Meaning |
|---|---|
| `0` | All tests passed |
| `1` | One or more tests failed (summary printed) |
| `2` | Prerequisite or startup error (missing `curl`/`jq`, missing credentials, Docker build failure, server failed to become healthy) |

### Log File

Every run writes a timestamped log to `$TMPDIR/overseerr-mcp-test.<YYYYMMDD-HHMMSS>.log` (typically `/tmp/`). The log path is printed in the summary. In non-verbose mode only request lines are logged; in `--verbose` mode full response bodies are appended.

---

## 3. Test Phases

The script is organized into four sequential phases for HTTP modes, plus an independent stdio test suite.

### Phase 1 — Health (`phase_health`)

**Purpose:** Verify the MCP server's unauthenticated health endpoint is reachable and returns the expected status document. This is the most basic liveness check — it does not require a Bearer token and does not touch the Overseerr backend.

**What is validated:**
1. `GET /health` returns HTTP `200`.
2. The JSON response body contains `"status": "ok"` (extracted via `.status` jq path).

**Pass criteria:** HTTP 200 AND `.status == "ok"`.
**Fail criteria:** Any non-200 status, or a 200 with a response body that does not have `.status == "ok"`.

---

### Phase 2 — Auth Enforcement (`phase_auth`)

**Purpose:** Verify that the MCP server's `/mcp` endpoint enforces Bearer token authentication and that a valid token is accepted.

**Three scenarios are tested:**

#### 2a. No token → 401
- Request: `POST /mcp` with no `Authorization` header.
- Body: `{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}`
- Expected: HTTP `401`.
- Pass: status code is exactly `"401"`.
- Fail: any other status code.

#### 2b. Bad token → 401
- Request: `POST /mcp` with `Authorization: Bearer definitely-wrong-token`.
- Body: same `initialize` payload.
- Expected: HTTP `401`.
- Pass: status code is exactly `"401"`.
- Fail: any other status code.

#### 2c. Good token → not 401/403
- Request: `POST /mcp` with `Authorization: Bearer <TOKEN>` (default: `ci-integration-token`).
- Body: full MCP `initialize` request with `protocolVersion: "2024-11-05"`.
- Expected: any HTTP status other than `401` or `403`.
- Pass: status is neither `401` nor `403`.
- Fail: status is `401` or `403`.

**Note:** The good-token test deliberately does not assert a specific success code (e.g., `200`) because the protocol may respond with `202` or other 2xx codes depending on transport negotiation. It only confirms the token is accepted.

---

### Phase 3 — MCP Protocol (`phase_protocol`)

**Purpose:** Verify the JSON-RPC 2.0 MCP protocol handshake works correctly: `initialize` returns server metadata and `tools/list` returns the complete, expected tool manifest.

#### 3a. `initialize`
- Request: `POST /mcp` — `{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1"}}}`
- Assertions:
  - HTTP `200`.
  - `.result.serverInfo.name` is non-null and non-empty (jq path: `.result.serverInfo.name`).
- Pass: Both the HTTP status and the jq assertion succeed.
- Fail: HTTP non-200, or `.result.serverInfo.name` is null/missing.

#### 3b. `tools/list` — HTTP status
- Request: `POST /mcp` — `{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}`
- Assertion: HTTP `200`.
- Pass/Fail: status is/is not `200`.

#### 3c. `tools/list` — tool presence (7 assertions, one per tool)
For each of the following tool names, the response body is checked:

| Tool Name | jq check |
|---|---|
| `search_media` | `[.result.tools[].name] \| map(select(. == "search_media")) \| length >= 1` |
| `get_movie_details` | same pattern |
| `get_tv_show_details` | same pattern |
| `request_movie` | same pattern |
| `request_tv_show` | same pattern |
| `list_failed_requests` | same pattern |
| `overseerr_help` | same pattern |

Each produces an independent `[PASS]` or `[FAIL]` line labeled `tools/list contains: <tool_name>`.

**Total assertions in Phase 3:** up to 9 (initialize HTTP, initialize serverInfo, tools/list HTTP, plus 7 tool-presence checks).

---

### Phase 4 — Tool Calls, Read-Only (`phase_tools`)

**Purpose:** Exercise each read-only tool end-to-end by calling it through the MCP server and validating that the response contains semantically meaningful data from the live Overseerr/TMDB backend. Write/mutation tools (`request_movie`, `request_tv_show`) are explicitly excluded to avoid creating unwanted media requests.

The helper function `call_tool` is used for all tool invocations. It:
1. Builds a JSON-RPC 2.0 `tools/call` request body.
2. POSTs to `/mcp`.
3. Fails the test if HTTP status is not `200`.
4. Fails the test if `.result.isError == true` in the response (extracting the error message from `.result.content[0].text`).
5. On success, stores the response in `$LAST_TOOL_BODY` for subsequent assertions.

---

#### Tool: `overseerr_help`

**Arguments:** `{}`

**Assertions:**
1. `call_tool` succeeds (HTTP 200, `isError != true`) — label: `overseerr_help: HTTP 200 + no isError`.
2. `.result.content[0].text` contains the substring "overseerr" (case-insensitive grep) — label: `overseerr_help: text contains 'overseerr'`.

**Proving correct operation:** The tool returns a help/documentation string. The test confirms the string actually mentions the service name, ruling out empty, wrong-server, or placeholder responses.

---

#### Tool: `search_media` (movie variant)

**Arguments:** `{"query":"The Matrix","media_type":"movie"}`

**Assertions:**
1. `call_tool` succeeds — label: `search_media movie (The Matrix): HTTP 200`.
2. `.result.content[0].text | fromjson | length > 0` — the parsed JSON text field is a non-empty array — label: `search_media movie: results array non-empty`.
3. `.result.content[0].text | fromjson | .[0].tmdbId | strings // tonumber | tostring` — the first result has a non-null `tmdbId` field — label: `search_media movie: first result has tmdbId`.

**Side effect (no assertion):** The `tmdbId` of the first result is captured into the shell variable `matrix_id` for use by `get_movie_details`.

**Proving correct operation:** The tool must decode the text payload as JSON, return at least one result, and the first result must carry a TMDB identifier — confirming a live TMDB/Overseerr search was executed, not a cached stub.

---

#### Tool: `search_media` (TV variant)

**Arguments:** `{"query":"Breaking Bad","media_type":"tv"}`

**Assertions:**
1. `call_tool` succeeds — label: `search_media tv (Breaking Bad): HTTP 200`.
2. `.result.content[0].text | fromjson | length > 0` — label: `search_media tv: results array non-empty`.

**Side effect:** The `tmdbId` of the first result is captured into `bb_id` for use by `get_tv_show_details`.

---

#### Tool: `search_media` (generic/no media_type variant)

**Arguments:** `{"query":"Inception"}` (no `media_type` field)

**Assertions:**
1. `call_tool` succeeds — label: `search_media generic (Inception): HTTP 200`.
2. `.result.content[0].text | fromjson | length > 0` — label: `search_media generic: results non-empty`.

**Purpose:** Confirms the tool works without the optional `media_type` argument.

---

#### Tool: `get_movie_details`

**Arguments:** `{"tmdb_id": <matrix_id>}` — dynamically set from the `search_media` movie result.

**Condition:** Only runs if `matrix_id` is non-empty and non-null. If `search_media` failed to return a `tmdbId`, this test is `[SKIP]`ed with message `get_movie_details (no tmdbId from search)`.

**Assertions:**
1. `call_tool` succeeds — label: `get_movie_details (tmdbId=<id>): HTTP 200`.
2. `.result.content[0].text | fromjson | .title | strings | select(length > 0)` — the detail object has a non-empty `.title` string — label: `get_movie_details: result has title`.

**Proving correct operation:** The response object must be parseable JSON and contain a `.title` field with a real string value, confirming the Overseerr movie detail endpoint was reached and returned a real movie record.

---

#### Tool: `get_tv_show_details`

**Arguments:** `{"tmdb_id": <bb_id>}` — dynamically set from the `search_media` TV result.

**Condition:** Only runs if `bb_id` is non-empty and non-null. Skipped with `get_tv_show_details (no tmdbId from search)` otherwise.

**Assertions:**
1. `call_tool` succeeds — label: `get_tv_show_details (tmdbId=<id>): HTTP 200`.
2. `.result.content[0].text | fromjson | (.name // .title) | strings | select(length > 0)` — the detail object has either a non-empty `.name` or `.title` string — label: `get_tv_show_details: result has name/title`.

**Note on dual-field assertion:** TV shows in the Overseerr/TMDB API may use `.name` rather than `.title`. The jq expression `(.name // .title)` handles both, making the test schema-tolerant.

---

#### Tool: `list_failed_requests`

**Arguments:** `{"count":5}`

**Assertions:**
1. `call_tool` succeeds — label: `list_failed_requests (count=5): HTTP 200`.
2. The text content is validated with three-way branching (all branches result in `[PASS]`):
   - Branch A: `.result.content[0].text` parses as a JSON array or object (`jq 'if type == "array" or type == "object" then "ok" else error end'`) — label: `list_failed_requests: response is valid JSON array/object`.
   - Branch B: The text contains the substring `"No failed requests"` — label: `list_failed_requests: no failures (expected)`.
   - Branch C: The text is any other non-empty string — label: `list_failed_requests: got response (<first 60 chars>)`.

**Proving correct operation:** The test accepts any well-formed response from the tool, including an empty queue. This is intentional: the presence or absence of failed requests depends on the live Overseerr instance state, which the test cannot control. The assertion proves the tool endpoint is reachable, authenticated, and returns a parseable response — not that a specific number of failures exists.

---

## 4. Skipped Tests and Why

| Test | Condition for Skip | Reason |
|---|---|---|
| `get_movie_details` | `matrix_id` is empty or `"null"` | `search_media` for "The Matrix" failed to return a result with a `tmdbId`. Typically indicates Overseerr/TMDB connectivity issue. |
| `get_tv_show_details` | `bb_id` is empty or `"null"` | `search_media` for "Breaking Bad" failed to return a result with a `tmdbId`. Same root cause. |
| `request_movie` | Always skipped (not present in script) | Write operation — would create a real media request in Overseerr. Excluded to prevent side effects on the live instance. |
| `request_tv_show` | Always skipped (not present in script) | Same reason as `request_movie`. |

**Design note:** The `request_movie` and `request_tv_show` tools appear in the `tools/list` presence check (Phase 3c) confirming they are registered, but they are never invoked via `call_tool` in Phase 4. The test suite is explicitly read-only for all actual tool executions.

---

## 5. Tools Tested vs. Registered

| Tool | Registered (`tools/list` check) | Invoked in Phase 4 | Invocation Type |
|---|---|---|---|
| `search_media` | Yes | Yes | 3 variants (movie, tv, generic) |
| `get_movie_details` | Yes | Yes (conditional) | 1 call |
| `get_tv_show_details` | Yes | Yes (conditional) | 1 call |
| `request_movie` | Yes | No | Skipped (write operation) |
| `request_tv_show` | Yes | No | Skipped (write operation) |
| `list_failed_requests` | Yes | Yes | 1 call |
| `overseerr_help` | Yes | Yes | 1 call |

---

## 6. Docker Mode Specifics

**Prerequisite:** `docker` must be on `PATH` — the script checks this and exits `2` if missing.

**Lifecycle:**

1. **Trap registration:** `trap 'docker_teardown' EXIT INT TERM` — the container named `overseerr-mcp-ci` is force-removed on any exit, including signals. This ensures cleanup even if the script is interrupted.

2. **Image build:**
   ```bash
   docker build -t overseerr-mcp-test "$REPO_DIR"
   ```
   Builds from the repo root's `Dockerfile` and tags the image `overseerr-mcp-test`. All build output goes to the log file. A build failure causes `exit 2`.

3. **Pre-flight cleanup:** `docker rm -f overseerr-mcp-ci` is run before `docker run` to clear any leftover container from a previous failed run.

4. **Container start:**
   ```bash
   docker run -d \
     --name overseerr-mcp-ci \
     -p <PORT>:<PORT> \
     -e OVERSEERR_URL=<value> \
     -e OVERSEERR_API_KEY=<value> \
     -e OVERSEERR_MCP_TOKEN=<token> \
     -e OVERSEERR_MCP_TRANSPORT=http \
     -e OVERSEERR_MCP_PORT=<PORT> \
     overseerr-mcp-test
   ```
   Key env vars injected:
   - `OVERSEERR_MCP_TRANSPORT=http` — forces HTTP transport mode inside the container.
   - `OVERSEERR_MCP_TOKEN` — sets the Bearer token the MCP server will enforce; matches `$TOKEN` in the test script (default: `ci-integration-token`).
   - `OVERSEERR_MCP_PORT` — the port the server binds to inside the container, mapped to the host via `-p`.

5. **Health polling:**
   ```bash
   for i in $(seq 1 30); do
     curl -sf -H "Accept: application/json, text/event-stream" "${BASE_URL}/health"
   done
   ```
   Polls `GET /health` once per second for up to 30 seconds. If the server does not become healthy within 30 seconds, `docker logs overseerr-mcp-ci` is printed to stderr and the script exits `2`. On success, the elapsed seconds are logged.

6. **HTTP phases:** Once healthy, `run_http_phases` is called — executing all four phases (health, auth, protocol, tools) against the containerized server.

7. **Teardown:** The `EXIT` trap calls `docker rm -f overseerr-mcp-ci`.

---

## 7. Stdio Mode Specifics

**Prerequisites:**
- `npx` must be on `PATH` (requires Node.js). Checked at entry; exits `2` if missing.
- `uvx` must be on `PATH` (requires [uv](https://github.com/astral-sh/uv)). Checked at entry; exits `2` if missing.

**Config generation:** A temporary JSON config file is created at `/tmp/mcporter-stdio-XXXXXX.json` using `mktemp`. It is automatically removed on function return via `trap 'rm -f "$cfg"' RETURN`. The config follows the `mcpServers` schema:

```json
{
  "mcpServers": {
    "overseerr-mcp": {
      "command": "uvx",
      "args": ["--directory", "<REPO_DIR>", "--from", ".", "overseerr-mcp-server"],
      "env": {
        "OVERSEERR_URL": "<value>",
        "OVERSEERR_API_KEY": "<value>",
        "OVERSEERR_MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

Key points:
- `OVERSEERR_MCP_TRANSPORT=stdio` puts the MCP server in stdio mode (no HTTP server, no auth token enforcement).
- `--from .` with `--directory <REPO_DIR>` tells `uvx` to install the package from the local repo directory.
- `mcporter-server` entry point is `overseerr-mcp-server` (as defined in `pyproject.toml`).
- No `OVERSEERR_MCP_TOKEN` is passed — stdio mode does not use Bearer token auth.

**Tests run in stdio mode:**

Stdio mode runs a reduced subset of tests (3 assertions vs. the full HTTP suite of 20+). It does not run all four phases — it runs a purpose-built stdio test suite.

#### Stdio Test 1: `mcporter list`
```bash
npx -y mcporter@latest list --config "$cfg"
```
Checks that the tool listing output contains the string `"search_media"`. This confirms the server spawns correctly via stdio and the tool manifest is discoverable.

- Pass: output contains `search_media`.
- Fail: command fails (non-zero exit) or output does not contain `search_media`.
- Label: `stdio: mcporter list includes search_media`

#### Stdio Test 2: `overseerr_help` via stdio
```bash
npx -y mcporter@latest call \
  --config "$cfg" --server overseerr-mcp \
  --tool overseerr_help --args '{}'
```
Checks that the output contains "overseerr" (case-insensitive).

- Pass: output contains "overseerr" (case-insensitive grep).
- Fail: command fails or output does not mention "overseerr".
- Labels: `stdio: overseerr_help contains 'overseerr'` or `stdio: overseerr_help call failed`

#### Stdio Test 3: `search_media` via stdio
```bash
npx -y mcporter@latest call \
  --config "$cfg" --server overseerr-mcp \
  --tool search_media --args '{"query":"The Matrix","media_type":"movie"}'
```
Checks that the output contains "matrix", "tmdbId", or "The Matrix" (case-insensitive).

- Pass: output matches any of those three strings.
- Fail: command fails or output matches none of them.
- Labels: `stdio: search_media returns Matrix results` or `stdio: search_media call failed`

**Important difference from HTTP mode:** Stdio mode does NOT test health, auth enforcement, MCP protocol handshake, or the full set of tools. It is a smoke test confirming the stdio transport path works end-to-end.

---

## 8. Authentication Tests — Detail

All auth tests are in Phase 2 and apply only to HTTP modes. Stdio mode bypasses auth entirely (no token enforcement in stdio transport).

| Scenario | Request | Expected HTTP Code | Pass Logic |
|---|---|---|---|
| No `Authorization` header | `POST /mcp` without `Authorization` | `401` | `$s == "401"` |
| Invalid Bearer token | `Authorization: Bearer definitely-wrong-token` | `401` | `$s == "401"` |
| Valid Bearer token | `Authorization: Bearer ci-integration-token` | Not `401` or `403` | `$HTTP_STATUS != "401" && $HTTP_STATUS != "403"` |

The valid-token test uses the `mcp_post` helper (which always attaches the current `$TOKEN`). It does not assert a specific success code — just absence of auth failure codes. This makes the test robust to HTTP 202, 200, or 204 responses.

---

## 9. `assert_jq` — Assertion Mechanics

All jq-based assertions in the script go through `assert_jq`:

```bash
assert_jq <label> <jq_filter> <json_string>
```

A test **passes** if and only if:
- `jq -r "$filter"` exits without error (no parse error).
- The output is neither empty string nor the literal string `"null"`.

A test **fails** if:
- `jq` exits non-zero (parse error — the response is not valid JSON).
- The filter output is empty (`""`) or `"null"`.

In verbose mode, the full response body is printed on failure.

Most Phase 4 assertions append `|| true` after `assert_jq`, meaning a jq assertion failure does not abort the tool test's remaining assertions — all assertions in the tool block are always attempted.

---

## 10. `call_tool` — Tool Call Mechanics

```bash
call_tool <label> <tool_name> <args_json>
```

Internally builds:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "<tool_name>",
    "arguments": <args_json>
  }
}
```

Posts to `/mcp`. **Two failure modes are checked:**

1. **HTTP failure:** If `$HTTP_STATUS != "200"`, calls `fail "<label> (HTTP <status>)"` and returns `1`.
2. **MCP application error:** If `.result.isError == true`, extracts `.result.content[0].text` as the error message and calls `fail "<label> (isError=true: <msg>)"`. Returns `1`.

On success, the raw response body is stored in the global `$LAST_TOOL_BODY` for subsequent `assert_jq` calls.

**Response body handling:** The `mcp_post` helper strips SSE framing. Responses prefixed with `data: ` (Server-Sent Events format) have that prefix removed via `sed 's/^data: //'`. This means the script handles both raw JSON and SSE-wrapped JSON transparently.

---

## 11. Summary Output Format

After all phases complete, `print_summary` prints a 65-character `=` separator line followed by:

```
PASS                   <count>    (green)
FAIL                   <count>    (red)
SKIP                   <count>    (yellow)
TOTAL                  <count>
=================================================================
Log: /tmp/overseerr-mcp-test.<timestamp>.log
```

If any failures occurred, the names of all failed tests are listed below the separator:
```
Failed tests:
  • <test label>
  • <test label>
```

The function returns `1` if `FAIL_COUNT > 0`, causing the main function to exit `1`.

**Interpreting results:**

- All `[PASS]` with `0` `[FAIL]` and no unexpected `[SKIP]`: the MCP server is fully functional against the live Overseerr instance.
- `[SKIP]` on `get_movie_details` or `get_tv_show_details`: the upstream search failed; check `OVERSEERR_URL` / `OVERSEERR_API_KEY` and Overseerr connectivity.
- `[FAIL]` on Phase 2 auth tests: the token configuration does not match between the test script and the running server. Verify `OVERSEERR_MCP_TOKEN` matches `$TOKEN` (`ci-integration-token` by default).
- `[FAIL]` on Phase 3 tool presence: the server started but is missing expected tools — likely a code or import error in `overseerr_mcp/server.py`.
- `[FAIL]` on Phase 4 tool calls with `isError=true`: the tool ran but the Overseerr API call failed — check API key permissions and Overseerr instance availability.

---

## 12. What is NOT Tested

The following are explicitly outside scope of this test script:

- **`request_movie` / `request_tv_show` tool invocation** — write operations, excluded to prevent creating real Overseerr media requests.
- **Rate limiting behavior** — no tests for 429 responses.
- **Concurrent requests** — tests are sequential, no concurrency testing.
- **Large result sets** — `list_failed_requests` uses `count=5`, not near-limit values.
- **Invalid argument handling** — no tests for missing required arguments or wrong argument types.
- **Token rotation / expiry** — only static tokens are tested.
- **TLS/HTTPS** — tests run against HTTP by default; HTTPS is not exercised.
- **Multi-season TV requests** — `get_tv_show_details` only checks for a name/title, not season/episode structure.
- **Overseerr request status fields** — `list_failed_requests` validates the response type but does not assert specific field names within individual request objects.
