# HTTP Transport Details — overseerr-mcp

## ASGI application

The HTTP server is a Starlette ASGI app created by FastMCP:

```python
app = mcp.http_app(path="/mcp")
```

This serves the MCP JSON-RPC endpoint at `/mcp`.

## Middleware stack

When bearer auth is enabled (default), the middleware stack is:

1. **BearerAuthMiddleware** — checks `Authorization: Bearer <token>` on all requests except `/health`
2. **FastMCP internal middleware** — JSON-RPC dispatch

## Custom routes

| Route | Method | Auth | Handler |
| --- | --- | --- | --- |
| `/health` | GET | none | Returns `{"status": "ok"}` |
| `/mcp` | POST | Bearer | MCP JSON-RPC |

The health endpoint is registered via `@mcp.custom_route("/health", methods=["GET"])`.

## Uvicorn

The HTTP server is run with Uvicorn:

```python
uvicorn.run(app, host=OVERSEERR_MCP_HOST, port=OVERSEERR_MCP_PORT)
```

Uvicorn is imported lazily — only when the transport is `http` or `streamable-http`.

## Request flow

```
Client → HTTP POST /mcp
       → BearerAuthMiddleware (check token)
       → FastMCP JSON-RPC dispatcher
       → Tool function (e.g., search_media)
       → OverseerrApiClient (httpx → Overseerr API)
       ��� Response
```

## Headers

### Required request headers

```
Content-Type: application/json
Authorization: Bearer <token>
```

### Recommended

```
Accept: application/json, text/event-stream
```

The `text/event-stream` accept type supports streamable-http responses.

## Port configuration

| Source | Default port |
| --- | --- |
| Python code | `6975` |
| `.env.example` | `9151` |
| Dockerfile | `9151` |
| docker-compose.yml | `9151` |

In practice, Docker deployments use `9151`. Local development uses whatever is in `.env` or falls back to `6975`.
