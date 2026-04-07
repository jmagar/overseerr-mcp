"""TV show domain handler for the overseerr tool."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .utils import validate_subaction

if TYPE_CHECKING:
    from ..client import OverseerrApiClient

logger = logging.getLogger(__name__)

_TV_SUBACTIONS: set[str] = {"details", "request", "help"}

_TV_HELP = """\
### `overseerr` action: `tv`

Retrieve TV show details or submit a TV show request.

| Subaction | Description |
|-----------|-------------|
| `details` | Get full TV show info (includes seasons) from Overseerr by TMDB ID. |
| `request` | Request a TV show or specific seasons by TMDB ID. |
| `help`    | Show this help text. |

**Parameters:**
- `tmdb_id` (int, required for `details` and `request`) — TMDB integer ID
- `seasons` (list[int], optional for `request`) — season numbers to request; omit to request all

**Examples:**
```
overseerr(action="tv", subaction="details", tmdb_id=1396)
overseerr(action="tv", subaction="request", tmdb_id=1396)
overseerr(action="tv", subaction="request", tmdb_id=1396, seasons=[1, 2])
```
"""


async def _handle_tv(
    subaction: str,
    tmdb_id: int | None,
    seasons: list[int] | None,
    *,
    client: OverseerrApiClient,
) -> dict[str, Any] | list[Any] | str:
    """Handle tv action subactions."""
    validate_subaction(subaction, _TV_SUBACTIONS, "tv")

    if subaction == "help":
        return _TV_HELP

    from fastmcp.exceptions import ToolError

    if tmdb_id is None:
        raise ToolError(f"tmdb_id is required for tv/{subaction}")

    logger.info("Executing overseerr action=tv subaction=%s tmdb_id=%s", subaction, tmdb_id)

    if subaction == "details":
        return await client.get(f"/tv/{tmdb_id}")

    # subaction == "request"
    return await client.post(
        "/request",
        json_data={"mediaType": "tv", "mediaId": tmdb_id, "seasons": seasons or "all"},
    )
