# overseerr-mcp

MCP server for Overseerr media request management.

## Development

- Language: Python (FastMCP + uv)
- Port: 9151 (OVERSEERR_MCP_PORT)
- Auth: Bearer token (OVERSEERR_MCP_TOKEN) + Overseerr API key (OVERSEERR_API_KEY)

## Commands

```bash
just dev       # run locally
just test      # run tests
just lint      # ruff check
just build     # docker build
```


## Version Bumping

**Every feature branch push MUST bump the version in ALL version-bearing files.**

Bump type is determined by the commit message prefix:
- `feat!:` or `BREAKING CHANGE` → **major** (X+1.0.0)
- `feat` or `feat(...)` → **minor** (X.Y+1.0)
- Everything else (`fix`, `chore`, `refactor`, `test`, `docs`, etc.) → **patch** (X.Y.Z+1)

**Files to update (if they exist in this repo):**
- `Cargo.toml` — `version = "X.Y.Z"` in `[package]`
- `package.json` — `"version": "X.Y.Z"`
- `pyproject.toml` — `version = "X.Y.Z"` in `[project]`
- `.claude-plugin/plugin.json` — `"version": "X.Y.Z"`
- `.codex-plugin/plugin.json` — `"version": "X.Y.Z"`
- `gemini-extension.json` — `"version": "X.Y.Z"`
- `README.md` — version badge or header
- `CHANGELOG.md` — new entry under the bumped version

All files MUST have the same version. Never bump only one file.
CHANGELOG.md must have an entry for every version bump.