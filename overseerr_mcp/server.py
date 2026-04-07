"""Overseerr MCP Server — FastMCP server for Overseerr media requests.

Tool:
  overseerr — all operations via action + subaction routing

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
from typing import TYPE_CHECKING

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
from .tools.overseerr import register_overseerr_tool

register_overseerr_tool(mcp, _client)


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
