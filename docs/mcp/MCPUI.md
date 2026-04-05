# Client UI Integration — overseerr-mcp

## Claude Code

### Plugin installation

```bash
/plugin marketplace add jmagar/claude-homelab
/plugin install overseerr-mcp @jmagar-claude-homelab
```

### Skill invocation

The `overseerr` skill activates automatically when the user mentions media requests, Overseerr, Plex, movies, or TV shows. Claude then uses the MCP tools directly.

### Tool names in Claude Code

Tools appear with the prefix `mcp__overseerr-mcp__`:

- `mcp__overseerr-mcp__search_media`
- `mcp__overseerr-mcp__get_movie_details`
- `mcp__overseerr-mcp__get_tv_show_details`
- `mcp__overseerr-mcp__request_movie`
- `mcp__overseerr-mcp__request_tv_show`
- `mcp__overseerr-mcp__list_failed_requests`
- `mcp__overseerr-mcp__overseerr_help`

### Default prompts (Codex)

The `.codex-plugin/plugin.json` suggests:

- "Search Overseerr for a movie."
- "Request a TV show in Overseerr."
- "Check failed Overseerr requests."

## Gemini

Extension file: `gemini-extension.json`

Gemini runs the server via `uv run overseerr-mcp-server` in stdio mode. Settings for `OVERSEERR_URL` and `OVERSEERR_API_KEY` are configured through the extension settings UI.

## Generic MCP clients

Any MCP-compatible client can connect via:

- **HTTP:** POST to `http://host:9151/mcp` with Bearer auth
- **stdio:** Run `uvx --from overseerr-mcp overseerr-mcp-server` with env vars
- **SSE:** Connect to `http://host:9151/sse`

See [CONNECT.md](CONNECT.md) for detailed examples.
