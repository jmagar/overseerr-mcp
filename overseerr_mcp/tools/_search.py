"""Search domain handler for the overseerr tool."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .utils import validate_subaction

if TYPE_CHECKING:
    from ..client import OverseerrApiClient

logger = logging.getLogger(__name__)

_SEARCH_SUBACTIONS: set[str] = {"media", "help"}

_SEARCH_HELP = """\
### `overseerr` action: `search`

Search for movies or TV shows in Overseerr.

| Subaction | Description |
|-----------|-------------|
| `media`   | Search by title. Use `media_type` to limit to `movie` or `tv`. |
| `help`    | Show this help text. |

**Parameters:**
- `query` (str, required for `media`) — search term
- `media_type` (str, optional) — `"movie"` or `"tv"`; omit to search both

**Examples:**
```
overseerr(action="search", subaction="media", query="Inception", media_type="movie")
overseerr(action="search", subaction="media", query="Breaking Bad")
```
"""


async def _handle_search(
    subaction: str,
    query: str | None,
    media_type: str | None,
    *,
    client: OverseerrApiClient,
) -> list[dict[str, Any]] | str:
    """Handle search action subactions."""
    validate_subaction(subaction, _SEARCH_SUBACTIONS, "search")

    if subaction == "help":
        return _SEARCH_HELP

    # subaction == "media"
    from fastmcp.exceptions import ToolError

    if not query:
        raise ToolError("query is required for search/media")

    logger.info("Executing overseerr action=search subaction=media query=%r", query)
    api_response = await client.get("/search", params={"query": query})

    if isinstance(api_response, str):
        return api_response

    if not isinstance(api_response, dict) or "results" not in api_response:
        return "Error: Received unexpected data structure from Overseerr search."

    results = []
    for item in api_response["results"]:
        item_media_type = item.get("mediaType")
        if media_type and item_media_type != media_type:
            continue
        results.append(
            {
                "tmdbId": item.get("id"),
                "mediaType": item_media_type,
                "title": item.get("title") or item.get("name") or item.get("originalName"),
                "year": (item.get("releaseDate", "") or item.get("firstAirDate", "") or "").split(
                    "-"
                )[0]
                or None,
                "overview": item.get("overview"),
                "posterPath": item.get("posterPath"),
            }
        )

    if not results:
        suffix = f" '{media_type}'" if media_type else ""
        return f"No{suffix} results found for query '{query}'."
    return results
