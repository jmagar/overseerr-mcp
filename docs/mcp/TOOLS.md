# MCP Tools Reference — overseerr-mcp

## Design

overseerr-mcp exposes 7 flat tools (no action router pattern). Each tool maps to a specific Overseerr API operation.

| Tool | Purpose | Destructive |
| --- | --- | --- |
| `search_media` | Search movies or TV shows by title | no |
| `get_movie_details` | Fetch full movie details by TMDB ID | no |
| `get_tv_show_details` | Fetch full TV show details by TMDB ID | no |
| `request_movie` | Submit a movie request | yes |
| `request_tv_show` | Submit a TV request (all or specific seasons) | yes |
| `list_failed_requests` | List failed requests with pagination | no |
| `overseerr_help` | Return built-in markdown help | no |

## search_media

Search for movies or TV shows by title.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `query` | string | yes | — | Title or keyword to search |
| `media_type` | string | no | `null` | `"movie"` or `"tv"` — searches both if omitted |

**Response:** List of dicts, each containing:

| Field | Type | Description |
| --- | --- | --- |
| `tmdbId` | int | TMDB integer ID |
| `mediaType` | string | `"movie"` or `"tv"` |
| `title` | string | Display title |
| `year` | string | Release or first-air year, `null` if unknown |
| `overview` | string | Plot summary |
| `posterPath` | string | TMDB poster path (relative) |

**Examples:**

```python
search_media(query="Dune")
search_media(query="Breaking Bad", media_type="tv")
search_media(query="Inception", media_type="movie")
```

**Error cases:** Returns error string if no results match or Overseerr API fails.

## get_movie_details

Fetch detailed information for a movie from Overseerr.

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `tmdb_id` | int | yes | TMDB integer ID from `search_media` results |

**Response:** Full Overseerr/TMDB movie object including `id`, `title`, `releaseDate`, `runtime`, `overview`, `genres`, `status`, `mediaInfo` (request/availability state), `credits` (cast/crew), `posterPath`.

**Example:**

```python
get_movie_details(tmdb_id=438631)
```

## get_tv_show_details

Fetch detailed information for a TV show from Overseerr, including season list.

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `tmdb_id` | int | yes | TMDB integer ID from `search_media` results |

**Response:** Full Overseerr/TMDB show object including `id`, `name`, `firstAirDate`, `numberOfSeasons`, `numberOfEpisodes`, `overview`, `genres`, `status`, `seasons` (with `seasonNumber`, `episodeCount`, `airDate`), `mediaInfo`.

**Example:**

```python
get_tv_show_details(tmdb_id=1396)
```

## request_movie

Submit a movie request to Overseerr. Overseerr forwards the request to Radarr for download.

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `tmdb_id` | int | yes | TMDB integer ID for the movie to request |

**Response:** Request object with `id`, `status` (int), `media` (object with `tmdbId`, `mediaType`), `requestedBy`, `createdAt`, `modifiedAt`.

**Example:**

```python
request_movie(tmdb_id=438631)
```

## request_tv_show

Submit a TV show request. Optionally request specific seasons.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `tmdb_id` | int | yes | — | TMDB integer ID for the TV show |
| `seasons` | list[int] | no | `null` | Season numbers to request; omit to request all |

**Examples:**

```python
request_tv_show(tmdb_id=1396)                  # all seasons
request_tv_show(tmdb_id=1396, seasons=[1, 2])  # specific seasons
```

Season numbers come from `get_tv_show_details` response. Season 0 is typically specials.

## list_failed_requests

List media requests that have entered a failed state, sorted by most recently modified.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `count` | int | no | `10` | Number of results to return |
| `skip` | int | no | `0` | Number of results to skip (pagination) |

**Response:** List of dicts, each containing:

| Field | Type | Description |
| --- | --- | --- |
| `requestId` | int | Overseerr request ID |
| `status` | int | Request status code |
| `type` | string | `"movie"` or `"tv"` |
| `tmdbId` | int | TMDB ID |
| `title` | string | Media title |
| `requested_by` | string | Display name of requesting user |
| `requested_at` | string | ISO timestamp |
| `modified_at` | string | ISO timestamp |

Returns `"No failed requests found."` when empty.

## overseerr_help

Returns built-in markdown help covering all tools and parameters.

```python
overseerr_help()
```

## Request status codes

| Code | Name | Meaning |
| --- | --- | --- |
| `1` | pending | Awaiting admin approval |
| `2` | approved | Sent to Radarr/Sonarr for download |
| `3` | declined | Rejected by admin |
| `4` | available | Available in Plex/Jellyfin |
| `5` | partially_available | Some seasons/episodes available |
| `8` | failed | Download or processing error |

## Error patterns

All tools return an error string beginning with `"Error:"` on failure:

| Error | Cause |
| --- | --- |
| `Error: Overseerr API request failed (401)` | Invalid `OVERSEERR_API_KEY` |
| `Error: Overseerr API request failed (404)` | TMDB ID not found |
| `Error: Overseerr API request failed (409)` | Request already exists |
| `Error: Failed to connect to Overseerr` | `OVERSEERR_URL` unreachable |
| `Error: Overseerr API client is not available` | Server startup failed |

## Typical workflow

```python
# 1. Search
results = search_media(query="Dune: Part Two")

# 2. Get details
details = get_movie_details(tmdb_id=693134)

# 3. Request
request_movie(tmdb_id=693134)

# 4. Check failures
list_failed_requests(count=20)
```
