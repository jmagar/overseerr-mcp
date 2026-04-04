#!/usr/bin/env bash
# tests/ci-test-tools.sh — HTTP-mode integration smoke-test for CI
#
# Runs mcporter tool calls against a running overseerr-mcp HTTP server.
# Used by the mcp-integration CI job for Docker HTTP and uvx HTTP modes.
#
# Usage:
#   ./tests/ci-test-tools.sh --url http://localhost:9151 --token <bearer-token>
#
# Exit codes:
#   0 — all tests passed
#   1 — one or more tests failed
#   2 — argument error

set -uo pipefail

URL=""
TOKEN=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --url)   URL="$2";   shift 2 ;;
    --token) TOKEN="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 --url <url> --token <bearer-token>"
      exit 0
      ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$URL" || -z "$TOKEN" ]]; then
  echo "ERROR: --url and --token are required" >&2
  exit 2
fi

# Write a temp mcporter config pointing at the running HTTP server
CFG=$(mktemp /tmp/mcporter-http-XXXXXX.json)
trap 'rm -f "$CFG"' EXIT

cat > "$CFG" <<JSON
{
  "mcpServers": {
    "overseerr-mcp": {
      "url": "${URL}",
      "headers": {
        "Authorization": "Bearer ${TOKEN}",
        "Accept": "application/json, text/event-stream"
      }
    }
  }
}
JSON

PASS=0
FAIL=0
FAILS=()

run() {
  local label="$1"; shift
  echo -n "  $label ... "
  local out
  if out=$(npx -y mcporter@latest call \
      --config "$CFG" \
      --server overseerr-mcp \
      "$@" 2>&1); then
    echo "PASS"
    PASS=$((PASS + 1))
  else
    echo "FAIL"
    echo "    output: $out"
    FAIL=$((FAIL + 1))
    FAILS+=("$label")
  fi
}

echo ""
echo "── overseerr-mcp HTTP integration tests ($URL) ──"

run "list tools"         --tool-list
run "help"               --tool overseerr_help --args '{}'
run "search movie"       --tool search_media   --args '{"query":"The Matrix","media_type":"movie"}'
run "search tv"          --tool search_media   --args '{"query":"Breaking Bad","media_type":"tv"}'
run "list failed reqs"   --tool list_failed_requests --args '{"count":5}'

echo ""
echo "Results: $PASS passed, $FAIL failed"

if [[ $FAIL -gt 0 ]]; then
  echo "Failed:"
  for f in "${FAILS[@]}"; do echo "  • $f"; done
  exit 1
fi
exit 0
