#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load .env if present (without exporting — just pick up variables)
if [ -f "$PROJECT_ROOT/.env" ]; then
    # shellcheck disable=SC1091
    set -a; source "$PROJECT_ROOT/.env"; set +a
fi

PUID="${PUID:-1000}"
PGID="${PGID:-1000}"
APPDATA_PATH="${APPDATA_PATH:-$PROJECT_ROOT/data}"

LOGS_DIR="$APPDATA_PATH/overseerr-mcp/logs"

mkdir -p "$LOGS_DIR"
chown -R "$PUID:$PGID" "$APPDATA_PATH/overseerr-mcp"

echo "Data directories ready (uid=$PUID gid=$PGID): $APPDATA_PATH/overseerr-mcp"
