# MCP Resources — overseerr-mcp

## Current state

overseerr-mcp does not expose any MCP resources. All data access is through MCP tools.

## Health endpoint

The server exposes a custom HTTP route (not an MCP resource):

```
GET /health → {"status": "ok"}
```

This is unauthenticated and used for Docker healthchecks and liveness probes.

## Future considerations

Potential MCP resources that could be added:

- `overseerr://requests/pending` — list of pending requests
- `overseerr://requests/failed` — list of failed requests
- `overseerr://status` — server and upstream Overseerr status
