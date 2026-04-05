# Tool Schema — overseerr-mcp

## Schema generation

Tool schemas are generated automatically by FastMCP from Python function signatures and docstrings. No manual schema maintenance is required.

## Source of truth

All tool definitions live in `overseerr_mcp/server.py`:

```python
@mcp.tool()
async def search_media(ctx: Context, query: str, media_type: str | None = None) -> list[dict] | str:
    """Searches Overseerr for movies or TV shows."""

@mcp.tool()
async def get_movie_details(ctx: Context, tmdb_id: int) -> dict | str:
    """Retrieves detailed information for a specific movie from Overseerr."""

@mcp.tool()
async def get_tv_show_details(ctx: Context, tmdb_id: int) -> dict | str:
    """Retrieves detailed information for a specific TV show from Overseerr."""

@mcp.tool()
async def request_movie(ctx: Context, tmdb_id: int) -> dict | str:
    """Requests a movie on Overseerr using its TMDB ID."""

@mcp.tool()
async def request_tv_show(ctx: Context, tmdb_id: int, seasons: list[int] | None = None) -> dict | str:
    """Requests a TV show or specific seasons on Overseerr using its TMDB ID."""

@mcp.tool()
async def list_failed_requests(ctx: Context, count: int = 10, skip: int = 0) -> list[dict] | str:
    """Lists failed media requests from Overseerr."""

@mcp.tool()
async def overseerr_help() -> str:
    """Returns markdown help for all Overseerr MCP tools and parameters."""
```

## Parameter types

| Python type | JSON Schema type | Notes |
| --- | --- | --- |
| `str` | `string` | — |
| `int` | `integer` | — |
| `str \| None` | `string` or `null` | Optional parameter |
| `list[int] \| None` | `array` of `integer` or `null` | Optional list |

## Return types

All tools return either structured data (`dict`, `list[dict]`) on success or an error string on failure. Clients should check whether the return value is a string before treating it as structured data.

## Verification

Run `tools/list` against a running server to see the generated schemas:

```bash
curl -s -X POST http://localhost:9151/mcp \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | jq '.result.tools'
```
