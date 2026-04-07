# Environment Variables

All credentials and configuration live in a single dotfile:

```
~/.config/overseerr-mcp/.env
```

This path is stable across plugin updates, works with every deployment mode (Claude Code plugin, Docker, local dev, `uvx`), and is created by `just setup` or the `config-media-stack` skill.

---

## Populating the dotfile

**First-time setup:**
```bash
just setup   # copies .env.example → ~/.config/overseerr-mcp/.env
```
Then edit the file and fill in your credentials.

**Automated extraction** (reads API keys directly from service config files):
```bash
extract-keys --appdata /mnt/user/appdata            # local
extract-keys --appdata myserver:/mnt/user/appdata   # remote via SSH
```

**Via Claude Code plugin settings UI:**
Set the URL fields in the plugin settings panel. The `ConfigChange` hook fires `bin/sync-urls` which writes them into the dotfile automatically. API keys cannot be written this way — use `extract-keys` or edit the file directly.

---

## Variables

### Required

| Variable | Description |
|---|---|
| `OVERSEERR_URL` | Base URL of your Overseerr server. No trailing slash. e.g. `https://overseerr.example.com` |
| `OVERSEERR_API_KEY` | Overseerr API key. Found in Overseerr Settings → General → API Key. |

### MCP Server

| Variable | Default | Description |
|---|---|---|
| `OVERSEERR_MCP_TRANSPORT` | `stdio` | Transport mode. `stdio` for Claude Code plugin/uvx. `http` for Docker/standalone. |
| `OVERSEERR_MCP_PORT` | `9151` | Port the HTTP server binds to. Only used when transport is `http`. |
| `OVERSEERR_MCP_HOST` | `0.0.0.0` | Interface to bind. Only used when transport is `http`. |
| `OVERSEERR_MCP_TOKEN` | — | Bearer token for HTTP auth. Required when transport is `http` and `OVERSEERR_MCP_NO_AUTH` is not set. Generate with: `openssl rand -hex 32` |
| `OVERSEERR_MCP_NO_AUTH` | `false` | Set `true` to disable bearer auth on HTTP transport. Only appropriate when secured at the network/proxy level. |

### Logging

| Variable | Default | Description |
|---|---|---|
| `OVERSEERR_LOG_LEVEL` | `INFO` | Log level for the MCP server. `DEBUG`, `INFO`, `WARNING`, `ERROR`. Takes precedence over `LOG_LEVEL`. |
| `LOG_LEVEL` | `INFO` | Fallback log level if `OVERSEERR_LOG_LEVEL` is not set. |

### Media Services (written by `sync-urls` / `extract-keys`)

| Variable | Description |
|---|---|
| `PLEX_URL` | Base URL of your Plex server. e.g. `http://plex:32400` |
| `PLEX_TOKEN` | Plex authentication token. |
| `RADARR_URL` | Base URL of your Radarr server. e.g. `http://radarr:7878` |
| `RADARR_API_KEY` | Radarr API key. |
| `SONARR_URL` | Base URL of your Sonarr server. e.g. `http://sonarr:8989` |
| `SONARR_API_KEY` | Sonarr API key. |
| `PROWLARR_URL` | Base URL of your Prowlarr server. e.g. `http://prowlarr:9696` |
| `PROWLARR_API_KEY` | Prowlarr API key. |
| `TAUTULLI_URL` | Base URL of your Tautulli server. e.g. `http://tautulli:8181` |
| `TAUTULLI_API_KEY` | Tautulli API key. |
| `SABNZBD_URL` | Base URL of your SABnzbd server. e.g. `http://sabnzbd:8080` |
| `SABNZBD_API_KEY` | SABnzbd API key. |
| `QBITTORRENT_URL` | Base URL of your qBittorrent WebUI. e.g. `http://qbittorrent:8080` |

### Docker / Compose

These are only relevant when running via `docker compose`. They are not read by the MCP server itself.

| Variable | Default | Description |
|---|---|---|
| `PUID` | `1000` | User ID the container process runs as. |
| `PGID` | `1000` | Group ID the container process runs as. |
| `DOCKER_NETWORK` | `overseerr-mcp` | Docker network name. |
| `APPDATA_PATH` | `./data` | Host path for persistent container data. |

---

## How each deployment mode loads the dotfile

| Mode | How it loads |
|---|---|
| Claude Code plugin (`.mcp.json`) | `server.py` calls `load_dotenv(~/.config/overseerr-mcp/.env)` at startup |
| Skills (`bin/load-env`) | `source ~/.config/overseerr-mcp/.env` via `load_env_file()` |
| Docker (`docker compose`) | `env_file: ${HOME}/.config/overseerr-mcp/.env` in `docker-compose.yml` |
| Local dev (`just dev`) | Same as plugin — `load_dotenv` in `server.py` |
| `uvx overseerr-mcp-server` | Same as plugin — `load_dotenv` in `server.py` |

---

## Security

The dotfile is created with `chmod 600` (owner read/write only). It should never be committed to git — `.gitignore` excludes `.env` and `.env.*` but explicitly tracks `.env.example`.
