# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.1] - 2026-04-15

### Changed
- Repository maintenance updates committed from the current working tree.
- Version-bearing manifests synchronized to 1.2.1.


## [1.2.0] - 2026-04-07

### Changed
- Replaced 6 flat MCP tools (`search_media`, `get_movie_details`, `get_tv_show_details`,
  `request_movie`, `request_tv_show`, `list_failed_requests`, `overseerr_help`) with a
  single `overseerr` tool using the action + subaction pattern.
- `action="help"` returns full documentation for all actions.
- Each action supports `subaction="help"` for action-specific documentation.
- Actions: `help`, `search`, `movie`, `tv`, `request`.

## [1.1.0] - 2026-04-07

### Added
- Comprehensive `docs/ENV.md` with full variable reference, deployment mode table, and `load_dotenv` precedence explanation

### Changed
- All credentials now load from a single dotfile at `~/.config/overseerr-mcp/.env` across all deployment modes (plugin, Docker, uvx, local dev)
- Removed sensitive credential fields (`overseerr_api_key`, `overseerr_mcp_token`) from plugin `userConfig` — credentials come from the dotfile only
- Default transport changed to `stdio`; default port corrected to `9151`
- README updated to reflect dotfile setup, stdio default, correct port, and removed SSE transport references
- `bin/load-env` and `bin/sync-urls` simplified to use `${HOME}/.config/overseerr-mcp/.env` directly
- `docker-compose.yml` env_file uses `${HOME}/.config/overseerr-mcp/.env`
- `just setup` bootstraps the dotfile from `.env.example`

### Removed
- `.pre-commit-config.yaml` (replaced by Lefthook)
- SSE transport support references

## [1.0.3] - 2026-04-07

### Fixed
- Scoped Lefthook Python checks to staged `*.py` files so doc and config commits do not trigger unnecessary repo-wide lint, format, and typecheck work during `git commit`

## [1.0.2] - 2026-04-04

### Added
- Comprehensive test coverage documentation (TEST_COVERAGE.md)

## [1.0.1] - 2026-04-03

### Fixed
- **OAuth discovery 401 cascade**: BearerAuthMiddleware was blocking GET /.well-known/oauth-protected-resource, causing MCP clients to surface generic "unknown error". Added WellKnownMiddleware (RFC 9728) to return resource metadata.

### Added
- **docs/AUTHENTICATION.md**: New setup guide covering token generation and client config.
- **README Authentication section**: Added quick-start examples and link to full guide.



### Added
- FastMCP server with `overseerr` and `overseerr_help` tools
- Planned: BearerAuthMiddleware with startup token validation (not yet implemented in this release)
- Dual transport (http/stdio via OVERSEERR_MCP_TRANSPORT)
- Pagination for all list actions
- Destructive ops confirmation gate

## [1.1.0] - 2026-04-07

### Added
- Bundled `skills/overseerr/scripts/overseerr-api` HTTP fallback wrapper for search, details, requests, and failed-request listing when the MCP server is unavailable
- Shell regression test coverage for the Overseerr fallback wrapper request formatting and endpoint selection

### Changed
- Updated the Overseerr skill docs to use the bundled fallback wrapper instead of ad hoc `curl` examples
