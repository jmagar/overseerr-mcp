# Output Styles — overseerr-mcp

## Current state

overseerr-mcp does not define any custom output styles. Tool responses use standard MCP text content.

All tools return either:
- Structured JSON data (dicts or lists) serialized by FastMCP
- Plain text error strings beginning with `"Error:"`
