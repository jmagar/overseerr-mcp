# Agent Definitions — overseerr-mcp

## Current state

overseerr-mcp does not define any agents. The `AGENTS.md` file in the repo root is a symlink to `CLAUDE.md`.

All functionality is exposed through MCP tools and the `overseerr` skill.

## When to add an agent

An agent would be appropriate if overseerr-mcp needed autonomous multi-step workflows, such as:

- A media-request orchestrator that searches, confirms availability, and submits requests
- A failed-request specialist that diagnoses and reports on download failures
- A media discovery agent that combines search with external recommendations

These are not currently needed because the individual tools are simple enough for Claude to orchestrate directly.
