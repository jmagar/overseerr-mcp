"""Overseerr MCP Server — FastMCP server for Overseerr media requests.

Tools:
  overseerr       — all operations via action + subaction routing
  overseerr_help  — returns markdown help for all actions

Transport: OVERSEERR_MCP_TRANSPORT=stdio (default) | http
Auth:      OVERSEERR_MCP_TOKEN (required for HTTP; skipped for stdio)
"""

from __future__ import annotations

import hmac
import logging
import logging.handlers
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any

from dotenv import load_dotenv
from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

if TYPE_CHECKING:
    from starlette.requests import Request

from .client import OverseerrApiClient

# ---------------------------------------------------------------------------
# Environment loading
# ---------------------------------------------------------------------------
load_dotenv(dotenv_path=Path.home() / ".config" / "overseerr-mcp" / ".env")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL_STR = os.getenv("OVERSEERR_LOG_LEVEL", os.getenv("LOG_LEVEL", "INFO")).upper()
NUMERIC_LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)

logger = logging.getLogger("OverseerrMCPServer")
logger.setLevel(NUMERIC_LOG_LEVEL)
logger.propagate = False

_console = logging.StreamHandler(sys.stderr)
_console.setLevel(NUMERIC_LOG_LEVEL)
_console.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    logger.addHandler(_console)

_logs_dir = Path(__file__).resolve().parent.parent / "logs"
try:
    _logs_dir.mkdir(parents=True, exist_ok=True)
    _file_handler = logging.handlers.RotatingFileHandler(
        _logs_dir / "overseerr_mcp.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    _file_handler.setLevel(NUMERIC_LOG_LEVEL)
    _file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s"
            " - %(module)s - %(funcName)s - %(lineno)d - %(message)s"
        )
    )
    if not any(isinstance(h, logging.handlers.RotatingFileHandler) for h in logger.handlers):
        logger.addHandler(_file_handler)
except (OSError, PermissionError) as _e:
    logger.warning("File logging unavailable (%s) — logging to stderr only", _e)

# ---------------------------------------------------------------------------
# Configuration & startup validation
# ---------------------------------------------------------------------------
OVERSEERR_URL = os.getenv("OVERSEERR_URL", "")
OVERSEERR_API_KEY = os.getenv("OVERSEERR_API_KEY", "")
OVERSEERR_MCP_TOKEN = os.getenv("OVERSEERR_MCP_TOKEN")
OVERSEERR_MCP_NO_AUTH = os.getenv("OVERSEERR_MCP_NO_AUTH", "").lower() in ("true", "1", "yes")
OVERSEERR_MCP_TRANSPORT = os.getenv("OVERSEERR_MCP_TRANSPORT", "stdio").lower()
OVERSEERR_MCP_HOST = os.getenv("OVERSEERR_MCP_HOST", "0.0.0.0")
OVERSEERR_MCP_PORT = int(os.getenv("OVERSEERR_MCP_PORT", "9151"))

if not OVERSEERR_URL:
    print(
        "CRITICAL: OVERSEERR_URL must be set in the environment.\n"
        "If running as a Claude Code plugin, set it in the plugin settings.",
        file=sys.stderr,
    )
    sys.exit(1)

if not OVERSEERR_API_KEY:
    print(
        "CRITICAL: OVERSEERR_API_KEY must be set in the environment.\n"
        "If running as a Claude Code plugin, set it in the plugin settings.",
        file=sys.stderr,
    )
    sys.exit(1)

if OVERSEERR_MCP_TRANSPORT != "stdio" and not OVERSEERR_MCP_NO_AUTH and not OVERSEERR_MCP_TOKEN:
    print(
        "CRITICAL: OVERSEERR_MCP_TOKEN is not set.\n"
        "Set OVERSEERR_MCP_TOKEN to a secure random token, or set OVERSEERR_MCP_NO_AUTH=true\n"
        "to disable auth (only appropriate when secured at the network/proxy level).\n\n"
        "Generate a token with: openssl rand -hex 32",
        file=sys.stderr,
    )
    sys.exit(1)

# Scrub sensitive credentials from process environment to reduce /proc exposure
for _key in ("OVERSEERR_API_KEY", "OVERSEERR_MCP_TOKEN"):
    os.environ.pop(_key, None)

# ---------------------------------------------------------------------------
# Overseerr API client (singleton)
# ---------------------------------------------------------------------------
_client = OverseerrApiClient(base_url=OVERSEERR_URL, api_key=OVERSEERR_API_KEY)


# ---------------------------------------------------------------------------
# FastMCP server + BearerAuth middleware
# ---------------------------------------------------------------------------
class BearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if OVERSEERR_MCP_NO_AUTH:
            return await call_next(request)
        # /health is always unauthenticated
        if request.url.path in ("/health",):
            return await call_next(request)
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        provided = auth[7:]
        if not hmac.compare_digest(provided, OVERSEERR_MCP_TOKEN or ""):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        return await call_next(request)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def overseerr_lifespan(_app: FastMCP):
    logger.info("Overseerr MCP: startup")
    yield
    logger.info("Overseerr MCP: shutdown")
    await _client.close()


