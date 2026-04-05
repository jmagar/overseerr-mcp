# Transport Configuration — overseerr-mcp

## Available transports

Set via `OVERSEERR_MCP_TRANSPORT`:

| Mode | Value | Endpoint | When to use |
| --- | --- | --- | --- |
| Streamable HTTP | `streamable-http` | `/mcp` | Default; modern MCP clients (Claude.ai) |
| HTTP | `http` | `/mcp` | Clients that do not support streaming |
| stdio | `stdio` | — | Local CLI integration, no network port |
| SSE | `sse` | `/sse` | Legacy MCP clients that require SSE |

## Streamable HTTP (default)

```bash
OVERSEERR_MCP_TRANSPORT=streamable-http
OVERSEERR_MCP_HOST=0.0.0.0
OVERSEERR_MCP_PORT=9151
```

The server creates a Starlette ASGI app via `mcp.http_app(path="/mcp")` and runs it with Uvicorn. Bearer auth middleware is added unless `OVERSEERR_MCP_NO_AUTH=true`.

## HTTP

```bash
OVERSEERR_MCP_TRANSPORT=http
```

Same as streamable-http but without streaming support. Uses the same `/mcp` endpoint.

## stdio

```bash
OVERSEERR_MCP_TRANSPORT=stdio
```

No HTTP server is started. The server reads JSON-RPC from stdin and writes to stdout. Used for local development and `uvx` invocations:

```bash
uvx --from . overseerr-mcp-server
```

No authentication is needed in stdio mode.

## SSE

```bash
OVERSEERR_MCP_TRANSPORT=sse
```

Server-Sent Events transport at `/sse`. Uses FastMCP's built-in SSE support:

```python
mcp.run(transport="sse", host=OVERSEERR_MCP_HOST, port=OVERSEERR_MCP_PORT, path="/sse")
```

## Client connection

### HTTP/streamable-http

```json
{
  "mcpServers": {
    "overseerr-mcp": {
      "type": "http",
      "url": "http://localhost:9151/mcp",
      "headers": {
        "Authorization": "Bearer <token>"
      }
    }
  }
}
```

### stdio

```json
{
  "mcpServers": {
    "overseerr-mcp": {
      "command": "uvx",
      "args": ["--from", "overseerr-mcp", "overseerr-mcp-server"],
      "env": {
        "OVERSEERR_URL": "https://overseerr.example.com",
        "OVERSEERR_API_KEY": "<key>",
        "OVERSEERR_MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

### SSE

```json
{
  "mcpServers": {
    "overseerr-mcp": {
      "type": "sse",
      "url": "http://localhost:9151/sse"
    }
  }
}
```

## Fallback behavior

If `OVERSEERR_MCP_TRANSPORT` is set to an unrecognized value, the server logs an error and falls back to stdio.
