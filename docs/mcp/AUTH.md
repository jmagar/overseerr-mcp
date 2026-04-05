# Authentication — overseerr-mcp

Two layers of authentication: inbound (client to MCP server) and outbound (MCP server to Overseerr).

## Inbound: Client to MCP server

### Bearer token (default)

HTTP transport requires `OVERSEERR_MCP_TOKEN`. All requests to `/mcp` must include:

```
Authorization: Bearer <token>
```

Generate a token:

```bash
just gen-token
# or: openssl rand -hex 32
```

Set in `.env`:

```bash
OVERSEERR_MCP_TOKEN=abc123...
```

### Token verification

The server uses `BearerAuthMiddleware` (Starlette middleware) with timing-safe comparison via `hmac.compare_digest`:

```python
class BearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path == "/health":
            return await call_next(request)
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer ") or not hmac.compare_digest(
            auth_header[len("Bearer "):], self._token
        ):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        return await call_next(request)
```

### No-auth mode

Set `OVERSEERR_MCP_NO_AUTH=true` to disable bearer auth. Only appropriate when the server is behind a trusted reverse proxy that handles authentication.

### Unauthenticated endpoints

`GET /health` is always unauthenticated for Docker healthchecks and liveness probes.

## Outbound: MCP server to Overseerr

The `OverseerrApiClient` authenticates to Overseerr using the `X-Api-Key` header:

```python
self._client = httpx.AsyncClient(headers={"X-Api-Key": self.api_key})
```

The API key is set via `OVERSEERR_API_KEY` and is never exposed to MCP clients.

## Transport-specific auth

| Transport | Auth required | Mechanism |
| --- | --- | --- |
| `streamable-http` | yes* | Bearer token on every HTTP request |
| `http` | yes* | Bearer token on every HTTP request |
| `sse` | no | SSE transport uses FastMCP's built-in auth |
| `stdio` | no | No network, no auth needed |

*Unless `OVERSEERR_MCP_NO_AUTH=true`.

## Client configuration examples

### Claude Code plugin

Configure via userConfig when installing the plugin:

```json
{
  "overseerr_mcp_url": "https://overseerr.example.com/mcp",
  "overseerr_mcp_token": "<your-token>"
}
```

### Direct HTTP client

```bash
curl -X POST http://localhost:9151/mcp \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"search_media","arguments":{"query":"Dune"}}}'
```
