# Security Guardrails — overseerr-mcp

Safety and security patterns enforced across the plugin.

## Credential management

### Storage

- All credentials in `.env` with `chmod 600` permissions
- Never commit `.env` or any file containing secrets
- Use `.env.example` as a tracked template with placeholder values only
- Generate tokens with `openssl rand -hex 32` or `just gen-token`

### Ignore files

`.gitignore` and `.dockerignore` must include:

```
.env
.env.*
!.env.example
backups/*
logs/*
```

### Hook enforcement

Hooks run automatically at session start and after tool use:

| Hook | Trigger | Purpose |
| --- | --- | --- |
| `sync-env.sh` | SessionStart | Syncs `userConfig` credentials to `.env` |
| `ensure-gitignore.sh` | SessionStart, PostToolUse | Verifies `.gitignore` has required patterns |
| `fix-env-perms.sh` | PostToolUse (Write/Edit/Bash) | Sets `.env` to `chmod 600` if touched |
| `ensure-ignore-files.sh` | PostToolUse | Checks both `.gitignore` and `.dockerignore` |

### Credential rotation

1. Generate new token: `just gen-token`
2. Update `.env` with new value
3. Restart the server: `just restart`
4. Update MCP client configuration with new token
5. Verify: `just health`

## Destructive operations

`request_movie` and `request_tv_show` submit real media requests to Overseerr. These are not reversible from the MCP server — requests must be cancelled through the Overseerr UI.

Environment gates reserved for future use:
- `OVERSEERR_MCP_ALLOW_DESTRUCTIVE=true` — bypass confirmation
- `OVERSEERR_MCP_ALLOW_YOLO=true` — alias for the same behavior

## Docker security

### Non-root execution

The container runs as `mcpuser` (UID/GID 1000):

```dockerfile
RUN groupadd --gid 1000 mcpuser && \
    useradd --uid 1000 --gid mcpuser --shell /bin/bash --create-home mcpuser
USER mcpuser
```

Override with `PUID` and `PGID` in `docker-compose.yml`.

### No baked environment

Docker images contain no credentials at build time:

- No `ENV OVERSEERR_API_KEY=...` in Dockerfile
- No `COPY .env` in Dockerfile
- Credentials injected at runtime via `env_file` in compose

Verify with:

```bash
bash scripts/check-no-baked-env.sh
bash scripts/check-docker-security.sh
```

### Image scanning

CI runs Trivy vulnerability scanning on every push to main:

```yaml
- uses: aquasecurity/trivy-action@v0.28.0
  with:
    severity: 'CRITICAL,HIGH'
```

## Network security

### HTTPS in production

- `OVERSEERR_URL` should use `https://` in production
- HTTP is acceptable only for local development

### Bearer token authentication

- HTTP transport requires `OVERSEERR_MCP_TOKEN` by default
- Token sent as `Authorization: Bearer <token>` header
- Timing-safe comparison via `hmac.compare_digest`
- Disable only behind a trusted reverse proxy (`OVERSEERR_MCP_NO_AUTH=true`)

### Health endpoint

- `GET /health` is unauthenticated — required for container liveness probes
- Returns only `{"status": "ok"}`, never credentials or internal state
- All other endpoints (`/mcp`, `/sse`) require bearer authentication

## Logging

- Credentials are never logged — startup logs only confirm presence (`Yes`/`No`)
- Log file permissions: rotated at 5 MB, 3 backups
- Sensitive headers masked in request logs
