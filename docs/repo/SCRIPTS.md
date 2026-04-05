# Scripts Reference — overseerr-mcp

## scripts/

### smoke-test.sh

End-to-end smoke test via mcporter. Tests all 7 tools against a running server, skipping destructive tools.

```bash
bash scripts/smoke-test.sh [--url http://host:9151/mcp]
```

### check-docker-security.sh

Validates Dockerfile security:
- Multi-stage build
- Non-root user
- No baked secrets in ENV/ARG
- HEALTHCHECK present
- Layer caching order

```bash
bash scripts/check-docker-security.sh [Dockerfile]
```

### check-no-baked-env.sh

Verifies no env vars are baked into Docker artifacts:
- No `environment:` block in compose
- No sensitive ENV in Dockerfile
- No COPY .env
- .dockerignore excludes .env

```bash
bash scripts/check-no-baked-env.sh [project-dir]
```

### check-outdated-deps.sh

Reports outdated Python packages. Checks `uv.lock` sync and `uv pip list --outdated`.

```bash
bash scripts/check-outdated-deps.sh [project-dir]
```

### ensure-ignore-files.sh

Ensures `.gitignore` and `.dockerignore` have all required patterns. Two modes:
- Auto-fix (default): appends missing patterns
- Check (`--check`): reports missing patterns, exits non-zero

```bash
bash scripts/ensure-ignore-files.sh              # auto-fix
bash scripts/ensure-ignore-files.sh --check .    # report only
```

### setup-data-dirs.sh

Creates data directories with correct ownership:

```bash
bash scripts/setup-data-dirs.sh
```

Creates `${APPDATA_PATH}/overseerr-mcp/logs` owned by `${PUID}:${PGID}`.

## hooks/scripts/

### sync-env.sh

Syncs Claude Code plugin userConfig to `.env`. Creates backups, uses file locking.

### fix-env-perms.sh

Resets `.env` permissions to 600 after Write/Edit/Bash tool use that touches `.env`.

### ensure-gitignore.sh

Lightweight gitignore checker (subset of ensure-ignore-files.sh). Ensures core patterns are present.

### ensure-ignore-files.sh

Full ignore-files checker for both `.gitignore` and `.dockerignore`. Shared between hooks and scripts.