mcp = FastMCP(
    name="OverseerrMCP",
    instructions="Interact with an Overseerr instance for media requests and discovery.",
    lifespan=overseerr_lifespan,
)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def search_media(query: str, media_type: str | None = None) -> list[dict] | str:
    """Searches Overseerr for movies or TV shows.

    Args:
        query: The search term.
        media_type: Optional. 'movie' or 'tv' to limit search. Searches both if None.

    Returns:
        A list of search results or an error string.
    """
    logger.info(f"search_media(query='{query}', media_type='{media_type}')")

    api_response = await _client.get("/search", params={"query": query})
    if isinstance(api_response, str):
        return api_response

    results = []
    if isinstance(api_response, dict) and "results" in api_response:
        for item in api_response["results"]:
            item_media_type = item.get("mediaType")
            if media_type and item_media_type != media_type:
                continue
            results.append(
                {
                    "tmdbId": item.get("id"),
                    "mediaType": item_media_type,
                    "title": item.get("title") or item.get("name") or item.get("originalName"),
                    "year": (
                        item.get("releaseDate", "") or item.get("firstAirDate", "") or ""
                    ).split("-")[0]
                    or None,
                    "overview": item.get("overview"),
                    "posterPath": item.get("posterPath"),
                }
            )

        if not results:
            suffix = f" '{media_type}'" if media_type else ""
            return f"No{suffix} results found for query '{query}'."
        return results

    logger.warning(f"Unexpected /search response: {api_response}")
    return "Error: Received unexpected data structure from Overseerr search."


@mcp.tool()
async def get_movie_details(tmdb_id: int) -> dict | str:
    """Retrieves detailed information for a specific movie from Overseerr.

    Args:
        tmdb_id: The TMDB integer ID for the movie.

    Returns:
        A dictionary containing movie details or an error string.
    """
    logger.info(f"get_movie_details(tmdb_id={tmdb_id})")

    api_response = await _client.get(f"/movie/{tmdb_id}")
    if isinstance(api_response, str):
        return api_response

    if isinstance(api_response, dict) and "id" in api_response and "title" in api_response:
        return api_response

    logger.warning(f"Unexpected /movie/{tmdb_id} response: {api_response}")
    return f"Error: Received incomplete movie data for TMDB ID {tmdb_id}."


@mcp.tool()
async def get_tv_show_details(tmdb_id: int) -> dict | str:
    """Retrieves detailed information for a specific TV show from Overseerr.

    Args:
        tmdb_id: The TMDB integer ID for the TV show.

    Returns:
        A dictionary containing TV show details (including seasons) or an error string.
    """
    logger.info(f"get_tv_show_details(tmdb_id={tmdb_id})")

    api_response = await _client.get(f"/tv/{tmdb_id}")
    if isinstance(api_response, str):
        return api_response

    if isinstance(api_response, dict) and "id" in api_response:
        return api_response

    logger.warning(f"Unexpected /tv/{tmdb_id} response: {api_response}")
    return f"Error: Received incomplete TV show data for TMDB ID {tmdb_id}."


@mcp.tool()
async def request_movie(tmdb_id: int) -> dict | str:
    """Requests a movie on Overseerr using its TMDB ID.

    Args:
        tmdb_id: The TMDB integer ID for the movie to request.

    Returns:
        A dictionary containing the request details or an error string.
    """
    logger.info(f"request_movie(tmdb_id={tmdb_id})")

    api_response = await _client.post(
        "/request", json_data={"mediaType": "movie", "mediaId": tmdb_id}
    )
    if isinstance(api_response, str):
        return api_response

    if (
        isinstance(api_response, dict)
        and "id" in api_response
        and "status" in api_response
        and isinstance(api_response.get("media"), dict)
        and api_response["media"].get("tmdbId") == tmdb_id
    ):
        logger.info(f"Movie TMDB ID {tmdb_id} requested. Request ID: {api_response['id']}")
        return api_response

    logger.warning(f"Unexpected /request response for movie {tmdb_id}: {api_response}")
    return f"Error: Movie request for TMDB ID {tmdb_id} returned unexpected data."


@mcp.tool()
async def request_tv_show(tmdb_id: int, seasons: list[int] | None = None) -> dict | str:
    """Requests a TV show or specific seasons on Overseerr using its TMDB ID.

    Args:
        tmdb_id: The TMDB integer ID for the TV show.
        seasons: Optional list of season numbers. Omit to request all seasons.

    Returns:
        A dictionary containing the request details or an error string.
    """
    logger.info(f"request_tv_show(tmdb_id={tmdb_id}, seasons={seasons})")

    payload: dict[str, Any] = {
        "mediaType": "tv",
        "mediaId": tmdb_id,
        "seasons": seasons if seasons else "all",
    }
    api_response = await _client.post("/request", json_data=payload)
    if isinstance(api_response, str):
        return api_response

    if (
        isinstance(api_response, dict)
        and "id" in api_response
        and "status" in api_response
        and isinstance(api_response.get("media"), dict)
        and api_response["media"].get("tmdbId") == tmdb_id
    ):
        logger.info(
            "TV show TMDB ID %s requested (seasons: %s). Request ID: %s",
            tmdb_id,
            payload["seasons"],
            api_response["id"],
        )
        return api_response

    logger.warning(f"Unexpected /request response for TV show {tmdb_id}: {api_response}")
    return f"Error: TV show request for TMDB ID {tmdb_id} returned unexpected data."


