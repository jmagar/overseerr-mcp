# Commands — overseerr-mcp

## Current state

overseerr-mcp does not define any slash commands. All functionality is accessed through MCP tools and the `overseerr` skill.

## Plugin-level invocation

The skill is invoked automatically by Claude when the user mentions media requests or Overseerr. No explicit slash command is needed.

If slash commands were added, they would go in a `commands/` directory and be registered in the plugin manifest.
