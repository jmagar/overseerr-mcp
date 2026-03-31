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
    bash scripts/lint-plugin.sh

validate-skills:
    echo "ok"

clean:
    rm -rf .cache/ dist/
