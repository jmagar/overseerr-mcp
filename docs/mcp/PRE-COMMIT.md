# Pre-commit Hooks — overseerr-mcp

## Configuration

File: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: local
    hooks:
      - id: skills-validate
        name: Validate skills
        entry: just validate-skills
        language: system
        pass_filenames: false
      - id: docker-security
        name: Docker security check
        entry: bash scripts/check-docker-security.sh
        language: system
        pass_filenames: false
      - id: no-baked-env
        name: No baked env vars
        entry: bash scripts/check-no-baked-env.sh
        language: system
        pass_filenames: false
      - id: ensure-ignore-files
        name: Ensure ignore files
        entry: bash scripts/ensure-ignore-files.sh --check
        language: system
        pass_filenames: false
```

## Hook descriptions

### skills-validate

Runs `just validate-skills` which currently returns "ok". Placeholder for future SKILL.md frontmatter validation.

### docker-security

Checks the Dockerfile for:
- Multi-stage build (builder + runtime)
- Non-root user (`mcpuser`)
- No sensitive `ENV` or `ARG` directives with real values
- `HEALTHCHECK` directive present
- Dependency manifest copied before source (layer caching)

### no-baked-env

Checks Docker artifacts for baked credentials:
- `docker-compose.yml` has no `environment:` block
- Dockerfile has no sensitive `ENV` values
- No `COPY .env` in Dockerfile
- `.dockerignore` excludes `.env`
- `entrypoint.sh` has no hardcoded credentials

### ensure-ignore-files

Verifies `.gitignore` and `.dockerignore` contain all required patterns (`.env`, `logs/*`, `backups/*`, editor directories, etc.).

## Installation

```bash
uv sync --dev  # installs pre-commit
pre-commit install
```

## Running manually

```bash
pre-commit run --all-files
```

Or individually:

```bash
bash scripts/check-docker-security.sh
bash scripts/check-no-baked-env.sh
bash scripts/ensure-ignore-files.sh --check .
```
