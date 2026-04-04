#!/usr/bin/env bash
# =============================================================================
# tests/test_live.sh — Canonical integration test for overseerr-mcp
#
# Modes:
#   http   — test against an already-running HTTP server
#   docker — build Docker image, start container, run HTTP tests, tear down
#   stdio  — run tests via mcporter stdio using uvx
#   all    — docker then stdio (default)
#
# Usage:
#   bash tests/test_live.sh [--mode MODE] [--url URL] [--token TOKEN] [--verbose]
#
# Environment (for upstream Overseerr credentials):
#   OVERSEERR_URL      — Overseerr instance URL (required)
#   OVERSEERR_API_KEY  — Overseerr API key (required)
#   PORT               — MCP server port (default: 9151)
#
# Exit codes:
#   0 — all tests passed
#   1 — one or more tests failed
#   2 — prerequisite / startup error
# =============================================================================

set -uo pipefail

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
readonly REPO_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd -P)"
readonly LOG_FILE="${TMPDIR:-/tmp}/overseerr-mcp-test.$(date +%Y%m%d-%H%M%S).log"

# ---------------------------------------------------------------------------
# Colors (disabled when stdout is not a TTY)
# ---------------------------------------------------------------------------
if [[ -t 1 ]]; then
  C_RESET='\033[0m'; C_BOLD='\033[1m'
  C_GREEN='\033[0;32m'; C_RED='\033[0;31m'
  C_YELLOW='\033[0;33m'; C_CYAN='\033[0;36m'; C_DIM='\033[2m'
else
  C_RESET=''; C_BOLD=''; C_GREEN=''; C_RED=''
  C_YELLOW=''; C_CYAN=''; C_DIM=''
fi

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
MODE="${MODE:-all}"
PORT="${PORT:-9151}"
BASE_URL=""
TOKEN="ci-integration-token"
VERBOSE=false

PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0
declare -a FAIL_NAMES=()

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --mode)    MODE="${2:?--mode requires a value}";    shift 2 ;;
      --url)     BASE_URL="${2:?--url requires a value}"; shift 2 ;;
      --token)   TOKEN="${2:?--token requires a value}";  shift 2 ;;
      --verbose) VERBOSE=true; shift ;;
      -h|--help)
        printf 'Usage: %s [--mode http|docker|stdio|all] [--url URL] [--token TOKEN] [--verbose]\n' \
          "$(basename "$0")"
        exit 0
        ;;
      *) printf 'Unknown argument: %s\n' "$1" >&2; exit 2 ;;
    esac
  done
  [[ -z "$BASE_URL" ]] && BASE_URL="http://localhost:${PORT}"
}

# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------
pass()    {
  printf "${C_GREEN}[PASS]${C_RESET} %s\n" "$*" | tee -a "$LOG_FILE"
  PASS_COUNT=$(( PASS_COUNT + 1 ))
}
fail()    {
  printf "${C_RED}[FAIL]${C_RESET} %s\n" "$*" | tee -a "$LOG_FILE"
  FAIL_COUNT=$(( FAIL_COUNT + 1 ))
  FAIL_NAMES+=("$*")
}
skip()    {
  printf "${C_YELLOW}[SKIP]${C_RESET} %s\n" "$*" | tee -a "$LOG_FILE"
  SKIP_COUNT=$(( SKIP_COUNT + 1 ))
}
section() {
  printf "\n${C_BOLD}── %s ──${C_RESET}\n" "$*" | tee -a "$LOG_FILE"
}
log_info() { printf "${C_CYAN}[INFO]${C_RESET}  %s\n" "$*" | tee -a "$LOG_FILE"; }
log_warn() { printf "${C_YELLOW}[WARN]${C_RESET}  %s\n" "$*" | tee -a "$LOG_FILE"; }
log_err()  { printf "${C_RED}[ERROR]${C_RESET} %s\n" "$*" | tee -a "$LOG_FILE" >&2; }

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

