# Technology Choices — overseerr-mcp

## Language

**Python 3.11+** (runtime), **3.12** (ruff target), **3.10** (minimum in pyproject.toml)

Rationale: FastMCP is a Python-first framework. The Overseerr API is straightforward REST that maps well to async Python.

## Core dependencies

| Package | Version | Purpose |
| --- | --- | --- |
| `fastmcp` | >=2.3.4 | MCP server framework — tool registration, transport, JSON-RPC |
| `httpx` | >=0.28.1 | Async HTTP client for Overseerr API calls |
| `python-dotenv` | >=1.1.0 | Load `.env` file at startup |

### FastMCP

Provides:
- `@mcp.tool()` decorator for tool registration
- `mcp.http_app()` for ASGI app creation
- `mcp.run()` for stdio/SSE transport
- `@mcp.custom_route()` for health endpoint
- `Context` for accessing server state in tools
- Lifespan management via async context manager

### httpx

Used in `OverseerrApiClient` for:
- Async HTTP requests to Overseerr REST API
- `X-Api-Key` header authentication
- Automatic JSON serialization/deserialization
- HTTP status error handling

### Starlette

Implicit dependency via FastMCP. Used for:
- `BaseHTTPMiddleware` (bearer auth)
- `Request`, `Response`, `JSONResponse` types
- ASGI application

### Uvicorn

Implicit dependency. ASGI server for HTTP transport.

## Development dependencies

| Package | Version | Purpose |
| --- | --- | --- |
| `ruff` | >=0.9 | Fast Python linter and formatter |
| `ty` | >=0.0.1a3 | Type checker (Astral) |
| `pytest` | >=8.0 | Test framework |
| `pytest-asyncio` | >=0.23 | Async test support |

## Build system

- **Build backend:** hatchling
- **Package manager:** uv
- **Lock file:** `uv.lock` (frozen installs)
- **Entry point:** `overseerr-mcp-server = "overseerr_mcp.server:main"`

## Container

- **Base image:** `python:3.11-slim` (multi-stage)
- **uv version:** `0.10.10` (from `ghcr.io/astral-sh/uv`)
- **Runtime user:** `mcpuser` (UID 1000)
- **Health tool:** `wget` (installed in runtime stage)

## Task runner

**Justfile** — 17 recipes covering dev, docker, verification, setup, and publishing.

## CI

**GitHub Actions** — 3 workflows:
- `ci.yml`: lint, typecheck, test, security, integration
- `docker-publish.yml`: multi-platform Docker build, GHCR push, Trivy scan
- `publish-pypi.yml`: PyPI publish, GitHub Release, MCP Registry publish
