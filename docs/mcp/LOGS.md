# Logging — overseerr-mcp

## Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `OVERSEERR_LOG_LEVEL` | `INFO` | Primary log level |
| `LOG_LEVEL` | `INFO` | Fallback if `OVERSEERR_LOG_LEVEL` not set |

Valid levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

## Log outputs

### Console (stdout)

Format:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

Example:
```
2026-04-04 12:00:00,000 - OverseerrMCPServer - INFO - Starting Overseerr MCP Server — transport: http, port: 9151
```

### File (rotating)

Location: `logs/overseerr_mcp.log`

Format:
```
%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s
```

Rotation: 5 MB max, 3 backups.

The `logs/` directory is created automatically at startup.

## Logger name

All server logs use the logger name `OverseerrMCPServer`.

## What gets logged

### Startup

- Log level and file path
- Whether `OVERSEERR_URL` and `OVERSEERR_API_KEY` are loaded (yes/no, never the values)
- Client initialization success/failure
- Transport mode and port
- Whether bearer auth middleware is enabled

### Tool calls

Each tool invocation logs its parameters at INFO level:

```
search_media(query='Dune', media_type='None')
get_movie_details(tmdb_id=438631)
request_movie(tmdb_id=438631)
list_failed_requests(count=10, skip=0)
```

### API errors

Overseerr API errors are logged at ERROR level with status code and response body:

```
Overseerr API HTTP Error: 401 for https://overseerr.example.com/api/v1/search - Response: Unauthorized
```

### Auth failures

Unauthorized requests are logged at WARNING level:

```
Unauthorized request to /mcp from ('192.168.1.100', 54321)
```

## Security

- Credentials are never logged, not even at DEBUG level
- Startup logs only confirm presence: `OVERSEERR_URL loaded: Yes`
- API error responses may contain upstream error messages but never tokens

## Docker logs

```bash
just logs
# or: docker compose logs -f
```

In Docker, console logs go to the container's stdout (captured by Docker). File logs go to `/app/logs/overseerr_mcp.log` inside the container (mount a volume to persist).

## Debug mode

```bash
OVERSEERR_LOG_LEVEL=DEBUG just dev
```

DEBUG level adds:
- Full API request details (method, URL, params, JSON body)
- Encoded parameter values
