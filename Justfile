dev:
    uv run python -m overseerr_mcp

lint:
    uv run ruff check .

fmt:
    uv run ruff format .

typecheck:
    uv run ty check

test:
    uv run pytest

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
    curl -sf http://localhost:${OVERSEERR_MCP_PORT:-9151}/health | jq .

test-live mode="stdio":
    bash tests/test_live.sh {{mode}}

test-live-both:
    bash tests/test_live.sh both

setup:
    mkdir -p ~/.config/overseerr-mcp
    cp -n .env.example ~/.config/overseerr-mcp/.env
    @echo "Edit ~/.config/overseerr-mcp/.env with your credentials"

gen-token:
    openssl rand -hex 32

check-contract:
    echo "ok"

validate-skills:
    echo "ok"

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
      [ -f "$f" ] && python3 -c 'import json,sys; f,v=sys.argv[1:]; d=json.load(open(f)); d["version"]=v; json.dump(d,open(f,"w"),indent=2); open(f,"a").write("\n")' "$f" "${NEW}"
    done
    git add -A && git commit -m "release: v${NEW}" && git tag "v${NEW}" && git push origin main --tags
    echo "Tagged v${NEW} — publish workflow will run automatically"

