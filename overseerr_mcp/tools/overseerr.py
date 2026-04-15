"""Single consolidated Overseerr tool registration.

Provides the `overseerr` tool with action + subaction routing.

Actions:
  help    - Full help for all actions and subactions
  search  - Search for movies or TV shows (subactions: media, help)
  movie   - Movie details and requests (subactions: details, request, help)
  tv      - TV show details and requests (subactions: details, request, help)
  request - Request management (subactions: failed, help)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from ._movie import _MOVIE_HELP, _handle_movie
from ._request import _REQUEST_HELP, _handle_request
from ._search import _SEARCH_HELP, _handle_search
from ._tv import _TV_HELP, _handle_tv

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from ..client import OverseerrApiClient

OVERSEERR_ACTIONS = Literal["help", "search", "movie", "tv", "request"]

_HELP_TEXT = f"""\
# Overseerr MCP

Single `overseerr` tool for media discovery and requests.

## Quick Reference

| Action    | Subactions                   | Description |
|-----------|------------------------------|-------------|
| `help`    | (none)                       | Show this full help |
| `search`  | `media`, `help`              | Search for movies or TV |
| `movie`   | `details`, `request`, `help` | Movie info and requests |
| `tv`      | `details`, `request`, `help` | TV info and requests |
| `request` | `failed`, `help`             | Request management |

For action-specific help: `overseerr(action="<action>", subaction="help")`

---

## Typical Workflow

1. Search: `overseerr(action="search", subaction="media", query="Dune")`
2. Get TMDB ID from results
3. Details: `overseerr(action="movie", subaction="details", tmdb_id=438631)`
4. Request: `overseerr(action="movie", subaction="request", tmdb_id=438631)`
5. Check failures: `overseerr(action="request", subaction="failed")`

---

{_SEARCH_HELP}

{_MOVIE_HELP}

{_TV_HELP}

{_REQUEST_HELP}
"""


def register_overseerr_tool(mcp: "FastMCP", client: "OverseerrApiClient") -> Any:
    """Register the single `overseerr` tool with the FastMCP instance.

    Returns the registered tool function for testing.
    """

    @mcp.tool()
    async def overseerr(
        action: OVERSEERR_ACTIONS,
        subaction: str = "",
        # search
        query: str | None = None,
        media_type: str | None = None,
        # movie + tv
        tmdb_id: int | None = None,
        # tv-only
        seasons: list[int] | None = None,
        # request list
        count: int = 10,
        skip: int = 0,
    ) -> dict[str, Any] | list[Any] | str:
        """Interact with Overseerr for media discovery and requests.

        Use action='help' for full documentation.
        Use subaction='help' on any action for action-specific help.
        """
        if action == "help":
            return _HELP_TEXT

        if action == "search":
            return await _handle_search(subaction, query, media_type, client=client)

        if action == "movie":
            return await _handle_movie(subaction, tmdb_id, client=client)

        if action == "tv":
            return await _handle_tv(subaction, tmdb_id, seasons, client=client)

        if action == "request":
            return await _handle_request(subaction, count, skip, client=client)

        from fastmcp.exceptions import ToolError

        raise ToolError(f"Invalid action '{action}'.")

    return overseerr
