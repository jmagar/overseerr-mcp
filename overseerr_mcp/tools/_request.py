"""Request management domain handler for the overseerr tool."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .utils import validate_subaction

if TYPE_CHECKING:
    from ..client import OverseerrApiClient

logger = logging.getLogger(__name__)

_REQUEST_SUBACTIONS: set[str] = {"failed", "help"}

_REQUEST_HELP = """\
### `overseerr` action: `request`

Manage media requests in Overseerr.

| Subaction | Description |
|-----------|-------------|
| `failed`  | List failed media requests. |
| `help`    | Show this help text. |

**Parameters:**
- `count` (int, default `10`) — number of requests to retrieve
- `skip` (int, default `0`) — number to skip for pagination

**Examples:**
```
overseerr(action="request", subaction="failed")
overseerr(action="request", subaction="failed", count=20, skip=10)
```
"""


async def _handle_request(
    subaction: str,
    count: int,
    skip: int,
    *,
    client: OverseerrApiClient,
) -> list[dict[str, Any]] | str:
    """Handle request action subactions."""
    validate_subaction(subaction, _REQUEST_SUBACTIONS, "request")

    if subaction == "help":
        return _REQUEST_HELP

    # subaction == "failed"
    logger.info("Executing overseerr action=request subaction=failed count=%s skip=%s", count, skip)
    api_response = await client.get(
        "/request",
        params={"take": count, "skip": skip, "sort": "modified", "filter": "failed"},
    )

    if isinstance(api_response, str):
        return api_response

    if not isinstance(api_response, dict) or "results" not in api_response:
        return "Error: Received unexpected data structure from Overseerr for failed requests."

    results = []
    for req in api_response["results"]:
        media_info = req.get("media", {})
        results.append({
            "requestId": req.get("id"),
            "status": req.get("status"),
            "type": media_info.get("mediaType"),
            "tmdbId": media_info.get("tmdbId"),
            "title": media_info.get("title") or media_info.get("name"),
            "requested_by": req.get("requestedBy", {}).get("displayName"),
            "requested_at": req.get("createdAt"),
            "modified_at": req.get("modifiedAt"),
        })

    return results if results else "No failed requests found."
