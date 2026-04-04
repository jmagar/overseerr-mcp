# Overseerr MCP

[![PyPI](https://img.shields.io/pypi/v/overseerr-mcp)](https://pypi.org/project/overseerr-mcp/) [![ghcr.io](https://img.shields.io/badge/ghcr.io-jmagar%2Foverseerr--mcp-blue?logo=docker)](https://github.com/jmagar/overseerr-mcp/pkgs/container/overseerr-mcp)

MCP server for searching Overseerr media, retrieving TMDB-backed details, and submitting movie or TV requests from Claude, Codex, or any MCP client.

## Overview

The server talks to an existing Overseerr instance via its REST API and exposes MCP tools over HTTP, stdio, or SSE transports. All Overseerr API authentication is handled server-side — clients only need a Bearer token for the MCP endpoint itself.

## What this repository ships

- `overseerr_mcp/`: FastMCP server and Overseerr HTTP client
- `.claude-plugin/`, `.codex-plugin/`, `gemini-extension.json`: client manifests
- `skills/overseerr/`: Claude-facing skill docs
- `docker-compose.yml`, `Dockerfile`, `entrypoint.sh`: container deployment
- `docs/overseerr-api.yaml`: bundled Overseerr API reference
- `scripts/`: linting, Docker, and smoke-test helpers

## Tools

| Tool | Purpose |
| --- | --- |
| `search_media` | Search movies or TV shows by title |
| `get_movie_details` | Fetch full movie details by TMDB ID |
| `get_tv_show_details` | Fetch full TV show details (including seasons) by TMDB ID |
| `request_movie` | Submit a movie request |
| `request_tv_show` | Submit a TV request, optionally scoped to specific seasons |
| `list_failed_requests` | List failed requests with pagination |
| `overseerr_help` | Return built-in markdown help for all tools |

The server also exposes `GET /health` (unauthenticated) for liveness checks.

### search_media

Search for movies or TV shows by title.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `query` | string | yes | — | Title or keyword to search |
| `media_type` | string | no | `null` | `"movie"` or `"tv"` — searches both if omitted |

**Response schema** — each item in the returned list:

| Field | Type | Description |
| --- | --- | --- |
| `tmdbId` | int | TMDB integer ID (use this for all subsequent tool calls) |
| `mediaType` | string | `"movie"` or `"tv"` |
| `title` | string | Display title (falls back to `name` or `originalName` for TV) |
| `year` | string | Release or first-air year (e.g. `"2021"`), `null` if unknown |
| `overview` | string | Plot summary |
| `posterPath` | string | TMDB poster path (relative, e.g. `/abc123.jpg`) |

**Examples:**

```
search_media(query="Dune")
search_media(query="Breaking Bad", media_type="tv")
search_media(query="Inception", media_type="movie")
```

Returns an error string if no results match or if the Overseerr API fails.

### get_movie_details

Fetch detailed information for a movie from Overseerr. Returns the full Overseerr/TMDB movie object including cast, genres, runtime, status, and current request state.

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `tmdb_id` | int | yes | TMDB integer ID from `search_media` results |

**Key response fields:**

| Field | Type | Description |
| --- | --- | --- |
| `id` | int | TMDB ID |
| `title` | string | Movie title |
| `releaseDate` | string | ISO date (`"2021-10-22"`) |
| `runtime` | int | Runtime in minutes |
| `overview` | string | Plot summary |
| `genres` | list | Genre objects with `id` and `name` |
| `status` | string | TMDB release status (e.g. `"Released"`) |
| `mediaInfo` | object | Overseerr request/availability state (see below) |
| `credits` | object | `cast` and `crew` arrays |
| `posterPath` | string | TMDB poster path |

**`mediaInfo` fields:**

| Field | Type | Description |
| --- | --- | --- |
| `status` | int | Overseerr media status code (see Request Status) |
| `requests` | list | Existing request objects for this media |
| `downloadStatus` | list | Radarr/Sonarr download state |

**Example:**

```
get_movie_details(tmdb_id=438631)
```

### get_tv_show_details

Fetch detailed information for a TV show from Overseerr. Includes season list — use the season numbers here to scope a `request_tv_show` call.

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `tmdb_id` | int | yes | TMDB integer ID from `search_media` results |

**Key response fields:**

| Field | Type | Description |
| --- | --- | --- |
| `id` | int | TMDB ID |
| `name` | string | Show title |
| `firstAirDate` | string | ISO date of first episode |
| `numberOfSeasons` | int | Total season count |
| `numberOfEpisodes` | int | Total episode count |
| `overview` | string | Plot summary |
| `genres` | list | Genre objects with `id` and `name` |
| `status` | string | TMDB show status (e.g. `"Ended"`, `"Returning Series"`) |
| `seasons` | list | Season objects with `seasonNumber`, `episodeCount`, `airDate` |
| `mediaInfo` | object | Overseerr request/availability state |

**Example:**

```
get_tv_show_details(tmdb_id=1396)
```

### request_movie

Submit a movie request to Overseerr. Overseerr forwards the request to Radarr for download.

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `tmdb_id` | int | yes | TMDB integer ID for the movie to request |

**Response fields:**

| Field | Type | Description |
| --- | --- | --- |
| `id` | int | Overseerr request ID |
| `status` | int | Request status code (see Request Status) |
| `media` | object | Media object with `tmdbId`, `mediaType`, and availability state |
| `requestedBy` | object | User who submitted the request |
| `createdAt` | string | ISO timestamp |
| `modifiedAt` | string | ISO timestamp of last status change |

**Example:**

```
request_movie(tmdb_id=438631)
```

### request_tv_show

Submit a TV show request. Optionally request specific seasons. Omitting `seasons` requests all seasons.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `tmdb_id` | int | yes | — | TMDB integer ID for the TV show |
| `seasons` | list[int] | no | `null` | Season numbers to request; omit to request all |

**Examples:**

```
# Request all seasons
request_tv_show(tmdb_id=1396)

# Request only seasons 1 and 2
request_tv_show(tmdb_id=1396, seasons=[1, 2])

# Request a single season
request_tv_show(tmdb_id=1396, seasons=[4])
```

Season numbers come from `get_tv_show_details` → `seasons[].seasonNumber`. Season 0 is typically specials; omit it unless specifically wanted.

### list_failed_requests

List media requests that have entered a failed state. Results are sorted by most recently modified.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `count` | int | no | `10` | Number of results to return |
| `skip` | int | no | `0` | Number of results to skip (for pagination) |

**Response fields** — each item in the returned list:

| Field | Type | Description |
| --- | --- | --- |
| `requestId` | int | Overseerr request ID |
| `status` | int | Request status code (see Request Status) |
| `type` | string | `"movie"` or `"tv"` |
| `tmdbId` | int | TMDB ID of the media |
| `title` | string | Media title |
| `requested_by` | string | Display name of the requesting user |
| `requested_at` | string | ISO timestamp of initial request |
| `modified_at` | string | ISO timestamp of last status change |

**Pagination examples:**

```
# First page
list_failed_requests(count=20)

# Second page
list_failed_requests(count=20, skip=20)

# Third page
list_failed_requests(count=20, skip=40)
```

Returns the string `"No failed requests found."` when the list is empty.

### overseerr_help

Returns the built-in markdown help document covering all tools and parameters.

```
overseerr_help()
```

## TMDB ID

The TMDB ID is The Movie Database's integer identifier for a specific title. It is the primary key used by Overseerr and all tools in this server.

- Always search first with `search_media`. The `tmdbId` field in each result is what you pass to all other tools.
- Never guess or construct a TMDB ID manually.
- The same integer is used for both movies and TV shows — the `mediaType` field distinguishes them.

Example: searching for "Dune: Part Two" returns `tmdbId: 693134`. Use that value directly in `get_movie_details(tmdb_id=693134)` and `request_movie(tmdb_id=693134)`.

## Request Status

Overseerr uses integer status codes for request and media state. These appear in `request_movie` / `request_tv_show` responses and `list_failed_requests` output.

| Code | Name | Meaning |
| --- | --- | --- |
| `1` | `pending` | Request submitted, awaiting admin approval |
| `2` | `approved` | Approved; sent to Radarr/Sonarr for download |
| `3` | `declined` | Request was rejected by an admin |
| `4` | `available` | Media is available in Plex/Jellyfin |
| `5` | `partially_available` | Some seasons/episodes are available |
| `8` | `failed` | Download or processing error in Radarr/Sonarr |

**Approval workflow:**

After `request_movie` or `request_tv_show`, the request enters `pending` (1) unless the Overseerr instance has auto-approval enabled for the requesting user. Once approved (2), Overseerr sends the request to Radarr (movies) or Sonarr (TV). When the download completes and Plex/Jellyfin picks it up, the status advances to `available` (4). A `failed` (8) status means an error in the download pipeline — report the title and request ID to the admin.

## Complete Workflow Example

```
# 1. Search by title
search_media(query="Dune: Part Two")
# → returns [{tmdbId: 693134, mediaType: "movie", title: "Dune: Part Two", year: "2024", ...}]

# 2. Inspect details to confirm and check existing request status
get_movie_details(tmdb_id=693134)
# → returns full movie object with mediaInfo.status showing current state

# 3. Submit the request
request_movie(tmdb_id=693134)
# → returns {id: 42, status: 1, media: {tmdbId: 693134, ...}, ...}
# status 1 = pending approval

# 4. For a TV show, check seasons first
get_tv_show_details(tmdb_id=1396)
# → returns show object with seasons list showing seasonNumber values

# 5. Request specific seasons
request_tv_show(tmdb_id=1396, seasons=[1, 2, 3])

# 6. Review any download failures
list_failed_requests(count=20)
```

## Installation

### Marketplace

```bash
/plugin marketplace add jmagar/claude-homelab
/plugin install overseerr-mcp @jmagar-claude-homelab
```

### Local development

```bash
uv sync --dev
uv run overseerr-mcp-server
```

Alternative entrypoint:

```bash
uv run python -m overseerr_mcp
```

## Configuration

Copy `.env.example` to `.env` and fill in required values:

```bash
cp .env.example .env
# or: just setup
```

### Environment variables

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `OVERSEERR_URL` | yes | — | Base URL of your Overseerr instance (e.g. `https://overseerr.example.com`) |
| `OVERSEERR_API_KEY` | yes | — | Overseerr API key (Settings → General → API Key) |
| `OVERSEERR_MCP_TRANSPORT` | no | `streamable-http` | Transport mode: `streamable-http`, `http`, `stdio`, or `sse` |
| `OVERSEERR_MCP_HOST` | no | `0.0.0.0` | Host interface to bind (use `0.0.0.0` for Docker) |
| `OVERSEERR_MCP_PORT` | no | `6975` | Port to bind; `.env.example` recommends `9151` |
| `OVERSEERR_MCP_TOKEN` | no | `""` | Bearer token for MCP endpoint auth; generate with `openssl rand -hex 32` |
| `OVERSEERR_MCP_NO_AUTH` | no | `false` | Set `true` to disable bearer auth (only if network-level auth is in place) |
| `OVERSEERR_MCP_ALLOW_DESTRUCTIVE` | no | `false` | Gate for destructive operations (reserved for future use) |
| `OVERSEERR_MCP_ALLOW_YOLO` | no | `false` | Gate to bypass confirmation prompts (reserved for future use) |
| `OVERSEERR_LOG_LEVEL` | no | `INFO` | Log verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR`. `LOG_LEVEL` is accepted as a fallback. |

`OVERSEERR_URL` and `OVERSEERR_API_KEY` are required — the server exits at startup if either is missing.

### Transport modes

| Mode | Description | When to use |
| --- | --- | --- |
| `streamable-http` | HTTP with streaming (MCP spec default) | Default; use for Claude.ai or any modern MCP client |
| `http` | Standard HTTP | Use when streaming is unsupported by the client |
| `stdio` | Standard input/output | Use for local CLI integration (no network port) |
| `sse` | Server-Sent Events | Use for legacy MCP clients that require SSE |

For HTTP transports, the MCP endpoint is served at `/mcp`. Requests must include `Authorization: Bearer <OVERSEERR_MCP_TOKEN>` unless `OVERSEERR_MCP_NO_AUTH=true`.

For `sse`, the endpoint is served at `/sse`.

### Authentication

Generate a token:

```bash
just gen-token
# or: openssl rand -hex 32
```

Set `OVERSEERR_MCP_TOKEN` in `.env` to that value. Configure your MCP client to send:

```
Authorization: Bearer <token>
```

The `/health` endpoint is always unauthenticated — it is used for Docker healthchecks.

## Error handling

All tools return an error string beginning with `"Error:"` when something goes wrong. Common errors:

| Error pattern | Cause |
| --- | --- |
| `Error: Overseerr API request failed (401)` | `OVERSEERR_API_KEY` is invalid or missing |
| `Error: Overseerr API request failed (404)` | TMDB ID does not exist in Overseerr |
| `Error: Overseerr API request failed (409)` | Request already exists for this media |
| `Error: Failed to connect to Overseerr` | `OVERSEERR_URL` is unreachable |
| `Error: Overseerr API client is not available` | Server startup failed (check logs) |
| `No results found for query '...'` | Search returned zero matches |

Always check whether the return value is a string before treating it as a dict or list.

## Development

```bash
just dev          # run server locally
just lint         # ruff check
just fmt          # ruff format
just typecheck    # ty check
just test         # run tests
just up           # docker compose up -d
just logs         # docker compose logs -f
just health       # curl /health
just test-live    # end-to-end live test (requires running server)
just gen-token    # generate a bearer token
just check-contract  # plugin contract lint
```

## Verification

Run after changes:

```bash
just lint
just typecheck
just test
just health
```

For a live end-to-end check against a running server:

```bash
just test-live
```

## Related plugins

| Plugin | Category | Description |
|--------|----------|-------------|
| [homelab-core](https://github.com/jmagar/claude-homelab) | core | Core agents, commands, skills, and setup/health workflows for homelab management. |
| [unraid-mcp](https://github.com/jmagar/unraid-mcp) | infrastructure | Query, monitor, and manage Unraid servers: Docker, VMs, array, parity, and live telemetry. |
| [unifi-mcp](https://github.com/jmagar/unifi-mcp) | infrastructure | Monitor and manage UniFi devices, clients, firewall rules, and network health. |
| [gotify-mcp](https://github.com/jmagar/gotify-mcp) | utilities | Send and manage push notifications via a self-hosted Gotify server. |
| [swag-mcp](https://github.com/jmagar/swag-mcp) | infrastructure | Create, edit, and manage SWAG nginx reverse proxy configurations. |
| [synapse-mcp](https://github.com/jmagar/synapse-mcp) | infrastructure | Docker management (Flux) and SSH remote operations (Scout) across homelab hosts. |
| [arcane-mcp](https://github.com/jmagar/arcane-mcp) | infrastructure | Manage Docker environments, containers, images, volumes, networks, and GitOps via Arcane. |
| [syslog-mcp](https://github.com/jmagar/syslog-mcp) | infrastructure | Receive, index, and search syslog streams from all homelab hosts via SQLite FTS5. |
| [plugin-lab](https://github.com/jmagar/plugin-lab) | dev-tools | Scaffold, review, align, and deploy homelab MCP plugins with agents and canonical templates. |
| [axon](https://github.com/jmagar/axon) | research | Self-hosted web crawl, ingest, embed, and RAG pipeline with MCP tooling. |

## License

MIT
