# Architecture — overseerr-mcp

## Overview

```
MCP Client (Claude, Codex, Gemini, etc.)
    │
    │  MCP JSON-RPC (HTTP/stdio/SSE)
    │  Authorization: Bearer <token>
    ▼
┌──────────────────────────────────┐
│  overseerr-mcp                   │
│  ┌────────────────────────────┐  │
│  │  BearerAuthMiddleware      │  │  ← Starlette middleware
│  │  (skips /health)           │  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │  FastMCP Server            │  │  ← MCP JSON-RPC dispatch
│  │  7 tools registered        │  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │  OverseerrApiClient        │  │  ← httpx async client
│  │  X-Api-Key auth            │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
    │
    │  REST API (HTTPS)
    │  X-Api-Key: <key>
    ▼
┌──────────────────────────────────┐
│  Overseerr                       │
│  /api/v1/search                  │
│  /api/v1/movie/{id}              │
│  /api/v1/tv/{id}                 │
│  /api/v1/request                 │
└──────────────────────────────────┘
    │
    ▼
Radarr / Sonarr → Download → Plex / Jellyfin
```

## Components

### FastMCP Server (server.py)

- Creates `FastMCP` instance with lifespan management
- Registers 7 tool functions via `@mcp.tool()` decorators
- Registers `/health` custom route
- Dispatches by transport mode in `main()`

### BearerAuthMiddleware (server.py)

- Starlette `BaseHTTPMiddleware`
- Checks `Authorization: Bearer <token>` on all requests except `/health`
- Uses `hmac.compare_digest` for timing-safe comparison
- Returns 401 JSON response on failure

### OverseerrApiClient (client.py)

- Wraps `httpx.AsyncClient`
- Appends `/api/v1` to base URL
- Sets `X-Api-Key` header
- URL-encodes string parameters
- Returns structured data on success, error strings on failure

### Lifespan

Async context manager that:
1. Attaches `overseerr_client` to the FastMCP app on startup
2. Closes the httpx client on shutdown

## Data flow

1. Client sends MCP JSON-RPC request to `/mcp`
2. Middleware validates bearer token
3. FastMCP dispatches to registered tool function
4. Tool retrieves `OverseerrApiClient` from context
5. Client makes async HTTP request to Overseerr `/api/v1/*`
6. Response is validated, transformed, and returned
7. FastMCP serializes response as MCP JSON-RPC

## Error handling

Errors are handled at multiple layers:
- **Transport layer:** Invalid JSON-RPC → FastMCP error response
- **Auth layer:** Missing/bad token → 401 JSON response
- **Tool layer:** Client unavailable → error string
- **API client layer:** HTTP errors, connection errors → error string
- **Response layer:** Unexpected data structure → error string with warning log