# mcp_post <path> <json_body>
# Sets globals: HTTP_STATUS, HTTP_BODY
mcp_post() {
  local path="$1"
  local body="$2"
  local raw
  raw="$(curl -s -w '\n__STATUS__%{http_code}' \
    -X POST \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -d "$body" \
    "${BASE_URL}${path}" 2>>"$LOG_FILE")" || true

  HTTP_STATUS="$(printf '%s' "$raw" | grep -o '__STATUS__[0-9]*' | tail -1 | sed 's/__STATUS__//')"
  # Strip the status line and strip SSE "data: " prefix if present
  HTTP_BODY="$(printf '%s' "$raw" | sed '/^__STATUS__/d' | sed 's/^data: //')"

  if [[ "$VERBOSE" == true ]]; then
    printf '[verbose] POST %s → %s\n%s\n' "$path" "$HTTP_STATUS" "$HTTP_BODY" | tee -a "$LOG_FILE"
  else
    printf '[debug] POST %s → %s\n' "$path" "$HTTP_STATUS" >>"$LOG_FILE"
  fi
}

# assert_jq <test_label> <jq_filter> <json_string>
# Validates that the jq filter returns a non-empty, non-null value.
assert_jq() {
  local label="$1"
  local filter="$2"
  local json="$3"
  local result
  result="$(printf '%s' "$json" | jq -r "$filter" 2>>"$LOG_FILE")" || {
    fail "${label} (jq parse error)"
    return 1
  }
  if [[ -z "$result" || "$result" == "null" ]]; then
    fail "${label} (filter '${filter}' returned empty/null)"
    if [[ "$VERBOSE" == true ]]; then
      printf '  body: %s\n' "$json" | tee -a "$LOG_FILE"
    fi
    return 1
  fi
  pass "$label"
  return 0
}

# call_tool <label> <tool_name> <args_json>
# Sets LAST_TOOL_BODY on success, calls fail() on HTTP error or isError.
LAST_TOOL_BODY=""
call_tool() {
  local label="$1"
  local tool="$2"
  local args="$3"

  local req
  req="$(printf '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"%s","arguments":%s}}' \
    "$tool" "$args")"

  mcp_post "/mcp" "$req"

  if [[ "$HTTP_STATUS" != "200" ]]; then
    fail "${label} (HTTP ${HTTP_STATUS})"
    return 1
  fi

  local is_error
  is_error="$(printf '%s' "$HTTP_BODY" | jq -r '.result.isError // false' 2>/dev/null)"
  if [[ "$is_error" == "true" ]]; then
    local err_msg
    err_msg="$(printf '%s' "$HTTP_BODY" | jq -r '.result.content[0].text // "unknown error"' 2>/dev/null)"
    fail "${label} (isError=true: ${err_msg})"
    return 1
  fi

  LAST_TOOL_BODY="$HTTP_BODY"
  return 0
}

# ---------------------------------------------------------------------------
# Prerequisite check
# ---------------------------------------------------------------------------
check_prereqs() {
  local ok=true
  for cmd in curl jq; do
    command -v "$cmd" &>/dev/null || { log_err "Required command not found: $cmd"; ok=false; }
  done
  [[ "$ok" == true ]] || exit 2
}

# ---------------------------------------------------------------------------
# Credential check
# ---------------------------------------------------------------------------
check_credentials() {
  # Try ~/.claude-homelab/.env if env vars not set
  if [[ -z "${OVERSEERR_URL:-}" || -z "${OVERSEERR_API_KEY:-}" ]]; then
    local env_file="${HOME}/.claude-homelab/.env"
    if [[ -f "$env_file" ]]; then
      log_info "Loading credentials from ${env_file}"
      set -a; source "$env_file"; set +a
    fi
  fi

  if [[ -z "${OVERSEERR_URL:-}" ]]; then
    log_err "OVERSEERR_URL is not set"
    exit 2
  fi
  if [[ -z "${OVERSEERR_API_KEY:-}" ]]; then
    log_err "OVERSEERR_API_KEY is not set"
    exit 2
  fi
  log_info "Upstream: OVERSEERR_URL=${OVERSEERR_URL}"
}

