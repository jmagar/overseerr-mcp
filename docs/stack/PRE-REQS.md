# Prerequisites — overseerr-mcp

## Required

| Dependency | Version | Purpose | Install |
| --- | --- | --- | --- |
| Python | 3.11+ | Runtime | System package manager or pyenv |
| uv | latest | Package manager | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

## Recommended

| Dependency | Version | Purpose | Install |
| --- | --- | --- | --- |
| Docker | 24+ | Container deployment | https://docs.docker.com/get-docker/ |
| Docker Compose | v2+ | Orchestration | Included with Docker Desktop |
| just | latest | Task runner | `cargo install just` or system package |
| openssl | any | Token generation | System package |
| jq | any | JSON processing (for health checks) | System package |
| curl | any | HTTP testing | System package |

## For CI/testing

| Dependency | Version | Purpose | Install |
| --- | --- | --- | --- |
| Node.js/npx | 18+ | mcporter (stdio tests) | https://nodejs.org/ |

## Upstream service

A running Overseerr instance is required:

| Requirement | Description |
| --- | --- |
| Overseerr | Any recent version |
| API key | Settings > General > API Key |
| Network access | MCP server must be able to reach `OVERSEERR_URL` |

## Quick setup

```bash
# Install uv (if not present)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install just (if not present)
cargo install just

# Clone and setup
git clone https://github.com/jmagar/overseerr-mcp.git
cd overseerr-mcp
uv sync --dev
just setup  # creates .env from template
```
