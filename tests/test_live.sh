#!/usr/bin/env bash
set -euo pipefail
TOKEN="${OVERSEERR_MCP_TOKEN:?OVERSEERR_MCP_TOKEN must be set}"
BASE_URL="${OVERSEERR_MCP_URL:-http://localhost:8083}"

# Test unauthenticated rejection
status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/mcp")
[ "$status" = "401" ] || { echo "FAIL: expected 401, got $status"; exit 1; }

# Test bad token rejection
status=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer bad-token" "$BASE_URL/mcp")
[ "$status" = "401" ] || { echo "FAIL: expected 401, got $status"; exit 1; }

# Test health
timeout 30 curl -sf -H "Authorization: Bearer $TOKEN" "$BASE_URL/health" | jq .

echo "All live tests passed."