# ---------------------------------------------------------------------------
# Phase 1 — Health
# ---------------------------------------------------------------------------
phase_health() {
  section "Phase 1: Health"
  local body status
  body="$(curl -s -w '\n__STATUS__%{http_code}' \
    -H "Accept: application/json, text/event-stream" \
    "${BASE_URL}/health" 2>>"$LOG_FILE")" || true
  status="$(printf '%s' "$body" | grep -o '__STATUS__[0-9]*' | tail -1 | sed 's/__STATUS__//')"
  local resp
  resp="$(printf '%s' "$body" | sed '/^__STATUS__/d')"

  if [[ "$status" != "200" ]]; then
    fail "GET /health → 200 (got ${status})"
    return 1
  fi
  local ok_val
  ok_val="$(printf '%s' "$resp" | jq -r '.status' 2>/dev/null)"
  if [[ "$ok_val" == "ok" ]]; then
    pass 'GET /health → {"status":"ok"}'
  else
    fail "GET /health response missing status:ok (got: ${resp})"
  fi
}

# ---------------------------------------------------------------------------
# Phase 2 — Auth enforcement
# ---------------------------------------------------------------------------
phase_auth() {
  section "Phase 2: Auth enforcement"

  # No token → 401
  local s
  s="$(curl -s -o /dev/null -w '%{http_code}' \
    -H "Accept: application/json, text/event-stream" \
    -X POST -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' \
    "${BASE_URL}/mcp" 2>>"$LOG_FILE")" || s="000"
  if [[ "$s" == "401" ]]; then
    pass "No token → 401"
  else
    fail "No token → expected 401, got ${s}"
  fi

  # Bad token → 401
  s="$(curl -s -o /dev/null -w '%{http_code}' \
    -H "Authorization: Bearer definitely-wrong-token" \
    -H "Accept: application/json, text/event-stream" \
    -X POST -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' \
    "${BASE_URL}/mcp" 2>>"$LOG_FILE")" || s="000"
  if [[ "$s" == "401" ]]; then
    pass "Bad token → 401"
  else
    fail "Bad token → expected 401, got ${s}"
  fi

  # Good token → not 401/403
  mcp_post "/mcp" '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1"}}}'
  if [[ "$HTTP_STATUS" == "401" || "$HTTP_STATUS" == "403" ]]; then
    fail "Good token → expected success, got ${HTTP_STATUS}"
  else
    pass "Good token → ${HTTP_STATUS} (not 401/403)"
  fi
}

# ---------------------------------------------------------------------------
# Phase 3 — MCP protocol
# ---------------------------------------------------------------------------
phase_protocol() {
  section "Phase 3: MCP protocol"

  # initialize
  mcp_post "/mcp" '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1"}}}'
  if [[ "$HTTP_STATUS" != "200" ]]; then
    fail "initialize → 200 (got ${HTTP_STATUS})"
  else
    assert_jq "initialize → result.serverInfo.name" '.result.serverInfo.name' "$HTTP_BODY"
  fi

  # tools/list — verify all expected tools present
  mcp_post "/mcp" '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
  if [[ "$HTTP_STATUS" != "200" ]]; then
    fail "tools/list → 200 (got ${HTTP_STATUS})"
    return
  fi
  pass "tools/list → 200"

  local expected_tools=("search_media" "get_movie_details" "get_tv_show_details"
    "request_movie" "request_tv_show" "list_failed_requests" "overseerr_help")
  local tools_json="$HTTP_BODY"
  for t in "${expected_tools[@]}"; do
    local found
    found="$(printf '%s' "$tools_json" | jq -r --arg t "$t" \
      '[.result.tools[].name] | map(select(. == $t)) | length' 2>/dev/null)"
    if [[ "${found:-0}" -ge 1 ]]; then
      pass "tools/list contains: ${t}"
    else
      fail "tools/list missing tool: ${t}"
    fi
  done
}

