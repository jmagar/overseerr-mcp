# Client Connection — overseerr-mcp

## Claude Code plugin (recommended)

```bash
/plugin marketplace add jmagar/claude-homelab
/plugin install overseerr-mcp @jmagar-claude-homelab
```

Configure `overseerr_mcp_url` and `overseerr_mcp_token` when prompted.

## Direct HTTP

### .mcp.json

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

### curl

```bash
# Initialize session
curl -X POST http://localhost:9151/mcp \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1"}}}'

# Call a tool
curl -X POST http://localhost:9151/mcp \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"search_media","arguments":{"query":"Dune"}}}'
```

## stdio (uvx)

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

## stdio (local development)

```json
{
  "mcpServers": {
    "overseerr-mcp": {
      "command": "uv",
      "args": ["run", "python", "-m", "overseerr_mcp"],
      "env": {
        "OVERSEERR_MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

## SSE

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

## Gemini

The `gemini-extension.json` configures Gemini to use stdio transport:

```json
{
  "mcpServers": {
    "overseerr-mcp": {
      "command": "uv",
      "args": ["run", "overseerr-mcp-server"],
      "cwd": "${extensionPath}"
    }
  }
}
```

## Health check

All transports can verify the server is running:

```bash
curl http://localhost:9151/health
# → {"status": "ok"}
```

Or:

```bash
just health
```
