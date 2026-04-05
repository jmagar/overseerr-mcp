# Setup Guide — overseerr-mcp

Step-by-step instructions to get overseerr-mcp running locally, in Docker, or as a Claude Code plugin.

## Prerequisites

| Dependency | Version | Purpose |
| --- | --- | --- |
| Python | 3.11+ | Runtime |
| uv | latest | Package manager |
| Docker | 24+ | Container deployment |
| Docker Compose | v2+ | Orchestration |
| just | latest | Task runner |
| openssl | any | Token generation |

## 1. Clone the repository

```bash
git clone https://github.com/jmagar/overseerr-mcp.git
cd overseerr-mcp
```

## 2. Install dependencies

```bash
uv sync --dev
```

Or use the setup recipe:

```bash
just setup
```

## 3. Configure environment

```bash
cp .env.example .env
chmod 600 .env
```

Edit `.env` and set required values:

```bash
# Upstream Overseerr credentials
OVERSEERR_URL=https://overseerr.example.com
OVERSEERR_API_KEY=your_overseerr_api_key

# MCP server auth token — generate one:
#   openssl rand -hex 32
OVERSEERR_MCP_TOKEN=<paste-generated-token>
```

See [CONFIG.md](CONFIG.md) for all environment variables.

## 4. Start locally

```bash
just dev
```

Or directly:

```bash
uv run python -m overseerr_mcp
```

The server starts on `http://localhost:6975` by default (`.env.example` recommends port `9151`).

## 5. Start via Docker

```bash
just up
```

Or manually:

```bash
docker compose up -d
```

## 6. Verify

```bash
just health
```

Or:

```bash
curl http://localhost:9151/health
```

Expected response:

```json
{"status": "ok"}
```

## 7. Install as Claude Code plugin

```bash
/plugin marketplace add jmagar/claude-homelab
/plugin install overseerr-mcp @jmagar-claude-homelab
```

Configure the plugin with your MCP token when prompted, or set it in the plugin's userConfig.

## Troubleshooting

### "Connection refused" on health check

- Confirm the server is running: `docker compose ps` or check process list
- Verify `OVERSEERR_MCP_PORT` matches the port you are curling
- If running in Docker, ensure the port is published in `docker-compose.yml`

### "401 Unauthorized" on tool calls

- Verify `OVERSEERR_MCP_TOKEN` in `.env` matches the token configured in your MCP client
- If behind a reverse proxy, set `OVERSEERR_MCP_NO_AUTH=true` and handle auth at the proxy

### "OVERSEERR_URL and OVERSEERR_API_KEY must be set" at startup

- Confirm `.env` exists and is readable: `ls -la .env`
- Confirm required variables are set: `grep OVERSEERR_URL .env`
- Check file permissions: `chmod 600 .env`

### Docker cannot reach upstream Overseerr

- `localhost` in `OVERSEERR_URL` does not resolve inside the container
- Use `host.docker.internal` or the service's LAN IP instead
- Check entrypoint logs: `just logs`

### Plugin not discovered by Claude Code

- Run `/plugin list` and confirm the plugin appears
- Check `~/.claude/plugins/cache/` for the plugin directory
- Re-run `/plugin marketplace add jmagar/claude-homelab` to refresh
