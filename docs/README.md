# Documentation — overseerr-mcp

Index of all documentation for the overseerr-mcp plugin.

## Root-level documents

| File | Description |
| --- | --- |
| [SETUP.md](SETUP.md) | Step-by-step setup guide — clone, install, configure, verify |
| [CONFIG.md](CONFIG.md) | Configuration reference — all env vars, userConfig, .env conventions |
| [CHECKLIST.md](CHECKLIST.md) | Pre-release quality checklist — version sync, security, CI, registry |
| [GUARDRAILS.md](GUARDRAILS.md) | Security guardrails — credentials, Docker, auth, input handling |
| [INVENTORY.md](INVENTORY.md) | Component inventory — tools, resources, env vars, surfaces, deps |

## Subdirectories

| Directory | Scope |
| --- | --- |
| [mcp/](mcp/CLAUDE.md) | MCP server docs: auth, transport, tools, resources, testing, deployment |
| [plugin/](plugin/CLAUDE.md) | Plugin system docs: manifests, hooks, skills, commands, channels |
| [repo/](repo/CLAUDE.md) | Repository docs: git conventions, scripts, memory, rules |
| [stack/](stack/CLAUDE.md) | Technology stack docs: prerequisites, architecture, dependencies |
| [upstream/](upstream/CLAUDE.md) | Upstream service docs: Overseerr API reference and integration patterns |

## Quick links

- **Get started:** [SETUP.md](SETUP.md)
- **Environment variables:** [CONFIG.md](CONFIG.md) or [mcp/ENV.md](mcp/ENV.md)
- **Tool reference:** [mcp/TOOLS.md](mcp/TOOLS.md)
- **Authentication:** [mcp/AUTH.md](mcp/AUTH.md)
- **Deployment:** [mcp/DEPLOY.md](mcp/DEPLOY.md)
- **CI/CD pipelines:** [mcp/CICD.md](mcp/CICD.md)
- **Publishing:** [mcp/PUBLISH.md](mcp/PUBLISH.md)
