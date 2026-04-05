# Upstream Service Documentation

Documentation for the Overseerr upstream service that overseerr-mcp integrates with.

## What is Overseerr?

[Overseerr](https://overseerr.dev/) is a media request management and discovery tool for the Plex ecosystem. It provides a web UI and REST API for users to request movies and TV shows, which are then forwarded to Radarr (movies) or Sonarr (TV) for automated download.

## API reference

The full Overseerr API specification is bundled at `docs/overseerr-api.yaml` (OpenAPI 3.0, 173 KB).

## Endpoints used by overseerr-mcp

| Endpoint | Method | Tool | Description |
| --- | --- | --- | --- |
| `/api/v1/search` | GET | `search_media` | Search movies and TV shows |
| `/api/v1/movie/{id}` | GET | `get_movie_details` | Movie details by TMDB ID |
| `/api/v1/tv/{id}` | GET | `get_tv_show_details` | TV show details by TMDB ID |
| `/api/v1/request` | POST | `request_movie`, `request_tv_show` | Submit a media request |
| `/api/v1/request` | GET | `list_failed_requests` | List requests with filters |

## Authentication

Overseerr uses API key authentication via the `X-Api-Key` header:

```bash
curl https://overseerr.example.com/api/v1/search?query=test \
  -H "X-Api-Key: your_api_key"
```

Get your API key from Overseerr Settings > General > API Key.

## Key concepts

### TMDB ID

The Movie Database (TMDB) integer identifier. Used as the primary key for all media in Overseerr.

- Always obtained from search results, never guessed
- Same ID space for movies and TV — `mediaType` distinguishes them
- Example: TMDB ID 693134 = "Dune: Part Two"

### Request status codes

| Code | Name | Description |
| --- | --- | --- |
| 1 | pending | Awaiting admin approval |
| 2 | approved | Sent to Radarr/Sonarr |
| 3 | declined | Rejected by admin |
| 4 | available | Available in Plex/Jellyfin |
| 5 | partially_available | Some content available |
| 8 | failed | Download/processing error |

### Request lifecycle

1. User submits request (status 1: pending)
2. Admin approves or auto-approval triggers (status 2: approved)
3. Overseerr sends to Radarr/Sonarr
4. Download completes, Plex scans (status 4: available)
5. Or download fails (status 8: failed)

## Error codes

| HTTP code | Meaning |
| --- | --- |
| 401 | Invalid or missing API key |
| 404 | TMDB ID not found |
| 409 | Request already exists for this media |
| 429 | Rate limited |
| 500+ | Overseerr internal error |

## Related services

| Service | Role |
| --- | --- |
| Radarr | Movie download management |
| Sonarr | TV show download management |
| Plex / Jellyfin | Media server (playback) |
| TMDB | Metadata source |
