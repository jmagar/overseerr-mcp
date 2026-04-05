# Development Rules — overseerr-mcp

## Version bumping

Every feature branch push must bump the version in all version-bearing files.

Bump type determined by commit message prefix:
- `feat!:` or `BREAKING CHANGE` — major (X+1.0.0)
- `feat` or `feat(...)` — minor (X.Y+1.0)
- Everything else — patch (X.Y.Z+1)

Files to update:
- `pyproject.toml` — `version = "X.Y.Z"`
- `.claude-plugin/plugin.json` — `"version": "X.Y.Z"`
- `.codex-plugin/plugin.json` — `"version": "X.Y.Z"`
- `gemini-extension.json` — `"version": "X.Y.Z"`
- `CHANGELOG.md` — new entry under the bumped version

All files must have the same version.

## Commit conventions

```
feat(tool): add season filtering to request_tv_show
fix(auth): correct bearer token comparison
docs(readme): update tool reference table
chore(deps): bump fastmcp to 2.4.0
```

## Code standards

- Python 3.10+ required, 3.12 target for ruff
- Line length: 100
- Ruff rules: E, F, I, UP
- Type hints on all functions
- Async/await for all I/O
- Google-style docstrings with Args/Returns

## Security rules

- Never commit `.env`
- Never log credentials
- Bearer token comparison via `hmac.compare_digest`
- Container runs as non-root
- No baked env vars in Docker

## Symlink rules

- `AGENTS.md` must be symlink to `CLAUDE.md`
- `GEMINI.md` must be symlink to `CLAUDE.md`

## Naming conventions

- Environment variables: `OVERSEERR_` or `OVERSEERR_MCP_` prefix
- No generic names: `API_KEY`, `TOKEN`, `PORT`, etc.
- Tool functions: snake_case, descriptive
- Package name: `overseerr_mcp` (snake_case)
- Plugin name: `overseerr-mcp` (kebab-case)
