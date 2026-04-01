# overseerr-mcp

MCP server for Overseerr media request management.

## Development

- Language: Python (FastMCP + uv)
- Port: 9151 (OVERSEERR_MCP_PORT)
- Auth: Bearer token (OVERSEERR_MCP_TOKEN) + Overseerr API key (OVERSEERR_API_KEY)

## Commands

```bash
just dev       # run locally
just test      # run tests
just lint      # ruff check
just build     # docker build
```
