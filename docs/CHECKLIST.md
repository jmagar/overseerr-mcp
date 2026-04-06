# Plugin Checklist — overseerr-mcp

Pre-release and quality checklist. Complete all items before tagging a release.

## Version and metadata

- [ ] All version-bearing files in sync: `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `gemini-extension.json`, `pyproject.toml`, `server.json`
- [ ] `CHANGELOG.md` has an entry for the new version
- [ ] README version badge is correct

## Configuration

- [ ] `.env.example` documents every environment variable the server reads
- [ ] `.env.example` has no actual secrets — only placeholders
- [ ] `.env` is in `.gitignore` and `.dockerignore`

## Documentation

- [ ] `CLAUDE.md` is current and matches repo structure
- [ ] `README.md` has up-to-date tool reference and environment variable table
- [ ] `skills/overseerr/SKILL.md` has correct frontmatter and tool reference
- [ ] Setup instructions work from a clean clone

## Security

- [ ] No credentials in code, docs, or git history
- [ ] `.gitignore` includes `.env`, `.env.*`, credentials files
- [ ] `.dockerignore` includes `.env`, `.git/`, secrets

- [ ] `/health` endpoint is unauthenticated; `/mcp` requires bearer auth
- [ ] Container runs as non-root (UID 1000, user `mcpuser`)
- [ ] No baked environment variables in Docker image

## Build and test

- [ ] Docker image builds: `just build`
- [ ] Docker healthcheck passes: `just health`
- [ ] CI pipeline passes: lint, typecheck, test, contract-drift, docker-security
- [ ] Live integration test passes: `just test-live`
- [ ] Pre-commit hooks configured and passing

## Deployment

- [ ] `docker-compose.yml` uses correct image tag and port (9151)
- [ ] `entrypoint.sh` is executable and validates `OVERSEERR_MCP_TOKEN`
- [ ] SWAG/reverse-proxy config tested (`docs/overseerr.subdomain.conf`)

## Registry (if publishing)

- [ ] `server.json` for MCP registry is valid (tv.tootie/overseerr-mcp)
- [ ] Package published to PyPI (`overseerr-mcp`)
- [ ] Docker image published to GHCR (`ghcr.io/jmagar/overseerr-mcp`)
- [ ] DNS verification for `tootie.tv` domain

## Marketplace

- [ ] Entry in `claude-homelab` marketplace manifest
- [ ] Plugin installs correctly: `/plugin marketplace add jmagar/claude-homelab`
