# Code Patterns — overseerr-mcp

## Tool pattern (flat tools)

Unlike the action-router pattern used by some plugins, overseerr-mcp uses flat tools — each operation is a separate `@mcp.tool()` function:

```python
@mcp.tool()
async def search_media(ctx: Context, query: str, media_type: str | None = None) -> list[dict] | str:
    ...
```

This is appropriate because overseerr-mcp has a small, well-defined API surface (7 tools).

## Client access pattern

Every tool retrieves the API client from the FastMCP context with a fallback to the module-level instance:

```python
client = getattr(ctx.fastmcp, "overseerr_client", None) or overseerr_client
if not client:
    return "Error: Overseerr API client is not available."
```

## Error handling pattern

Tools return structured data on success and error strings on failure. Error strings always start with `"Error:"`:

```python
api_response = await client.get("/search", params={"query": query})
if isinstance(api_response, str):
    return api_response  # Already an error string from the client
```

The `OverseerrApiClient._request` method catches:
- `httpx.HTTPStatusError` — HTTP 4xx/5xx from Overseerr
- `httpx.RequestError` — connection failures
- Generic `Exception` — unexpected errors

All are converted to descriptive error strings.

## Response validation pattern

Tools validate response structure before returning:

```python
if isinstance(api_response, dict) and "id" in api_response and "title" in api_response:
    return api_response
logger.warning(f"Unexpected response: {api_response}")
return f"Error: Received incomplete data for TMDB ID {tmdb_id}."
```

## URL encoding pattern

The API client URL-encodes string parameters:

```python
if isinstance(value, str):
    encoded_params[key] = quote_plus(value)
```

## Middleware pattern

Bearer auth is a Starlette middleware added to the ASGI app:

```python
app = mcp.http_app(path="/mcp")
if not OVERSEERR_MCP_NO_AUTH and OVERSEERR_MCP_TOKEN:
    app.add_middleware(BearerAuthMiddleware, token=OVERSEERR_MCP_TOKEN)
```

The middleware exempts `/health` from auth.

## Lifespan pattern

The server uses FastMCP's async context manager lifespan for client lifecycle:

```python
@asynccontextmanager
async def overseerr_lifespan(app: FastMCP):
    logger.info("Overseerr MCP: startup")
    app.overseerr_client = overseerr_client
    yield
    logger.info("Overseerr MCP: shutdown")
    if overseerr_client:
        await overseerr_client.close()
```

## Logging pattern

Log tool invocations at INFO with parameters. Log API errors at ERROR with full context. Never log credentials.

```python
logger.info(f"search_media(query='{query}', media_type='{media_type}')")
logger.error(f"Overseerr API HTTP Error: {e.response.status_code} for {e.request.url}")
```
