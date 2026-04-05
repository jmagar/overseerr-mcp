dev:
    uv run python -m overseerr_mcp

lint:
    uv run ruff check .

fmt:
    uv run ruff format .

typecheck:
    uv run ty check

test:
    uv run pytest .cache/pytest

build:
    docker build -t overseerr-mcp .

up:
    docker compose up -d

down:
    docker compose down

restart:
    docker compose restart

logs:
    docker compose logs -f

health:
    curl -sf http://localhost:8083/health | jq .

test-live:
    bash tests/test_live.sh

setup:
    cp .env.example .env

gen-token:
    openssl rand -hex 32

check-contract:
    echo "ok"

validate-skills:
    echo "ok"

# Generate a standalone CLI for this server (requires running server)
generate-cli:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "⚠  Server must be running on port 8083 (run 'just dev' first)"
    echo "⚠  Generated CLI embeds your OAuth token — do not commit or share"
    mkdir -p dist dist/.cache
    current_hash=$(timeout 10 curl -sf \
      -H "Authorization: Bearer $MCP_TOKEN" \
      -H "Accept: application/json, text/event-stream" \
      http://localhost:8083/mcp/tools/list 2>/dev/null | sha256sum | cut -d' ' -f1 || echo "nohash")
    cache_file="dist/.cache/overseerr-mcp-cli.schema_hash"
    if [[ -f "$cache_file" ]] && [[ "$(cat "$cache_file")" == "$current_hash" ]] && [[ -f "dist/overseerr-mcp-cli" ]]; then
      echo "SKIP: overseerr-mcp tool schema unchanged — use existing dist/overseerr-mcp-cli"
      exit 0
    fi
    timeout 30 mcporter generate-cli \
      --command http://localhost:8083/mcp \
      --header "Authorization: Bearer $MCP_TOKEN" \
      --name overseerr-mcp-cli \
      --output dist/overseerr-mcp-cli
    printf '%s' "$current_hash" > "$cache_file"
    echo "✓ Generated dist/overseerr-mcp-cli (requires bun at runtime)"

clean:
    rm -rf .cache/ dist/

# Publish: bump version, tag, push (triggers PyPI + Docker publish)
publish bump="patch":
    #!/usr/bin/env bash
    set -euo pipefail
    [ "$(git branch --show-current)" = "main" ] || { echo "Switch to main first"; exit 1; }
    [ -z "$(git status --porcelain)" ] || { echo "Commit or stash changes first"; exit 1; }
    git pull origin main
    CURRENT=$(grep -m1 "^version" pyproject.toml | sed "s/.*\"\(.*\)\".*/\1/")
    IFS="." read -r major minor patch <<< "$CURRENT"
    case "{{bump}}" in
      major) major=$((major+1)); minor=0; patch=0 ;;
      minor) minor=$((minor+1)); patch=0 ;;
      patch) patch=$((patch+1)) ;;
      *) echo "Usage: just publish [major|minor|patch]"; exit 1 ;;
    esac
    NEW="${major}.${minor}.${patch}"
    echo "Version: ${CURRENT} → ${NEW}"
    sed -i "s/^version = \"${CURRENT}\"/version = \"${NEW}\"/" pyproject.toml
    for f in .claude-plugin/plugin.json .codex-plugin/plugin.json gemini-extension.json; do
      [ -f "$f" ] && python3 -c "import json; d=json.load(open(\"$f\")); d[\"version\"]=\"${NEW}\"; json.dump(d,open(\"$f\",\"w\"),indent=2); open(\"$f\",\"a\").write(\"
\")"
    done
    git add -A && git commit -m "release: v${NEW}" && git tag "v${NEW}" && git push origin main --tags
    echo "Tagged v${NEW} — publish workflow will run automatically"

