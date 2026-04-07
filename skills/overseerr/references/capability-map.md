# Overseerr Capability Map

MCP tools are available when the overseerr-mcp HTTP server is running (`http://overseerr-mcp:9151`).
The script (`./skills/overseerr/scripts/overseerr-api`) is always available when the plugin is enabled.

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ MCP | Available as an MCP tool (`mcp__overseerr-mcp__*`) |
| ✅ Script | Available via the shell script |
| — | Not available via that interface |

---

## Search & Details

| Operation | MCP | Script | Notes |
|-----------|-----|--------|-------|
| Search movies + TV | ✅ `search_media` | ✅ `search` / `search-json` | MCP returns structured list; script formats with TMDB links |
| Movie details | ✅ `get_movie_details` | ✅ `movie <tmdb-id>` | |
| TV show details | ✅ `get_tv_show_details` | ✅ `tv <tmdb-id>` | |
| Movie recommendations | — | ✅ `movie-recommendations <tmdb-id>` | |
| Similar movies | — | ✅ `movie-similar <tmdb-id>` | |
| Movie ratings (RT/IMDB) | — | ✅ `movie-ratings <tmdb-id>` | |
| TV recommendations | — | ✅ `tv-recommendations <tmdb-id>` | |
| Similar TV shows | — | ✅ `tv-similar <tmdb-id>` | |
| Season/episode details | — | ✅ `tv-season <tmdb-id> <season>` | |
| Person/actor details | — | ✅ `person <person-id>` | |

---

## Discover

| Operation | MCP | Script | Notes |
|-----------|-----|--------|-------|
| Discover movies | — | ✅ `discover-movies [--genre --sort]` | |
| Discover TV shows | — | ✅ `discover-tv [--genre --sort]` | |
| Upcoming movies | — | ✅ `upcoming-movies` | |
| Upcoming TV | — | ✅ `upcoming-tv` | |
| Trending (movies + TV) | — | ✅ `trending` | |
| Plex watchlist | — | ✅ `watchlist` | |

---

## Requests

| Operation | MCP | Script | Notes |
|-----------|-----|--------|-------|
| List all requests | — | ✅ `requests [--filter --sort --user]` | Filters: pending, approved, declined, failed, available, processing |
| Request count summary | — | ✅ `request-count` | Returns pending/approved/declined/processing/available totals |
| Get request by ID | — | ✅ `request <id>` | |
| Create movie request | ✅ `request_movie` | ✅ `request-movie <tmdb-id>` | |
| Create TV request | ✅ `request_tv_show` | ✅ `request-tv <tmdb-id> [--season N]` | Both default to all seasons |
| Approve request | — | ✅ `approve <id>` | Admin only |
| Decline request | — | ✅ `decline <id>` | Admin only |
| Retry failed request | — | ✅ `retry <id>` | |
| Update request | — | ✅ `update-request <id> [--season --server --profile --root]` | |
| Delete request | — | ✅ `delete-request <id>` | |
| List failed requests | ✅ `list_failed_requests` | ✅ `failed-requests [--take --sort]` | MCP takes `count`/`skip`; script takes `--take`/`--skip`/`--sort` |

---

## Media

| Operation | MCP | Script | Notes |
|-----------|-----|--------|-------|
| List media | — | ✅ `media [--filter --sort]` | Filters: available, partial, processing, pending, unknown |
| Update media status | — | ✅ `media-status <id> <status>` | Admin only |
| Watch/playback data | — | ✅ `watch-data <id>` | Play counts and viewer history |
| Delete media | — | ✅ `delete-media <id>` | Admin only, destructive |

---

## Users

| Operation | MCP | Script | Notes |
|-----------|-----|--------|-------|
| List users | — | ✅ `users [--take --sort]` | |
| Get user details | — | ✅ `user <id>` | |
| Get user quotas | — | ✅ `user-quota <id>` | Movie/TV request limits and usage |
| Get user requests | — | ✅ `user-requests <id>` | |

---

## Issues

| Operation | MCP | Script | Notes |
|-----------|-----|--------|-------|
| List issues | — | ✅ `issues [--filter --sort]` | Filters: open, resolved |
| Get issue details | — | ✅ `issue <id>` | |
| Create issue | — | ✅ `create-issue <media-id> <type> <msg>` | Types: 1=video 2=audio 3=subtitle 4=other |
| Resolve issue | — | ✅ `resolve-issue <id>` | |
| Close issue | — | ✅ `close-issue <id>` | |

---

## MCP-Only

| Tool | Purpose |
|------|---------|
| `overseerr_help` | Returns help text about available MCP tools |

---

## Summary

- **MCP tools:** 7 (search, movie details, TV details, request movie, request TV, list failed requests, help)
- **Script commands:** ~40 covering all high/medium-value API endpoints
- **MCP coverage:** Core request workflow only — search, get details, submit requests, check failures
- **Script-only:** Approve/decline, discover, users, media management, issues, ratings, recommendations, watch data

**Recommendation:** Use MCP mode for the common request workflow. Drop to the script for admin operations (approve/decline), discovery browsing, user management, and anything not in the MCP tool list.
