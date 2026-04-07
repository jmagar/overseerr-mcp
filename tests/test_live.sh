#!/usr/bin/env bash
# tests/test_live.sh — live tests for overseerr-mcp
#
# Usage: bash tests/test_live.sh [stdio|http|both]
#   stdio  (default) — starts server via fastmcp --command, calls tools via fastmcp call
#   http             — auth rejection + health via curl; tool calls via fastmcp call <url>
#   both             — runs both suites
#
# Environment (both modes):
#   OVERSEERR_URL       required
#   OVERSEERR_API_KEY   required
#
# Environment (http auth tests only):
#   OVERSEERR_MCP_TOKEN required
#   OVERSEERR_MCP_URL   optional, default http://localhost:9151
#
# Test IDs (not in library — safe to request and auto-delete):
#   Movie: 7512  — Idiocracy (2006)
#   TV:    43199 — Danger 5

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-stdio}"

MOVIE_ID=7512    # Idiocracy (2006) — verified not in library
TV_ID=43199      # Danger 5         — verified not in library

# stdio command — env prefix overrides .env so fastmcp always gets stdio transport
STDIO_CMD="env OVERSEERR_MCP_TRANSPORT=stdio OVERSEERR_LOG_LEVEL=WARNING uv run --project ${ROOT_DIR} overseerr-mcp-server"

# ── helpers ────────────────────────────────────────────────────────────────────

pass() { printf '  PASS: %s\n' "$*"; }
fail() { printf '  FAIL: %s\n' "$*" >&2; exit 1; }

# Call a tool via fastmcp stdio and return content[0].text (the tool result).
# Usage: fcall_stdio <tool> <json-args>
fcall_stdio() {
    local tool="$1" args="$2"
    fastmcp call \
        --command "$STDIO_CMD" \
        --target  "$tool" \
        --input-json "$args" \
        --json 2>/dev/null \
    | jq -r '.content[0].text'
}

# Call a tool via fastmcp HTTP and return content[0].text.
# Usage: fcall_http <tool> <json-args>
fcall_http() {
    local tool="$1" args="$2"
    fastmcp call \
        "${HTTP_BASE}/mcp" \
        "$tool" \
        --input-json "$args" \
        --auth "$HTTP_TOKEN" \
        --json 2>/dev/null \
    | jq -r '.content[0].text'
}

# Delete an Overseerr request by ID (cleanup after request tests).
delete_request() {
    local req_id="$1"
    curl -sf -X DELETE \
        -H "X-Api-Key: ${OVERSEERR_API_KEY}" \
        "${OVERSEERR_URL}/api/v1/request/${req_id}" >/dev/null \
        || printf '  WARN: could not delete request %s\n' "$req_id" >&2
}

# ── tool tests (called with a provided fcall function) ────────────────────────

