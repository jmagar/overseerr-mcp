# Repository Structure — overseerr-mcp

## Layout

```
overseerr-mcp/
├── overseerr_mcp/               # Python package
│   ├── __init__.py              # Package docstring
│   ├── server.py                # FastMCP server, tools, auth middleware
│   └── client.py                # OverseerrApiClient (httpx)
│
├── skills/overseerr/            # Claude-facing skill
│   └── SKILL.md                 # Trigger phrases, tool reference, fallback mode
│
├── hooks/                       # Plugin hooks
│   ├── CLAUDE.md                # Hook development notes
│   └── hooks.json               # Hook triggers configuration
│
├── scripts/                     # CI and maintenance scripts
│   ├── smoke-test.sh            # mcporter smoke test
│   ├── check-docker-security.sh # Dockerfile security audit
│   ├── check-no-baked-env.sh    # Baked env var check
│   ├── check-outdated-deps.sh   # Dependency freshness check
│   ├── ensure-ignore-files.sh   # Ignore file enforcement
│   └── setup-data-dirs.sh       # Data directory setup
│
├── tests/
│   ├── test_live.sh             # Integration test suite (http/docker/stdio)
│   └── TEST_COVERAGE.md         # Coverage notes
│
├── .claude-plugin/plugin.json   # Claude Code manifest
├── .codex-plugin/plugin.json    # Codex manifest
├── gemini-extension.json        # Gemini manifest
├── .mcp.json                    # MCP client config
├── .app.json                    # App metadata
├── server.json                  # MCP Registry manifest
│
├── .github/workflows/
│   ├── ci.yml                   # Lint, typecheck, test, security, integration
│   ├── docker-publish.yml       # GHCR publish
│   └── publish-pypi.yml         # PyPI + MCP Registry publish
│
├── docs/                        # Documentation (this directory)
├── assets/                      # Icons and logos
├── backups/                     # .env backups (gitignored)
├── data/                        # Persistent data (gitignored)
├── logs/                        # Log files (gitignored)
│
├── CLAUDE.md                    # Development guidelines
├── AGENTS.md → CLAUDE.md        # Symlink
├── GEMINI.md → CLAUDE.md        # Symlink
├── README.md                    # User-facing documentation
├── CHANGELOG.md                 # Release history
├── LICENSE                      # MIT license
│
├── Dockerfile                   # Multi-stage Docker build
├── docker-compose.yml           # Compose deployment
├── entrypoint.sh                # Container entrypoint
├── .dockerignore                # Docker build context exclusions
│
├── pyproject.toml               # Python project config
├── uv.lock                      # Lock file
├── Justfile                     # Task runner
├── .env.example                 # Environment template
└── .gitignore                   # Git exclusions
```

## Key conventions

- `AGENTS.md` and `GEMINI.md` are symlinks to `CLAUDE.md`
- `backups/`, `logs/`, `data/` directories contain `.gitkeep` for tracking
- `.env` is always gitignored; `.env.example` is tracked
- Repository automation lives in `hooks/hooks.json`, GitHub Actions, and `scripts/`
