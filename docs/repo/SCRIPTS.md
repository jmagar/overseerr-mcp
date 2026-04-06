# Scripts Reference — overseerr-mcp

## scripts/

smoke-test.sh

End-to-end smoke test via mcporter. Tests all 7 tools against a running server, skipping destructive tools.

```bash
bash bin/smoke-test.sh [--url http://host:9151/mcp]
```



Validates Dockerfile security:
- Multi-stage build
- Non-root user
- No baked secrets in ENV/ARG
- HEALTHCHECK present
- Layer caching order

```bash

```



Verifies no env vars are baked into Docker artifacts:
- No `environment:` block in compose
- No sensitive ENV in Dockerfile
- No COPY .env
- .dockerignore excludes .env

```bash

```



Reports outdated Python packages. Checks `uv.lock` sync and `uv pip list --outdated`.

```bash

```



Ensures `.gitignore` and `.dockerignore` have all required patterns. Two modes:
- Auto-fix (default): appends missing patterns
- Check (`--check`): reports missing patterns, exits non-zero

```bash


```

setup-data-dirs.sh

Creates data directories with correct ownership:

```bash
bash bin/setup-data-dirs.sh
```

Creates `${APPDATA_PATH}/overseerr-mcp/logs` owned by `${PUID}:${PGID}`.

## bin/

sync-uv.sh

Syncs Claude Code plugin userConfig to `.env`. Creates backups, uses file locking.

Resets `.env` permissions to 600 after Write/Edit/Bash tool use that touches `.env`.







Full ignore-files checker for both `.gitignore` and `.dockerignore`. Shared between hooks and scripts.
