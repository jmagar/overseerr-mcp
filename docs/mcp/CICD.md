# CI/CD — overseerr-mcp

## Workflows

### ci.yml

**Trigger:** Push to main, pull requests.

| Job | Runner | Steps |
| --- | --- | --- |
| `lint` | ubuntu-latest | `uv sync --group dev`, `ruff check .`, `ruff format --check .` |
| `typecheck` | ubuntu-latest | `uv sync --group dev`, `ty check` |
| `test` | ubuntu-latest | `uv sync --group dev`, `pytest` (exit 5 accepted) |


| `mcp-integration` | ubuntu-latest | `test_live.sh` with secrets (needs lint+typecheck+test; push or same-repo PRs only) |

### docker-publish.yml

**Trigger:** Push to main, tag push (`v*`), pull requests, manual dispatch.

Steps:
1. Checkout
2. Set up Docker Buildx
3. Log in to GHCR (`ghcr.io`)
4. Extract metadata (tags: ref, semver, latest, sha)
5. Build and push multi-platform image (`linux/amd64`, `linux/arm64`)
6. Trivy vulnerability scan (CRITICAL, HIGH)

**Tags generated:**

| Pattern | Example |
| --- | --- |
| Branch | `ghcr.io/jmagar/overseerr-mcp:main` |
| Semver | `ghcr.io/jmagar/overseerr-mcp:1.0.1` |
| Major.Minor | `ghcr.io/jmagar/overseerr-mcp:1.0` |
| Major | `ghcr.io/jmagar/overseerr-mcp:1` |
| Latest | `ghcr.io/jmagar/overseerr-mcp:latest` |
| SHA | `ghcr.io/jmagar/overseerr-mcp:sha-abc1234` |

### publish-pypi.yml

**Trigger:** Tag push matching `v*.*.*`.

Steps:
1. Checkout
2. Verify tag matches `pyproject.toml` version
3. Build package with `uv build`
4. Publish to PyPI via `pypa/gh-action-pypi-publish` (with attestations)
5. Create GitHub Release with generated notes and dist artifacts
6. Install `mcp-publisher`
7. Set version in `server.json`
8. Authenticate to MCP Registry via DNS (`tootie.tv`)
9. Publish to MCP Registry

## Secrets required

| Secret | Used by | Description |
| --- | --- | --- |
| `GITHUB_TOKEN` | docker-publish, publish-pypi | Auto-provided by GitHub Actions |
| `OVERSEERR_URL` | ci (mcp-integration) | Upstream Overseerr URL for live tests |
| `OVERSEERR_API_KEY` | ci (mcp-integration) | Upstream Overseerr API key for live tests |
| `MCP_PRIVATE_KEY` | publish-pypi | DNS private key for MCP Registry auth |

## Release process

1. Ensure main is clean and all CI passes
2. Run `just publish [major|minor|patch]`
3. This bumps version in all files, commits, tags, and pushes
4. Tag push triggers `publish-pypi.yml` and `docker-publish.yml`
5. PyPI package, GitHub Release, GHCR image, and MCP Registry entry are all created automatically