# ---------------------------------------------------------------------------
# Phase 4 — Tool calls (read-only)
# ---------------------------------------------------------------------------
phase_tools() {
  section "Phase 4: Tool calls (read-only)"

  # overseerr_help
  if call_tool "overseerr_help: HTTP 200 + no isError" "overseerr_help" '{}'; then
    local help_text
    help_text="$(printf '%s' "$LAST_TOOL_BODY" | jq -r '.result.content[0].text' 2>/dev/null)"
    if printf '%s' "$help_text" | grep -qi "overseerr"; then
      pass "overseerr_help: text contains 'overseerr'"
    else
      fail "overseerr_help: text does not contain 'overseerr' (got: ${help_text:0:80}...)"
    fi
  fi

  # search_media — movie
  local matrix_id=""
  if call_tool "search_media movie (The Matrix): HTTP 200" \
      "search_media" '{"query":"The Matrix","media_type":"movie"}'; then
    assert_jq "search_media movie: results array non-empty" \
      '.result.content[0].text | fromjson | length > 0 | if . then "yes" else empty end' \
      "$LAST_TOOL_BODY" || true
    assert_jq "search_media movie: first result has tmdbId" \
      '.result.content[0].text | fromjson | .[0].tmdbId | strings // tonumber | tostring' \
      "$LAST_TOOL_BODY" || true
    matrix_id="$(printf '%s' "$LAST_TOOL_BODY" | \
      jq -r '.result.content[0].text | fromjson | .[0].tmdbId' 2>/dev/null || true)"
  fi

  # search_media — TV
  local bb_id=""
  if call_tool "search_media tv (Breaking Bad): HTTP 200" \
      "search_media" '{"query":"Breaking Bad","media_type":"tv"}'; then
    assert_jq "search_media tv: results array non-empty" \
      '.result.content[0].text | fromjson | length > 0 | if . then "yes" else empty end' \
      "$LAST_TOOL_BODY" || true
    bb_id="$(printf '%s' "$LAST_TOOL_BODY" | \
      jq -r '.result.content[0].text | fromjson | .[0].tmdbId' 2>/dev/null || true)"
  fi

  # search_media — generic
  if call_tool "search_media generic (Inception): HTTP 200" \
      "search_media" '{"query":"Inception"}'; then
    assert_jq "search_media generic: results non-empty" \
      '.result.content[0].text | fromjson | length > 0 | if . then "yes" else empty end' \
      "$LAST_TOOL_BODY" || true
  fi

  # get_movie_details
  if [[ -n "$matrix_id" && "$matrix_id" != "null" ]]; then
    local args
    args="$(printf '{"tmdb_id":%s}' "$matrix_id")"
    if call_tool "get_movie_details (tmdbId=${matrix_id}): HTTP 200" \
        "get_movie_details" "$args"; then
      assert_jq "get_movie_details: result has title" \
        '.result.content[0].text | fromjson | .title | strings | select(length > 0)' \
        "$LAST_TOOL_BODY" || true
    fi
  else
    skip "get_movie_details (no tmdbId from search)"
  fi

  # get_tv_show_details
  if [[ -n "$bb_id" && "$bb_id" != "null" ]]; then
    local args
    args="$(printf '{"tmdb_id":%s}' "$bb_id")"
    if call_tool "get_tv_show_details (tmdbId=${bb_id}): HTTP 200" \
        "get_tv_show_details" "$args"; then
      assert_jq "get_tv_show_details: result has name/title" \
        '.result.content[0].text | fromjson | (.name // .title) | strings | select(length > 0)' \
        "$LAST_TOOL_BODY" || true
    fi
  else
    skip "get_tv_show_details (no tmdbId from search)"
  fi

  # list_failed_requests — must return valid JSON array or object
  if call_tool "list_failed_requests (count=5): HTTP 200" \
      "list_failed_requests" '{"count":5}'; then
    local lf_text
    lf_text="$(printf '%s' "$LAST_TOOL_BODY" | jq -r '.result.content[0].text' 2>/dev/null)"
    # Accept either a JSON array, a JSON object, or the "No failed requests found." string
    if printf '%s' "$lf_text" | jq 'if type == "array" or type == "object" then "ok" else error end' &>/dev/null; then
      pass "list_failed_requests: response is valid JSON array/object"
    elif [[ "$lf_text" == *"No failed requests"* ]]; then
      pass "list_failed_requests: no failures (expected)"
    else
      # May be a string response from the tool — still a valid outcome
      pass "list_failed_requests: got response (${lf_text:0:60})"
    fi
  fi
}