@mcp.tool()
async def list_failed_requests(count: int = 10, skip: int = 0) -> list[dict] | str:
    """Lists failed media requests from Overseerr.

    Args:
        count: Number of requests to retrieve (default 10).
        skip: Number of requests to skip for pagination (default 0).

    Returns:
        A list of failed requests or an error string.
    """
    logger.info(f"list_failed_requests(count={count}, skip={skip})")

    api_response = await _client.get(
        "/request", params={"take": count, "skip": skip, "sort": "modified", "filter": "failed"}
    )
    if isinstance(api_response, str):
        return api_response

    if isinstance(api_response, dict) and "results" in api_response:
        results = []
        for req in api_response["results"]:
            media_info = req.get("media", {})
            results.append(
                {
                    "requestId": req.get("id"),
                    "status": req.get("status"),
                    "type": media_info.get("mediaType"),
                    "tmdbId": media_info.get("tmdbId"),
                    "title": media_info.get("title") or media_info.get("name"),
                    "requested_by": req.get("requestedBy", {}).get("displayName"),
                    "requested_at": req.get("createdAt"),
                    "modified_at": req.get("modifiedAt"),
                }
            )
        return results if results else "No failed requests found."

    logger.warning(f"Unexpected /request response for failed list: {api_response}")
    return "Error: Received unexpected data structure from Overseerr for failed requests."


# ---------------------------------------------------------------------------
# Tool: overseerr_help
# ---------------------------------------------------------------------------

_HELP_TEXT = """# Overseerr MCP Server

Interact with an Overseerr instance for media discovery and requests.

## Tools

### `overseerr_help`

Returns this markdown help document.

### `search_media`

Search for movies or TV shows.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | yes | Search term |
| `media_type` | string | no | `"movie"` or `"tv"` — searches both if omitted |

**Example:**
```
search_media(query="Inception", media_type="movie")
search_media(query="Breaking Bad")
```

### `get_movie_details`

Retrieve detailed information for a specific movie.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tmdb_id` | int | yes | TMDB integer ID for the movie |

**Example:**
```
get_movie_details(tmdb_id=27205)
```

### `get_tv_show_details`

Retrieve detailed information for a specific TV show (includes seasons).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tmdb_id` | int | yes | TMDB integer ID for the TV show |

**Example:**
```
get_tv_show_details(tmdb_id=1396)
```

### `request_movie`

Request a movie on Overseerr using its TMDB ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tmdb_id` | int | yes | TMDB integer ID for the movie to request |

**Example:**
```
request_movie(tmdb_id=27205)
```

### `request_tv_show`

Request a TV show or specific seasons on Overseerr.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tmdb_id` | int | yes | TMDB integer ID for the TV show |
| `seasons` | list[int] | no | Season numbers to request — omit to request all seasons |

**Example:**
```
request_tv_show(tmdb_id=1396)
request_tv_show(tmdb_id=1396, seasons=[1, 2])
```

### `list_failed_requests`

List failed media requests from Overseerr.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `count` | int | `10` | Number of requests to retrieve |
| `skip` | int | `0` | Number of requests to skip (pagination) |

**Example:**
```
list_failed_requests(count=20)
list_failed_requests(count=10, skip=10)
```

## Typical Workflow

1. Search for content: `search_media(query="Dune")`
2. Get TMDB ID from results
3. View details: `get_movie_details(tmdb_id=438631)`
4. Submit request: `request_movie(tmdb_id=438631)`
5. Check failures: `list_failed_requests()`
"""


@mcp.tool()
async def overseerr_help() -> str:
    """Returns markdown help for all Overseerr MCP tools and parameters."""
    return _HELP_TEXT


# ---------------------------------------------------------------------------
# /health endpoint (unauthenticated)
# ---------------------------------------------------------------------------


@mcp.custom_route("/health", methods=["GET"])
async def health_check(_request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    logger.info(
        "Starting Overseerr MCP Server — transport=%s host=%s port=%s auth=%s",
        OVERSEERR_MCP_TRANSPORT,
        OVERSEERR_MCP_HOST,
        OVERSEERR_MCP_PORT,
        "disabled" if OVERSEERR_MCP_NO_AUTH else "bearer",
    )

    if OVERSEERR_MCP_TRANSPORT == "stdio":
        mcp.run(transport="stdio")
    else:
        http_middleware = None if OVERSEERR_MCP_NO_AUTH else [Middleware(BearerAuthMiddleware)]
        mcp.run(
            transport="streamable-http",
            host=OVERSEERR_MCP_HOST,
            port=OVERSEERR_MCP_PORT,
            log_level=LOG_LEVEL_STR.lower(),
            middleware=http_middleware,
        )


if __name__ == "__main__":
    main()
