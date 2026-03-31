#!/usr/bin/env bash
set -euo pipefail

# Validate required env vars before starting server
if [ -z "${OVERSEERR_MCP_TOKEN:-}" ] && [ "${OVERSEERR_MCP_NO_AUTH:-false}" != "true" ]; then
    echo "CRITICAL: OVERSEERR_MCP_TOKEN is not set." >&2
    echo "Set OVERSEERR_MCP_TOKEN to a secure random token, or set OVERSEERR_MCP_NO_AUTH=true" >&2
    echo "to disable auth (only appropriate when secured at the network/proxy level)." >&2
    echo "" >&2
    echo "Generate a token with: openssl rand -hex 32" >&2
    exit 1
fi

exec python3 -m overseerr_mcp.server