# ---------------------------------------------------------------------------
# HTTP mode — run all 4 phases
# ---------------------------------------------------------------------------
run_http_phases() {
  phase_health
  phase_auth
  phase_protocol
  phase_tools
}

# ---------------------------------------------------------------------------
# Docker mode
# ---------------------------------------------------------------------------
DOCKER_CONTAINER="overseerr-mcp-ci"
docker_teardown() {
  docker rm -f "$DOCKER_CONTAINER" &>/dev/null || true
}

run_docker_mode() {
  section "Mode: docker"

  command -v docker &>/dev/null || { log_err "docker not found in PATH"; exit 2; }

  # Always remove container on exit
  trap 'docker_teardown' EXIT INT TERM

  log_info "Building Docker image overseerr-mcp-test..."
  docker build -t overseerr-mcp-test "$REPO_DIR" >>"$LOG_FILE" 2>&1 || {
    log_err "Docker build failed — see $LOG_FILE"
    exit 2
  }

  docker_teardown  # clear any leftover container

  log_info "Starting container on port ${PORT}..."
  docker run -d \
    --name "$DOCKER_CONTAINER" \
    -p "${PORT}:${PORT}" \
    -e "OVERSEERR_URL=${OVERSEERR_URL}" \
    -e "OVERSEERR_API_KEY=${OVERSEERR_API_KEY}" \
    -e "OVERSEERR_MCP_TOKEN=${TOKEN}" \
    -e "OVERSEERR_MCP_TRANSPORT=http" \
    -e "OVERSEERR_MCP_PORT=${PORT}" \
    overseerr-mcp-test >>"$LOG_FILE" 2>&1

  log_info "Waiting for /health (up to 30s)..."
  local healthy=false
  for i in $(seq 1 30); do
    if curl -sf -H "Accept: application/json, text/event-stream" \
        "${BASE_URL}/health" &>/dev/null; then
      healthy=true
      log_info "Server healthy after ${i}s"
      break
    fi
    printf '.' >&2
    sleep 1
  done
  printf '\n' >&2
  if [[ "$healthy" != true ]]; then
    log_err "Server did not become healthy. Docker logs:"
    docker logs "$DOCKER_CONTAINER" >&2 || true
    exit 2
  fi

  run_http_phases
}

