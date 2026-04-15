# Justfile is an entrypoint only — no business logic here.
# All non-trivial logic belongs in scripts under bin/ or tests/.
# Recipes should shell out to those scripts, not implement logic inline.

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
    curl -sf http://${OVERSEERR_MCP_URL:-localhost}:${OVERSEERR_MCP_PORT:-9151}/health | jq .

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

validate-skills:
    npx skills-ref validate skills/

clean:
    rm -rf .cache/ dist/

publish bump="patch":
    bash bin/publish {{bump}}
