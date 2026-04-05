# Justfile Recipes — overseerr-mcp

## Development

| Recipe | Command | Description |
| --- | --- | --- |
| `dev` | `uv run python -m overseerr_mcp` | Run server locally |
| `lint` | `uv run ruff check .` | Ruff lint check |
| `fmt` | `uv run ruff format .` | Ruff auto-format |
| `typecheck` | `uv run ty check` | Type check with ty |
| `test` | `uv run pytest .cache/pytest` | Run pytest |

## Docker

| Recipe | Command | Description |
| --- | --- | --- |
| `build` | `docker build -t overseerr-mcp .` | Build Docker image |
| `up` | `docker compose up -d` | Start containers |
| `down` | `docker compose down` | Stop containers |
| `restart` | `docker compose restart` | Restart containers |
| `logs` | `docker compose logs -f` | Tail container logs |

## Verification

| Recipe | Command | Description |
| --- | --- | --- |
| `health` | `curl -sf http://localhost:8083/health \| jq .` | Check health endpoint |
| `test-live` | `bash tests/test_live.sh` | Run integration tests |
| `check-contract` | `bash scripts/lint-plugin.sh` | Plugin contract lint |
| `validate-skills` | `echo "ok"` | Skill validation (placeholder) |

## Setup

| Recipe | Command | Description |
| --- | --- | --- |
| `setup` | `cp .env.example .env` | Create .env from template |
| `gen-token` | `openssl rand -hex 32` | Generate bearer token |
| `clean` | `rm -rf .cache/ dist/` | Remove build artifacts |

## Publishing

| Recipe | Command | Description |
| --- | --- | --- |
| `publish [bump]` | (script) | Bump version, tag, push (triggers CI publish) |

The `publish` recipe accepts `major`, `minor`, or `patch` (default: `patch`). It:
1. Verifies clean main branch
2. Reads current version from `pyproject.toml`
3. Computes new version
4. Updates all version-bearing files
5. Commits, tags, and pushes