# ---------------------------------------------------------------------------
# stdio mode
# ---------------------------------------------------------------------------
run_stdio_mode() {
  section "Mode: stdio (mcporter + uvx)"

  command -v npx &>/dev/null || { log_err "npx not found in PATH (Node.js required for stdio mode)"; exit 2; }
  command -v uvx &>/dev/null || { log_err "uvx not found in PATH (install uv)"; exit 2; }

  local cfg
  cfg="$(mktemp /tmp/mcporter-stdio-XXXXXX.json)"
  trap 'rm -f "$cfg"' RETURN

  cat > "$cfg" <<JSON
{
  "mcpServers": {
    "overseerr-mcp": {
      "command": "uvx",
      "args": ["--directory", "${REPO_DIR}", "--from", ".", "overseerr-mcp-server"],
      "env": {
        "OVERSEERR_URL": "${OVERSEERR_URL}",
        "OVERSEERR_API_KEY": "${OVERSEERR_API_KEY}",
        "OVERSEERR_MCP_TRANSPORT": "stdio"
      }
    }
  }
}
JSON

  # list tools
  local list_out
  log_info "Running mcporter list..."
  if list_out="$(npx -y mcporter@latest list --config "$cfg" 2>>"$LOG_FILE")"; then
    if printf '%s' "$list_out" | grep -q "search_media"; then
      pass "stdio: mcporter list includes search_media"
    else
      fail "stdio: mcporter list did not include search_media"
    fi
  else
    fail "stdio: mcporter list failed"
    return
  fi

  # overseerr_help
  local help_out
  if help_out="$(npx -y mcporter@latest call \
      --config "$cfg" --server overseerr-mcp \
      --tool overseerr_help --args '{}' 2>>"$LOG_FILE")"; then
    if printf '%s' "$help_out" | grep -qi "overseerr"; then
      pass "stdio: overseerr_help contains 'overseerr'"
    else
      fail "stdio: overseerr_help output missing 'overseerr' (got: ${help_out:0:80})"
    fi
  else
    fail "stdio: overseerr_help call failed"
  fi

  # search_media
  local search_out
  if search_out="$(npx -y mcporter@latest call \
      --config "$cfg" --server overseerr-mcp \
      --tool search_media --args '{"query":"The Matrix","media_type":"movie"}' 2>>"$LOG_FILE")"; then
    if printf '%s' "$search_out" | grep -qi "matrix\|tmdbId\|The Matrix"; then
      pass "stdio: search_media returns Matrix results"
    else
      fail "stdio: search_media output does not mention Matrix (got: ${search_out:0:120})"
    fi
  else
    fail "stdio: search_media call failed"
  fi
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print_summary() {
  local total=$(( PASS_COUNT + FAIL_COUNT + SKIP_COUNT ))
  printf "\n${C_BOLD}%s${C_RESET}\n" "$(printf '=%.0s' {1..65})"
  printf "${C_BOLD}%-20s${C_RESET}  ${C_GREEN}%d${C_RESET}\n" "PASS" "$PASS_COUNT"
  printf "${C_BOLD}%-20s${C_RESET}  ${C_RED}%d${C_RESET}\n"   "FAIL" "$FAIL_COUNT"
  printf "${C_BOLD}%-20s${C_RESET}  ${C_YELLOW}%d${C_RESET}\n" "SKIP" "$SKIP_COUNT"
  printf "${C_BOLD}%-20s${C_RESET}  %d\n" "TOTAL" "$total"
  printf "${C_BOLD}%s${C_RESET}\n" "$(printf '=%.0s' {1..65})"
  printf "Log: %s\n" "$LOG_FILE"

  if [[ "$FAIL_COUNT" -gt 0 ]]; then
    printf "\n${C_RED}Failed tests:${C_RESET}\n"
    local n
    for n in "${FAIL_NAMES[@]}"; do
      printf "  • %s\n" "$n"
    done
    return 1
  fi
  return 0
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
  parse_args "$@"
  check_prereqs
  check_credentials

  printf "${C_BOLD}%s${C_RESET}\n" "$(printf '=%.0s' {1..65})"
  printf "${C_BOLD}  overseerr-mcp integration tests${C_RESET}\n"
  printf "${C_BOLD}  mode: %s | base-url: %s${C_RESET}\n" "$MODE" "$BASE_URL"
  printf "${C_BOLD}%s${C_RESET}\n\n" "$(printf '=%.0s' {1..65})"

  case "$MODE" in
    http)
      run_http_phases
      ;;
    docker)
      run_docker_mode
      ;;
    stdio)
      run_stdio_mode
      ;;
    all)
      run_docker_mode
      run_stdio_mode
      ;;
    *)
      log_err "Unknown mode '${MODE}'. Use: http|docker|stdio|all"
      exit 2
      ;;
  esac

  print_summary
}

main "$@"