run_tool_tests() {
    local fcall="$1"   # name of function to use: fcall_stdio or fcall_http

    # overseerr_help — header + tool entries present
    result=$("$fcall" overseerr_help '{}')
    [[ "$result" == *"Overseerr MCP Server"* && "$result" == *"search_media"* && "$result" == *"request_movie"* ]] \
        || fail "overseerr_help: unexpected content"
    pass "overseerr_help"

    # search_media — first result is Inception (tmdbId=27205, movie, 2010)
    result=$("$fcall" search_media '{"query":"Inception","media_type":"movie"}')
    printf '%s\n' "$result" | jq -e '
        type == "array" and
        .[0].tmdbId    == 27205 and
        .[0].title     == "Inception" and
        .[0].mediaType == "movie" and
        .[0].year      == "2010"
    ' >/dev/null || fail "search_media: unexpected result: $(printf '%s\n' "$result" | jq '.[0]')"
    pass "search_media"

    # get_movie_details — Idiocracy
    result=$("$fcall" get_movie_details "{\"tmdb_id\":$MOVIE_ID}")
    printf '%s\n' "$result" | jq -e "
        .id    == $MOVIE_ID and
        .title == \"Idiocracy\" and
        (.releaseDate | startswith(\"2006\"))
    " >/dev/null || fail "get_movie_details: unexpected result: $result"
    pass "get_movie_details"

    # get_tv_show_details — Danger 5
    result=$("$fcall" get_tv_show_details "{\"tmdb_id\":$TV_ID}")
    printf '%s\n' "$result" | jq -e "
        .id             == $TV_ID and
        .name           == \"Danger 5\" and
        .numberOfSeasons == 2 and
        (.firstAirDate  | startswith(\"2012\"))
    " >/dev/null || fail "get_tv_show_details: unexpected result: $result"
    pass "get_tv_show_details"

    # list_failed_requests — array where every item has expected fields, or empty message
    result=$("$fcall" list_failed_requests '{"count":5}')
    if printf '%s\n' "$result" | jq -e 'type == "array"' >/dev/null 2>&1; then
        printf '%s\n' "$result" | jq -e '
            all(.[]; has("requestId") and has("status") and has("type") and has("tmdbId"))
        ' >/dev/null || fail "list_failed_requests: items missing expected fields: $result"
    else
        [[ "$result" == *"No failed requests"* ]] \
            || fail "list_failed_requests: unexpected response: $result"
    fi
    pass "list_failed_requests"

    # request_movie — pending request for correct movie, then delete
    result=$("$fcall" request_movie "{\"tmdb_id\":$MOVIE_ID}")
    printf '%s\n' "$result" | jq -e "
        .status             == 2 and
        .media.tmdbId       == $MOVIE_ID and
        .media.mediaType    == \"movie\"
    " >/dev/null || fail "request_movie: unexpected result: $result"
    req_id=$(printf '%s\n' "$result" | jq -r '.id')
    delete_request "$req_id"
    pass "request_movie (request $req_id created and deleted)"

    # request_tv_show — pending request for correct show, then delete
    result=$("$fcall" request_tv_show "{\"tmdb_id\":$TV_ID}")
    printf '%s\n' "$result" | jq -e "
        .status          == 2 and
        .media.tmdbId    == $TV_ID
    " >/dev/null || fail "request_tv_show: unexpected result: $result"
    req_id=$(printf '%s\n' "$result" | jq -r '.id')
    delete_request "$req_id"
    pass "request_tv_show (request $req_id created and deleted)"
}

# ── stdio suite ────────────────────────────────────────────────────────────────

test_stdio() {
    echo "=== stdio mode ==="
    : "${OVERSEERR_URL:?OVERSEERR_URL must be set}"
    : "${OVERSEERR_API_KEY:?OVERSEERR_API_KEY must be set}"

    run_tool_tests fcall_stdio

    echo "=== stdio: all tests passed ==="
}

# ── HTTP suite ─────────────────────────────────────────────────────────────────

test_http() {
    echo "=== http mode ==="
    : "${OVERSEERR_URL:?OVERSEERR_URL must be set}"
    : "${OVERSEERR_API_KEY:?OVERSEERR_API_KEY must be set}"

    HTTP_TOKEN="${OVERSEERR_MCP_TOKEN:?OVERSEERR_MCP_TOKEN must be set for http mode}"
    HTTP_BASE="${OVERSEERR_MCP_URL:-http://localhost:9151}"
    export HTTP_TOKEN HTTP_BASE

    # 401 — no token
    status=$(curl -s -o /dev/null -w "%{http_code}" "$HTTP_BASE/mcp")
    [ "$status" = "401" ] || fail "expected 401 without token, got $status"
    pass "unauthenticated request rejected (401)"

    # 401 — bad token
    status=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer bad-token" "$HTTP_BASE/mcp")
    [ "$status" = "401" ] || fail "expected 401 with bad token, got $status"
    pass "bad token rejected (401)"

    # Health (unauthenticated)
    health=$(timeout 30 curl -sf "$HTTP_BASE/health")
    printf '%s\n' "$health" | jq -e '.status == "ok"' >/dev/null \
        || fail "health did not return {status:ok}: $health"
    pass "health endpoint"

    run_tool_tests fcall_http

    echo "=== http: all tests passed ==="
}

# ── dispatch ───────────────────────────────────────────────────────────────────

case "$MODE" in
    stdio) test_stdio ;;
    http)  test_http ;;
    both)  test_stdio; test_http ;;
    *)
        printf 'Usage: %s [stdio|http|both]\n' "$(basename "$0")" >&2
        printf '  stdio  (default) — fastmcp call --command via uv run\n' >&2
        printf '  http             — curl auth/health + fastmcp call <url>\n' >&2
        printf '  both             — run both suites\n' >&2
        exit 1
        ;;
esac
