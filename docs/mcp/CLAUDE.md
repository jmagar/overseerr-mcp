# MCP Server Documentation

Documentation for the overseerr-mcp MCP server.

## Files

| File | Description |
| --- | --- |
| [TOOLS.md](TOOLS.md) | Tool definitions, parameters, response formats, and examples |
| [RESOURCES.md](RESOURCES.md) | MCP resource URIs (none currently exposed) |
| [SCHEMA.md](SCHEMA.md) | Tool schema definitions and generation |
| [ENV.md](ENV.md) | All environment variables with types, defaults, and sensitivity |
| [AUTH.md](AUTH.md) | Inbound (client) and outbound (upstream) authentication patterns |
| [TRANSPORT.md](TRANSPORT.md) | stdio, HTTP, SSE, and streamable-http configuration |
| [DEPLOY.md](DEPLOY.md) | Docker, compose, and production deployment |
| [LOGS.md](LOGS.md) | Logging configuration, rotation, and troubleshooting |
| [TESTS.md](TESTS.md) | Test strategy, unit tests, and integration tests |
| [MCPORTER.md](MCPORTER.md) | Live smoke testing with mcporter and test_live.sh |
| [CICD.md](CICD.md) | GitHub Actions workflows and CI pipeline |
| [PRE-COMMIT.md](PRE-COMMIT.md) | Local verification commands and repo checks |
| [PUBLISH.md](PUBLISH.md) | Publishing to PyPI, GHCR, and MCP Registry |
| [CONNECT.md](CONNECT.md) | Client connection examples |
| [DEV.md](DEV.md) | Local development workflow |
| [ELICITATION.md](ELICITATION.md) | Prompt design and tool elicitation patterns |
| [PATTERNS.md](PATTERNS.md) | Code patterns and conventions |
| [WEBMCP.md](WEBMCP.md) | HTTP transport details and middleware |
| [MCPUI.md](MCPUI.md) | Client UI integration notes |

## Reading order

**New to this MCP server:**
1. ENV.md — understand required configuration
2. AUTH.md — set up authentication
3. TRANSPORT.md — choose a transport and connect
4. TOOLS.md — learn available operations

**Experienced developers:**
- TOOLS.md for the API surface
- ENV.md for configuration reference
- DEV.md for development workflow

## Cross-references

- [plugin/](../plugin/) — Plugin manifest, hooks, and marketplace config
- [stack/](../stack/) — Language-specific implementation details
- [upstream/](../upstream/) — Overseerr API documentation
- [repo/](../repo/) — Repository structure and development workflow
