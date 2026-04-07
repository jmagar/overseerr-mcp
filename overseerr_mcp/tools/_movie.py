"""Movie domain handler for the overseerr tool."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .utils import validate_subaction

if TYPE_CHECKING:
    from ..client import OverseerrApiClient

logger = logging.getLogger(__name__)

_MOVIE_SUBACTIONS: set[str] = {"details", "request", "help"}

_MOVIE_HELP = """\
### `overseerr` action: `movie`

Retrieve movie details or submit a movie request.

| Subaction | Description |
|-----------|-------------|
| `details` | Get full movie info from Overseerr by TMDB ID. |
| `request` | Request a movie by TMDB ID. |
| `help`    | Show this help text. |

**Parameters:**
- `tmdb_id` (int, required for `details` and `request`) — TMDB integer ID

**Examples:**
```
overseerr(action="movie", subaction="details", tmdb_id=27205)
overseerr(action="movie", subaction="request", tmdb_id=27205)
```
"""


async def _handle_movie(
    subaction: str,
    tmdb_id: int | None,
    *,
    client: OverseerrApiClient,
) -> dict[str, Any] | str:
    """Handle movie action subactions."""
    validate_subaction(subaction, _MOVIE_SUBACTIONS, "movie")

    if subaction == "help":
        return _MOVIE_HELP

    from fastmcp.exceptions import ToolError

    if tmdb_id is None:
        raise ToolError(f"tmdb_id is required for movie/{subaction}")

    logger.info("Executing overseerr action=movie subaction=%s tmdb_id=%s", subaction, tmdb_id)

    if subaction == "details":
        return await client.get(f"/movie/{tmdb_id}")

    # subaction == "request"
    return await client.post("/request", json_data={"mediaType": "movie", "mediaId": tmdb_id})
