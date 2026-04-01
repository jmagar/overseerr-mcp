"""Overseerr MCP Server — FastMCP server for Overseerr media requests."""

import logging
import os
import sys
from collections.abc import Callable
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastmcp import Context, FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .client import OverseerrApiClient

# --- Environment & Configuration ---
REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=REPO_ROOT / ".env", override=True)

OVERSEERR_URL = os.getenv("OVERSEERR_URL")
OVERSEERR_API_KEY = os.getenv("OVERSEERR_API_KEY")

OVERSEERR_MCP_TRANSPORT = os.getenv("OVERSEERR_MCP_TRANSPORT", "streamable-http").lower()
OVERSEERR_MCP_HOST = os.getenv("OVERSEERR_MCP_HOST", "0.0.0.0")
OVERSEERR_MCP_PORT = int(os.getenv("OVERSEERR_MCP_PORT", "6975"))
OVERSEERR_MCP_TOKEN = os.getenv("OVERSEERR_MCP_TOKEN", "")
OVERSEERR_MCP_NO_AUTH = os.getenv("OVERSEERR_MCP_NO_AUTH", "false").lower() == "true"

LOG_LEVEL_STR = os.getenv("OVERSEERR_LOG_LEVEL", os.getenv("LOG_LEVEL", "INFO")).upper()
NUMERIC_LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)

# --- Logging Setup ---
logger = logging.getLogger("OverseerrMCPServer")
logger.setLevel(NUMERIC_LOG_LEVEL)
logger.propagate = False

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(NUMERIC_LOG_LEVEL)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    logger.addHandler(console_handler)

LOGS_DIR = REPO_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)
log_file_path = LOGS_DIR / "overseerr_mcp.log"
file_handler = RotatingFileHandler(
    log_file_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
)
file_handler.setLevel(NUMERIC_LOG_LEVEL)
file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s"
    )
)
if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
    logger.addHandler(file_handler)

logger.info(f"Log level: {LOG_LEVEL_STR}, log file: {log_file_path}")
logger.info(f"OVERSEERR_URL loaded: {'Yes' if OVERSEERR_URL else 'No'}")
logger.info(f"OVERSEERR_API_KEY loaded: {'Yes' if OVERSEERR_API_KEY else 'No'}")

if not OVERSEERR_URL or not OVERSEERR_API_KEY:
    logger.error("CRITICAL: OVERSEERR_URL and OVERSEERR_API_KEY must be set. Server cannot start.")
    sys.exit(1)

# --- Client Initialization ---
overseerr_client: OverseerrApiClient | None = None
try:
    overseerr_client = OverseerrApiClient(base_url=OVERSEERR_URL, api_key=OVERSEERR_API_KEY)
    logger.info("OverseerrApiClient initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OverseerrApiClient: {e}", exc_info=True)


