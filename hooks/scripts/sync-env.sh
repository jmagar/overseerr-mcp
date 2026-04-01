#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${CLAUDE_PLUGIN_ROOT}/.env"
BACKUP_DIR="${CLAUDE_PLUGIN_ROOT}/backups"
mkdir -p "$BACKUP_DIR"

declare -A MANAGED=(
  [OVERSEERR_URL]="${CLAUDE_PLUGIN_OPTION_OVERSEERR_URL:-}"
  [OVERSEERR_API_KEY]="${CLAUDE_PLUGIN_OPTION_OVERSEERR_API_KEY:-}"
  [OVERSEERR_MCP_URL]="${CLAUDE_PLUGIN_OPTION_OVERSEERR_MCP_URL:-}"
  [OVERSEERR_MCP_TOKEN]="${CLAUDE_PLUGIN_OPTION_OVERSEERR_MCP_TOKEN:-}"
)

touch "$ENV_FILE"

(
  flock -x 200

  if [ -s "$ENV_FILE" ]; then
    cp "$ENV_FILE" "${BACKUP_DIR}/.env.bak.$(date +%s)"
  fi

  for key in "${!MANAGED[@]}"; do
    value="${MANAGED[$key]}"
    [ -z "$value" ] && continue
    if grep -q "^${key}=" "$ENV_FILE" 2>/dev/null; then
      awk -v k="$key" -v v="$value" \
        '$0 ~ "^" k "=" {sub(/=.*/, "=" v)} {print}' \
        "$ENV_FILE" > "${ENV_FILE}.tmp" && mv "${ENV_FILE}.tmp" "$ENV_FILE"
    else
      echo "${key}=${value}" >> "$ENV_FILE"
    fi
  done

  chmod 600 "$ENV_FILE"

  mapfile -t baks < <(ls -t "${BACKUP_DIR}"/.env.bak.* 2>/dev/null)
  for bak in "${baks[@]}"; do
    chmod 600 "$bak"
  done
  for bak in "${baks[@]:3}"; do
    rm -f "$bak"
  done

) 200>"${ENV_FILE}.lock"