# --- Bearer Auth Middleware ---
class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Enforce Bearer token authentication on all requests except /health."""

    def __init__(self, app: Any, token: str) -> None:
        super().__init__(app)
        self._token = token

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Health endpoint is unauthenticated (for Docker healthchecks)
        if request.url.path == "/health":
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer ") or auth_header[len("Bearer ") :] != self._token:
            logger.warning(f"Unauthorized request to {request.url.path} from {request.client}")
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

        return await call_next(request)


# --- Lifespan ---
@asynccontextmanager
async def overseerr_lifespan(app: FastMCP):
    logger.info("Overseerr MCP: startup")
    app.overseerr_client = overseerr_client
    yield
    logger.info("Overseerr MCP: shutdown")
    if overseerr_client:
        await overseerr_client.close()


# --- MCP Server ---
mcp = FastMCP(
    name="OverseerrMCP",
    instructions="Interact with an Overseerr instance for media requests and discovery.",
    lifespan=overseerr_lifespan,
)
mcp.overseerr_client = overseerr_client


# --- Tools ---
@mcp.tool()
async def search_media(ctx: Context, query: str, media_type: str | None = None) -> list[dict] | str:
    """Searches Overseerr for movies or TV shows.

    Args:
        query: The search term.
        media_type: Optional. 'movie' or 'tv' to limit search. Searches both if None.

    Returns:
        A list of search results or an error string.
    """
    logger.info(f"search_media(query='{query}', media_type='{media_type}')")
    client = getattr(ctx.fastmcp, "overseerr_client", None) or overseerr_client
    if not client:
        return "Error: Overseerr API client is not available."

    api_response = await client.get("/search", params={"query": query})
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
async def get_movie_details(ctx: Context, tmdb_id: int) -> dict | str:
    """Retrieves detailed information for a specific movie from Overseerr.

    Args:
        tmdb_id: The TMDB integer ID for the movie.

    Returns:
        A dictionary containing movie details or an error string.
    """
    logger.info(f"get_movie_details(tmdb_id={tmdb_id})")
    client = getattr(ctx.fastmcp, "overseerr_client", None) or overseerr_client
    if not client:
        return "Error: Overseerr API client is not available."

    api_response = await client.get(f"/movie/{tmdb_id}")
    if isinstance(api_response, str):
        return api_response

    if isinstance(api_response, dict) and "id" in api_response and "title" in api_response:
        return api_response

    logger.warning(f"Unexpected /movie/{tmdb_id} response: {api_response}")
    return f"Error: Received incomplete movie data for TMDB ID {tmdb_id}."


@mcp.tool()
async def get_tv_show_details(ctx: Context, tmdb_id: int) -> dict | str:
    """Retrieves detailed information for a specific TV show from Overseerr.

    Args:
        tmdb_id: The TMDB integer ID for the TV show.

    Returns:
        A dictionary containing TV show details (including seasons) or an error string.
    """
    logger.info(f"get_tv_show_details(tmdb_id={tmdb_id})")
    client = getattr(ctx.fastmcp, "overseerr_client", None) or overseerr_client
    if not client:
        return "Error: Overseerr API client is not available."

    api_response = await client.get(f"/tv/{tmdb_id}")
    if isinstance(api_response, str):
        return api_response

    if isinstance(api_response, dict) and "id" in api_response:
        return api_response

    logger.warning(f"Unexpected /tv/{tmdb_id} response: {api_response}")
    return f"Error: Received incomplete TV show data for TMDB ID {tmdb_id}."


@mcp.tool()
async def request_movie(ctx: Context, tmdb_id: int) -> dict | str:
    """Requests a movie on Overseerr using its TMDB ID.

    Args:
        tmdb_id: The TMDB integer ID for the movie to request.

    Returns:
        A dictionary containing the request details or an error string.
    """
    logger.info(f"request_movie(tmdb_id={tmdb_id})")
    client = getattr(ctx.fastmcp, "overseerr_client", None) or overseerr_client
    if not client:
        return "Error: Overseerr API client is not available."

    api_response = await client.post(
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
async def request_tv_show(
    ctx: Context, tmdb_id: int, seasons: list[int] | None = None
) -> dict | str:
    """Requests a TV show or specific seasons on Overseerr using its TMDB ID.

    Args:
        tmdb_id: The TMDB integer ID for the TV show.
        seasons: Optional list of season numbers. Omit to request all seasons.

    Returns:
        A dictionary containing the request details or an error string.
    """
    logger.info(f"request_tv_show(tmdb_id={tmdb_id}, seasons={seasons})")
    client = getattr(ctx.fastmcp, "overseerr_client", None) or overseerr_client
    if not client:
        return "Error: Overseerr API client is not available."

    payload: dict[str, Any] = {
        "mediaType": "tv",
        "mediaId": tmdb_id,
        "seasons": seasons if seasons else "all",
    }
    api_response = await client.post("/request", json_data=payload)
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
            f"TV show TMDB ID {tmdb_id} requested (seasons: {payload['seasons']}). Request ID: {api_response['id']}"
        )
        return api_response

    logger.warning(f"Unexpected /request response for TV show {tmdb_id}: {api_response}")
    return f"Error: TV show request for TMDB ID {tmdb_id} returned unexpected data."


@mcp.tool()
async def list_failed_requests(ctx: Context, count: int = 10, skip: int = 0) -> list[dict] | str:
    """Lists failed media requests from Overseerr.

    Args:
        count: Number of requests to retrieve (default 10).
        skip: Number of requests to skip for pagination (default 0).

    Returns:
        A list of failed requests or an error string.
    """
    logger.info(f"list_failed_requests(count={count}, skip={skip})")
    client = getattr(ctx.fastmcp, "overseerr_client", None) or overseerr_client
    if not client:
        return "Error: Overseerr API client is not available."

    api_response = await client.get(
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


# --- Health Endpoint ---
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    logger.info("Health check requested")
    client: OverseerrApiClient | None = (
        getattr(request.app, "overseerr_client", None)
        or getattr(mcp, "overseerr_client", None)
        or overseerr_client
    )

    if not OVERSEERR_URL or not OVERSEERR_API_KEY:
        return JSONResponse(
            {
                "status": "error",
                "service_accessible": False,
                "reason": "OVERSEERR_URL or OVERSEERR_API_KEY not configured",
            },
            status_code=500,
        )

    if not client:
        return JSONResponse(
            {
                "status": "error",
                "service_accessible": False,
                "reason": "Overseerr client not initialized",
            },
            status_code=503,
        )

    try:
        response = await client.get("/settings/main")
        if isinstance(response, dict):
            return JSONResponse(
                {
                    "status": "ok",
                    "service_accessible": True,
                    "details": {
                        "app_title": response.get("applicationTitle", "Overseerr"),
                        "app_url": response.get("applicationUrl", "N/A"),
                    },
                }
            )
        return JSONResponse(
            {"status": "error", "service_accessible": False, "reason": f"API error: {response}"},
            status_code=503,
        )
    except Exception as e:
        logger.exception("Unexpected exception during health check")
        return JSONResponse(
            {"status": "error", "service_accessible": False, "reason": str(e)},
            status_code=500,
        )


def main() -> None:
    """Entry point for the Overseerr MCP server."""
    logger.info(
        f"Starting Overseerr MCP Server — transport: {OVERSEERR_MCP_TRANSPORT}, port: {OVERSEERR_MCP_PORT}"
    )

    if OVERSEERR_MCP_TRANSPORT == "stdio":
        mcp.run()
    elif OVERSEERR_MCP_TRANSPORT in ("http", "streamable-http"):
        app = mcp.http_app(path="/mcp")
        if not OVERSEERR_MCP_NO_AUTH and OVERSEERR_MCP_TOKEN:
            app.add_middleware(BearerAuthMiddleware, token=OVERSEERR_MCP_TOKEN)
            logger.info("BearerAuthMiddleware enabled")
        else:
            logger.warning(
                "Bearer auth disabled — set OVERSEERR_MCP_TOKEN to enable request-level authentication"
            )
        import uvicorn

        uvicorn.run(app, host=OVERSEERR_MCP_HOST, port=OVERSEERR_MCP_PORT)
    elif OVERSEERR_MCP_TRANSPORT == "sse":
        mcp.run(transport="sse", host=OVERSEERR_MCP_HOST, port=OVERSEERR_MCP_PORT, path="/sse")
    else:
        logger.error(f"Invalid transport '{OVERSEERR_MCP_TRANSPORT}', falling back to stdio")
        mcp.run()


if __name__ == "__main__":
    main()
